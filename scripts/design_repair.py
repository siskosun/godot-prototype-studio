#!/usr/bin/env python3
"""Validate a design/source map and localize observed failures. Never edit source or Review."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
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
    return current


def diagnostic_text(root: Path, check: dict[str, Any]) -> str:
    # Use the retained full log, not a possibly truncated tail. Never read an arbitrary path.
    if check.get("logPath"):
        path = Path(check["logPath"]).resolve()
        if not path.is_relative_to((root / ".prototype/evidence/godot-checks").resolve()):
            raise ValueError("check log must be inside .prototype/evidence/godot-checks")
        if path.is_symlink() or not path.is_file() or check.get("logSha256") != sha256_file(path):
            raise ValueError("check log is missing or changed")
        text = path.read_text(encoding="utf-8")
        if "\n\n--- stdout ---\n" not in text:
            raise ValueError("unsupported check log format")
        return text.split("\n\n--- stdout ---\n", 1)[1]
    return "\n".join(check.get("actionableErrorLines", [])) + "\n" + str(check.get("outputTail", ""))


def binding_paths(rows: list[dict[str, Any]]) -> set[str]:
    return {binding["path"] for row in rows for binding in row["bindings"]}


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
            paths = set(RESOURCE_PATH.findall(text))
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
        oracle_paths = binding_paths(list(tables["scenarios"].values()))
        paths = {path for path in paths if path not in oracle_paths
                 and not path.startswith(("tests/", "test/", "qa/"))}
        item.update(elements=sorted(elements), interactions=sorted(interactions),
                    scenarios=sorted(row["id"] for row in related), suspectPaths=sorted(paths),
                    checkPaths=sorted(binding_paths(related)))
        repair_paths.update(paths)
        if not paths:
            unresolved = True
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
    passed = bool(changed) and not outside and not missing and not changed_commands and report.get("overall") == "PASS"
    return {"schemaVersion": 1, "status": "LOCAL_REPAIR_VERIFIED" if passed else "INCONCLUSIVE",
            "changedPaths": changed, "outsidePlan": outside, "missingOrFailedChecks": missing,
            "changedCheckCommands": changed_commands,
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
