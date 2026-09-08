#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from _common import utc_now, write_json


def find_godot(explicit: str | None) -> str | None:
    candidates = [explicit, os.environ.get("GODOT_BIN"), "godot4", "godot", "godot4.7", "godot4.6", "godot4.5", "godot4.4"]
    for candidate in candidates:
        if not candidate:
            continue
        expanded = str(Path(candidate).expanduser()) if any(ch in candidate for ch in ("/", "\\", "~")) else candidate
        path = shutil.which(expanded) or (expanded if Path(expanded).is_file() else None)
        if path:
            return str(Path(path).resolve())
    return None


def command_version(binary: str | None) -> tuple[str | None, bool, str | None]:
    if not binary:
        return None, False, None
    try:
        proc = subprocess.run([binary, "--version"], capture_output=True, text=True, timeout=10)
    except Exception as exc:
        return None, False, str(exc)
    combined = (proc.stdout + "\n" + proc.stderr).strip()
    first = combined.splitlines()[0].strip() if combined else None
    return first, proc.returncode == 0, None if proc.returncode == 0 else combined[:500]


def parse_project(project_file: Path, root: Path) -> dict[str, Any]:
    data: dict[str, Any] = {
        "projectFile": str(project_file) if project_file.exists() else None,
        "configVersion": None,
        "features": [],
        "mainScene": None,
        "language": "unknown",
        "autoloads": [],
        "addons": [],
        "testSignals": [],
        "exportPresets": (root / "export_presets.cfg").exists(),
    }
    if project_file.exists():
        text = project_file.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"^config_version\s*=\s*(\d+)", text, re.MULTILINE)
        if match:
            data["configVersion"] = int(match.group(1))
        match = re.search(r'^run/main_scene\s*=\s*"([^"]+)"', text, re.MULTILINE)
        if match:
            data["mainScene"] = match.group(1)
        match = re.search(r"^config/features\s*=\s*PackedStringArray\((.*?)\)", text, re.MULTILINE)
        if match:
            data["features"] = re.findall(r'"([^"]+)"', match.group(1))
        autoload_match = re.search(r"^\[autoload\]\s*$([\s\S]*?)(?=^\[|\Z)", text, re.MULTILINE)
        if autoload_match:
            data["autoloads"] = re.findall(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=", autoload_match.group(1), re.MULTILINE)

    gd_files = list(root.rglob("*.gd")) if root.exists() else []
    cs_files = list(root.rglob("*.cs")) if root.exists() else []
    has_csproj = any(root.glob("*.csproj")) if root.exists() else False
    if gd_files and (cs_files or has_csproj):
        data["language"] = "MIXED"
    elif cs_files or has_csproj:
        data["language"] = "CSHARP"
    elif gd_files:
        data["language"] = "GDScript"

    addons = root / "addons"
    if addons.is_dir():
        data["addons"] = sorted(p.name for p in addons.iterdir() if p.is_dir())

    signals: list[str] = []
    if (root / "tests").is_dir():
        signals.append("tests-directory")
    lowered_addons = {name.lower() for name in data["addons"]}
    for name, marker in (("gdunit4", "GdUnit4"), ("gut", "GUT"), ("machine_qa", "MachineQA")):
        if name in lowered_addons:
            signals.append(marker)
    if any(path.name in {"test_runner.gd", "run_tests.gd"} for path in gd_files):
        signals.append("GDScript test runner")
    data["testSignals"] = sorted(set(signals))
    return data


def codex_config_mentions_godot(root: Path) -> bool:
    candidates = [
        Path.home() / ".codex/config.toml",
        Path.home() / ".config/codex/config.toml",
        root / ".codex/config.toml",
    ]
    needles = ("godot-mcp", "godot_mcp", "@satelliteoflove/godot-mcp", "gda-mcp")
    for path in candidates:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace").lower()
        if any(needle in text for needle in needles):
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect Godot and prototype verification capabilities.")
    parser.add_argument("project_root")
    parser.add_argument("--godot", help="Explicit Godot binary path.")
    parser.add_argument("--write", action="store_true", help="Write .prototype/spec/capability_profile.json")
    args = parser.parse_args()

    root = Path(args.project_root).expanduser().resolve()
    binary = find_godot(args.godot)
    version, version_ok, version_error = command_version(binary)
    project = parse_project(root / "project.godot", root)
    display = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    gda = shutil.which("gda")
    mcp_mentioned = codex_config_mentions_godot(root)
    qa_bridge = any(
        path.exists()
        for path in (
            root / "qa/qa_bridge.gd",
            root / "scripts/qa_bridge.gd",
            root / "addons/machine_qa",
        )
    )

    if not binary:
        tier = "E1_EDIT_AND_STATIC"
    elif display or gda or mcp_mentioned:
        tier = "E3_RUNTIME_OBSERVE_CANDIDATE"
    else:
        tier = "E2_HEADLESS_VERIFY_CANDIDATE"
    if binary and qa_bridge and project["testSignals"] and (display or gda or mcp_mentioned):
        tier = "E4_BOUNDED_EXPERIMENT_CANDIDATE"

    limitations: list[str] = []
    if not binary:
        limitations.append("Godot CLI not detected; import, test, and runtime claims cannot be verified here.")
    elif not version_ok:
        limitations.append("Godot binary was found but --version failed; exercise it before assigning E2.")
    else:
        limitations.append("Godot version detection alone does not prove project import or runtime success; run Godot checks.")
    if mcp_mentioned:
        limitations.append("Godot MCP is mentioned in Codex config but connectivity has not been proven.")
    if gda:
        limitations.append("GDA is installed but live/project connectivity has not been proven.")
    if not display and not gda and not mcp_mentioned:
        limitations.append("No display or runtime bridge detected; presentation and real-input claims need another path.")

    report = {
        "schemaVersion": 1,
        "generatedAt": utc_now(),
        "projectRoot": str(root),
        "godot": {
            "detected": bool(binary),
            "path": binary,
            "version": version,
            "versionCommandSucceeded": version_ok,
            "versionError": version_error,
        },
        "project": project,
        "runtimeObservation": {
            "displayEnvironment": display,
            "gdaDetected": bool(gda),
            "gdaPath": gda,
            "godotMcpMentionedInCodexConfig": mcp_mentioned,
            "qaBridgeDetected": qa_bridge,
        },
        "recommendedExecutionTier": tier,
        "provenExecutionTier": "E1_EDIT_AND_STATIC",
        "limitations": limitations,
    }

    if args.write:
        destination = root / ".prototype/spec/capability_profile.json"
        write_json(destination, report)
        report["writtenTo"] = str(destination)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
