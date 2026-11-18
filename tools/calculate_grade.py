#!/usr/bin/env python3
"""Deterministic grade and maintenance-figure calculator for Acquisitions Analysis.

The agent (or analyst) gathers evidence and answers the questions. This tool applies
the rules: it never interprets a breaker or improvises a formula.

Usage:
    python3 tools/calculate_grade.py data/assessments.csv [--deals data/deals.csv] [--out report.json]

Exit codes: 0 all rows computed and match the recorded values; 2 usage or input error;
3 at least one recorded computed field differs from the computation.
Standard library only.
"""
import argparse
import csv
import json
import os
import sys

VERSION = "0.0.3"

BREAKER_FIELDS = ["b1_regulatory", "b2_customer_concentration", "b3_platform_end_of_life",
                  "b4_liabilities", "b5_funding", "b6_unverified_numbers", "b7_quality_standing",
                  "b8_labor_blocks", "b9_ip_supply", "b10_policy_dependency", "b11_catchup_capex"]
DIM_WEIGHTS = {"d1_strategic_fit": 2, "d2_customer_contract": 2, "d3_tech_cycle": 2,
               "d4_financial_quality": 2, "d5_price_structure": 2, "d6_synergies": 1,
               "d7_integration": 1, "d8_regulatory_geo": 1, "d9_maintenance_lifecycle": 2}
MAX_SCORE = 4 * sum(DIM_WEIGHTS.values())  # 60
GRADES = ["horrid", "bad", "okay", "good", "great"]  # worst to best
BREAKER_VALUES = {"Y", "N", "U", "M"}
PACK_BREAKER_VALUES = {"n/a", "clear", "mitigated", "unmitigated"}

# Band floors as weighted-score points out of 60 (80% = 48, 65% = 39, 50% = 30, 35% = 21).
# Integer arithmetic: no floating-point edge cases at the boundaries.
BAND_FLOORS = [(48, "great"), (39, "good"), (30, "okay"), (21, "bad")]


class InputError(ValueError):
    pass


def _worse(a, b):
    return a if GRADES.index(a) <= GRADES.index(b) else b


def band_for(weighted_score):
    for floor, name in BAND_FLOORS:
        if weighted_score >= floor:
            return name
    return "horrid"


def grade(breakers, pack_breakers, dims):
    """Return the grade and how it was reached.

    The grade is the WORST of three independent ceilings:
      1. breaker ceiling: any core `Y` or `U`, or pack `unmitigated` -> horrid;
         else any core `M` or pack `mitigated` -> okay; else none (great).
      2. zero-dimension ceiling: any dimension scored 0 -> bad; else none.
      3. score band from the weighted score.
    """
    for f in BREAKER_FIELDS:
        if breakers.get(f) not in BREAKER_VALUES:
            raise InputError("%s must be one of Y, N, U, M (got %r)" % (f, breakers.get(f)))
    if pack_breakers not in PACK_BREAKER_VALUES:
        raise InputError("pack_breakers must be one of n/a, clear, mitigated, unmitigated (got %r)" % (pack_breakers,))
    for f in DIM_WEIGHTS:
        v = dims.get(f)
        if not isinstance(v, int) or isinstance(v, bool) or not 0 <= v <= 4:
            raise InputError("%s must be an integer 0 to 4 (got %r)" % (f, v))

    weighted = sum(dims[f] * w for f, w in DIM_WEIGHTS.items())
    reasons = []

    answers = [breakers[f] for f in BREAKER_FIELDS]
    if any(a in ("Y", "U") for a in answers) or pack_breakers == "unmitigated":
        breaker_ceiling = "horrid"
        reasons.append("unmitigated breaker (Y or U, or pack breaker unmitigated)")
    elif any(a == "M" for a in answers) or pack_breakers == "mitigated":
        breaker_ceiling = "okay"
        reasons.append("mitigated breaker caps the grade at okay")
    else:
        breaker_ceiling = "great"

    if any(dims[f] == 0 for f in DIM_WEIGHTS):
        zero_ceiling = "bad"
        reasons.append("a dimension scored 0 caps the grade at bad")
    else:
        zero_ceiling = "great"

    band = band_for(weighted)
    result = _worse(_worse(breaker_ceiling, zero_ceiling), band)
    return {
        "weighted_score": weighted,
        "max_score": MAX_SCORE,
        "score_pct": round(weighted * 100.0 / MAX_SCORE, 1),
        "breaker_ceiling": breaker_ceiling,
        "zero_dimension_ceiling": zero_ceiling,
        "band": band,
        "grade": result,
        "reasons": reasons,
    }


def _num(s):
    s = (s or "").strip()
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        raise InputError("not a number: %r" % s)


def maintenance(row, enterprise_value):
    """Maintenance-adjusted figures. Any blank input leaves the output blank (unknown)."""
    ebitda = _num(row.get("ebitda_usd_m"))
    capex = _num(row.get("maint_capex_usd_m"))
    warr = _num(row.get("warranty_normalization_usd_m"))
    known = _num(row.get("known_upcoming_costs_usd_m"))
    out = {"maint_adj_ebitda_usd_m": None, "maint_adj_ev_ebitda": None,
           "price_adj_for_known_usd_m": None, "adjusted_ebitda_not_positive": False}
    if ebitda is not None and capex is not None and warr is not None:
        adj = ebitda - capex - warr
        out["maint_adj_ebitda_usd_m"] = round(adj, 2)
        if adj <= 0:
            out["adjusted_ebitda_not_positive"] = True   # multiple is not meaningful: left blank
        elif enterprise_value is not None:
            out["maint_adj_ev_ebitda"] = round(enterprise_value / adj, 2)
    if enterprise_value is not None and known is not None:
        out["price_adj_for_known_usd_m"] = round(enterprise_value - known, 2)
    return out


def compute_row(row, enterprise_value):
    breakers = {f: (row.get(f) or "").strip() for f in BREAKER_FIELDS}
    dims = {}
    for f in DIM_WEIGHTS:
        s = (row.get(f) or "").strip()
        try:
            dims[f] = int(s)
        except ValueError:
            raise InputError("%s must be an integer 0 to 4 (got %r)" % (f, s))
    g = grade(breakers, (row.get("pack_breakers") or "").strip(), dims)
    g.update(maintenance(row, enterprise_value))
    return g


def _same(recorded, computed, tol=0.01):
    r = (recorded or "").strip()
    if computed is None:
        return r == ""
    if r == "":
        return False
    try:
        return abs(float(r) - float(computed)) <= tol
    except ValueError:
        return False


def compare(row, comp):
    """Differences between recorded computed fields and the computation."""
    diffs = []
    pairs = [("weighted_score", comp["weighted_score"], 0), ("score_pct", comp["score_pct"], 0.05),
             ("maint_adj_ebitda_usd_m", comp["maint_adj_ebitda_usd_m"], 0.01),
             ("maint_adj_ev_ebitda", comp["maint_adj_ev_ebitda"], 0.01),
             ("price_adj_for_known_usd_m", comp["price_adj_for_known_usd_m"], 0.01)]
    for f, c, tol in pairs:
        if not _same(row.get(f), c, tol):
            diffs.append({"field": f, "recorded": (row.get(f) or "").strip(), "computed": c})
    if (row.get("grade") or "").strip() != comp["grade"]:
        diffs.append({"field": "grade", "recorded": (row.get("grade") or "").strip(), "computed": comp["grade"]})
    return diffs


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Compute grades and maintenance figures from assessments.csv")
    ap.add_argument("assessments")
    ap.add_argument("--deals", default=None, help="deals.csv for enterprise values (default: sibling deals.csv)")
    ap.add_argument("--out", default=None, help="write a JSON report here")
    args = ap.parse_args(argv)
    try:
        rows = read_csv(args.assessments)
        deals_path = args.deals or os.path.join(os.path.dirname(os.path.abspath(args.assessments)), "deals.csv")
        ev = {}
        if os.path.exists(deals_path):
            for d in read_csv(deals_path):
                ev[d["deal_id"]] = _num(d.get("value_usd_m"))
        results = []
        mismatched = 0
        for r in rows:
            comp = compute_row(r, ev.get(r.get("deal_id")))
            diffs = compare(r, comp)
            mismatched += 1 if diffs else 0
            results.append({"assessment_id": r.get("assessment_id"), "computed": comp, "differences": diffs})
    except (InputError, OSError, KeyError, csv.Error) as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    results.sort(key=lambda x: x["assessment_id"] or "")
    print("calculate_grade %s | %d assessments" % (VERSION, len(results)))
    for x in results:
        c = x["computed"]
        flag = "MISMATCH" if x["differences"] else "ok"
        print("  %-40s %5.1f%%  %-6s [%s]" % (x["assessment_id"], c["score_pct"], c["grade"], flag))
        for d in x["differences"]:
            print("      %s: recorded %r, computed %r" % (d["field"], d["recorded"], d["computed"]))
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump({"tool": "calculate_grade", "version": VERSION, "results": results}, f, indent=2, sort_keys=True)
    return 3 if mismatched else 0


if __name__ == "__main__":
    sys.exit(main())
