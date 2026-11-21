#!/usr/bin/env python3
"""Validate the three data tables against docs/schema.md and the evidence rules.

Usage:
    python3 tools/validate_data.py [--data data] [--schema docs/schema.md] [--out report.json]

Checks (errors fail the run; warnings are reported):
  - headers match the field lists in docs/schema.md, in order
  - enum, date, integer and number formats
  - ids: unique assessment and evidence ids; deal and assessment references resolve
  - scope: out-of-scope sides are blank; in-scope sides are complete
  - computed fields (structural, negotiation, overall, maintenance) match calculate_grade
  - evidence rules: every non-U breaker answer and every non-blank negotiation score has a
    `supports` row; any `M` has breaker_notes; prospective assessments have information_cutoff
    and only cite evidence dated on or before it
  - maintenance rules: D9 <= 2 if maintenance capex is blank; D4 <= 1 if adjusted EBITDA is not
    positive (and maint_notes explains it); known_upcoming_costs >= catchup_capex
Exit codes: 0 no errors; 2 usage or input error; 3 errors found. Standard library only.
"""
import argparse
import csv
import datetime
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calculate_grade as cg  # noqa: E402

VERSION = "0.1.1"

ENUMS = {
    "deals": {
        "acquirer_type": {"strategic", "pe", "other"},
        "deal_type": {"acquisition", "merger", "carve_out", "minority_stake", "jv"},
        "status": {"rumored", "announced", "pending", "closed", "withdrawn", "blocked"},
        "value_basis": {"disclosed", "reported", "estimated", "unknown"},
        "source_type": {"filing", "press_release", "regulator", "news", "other"},
        "confidence": {"high", "medium", "low"},
    },
    "assessments": {
        "grade_basis": {"prospective", "retrospective"},
        "grade_perspective": {"acquirer", "target_holders", "neutral"},
        "assessment_scope": cg.SCOPES,
        "warranty_trend": {"rising", "flat", "falling", "unknown"},
        "maint_basis": {"disclosed", "reported", "estimated", "unknown"},
        "structural_grade": set(cg.GRADES),
        "negotiation_classification": cg.NEG_CLASSES,
        "overall_integrity_verdict": set(cg.GRADES),
        "overall_driver": {"structural", "negotiation", "both"},
        "overall_provisional": {"yes", "no"},
        "pack_breakers": cg.PACK_BREAKER_VALUES,
        **{f: cg.BREAKER_VALUES for f in cg.BREAKER_FIELDS},
    },
    "evidence": {
        "evidence_type": {"filing", "press_release", "regulator", "analyst_estimate", "news", "interview",
                          "internal", "negative_finding", "inference", "other"},
        "bearing": {"supports", "contradicts", "inconclusive"},
        "confidence": {"high", "medium", "low"},
    },
}
DATES = {"deals": ["announced_date", "closed_date", "last_verified"],
         "assessments": ["assessment_date", "information_cutoff"],
         "evidence": ["source_date", "accessed_date"]}
NUMBERS = {"deals": ["value_usd_m", "ev_revenue", "ev_ebitda"],
           "assessments": ["ebitda_usd_m", "maint_capex_usd_m", "growth_capex_usd_m", "catchup_capex_usd_m",
                           "warranty_pct_revenue", "warranty_normalization_usd_m", "known_upcoming_costs_usd_m",
                           "maint_adj_ebitda_usd_m", "maint_adj_ev_ebitda", "price_adj_for_known_usd_m",
                           "score_pct", "nqs", "nq_multiplicative"],
           "evidence": []}
BREAKER_Q = ["b%d" % i for i in range(1, 12)]
DIM_Q = ["d%d" % i for i in range(1, 10)]
N_Q = ["n%d" % i for i in range(1, 11)]
QUESTION_BASE = BREAKER_Q + DIM_Q + N_Q + ["maint"]
PACK_Q = re.compile(r"^[a-z][a-z0-9]*_b[0-9]+$")
STRUCT_FIELDS = (cg.BREAKER_FIELDS + ["pack_breakers"] + list(cg.DIM_WEIGHTS))
STRUCT_COMPUTED = ["weighted_score", "score_pct", "structural_grade"]
MAINT_INPUTS = ["ebitda_usd_m", "maint_capex_usd_m", "growth_capex_usd_m", "catchup_capex_usd_m",
                "warranty_pct_revenue", "warranty_trend", "warranty_normalization_usd_m",
                "known_upcoming_costs_usd_m", "maint_basis", "maint_notes",
                "maint_adj_ebitda_usd_m", "maint_adj_ev_ebitda", "price_adj_for_known_usd_m"]
NEG_FIELDS = list(cg.N_WEIGHTS)
NEG_COMPUTED = ["nqs", "negotiation_classification", "failure_predicates", "nq_multiplicative"]


class Report:
    def __init__(self):
        self.errors, self.warnings = [], []

    def err(self, table, key, msg):
        self.errors.append({"table": table, "key": key, "message": msg})

    def warn(self, table, key, msg):
        self.warnings.append({"table": table, "key": key, "message": msg})


def schema_fields(schema_path):
    with open(schema_path, encoding="utf-8") as fh:
        text = fh.read()
    out, cur = {}, None
    for line in text.split("\n"):
        m = re.match(r"## (deals|assessments|evidence)\.csv\s*$", line)
        if m:
            cur = m.group(1)
            out[cur] = []
            continue
        if line.startswith("## "):
            cur = None
        m = re.match(r"\| `([a-z0-9_]+)` \|", line)
        if m and cur:
            out[cur].append(m.group(1))
    return out


def read_table(path):
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.reader(f)
        header = next(r, None)
        rows = [dict(zip(header, row)) for row in r if any(c.strip() for c in row)]
    return header, rows


def is_date(s):
    try:
        datetime.date.fromisoformat(s)
        return len(s) == 10
    except ValueError:
        return False


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def num(s):
    s = (s or "").strip()
    return float(s) if s else None


def blank(r, f):
    return (r.get(f) or "").strip() == ""


def format_checks(table, rows, rep, idfield):
    for r in rows:
        key = r.get(idfield) or "?"
        for f, allowed in ENUMS[table].items():
            v = (r.get(f) or "").strip()
            if v != "" and v not in allowed:
                rep.err(table, key, "%s: %r is not an allowed value" % (f, v))
        for f in DATES[table]:
            v = (r.get(f) or "").strip()
            if v != "" and not is_date(v):
                rep.err(table, key, "%s: %r is not a YYYY-MM-DD date" % (f, v))
        for f in NUMBERS[table]:
            v = (r.get(f) or "").strip()
            if v != "" and not is_number(v):
                rep.err(table, key, "%s: %r is not a number" % (f, v))


def validate(data_dir, schema_path):
    rep = Report()
    fields = schema_fields(schema_path)
    tables = {}
    for t in ("deals", "assessments", "evidence"):
        header, rows = read_table(os.path.join(data_dir, t + ".csv"))
        if header != fields.get(t):
            rep.err(t, "header", "header does not match docs/schema.md (missing: %s; extra: %s)" % (
                sorted(set(fields.get(t, [])) - set(header or [])), sorted(set(header or []) - set(fields.get(t, [])))))
        tables[t] = rows
    deals, assess, evid = tables["deals"], tables["assessments"], tables["evidence"]

    for t, rows, idf in (("deals", deals, "deal_id"), ("assessments", assess, "assessment_id"), ("evidence", evid, "evidence_id")):
        seen = set()
        for r in rows:
            k = (r.get(idf) or "").strip()
            if not k:
                rep.err(t, "?", "%s is blank" % idf)
            elif k in seen:
                rep.err(t, k, "duplicate %s" % idf)
            seen.add(k)
        format_checks(t, rows, rep, idf)

    deal_by_id = {d["deal_id"]: d for d in deals}
    ev_by_assess = {}
    for e in evid:
        ev_by_assess.setdefault(e["assessment_id"], []).append(e)
    assess_ids = {a["assessment_id"] for a in assess}
    for e in evid:
        if e["assessment_id"] not in assess_ids:
            rep.err("evidence", e["evidence_id"], "assessment_id %r not in assessments.csv" % e["assessment_id"])
        q = (e.get("question_id") or "").strip()
        if q not in QUESTION_BASE and not PACK_Q.match(q):
            rep.err("evidence", e["evidence_id"], "question_id %r is not b1-b11, d1-d9, n1-n10, maint or a pack breaker id" % q)

    for a in assess:
        aid = a["assessment_id"]
        if a["deal_id"] not in deal_by_id:
            rep.err("assessments", aid, "deal_id %r not in deals.csv" % a["deal_id"])
        ev = ev_by_assess.get(aid, [])
        qs = {}
        for e in ev:
            qs.setdefault((e.get("question_id") or "").strip(), []).append(e)
        supports = lambda q: any((e.get("bearing") or "").strip() == "supports" for e in qs.get(q, []))  # noqa: E731

        scope = (a.get("assessment_scope") or "").strip()
        if scope not in cg.SCOPES:
            rep.err("assessments", aid, "assessment_scope must be structural, negotiation or both (got %r)" % scope)
            continue
        in_struct = scope in ("structural", "both")
        in_neg = scope in ("negotiation", "both")

        # scope: out-of-scope sides stay blank
        if not in_struct:
            extra = [f for f in STRUCT_FIELDS + STRUCT_COMPUTED + ["breaker_notes"] + MAINT_INPUTS if not blank(a, f)]
            if extra:
                rep.err("assessments", aid, "scope is negotiation but structural fields are filled: %s" % ", ".join(extra))
        if not in_neg:
            extra = [f for f in NEG_FIELDS + NEG_COMPUTED + ["negotiation_notes"] if not blank(a, f)]
            if extra:
                rep.err("assessments", aid, "scope is structural but negotiation fields are filled: %s" % ", ".join(extra))

        # computed fields
        ev_value = num(deal_by_id.get(a["deal_id"], {}).get("value_usd_m"))
        comp = None
        try:
            comp = cg.compute_row(a, ev_value)
        except cg.InputError as ex:
            rep.err("assessments", aid, "cannot compute: %s" % ex)
        if comp:
            for d in cg.compare(a, comp):
                rep.err("assessments", aid, "%s: recorded %r, computed %r" % (d["field"], d["recorded"], d["computed"]))

        # structural evidence rules
        if in_struct:
            for f, qid in zip(cg.BREAKER_FIELDS, BREAKER_Q):
                ans = (a.get(f) or "").strip()
                if ans == "U":
                    rep.warn("assessments", aid, "%s is U (unresolved unknown): the grade stays horrid until resolved" % f)
                elif ans in ("Y", "N", "M") and not supports(qid):
                    rep.err("assessments", aid, "%s answered %s but has no 'supports' evidence row for %s" % (f, ans, qid))
                if ans == "M" and blank(a, "breaker_notes"):
                    rep.err("assessments", aid, "%s is M but breaker_notes is empty" % f)
            for f in cg.DIM_WEIGHTS:
                qid = f.split("_")[0]
                if qid not in qs:
                    rep.warn("assessments", aid, "dimension %s has no evidence rows" % qid)

        # negotiation evidence rules
        if in_neg:
            for f, qid in zip(NEG_FIELDS, N_Q):
                if blank(a, f):
                    rep.warn("assessments", aid, "%s is unknown (blank): the negotiation stays unresolved until it is answered" % qid)
                    continue
                if not supports(qid):
                    rep.err("assessments", aid, "%s scored but has no 'supports' evidence row for %s" % (f, qid))
                else:
                    sup = [e for e in qs.get(qid, []) if (e.get("bearing") or "").strip() == "supports"]
                    if all((e.get("evidence_type") or "").strip() == "inference" for e in sup):
                        rep.warn("assessments", aid, "%s rests only on inference (no direct evidence)" % qid)

        for qid, rows_ in qs.items():
            if any((e.get("bearing") or "").strip() == "contradicts" for e in rows_) and blank(a, "breaker_notes") and blank(a, "negotiation_notes") and blank(a, "notes"):
                rep.warn("assessments", aid, "%s has contradicting evidence but the assessment has no notes explaining it" % qid)

        # information cutoff
        basis = (a.get("grade_basis") or "").strip()
        cutoff = (a.get("information_cutoff") or "").strip()
        if basis == "prospective":
            if not cutoff:
                rep.err("assessments", aid, "prospective assessment needs information_cutoff")
            else:
                for e in ev:
                    sd = (e.get("source_date") or "").strip()
                    if not sd:
                        rep.err("evidence", e["evidence_id"], "prospective evidence needs source_date")
                    elif is_date(sd) and is_date(cutoff) and sd > cutoff:
                        rep.err("evidence", e["evidence_id"], "source_date %s is after information_cutoff %s of %s (hindsight in a prospective assessment)" % (sd, cutoff, aid))
            for e in ev:
                if (e.get("evidence_type") or "").strip() == "internal":
                    rep.warn("evidence", e["evidence_id"], "internal evidence in a prospective assessment: confirm it was available to the assessor's perspective at the time")
        elif basis == "retrospective" and cutoff:
            rep.warn("assessments", aid, "retrospective assessment has an information_cutoff; it will not limit evidence")

        # maintenance rules (structural only)
        if in_struct and comp:
            try:
                d9 = int((a.get("d9_maintenance_lifecycle") or "").strip())
                d4 = int((a.get("d4_financial_quality") or "").strip())
            except ValueError:
                d9 = d4 = None
            if d9 is not None and num(a.get("maint_capex_usd_m")) is None and d9 > 2:
                rep.err("assessments", aid, "maint_capex_usd_m is unknown, so D9 may not exceed 2 (scored %d)" % d9)
            if comp["maintenance"]["adjusted_ebitda_not_positive"]:
                if d4 is not None and d4 > 1:
                    rep.err("assessments", aid, "adjusted EBITDA is not positive, so D4 may not exceed 1 (scored %d)" % d4)
                if blank(a, "maint_notes"):
                    rep.err("assessments", aid, "adjusted EBITDA is not positive: maint_notes must explain")
            known, catchup = num(a.get("known_upcoming_costs_usd_m")), num(a.get("catchup_capex_usd_m"))
            if known is not None and catchup is not None and known < catchup:
                rep.err("assessments", aid, "known_upcoming_costs (%.2f) is below catchup_capex (%.2f), but it includes it" % (known, catchup))
    return rep, {t: len(r) for t, r in tables.items()}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Validate DealIntegrity data tables")
    ap.add_argument("--data", default="data")
    ap.add_argument("--schema", default="docs/schema.md")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    try:
        rep, counts = validate(args.data, args.schema)
    except (OSError, csv.Error, KeyError, TypeError) as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    print("validate_data %s | deals %d, assessments %d, evidence %d" % (VERSION, counts["deals"], counts["assessments"], counts["evidence"]))
    for e in rep.errors:
        print("  ERROR   %s %s: %s" % (e["table"], e["key"], e["message"]))
    for w in rep.warnings:
        print("  warning %s %s: %s" % (w["table"], w["key"], w["message"]))
    print("%d errors, %d warnings" % (len(rep.errors), len(rep.warnings)))
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump({"tool": "validate_data", "version": VERSION, "counts": counts, "errors": rep.errors,
                       "warnings": rep.warnings}, f, indent=2, sort_keys=True)
    return 3 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
