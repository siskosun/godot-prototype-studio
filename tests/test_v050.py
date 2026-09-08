"""Regression coverage for 0.5.0 gameplay discovery and visual-reference intake."""
from __future__ import annotations
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
import init_workspace
import validate_mission_brief as brief


class TempCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)

    def cli(self, module, *args):
        with mock.patch.object(sys, "argv", [module.__file__, *map(str, args)]), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return module.main()


class WorkspaceTests(TempCase):
    def test_mechanic_lab_is_opt_in(self):
        self.assertEqual(self.cli(init_workspace, self.base, "--novel-gameplay"), 0)
        self.assertTrue((self.base / ".prototype/spec/mechanic_lab.md").exists())
        self.assertFalse((self.base / ".prototype/spec/prototype_contract.md").exists())

    def test_mechanic_lab_does_not_overwrite_user_record(self):
        target = self.base / ".prototype/spec/mechanic_lab.md"
        target.parent.mkdir(parents=True)
        target.write_text("user-owned", encoding="utf-8")
        self.assertEqual(self.cli(init_workspace, self.base, "--novel-gameplay"), 0)
        self.assertEqual(target.read_text(encoding="utf-8"), "user-owned")


class VisualIntentTests(unittest.TestCase):
    @staticmethod
    def base() -> str:
        return """# Mission Brief
## Outcome
Playable result
## Delivery
Local project
## Success
Observable success
## Evidence Required
Runtime evidence
## Boundaries
No destructive work
## Non-goals
No public release
## Execution Authority
Reversible local changes delegated
## Completion
DONE when requirements pass; BLOCKED on a genuine blocker
"""

    def with_visual(self, body: str) -> str:
        return self.base() + "\n## Visual Reference Intent\n" + body + "\n"

    def test_partial_reference_requires_scope(self):
        self.assertTrue(brief.validate_text(self.with_visual("- Mode: PARTIAL_REFERENCE\n- Partial scope: not applicable")))
        self.assertEqual(brief.validate_text(self.with_visual("- Mode: PARTIAL_REFERENCE\n- Images: concept.png\n- Partial scope: camera and composition only")), [])

    def test_pixel_reference_requires_target_and_rights(self):
        invalid = brief.validate_text(self.with_visual("- Mode: PIXEL_ACCURATE_REFERENCE\n- Pixel targets: not applicable\n- Rights status: unknown"))
        self.assertTrue(any("Pixel targets" in item for item in invalid))
        self.assertTrue(any("Rights status" in item for item in invalid))
        valid = self.with_visual("- Mode: PIXEL_ACCURATE_REFERENCE\n- Images: owned.png\n- Pixel targets: main menu at 1280x720, full viewport\n- Rights status: user confirms ownership")
        self.assertEqual(brief.validate_text(valid), [])

    def test_original_delegated_is_valid(self):
        self.assertEqual(brief.validate_text(self.with_visual("- Mode: ORIGINAL_DELEGATED\n- Images: none supplied")), [])

    def test_not_applicable_requires_reason(self):
        self.assertTrue(brief.validate_text(self.with_visual("- Mode: NOT_APPLICABLE")))
        valid = self.with_visual("- Mode: NOT_APPLICABLE\n- Reason: logic-only diagnostic graybox")
        self.assertEqual(brief.validate_text(valid), [])

    def test_legacy_brief_remains_valid(self):
        self.assertEqual(brief.validate_text(self.base()), [])


if __name__ == "__main__":
    unittest.main()
