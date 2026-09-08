extends Node

const MAX_EVENTS: int = 200

var _events: Array[Dictionary] = []

func record_event(event_name: StringName, payload: Dictionary) -> void:
    _events.append({
        "frame": Engine.get_process_frames(),
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
    }

func setup_scenario(scenario_name: StringName) -> bool:
    var current_scene := get_tree().current_scene
    if current_scene != null and current_scene.has_method("qa_setup_scenario"):
        return bool(current_scene.qa_setup_scenario(scenario_name))
    return false

func clear_events() -> void:
    _events.clear()

func print_snapshot() -> void:
    print(JSON.stringify(snapshot()))

func _mcp_state() -> Dictionary:
    return snapshot()
