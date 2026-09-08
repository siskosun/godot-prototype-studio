#!/usr/bin/env python3
"""Structural check only; does not infer authority, quality, or task completion."""
from __future__ import annotations
import argparse
import re
from pathlib import Path

REQUIRED = ("Outcome", "Delivery", "Success", "Evidence Required", "Boundaries", "Non-goals", "Execution Authority", "Completion")
PLACEHOLDER = re.compile(r"\b(?:TBD|TODO|UNSET)\b|^\s*(?:-\s+[^:\n]+:\s*)?\[[^\]\n]+\]\s*$", re.MULTILINE)

def validate_text(text: str) -> list[str]:
    headings = list(re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE))
    sections: dict[str, str] = {}
    errors: list[str] = []
    for index, match in enumerate(headings):
        title = match.group(1)
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        if title in sections:
            errors.append(f"duplicate section: {title}")
        sections[title] = text[match.end():end].strip()
    for title in REQUIRED:
        if not sections.get(title):
            errors.append(f"missing or empty section: {title}")
        elif PLACEHOLDER.search(sections[title]):
            errors.append(f"unresolved placeholder in: {title}")
    if "DONE" not in sections.get("Completion", "") or "BLOCKED" not in sections.get("Completion", ""):
        errors.append("Completion must distinguish DONE and BLOCKED")
    return errors

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brief")
    args = parser.parse_args()
    try:
        errors = validate_text(Path(args.brief).read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        print(f"BRIEF INVALID: {exc}")
        return 2
    print("BRIEF INVALID" if errors else "BRIEF STRUCTURE VALID (not evidence of authority or completion)")
    for error in errors:
        print(f"- {error}")
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
