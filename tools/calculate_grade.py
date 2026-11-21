#!/usr/bin/env python3
"""Deterministic calculator for DealIntegrity: structural grade, negotiation score,
overall integrity verdict, and maintenance-adjusted figures.

The agent (or analyst) gathers evidence and answers the questions. This tool applies
the rules: it never interprets a breaker, improvises a formula, or softens a predicate.

Usage:
    python3 tools/calculate_grade.py data/assessments.csv [--deals data/deals.csv] [--out report.json]

Exit codes: 0 all rows computed and match the recorded values; 2 usage or input error;
3 at least one recorded computed field differs from the computation (a blank recorded
field that should hold a value counts as a difference). Standard library only.
"""
import argparse
import csv
import json
import os
import sys

VERSION = "0.1.1"

# ---------------------------------------------------------------- structural side
BREAKER_FIELDS = ["b1_regulatory", "b2_customer_concentration", "b3_platform_end_of_life",
                  "b4_liabilities", "b5_funding", "b6_unverified_numbers", "b7_quality_standing",
                  "b8_labor_blocks", "b9_ip_supply", "b10_policy_dependency", "b11_catchup_capex"]
DIM_WEIGHTS = {"d1_strategic_fit": 2, "d2_customer_contract": 2, "d3_tech_cycle": 2,
               "d4_financial_quality": 2, "d5_price_structure": 2, "d6_synergies": 1,
               "d7_integration": 1, "d8_regulatory_geo": 1, "d9_maintenance_lifecycle": 2}
MAX_SCORE = 4 * sum(DIM_WEIGHTS.values())  # 60
GRADES = ["horrid", "bad", "okay", "good", "great"]  # worst to best; also the overall scale
BREAKER_VALUES = {"Y", "N", "U", "M"}
PACK_BREAKER_VALUES = {"n/a", "clear", "mitigated", "unmitigated"}
# Band floors in weighted-score points out of 60 (80% = 48, 65% = 39, 50% = 30, 35% = 21).
BAND_FLOORS = [(48, "great"), (39, "good"), (30, "okay"), (21, "bad")]

# ------------------------------------------------------------- negotiation side
# Weights are whole percents (sum 100); scores are whole numbers 0 to 100. Integer
# arithmetic: no floating-point edge cases at the band boundaries.
N_WEIGHTS = {"n1_preparation": 10, "n2_information_discovery": 15, "n3_value_creation": 15,
             "n4_communication": 10, "n5_value_capture": 10, "n6_objective_alignment": 10,
             "n7_relationship": 10, "n8_risk_allocation": 8, "n9_epistemic_integrity": 8,
             "n10_procedural_legitimacy": 4}
PREDICATES = [("F1", "n9_epistemic_integrity"), ("F2", "n8_risk_allocation"),
              ("F3", "n10_procedural_legitimacy")]
PREDICATE_THRESHOLD = 40
# Band floors in points (sum of score x weight, 0 to 10000): 95, 85, 70, 55, 40.
NEG_BAND_FLOORS = [(9500, "exceptional"), (8500, "high_quality"), (7000, "competent"),
                   (5500, "marginal"), (4000, "poor")]
NEG_CLASSES = {"exceptional", "high_quality", "competent", "marginal", "poor", "failed", "unresolved"}
# Negotiation classification on the shared overall scale.
NEG_TO_OVERALL = {"failed": "horrid", "unresolved": "horrid", "poor": "bad", "marginal": "okay",
                  "competent": "good", "high_quality": "great", "exceptional": "great"}
SCOPES = {"structural", "negotiation", "both"}


class InputError(ValueError):
    pass


def _worse(a, b):
    return a if GRADES.index(a) <= GRADES.index(b) else b


def band_for(weighted_score):
    for floor, name in BAND_FLOORS:
        if weighted_score >= floor:
            return name
    return "horrid"


def structural_grade(breakers, pack_breakers, dims):
    """The grade is the WORST of three independent ceilings:
      1. breaker ceiling: any core `Y` or `U`, or pack `unmitigated` -> horrid;
         else any core `M` or pack `mitigated` -> okay; else none.
      2. zero-dimension ceiling: any dimension scored 0 -> bad.
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
    return {"weighted_score": weighted, "max_score": MAX_SCORE,
            "score_pct": round(weighted * 100.0 / MAX_SCORE, 1),
            "breaker_ceiling": breaker_ceiling, "zero_dimension_ceiling": zero_ceiling,
            "band": band, "structural_grade": result, "reasons": reasons,
            "has_unknown": any(a == "U" for a in answers)}


def negotiation(nscores):
    """Negotiation Quality Score and classification.

    Scores are whole numbers 0 to 100; blank or None means UNKNOWN. An unknown is never a pass:
      - any predicate dimension (N8, N9, N10) below 40 fires its predicate -> failed;
      - otherwise any unknown dimension -> unresolved (no NQS, shown as Failed, provisional);
      - otherwise the NQS band applies.
    """
    present, missing = {}, []
    for k in N_WEIGHTS:
        v = nscores.get(k)
        if v is None or (isinstance(v, str) and v.strip() == ""):
            missing.append(k)
            continue
        if isinstance(v, bool):
            raise InputError("%s must be a whole number 0 to 100 (got %r)" % (k, v))
        try:
            iv = int(str(v).strip())
        except ValueError:
            raise InputError("%s must be a whole number 0 to 100 (got %r)" % (k, v))
        if str(iv) != str(v).strip() or not 0 <= iv <= 100:
            raise InputError("%s must be a whole number 0 to 100 (got %r)" % (k, v))
        present[k] = iv

    fired = [code for code, dim in PREDICATES if dim in present and present[dim] < PREDICATE_THRESHOLD]
    reasons = []
    nqs = None
    if not missing:
        points = sum(present[k] * w for k, w in N_WEIGHTS.items())
        nqs = round(points / 100.0, 1)
    if fired:
        classification = "failed"
        reasons.append("failure predicate fired: " + ", ".join(fired))
    elif missing:
        classification = "unresolved"
        reasons.append("unknown negotiation dimensions: " + ", ".join(sorted(m.split("_")[0] for m in missing)))
    else:
        classification = "failed"
        for floor, name in NEG_BAND_FLOORS:
            if points >= floor:
                classification = name
                break
    return {"nqs": nqs, "negotiation_classification": classification, "failure_predicates": fired,
            "missing": missing, "reasons": reasons, "nq_multiplicative": _multiplicative(present)}


def _multiplicative(p):
    """EXPERIMENTAL diagnostic, never used in a verdict. Product of four factors (0 to 1):
    OutcomePotential = (15*N2 + 15*N3 + 10*N5) / 4000, EpistemicIntegrity = N9/100,
    RiskAdequacy = N8/100, StrategicAlignment = N6/100. A critical failure in any factor
    cannot be offset by the others."""
    need = ("n2_information_discovery", "n3_value_creation", "n5_value_capture",
            "n6_objective_alignment", "n8_risk_allocation", "n9_epistemic_integrity")
    if not all(k in p for k in need):
        return None
    outcome = (15 * p["n2_information_discovery"] + 15 * p["n3_value_creation"] + 10 * p["n5_value_capture"]) / 4000.0
    return round(outcome * (p["n9_epistemic_integrity"] / 100.0) * (p["n8_risk_allocation"] / 100.0)
                 * (p["n6_objective_alignment"] / 100.0), 3)


def overall(scope, structural, neg):
    """Worst of the in-scope sides on the shared scale horrid..great."""
    sides = {}
    if structural is not None:
        sides["structural"] = structural["structural_grade"]
    if neg is not None:
        sides["negotiation"] = NEG_TO_OVERALL[neg["negotiation_classification"]]
    verdict = None
    for v in sides.values():
        verdict = v if verdict is None else _worse(verdict, v)
    drivers = [s for s, v in sides.items() if v == verdict]
    driver = "both" if len(drivers) == 2 else drivers[0]
    provisional = bool((structural and structural["has_unknown"]) or (neg and neg["negotiation_classification"] == "unresolved"))
    return {"overall_integrity_verdict": verdict, "overall_driver": driver,
            "overall_provisional": "yes" if provisional else "no"}


# ------------------------------------------------------------------ maintenance
def _num(s):
    s = (s if isinstance(s, str) else ("" if s is None else str(s))).strip()
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
            out["adjusted_ebitda_not_positive"] = True
        elif enterprise_value is not None:
            out["maint_adj_ev_ebitda"] = round(enterprise_value / adj, 2)
    if enterprise_value is not None and known is not None:
        out["price_adj_for_known_usd_m"] = round(enterprise_value - known, 2)
    return out


# ---------------------------------------------------------------------- one row
def _scope(row):
    s = (row.get("assessment_scope") or "").strip()
    if s not in SCOPES:
        raise InputError("assessment_scope must be one of structural, negotiation, both (got %r)" % s)
    return s


def compute_row(row, enterprise_value):
    scope = _scope(row)
    out = {"scope": scope, "structural": None, "negotiation": None}
    if scope in ("structural", "both"):
        breakers = {f: (row.get(f) or "").strip() for f in BREAKER_FIELDS}
        dims = {}
        for f in DIM_WEIGHTS:
            s = (row.get(f) or "").strip()
            try:
                dims[f] = int(s)
            except ValueError:
                raise InputError("%s must be an integer 0 to 4 (got %r)" % (f, s))
        out["structural"] = structural_grade(breakers, (row.get("pack_breakers") or "").strip(), dims)
        out["maintenance"] = maintenance(row, enterprise_value)
    else:
        out["maintenance"] = {"maint_adj_ebitda_usd_m": None, "maint_adj_ev_ebitda": None,
                              "price_adj_for_known_usd_m": None, "adjusted_ebitda_not_positive": False}
    if scope in ("negotiation", "both"):
        out["negotiation"] = negotiation({k: row.get(k) for k in N_WEIGHTS})
    out["overall"] = overall(scope, out["structural"], out["negotiation"])
    return out


def expected_fields(comp):
    """The recorded computed fields as (name, expected value or None, tolerance)."""
    s, n, m, o = comp["structural"], comp["negotiation"], comp["maintenance"], comp["overall"]
    return [
        ("weighted_score", s and s["weighted_score"], 0),
        ("score_pct", s and s["score_pct"], 0.05),
        ("structural_grade", s and s["structural_grade"], None),
        ("maint_adj_ebitda_usd_m", m["maint_adj_ebitda_usd_m"], 0.01),
        ("maint_adj_ev_ebitda", m["maint_adj_ev_ebitda"], 0.01),
        ("price_adj_for_known_usd_m", m["price_adj_for_known_usd_m"], 0.01),
        ("nqs", n and n["nqs"], 0.05),
        ("negotiation_classification", n and n["negotiation_classification"], None),
        ("failure_predicates", (";".join(n["failure_predicates"]) if n else None) or None, None),
        ("nq_multiplicative", n and n["nq_multiplicative"], 0.0005),
        ("overall_integrity_verdict", o["overall_integrity_verdict"], None),
        ("overall_driver", o["overall_driver"], None),
        ("overall_provisional", o["overall_provisional"], None),
    ]


def compare(row, comp):
    """Differences between the recorded computed fields and the computation."""
    diffs = []
    for field, want, tol in expected_fields(comp):
        got = (row.get(field) or "").strip()
        if want is None or want == "":
            ok = got == ""
        elif got == "":
            ok = False
        elif tol is None:
            ok = got == str(want)
        else:
            try:
                ok = abs(float(got) - float(want)) <= tol
            except ValueError:
                ok = False
        if not ok:
            diffs.append({"field": field, "recorded": got, "computed": "" if want is None else want})
    return diffs


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def summary(comp):
    s, n, o = comp["structural"], comp["negotiation"], comp["overall"]
    parts = []
    if s:
        parts.append("structural %s (%.1f%%)" % (s["structural_grade"], s["score_pct"]))
    if n:
        parts.append("negotiation %s%s" % (n["negotiation_classification"], "" if n["nqs"] is None else " (NQS %.1f)" % n["nqs"]))
    return "%s -> OVERALL %s%s [driver: %s]" % ("; ".join(parts), o["overall_integrity_verdict"],
                                                 " (provisional)" if o["overall_provisional"] == "yes" else "",
                                                 o["overall_driver"])


def main(argv=None):
    ap = argparse.ArgumentParser(description="Compute DealIntegrity grades from assessments.csv")
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
        results, mismatched = [], 0
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
        print("  %s" % x["assessment_id"])
        print("    %s%s" % (summary(x["computed"]), "  [MISMATCH]" if x["differences"] else ""))
        for d in x["differences"]:
            print("      %s: recorded %r, computed %r" % (d["field"], d["recorded"], d["computed"]))
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump({"tool": "calculate_grade", "version": VERSION, "results": results}, f, indent=2, sort_keys=True)
    return 3 if mismatched else 0


if __name__ == "__main__":
    sys.exit(main())
