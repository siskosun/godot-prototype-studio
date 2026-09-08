class_name PrototypeGameModel
extends RefCounted

signal domain_event(event_name: StringName, payload: Dictionary)

const MIN_X: float = 0.08
const MAX_X: float = 0.92
const TARGET_X: float = 0.82
const TARGET_RADIUS: float = 0.045

var player_x: float = 0.18
var elapsed_seconds: float = 0.0
var move_count: int = 0
var reached_target: bool = false
var seed: int = 1

func _init(seed_value: int = 1) -> void:
    reset(seed_value)

func reset(seed_value: int = 1) -> void:
    seed = seed_value
    player_x = 0.18
    elapsed_seconds = 0.0
    move_count = 0
    reached_target = false
    domain_event.emit(&"run_reset", {"seed": seed})

func apply_action(action: StringName, value: float = 1.0) -> void:
    if reached_target:
        return
    if action == &"move":
        var previous_x: float = player_x
        player_x = clampf(player_x + value, MIN_X, MAX_X)
        if not is_equal_approx(previous_x, player_x):
            move_count += 1
            domain_event.emit(&"player_moved", {"x": player_x, "moves": move_count})

func step(delta: float) -> void:
    if delta <= 0.0 or reached_target:
        return
    elapsed_seconds += delta
    if absf(player_x - TARGET_X) <= TARGET_RADIUS:
        reached_target = true
        domain_event.emit(&"target_reached", {"elapsed": elapsed_seconds, "moves": move_count})

func snapshot() -> Dictionary:
    return {
        "player_x": player_x,
        "target_x": TARGET_X,
        "target_radius": TARGET_RADIUS,
        "elapsed_seconds": elapsed_seconds,
        "move_count": move_count,
        "reached_target": reached_target,
        "seed": seed,
    }
