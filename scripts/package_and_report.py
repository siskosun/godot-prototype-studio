#!/usr/bin/env python3
"""Stage, hash, package, and summarize delivery identities by reusing existing validators.

Fills hashes and file links only. Visual/player judgments stay UNREVIEWED until actually inspected.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any

from _common import deterministic_tree_hash, sha256_file, should_exclude, utc_now, write_json
from _identities import artifact_identities, is_generated_web, package_identity
from stamp_web_build import stamp as stamp_web

SKILL_SCRIPTS = Path(__file__).resolve().parent


def stage_source(project: Path, dest: Path) -> list[str]:
    if dest.exists():
        raise ValueError(f"staging directory already exists: {dest}")
    dest.mkdir(parents=True)
    copied: list[str] = []
    for path in sorted(p for p in project.rglob("*") if p.is_file()):
        if path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
            raise ValueError(f"symlink unsupported: {path}")
        relative = path.relative_to(project)
        if should_exclude(relative) or is_generated_web(relative.as_posix()):
            continue
        target = dest / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        copied.append(relative.as_posix())
    if not (dest / "project.godot").is_file():
        raise ValueError("staged source is missing project.godot")
    return copied


def write_zip(tree: Path, archive: Path) -> None:
    if archive.exists():
        raise ValueError(f"archive already exists: {archive}")
    archive.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(p for p in tree.rglob("*") if p.is_file()):
            bundle.write(path, path.relative_to(tree).as_posix())


def _run_validator(script: str, args: list[str]) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, str(SKILL_SCRIPTS / script), *args],
        text=True, capture_output=True, timeout=60)
    payload: Any
    try:
        payload = json.loads(result.stdout) if result.stdout.strip().startswith("{") else {
            "status": "FAIL" if result.returncode else "PASS", "output": result.stdout.strip()}
    except json.JSONDecodeError:
        payload = {"status": "FAIL" if result.returncode else "PASS", "output": result.stdout.strip()}
    if not isinstance(payload, dict):
        payload = {"status": "FAIL", "output": result.stdout.strip()}
    payload.setdefault("status", "FAIL" if result.returncode else "PASS")
    payload["returncode"] = result.returncode
    if result.stderr.strip():
        payload["stderr"] = result.stderr.strip()
    return payload


def write_session_status(path: Path, report: dict[str, Any]) -> None:
    identities = report.get("identities", {})
    game = identities.get("gameContent", {})
    commands = report.get("commands", [])
    validators = report.get("validators", [])
    passed = [row["name"] for row in validators if row.get("status") == "PASS"]
    open_issues = [row["name"] for row in validators if row.get("status") != "PASS"]
    if report.get("visualJudgmentRequired"):
        open_issues.append("visual/player review still required")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Session Status\n\n"
        f"- Skill / project version: {report.get('skillVersion', 'unknown')}\n"
        f"- Current artifact / BUILD_ID / source hash: "
        f"{report.get('buildId') or 'n/a'} / {game.get('sha256', 'n/a')}\n"
        f"- Passed checks: {', '.join(passed) if passed else 'none yet'}\n"
        f"- Open issues: {', '.join(open_issues) if open_issues else 'none recorded'}\n"
        f"- Run commands:\n" +
        ("".join(f"  - `{item}`\n" for item in commands) if commands else "  - none\n") +
        f"- Next step: {report.get('nextStep', 'Review the delivery report and inspect player-facing visuals.')}\n",
        encoding="utf-8",
    )


def package_and_report(project: Path, out_dir: Path, web_export: Path | None = None,
                       source_zip_name: str = "game-source.zip",
                       quality_review: Path | None = None,
                       browser_report: Path | None = None,
                       preflight: Path | None = None,
                       release_evidence: Path | None = None) -> dict[str, Any]:
    project = project.expanduser().resolve()
    out_dir = out_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    staged = out_dir / "source-tree"
    copied = stage_source(project, staged)
    tree_hash, tree_entries = deterministic_tree_hash(staged)
    identities = artifact_identities(staged)
    archive = out_dir / source_zip_name
    write_zip(staged, archive)
    identities["package"] = package_identity(archive)

    web_record: dict[str, Any] | None = None
    commands = [
        f"python {SKILL_SCRIPTS / 'package_and_report.py'} {project} --out {out_dir}",
    ]
    if web_export is not None:
        web_export = web_export.expanduser().resolve()
        stamped = stamp_web(web_export)
        web_hash, _ = deterministic_tree_hash(web_export)
        web_record = {
            "path": str(web_export),
            "sha256": web_hash,
            "buildId": stamped["buildId"],
        }
        commands.append(f"python {SKILL_SCRIPTS / 'stamp_web_build.py'} {web_export}")
        commands.append(f"python {SKILL_SCRIPTS / 'serve_web_export.py'} {web_export}")

    validators: list[dict[str, Any]] = []
    if quality_review is not None:
        artifact = web_export if web_export is not None else staged
        result = _run_validator("validate_quality_review.py",
                                [str(quality_review), "--artifact", str(artifact)])
        validators.append({"name": "quality_review", "status": result.get("status"), "result": result})
    if preflight is not None:
        validators.append({
            "name": "web_preflight_linked",
            "status": "LINKED",
            "path": str(preflight),
            "sha256": sha256_file(preflight),
            "note": "Existing preflight attached by hash; this entry does not re-perceive the browser",
        })
    if release_evidence is not None:
        artifact = web_export if web_export is not None else archive
        result = _run_validator("validate_release_evidence.py",
                                [str(artifact), "--evidence", str(release_evidence)])
        validators.append({"name": "release_evidence", "status": result.get("status"), "result": result})
    if browser_report is not None:
        validators.append({
            "name": "browser_report_linked",
            "status": "UNREVIEWED",
            "path": str(browser_report),
            "sha256": sha256_file(browser_report),
            "note": "Linked only; visual/player judgments are not inferred from the filename",
        })

    skill_version = (SKILL_SCRIPTS.parent / "VERSION").read_text(encoding="utf-8").strip()
    report = {
        "schemaVersion": 1,
        "generatedAt": utc_now(),
        "skillVersion": skill_version,
        "visualJudgmentRequired": True,
        "project": str(project),
        "sourceTree": {
            "path": str(staged),
            "sha256": tree_hash,
            "fileCount": len(tree_entries),
        },
        "sourceZip": identities["package"],
        "webExport": web_record,
        "buildId": None if web_record is None else web_record["buildId"],
        "identities": {
            "gameContent": identities["gameContent"],
            "testHarness": identities["testHarness"],
            "displaySet": identities["displaySet"],
            "packaging": identities["packaging"],
            "package": identities["package"],
        },
        "copiedFiles": copied,
        "validators": validators,
        "commands": commands,
        "nextStep": "Inspect player-facing visuals and bind only the evidence that was actually reviewed.",
        "validationScope": "hashes, staging, ZIP membership, and optional validator invocation; not beauty, fun, or honest play",
    }
    write_json(out_dir / "delivery_report.json", report)
    write_json(out_dir / "identities.json", {
        "schemaVersion": 1,
        "generatedAt": report["generatedAt"],
        **{key: identities[key] for key in ("gameContent", "testHarness", "displaySet", "packaging", "package")},
    })
    write_session_status(out_dir / "session_status.md", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project")
    parser.add_argument("--out", required=True)
    parser.add_argument("--web-export")
    parser.add_argument("--source-zip-name", default="game-source.zip")
    parser.add_argument("--quality-review")
    parser.add_argument("--browser-report")
    parser.add_argument("--preflight")
    parser.add_argument("--release-evidence")
    args = parser.parse_args()
    try:
        report = package_and_report(
            Path(args.project), Path(args.out),
            Path(args.web_export) if args.web_export else None,
            args.source_zip_name,
            Path(args.quality_review) if args.quality_review else None,
            Path(args.browser_report) if args.browser_report else None,
            Path(args.preflight) if args.preflight else None,
            Path(args.release_evidence) if args.release_evidence else None)
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"status": "FAIL", "errors": [str(exc)]}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
