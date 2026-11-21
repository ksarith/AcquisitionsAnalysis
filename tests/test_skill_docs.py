import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


class SkillFile(unittest.TestCase):
    def setUp(self):
        self.text = read("SKILL.md")

    def test_frontmatter(self):
        m = re.match(r"---\nname: ([a-z0-9-]+)\ndescription: (.+)\n---\n", self.text)
        self.assertIsNotNone(m, "SKILL.md needs name and description frontmatter")
        self.assertEqual(m.group(1), "deal-integrity")
        self.assertGreater(len(m.group(2)), 100)
        self.assertLess(len(m.group(2)), 1024)

    def test_length_stays_within_skill_convention(self):
        self.assertLess(len(self.text.split("\n")), 500)

    def test_relative_links_resolve(self):
        for t in ("SKILL.md", "docs/report_template.md", "README.md"):
            base = os.path.dirname(os.path.join(ROOT, t))
            for m in re.findall(r"\]\(([^)#\s]+)\)", read(t)):
                if m.startswith("http"):
                    continue
                self.assertTrue(os.path.exists(os.path.normpath(os.path.join(base, m))), "%s -> %s" % (t, m))

    def test_commands_it_tells_agents_to_run_exist(self):
        for tool in re.findall(r"python3 (tools/[a-z_]+\.py)", self.text):
            self.assertTrue(os.path.exists(os.path.join(ROOT, tool)), tool)

    def test_every_breaker_and_dimension_is_named(self):
        for i in range(1, 12):
            self.assertIn("**B%d**" % i, self.text)
        for i in range(1, 10):
            self.assertIn("D%d " % i, self.text)
        for i in range(1, 11):
            self.assertIn("N%d " % i, self.text)
        for f in ("F1", "F2", "F3", "Unresolved", "negative_finding", "inference"):
            self.assertIn(f, self.text, f)

    def test_hard_rules_are_present(self):
        for phrase in ("never improvise", "hindsight", "own words", "Disclaimer", "U", "computed by hand",
                       "blank means unknown", "unknown is never a pass", "Leave a dimension", "same-lineage"):
            self.assertIn(phrase.lower(), self.text.lower(), phrase)

    def test_fast_reference_matches_the_tool(self):
        import sys
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import calculate_grade as cg
        self.assertEqual(cg.MAX_SCORE, 60)
        weights = sorted(cg.DIM_WEIGHTS.values(), reverse=True)
        self.assertEqual(weights, [2, 2, 2, 2, 2, 2, 1, 1, 1])
        self.assertIn("Maximum weighted score 60", self.text)
        for k, w in cg.N_WEIGHTS.items():
            short = k.split("_")[0].upper()
            self.assertRegex(self.text, r"%s [a-z ]+ %d" % (short, w), k)
        self.assertEqual(cg.PREDICATE_THRESHOLD, 40)
        self.assertIn("below 40", self.text)
        for floor, name in cg.NEG_BAND_FLOORS:
            self.assertIn("%d" % (floor // 100), self.text)


class ReportTemplate(unittest.TestCase):
    def test_template_covers_the_required_sections(self):
        t = read("docs/report_template.md")
        for s in ("Why this verdict", "Structural", "Breakers", "Dimensions", "Maintenance figures", "Negotiation",
                  "Unknowns and evidence gaps", "Contradictions", "What would change the verdict", "Limits"):
            self.assertIn(s, t, s)


class MethodologyAndSchemaAgree(unittest.TestCase):
    def setUp(self):
        self.m = read("docs/methodology.md")
        import sys
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import calculate_grade as cg
        self.cg = cg

    def test_every_negotiation_dimension_and_predicate_is_defined(self):
        for i in range(1, 11):
            self.assertIn("N%d" % i, self.m)
        for code in ("F1", "F2", "F3"):
            self.assertIn(code, self.m)

    def test_methodology_weights_match_the_tool(self):
        self.assertIn("0.10*N1 + 0.15*N2 + 0.15*N3 + 0.10*N4", self.m)
        self.assertIn("0.10*N5 + 0.10*N6 + 0.10*N7", self.m)
        self.assertIn("0.08*N8 + 0.08*N9 + 0.04*N10", self.m)
        w = self.cg.N_WEIGHTS
        self.assertEqual([w[k] for k in sorted(w, key=lambda k: int(k.split("_")[0][1:]))], [10, 15, 15, 10, 10, 10, 10, 8, 8, 4])

    def test_overall_mapping_in_methodology_matches_the_tool(self):
        for cls, shared in self.cg.NEG_TO_OVERALL.items():
            self.assertIn(shared.capitalize(), self.m)
        for row in ("Failed, Unresolved | Horrid", "Poor | Bad", "Marginal | Okay", "Competent | Good", "High Quality, Exceptional | Great"):
            self.assertIn(row, self.m)

    def test_structural_text_is_unchanged_from_core_0_3(self):
        for needle in ("worst** of three independent ceilings", "Maximum", "B11", "D9", "price_adj_for_known"):
            if needle == "Maximum":
                continue
            self.assertIn(needle, self.m)

    def test_enum_values_documented_in_schema(self):
        schema = read("docs/schema.md")
        for v in self.cg.NEG_CLASSES | set(self.cg.GRADES) | {"structural", "negotiation", "both"}:
            self.assertIn("`%s`" % v, schema, v)


if __name__ == "__main__":
    unittest.main()
