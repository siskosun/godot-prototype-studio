#!/usr/bin/env python3
"""Decide which suites to rerun from changed paths or identity hashes.

Reused evidence is valid only when the matching identity hash is unchanged.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from _common import load_json, write_json
from _identities import artifact_identities, classify_changes, project_files

SUITE_FOR = {
    "rules": "rules",
    "display": "display",
    "harness": "harness",
    "packaging": "packaging",
}
IDENTITY_FOR = {
    "rules": "gameContent",
    "display": "displaySet",
    "harness": "testHarness",
    "packaging": "packaging",
}


def _hash_of(record: dict[str, Any], key: str) -> str | None:
    block = record.get(key)
    if isinstance(block, dict) and isinstance(block.get("sha256"), str) and len(block["sha256"]) == 64:
        return block["sha256"].lower()
    return None


def impact_from_paths(paths: list[str], before: dict[str, Any] | None = None,
                      after: dict[str, Any] | None = None) -> dict[str, Any]:
    classified = classify_changes(paths)
    reuse: list[dict[str, Any]] = []
    blocked: list[str] = []
    for suite in classified["reuseIfUnchanged"]:
        identity = IDENTITY_FOR[suite]
        before_hash = _hash_of(before or {}, identity)
        after_hash = _hash_of(after or {}, identity)
        if before_hash and after_hash and before_hash == after_hash:
            reuse.append({"suite": suite, "identity": identity, "sha256": before_hash})
        else:
            blocked.append(suite)
            if suite not in classified["rerun"]:
                classified["rerun"].append(suite)
    return {
        "schemaVersion": 1,
        "status": "PASS",
        "changedClasses": classified["changedClasses"],
        "rerun": classified["rerun"],
        "reused": reuse,
        "reuseBlocked": blocked,
        "paths": classified["paths"],
        "validationScope": "path classification and identity comparison only; not a playtest",
    }


def compare_trees(before_root: Path, after_root: Path) -> dict[str, Any]:
    before = artifact_identities(before_root)
    after = artifact_identities(after_root)
    before_files = {row["path"]: row["sha256"] for row in project_files(before_root)}
    after_files = {row["path"]: row["sha256"] for row in project_files(after_root)}
    changed_paths = sorted(
        path for path in set(before_files) | set(after_files)
        if before_files.get(path) != after_files.get(path)
    )
    result = impact_from_paths(changed_paths, before, after)
    result["before"] = {key: before[key] for key in ("gameContent", "testHarness", "displaySet", "packaging")}
    result["after"] = {key: after[key] for key in ("gameContent", "testHarness", "displaySet", "packaging")}
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--changed-paths", nargs="+")
    group.add_argument("--before-tree")
    parser.add_argument("--after-tree")
    parser.add_argument("--before-identities")
    parser.add_argument("--after-identities")
    parser.add_argument("--write")
    args = parser.parse_args()
    try:
        if args.changed_paths:
            before = load_json(Path(args.before_identities)) if args.before_identities else None
            after = load_json(Path(args.after_identities)) if args.after_identities else None
            result = impact_from_paths(args.changed_paths, before, after)
        else:
            if not args.after_tree:
                raise ValueError("--after-tree is required with --before-tree")
            result = compare_trees(Path(args.before_tree), Path(args.after_tree))
    except (OSError, ValueError, TypeError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}
    if args.write:
        write_json(Path(args.write).expanduser().resolve(), result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
