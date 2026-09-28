"""Utility/negative tests, not live agent, Godot, visual or player evaluation."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import _review_state as records
import check_project_memory as memory
import verification_checkpoint as checkpoint


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write("project.godot", '[application]\nconfig/name="fixture"\n')
        self.write("scripts/rule.gd", "extends Node\n")
        self.brief = ".prototype/spec/mission_brief.md"
        self.plan = ".prototype/spec/mechanic_lab.md"
        self.output = ".prototype/evidence/review-01.json"
        self.write(self.brief, "# Brief\nUser requires a local kernel.\n")
        self.write(self.plan, "# Plan\nCompare action consequences from a clean start.\n")
        self.write(".prototype/evidence/run.txt", "Fixture evidence, not an actual game run.\n")

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def entry(self):
        return {"id": "hypothesis-1", "kind": "hypothesis", "status": "ACTIVE",
                "claim": "Changing the rule may alter the next action.",
                "scope": "This fixture only", "revisitWhen": "Rule or scenario changes",
                "sources": [records.fingerprint(self.root, ".prototype/evidence/run.txt")],
                "dependsOn": [records.fingerprint(self.root, "scripts/rule.gd")]}

    def data(self, entry=None):
        return {"schemaVersion": 1, "entries": [entry or self.entry()]}

    def run_cli(self, script, *args):
        return subprocess.run([sys.executable, str(ROOT / "scripts" / script), *map(str, args)],
                              text=True, capture_output=True, timeout=15)

    def freeze(self):
        return checkpoint.freeze(self.root, self.brief, self.plan, self.output)


class MemoryTests(Fixture):
    def test_empty_memory_is_valid(self):
        self.assertEqual(memory.inspect_memory({"schemaVersion": 1, "entries": []}, self.root)["status"], "RECORDS_CURRENT")

    def test_current_hypothesis_stays_hypothesis(self):
        result = memory.inspect_memory(self.data(), self.root)
        self.assertEqual(result["entries"][0]["state"], "CURRENT_RECORD")
        self.assertEqual(result["entries"][0]["kind"], "hypothesis")
        self.assertIn("not truth", result["scope"])

    def test_dependency_change_is_stale(self):
        data = self.data()
        self.write("scripts/rule.gd", "extends RefCounted\n")
        result = memory.inspect_memory(data, self.root)
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertEqual(result["entries"][0]["state"], "STALE")

    def test_source_change_is_stale(self):
        data = self.data()
        self.write(".prototype/evidence/run.txt", "New evidence cannot replace the old record identity.\n")
        self.assertEqual(memory.inspect_memory(data, self.root)["entries"][0]["state"], "STALE")

    def test_missing_and_empty_source_are_stale(self):
        data = self.data()
        (self.root / ".prototype/evidence/run.txt").unlink()
        self.assertEqual(memory.inspect_memory(data, self.root)["entries"][0]["state"], "STALE")
        self.write(".prototype/evidence/run.txt", "")
        self.assertEqual(memory.inspect_memory(data, self.root)["entries"][0]["state"], "STALE")

    def test_missing_source_or_dependency_is_unverified(self):
        for field in ("sources", "dependsOn"):
            with self.subTest(field=field):
                data = self.data(); data["entries"][0][field] = []
                self.assertEqual(memory.inspect_memory(data, self.root)["entries"][0]["state"], "UNVERIFIED")

    def test_superseded_retains_changed_evidence(self):
        data = self.data(); entry = data["entries"][0]
        entry.update(status="SUPERSEDED", supersededReason="User changed the premise")
        self.write("scripts/rule.gd", "changed")
        result = memory.inspect_memory(data, self.root)
        self.assertEqual(result["entries"][0]["state"], "SUPERSEDED")
        self.assertTrue(result["entries"][0]["changes"])

    def test_supersession_needs_nonempty_reason(self):
        for reason in (None, "", "   "):
            with self.subTest(reason=reason):
                data = self.data(); data["entries"][0].update(status="SUPERSEDED", supersededReason=reason)
                with self.assertRaises(ValueError): memory.inspect_memory(data, self.root)

    def test_duplicate_ids_and_missing_conditions_rejected(self):
        data = self.data(); data["entries"].append(copy.deepcopy(data["entries"][0]))
        with self.assertRaises(ValueError): memory.inspect_memory(data, self.root)
        for field in ("scope", "claim", "id", "revisitWhen"):
            data = self.data(); data["entries"][0][field] = ""
            with self.assertRaises(ValueError): memory.inspect_memory(data, self.root)

    def test_unknown_kind_and_status_rejected(self):
        for key, value in (("kind", "proven_fact"), ("status", "AUTO_APPROVED")):
            data = self.data(); data["entries"][0][key] = value
            with self.assertRaises(ValueError): memory.inspect_memory(data, self.root)

    def test_file_reference_hash_and_path_are_checked(self):
        for value in ("x" * 64, True, "", "A" * 64):
            data = self.data(); data["entries"][0]["sources"][0]["sha256"] = value
            with self.assertRaises(ValueError): memory.inspect_memory(data, self.root)
        data = self.data(); data["entries"][0]["sources"][0]["path"] = "../outside"
        with self.assertRaises(ValueError): memory.inspect_memory(data, self.root)

    def test_inspection_is_read_only(self):
        data = self.data(); before = copy.deepcopy(data)
        files = {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        memory.inspect_memory(data, self.root)
        self.assertEqual(data, before)
        self.assertEqual(files, {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_cli_current_stale_and_invalid_exit_codes(self):
        self.write(".prototype/project_memory.json", json.dumps(self.data()))
        result = self.run_cli("check_project_memory.py", self.root)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.write("scripts/rule.gd", "changed")
        self.assertEqual(self.run_cli("check_project_memory.py", self.root).returncode, 1)
        self.write(".prototype/project_memory.json", "invalid")
        result = self.run_cli("check_project_memory.py", self.root)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "INVALID")


class RecordTests(Fixture):
    def test_unsafe_paths_are_rejected(self):
        for path in ("/tmp/x", "../x", "a/../x", "./x", "a//x", "a\\x", "C:/x", "x\n", " x", "https://example.test"):
            with self.subTest(path=path), self.assertRaises(ValueError): records.local_path(self.root, path)

    def test_symlink_file_directory_and_root_rejected(self):
        (self.root / "alias").symlink_to(self.root / "scripts", target_is_directory=True)
        with self.assertRaises(ValueError): records.local_path(self.root, "alias/rule.gd")
        with self.assertRaises(ValueError): records.project_root(self.root / "alias")
        (self.root / "link.gd").symlink_to(self.root / "scripts/rule.gd")
        with self.assertRaises(ValueError): records.fingerprint(self.root, "link.gd")

    def test_duplicate_keys_nonfinite_and_wrong_schema_rejected(self):
        for text in ('{"schemaVersion":1,"schemaVersion":1}', '{"schemaVersion":1,"x":NaN}',
                     '{"schemaVersion":1,"x":Infinity}', '{"schemaVersion":true}',
                     '{"schemaVersion":2}', '[]'):
            path = self.write("record.json", text)
            with self.subTest(text=text), self.assertRaises(ValueError): records.read_record(path)

    def test_oversize_record_rejected(self):
        path = self.write("large.json", " " * (records.MAX_RECORD_BYTES + 1))
        with self.assertRaises(ValueError): records.read_record(path)

    def test_empty_file_cannot_be_fingerprinted(self):
        self.write("empty.txt", "")
        with self.assertRaises(ValueError): records.fingerprint(self.root, "empty.txt")


class CheckpointTests(Fixture):
    def test_freeze_then_check_matches(self):
        data = self.freeze()
        self.assertEqual(checkpoint.check(self.root, data)["status"], "MATCH")
        self.assertNotIn("PASS", data)

    def test_artifact_change_detected(self):
        data = self.freeze(); self.write("scripts/rule.gd", "changed")
        self.assertEqual(checkpoint.check(self.root, data)["status"], "DRIFT")

    def test_brief_and_plan_edits_detected_outside_tree_hash(self):
        for path in (self.brief, self.plan):
            data = self.freeze() if not (self.root / self.output).exists() else records.read_record(self.root / self.output)
            old = (self.root / path).read_text(); self.write(path, old + "changed")
            self.assertEqual(checkpoint.check(self.root, data)["status"], "DRIFT")
            self.write(path, old)

    def test_append_observations_does_not_change_artifact(self):
        data = self.freeze(); self.write(".prototype/evidence/reviewer.txt", "observed")
        self.assertEqual(checkpoint.check(self.root, data)["status"], "MATCH")

    def test_exclusion_and_schema_tampering_rejected(self):
        original = self.freeze()
        for field, value in (("exclusions", {"parts": ["scripts"], "prefixes": []}),
                             ("schemaVersion", True), ("fileCount", True), ("artifactSha256", "x")):
            data = copy.deepcopy(original); data[field] = value
            with self.assertRaises(ValueError): checkpoint.check(self.root, data)

    def test_existing_checkpoint_cannot_be_overwritten(self):
        self.freeze(); before = (self.root / self.output).read_bytes()
        with self.assertRaises(ValueError): self.freeze()
        self.assertEqual((self.root / self.output).read_bytes(), before)

    def test_output_cannot_overwrite_source_brief_or_plan(self):
        for output in ("scripts/check.json", self.brief, self.plan):
            with self.subTest(output=output), self.assertRaises(ValueError):
                checkpoint.freeze(self.root, self.brief, self.plan, output)

    def test_missing_reference_detected_and_missing_plan_cannot_freeze(self):
        data = self.freeze(); (self.root / self.plan).unlink()
        self.assertEqual(checkpoint.check(self.root, data)["status"], "DRIFT")
        with self.assertRaises(ValueError):
            checkpoint.freeze(self.root, self.brief, self.plan, ".prototype/evidence/other.json")

    def test_empty_artifact_rejected(self):
        (self.root / "project.godot").unlink(); (self.root / "scripts/rule.gd").unlink()
        with self.assertRaises(ValueError): self.freeze()

    def test_cli_freeze_match_drift_and_invalid(self):
        result = self.run_cli("verification_checkpoint.py", "freeze", self.root, "--plan", self.plan, "--out", self.output)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        args = ("check", self.root, "--record", self.output)
        self.assertEqual(self.run_cli("verification_checkpoint.py", *args).returncode, 0)
        self.write("scripts/rule.gd", "changed")
        self.assertEqual(self.run_cli("verification_checkpoint.py", *args).returncode, 1)
        self.write(self.output, "invalid")
        self.assertEqual(self.run_cli("verification_checkpoint.py", *args).returncode, 2)


class WorkspaceTests(Fixture):
    def test_default_workspace_still_has_only_two_records(self):
        with tempfile.TemporaryDirectory() as path:
            result = self.run_cli("init_workspace.py", path)
            self.assertEqual(result.returncode, 0)
            paths = {p.relative_to(path).as_posix() for p in Path(path).rglob("*") if p.is_file()}
            self.assertEqual(paths, {".prototype/spec/mission_brief.md", ".prototype/progress.md"})

    def test_memory_is_empty_opt_in_and_preserved(self):
        result = self.run_cli("init_workspace.py", self.root, "--with-memory", "--novel-gameplay")
        self.assertEqual(result.returncode, 0)
        path = self.root / ".prototype/project_memory.json"
        self.assertEqual(json.loads(path.read_text())["entries"], [])
        path.write_text("user-owned")
        self.assertEqual(self.run_cli("init_workspace.py", self.root, "--with-memory").returncode, 0)
        self.assertEqual(path.read_text(), "user-owned")


if __name__ == "__main__":
    unittest.main()
