"""Keeps the plugin's always-read text small.

Every agent and skill body here is loaded into context whenever it runs, and Claude Code trims
re-attached skills past 20,000 bytes after compaction. Rarely needed material belongs in a skill's
references/ folder, read only at the step that needs it.

Run: python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
LIMIT = 19_000
DESCRIPTION_LIMIT = 1_000


class SizeTests(unittest.TestCase):
    def files(self):
        return sorted(PLUGIN.glob("skills/*/SKILL.md")) + sorted(PLUGIN.glob("agents/*.md"))

    def test_bodies_under_limit(self):
        for path in self.files():
            with self.subTest(path=path.relative_to(PLUGIN)):
                self.assertLess(path.stat().st_size, LIMIT)

    def test_descriptions(self):
        for path in self.files():
            text = path.read_text(encoding="utf-8")
            match = re.search(r"^description: (.+)$", text, re.M)
            with self.subTest(path=path.relative_to(PLUGIN)):
                self.assertIsNotNone(match)
                self.assertLess(len(match.group(1)), DESCRIPTION_LIMIT)
                if "skills/" in str(path):
                    # Skill descriptions say only when to use them; a summary of the workflow makes
                    # the model follow the summary instead of reading the skill.
                    self.assertTrue(match.group(1).startswith("Use when"))


if __name__ == "__main__":
    unittest.main()
