"""experience-validation instruction tests; not live gameplay or human-player evidence."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ExperienceValidationUpgradeTests(unittest.TestCase):
    def test_version_and_routes(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(len(version.split(".")), 3)
        self.assertGreaterEqual(tuple(map(int, version.split("."))), (0, 8, 0))
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("experience-validation-loop.md", skill)
        self.assertIn("runtime-logic-verification.md", skill)
        runtime = (ROOT / "references" / "runtime-logic-verification.md").read_text(encoding="utf-8")
        self.assertIn("acceptance is conjunctive", runtime)

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


    def test_optional_opportunity_v04_preserves_real_player_boundary(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        playtest = (ROOT / "references/playtest-and-player-qa.md").read_text(encoding="utf-8")
        for phrase in ("game-opportunity", "unique players", "human Review", "digest"):
            self.assertIn(phrase.casefold(), (skill + playtest).casefold())
        self.assertIn("never average conflicting aggregates", playtest)
        self.assertIn("normal Godot playtest schema unchanged", playtest)


if __name__ == "__main__":
    unittest.main()
