import csv
import io
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import validate_data as vd  # noqa: E402
import calculate_grade as cg  # noqa: E402

EXAMPLE = os.path.join(ROOT, "examples", "synthetic")
SCHEMA = os.path.join(ROOT, "docs", "schema.md")
P = "2020-examplebuyer-exampletarget_prospective_acquirer_1"
R = "2020-examplebuyer-exampletarget_retrospective_acquirer_1"


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def save(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        for n in ("deals", "assessments", "evidence"):
            shutil.copy(os.path.join(EXAMPLE, n + ".csv"), self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def mutate(self, table, fn):
        p = os.path.join(self.tmp, table + ".csv")
        cols, rows = load(p)
        out = fn(cols, rows)
        save(p, out[0] if out else cols, out[1] if out else rows)

    def run_validate(self):
        rep, counts = vd.validate(self.tmp, SCHEMA)
        return rep

    def messages(self, rep):
        return " || ".join(e["message"] for e in rep.errors)

    def set_assess(self, aid, **kv):
        def fn(cols, rows):
            for r in rows:
                if r["assessment_id"] == aid:
                    r.update(kv)
        self.mutate("assessments", fn)

    def recompute(self, aid):
        """Recompute and store the computed fields so only the targeted rule can fail."""
        _, deals = load(os.path.join(self.tmp, "deals.csv"))
        ev = float(deals[0]["value_usd_m"])

        def fn(cols, rows):
            for r in rows:
                if r["assessment_id"] == aid:
                    c = cg.compute_row(r, ev)
                    r["weighted_score"] = str(c["weighted_score"])
                    r["score_pct"] = "%.1f" % c["score_pct"]
                    r["grade"] = c["grade"]
                    r["maint_adj_ebitda_usd_m"] = "" if c["maint_adj_ebitda_usd_m"] is None else "%.2f" % c["maint_adj_ebitda_usd_m"]
                    r["maint_adj_ev_ebitda"] = "" if c["maint_adj_ev_ebitda"] is None else "%.2f" % c["maint_adj_ev_ebitda"]
                    r["price_adj_for_known_usd_m"] = "" if c["price_adj_for_known_usd_m"] is None else "%.2f" % c["price_adj_for_known_usd_m"]
        self.mutate("assessments", fn)


class Clean(Base):
    def test_synthetic_example_is_clean(self):
        rep = self.run_validate()
        self.assertEqual(rep.errors, [])
        self.assertEqual(rep.warnings, [])

    def test_shipped_tables_are_empty_and_match_schema(self):
        rep, counts = vd.validate(os.path.join(ROOT, "data"), SCHEMA)
        self.assertEqual(rep.errors, [])
        self.assertEqual(counts, {"deals": 0, "assessments": 0, "evidence": 0})

    def test_schema_fields_equal_headers(self):
        fields = vd.schema_fields(SCHEMA)
        for t in ("deals", "assessments", "evidence"):
            header, _ = vd.read_table(os.path.join(ROOT, "data", t + ".csv"))
            self.assertEqual(header, fields[t], t)

    def test_enum_values_are_documented_in_the_schema(self):
        with open(SCHEMA, encoding="utf-8") as fh:
            text = fh.read()
        for table, enums in vd.ENUMS.items():
            for field, values in enums.items():
                if field in cg.BREAKER_FIELDS:
                    continue
                for v in values:
                    self.assertIn("`%s`" % v, text, "%s.%s value %s" % (table, field, v))


class EvidenceRules(Base):
    def test_hindsight_in_a_prospective_assessment_is_an_error(self):
        def fn(cols, rows):
            for r in rows:
                if r["assessment_id"] == P and r["question_id"] == "b4":
                    r["source_date"] = "2021-01-01"
        self.mutate("evidence", fn)
        self.assertIn("hindsight", self.messages(self.run_validate()))

    def test_prospective_needs_cutoff_and_source_dates(self):
        self.set_assess(P, information_cutoff="")
        self.assertIn("needs information_cutoff", self.messages(self.run_validate()))

    def test_retrospective_evidence_may_be_late(self):
        rep = self.run_validate()
        self.assertEqual(rep.errors, [])

    def test_non_unknown_answer_needs_supporting_evidence(self):
        def fn(cols, rows):
            rows[:] = [r for r in rows if not (r["assessment_id"] == P and r["question_id"] == "b5")]
        self.mutate("evidence", fn)
        self.assertIn("no 'supports' evidence row for b5", self.messages(self.run_validate()))

    def test_inconclusive_evidence_does_not_back_an_answer(self):
        def fn(cols, rows):
            for r in rows:
                if r["assessment_id"] == P and r["question_id"] == "b5":
                    r["bearing"] = "inconclusive"
        self.mutate("evidence", fn)
        self.assertIn("no 'supports' evidence row for b5", self.messages(self.run_validate()))

    def test_unknown_needs_no_evidence_but_warns_and_grades_horrid(self):
        self.set_assess(P, b5_funding="U")
        self.recompute(P)

        def fn(cols, rows):
            rows[:] = [r for r in rows if not (r["assessment_id"] == P and r["question_id"] == "b5")]
        self.mutate("evidence", fn)
        rep = self.run_validate()
        self.assertEqual(rep.errors, [])
        self.assertTrue(any("unresolved unknown" in w["message"] for w in rep.warnings))
        _, rows = load(os.path.join(self.tmp, "assessments.csv"))
        self.assertEqual([r for r in rows if r["assessment_id"] == P][0]["grade"], "horrid")

    def test_mitigated_needs_notes(self):
        self.set_assess(P, breaker_notes="")
        self.assertIn("breaker_notes is empty", self.messages(self.run_validate()))

    def test_bad_question_id(self):
        def fn(cols, rows):
            rows[0]["question_id"] = "z9"
        self.mutate("evidence", fn)
        self.assertIn("question_id 'z9'", self.messages(self.run_validate()))

    def test_dimension_without_evidence_is_a_warning(self):
        def fn(cols, rows):
            rows[:] = [r for r in rows if not (r["assessment_id"] == P and r["question_id"] == "d3")]
        self.mutate("evidence", fn)
        rep = self.run_validate()
        self.assertEqual(rep.errors, [])
        self.assertTrue(any("d3" in w["message"] for w in rep.warnings))


class ComputedFields(Base):
    def test_tampered_grade_is_caught(self):
        self.set_assess(P, grade="great")
        self.assertIn("grade: recorded 'great', computed 'okay'", self.messages(self.run_validate()))

    def test_tampered_score_is_caught(self):
        self.set_assess(P, weighted_score="50", score_pct="83.3")
        msg = self.messages(self.run_validate())
        self.assertIn("weighted_score", msg)
        self.assertIn("score_pct", msg)

    def test_tampered_maintenance_figure_is_caught(self):
        self.set_assess(P, maint_adj_ebitda_usd_m="99.00")
        self.assertIn("maint_adj_ebitda_usd_m", self.messages(self.run_validate()))

    def test_blank_computed_field_is_caught(self):
        self.set_assess(P, price_adj_for_known_usd_m="")
        self.assertIn("price_adj_for_known_usd_m", self.messages(self.run_validate()))


class MaintenanceRules(Base):
    def test_d9_above_two_with_unknown_maintenance_capex(self):
        self.set_assess(P, maint_capex_usd_m="", d9_maintenance_lifecycle="3")
        self.recompute(P)
        self.assertIn("D9 may not exceed 2", self.messages(self.run_validate()))

    def test_d9_two_with_unknown_maintenance_capex_is_allowed(self):
        self.set_assess(P, maint_capex_usd_m="", d9_maintenance_lifecycle="2")
        self.recompute(P)
        self.assertEqual(self.run_validate().errors, [])

    def test_non_positive_adjusted_ebitda_caps_d4_and_needs_notes(self):
        self.set_assess(P, maint_capex_usd_m="98", maint_notes="")
        self.recompute(P)
        msg = self.messages(self.run_validate())
        self.assertIn("D4 may not exceed 1", msg)
        self.assertIn("maint_notes must explain", msg)

    def test_non_positive_adjusted_ebitda_allowed_when_handled(self):
        self.set_assess(P, maint_capex_usd_m="98", d4_financial_quality="1", maint_notes="Upkeep consumes all EBITDA.")
        self.recompute(P)
        self.assertEqual(self.run_validate().errors, [])

    def test_known_costs_must_include_catchup(self):
        self.set_assess(P, known_upcoming_costs_usd_m="10")
        self.recompute(P)
        self.assertIn("below catchup_capex", self.messages(self.run_validate()))


class Structure(Base):
    def test_header_mismatch(self):
        def fn(cols, rows):
            cols2 = [c for c in cols if c != "notes"]
            for r in rows:
                r.pop("notes", None)
            return cols2, rows
        self.mutate("deals", fn)
        self.assertIn("header does not match", self.messages(self.run_validate()))

    def test_unknown_references(self):
        self.set_assess(P, deal_id="1999-nobody-nothing")
        def fn(cols, rows):
            rows[0]["assessment_id"] = "ghost"
        self.mutate("evidence", fn)
        msg = self.messages(self.run_validate())
        self.assertIn("not in deals.csv", msg)
        self.assertIn("'ghost' not in assessments.csv", msg)

    def test_duplicate_ids(self):
        def fn(cols, rows):
            rows.append(dict(rows[0]))
        self.mutate("evidence", fn)
        self.assertIn("duplicate evidence_id", self.messages(self.run_validate()))

    def test_formats(self):
        self.set_assess(P, assessment_date="18/11/2026", ebitda_usd_m="lots", grade_perspective="boss")
        msg = self.messages(self.run_validate())
        self.assertIn("not a YYYY-MM-DD date", msg)
        self.assertIn("not a number", msg)
        self.assertIn("grade_perspective", msg)


class Cli(Base):
    def run_cli(self, argv, tool=vd):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = tool.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_exit_codes(self):
        code, out, _ = self.run_cli(["--data", self.tmp, "--schema", SCHEMA])
        self.assertEqual(code, 0)
        self.set_assess(P, grade="great")
        code, out, _ = self.run_cli(["--data", self.tmp, "--schema", SCHEMA])
        self.assertEqual(code, 3)
        self.assertIn("ERROR", out)
        code, _, err = self.run_cli(["--data", os.path.join(self.tmp, "missing"), "--schema", SCHEMA])
        self.assertEqual(code, 2)

    def test_calculate_grade_cli(self):
        a = os.path.join(self.tmp, "assessments.csv")
        code, out, _ = self.run_cli([a], tool=cg)
        self.assertEqual(code, 0)
        self.assertIn("okay", out)
        self.assertIn("horrid", out)
        self.set_assess(P, grade="good")
        code, out, _ = self.run_cli([a], tool=cg)
        self.assertEqual(code, 3)
        self.assertIn("MISMATCH", out)
        code, _, err = self.run_cli([os.path.join(self.tmp, "nope.csv")], tool=cg)
        self.assertEqual(code, 2)

    def test_deterministic_json_report(self):
        a = os.path.join(self.tmp, "assessments.csv")
        o1, o2 = os.path.join(self.tmp, "r1.json"), os.path.join(self.tmp, "r2.json")
        self.run_cli([a, "--out", o1], tool=cg)
        self.run_cli([a, "--out", o2], tool=cg)
        with open(o1) as f1, open(o2) as f2:
            self.assertEqual(f1.read(), f2.read())


if __name__ == "__main__":
    unittest.main()
