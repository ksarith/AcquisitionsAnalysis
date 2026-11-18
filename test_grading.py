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
    return cg.grade(breakers or CLEAR, pack, dims)["grade"]


class Bands(unittest.TestCase):
    def test_boundaries_are_inclusive_floors(self):
        cases = {60: "great", 48: "great", 47: "good", 39: "good", 38: "okay", 30: "okay",
                 29: "bad", 21: "bad", 20: "horrid", 15: "horrid"}
        for score, want in cases.items():
            self.assertEqual(g(dims=dims_for(score)), want, score)

    def test_percentages_match_the_documented_bands(self):
        self.assertEqual(cg.grade(CLEAR, "n/a", dims_for(48))["score_pct"], 80.0)
        self.assertEqual(cg.grade(CLEAR, "n/a", dims_for(39))["score_pct"], 65.0)
        self.assertEqual(cg.grade(CLEAR, "n/a", dims_for(30))["score_pct"], 50.0)
        self.assertEqual(cg.grade(CLEAR, "n/a", dims_for(21))["score_pct"], 35.0)

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
        r = cg.grade(dict(CLEAR, b4_liabilities="U"), "n/a", dims_for(60))
        self.assertTrue(r["reasons"])
        self.assertEqual(r["breaker_ceiling"], "horrid")
        self.assertEqual(r["band"], "great")


class BadInput(unittest.TestCase):
    def test_rejects_invalid_values(self):
        d = dims_for(40)
        with self.assertRaises(cg.InputError):
            cg.grade(dict(CLEAR, b1_regulatory="maybe"), "n/a", d)
        with self.assertRaises(cg.InputError):
            cg.grade(dict(CLEAR, b1_regulatory=""), "n/a", d)
        with self.assertRaises(cg.InputError):
            cg.grade(CLEAR, "none", d)
        with self.assertRaises(cg.InputError):
            cg.grade(CLEAR, "n/a", dict(d, d1_strategic_fit=5))
        with self.assertRaises(cg.InputError):
            cg.grade(CLEAR, "n/a", dict(d, d1_strategic_fit=True))
        with self.assertRaises(cg.InputError):
            cg.grade(CLEAR, "n/a", {k: v for k, v in d.items() if k != "d9_maintenance_lifecycle"})


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


if __name__ == "__main__":
    unittest.main()
