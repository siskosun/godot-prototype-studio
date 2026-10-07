#!/usr/bin/env python3
"""Validate a design/source map and localize observed failures. Never edit source or Review."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

from _common import load_json, sha256_file, write_json
from _identities import classify_changes, project_files

CHECKS = {"import", "test", "smoke"}
ENVIRONMENT = {"TOOL_MISSING", "EXECUTION_UNAVAILABLE", "ENVIRONMENT_BLOCKER", "TIMEOUT"}
RESOURCE_PATH = re.compile(r"res://([^\s\)\],\"']+?)(?=:\d|[\s\)\],\"']|$)")
SCOPE = "Local diagnostic evidence only; not runtime object identity, a playtest, or game-exp Review."


def require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty string")
    return value


def source_path(root: Path, value: Any) -> Path:
    text = require_text(value, "binding.path")
    relative = PurePosixPath(text)
    if (relative.is_absolute() or ".." in relative.parts or "\\" in text or ":" in text
            or relative.as_posix() != text or text.startswith("./")):
        raise ValueError(f"binding path must be a normalized project-relative path: {text}")
    if any(part in {".git", ".godot", ".prototype", "__pycache__"} for part in relative.parts):
        raise ValueError(f"binding must target source, not state/generated files: {text}")
    if text == "export/web" or text.startswith("export/web/"):
        raise ValueError(f"binding must target editable source: {text}")
    path = root / text
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"binding escapes project: {text}")
    if any(part.is_symlink() for part in [path, *path.parents] if part != root.parent):
        raise ValueError(f"symlink binding is unsupported: {text}")
    if not path.is_file():
        raise ValueError(f"binding file is missing: {text}")
    return path


def validate_map(root: Path, design: Any) -> dict[str, dict[str, dict[str, Any]]]:
    if not isinstance(design, dict) or type(design.get("schemaVersion")) is not int or design["schemaVersion"] != 1:
        raise ValueError("design map schemaVersion must be 1")
    objective = design.get("objective")
    if not isinstance(objective, dict):
        raise ValueError("objective must be an object")
    for key in ("success", "failure"):
        require_text(objective.get(key), f"objective.{key}")
    tables: dict[str, dict[str, dict[str, Any]]] = {}
    all_ids: set[str] = set()
    for kind in ("elements", "interactions", "scenarios"):
        rows = design.get(kind)
        if not isinstance(rows, list) or not rows:
            raise ValueError(f"{kind} must be a nonempty list")
        tables[kind] = {}
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError(f"{kind} entry must be an object")
            identity = require_text(row.get("id"), f"{kind}.id")
            if identity in all_ids:
                raise ValueError(f"duplicate stable id: {identity}")
            all_ids.add(identity)
            tables[kind][identity] = row
            fields = {"elements": ("role",), "interactions": ("trigger", "preconditions", "stateChange"),
                      "scenarios": ("failureMarker",)}[kind]
            for field in fields:
                require_text(row.get(field), f"{identity}.{field}")
            bindings = row.get("bindings")
            if not isinstance(bindings, list) or not bindings:
                raise ValueError(f"{identity}.bindings must be nonempty")
            for binding in bindings:
                if not isinstance(binding, dict):
                    raise ValueError(f"{identity}.binding must be an object")
                path = source_path(root, binding.get("path"))
                anchor = require_text(binding.get("anchor"), f"{identity}.anchor")
                if path.read_text(encoding="utf-8").count(anchor) != 1:
                    raise ValueError(f"{identity}: source anchor must occur exactly once in {binding['path']}")
    for identity, row in tables["interactions"].items():
        refs = row.get("participants")
        if not isinstance(refs, list) or not refs or any(not isinstance(ref, str) or ref not in tables["elements"] for ref in refs):
            raise ValueError(f"{identity}.participants must reference known elements")
    markers: set[tuple[str, str]] = set()
    for identity, row in tables["scenarios"].items():
        refs = row.get("interactions")
        if not isinstance(refs, list) or not refs or any(not isinstance(ref, str) or ref not in tables["interactions"] for ref in refs):
            raise ValueError(f"{identity}.interactions must reference known interactions")
        if row.get("check") not in CHECKS:
            raise ValueError(f"{identity}.check must be import, test, or smoke")
        marker = (row["check"], row["failureMarker"])
        if marker in markers:
            raise ValueError(f"duplicate failure marker: {marker}")
        markers.add(marker)
    return tables


def capture_context(root: Path, design: dict[str, Any]) -> dict[str, Any]:
    validate_map(root, design)
    encoded = json.dumps(design, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return {"projectRoot": str(root.resolve()), "mapSha256": hashlib.sha256(encoded).hexdigest(),
            "files": {row["path"]: row["sha256"] for row in project_files(root)}}


def require_current_report(root: Path, design: dict[str, Any], report: Any) -> dict[str, Any]:
    current = capture_context(root, design)
    if not isinstance(report, dict) or report.get("designMapEvidence") != current:
        raise ValueError("unbound or stale report: rerun run_godot_checks.py with --design-map on this source")
    if report.get("projectRoot") != current["projectRoot"]:
        raise ValueError("report belongs to a different project")
    if not isinstance(report.get("checks"), list):
        raise ValueError("report.checks must be a list")
    names = [row.get("name") for row in report["checks"] if isinstance(row, dict)]
    if len(names) != len(report["checks"]) or any(not isinstance(name, str) for name in names) or len(set(names)) != len(names):
        raise ValueError("report checks require unique names")
    return current


def execution_time(value: Any) -> datetime:
    parsed = datetime.fromisoformat(require_text(value, "execution time"))
    if parsed.tzinfo is None:
        raise ValueError("execution time must include a timezone")
    return parsed


def diagnostic_text(root: Path, check: dict[str, Any]) -> str:
    # Use the retained full log, not a possibly truncated tail. Never read an arbitrary path.
    if check.get("logPath"):
        raw_path = Path(check["logPath"])
        path = raw_path.resolve()
        if not path.is_relative_to((root / ".prototype/evidence/godot-checks").resolve()):
            raise ValueError("check log must be inside .prototype/evidence/godot-checks")
        if any(part.is_symlink() for part in [raw_path, *raw_path.parents]) or not path.is_file() or check.get("logSha256") != sha256_file(path):
            raise ValueError("check log is missing or changed")
        text = path.read_text(encoding="utf-8")
        if "\n\n--- stdout ---\n" not in text:
            raise ValueError("unsupported check log format")
        header = text.splitlines()[0]
        if not header.startswith("# execution: "):
            raise ValueError("unbound check log: rerun checks with execution metadata")
        metadata = json.loads(header[len("# execution: "):])
        for key in ("name", "command", "executionId", "startedAt", "completedAt", "executable",
                    "executed", "exitCode", "status", "classification"):
            if key not in metadata or metadata[key] != check.get(key):
                raise ValueError(f"check log metadata differs from report: {key}")
        require_text(check.get("executionId"), "executionId")
        if execution_time(check.get("completedAt")) < execution_time(check.get("startedAt")):
            raise ValueError("check completion precedes execution")
        executable = check.get("executable")
        if not isinstance(executable, dict) or executable.get("sha256") != sha256_file(Path(executable["path"])):
            raise ValueError("check executable is missing or changed")
        prefix = header + "\n$ " + " ".join(check["command"]) + "\n\n--- stdout ---\n"
        if not text.startswith(prefix):
            raise ValueError("check command header differs from exact argv")
        output = text[len(prefix):]
        from run_godot_checks import ACTIONABLE_ERROR
        observed_errors = [line for line in output.splitlines() if ACTIONABLE_ERROR.search(line)]
        if check.get("actionableErrorLines") != observed_errors:
            raise ValueError("check diagnostics differ from full log")
        if check.get("status") == "PASS" and (check.get("executed") is not True or check.get("exitCode") != 0 or observed_errors):
            raise ValueError("check PASS contradicts execution evidence")
        return output
    raise ValueError("check full log is required")


def command_oracles(root: Path, check: dict[str, Any]) -> set[str]:
    command = check.get("command")
    if not isinstance(command, list) or not command or any(not isinstance(arg, str) for arg in command):
        raise ValueError("executed check requires exact command argv")
    paths: set[str] = set()
    if "--script" in command:
        index = command.index("--script") + 1
        if index >= len(command) or not command[index].startswith("res://"):
            raise ValueError("repair checks require a project-source res:// test script")
        relative = command[index][len("res://"):]
        source_path(root, relative)
        paths.add(relative)
    return paths


def binding_paths(rows: list[dict[str, Any]]) -> set[str]:
    return {binding["path"] for row in rows for binding in row["bindings"]}


def error_blocks(text: str) -> list[str]:
    from run_godot_checks import ACTIONABLE_ERROR
    blocks: list[list[str]] = []
    in_stack = False
    for line in text.splitlines():
        if ACTIONABLE_ERROR.search(line):
            blocks.append([line])
            in_stack = True
        elif in_stack and re.match(r"\s*(?:at:|GDScript backtrace|\[\d+\])", line):
            blocks[-1].append(line)
        elif line.strip():
            in_stack = False
    return ["\n".join(block) for block in blocks]


def create_plan(root: Path, design: dict[str, Any], report: dict[str, Any]) -> dict[str, Any]:
    context = require_current_report(root, design, report)
    tables = validate_map(root, design)
    failures = [row for row in report["checks"] if row.get("status") == "FAIL"]
    result: dict[str, Any] = {"schemaVersion": 1, "status": "INCONCLUSIVE", "before": context,
                             "evidenceClass": "PARTICIPANT_REPORTED", "validationScope": SCOPE,
                             "failures": [], "repairPaths": [], "retestChecks": [],
                             "checkCommands": {row["name"]: row.get("command") for row in report["checks"]
                                               if row.get("name") in CHECKS}}
    if not failures:
        result["status"] = "NO_FAILURES" if report.get("overall") == "PASS" else "INCONCLUSIVE"
        return result
    repair_paths: set[str] = set()
    command_paths: set[str] = set()
    result["checkExecutions"] = {}
    for check in report["checks"]:
        if check.get("executed") is True and check.get("name") in CHECKS and check.get("classification") not in ENVIRONMENT:
            diagnostic_text(root, check)
            command_paths.update(command_oracles(root, check))
            result["checkExecutions"][check["name"]] = {key: check[key] for key in
                                                        ("executionId", "completedAt", "executable")}
    retest = {row["name"] for row in report["checks"] if row.get("name") in CHECKS}
    unresolved = False
    for check in failures:
        item: dict[str, Any] = {"check": check.get("name"), "classification": check.get("classification"),
                               "localization": "UNRESOLVED", "elements": [], "interactions": [], "scenarios": []}
        result["failures"].append(item)
        if check.get("classification") in ENVIRONMENT or check.get("executed") is not True:
            item["localization"] = "ENVIRONMENT_OR_UNEXECUTED"
            unresolved = True
            continue
        text = diagnostic_text(root, check)
        error_lines = check.get("actionableErrorLines", [])
        scenarios = [row for row in tables["scenarios"].values()
                     if row["check"] == check["name"]
                     and any(row["failureMarker"] in line for line in error_lines)]
        interactions = {ref for row in scenarios for ref in row["interactions"]}
        elements = {ref for ref in interactions for ref in tables["interactions"][ref]["participants"]}
        if scenarios:
            item["localization"] = "SCENARIO_MARKER"
            unknown = [line for line in error_lines
                       if not any(row["failureMarker"] in line for row in scenarios)
                       and not re.search(r"(?:ERROR:\s*)?TESTS? FAILED:\s*\d+\s*$", line, re.I)]
            if unknown:
                item["unmappedErrorLines"] = unknown
                unresolved = True
        else:
            # A resource mentioned in normal output is not a failure location.
            # Every observed error needs a mapped candidate, not just one of them.
            blocks = error_blocks(text)
            mapped_paths = binding_paths(list(tables["elements"].values()) + list(tables["interactions"].values()))
            paths: set[str] = set()
            for block in blocks:
                candidates = set(RESOURCE_PATH.findall(block)) & mapped_paths
                paths.update(candidates)
                if not candidates:
                    unresolved = True
            elements = {key for key, row in tables["elements"].items() if binding_paths([row]) & paths}
            interactions = {key for key, row in tables["interactions"].items() if binding_paths([row]) & paths}
            interactions.update(key for key, row in tables["interactions"].items() if set(row["participants"]) & elements)
            elements.update(ref for key in interactions for ref in tables["interactions"][key]["participants"])
            if elements or interactions:
                item["localization"] = "RESOURCE_PATH_CANDIDATES"
        related = [row for row in tables["scenarios"].values() if set(row["interactions"]) & interactions]
        retest.update(row["check"] for row in related)
        paths = binding_paths([tables["elements"][key] for key in elements] +
                              [tables["interactions"][key] for key in interactions])
        # Test-oracle files are observations, not default repair targets.
        oracle_paths = {os.path.normcase(path) for path in binding_paths(list(tables["scenarios"].values())) | command_paths}
        paths = {path for path in paths if os.path.normcase(path) not in oracle_paths
                 and not path.lower().startswith(("tests/", "test/", "qa/"))}
        item.update(elements=sorted(elements), interactions=sorted(interactions),
                    scenarios=sorted(row["id"] for row in related), suspectPaths=sorted(paths),
                    checkPaths=sorted(binding_paths(related)))
        repair_paths.update(paths)
        if not paths:
            unresolved = True
    unresolved = unresolved or not retest.issubset(result["checkExecutions"])
    result.update(status="INCONCLUSIVE" if unresolved else "REPAIRABLE", repairPaths=sorted(repair_paths),
                  retestChecks=sorted(retest), changedClasses=classify_changes(repair_paths)["changedClasses"])
    return result


def verify_repair(root: Path, design: dict[str, Any], plan: dict[str, Any], report: dict[str, Any]) -> dict[str, Any]:
    current = require_current_report(root, design, report)
    if plan.get("status") != "REPAIRABLE" or plan.get("schemaVersion") != 1:
        raise ValueError("verify requires a REPAIRABLE plan")
    before = plan["before"]
    if before["projectRoot"] != current["projectRoot"] or before["mapSha256"] != current["mapSha256"]:
        raise ValueError("project or design map changed: establish a new baseline instead of relabeling this repair")
    old, new = before["files"], current["files"]
    changed = sorted(path for path in set(old) | set(new) if old.get(path) != new.get(path))
    outside = sorted(set(changed) - set(plan["repairPaths"]))
    checks = {row["name"]: row for row in report["checks"]}
    missing = [name for name in plan["retestChecks"] if checks.get(name, {}).get("status") != "PASS"
               or checks.get(name, {}).get("executed") is not True]
    changed_commands = [name for name, command in plan["checkCommands"].items()
                        if command != checks.get(name, {}).get("command")]
    invalid_evidence: dict[str, str] = {}
    executions = plan.get("checkExecutions", {})
    baseline_end = max((execution_time(row["completedAt"]) for row in executions.values()), default=None)
    for name in plan["retestChecks"]:
        if name in missing or name in changed_commands:
            continue
        try:
            check = checks[name]
            diagnostic_text(root, check)
            command_oracles(root, check)
            baseline = executions.get(name)
            if not baseline or baseline_end is None or check["executionId"] == baseline["executionId"] or execution_time(check["startedAt"]) <= baseline_end:
                raise ValueError("retest must be a new execution after the failing baseline")
            if check["executable"] != baseline["executable"]:
                raise ValueError("original check executable changed")
        except (OSError, ValueError, TypeError, KeyError) as exc:
            invalid_evidence[name] = str(exc)
    passed = bool(changed) and not outside and not missing and not changed_commands and not invalid_evidence and report.get("overall") == "PASS"
    return {"schemaVersion": 1, "status": "LOCAL_REPAIR_VERIFIED" if passed else "INCONCLUSIVE",
            "changedPaths": changed, "outsidePlan": outside, "missingOrFailedChecks": missing,
            "changedCheckCommands": changed_commands,
            "invalidCheckEvidence": invalid_evidence,
            "sourceChanged": bool(changed), "before": before, "after": current,
            "evidenceClass": "PARTICIPANT_REPORTED", "validationScope": SCOPE}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("validate", "plan", "verify"))
    parser.add_argument("project_root")
    parser.add_argument("--map", required=True, dest="map_path")
    parser.add_argument("--report")
    parser.add_argument("--plan")
    parser.add_argument("--write")
    args = parser.parse_args()
    try:
        root = Path(args.project_root).expanduser().resolve()
        design = load_json(Path(args.map_path))
        if args.action == "validate":
            capture_context(root, design)
            result = {"status": "MAP_VALID", "validationScope": "Source anchors and cross-references only; " + SCOPE}
        else:
            if not args.report or (args.action == "verify" and not args.plan):
                raise ValueError("--report is required; verify also requires --plan")
            report = load_json(Path(args.report))
            result = (create_plan(root, design, report) if args.action == "plan" else
                      verify_repair(root, design, load_json(Path(args.plan)), report))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        result = {"status": "INCONCLUSIVE", "errors": [str(exc)], "validationScope": SCOPE}
    if args.write:
        write_json(Path(args.write), result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"MAP_VALID", "REPAIRABLE", "NO_FAILURES", "LOCAL_REPAIR_VERIFIED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
