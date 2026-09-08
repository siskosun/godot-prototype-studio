#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED = [
    "Program Question",
    "Approved Objective",
    "Human-Owned Decisions",
    "Allowed Files or Systems",
    "Allowed Variables and Bounds",
    "Allowed Experiment Types",
    "Maximum Experiments",
    "Maximum Runtime or Resource Budget",
    "Required Evidence per Experiment",
    "Decision-Relevant Checkpoint",
    "Stop Conditions",
    "Escalation Conditions",
    "Rollback Strategy",
    "Resume State Location",
    "External Actions Allowed",
    "Completion Rule",
]


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_program_contract.py <supervised_program.md>")
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"PROGRAM CONTRACT INVALID\n- missing file: {path}")
        return 2
    text = path.read_text(encoding="utf-8")
    values = {m.group(1).strip(): m.group(2).strip() for m in re.finditer(r"^- ([^:\n]+):\s*(.*)$", text, re.MULTILINE)}
    errors: list[str] = []
    for field in REQUIRED:
        value = values.get(field, "")
        if not value:
            errors.append(f"empty or missing field: {field}")
        elif value in {"TBD", "UNSET"} or value.startswith("<"):
            errors.append(f"unresolved field: {field}")
    maximum = values.get("Maximum Experiments", "")
    if maximum and (not maximum.isdigit() or int(maximum) < 1 or int(maximum) > 100):
        errors.append("Maximum Experiments must be an integer from 1 to 100")
    external = values.get("External Actions Allowed", "")
    if external.lower() != "none":
        errors.append("External Actions Allowed must be 'none'; use a separate RISK/COMMITMENT gate for external actions")
    if errors:
        print("PROGRAM CONTRACT INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PROGRAM CONTRACT VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
