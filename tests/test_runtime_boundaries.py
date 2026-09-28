"""Regression tests for GPS 1.0 runtime boundaries and packaging."""
from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

class RuntimeBoundaryTests(unittest.TestCase):
    def test_starter_records_inputmap_events_with_source(self):
        text = (ROOT / "assets/starter-2d/qa/qa_bridge.gd").read_text(encoding="utf-8")
        self.assertIn("for action in InputMap.get_actions()", text)
        self.assertIn("event.is_action(action)", text)
        self.assertIn('"source": event.get_class()', text)
        self.assertNotIn("event is not InputEventAction", text)

    def test_starter_qa_is_release_guarded(self):
        text = (ROOT / "assets/starter-2d/qa/qa_bridge.gd").read_text(encoding="utf-8")
        self.assertIn("OS.is_debug_build()", text)
        self.assertIn('OS.has_feature("qa")', text)
        self.assertIn("DISABLED_IN_RELEASE", text)

    def test_starter_declares_godot_43(self):
        project = (ROOT / "assets/starter-2d/project.godot").read_text(encoding="utf-8")
        readme = (ROOT / "assets/starter-2d/README.md").read_text(encoding="utf-8")
        self.assertIn("Godot 4.3+", project)
        self.assertIn("Godot 4.3+", readme)

    def test_subprocess_text_calls_are_utf8_safe(self):
        for name in (
            "run_godot_checks.py",
            "detect_capabilities.py",
            "package_and_report.py",
            "serve_web_export.py",
        ):
            text = (ROOT / "scripts" / name).read_text(encoding="utf-8")
            for line in text.splitlines():
                if "subprocess.run" in line and "text=True" in line:
                    self.assertIn('encoding="utf-8"', line, name)

    def test_game_exp_boundary_is_explicit(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        integration = (ROOT / "references/game-exp-integration.md").read_text(encoding="utf-8")
        variants = (ROOT / "references/variant-experiments.md").read_text(encoding="utf-8")
        self.assertIn("game-exp", skill)
        self.assertIn("protected Ledger", integration)
        self.assertIn("Candidate boundary", variants)
        self.assertIn("must not select one", variants)

class RuntimePackageTests(unittest.TestCase):
    def test_runtime_package_excludes_development_files(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "skill.zip"
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_skill_package.py"), "--out", str(out)],
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with zipfile.ZipFile(out) as zf:
                names = set(zf.namelist())
            self.assertIn("SKILL.md", names)
            self.assertIn("agents/openai.yaml", names)
            self.assertIn("references/godot-practical-guide.md", names)
            self.assertNotIn("CHANGELOG.md", names)
            self.assertFalse(any(name.startswith("audit/") for name in names))
            self.assertFalse(any(name.startswith("tests/") for name in names))
            self.assertNotIn("references/research-basis.md", names)
            self.assertNotIn("references/instruction-audit.md", names)

if __name__ == "__main__":
    unittest.main()
