#!/usr/bin/env python3
"""Structural check only; does not infer authority, rights, quality, or completion."""
from __future__ import annotations
import argparse
import re
from pathlib import Path

REQUIRED = ("Outcome", "Delivery", "Success", "Evidence Required", "Boundaries", "Non-goals", "Execution Authority", "Completion")
VISUAL_SECTION = "Visual Reference Intent"
VISUAL_MODES = {"PARTIAL_REFERENCE", "PIXEL_ACCURATE_REFERENCE", "ORIGINAL_DELEGATED", "NOT_APPLICABLE"}
PLACEHOLDER = re.compile(r"\b(?:TBD|TODO|UNSET|UNRESOLVED)\b|^\s*(?:-\s+[^:\n]+:\s*)?\[[^\]\n]+\]\s*$", re.MULTILINE)


def field(section: str, name: str) -> str:
    match = re.search(rf"^\s*-\s*{re.escape(name)}\s*:\s*(.*?)\s*$", section, re.MULTILINE | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def concrete(value: str) -> bool:
    if not value or PLACEHOLDER.search(value):
        return False
    return value.strip().lower() not in {"none", "unknown", "unresolved", "pending", "n/a", "na", "not applicable"}


def validate_visual_intent(section: str) -> list[str]:
    errors: list[str] = []
    mode = field(section, "Mode").upper()
    if mode not in VISUAL_MODES:
        errors.append("Visual Reference Intent has invalid or unresolved Mode")
        return errors
    if mode == "PARTIAL_REFERENCE" and not concrete(field(section, "Partial scope")):
        errors.append("PARTIAL_REFERENCE requires a concrete Partial scope")
    if mode == "PIXEL_ACCURATE_REFERENCE":
        if not concrete(field(section, "Pixel targets")):
            errors.append("PIXEL_ACCURATE_REFERENCE requires concrete Pixel targets")
        if not concrete(field(section, "Rights status")):
            errors.append("PIXEL_ACCURATE_REFERENCE requires a concrete Rights status")
    if mode == "NOT_APPLICABLE" and not concrete(field(section, "Reason")):
        errors.append("NOT_APPLICABLE requires a concrete Reason")
    return errors


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
    if VISUAL_SECTION in sections:
        if not sections[VISUAL_SECTION]:
            errors.append(f"missing or empty section: {VISUAL_SECTION}")
        else:
            errors.extend(validate_visual_intent(sections[VISUAL_SECTION]))
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
    print("BRIEF INVALID" if errors else "BRIEF STRUCTURE VALID (not evidence of authority, rights, quality, or completion)")
    for error in errors:
        print(f"- {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
