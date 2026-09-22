"""0.8 experience-validation instruction tests; not live gameplay or human-player evidence."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ExperienceValidationUpgradeTests(unittest.TestCase):
    def test_version_and_routes(self):
        self.assertEqual((ROOT / "VERSION").read_text().strip(), "0.8.0")
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("experience-validation-loop.md", skill)
        self.assertIn("runtime-logic-verification.md", skill)
        self.assertIn("Core requirements all pass", skill)

    def test_experience_loop_preserves_evidence_boundary(self):
        text = (ROOT / "references" / "experience-validation-loop.md").read_text(encoding="utf-8")
        self.assertIn("Lower layers cannot prove higher ones", text)
        self.assertIn("There is no universal minimum participant count", text)
        self.assertIn("Do not infer a participant's internal emotion", text)

    def test_runtime_logic_requires_oracle_sanity_without_forcing_universal_tick_checks(self):
        text = (ROOT / "references" / "runtime-logic-verification.md").read_text(encoding="utf-8")
        self.assertIn("known-bad fixture", text)
        self.assertIn("Do not sample every tick by default", text)
        self.assertIn("acceptance is conjunctive", text)
        self.assertIn("Same-rule harder scenario", text)

    def test_mechanic_lab_exposes_contract_without_becoming_acceptance_authority(self):
        text = (ROOT / "templates" / "mechanic_lab.md").read_text(encoding="utf-8")
        self.assertIn("delivery acceptance remains in the mission brief", text)
        self.assertIn("Core required outcomes (all must pass)", text)
        self.assertIn("Known-bad disposable fixture or mutant", text)


if __name__ == "__main__":
    unittest.main()
