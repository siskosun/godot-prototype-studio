#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_HEADINGS = ["## Game Designer Review", "## Novice Vibe Creator Review", "## Publisher Review", "## Incorporated Changes"]
REQUIRED_FIELDS = [
    "Build or Tree Hash", "Prototype Question", "Current Verdict", "Evidence Stage", "Player Promise", "Evidence Reviewed",
    "Strongest success", "Highest-risk design contradiction", "Setup friction", "Decision burden",
    "Demonstrable player promise", "Audience evidence", "Commercial assumptions still unproven",
    "Milestone recommendation",
]


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_review_packet.py <review_packet.md>")
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"REVIEW PACKET INVALID\n- missing file: {path}")
        return 2
    text = path.read_text(encoding="utf-8")
    values = {m.group(1).strip(): m.group(2).strip() for m in re.finditer(r"^- ([^:\n]+):\s*(.*)$", text, re.MULTILINE)}
    errors: list[str] = []
    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"missing heading: {heading}")
    for field in REQUIRED_FIELDS:
        if not values.get(field, ""):
            errors.append(f"empty or missing field: {field}")
    if "TBD" in text or "REPLACE_WITH" in text:
        errors.append("unresolved template marker remains")
    verdict = values.get("Current Verdict")
    if verdict not in {"SUPPORTED", "REVISE", "NOT_SUPPORTED", "INCONCLUSIVE"}:
        errors.append("invalid Current Verdict")
    stage = values.get("Evidence Stage")
    if stage not in {"CONCEPT", "EXPERIENCE", "TECHNICAL", "PITCH", "PRODUCTION"}:
        errors.append("invalid Evidence Stage")
    recommendation = values.get("Milestone recommendation")
    if recommendation not in {"ADVANCE", "REVISE", "HOLD", "STOP_THIS_HYPOTHESIS"}:
        errors.append("invalid Milestone recommendation")
    if errors:
        print("REVIEW PACKET INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("REVIEW PACKET VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
