#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any

from _common import utc_now, write_json
from detect_capabilities import command_version, find_godot

# Godot can print script/runtime errors while a later normal quit returns zero.
ACTIONABLE_ERROR = re.compile(
    r"^\s*(?:(?:SCRIPT |SHADER |USER )?ERROR:|Parse Error:|TESTS?_FAILED\b|"
    r"Assertion failed\b|Tests? failed\b)", re.IGNORECASE | re.MULTILINE
)


def classify_failure(text: str, returncode: int | None, timed_out: bool) -> str:
    lowered = text.lower()
    if timed_out:
        return "TIMEOUT"
    if returncode is None:
        return "UNKNOWN"
    if any(token in lowered for token in ("parse error", "failed to load script", "could not parse", "error at (")):
        return "IMPORT_OR_PARSE"
    if any(token in lowered for token in ("assertion failed", "test failed", "tests failed", "failed test")):
        return "TEST_FAILURE"
    if any(token in lowered for token in ("cannot open display", "vulkan", "display server", "driver")):
        return "ENVIRONMENT_BLOCKER"
    if any(token in lowered for token in ("failed loading resource", "could not load", "nonexistent function", "invalid call")):
        return "RUNTIME_FAILURE"
    return "UNKNOWN"


def run_command(name: str, command: list[str], report_dir: Path, timeout: int) -> dict[str, Any]:
    report_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    timed_out = False
    launch_error = None
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        returncode: int | None = proc.returncode
        stdout = proc.stdout
        stderr = proc.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        returncode = None
        stdout = exc.stdout.decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
    except OSError as exc:
        launch_error = str(exc)
        returncode = None
        stdout, stderr = "", launch_error
    duration = round(time.monotonic() - started, 3)
    combined = (stdout + "\n" + stderr).strip()
    log_path = report_dir / f"{name}.log"
    log_path.write_text(
        "$ " + " ".join(command) + "\n\n--- stdout ---\n" + stdout + "\n--- stderr ---\n" + stderr,
        encoding="utf-8",
    )
    error_lines = [line for line in combined.splitlines() if ACTIONABLE_ERROR.search(line)]
    passed = returncode == 0 and not timed_out and not error_lines and not launch_error
    return {
        "name": name,
        "status": "PASS" if passed else "FAIL",
        "classification": None if passed else ("EXECUTION_UNAVAILABLE" if launch_error else classify_failure("\n".join(error_lines) or combined, returncode, timed_out)),
        "actionableErrorLines": error_lines,
        "executed": launch_error is None,
        "command": command,
        "exitCode": returncode,
        "durationSeconds": duration,
        "logPath": str(log_path),
        "outputTail": combined[-2000:],
    }


def resolve_res_path(root: Path, value: str) -> Path | None:
    if value.startswith("res://"):
        return root / value[len("res://"):]
    if value.startswith("uid://"):
        return None
    return root / value


def preflight(root: Path) -> tuple[dict[str, Any], list[str]]:
    project = root / "project.godot"
    errors: list[str] = []
    result: dict[str, Any] = {"projectFile": str(project), "mainScene": None, "mainSceneExists": None}
    if not project.exists():
        errors.append("project.godot is missing")
        return result, errors
    text = project.read_text(encoding="utf-8", errors="replace")
    match = re.search(r'^run/main_scene\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not match:
        errors.append("run/main_scene is not declared in project.godot")
    else:
        main_scene = match.group(1)
        result["mainScene"] = main_scene
        resolved = resolve_res_path(root, main_scene)
        if resolved is not None:
            result["mainSceneExists"] = resolved.exists()
            if not resolved.exists():
                errors.append(f"main scene does not exist: {resolved}")
    return result, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Run structured Godot import, test, and headless smoke checks.")
    parser.add_argument("project_root")
    parser.add_argument("--godot", help="Explicit Godot binary path.")
    parser.add_argument("--mode", choices=["import", "test", "smoke", "all"], default="all")
    parser.add_argument("--test-script", default="res://tests/test_runner.gd")
    parser.add_argument("--smoke-frames", type=int, default=120)
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--report", help="JSON report path.")
    args = parser.parse_args()

    if args.timeout <= 0 or args.smoke_frames <= 0:
        parser.error("timeout and smoke-frames must be positive")
    root = Path(args.project_root).expanduser().resolve()
    report_dir = root / ".prototype/evidence/godot-checks"
    report_path = Path(args.report).expanduser().resolve() if args.report else report_dir / "report.json"
    structure, preflight_errors = preflight(root)
    binary = find_godot(args.godot)
    version, version_ok, version_error = command_version(binary)

    report: dict[str, Any] = {
        "schemaVersion": 1,
        "generatedAt": utc_now(),
        "projectRoot": str(root),
        "godot": {"path": binary, "version": version, "versionCommandSucceeded": version_ok, "versionError": version_error},
        "preflight": {"status": "PASS" if not preflight_errors else "FAIL", "details": structure, "errors": preflight_errors},
        "checks": [],
        "overall": "FAIL",
    }

    if preflight_errors:
        write_json(report_path, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1
    if not binary:
        report["checks"].append({"name": "godot", "status": "FAIL", "classification": "TOOL_MISSING", "message": "Godot binary not detected"})
        write_json(report_path, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 2

    if not version_ok:
        report["checks"].append({"name": "godot-version", "status": "FAIL", "classification": "EXECUTION_UNAVAILABLE", "message": version_error or "--version failed"})
        write_json(report_path, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 2

    selected = [args.mode] if args.mode != "all" else ["import", "test", "smoke"]
    for mode in selected:
        engine_log = report_dir / f"{mode}-engine.log"
        common = [binary, "--headless", "--path", str(root), "--log-file", str(engine_log)]
        if mode == "import":
            command = common + ["--import", "--quit"]
        elif mode == "test":
            test_path = resolve_res_path(root, args.test_script)
            if test_path is not None and not test_path.exists():
                report["checks"].append({
                    "name": "test",
                    "status": "SKIPPED",
                    "classification": None,
                    "message": f"test script not found: {test_path}",
                })
                continue
            command = common + ["--script", args.test_script]
        else:
            command = common + ["--quit-after", str(args.smoke_frames)]
        report["checks"].append(run_command(mode, command, report_dir, args.timeout))

    failures = [check for check in report["checks"] if check.get("status") == "FAIL"]
    skipped = [check for check in report["checks"] if check.get("status") == "SKIPPED"]
    if failures:
        report["overall"] = "FAIL"
    elif skipped:
        report["overall"] = "PARTIAL"
    else:
        report["overall"] = "PASS"
    write_json(report_path, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if failures else (3 if skipped else 0)


if __name__ == "__main__":
    raise SystemExit(main())
