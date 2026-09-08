#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _common import utc_now


def path_for(root: Path) -> Path:
    path = root / ".prototype/logs/experiments.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)
    return path


def read_events(path: Path) -> list[dict]:
    events: list[dict] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"malformed JSONL line {number}: {exc}")
        if not isinstance(value, dict):
            raise ValueError(f"line {number} is not an object")
        events.append(value)
    return events


def append(path: Path, value: dict) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False) + "\n")


def next_id(events: list[dict]) -> str:
    numbers = [int(str(e.get("id"))[1:]) for e in events if str(e.get("id", "")).startswith("E") and str(e.get("id"))[1:].isdigit()]
    return f"E{(max(numbers) + 1 if numbers else 1):03d}"


def begin(args: argparse.Namespace) -> int:
    root = Path(args.project_root).expanduser().resolve()
    path = path_for(root)
    try:
        events = read_events(path)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1
    signature = {
        "question": args.question.strip(),
        "hypothesis": args.hypothesis.strip(),
        "change": args.change.strip(),
        "scenario": args.scenario.strip(),
    }
    prior = [e for e in events if e.get("event") == "begin" and e.get("signature") == signature]
    if prior and not args.allow_repeat:
        print(f"ERROR: exact experiment already began as {prior[-1].get('id')}; use --allow-repeat with a retest reason")
        return 1
    if args.allow_repeat and not args.retest_reason.strip():
        print("ERROR: --allow-repeat requires --retest-reason")
        return 2
    experiment_id = next_id(events)
    append(path, {
        "event": "begin",
        "id": experiment_id,
        "time": utc_now(),
        "question": args.question,
        "hypothesis": args.hypothesis,
        "change": args.change,
        "scenario": args.scenario,
        "bounds": args.bounds,
        "evidencePlan": args.evidence_plan,
        "keepCriterion": args.keep_criterion,
        "stopRule": args.stop_rule,
        "baseline": args.baseline,
        "rollback": args.rollback,
        "retestReason": args.retest_reason,
        "signature": signature,
    })
    print(experiment_id)
    return 0


def finish(args: argparse.Namespace) -> int:
    root = Path(args.project_root).expanduser().resolve()
    path = path_for(root)
    try:
        events = read_events(path)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1
    starts = [e for e in events if e.get("event") == "begin" and e.get("id") == args.id]
    if not starts:
        print(f"ERROR: unknown experiment id: {args.id}")
        return 1
    if any(e.get("event") == "finish" and e.get("id") == args.id for e in events):
        print(f"ERROR: experiment already finished: {args.id}")
        return 1
    append(path, {
        "event": "finish",
        "id": args.id,
        "time": utc_now(),
        "outcome": args.outcome,
        "evidence": args.evidence,
        "observations": args.observations,
        "keptOrReverted": args.kept_or_reverted,
        "interpretation": args.interpretation,
        "alternativeExplanation": args.alternative_explanation,
        "next": args.next,
    })
    print(args.id)
    return 0


def recent(args: argparse.Namespace) -> int:
    path = path_for(Path(args.project_root).expanduser().resolve())
    try:
        events = read_events(path)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1
    for event in events[-args.limit:]:
        print(json.dumps(event, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Append-only prototype experiment log.")
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("begin")
    start.add_argument("project_root")
    start.add_argument("--question", required=True)
    start.add_argument("--hypothesis", required=True)
    start.add_argument("--change", required=True)
    start.add_argument("--scenario", default="")
    start.add_argument("--bounds", default="")
    start.add_argument("--evidence-plan", required=True)
    start.add_argument("--keep-criterion", default="")
    start.add_argument("--stop-rule", default="")
    start.add_argument("--baseline", default="")
    start.add_argument("--rollback", default="")
    start.add_argument("--allow-repeat", action="store_true")
    start.add_argument("--retest-reason", default="")
    start.set_defaults(func=begin)

    end = sub.add_parser("finish")
    end.add_argument("project_root")
    end.add_argument("--id", required=True)
    end.add_argument("--outcome", required=True, choices=["PASS", "FAIL", "PARTIAL", "INVALID"])
    end.add_argument("--evidence", required=True)
    end.add_argument("--observations", default="")
    end.add_argument("--kept-or-reverted", required=True, choices=["KEPT", "REVERTED", "N/A"])
    end.add_argument("--interpretation", required=True)
    end.add_argument("--alternative-explanation", default="")
    end.add_argument("--next", default="")
    end.set_defaults(func=finish)

    show = sub.add_parser("recent")
    show.add_argument("project_root")
    show.add_argument("--limit", type=int, default=10)
    show.set_defaults(func=recent)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
