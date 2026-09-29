from __future__ import annotations

import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class IterationDeliveryV102Tests(unittest.TestCase):
    def test_version_and_skill_contract(self):
        self.assertEqual((ROOT / "VERSION").read_text(encoding="utf-8").strip(), "1.0.4")
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("iteration_delivery", skill)
        self.assertIn("participant-reported implementation context", skill)

    def test_game_exp_delivery_contract_preserves_human_gates(self):
        text = (ROOT / "references" / "game-exp-integration.md").read_text(encoding="utf-8")
        for phrase in (
            "SHAREABLE_URL | LOCAL_URL | ARTIFACT_ONLY | MISSING",
            "producer",
            "previous_candidate_id",
            "participant_reported",
            "experiment_panel.delivery_card",
            "never invent a URL",
            "publish_github_pages.py",
            "play/<result_source_sha>/",
            "WEB_PREFLIGHT",
            "thread_support=false",
        ):
            self.assertIn(phrase, text)
        for gate in ("Review", "PROMISING", "SELECTED", "REJECTED"):
            self.assertIn(gate, text)


if __name__ == "__main__":
    unittest.main()
