"""Packaging, identity, and change-impact fixtures. These are not Godot playtests."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from _identities import artifact_identities, classify_path
import change_impact
import package_and_report
import stamp_web_build


class DeliveryOpsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.project = self.base / "game"
        self.project.mkdir()
        (self.project / "project.godot").write_text('[application]\nconfig/name="fixture"\n', encoding="utf-8")
        (self.project / "scripts").mkdir()
        (self.project / "scripts" / "player.gd").write_text("extends Node\n", encoding="utf-8")
        (self.project / "tests").mkdir()
        (self.project / "tests" / "test_player.gd").write_text("extends GutTest\n", encoding="utf-8")
        (self.project / "assets" / "fonts").mkdir(parents=True)
        (self.project / "assets" / "fonts" / "ui.ttf").write_bytes(b"font-fixture")
        (self.project / "README.md").write_text("docs\n", encoding="utf-8")

    def test_classifies_rules_harness_display_and_packaging(self):
        self.assertEqual(classify_path("scripts/player.gd"), "rules")
        self.assertEqual(classify_path("tests/test_player.gd"), "harness")
        self.assertEqual(classify_path("assets/fonts/ui.ttf"), "display")
        self.assertEqual(classify_path("README.md"), "packaging")
        self.assertEqual(classify_path("export/web/index.html"), "excluded")

    def test_harness_only_change_reuses_game_content(self):
        before = self.base / "before"
        after = self.base / "after"
        package_and_report.stage_source(self.project, before)
        package_and_report.stage_source(self.project, after)
        (after / "tests" / "test_player.gd").write_text("extends GutTest\n# harness only\n", encoding="utf-8")
        result = change_impact.compare_trees(before, after)
        self.assertEqual(result["changedClasses"], ["harness"])
        self.assertIn("harness", result["rerun"])
        self.assertTrue(any(row["suite"] == "rules" for row in result["reused"]))
        self.assertEqual(result["before"]["gameContent"]["sha256"], result["after"]["gameContent"]["sha256"])

    def test_package_and_report_writes_identities_and_zip(self):
        out = self.base / "release"
        report = package_and_report.package_and_report(self.project, out)
        self.assertTrue((out / "game-source.zip").is_file())
        self.assertTrue((out / "delivery_report.json").is_file())
        self.assertTrue((out / "session_status.md").is_file())
        self.assertTrue(report["visualJudgmentRequired"])
        self.assertIn("gameContent", report["identities"])
        self.assertGreater(report["identities"]["gameContent"]["fileCount"], 0)
        self.assertGreater(report["identities"]["testHarness"]["fileCount"], 0)
        staged = Path(report["sourceTree"]["path"])
        self.assertTrue((staged / "project.godot").is_file())
        self.assertFalse((staged / "export" / "web").exists())

    def test_package_and_report_excludes_generated_web_and_stamps_separately(self):
        web = self.project / "export" / "web"
        web.mkdir(parents=True)
        (web / "index.html").write_text(
            '<!doctype html><html><body><canvas id="canvas"></canvas>'
            '<script>const cfg={"canvasResizePolicy":1};</script></body></html>', encoding="utf-8")
        (web / "game.wasm").write_bytes(b"\0asmfixture")
        (web / "game.pck").write_bytes(b"pck-fixture")
        (web / "game.js").write_text('console.log("fixture")', encoding="utf-8")
        out = self.base / "release"
        report = package_and_report.package_and_report(self.project, out, web_export=web)
        self.assertIsNotNone(report["webExport"])
        self.assertTrue(str(report["buildId"]).startswith("WEB-"))
        identities = artifact_identities(Path(report["sourceTree"]["path"]))
        self.assertNotIn("export/web/index.html", sum(identities["classes"].values(), []))
        stamp_web_build.stamp(web)

    def test_changed_paths_without_identity_proof_cannot_reuse(self):
        result = change_impact.impact_from_paths(["tests/test_player.gd"])
        self.assertEqual(result["changedClasses"], ["harness"])
        self.assertIn("rules", result["reuseBlocked"])


if __name__ == "__main__":
    unittest.main()
