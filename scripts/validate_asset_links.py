#!/usr/bin/env python3
"""Read-only, opt-in validation of asset design and runtime evidence references."""
from __future__ import annotations
import hashlib
import json
import re
import sys
from pathlib import Path


def validate(data: dict, root: Path) -> list[str]:
    if not isinstance(data, dict) or not isinstance(data.get("assets"), list):
        return ["assets must be a list"]
    root = root.resolve()
    errors: list[str] = []
    ids: set[str] = set()
    parents: dict[str, list[str]] = {}

    def local_file(value: object, label: str) -> Path | None:
        if not isinstance(value, str) or not value or "://" in value:
            errors.append(f"{label}: expected project-relative path")
            return None
        relative = Path(value)
        if relative.is_absolute() or ".." in relative.parts:
            errors.append(f"{label}: traversal/absolute path")
            return None
        result = (root / relative).resolve()
        if not result.is_relative_to(root) or not result.is_file():
            errors.append(f"{label}: local file unavailable")
            return None
        return result

    for i, asset in enumerate(data["assets"]):
        if not isinstance(asset, dict):
            errors.append(f"asset[{i}]: expected object")
            continue
        aid = asset.get("id")
        if not isinstance(aid, str) or not aid.strip():
            errors.append(f"asset[{i}]: invalid id")
        elif aid in ids:
            errors.append(f"asset[{i}]: duplicate id {aid}")
        else:
            ids.add(aid)

    for i, asset in enumerate(data["assets"]):
        if not isinstance(asset, dict):
            continue
        aid = asset.get("id", f"asset[{i}]")
        if "designRef" in asset:
            local_file(asset["designRef"], f"{aid}.designRef")
        if "derivedFrom" in asset:
            p = asset["derivedFrom"]
            if not isinstance(p, list) or any(not isinstance(x, str) for x in p) or len(set(p)) != len(p):
                errors.append(f"{aid}.derivedFrom: expected unique ID strings")
            else:
                for x in p:
                    if x not in ids or x == aid:
                        errors.append(f"{aid}.derivedFrom: invalid parent {x}")
                if isinstance(aid, str) and aid in ids:
                    parents[aid] = p
        if "runtimeEvidence" in asset:
            evidence = asset["runtimeEvidence"]
            if not isinstance(evidence, list):
                errors.append(f"{aid}.runtimeEvidence: expected list")
                continue
            for j, item in enumerate(evidence):
                if not isinstance(item, dict):
                    errors.append(f"{aid}.runtimeEvidence[{j}]: expected object")
                    continue
                f = local_file(item.get("path"), f"{aid}.runtimeEvidence[{j}]")
                digest = item.get("sha256")
                if digest is not None:
                    if not isinstance(digest, str) or not re.fullmatch("[0-9a-f]{64}", digest):
                        errors.append(f"{aid}.runtimeEvidence[{j}]: invalid sha256")
                    elif f is not None and hashlib.sha256(f.read_bytes()).hexdigest() != digest:
                        errors.append(f"{aid}.runtimeEvidence[{j}]: stale sha256")

    done: set[str] = set()
    def visit(aid: str, chain: set[str]) -> None:
        if aid in chain:
            errors.append(f"asset derivation cycle: {aid}")
        elif aid not in done:
            for x in parents.get(aid, []):
                if x in ids:
                    visit(x, chain | {aid})
            done.add(aid)
    for aid in parents:
        visit(aid, set())
    return errors


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: validate_asset_links.py MANIFEST PROJECT_ROOT")
        return 2
    try:
        errors = validate(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")), Path(sys.argv[2]).resolve(strict=True))
    except (OSError, ValueError) as exc:
        print(f"ASSET LINKS ERROR: {exc}")
        return 2
    if errors:
        print("\n".join(errors))
        return 1
    print("ASSET LINKS VALID (references only; not rendered QA)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
