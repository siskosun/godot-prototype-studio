from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from design_repair import capture_context, create_plan, validate_map, verify_repair
from run_godot_checks import run_command


class DesignRepairFixture:
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        shutil.copytree(ROOT / "assets/starter-2d", self.root, dirs_exist_ok=True)
        self.design = json.loads((ROOT / "templates/design_map.json").read_text())

    def observed(self, text="ERROR: FAIL: move action changes authoritative state", returncode=1):
        context = capture_context(self.root, self.design)
        check = run_command("test", [sys.executable, "-c", f"import sys; print({text!r}); sys.exit({returncode})"],
                            self.root / ".prototype/evidence/godot-checks", 10)
        return {"projectRoot": str(self.root), "designMapEvidence": context, "checks": [check],
                "overall": "PASS" if check["status"] == "PASS" else "FAIL"}

    def repaired(self):
        report = self.observed()
        plan = create_plan(self.root, self.design, report)
        with (self.root / "scripts/game_model.gd").open("a") as handle:
            handle.write("\n# local implementation change\n")
        after = self.observed("TESTS PASS", 0)
        # Unit fixtures simulate two executions of the same harness command.
        after["checks"][0]["command"] = plan["checkCommands"]["test"]
        return plan, after

class DesignRepairTests(DesignRepairFixture, unittest.TestCase):
    def test_observed_failure_localizes_interaction_and_preserves_oracle(self):
        result = create_plan(self.root, self.design, self.observed())
        self.assertEqual(result["status"], "REPAIRABLE")
        self.assertEqual(result["repairPaths"], ["scripts/game_model.gd"])
        self.assertEqual(result["failures"][0]["interactions"], ["move-player"])
        self.assertEqual(result["failures"][0]["scenarios"], ["movement-count", "movement-state"])
        self.assertEqual(result["evidenceClass"], "PARTICIPANT_REPORTED")
        self.assertNotIn("review", result)

    def test_exit_zero_with_actionable_error_still_localizes_failure(self):
        report = self.observed(returncode=0)
        self.assertEqual(report["checks"][0]["status"], "FAIL")
        self.assertEqual(create_plan(self.root, self.design, report)["status"], "REPAIRABLE")

    def test_stack_resource_path_is_only_a_candidate_localization(self):
        report = self.observed("SCRIPT ERROR: Invalid call\n at: res://scripts/game_model.gd:23")
        result = create_plan(self.root, self.design, report)
        self.assertEqual(result["status"], "REPAIRABLE")
        self.assertEqual(result["failures"][0]["localization"], "RESOURCE_PATH_CANDIDATES")

    def test_unmapped_failure_does_not_recommend_whole_project(self):
        result = create_plan(self.root, self.design, self.observed("ERROR: unrelated failure"))
        self.assertEqual(result["status"], "INCONCLUSIVE")
        self.assertEqual(result["repairPaths"], [])

    def test_one_mapped_error_cannot_hide_a_second_unmapped_error(self):
        report = self.observed("ERROR: FAIL: move action changes authoritative state\nERROR: another subsystem failed")
        self.assertEqual(create_plan(self.root, self.design, report)["status"], "INCONCLUSIVE")

    def test_marker_printed_outside_error_lines_cannot_localize(self):
        report = self.observed("Expected FAIL: move action changes authoritative state\nERROR: unrelated failure")
        self.assertEqual(create_plan(self.root, self.design, report)["status"], "INCONCLUSIVE")

    def test_resource_path_in_command_header_cannot_localize(self):
        report = self.observed("ERROR: unrelated failure")
        # The command header is attacker/participant-controlled text, not observed output.
        report["checks"][0] = run_command(
            "test", [sys.executable, "-c", "import sys; print('ERROR: unrelated failure'); sys.exit(1) # res://scripts/game_model.gd:3"],
            self.root / ".prototype/evidence/godot-checks", 10)
        self.assertEqual(create_plan(self.root, self.design, report)["status"], "INCONCLUSIVE")

    def test_environment_failure_does_not_blame_game_code(self):
        report = self.observed()
        report["checks"][0]["classification"] = "ENVIRONMENT_BLOCKER"
        result = create_plan(self.root, self.design, report)
        self.assertEqual(result["status"], "INCONCLUSIVE")
        self.assertEqual(result["repairPaths"], [])

    def test_unbound_and_stale_source_reports_are_rejected(self):
        report = self.observed()
        unbound = copy.deepcopy(report)
        del unbound["designMapEvidence"]
        with self.assertRaisesRegex(ValueError, "unbound or stale"):
            create_plan(self.root, self.design, unbound)
        (self.root / "README.md").write_text("changed\n")
        with self.assertRaisesRegex(ValueError, "unbound or stale"):
            create_plan(self.root, self.design, report)

    def test_changed_or_missing_full_log_is_rejected(self):
        report = self.observed()
        log = Path(report["checks"][0]["logPath"])
        log.write_text("invented diagnostic")
        with self.assertRaisesRegex(ValueError, "missing or changed"):
            create_plan(self.root, self.design, report)

    def test_log_path_cannot_escape_evidence_directory(self):
        report = self.observed()
        report["checks"][0]["logPath"] = str(self.root / "README.md")
        with self.assertRaisesRegex(ValueError, "log must be inside"):
            create_plan(self.root, self.design, report)

    def test_map_rejects_duplicate_ids_and_dangling_references(self):
        design = copy.deepcopy(self.design)
        design["elements"][1]["id"] = "player"
        with self.assertRaisesRegex(ValueError, "duplicate stable id"):
            validate_map(self.root, design)
        design = copy.deepcopy(self.design)
        design["interactions"][0]["participants"] = ["absent"]
        with self.assertRaisesRegex(ValueError, "known elements"):
            validate_map(self.root, design)

    def test_map_rejects_missing_and_ambiguous_anchors(self):
        for anchor in ("missing anchor", "var "):
            with self.subTest(anchor=anchor):
                design = copy.deepcopy(self.design)
                design["elements"][0]["bindings"][0]["anchor"] = anchor
                with self.assertRaisesRegex(ValueError, "exactly once"):
                    validate_map(self.root, design)

    def test_map_rejects_path_escape_absolute_and_state_bindings(self):
        for path in ("../escape.gd", "/tmp/escape.gd", "C:/escape.gd", "scripts\\game_model.gd", ".prototype/map.json"):
            with self.subTest(path=path):
                design = copy.deepcopy(self.design)
                design["elements"][0]["bindings"][0]["path"] = path
                with self.assertRaises(ValueError):
                    validate_map(self.root, design)

    def test_scenario_file_outside_tests_directory_is_still_not_a_repair_target(self):
        old = self.root / "tests/test_runner.gd"
        new = self.root / "scripts/oracle.gd"
        old.rename(new)
        for row in self.design["scenarios"]:
            row["bindings"][0]["path"] = "scripts/oracle.gd"
        self.design["elements"][0]["bindings"].append({"path": "scripts/oracle.gd", "anchor": "var _failures:"})
        result = create_plan(self.root, self.design, self.observed())
        self.assertEqual(result["repairPaths"], ["scripts/game_model.gd"])

    def test_renamed_binding_can_keep_stable_design_ids_on_a_new_baseline(self):
        before_ids = [row["id"] for row in self.design["elements"]]
        (self.root / "scripts/game_model.gd").rename(self.root / "scripts/renamed_model.gd")
        for kind in ("elements", "interactions"):
            for row in self.design[kind]:
                for binding in row["bindings"]:
                    binding["path"] = "scripts/renamed_model.gd"
        validate_map(self.root, self.design)
        self.assertEqual(before_ids, [row["id"] for row in self.design["elements"]])

    def test_verify_binds_the_new_report_and_checks_changed_scope(self):
        plan, report = self.repaired()
        result = verify_repair(self.root, self.design, plan, report)
        self.assertEqual(result["status"], "LOCAL_REPAIR_VERIFIED")
        self.assertEqual(result["changedPaths"], ["scripts/game_model.gd"])

    def test_unrelated_edits_or_modified_test_oracle_cannot_verify(self):
        for path in ("README.md", "tests/test_runner.gd"):
            with self.subTest(path=path):
                plan, _ = self.repaired()
                with (self.root / path).open("a") as handle:
                    handle.write("\n# unrelated edit\n")
                report = self.observed("TESTS PASS", 0)
                report["checks"][0]["command"] = plan["checkCommands"]["test"]
                result = verify_repair(self.root, self.design, plan, report)
                self.assertEqual(result["status"], "INCONCLUSIVE")
                self.assertIn(path, result["outsidePlan"])

    def test_skipped_or_unexecuted_retest_cannot_verify(self):
        plan, report = self.repaired()
        for status, executed in (("SKIPPED", True), ("PASS", False)):
            report["checks"][0].update(status=status, executed=executed)
            self.assertEqual(verify_repair(self.root, self.design, plan, report)["status"], "INCONCLUSIVE")

    def test_smoke_pass_cannot_replace_the_failed_gameplay_test(self):
        plan, report = self.repaired()
        report["checks"][0]["name"] = "smoke"
        result = verify_repair(self.root, self.design, plan, report)
        self.assertEqual(result["missingOrFailedChecks"], ["test"])
        self.assertEqual(result["status"], "INCONCLUSIVE")

    def test_different_test_script_cannot_replace_original_reproduction(self):
        plan, report = self.repaired()
        report["checks"][0]["command"] = ["godot", "--script", "res://tests/always_pass.gd"]
        result = verify_repair(self.root, self.design, plan, report)
        self.assertEqual(result["status"], "INCONCLUSIVE")
        self.assertEqual(result["changedCheckCommands"], ["test"])

    def test_map_semantics_or_identity_cannot_change_during_repair(self):
        plan, _ = self.repaired()
        self.design["objective"]["success"] = "Always succeed."
        report = self.observed("TESTS PASS", 0)
        with self.assertRaisesRegex(ValueError, "design map changed"):
            verify_repair(self.root, self.design, plan, report)

    def test_no_source_change_is_not_a_verified_repair(self):
        plan = create_plan(self.root, self.design, self.observed())
        report = self.observed("TESTS PASS", 0)
        self.assertEqual(verify_repair(self.root, self.design, plan, report)["status"], "INCONCLUSIVE")


@unittest.skipUnless(os.environ.get("GPS_TEST_GODOT"), "set GPS_TEST_GODOT for live engine integration")
class LiveGodotRepairTests(DesignRepairFixture, unittest.TestCase):
    # Use an isolated starter; never introduce a mutant into a consumer project.
    def test_live_broken_movement_local_repair_and_same_engine_retest(self):
        binary = os.environ["GPS_TEST_GODOT"]
        model = self.root / "scripts/game_model.gd"
        original = model.read_text()
        mutant = original.replace('if action == &"move":', 'if action == &"move":\n        return')
        model.write_text(mutant)
        map_path = self.root / ".prototype/spec/design_map.json"
        map_path.parent.mkdir(parents=True)
        map_path.write_text(json.dumps(self.design))
        # First import may create .gd.uid files. Establish identity after import.
        subprocess.run([binary, "--headless", "--path", str(self.root), "--import", "--quit"],
                       capture_output=True, timeout=30, check=True)

        def run_checks(expected):
            proc = subprocess.run([sys.executable, str(ROOT / "scripts/run_godot_checks.py"), str(self.root),
                                   "--godot", binary, "--mode", "all", "--design-map", str(map_path)],
                                  capture_output=True, text=True, encoding="utf-8", timeout=45)
            self.assertEqual(proc.returncode, expected, proc.stderr)
            return json.loads(proc.stdout)

        before = run_checks(1)
        plan = before["localRepair"]
        self.assertEqual(plan["status"], "REPAIRABLE", plan)
        self.assertEqual(plan["repairPaths"], ["scripts/game_model.gd"])
        self.assertEqual(plan["failures"][0]["interactions"], ["move-player"])
        model.write_text(original)
        after = run_checks(0)
        verification = verify_repair(self.root, self.design, plan, after)
        self.assertEqual(verification["status"], "LOCAL_REPAIR_VERIFIED", verification)
        self.assertEqual(verification["changedPaths"], ["scripts/game_model.gd"])


if __name__ == "__main__":
    unittest.main()
