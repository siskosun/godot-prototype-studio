#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED = [
    "TaskMode", "PrototypeKind", "CollaborationProfile", "ReviewIntensity", "ExistingProject",
    "ProjectName", "GodotVersion", "Language", "TargetPlatform", "TargetViewportOrResolution",
    "PrimaryInput", "PlayerPromise", "PrototypeQuestion", "IntendedAudience",
    "ReferenceGamesOrProducts", "Persistence", "DeliveryTarget", "SuppliedAssetsAndRightsStatus",
    "HardConstraints", "OutOfScope",
]
ENUMS = {
    "TaskMode": {"DISCOVERY", "NEW_PROTOTYPE", "EXPERIMENT", "FEATURE_CHANGE", "BUGFIX", "POLISH_QA", "RELEASE_REVIEW"},
    "PrototypeKind": {"MECHANIC_PROBE", "EXPERIENCE_SLICE", "TECHNICAL_SPIKE", "PITCH_SLICE", "N/A"},
    "CollaborationProfile": {"NOVICE", "DESIGNER", "TECHNICAL", "MIXED"},
    "ReviewIntensity": {"LEAN", "STANDARD", "FULL"},
    "ExistingProject": {"yes", "no"},
    "Language": {"GDScript", "CSHARP", "MIXED", "unknown"},
    "Persistence": {"none", "run", "run+meta", "existing"},
    "DeliveryTarget": {"LOCAL_PROJECT", "GODOT_PROJECT_ZIP", "DESKTOP_BUILD", "WEB_EXPORT", "ANDROID_BUILD", "N/A"},
}


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_project_profile.py <project_profile.md>")
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"PROJECT PROFILE INVALID\n- missing file: {path}")
        return 2
    text = path.read_text(encoding="utf-8")
    values = {m.group(1): m.group(2).strip() for m in re.finditer(r"^- ([A-Za-z][A-Za-z0-9]+):\s*(.*)$", text, re.MULTILINE)}
    errors: list[str] = []
    for key in REQUIRED:
        if key not in values:
            errors.append(f"missing field: {key}")
        elif not values[key]:
            errors.append(f"empty field: {key}")
        elif values[key].startswith("<") or " | " in values[key] or values[key] in {"UNSET", "TBD"}:
            errors.append(f"unresolved template value: {key}")
    for key, allowed in ENUMS.items():
        if key in values and values[key] and values[key] not in allowed:
            errors.append(f"{key} must be one of: {', '.join(sorted(allowed))}")
    if errors:
        print("PROJECT PROFILE INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PROJECT PROFILE VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
