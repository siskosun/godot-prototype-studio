#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

from _common import load_json

ALLOWED_SESSION_TYPES = {"SELF_PLAY", "EXPERT_REVIEW", "NAIVE_PLAYER", "TARGET_PLAYER", "PUBLISHER_REVIEW"}
ALLOWED_IMPACTS = {"SUPPORTED", "REVISE", "NOT_SUPPORTED", "INCONCLUSIVE"}
REQUIRED = {
    "schemaVersion", "playtestId", "buildHash", "prototypeQuestion", "sessionType", "participants",
    "completedIntendedLoop", "observations", "participantStatements", "technicalFacts", "humanJudgments",
    "agentInterpretation", "alternativeExplanations", "decisionImpact", "limitations",
}


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_playtest_report.py <playtest_report.json>")
        return 2
    path = Path(sys.argv[1])
    try:
        data = load_json(path)
    except ValueError as exc:
        print(f"PLAYTEST REPORT INVALID\n- {exc}")
        return 2
    errors: list[str] = []
    if not isinstance(data, dict):
        errors.append("root must be an object")
        data = {}
    missing = REQUIRED - set(data)
    if missing:
        errors.append("missing fields: " + ", ".join(sorted(missing)))
    if not re.fullmatch(r"[a-fA-F0-9]{64}", str(data.get("buildHash", ""))):
        errors.append("buildHash must be a 64-character SHA-256")
    if not str(data.get("prototypeQuestion", "")).strip():
        errors.append("prototypeQuestion must be non-empty")
    if data.get("sessionType") not in ALLOWED_SESSION_TYPES:
        errors.append("invalid sessionType")
    if not isinstance(data.get("completedIntendedLoop"), bool):
        errors.append("completedIntendedLoop must be boolean")
    participants = data.get("participants")
    if not isinstance(participants, list) or not participants:
        errors.append("participants must contain at least one entry")
    else:
        for index, participant in enumerate(participants):
            if not isinstance(participant, dict):
                errors.append(f"participant[{index}] must be an object")
                continue
            for field in ("id", "profile", "priorFamiliarity"):
                if not str(participant.get(field, "")).strip():
                    errors.append(f"participant[{index}] missing {field}")
    observations = data.get("observations")
    statements = data.get("participantStatements")
    if not isinstance(observations, list):
        errors.append("observations must be a list")
        observations = []
    if not isinstance(statements, list):
        errors.append("participantStatements must be a list")
        statements = []
    if not observations and not statements:
        errors.append("record at least one observation or participant statement")
    for field in ("technicalFacts", "alternativeExplanations", "limitations"):
        if not isinstance(data.get(field), list):
            errors.append(f"{field} must be a list")
    judgments = data.get("humanJudgments")
    if not isinstance(judgments, dict):
        errors.append("humanJudgments must be an object")
    else:
        tested = judgments.get("testedDimensions")
        not_tested = judgments.get("notTestedDimensions")
        if not isinstance(tested, list) or not isinstance(not_tested, list):
            errors.append("humanJudgments requires testedDimensions and notTestedDimensions lists")
        elif not tested and not not_tested:
            errors.append("classify at least one human-judgment dimension as tested or not tested")
    if not str(data.get("agentInterpretation", "")).strip():
        errors.append("agentInterpretation must be non-empty")
    if data.get("decisionImpact") not in ALLOWED_IMPACTS:
        errors.append("decisionImpact must be SUPPORTED, REVISE, NOT_SUPPORTED, or INCONCLUSIVE")

    if errors:
        print("PLAYTEST REPORT INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PLAYTEST REPORT VALID ({len(participants)} participant(s), impact={data['decisionImpact']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
