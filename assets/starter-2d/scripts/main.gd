extends Node2D

@export_range(0.05, 2.0, 0.01) var movement_rate: float = 0.55

var model: PrototypeGameModel

func _ready() -> void:
    _ensure_default_inputs()
    model = PrototypeGameModel.new(1)
    model.domain_event.connect(_on_domain_event)
    queue_redraw()

func _physics_process(delta: float) -> void:
    var direction: float = Input.get_axis(&"move_left", &"move_right")
    if not is_zero_approx(direction):
        model.apply_action(&"move", direction * movement_rate * delta)
    if Input.is_action_just_pressed(&"restart"):
        model.reset(1)
    model.step(delta)
    queue_redraw()

func _draw() -> void:
    var viewport_size: Vector2 = get_viewport_rect().size
    var track_y: float = viewport_size.y * 0.58
    var left: float = viewport_size.x * 0.08
    var right: float = viewport_size.x * 0.92
    draw_line(Vector2(left, track_y), Vector2(right, track_y), Color(0.38, 0.45, 0.58), 8.0, true)

    var target_position := Vector2(viewport_size.x * PrototypeGameModel.TARGET_X, track_y)
    draw_circle(target_position, maxf(18.0, viewport_size.y * 0.045), Color(0.95, 0.72, 0.24))

    var player_position := Vector2(viewport_size.x * model.player_x, track_y)
    draw_circle(player_position, maxf(16.0, viewport_size.y * 0.04), Color(0.42, 0.77, 0.95))

    var title := "Instrumented Godot Prototype Starter"
    var instruction := "Move with A/D or arrow keys. Reach the gold target. Press R to restart."
    var status := "Target reached" if model.reached_target else "Moves: %d" % model.move_count
    draw_string(ThemeDB.fallback_font, Vector2(36, 56), title, HORIZONTAL_ALIGNMENT_LEFT, -1, 28)
    draw_string(ThemeDB.fallback_font, Vector2(36, 92), instruction, HORIZONTAL_ALIGNMENT_LEFT, -1, 18)
    draw_string(ThemeDB.fallback_font, Vector2(36, viewport_size.y - 34), status, HORIZONTAL_ALIGNMENT_LEFT, -1, 18)

func qa_snapshot() -> Dictionary:
    return {
        "scene": "main",
        "viewport": [get_viewport_rect().size.x, get_viewport_rect().size.y],
        "game": model.snapshot(),
    }

func qa_setup_scenario(scenario_name: StringName) -> bool:
    if scenario_name == &"start":
        model.reset(1)
        return true
    if scenario_name == &"near_target":
        model.reset(1)
        model.player_x = PrototypeGameModel.TARGET_X - PrototypeGameModel.TARGET_RADIUS * 1.5
        return true
    return false

func _on_domain_event(event_name: StringName, payload: Dictionary) -> void:
    var bridge := get_node_or_null("/root/QA")
    if bridge != null and bridge.has_method("record_event"):
        bridge.record_event(event_name, payload)

func _ensure_default_inputs() -> void:
    _ensure_key(&"move_left", KEY_A)
    _ensure_key(&"move_left", KEY_LEFT)
    _ensure_key(&"move_right", KEY_D)
    _ensure_key(&"move_right", KEY_RIGHT)
    _ensure_key(&"restart", KEY_R)

func _ensure_key(action: StringName, keycode: Key) -> void:
    if not InputMap.has_action(action):
        InputMap.add_action(action)
    for existing_event in InputMap.action_get_events(action):
        if existing_event is InputEventKey and existing_event.physical_keycode == keycode:
            return
    var event := InputEventKey.new()
    event.physical_keycode = keycode
    InputMap.action_add_event(action, event)
