#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from _common import utc_now

DIRS = [
    ".prototype/spec",
    ".prototype/decisions",
    ".prototype/playtests",
    ".prototype/evidence",
    ".prototype/release",
    ".prototype/logs",
]

LEGACY_TEMPLATE_MAP = {
    "project_profile.md": ".prototype/spec/project_profile.md",
    "capability_profile.json": ".prototype/spec/capability_profile.json",
    "prototype_contract.md": ".prototype/spec/prototype_contract.md",
    "visual_canon.json": ".prototype/spec/visual_canon.json",
    "asset_manifest.json": ".prototype/spec/asset_manifest.json",
    "evidence_manifest.json": ".prototype/evidence/manifest.json",
    "creator_checkpoint.md": ".prototype/creator_checkpoint.md",
}


def copy_if_missing(source: Path, destination: Path) -> bool:
    if destination.exists():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return True


def copy_starter(starter: Path, root: Path) -> list[str]:
    collisions = [p.relative_to(starter).as_posix() for p in starter.rglob("*") if p.is_file() and (root / p.relative_to(starter)).exists()]
    if collisions:
        raise ValueError("starter would overwrite existing files: " + ", ".join(collisions[:10]))
    copied: list[str] = []
    for path in starter.rglob("*"):
        if not path.is_file():
            continue
        destination = root / path.relative_to(starter)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        copied.append(destination.relative_to(root).as_posix())
    return copied


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize Godot Prototype Studio state in a project.")
    parser.add_argument("project_root")
    parser.add_argument("--with-starter", action="store_true", help="Copy the thin 2D starter into a blank directory.")
    parser.add_argument("--legacy-full", action="store_true", help="Create optional detailed research records (not needed for normal tasks).")
    args = parser.parse_args()

    root = Path(args.project_root).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    skill_root = Path(__file__).resolve().parent.parent
    templates = skill_root / "templates"

    # Check starter collisions before writing anything into the project.
    if args.with_starter:
        starter = skill_root / "assets/starter-2d"
        collisions = [str(x.relative_to(starter)) for x in starter.rglob("*")
                      if x.is_file() and (root / x.relative_to(starter)).exists()]
        if collisions:
            parser.error("starter would overwrite existing files: " + ", ".join(collisions[:10]))
    for directory in (DIRS if args.legacy_full else [".prototype/spec"]):
        (root / directory).mkdir(parents=True, exist_ok=True)
    template_map = {"mission_brief.md": ".prototype/spec/mission_brief.md"}
    if args.legacy_full:
        template_map.update(LEGACY_TEMPLATE_MAP)
    created: list[str] = []
    for source_name, relative_destination in template_map.items():
        destination = root / relative_destination
        if copy_if_missing(templates / source_name, destination):
            created.append(relative_destination)

    version_file = skill_root / "VERSION"
    skill_version = version_file.read_text(encoding="utf-8").strip() if version_file.exists() else "unknown"

    progress = root / ".prototype/progress.md"
    if not progress.exists():
        progress.write_text(
            "# Session Status\n\n"
            f"- Skill / project version: {skill_version}\n"
            "- Current artifact / BUILD_ID / source hash: none yet\n"
            "- Passed checks: none yet\n"
            "- Open issues: none recorded\n"
            "- Run commands:\n"
            "  - none\n"
            "- Next step: Complete the brief from known decisions; continue within delegation.\n"
            f"- Initialized: {utc_now()}\n"
            "- Brief: spec/mission_brief.md\n",
            encoding="utf-8",
        )
        created.append(".prototype/progress.md")

    if args.legacy_full:
        experiments = root / ".prototype/logs/experiments.jsonl"
        experiments.touch(exist_ok=True)

    starter_files: list[str] = []
    if args.with_starter:
        if (root / "project.godot").exists():
            raise SystemExit("ERROR: --with-starter requires a blank directory without project.godot")
        starter_files = copy_starter(skill_root / "assets/starter-2d", root)

    result = {
        "projectRoot": str(root),
        "created": created,
        "starterFiles": starter_files,
        "existingFilesPreserved": True,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
