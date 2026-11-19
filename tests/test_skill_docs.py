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
        self.assertEqual(m.group(1), "acquisitions-analysis")
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

    def test_hard_rules_are_present(self):
        for phrase in ("never improvise", "hindsight", "own words", "Disclaimer", "U", "computed by hand"):
            self.assertIn(phrase.lower(), self.text.lower(), phrase)

    def test_fast_reference_matches_the_tool(self):
        import sys
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import calculate_grade as cg
        self.assertEqual(cg.MAX_SCORE, 60)
        weights = sorted(cg.DIM_WEIGHTS.values(), reverse=True)
        self.assertEqual(weights, [2, 2, 2, 2, 2, 2, 1, 1, 1])
        self.assertIn("Maximum weighted score 60", self.text)


class ReportTemplate(unittest.TestCase):
    def test_template_covers_the_required_sections(self):
        t = read("docs/report_template.md")
        for s in ("Why this grade", "Breakers", "Dimensions", "Maintenance figures",
                  "Unknowns and evidence gaps", "Contradictions", "What would change the grade", "Limits"):
            self.assertIn(s, t, s)


if __name__ == "__main__":
    unittest.main()
