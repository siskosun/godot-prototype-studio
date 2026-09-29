"""evaluation-interface tests; not live Godot execution or human-playtest evidence."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_validator():
    path = ROOT / "scripts" / "validate_replay_trace.py"
    spec = importlib.util.spec_from_file_location("validate_replay_trace", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class EvaluationInterfaceUpgradeTests(unittest.TestCase):
    def test_version_and_skill_route(self):
        self.assertIn((ROOT / "VERSION").read_text().strip(), {"1.0.1", "1.0.2", "1.0.3", "1.0.4"})
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("evaluation-interface.md", skill)
        contract = (ROOT / "references" / "evaluation-interface.md").read_text(encoding="utf-8")
        self.assertIn("TRUSTED_OBSERVED", contract)
        self.assertIn("PARTICIPANT_REPORTED", contract)
        self.assertIn("HUMAN_REPORTED", contract)

    def test_starter_exposes_truthful_evaluation_interface(self):
        bridge = (
            ROOT / "assets" / "starter-2d" / "qa" / "qa_bridge.gd"
        ).read_text(encoding="utf-8")
        for phrase in (
            "func configure_seed",
            "func start_input_recording",
            "func stop_input_recording",
            "func inject_action",
            "func step_frames",
            "func replay_trace",
            "SCENE_CONTROLLED",
            "GLOBAL_RNG_ONLY",
            "REALTIME_PHYSICS_WAIT",
            "it is not deterministic manual stepping",
        ):
            self.assertIn(phrase, bridge)

    def test_replay_trace_template_validates(self):
        validator = load_validator()
        value = json.loads(
            (ROOT / "templates" / "replay_trace.json").read_text(encoding="utf-8")
        )
        result = validator.validate_trace(value)
        self.assertTrue(result["valid"])
        self.assertEqual(result["actionCount"], 2)
        self.assertIn("no replay execution is proven", result["claim"])

    def test_replay_trace_rejects_backwards_frames(self):
        validator = load_validator()
        value = json.loads(
            (ROOT / "templates" / "replay_trace.json").read_text(encoding="utf-8")
        )
        value["actions"][1]["frame"] = -1
        with self.assertRaises(validator.TraceError):
            validator.validate_trace(value)

    def test_contract_keeps_exploration_and_replay_separate(self):
        text = (ROOT / "references" / "evaluation-interface.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "Separate exploration from replay",
            "trusted clean workflow",
            "three outcomes",
            "MACHINE_DOMINATED",
            "Do not add Elo",
            "not a product defect",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
