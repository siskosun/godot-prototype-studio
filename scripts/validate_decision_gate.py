#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

from _common import load_json

ALLOWED_TYPES = {"DIRECTION_GATE", "TASTE_GATE", "RISK_GATE", "COMMITMENT_GATE"}
ALLOWED_STATUS = {"OPEN", "RESOLVED", "DEFERRED", "SUPERSEDED"}
REQUIRED = {"schemaVersion", "id", "type", "status", "owner", "decision", "whyNow", "evidence", "recommendation", "options", "downstreamImpact", "humanDecision", "resolvedAt"}


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_decision_gate.py <decision_gate.json>")
        return 2
    path = Path(sys.argv[1])
    try:
        data = load_json(path)
    except ValueError as exc:
        print(f"DECISION GATE INVALID\n- {exc}")
        return 2
    errors: list[str] = []
    if not isinstance(data, dict):
        errors.append("root must be an object")
        data = {}
    missing = sorted(REQUIRED - set(data))
    if missing:
        errors.append("missing fields: " + ", ".join(missing))
    if data.get("type") not in ALLOWED_TYPES:
        errors.append("invalid gate type")
    if data.get("status") not in ALLOWED_STATUS:
        errors.append("invalid status")
    if data.get("owner") != "human":
        errors.append("owner must be human")
    if not re.fullmatch(r"[A-Z]{1,4}-\d{3,}", str(data.get("id", ""))):
        errors.append("id must look like DG-001")
    for field in ("decision", "whyNow", "downstreamImpact"):
        if not str(data.get(field, "")).strip():
            errors.append(f"{field} must be non-empty")
    evidence = data.get("evidence")
    if not isinstance(evidence, list):
        errors.append("evidence must be a list")
    options = data.get("options")
    option_ids: set[str] = set()
    if not isinstance(options, list) or not 1 <= len(options) <= 3:
        errors.append("options must contain 1 to 3 items")
    else:
        for index, option in enumerate(options):
            if not isinstance(option, dict):
                errors.append(f"option[{index}] must be an object")
                continue
            oid = str(option.get("id", "")).strip()
            if not oid or oid in option_ids:
                errors.append(f"option[{index}] has empty or duplicate id")
            option_ids.add(oid)
            if not str(option.get("label", "")).strip() or not str(option.get("tradeoff", "")).strip():
                errors.append(f"option[{index}] requires label and tradeoff")
    recommendation = data.get("recommendation")
    if not isinstance(recommendation, dict):
        errors.append("recommendation must be an object")
    else:
        if recommendation.get("optionId") not in option_ids:
            errors.append("recommendation.optionId must reference an option")
        if not str(recommendation.get("reason", "")).strip():
            errors.append("recommendation.reason must be non-empty")
    status = data.get("status")
    if status == "RESOLVED":
        if not str(data.get("humanDecision") or "").strip():
            errors.append("resolved gate requires humanDecision")
        if not str(data.get("resolvedAt") or "").strip():
            errors.append("resolved gate requires resolvedAt")
    elif status == "OPEN" and data.get("humanDecision") not in (None, ""):
        errors.append("open gate cannot already contain humanDecision")

    if status == "SUPERSEDED":
        if not str(data.get("authorityReference") or "").strip():
            errors.append("superseded gate requires authorityReference to recorded delegation or replacement")
        if not str(data.get("supersededAt") or "").strip():
            errors.append("superseded gate requires supersededAt")
        if data.get("humanDecision") not in (None, ""):
            errors.append("supersession is not a fabricated humanDecision; preserve any real decision separately")

    if errors:
        print("DECISION GATE INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"DECISION GATE VALID ({status})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
