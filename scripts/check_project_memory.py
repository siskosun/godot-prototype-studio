#!/usr/bin/env python3
"""Inspect optional project-memory provenance and freshness without editing it.

CURRENT_RECORD means recorded files match, not that a statement is true or authorized.
Exit 0: all active references current (or no entries); 1: stale/unverified; 2: invalid.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from _review_state import check_reference, local_path, project_root, read_record

KINDS = {"decision", "observation", "hypothesis", "rejected_attempt", "constraint"}


def inspect_memory(data: dict[str, Any], root: Path) -> dict[str, Any]:
    if not isinstance(data, dict) or type(data.get("schemaVersion")) is not int or data["schemaVersion"] != 1:
        raise ValueError("integer schemaVersion 1 required")
    entries = data.get("entries")
    if not isinstance(entries, list) or len(entries) > 512:
        raise ValueError("entries must be a list of at most 512 records")
    ids: set[str] = set()
    output: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("memory entry must be an object")
        for key in ("id", "claim", "scope", "revisitWhen"):
            if not isinstance(entry.get(key), str) or not entry[key].strip():
                raise ValueError(f"entry requires nonempty {key}")
        if entry["id"] in ids:
            raise ValueError("duplicate memory id")
        ids.add(entry["id"])
        if entry.get("kind") not in KINDS or entry.get("status") not in {"ACTIVE", "SUPERSEDED"}:
            raise ValueError("invalid memory kind/status")
        if entry["status"] == "SUPERSEDED" and (not isinstance(entry.get("supersededReason"), str)
                                                   or not entry["supersededReason"].strip()):
            raise ValueError("superseded record needs supersededReason")
        changes: list[str] = []
        for key in ("sources", "dependsOn"):
            refs = entry.get(key)
            if not isinstance(refs, list) or len(refs) > 256:
                raise ValueError(f"{key} must be a list of at most 256 file references")
            for ref in refs:
                changed = check_reference(root, ref)
                if changed:
                    changes.append(changed)
        if entry["status"] == "SUPERSEDED":
            state = "SUPERSEDED"
        elif changes:
            state = "STALE"
        elif not entry["sources"] or not entry["dependsOn"]:
            state = "UNVERIFIED"
        else:
            state = "CURRENT_RECORD"
        output.append({"id": entry["id"], "kind": entry["kind"], "state": state,
                       "changes": changes, "revisitWhen": entry["revisitWhen"]})
    status = "REVIEW_REQUIRED" if any(row["state"] in {"STALE", "UNVERIFIED"} for row in output) else "RECORDS_CURRENT"
    return {"status": status, "entries": output,
            "scope": "file-reference freshness only; not truth, authority, completeness or creative quality"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project")
    parser.add_argument("--memory", default=".prototype/project_memory.json")
    args = parser.parse_args()
    try:
        root = project_root(Path(args.project))
        result = inspect_memory(read_record(local_path(root, args.memory)), root)
    except (OSError, ValueError, TypeError, UnicodeError) as exc:
        print(json.dumps({"status": "INVALID", "errors": [str(exc)]}))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "RECORDS_CURRENT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
