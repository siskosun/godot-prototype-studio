#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_HEADINGS = [
    "## 1. Player Promise",
    "## 2. Primary Question and Hypothesis",
    "## 3. Design Pillars",
    "## 4. Dominant Loop",
    "## 5. State, Legal Actions, and P0 Mechanics",
    "## 7. Representative Scenarios",
    "## 8. Machine-Verifiable Acceptance",
    "## 9. Human-Judged Experience",
    "## 10. Instrumentation and Evidence",
    "## 11. Scope, Fidelity, and Reuse",
]
REQUIRED_LABELS = [
    "Player Promise", "Intended Audience", "Prototype Kind", "Primary Question", "Hypothesis",
    "Supporting Observation", "Disconfirming Observation", "Decision Impact if SUPPORTED",
    "Decision Impact if REVISE", "Decision Impact if NOT_SUPPORTED", "Decision Impact if INCONCLUSIVE",
    "State", "Legal Actions", "Included", "Excluded", "Fidelity Target", "Code Intent",
    "Expansion Condition", "Stop Rule",
]
MECHANIC_TOKENS = ["Trigger", "Preconditions", "Player Action", "State Delta", "Feedback", "Termination"]


def values_for(text: str) -> dict[str, str]:
    return {m.group(1).strip(): m.group(2).strip() for m in re.finditer(r"^- ([^:\n]+):\s*(.*)$", text, re.MULTILINE)}


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_prototype_contract.py <prototype_contract.md>")
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"PROTOTYPE CONTRACT INVALID\n- missing file: {path}")
        return 2
    text = path.read_text(encoding="utf-8")
    values = values_for(text)
    errors: list[str] = []

    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"missing heading: {heading}")
    for label in REQUIRED_LABELS:
        value = values.get(label, "")
        if not value:
            errors.append(f"empty or missing field: {label}")
        elif value.startswith("<") or value in {"TBD", "UNSET"}:
            errors.append(f"unresolved field: {label}")
    kind = values.get("Prototype Kind")
    if kind not in {"MECHANIC_PROBE", "EXPERIENCE_SLICE", "TECHNICAL_SPIKE", "PITCH_SLICE"}:
        errors.append("Prototype Kind must select one allowed value")
    code_intent = values.get("Code Intent")
    if code_intent not in {"disposable", "selectively reusable", "production-intent"}:
        errors.append("Code Intent must select disposable, selectively reusable, or production-intent")

    pillars = re.findall(r"^- P\d+:\s*(\S.*)$", text, re.MULTILINE)
    if kind == "TECHNICAL_SPIKE":
        if len(pillars) > 4:
            errors.append(f"Design Pillars must contain 0 to 4 filled entries for a technical spike, got {len(pillars)}")
    elif not 1 <= len(pillars) <= 4:
        errors.append(f"Design Pillars must contain 1 to 4 filled entries, got {len(pillars)}")

    mechanics = re.findall(r"^- M\d+:\s*(.+)$", text, re.MULTILINE)
    if not mechanics:
        errors.append("at least one P0 mechanic M1 is required")
    for index, mechanic in enumerate(mechanics, 1):
        missing = [token for token in MECHANIC_TOKENS if token not in mechanic]
        if missing:
            errors.append(f"M{index} missing mechanic tokens: {', '.join(missing)}")

    scenarios = re.findall(r"^- S\d+:\s*(\S.*)$", text, re.MULTILINE)
    if not 2 <= len(scenarios) <= 4:
        errors.append(f"Representative Scenarios must contain 2 to 4 filled entries, got {len(scenarios)}")
    machine = re.findall(r"^- A\d+:\s*(\S.*)$", text, re.MULTILINE)
    human = re.findall(r"^- H\d+:\s*(\S.*)$", text, re.MULTILINE)
    if not machine:
        errors.append("at least one machine-verifiable acceptance item is required")
    if not human:
        errors.append("at least one human-judged item or explicit N/A item is required")

    if "Verdict Vocabulary: SUPPORTED | REVISE | NOT_SUPPORTED | INCONCLUSIVE" not in text:
        errors.append("verdict vocabulary is missing or changed")

    if errors:
        print("PROTOTYPE CONTRACT INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PROTOTYPE CONTRACT VALID ({len(mechanics)} mechanics, {len(scenarios)} scenarios)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
