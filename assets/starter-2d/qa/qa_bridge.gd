extends Node

const MAX_EVENTS: int = 200
const MAX_TRACE_ACTIONS: int = 10000
const TRACE_SCHEMA_VERSION: String = "1.0"

var _events: Array[Dictionary] = []
var _recording: bool = false
var _trace_start_physics_frame: int = 0
var _trace_actions: Array[Dictionary] = []
var _seed_record: Dictionary = {"value": null, "mode": "UNSET"}
var _scenario_name: String = ""

func record_event(event_name: StringName, payload: Dictionary) -> void:
    _events.append({
        "frame": Engine.get_process_frames(),
        "physics_frame": Engine.get_physics_frames(),
        "name": String(event_name),
        "payload": payload.duplicate(true),
    })
    if _events.size() > MAX_EVENTS:
        _events.pop_front()

func snapshot() -> Dictionary:
    var current_scene := get_tree().current_scene
    var scene_state: Dictionary = {}
    if current_scene != null and current_scene.has_method("qa_snapshot"):
        scene_state = current_scene.qa_snapshot()
    return {
        "scene_state": scene_state,
        "recent_events": _events.duplicate(true),
        "evaluation_interface": {
            "trace_schema_version": TRACE_SCHEMA_VERSION,
            "recording": _recording,
            "seed": _seed_record.duplicate(true),
            "scenario": _scenario_name,
        },
    }

func setup_scenario(scenario_name: StringName) -> bool:
    var current_scene := get_tree().current_scene
    if current_scene != null and current_scene.has_method("qa_setup_scenario"):
        var ok := bool(current_scene.qa_setup_scenario(scenario_name))
        if ok:
            _scenario_name = String(scenario_name)
            record_event("qa_scenario_setup", {"scenario": _scenario_name})
        return ok
    return false

func configure_seed(seed_value: int) -> Dictionary:
    var current_scene := get_tree().current_scene
    var mode := "GLOBAL_RNG_ONLY"
    if current_scene != null and current_scene.has_method("qa_set_seed"):
        current_scene.qa_set_seed(seed_value)
        mode = "SCENE_CONTROLLED"
    else:
        seed(seed_value)
    _seed_record = {"value": seed_value, "mode": mode}
    record_event("qa_seed_configured", _seed_record)
    return _seed_record.duplicate(true)

func start_input_recording(clear_existing: bool = true) -> Dictionary:
    if clear_existing:
        _trace_actions.clear()
    _trace_start_physics_frame = Engine.get_physics_frames()
    _recording = true
    record_event("qa_input_recording_started", {
        "start_physics_frame": _trace_start_physics_frame,
    })
    return {
        "recording": true,
        "start_physics_frame": _trace_start_physics_frame,
    }

func stop_input_recording() -> Dictionary:
    _recording = false
    record_event("qa_input_recording_stopped", {
        "action_count": _trace_actions.size(),
    })
    return replay_trace_record()

func replay_trace_record() -> Dictionary:
    return {
        "schemaVersion": TRACE_SCHEMA_VERSION,
        "seed": _seed_record.duplicate(true),
        "scenario": _scenario_name,
        "framePolicy": {
            "clock": "physics_frame_offset",
            "captureMode": "INPUT_EVENT_ACTION",
        },
        "actions": _trace_actions.duplicate(true),
    }

func inject_action(action: StringName, pressed: bool, strength: float = 1.0) -> bool:
    if not InputMap.has_action(action):
        record_event("qa_input_injection_rejected", {"action": String(action)})
        return false
    var event := InputEventAction.new()
    event.action = action
    event.pressed = pressed
    event.strength = clampf(strength, 0.0, 1.0)
    Input.parse_input_event(event)
    return true

func step_frames(frame_count: int) -> Dictionary:
    if frame_count < 0:
        return {"status": "FAIL", "mode": "INVALID", "frames": frame_count}
    var current_scene := get_tree().current_scene
    if current_scene != null and current_scene.has_method("qa_step_frames"):
        var result = await current_scene.qa_step_frames(frame_count)
        return {
            "status": "PASS",
            "mode": "SCENE_CONTROLLED",
            "frames": frame_count,
            "scene_result": result,
        }
    for _index in range(frame_count):
        await get_tree().physics_frame
    return {
        "status": "PASS",
        "mode": "REALTIME_PHYSICS_WAIT",
        "frames": frame_count,
        "warning": "This waits natural physics frames; it is not deterministic manual stepping.",
    }

func replay_trace(trace: Dictionary) -> Dictionary:
    var validation := _validate_trace(trace)
    if validation.get("status") != "PASS":
        return validation

    var seed_entry = trace.get("seed", {})
    if seed_entry is Dictionary and seed_entry.get("value") is int:
        configure_seed(int(seed_entry["value"]))

    var scenario := String(trace.get("scenario", ""))
    if not scenario.is_empty():
        if not setup_scenario(scenario):
            return {
                "status": "FAIL",
                "classification": "TEST_HARNESS",
                "reason": "scenario setup unavailable",
                "scenario": scenario,
            }

    var prior_recording := _recording
    _recording = false
    var previous_frame := 0
    var step_modes: Array[String] = []

    for action_entry in trace.get("actions", []):
        var target_frame := int(action_entry["frame"])
        var delta := target_frame - previous_frame
        var step_result := await step_frames(delta)
        if step_result.get("status") != "PASS":
            _recording = prior_recording
            return step_result
        step_modes.append(String(step_result.get("mode", "UNKNOWN")))
        if not inject_action(
            StringName(action_entry["action"]),
            bool(action_entry["pressed"]),
            float(action_entry.get("strength", 1.0))
        ):
            _recording = prior_recording
            return {
                "status": "FAIL",
                "classification": "TEST_HARNESS",
                "reason": "trace references unknown action",
                "action": action_entry["action"],
            }
        previous_frame = target_frame

    _recording = prior_recording
    return {
        "status": "PASS",
        "replayMode": (
            "SCENE_CONTROLLED"
            if not step_modes.is_empty() and step_modes.all(func(mode): return mode == "SCENE_CONTROLLED")
            else "REALTIME_PHYSICS_WAIT"
        ),
        "actionCount": trace.get("actions", []).size(),
        "finalSnapshot": snapshot(),
    }

func clear_events() -> void:
    _events.clear()

func print_snapshot() -> void:
    print(JSON.stringify(snapshot()))

func print_trace() -> void:
    print(JSON.stringify(replay_trace_record()))

func _input(event: InputEvent) -> void:
    if not _recording:
        return
    if event is not InputEventAction:
        return
    if _trace_actions.size() >= MAX_TRACE_ACTIONS:
        _recording = false
        record_event("qa_input_recording_limit_reached", {
            "max_actions": MAX_TRACE_ACTIONS,
        })
        return
    var action_event := event as InputEventAction
    _trace_actions.append({
        "frame": maxi(0, Engine.get_physics_frames() - _trace_start_physics_frame),
        "action": String(action_event.action),
        "pressed": action_event.pressed,
        "strength": action_event.strength,
    })

func _validate_trace(trace: Dictionary) -> Dictionary:
    if String(trace.get("schemaVersion", "")) != TRACE_SCHEMA_VERSION:
        return {
            "status": "FAIL",
            "classification": "TEST_HARNESS",
            "reason": "unsupported replay trace schema",
        }
    var actions = trace.get("actions")
    if actions is not Array:
        return {
            "status": "FAIL",
            "classification": "TEST_HARNESS",
            "reason": "trace actions must be an array",
        }
    var previous_frame := 0
    for entry in actions:
        if entry is not Dictionary:
            return {
                "status": "FAIL",
                "classification": "TEST_HARNESS",
                "reason": "trace action must be an object",
            }
        var frame = entry.get("frame")
        var action = entry.get("action")
        if frame is not int or int(frame) < previous_frame:
            return {
                "status": "FAIL",
                "classification": "TEST_HARNESS",
                "reason": "trace frames must be nondecreasing integers",
            }
        if action is not String or String(action).is_empty():
            return {
                "status": "FAIL",
                "classification": "TEST_HARNESS",
                "reason": "trace action name is required",
            }
        if entry.get("pressed") is not bool:
            return {
                "status": "FAIL",
                "classification": "TEST_HARNESS",
                "reason": "trace pressed must be boolean",
            }
        previous_frame = int(frame)
    return {"status": "PASS"}

func _mcp_state() -> Dictionary:
    return snapshot()
