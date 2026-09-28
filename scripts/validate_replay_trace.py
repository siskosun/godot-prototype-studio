#!/usr/bin/env python3
"""Validate GPS replay-trace v1 records without claiming that a replay actually ran."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


class TraceError(ValueError):
    pass


def validate_trace(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TraceError("trace must be an object")
    if value.get("schemaVersion") != "1.0":
        raise TraceError("schemaVersion must equal 1.0")

    seed = value.get("seed")
    if not isinstance(seed, dict) or set(seed) != {"value", "mode"}:
        raise TraceError("seed must contain exactly value and mode")
    if seed["value"] is not None and (
        not isinstance(seed["value"], int) or isinstance(seed["value"], bool)
    ):
        raise TraceError("seed.value must be integer or null")
    if seed["mode"] not in {"SCENE_CONTROLLED", "GLOBAL_RNG_ONLY", "UNSET"}:
        raise TraceError("seed.mode is invalid")

    scenario = value.get("scenario")
    if not isinstance(scenario, str):
        raise TraceError("scenario must be a string")

    frame_policy = value.get("framePolicy")
    if not isinstance(frame_policy, dict):
        raise TraceError("framePolicy must be an object")
    if frame_policy.get("clock") != "physics_frame_offset":
        raise TraceError("framePolicy.clock must equal physics_frame_offset")
    if frame_policy.get("captureMode") != "INPUT_EVENT_ACTION":
        raise TraceError("framePolicy.captureMode must equal INPUT_EVENT_ACTION")

    actions = value.get("actions")
    if not isinstance(actions, list):
        raise TraceError("actions must be a list")
    if len(actions) > 10000:
        raise TraceError("actions exceeds 10000 entries")

    previous = 0
    for index, action in enumerate(actions):
        if not isinstance(action, dict):
            raise TraceError(f"actions[{index}] must be an object")
        if set(action) != {"frame", "action", "pressed", "strength"}:
            raise TraceError(f"actions[{index}] keys mismatch")
        frame = action["frame"]
        if not isinstance(frame, int) or isinstance(frame, bool) or frame < previous:
            raise TraceError(f"actions[{index}].frame must be a nondecreasing integer")
        name = action["action"]
        if not isinstance(name, str) or not name:
            raise TraceError(f"actions[{index}].action must be non-empty")
        if not isinstance(action["pressed"], bool):
            raise TraceError(f"actions[{index}].pressed must be boolean")
        strength = action["strength"]
        if (
            not isinstance(strength, (int, float))
            or isinstance(strength, bool)
            or not math.isfinite(float(strength))
            or float(strength) < 0.0
            or float(strength) > 1.0
        ):
            raise TraceError(f"actions[{index}].strength must be finite in [0,1]")
        previous = frame

    return {
        "valid": True,
        "schemaVersion": "1.0",
        "actionCount": len(actions),
        "lastFrame": previous if actions else 0,
        "claim": "schema-valid only; no replay execution is proven",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace")
    args = parser.parse_args()
    try:
        value = json.loads(Path(args.trace).read_text(encoding="utf-8"))
        result = validate_trace(value)
        code = 0
    except (OSError, json.JSONDecodeError, TraceError) as exc:
        result = {"valid": False, "error": str(exc)}
        code = 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
