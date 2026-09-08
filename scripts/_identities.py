#!/usr/bin/env python3
"""Classify project files and hash game content, test harness, and display sets.

These identities prove whether related files changed. They do not prove a test was run.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Callable, Iterable

from _common import deterministic_tree_hash, sha256_file, should_exclude

HARNESS_PREFIXES = ("tests/", "qa/", "test/")
DISPLAY_PREFIXES = ("assets/ui/", "assets/fonts/", "ui/", "fonts/", "theme/")
DISPLAY_SUFFIXES = (".ttf", ".otf", ".woff", ".woff2")
PACKAGING_PREFIXES = ("docs/", "release/", ".prototype/")
PACKAGING_NAMES = {"readme.md", "license", "changelog.md", "art.md", "agents.md"}
GENERATED_WEB = ("export/web", "export/web/")


def posix(relative: Path | str) -> str:
    return Path(relative).as_posix().lstrip("./")


def is_generated_web(relative: str) -> bool:
    path = posix(relative)
    return path == "export/web" or path.startswith("export/web/")


def classify_path(relative: Path | str) -> str:
    path = posix(relative)
    lowered = path.lower()
    if is_generated_web(path) or should_exclude(Path(path)):
        return "excluded"
    if any(lowered == prefix.rstrip("/") or lowered.startswith(prefix) for prefix in HARNESS_PREFIXES):
        return "harness"
    if any(lowered == prefix.rstrip("/") or lowered.startswith(prefix) for prefix in PACKAGING_PREFIXES):
        return "packaging"
    if Path(lowered).name in PACKAGING_NAMES:
        return "packaging"
    if any(lowered == prefix.rstrip("/") or lowered.startswith(prefix) for prefix in DISPLAY_PREFIXES):
        return "display"
    if lowered.endswith(DISPLAY_SUFFIXES) or "theme" in Path(lowered).name:
        return "display"
    return "rules"


def _hash_entries(entries: Iterable[dict[str, Any]]) -> str:
    aggregate = hashlib.sha256()
    for entry in sorted(entries, key=lambda item: item["path"]):
        aggregate.update(entry["path"].encode("utf-8"))
        aggregate.update(b"\0")
        aggregate.update(str(entry["size"]).encode("ascii"))
        aggregate.update(b"\0")
        aggregate.update(entry["sha256"].encode("ascii"))
        aggregate.update(b"\n")
    return aggregate.hexdigest()


def project_files(root: Path, extra_excludes: Iterable[str] = ()) -> list[dict[str, Any]]:
    root = root.expanduser().resolve()
    _, entries = deterministic_tree_hash(root, extra_excludes)
    return [entry for entry in entries if classify_path(entry["path"]) != "excluded" and not is_generated_web(entry["path"])]


def scoped_identity(root: Path, extra_excludes: Iterable[str] = (),
                    include: Callable[[str], bool] | None = None) -> dict[str, Any]:
    rows = []
    for entry in project_files(root, extra_excludes):
        if include is None or include(entry["path"]):
            rows.append(entry)
    return {"sha256": _hash_entries(rows), "fileCount": len(rows), "files": rows}


def artifact_identities(root: Path, extra_excludes: Iterable[str] = ()) -> dict[str, Any]:
    files = project_files(root, extra_excludes)
    grouped: dict[str, list[dict[str, Any]]] = {"rules": [], "display": [], "harness": [], "packaging": []}
    for entry in files:
        grouped[classify_path(entry["path"])].append(entry)
    game = grouped["rules"] + grouped["display"]
    return {
        "schemaVersion": 1,
        "root": str(root.expanduser().resolve()),
        "gameContent": {"sha256": _hash_entries(game), "fileCount": len(game)},
        "testHarness": {"sha256": _hash_entries(grouped["harness"]), "fileCount": len(grouped["harness"])},
        "displaySet": {"sha256": _hash_entries(grouped["display"]), "fileCount": len(grouped["display"])},
        "packaging": {"sha256": _hash_entries(grouped["packaging"]), "fileCount": len(grouped["packaging"])},
        "classes": {key: [row["path"] for row in rows] for key, rows in grouped.items()},
    }


def classify_changes(paths: Iterable[str]) -> dict[str, Any]:
    classes: dict[str, list[str]] = {"rules": [], "display": [], "harness": [], "packaging": [], "excluded": []}
    for raw in paths:
        kind = classify_path(raw)
        classes.setdefault(kind, []).append(posix(raw))
    rerun = [name for name in ("rules", "display", "harness", "packaging") if classes[name]]
    reuse = [name for name in ("rules", "display", "harness", "packaging") if name not in rerun]
    return {"changedClasses": [name for name in rerun], "rerun": rerun, "reuseIfUnchanged": reuse, "paths": classes}


def package_identity(archive: Path) -> dict[str, Any]:
    digest = sha256_file(archive)
    return {"path": str(archive), "sha256": digest, "size": archive.stat().st_size}
