#!/usr/bin/env python3
"""Bind a review to current artifact, brief and plan hashes, then detect drift.

This creates a checkpoint, not a sandbox or a PASS record. It never runs Godot.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from _common import DEFAULT_TREE_EXCLUDES, DEFAULT_PREFIX_EXCLUDES, deterministic_tree_hash, utc_now
from _review_state import SHA256, check_reference, fingerprint, local_path, project_root, read_record


def exclusions() -> dict[str, list[str]]:
    return {"parts": sorted(DEFAULT_TREE_EXCLUDES), "prefixes": sorted(DEFAULT_PREFIX_EXCLUDES)}


def freeze(root: Path, brief: str, plan: str, output: str) -> dict[str, Any]:
    dest = local_path(root, output)
    if not output.startswith(".prototype/"):
        raise ValueError("checkpoint must live under .prototype/ outside artifact identity")
    if dest.exists() or output in {brief, plan}:
        raise ValueError("refusing to overwrite checkpoint, brief or plan")
    refs = {"brief": fingerprint(root, brief), "plan": fingerprint(root, plan)}
    digest, files = deterministic_tree_hash(root)
    if not files:
        raise ValueError("empty artifact cannot be checkpointed")
    record = {"schemaVersion": 1, "createdAt": utc_now(), "artifactSha256": digest,
              "fileCount": len(files), "exclusions": exclusions(), **refs,
              "scope": "artifact/brief/plan identity only; not sandbox enforcement or test results"}
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation preserves older checkpoints and review evidence.
    with dest.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    return record


def check(root: Path, record: dict[str, Any]) -> dict[str, Any]:
    if (type(record.get("schemaVersion")) is not int or record["schemaVersion"] != 1
            or not isinstance(record.get("artifactSha256"), str)
            or not SHA256.fullmatch(record["artifactSha256"])
            or record.get("exclusions") != exclusions()
            or type(record.get("fileCount")) is not int or record["fileCount"] <= 0):
        raise ValueError("invalid checkpoint schema, identity or exclusions")
    changes = []
    for key in ("brief", "plan"):
        changed = check_reference(root, record.get(key))
        if changed:
            changes.append(changed)
    digest, files = deterministic_tree_hash(root)
    if digest != record["artifactSha256"] or len(files) != record["fileCount"]:
        changes.append("artifact changed since checkpoint")
    return {"status": "DRIFT" if changes else "MATCH", "changes": changes,
            "artifactSha256": digest, "scope": "identity only; not evidence of execution, independence or enjoyment"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("freeze")
    create.add_argument("project")
    create.add_argument("--brief", default=".prototype/spec/mission_brief.md")
    create.add_argument("--plan", required=True, help="Existing scenario/experiment plan, relative to project")
    create.add_argument("--out", required=True, help="New checkpoint under .prototype/")
    verify = sub.add_parser("check")
    verify.add_argument("project")
    verify.add_argument("--record", required=True, help="Project-relative checkpoint path")
    args = parser.parse_args()
    try:
        root = project_root(Path(args.project))
        if args.command == "freeze":
            result = freeze(root, args.brief, args.plan, args.out)
        else:
            result = check(root, read_record(local_path(root, args.record)))
    except (OSError, ValueError, TypeError, UnicodeError) as exc:
        print(json.dumps({"status": "INVALID", "errors": [str(exc)]}))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get("status") == "DRIFT" else 0


if __name__ == "__main__":
    raise SystemExit(main())
