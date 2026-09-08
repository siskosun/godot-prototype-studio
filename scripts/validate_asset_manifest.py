#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

from _common import load_json

REQUIRED = {
    "id", "sourceFile", "runtimePath", "type", "role", "sourceOrGenerator", "provenanceReference",
    "licenseStatus", "humanEdits", "expectedScene", "expectedNode", "required",
}
LICENSES = {"unknown", "prototype-only", "cleared", "restricted"}


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print("usage: validate_asset_manifest.py <asset_manifest.json> [project-root]")
        return 2
    path = Path(sys.argv[1])
    project_root = Path(sys.argv[2]).resolve() if len(sys.argv) == 3 else path.parent.parent.parent.resolve()
    try:
        data = load_json(path)
    except ValueError as exc:
        print(f"ASSET MANIFEST INVALID\n- {exc}")
        return 2
    errors: list[str] = []
    assets = data.get("assets") if isinstance(data, dict) else None
    if not isinstance(assets, list):
        errors.append("assets must be a list")
        assets = []
    seen: set[str] = set()
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            errors.append(f"asset[{index}] must be an object")
            continue
        missing = REQUIRED - set(asset)
        if missing:
            errors.append(f"asset[{index}] missing fields: {', '.join(sorted(missing))}")
        asset_id = str(asset.get("id", "")).strip()
        if not asset_id or asset_id in seen:
            errors.append(f"asset[{index}] has empty or duplicate id")
        seen.add(asset_id)
        runtime_path = str(asset.get("runtimePath", ""))
        if runtime_path and not runtime_path.startswith("res://"):
            errors.append(f"{asset_id}: runtimePath must start with res://")
        if asset.get("licenseStatus") not in LICENSES:
            errors.append(f"{asset_id}: invalid licenseStatus")
        if not isinstance(asset.get("required"), bool):
            errors.append(f"{asset_id}: required must be boolean")
        source_file = str(asset.get("sourceFile", "")).strip()
        if asset.get("required") and source_file:
            source = Path(source_file)
            if not source.is_absolute():
                source = project_root / source
            if not source.exists():
                errors.append(f"{asset_id}: required source file missing: {source}")
        if asset.get("required") and asset.get("licenseStatus") == "unknown":
            errors.append(f"{asset_id}: required asset has unknown license status")
    if errors:
        print("ASSET MANIFEST INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"ASSET MANIFEST VALID ({len(assets)} assets)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
