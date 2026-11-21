import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import calculate_grade as cg  # noqa: E402

CLEAR = {f: "N" for f in cg.BREAKER_FIELDS}
W1 = ["d6_synergies", "d7_integration", "d8_regulatory_geo"]


def dims_for(target):
    """Dimension scores (none zero) with the given weighted score, 15 to 60."""
    d = {f: 1 for f in cg.DIM_WEIGHTS}
    rem = target - 15
    assert 0 <= rem <= 45
    if rem % 2:
        d[W1[0]] += 1
        rem -= 1
    for f in sorted(cg.DIM_WEIGHTS, key=lambda k: -cg.DIM_WEIGHTS[k]):   # weight-2 dims first
        w = cg.DIM_WEIGHTS[f]
        while rem >= w and d[f] < 4:
            d[f] += 1
            rem -= w
    assert rem == 0, (target, rem)
    assert sum(d[f] * cg.DIM_WEIGHTS[f] for f in d) == target
    return d


def g(breakers=None, pack="n/a", dims=None):
    return cg.structural_grade(breakers or CLEAR, pack, dims)["structural_grade"]


class Bands(unittest.TestCase):
    def test_boundaries_are_inclusive_floors(self):
        cases = {60: "great", 48: "great", 47: "good", 39: "good", 38: "okay", 30: "okay",
                 29: "bad", 21: "bad", 20: "horrid", 15: "horrid"}
        for score, want in cases.items():
            self.assertEqual(g(dims=dims_for(score)), want, score)

    def test_percentages_match_the_documented_bands(self):
        self.assertEqual(cg.structural_grade(CLEAR, "n/a", dims_for(48))["score_pct"], 80.0)
        self.assertEqual(cg.structural_grade(CLEAR, "n/a", dims_for(39))["score_pct"], 65.0)
        self.assertEqual(cg.structural_grade(CLEAR, "n/a", dims_for(30))["score_pct"], 50.0)
        self.assertEqual(cg.structural_grade(CLEAR, "n/a", dims_for(21))["score_pct"], 35.0)

    def test_max_score_is_60(self):
        self.assertEqual(cg.MAX_SCORE, 60)


class Precedence(unittest.TestCase):
    """The v0.1 table checked zero-dimension before percentage, so a 0% deal graded Bad
    while a 20% deal graded Horrid. The worst-of rule must never invert."""

    def test_all_zero_is_horrid_not_bad(self):
        self.assertEqual(g(dims={f: 0 for f in cg.DIM_WEIGHTS}), "horrid")

    def test_zero_dimension_caps_at_bad(self):
        d = {f: 4 for f in cg.DIM_WEIGHTS}
        d["d6_synergies"] = 0
        self.assertEqual(g(dims=d), "bad")

    def test_zero_dimension_with_low_score_still_horrid(self):
        d = {f: 1 for f in cg.DIM_WEIGHTS}
        d["d6_synergies"] = 0
        self.assertEqual(g(dims=d), "horrid")

    def test_worse_deal_never_gets_better_grade(self):
        order = cg.GRADES
        for score in range(15, 61):
            d = dims_for(score)
            plain = g(dims=d)
            zeroed = dict(d, d6_synergies=0)
            self.assertLessEqual(order.index(g(dims=zeroed)), order.index(plain), score)
        # the specific inversion in v0.1
        self.assertLessEqual(cg.GRADES.index(g(dims={f: 0 for f in cg.DIM_WEIGHTS})),
                             cg.GRADES.index(g(dims=dims_for(18))))

    def test_mitigated_breaker_caps_at_okay(self):
        b = dict(CLEAR, b7_quality_standing="M")
        self.assertEqual(g(b, dims=dims_for(60)), "okay")
        self.assertEqual(g(b, dims=dims_for(30)), "okay")
        self.assertEqual(g(b, dims=dims_for(25)), "bad")        # score below the cap wins

    def test_unmitigated_breaker_is_horrid_whatever_the_score(self):
        for a in ("Y", "U"):
            self.assertEqual(g(dict(CLEAR, b4_liabilities=a), dims=dims_for(60)), "horrid", a)

    def test_pack_breakers(self):
        self.assertEqual(g(pack="unmitigated", dims=dims_for(60)), "horrid")
        self.assertEqual(g(pack="mitigated", dims=dims_for(60)), "okay")
        self.assertEqual(g(pack="clear", dims=dims_for(60)), "great")

    def test_mitigated_plus_zero_dimension_takes_the_worse_cap(self):
        d = {f: 4 for f in cg.DIM_WEIGHTS}
        d["d9_maintenance_lifecycle"] = 0
        self.assertEqual(g(dict(CLEAR, b2_customer_concentration="M"), dims=d), "bad")

    def test_reasons_are_reported(self):
        r = cg.structural_grade(dict(CLEAR, b4_liabilities="U"), "n/a", dims_for(60))
        self.assertTrue(r["reasons"])
        self.assertEqual(r["breaker_ceiling"], "horrid")
        self.assertEqual(r["band"], "great")


class BadInput(unittest.TestCase):
    def test_rejects_invalid_values(self):
        d = dims_for(40)
        with self.assertRaises(cg.InputError):
            cg.structural_grade(dict(CLEAR, b1_regulatory="maybe"), "n/a", d)
        with self.assertRaises(cg.InputError):
            cg.structural_grade(dict(CLEAR, b1_regulatory=""), "n/a", d)
        with self.assertRaises(cg.InputError):
            cg.structural_grade(CLEAR, "none", d)
        with self.assertRaises(cg.InputError):
            cg.structural_grade(CLEAR, "n/a", dict(d, d1_strategic_fit=5))
        with self.assertRaises(cg.InputError):
            cg.structural_grade(CLEAR, "n/a", dict(d, d1_strategic_fit=True))
        with self.assertRaises(cg.InputError):
            cg.structural_grade(CLEAR, "n/a", {k: v for k, v in d.items() if k != "d9_maintenance_lifecycle"})


class Maintenance(unittest.TestCase):
    ROW = {"ebitda_usd_m": "100", "maint_capex_usd_m": "30", "warranty_normalization_usd_m": "5",
           "known_upcoming_costs_usd_m": "80"}

    def test_figures(self):
        m = cg.maintenance(self.ROW, 1200.0)
        self.assertEqual(m["maint_adj_ebitda_usd_m"], 65.0)
        self.assertEqual(m["maint_adj_ev_ebitda"], 18.46)
        self.assertEqual(m["price_adj_for_known_usd_m"], 1120.0)
        self.assertFalse(m["adjusted_ebitda_not_positive"])

    def test_non_positive_adjusted_ebitda_leaves_multiple_blank_and_flags(self):
        m = cg.maintenance(dict(self.ROW, maint_capex_usd_m="98"), 1200.0)
        self.assertEqual(m["maint_adj_ebitda_usd_m"], -3.0)
        self.assertIsNone(m["maint_adj_ev_ebitda"])
        self.assertTrue(m["adjusted_ebitda_not_positive"])
        m0 = cg.maintenance(dict(self.ROW, maint_capex_usd_m="95"), 1200.0)
        self.assertEqual(m0["maint_adj_ebitda_usd_m"], 0.0)
        self.assertTrue(m0["adjusted_ebitda_not_positive"])

    def test_blank_inputs_stay_unknown(self):
        for blank in ("ebitda_usd_m", "maint_capex_usd_m", "warranty_normalization_usd_m"):
            m = cg.maintenance(dict(self.ROW, **{blank: ""}), 1200.0)
            self.assertIsNone(m["maint_adj_ebitda_usd_m"], blank)
            self.assertIsNone(m["maint_adj_ev_ebitda"], blank)
        m = cg.maintenance(dict(self.ROW, known_upcoming_costs_usd_m=""), 1200.0)
        self.assertIsNone(m["price_adj_for_known_usd_m"])

    def test_unknown_enterprise_value(self):
        m = cg.maintenance(self.ROW, None)
        self.assertEqual(m["maint_adj_ebitda_usd_m"], 65.0)
        self.assertIsNone(m["maint_adj_ev_ebitda"])
        self.assertIsNone(m["price_adj_for_known_usd_m"])


NS = {k: 80 for k in cg.N_WEIGHTS}


def neg(**over):
    d = dict(NS)
    d.update(over)
    return cg.negotiation(d)


class Negotiation(unittest.TestCase):
    def test_weights_sum_to_100_and_groups_match_the_method(self):
        self.assertEqual(sum(cg.N_WEIGHTS.values()), 100)
        w = cg.N_WEIGHTS
        self.assertEqual(w["n1_preparation"] + w["n2_information_discovery"] + w["n3_value_creation"] + w["n4_communication"], 50)
        self.assertEqual(w["n5_value_capture"] + w["n6_objective_alignment"] + w["n7_relationship"], 30)
        self.assertEqual(w["n8_risk_allocation"] + w["n9_epistemic_integrity"] + w["n10_procedural_legitimacy"], 20)

    def test_bands_are_inclusive_floors(self):
        cases = {100: "exceptional", 95: "exceptional", 94: "high_quality", 85: "high_quality", 84: "competent",
                 70: "competent", 69: "marginal", 55: "marginal", 54: "poor", 40: "poor"}
        for v, want in cases.items():
            r = cg.negotiation({k: v for k in cg.N_WEIGHTS})
            self.assertEqual(r["negotiation_classification"], want, v)
            self.assertEqual(r["nqs"], float(v))

    def test_all_39_fires_every_predicate(self):
        r = cg.negotiation({k: 39 for k in cg.N_WEIGHTS})
        self.assertEqual(r["failure_predicates"], ["F1", "F2", "F3"])
        self.assertEqual(r["negotiation_classification"], "failed")

    def test_each_predicate_fires_alone_and_threshold_is_exclusive(self):
        for code, dim in cg.PREDICATES:
            r = neg(**{dim: 39})
            self.assertEqual(r["failure_predicates"], [code])
            self.assertEqual(r["negotiation_classification"], "failed")
            ok = neg(**{dim: 40})
            self.assertEqual(ok["failure_predicates"], [])
            self.assertNotEqual(ok["negotiation_classification"], "failed")

    def test_high_average_cannot_offset_a_predicate(self):
        r = neg(**{**{k: 100 for k in cg.N_WEIGHTS}, "n9_epistemic_integrity": 10})
        self.assertEqual(r["negotiation_classification"], "failed")
        self.assertGreater(r["nqs"], 90)

    def test_unknown_is_never_a_pass(self):
        """The v0.1.0 draft skipped blank dimensions, so a blank N9 graded better than N9 = 10."""
        blank = neg(n9_epistemic_integrity="")
        low = neg(n9_epistemic_integrity=10)
        self.assertEqual(blank["negotiation_classification"], "unresolved")
        self.assertIsNone(blank["nqs"])
        self.assertEqual(low["negotiation_classification"], "failed")
        self.assertEqual(cg.NEG_TO_OVERALL["unresolved"], cg.NEG_TO_OVERALL["failed"])

    def test_any_blank_dimension_is_unresolved_not_averaged(self):
        for k in cg.N_WEIGHTS:
            r = neg(**{k: None})
            self.assertEqual(r["negotiation_classification"], "unresolved", k)
            self.assertIsNone(r["nqs"], k)
            self.assertEqual(r["missing"], [k])

    def test_all_blank_is_unresolved(self):
        r = cg.negotiation({})
        self.assertEqual(r["negotiation_classification"], "unresolved")

    def test_predicate_fires_even_with_other_dimensions_unknown(self):
        r = neg(n9_epistemic_integrity="", n8_risk_allocation=10)
        self.assertEqual(r["negotiation_classification"], "failed")
        self.assertEqual(r["failure_predicates"], ["F2"])
        self.assertIsNone(r["nqs"])

    def test_whole_numbers_only(self):
        for bad in (80.5, "80.5", "abc", -1, 101, True, "1e2"):
            with self.assertRaises(cg.InputError, msg=repr(bad)):
                neg(n1_preparation=bad)

    def test_multiplicative_diagnostic_collapses_on_a_critical_failure(self):
        hi = neg(**{k: 90 for k in cg.N_WEIGHTS})["nq_multiplicative"]
        lo = neg(**{**{k: 90 for k in cg.N_WEIGHTS}, "n9_epistemic_integrity": 10})["nq_multiplicative"]
        self.assertGreater(hi, 0.5)
        self.assertLess(lo, hi / 5)
        self.assertEqual(cg.negotiation({k: 100 for k in cg.N_WEIGHTS})["nq_multiplicative"], 1.0)
        self.assertIsNone(neg(n2_information_discovery="")["nq_multiplicative"])

    def test_multiplicative_never_changes_the_classification(self):
        a = neg(**{k: 95 for k in cg.N_WEIGHTS})
        b = neg(**{**{k: 95 for k in cg.N_WEIGHTS}, "n6_objective_alignment": 41})
        self.assertEqual(a["negotiation_classification"], "exceptional")
        self.assertNotEqual(a["nq_multiplicative"], b["nq_multiplicative"])


class Overall(unittest.TestCase):
    def sg(self, grade_target):
        d = {"great": 60, "good": 42, "okay": 33, "bad": 24, "horrid": 15}[grade_target]
        return cg.structural_grade(CLEAR, "n/a", dims_for(d))

    def test_worse_of_the_two_sides(self):
        s = self.sg("great")
        for neg_class, want in (("failed", "horrid"), ("poor", "bad"), ("marginal", "okay"),
                                ("competent", "good"), ("high_quality", "great"), ("exceptional", "great")):
            n = {"negotiation_classification": neg_class}
            o = cg.overall("both", s, n)
            self.assertEqual(o["overall_integrity_verdict"], want, neg_class)

    def test_structural_horrid_beats_exceptional_negotiation(self):
        o = cg.overall("both", self.sg("horrid"), {"negotiation_classification": "exceptional"})
        self.assertEqual(o["overall_integrity_verdict"], "horrid")
        self.assertEqual(o["overall_driver"], "structural")

    def test_structural_great_cannot_hide_a_failed_negotiation(self):
        o = cg.overall("both", self.sg("great"), {"negotiation_classification": "failed"})
        self.assertEqual(o["overall_integrity_verdict"], "horrid")
        self.assertEqual(o["overall_driver"], "negotiation")

    def test_tie_reports_both(self):
        o = cg.overall("both", self.sg("good"), {"negotiation_classification": "competent"})
        self.assertEqual((o["overall_integrity_verdict"], o["overall_driver"]), ("good", "both"))

    def test_single_side_scopes(self):
        s = self.sg("okay")
        self.assertEqual(cg.overall("structural", s, None)["overall_integrity_verdict"], "okay")
        o = cg.overall("negotiation", None, {"negotiation_classification": "competent"})
        self.assertEqual((o["overall_integrity_verdict"], o["overall_driver"]), ("good", "negotiation"))

    def test_provisional_flag(self):
        clear = self.sg("great")
        unk = cg.structural_grade(dict(CLEAR, b5_funding="U"), "n/a", dims_for(60))
        self.assertEqual(cg.overall("structural", clear, None)["overall_provisional"], "no")
        self.assertEqual(cg.overall("structural", unk, None)["overall_provisional"], "yes")
        self.assertEqual(cg.overall("negotiation", None, {"negotiation_classification": "unresolved"})["overall_provisional"], "yes")
        self.assertEqual(cg.overall("negotiation", None, {"negotiation_classification": "failed"})["overall_provisional"], "no")

    def test_every_negotiation_class_maps_to_the_shared_scale(self):
        self.assertEqual(set(cg.NEG_TO_OVERALL), cg.NEG_CLASSES)
        self.assertTrue(set(cg.NEG_TO_OVERALL.values()) <= set(cg.GRADES))

    def test_compute_row_requires_a_valid_scope(self):
        for bad in ("", "bogus", "BOTH"):
            with self.assertRaises(cg.InputError, msg=repr(bad)):
                cg.compute_row({"assessment_scope": bad}, None)

    def test_non_numeric_dimension_is_an_input_error_not_a_crash(self):
        row = {"assessment_scope": "structural", "pack_breakers": "n/a"}
        row.update({f: "N" for f in cg.BREAKER_FIELDS})
        row.update({f: "4" for f in cg.DIM_WEIGHTS})
        row["d1_strategic_fit"] = "x"
        with self.assertRaises(cg.InputError):
            cg.compute_row(row, None)


if __name__ == "__main__":
    unittest.main()
