# Godot 4.3+ practical guide

Use this as the concrete implementation reference for ordinary Godot work. Confirm the project's actual engine version before relying on newer APIs.

## Input and focus

Define gameplay actions in InputMap and read named actions instead of hard-coding keys.

```gdscript
func _physics_process(delta: float) -> void:
    var axis := Input.get_axis("move_left", "move_right")
    velocity.x = axis * speed
    move_and_slide()
```

For `Control` nodes, `mouse_filter` can silently consume or pass pointer input. Check it when clicks reach a parent but not the intended control, or gameplay input stops under UI.

Use `_unhandled_input` when gameplay should receive input only after UI had a chance to handle it. Use `_input` for instrumentation that must observe raw events.

## Tile maps

For Godot 4.3+, prefer `TileMapLayer` for new work rather than expanding legacy `TileMap` usage. When opening an older project, preserve its existing structure unless migration solves a real problem.

## Scene references

Use `@onready` for nodes that exist after the scene enters the tree:

```gdscript
@onready var score_label: Label = %ScoreLabel

func _ready() -> void:
    score_label.text = "0"
```

If a node may be absent in some variant, do not force a typed reference that crashes every variant; resolve it deliberately and validate the expected scene contract.

## Tween lifecycle

Create a new Tween for each animation sequence. Do not keep and restart an already-finished Tween.

```gdscript
func pulse(node: CanvasItem) -> void:
    var tween := create_tween()
    tween.tween_property(node, "scale", Vector2(1.08, 1.08), 0.08)
    tween.tween_property(node, "scale", Vector2.ONE, 0.10)
```

Kill or replace a still-running Tween when overlapping animation would produce invalid state.

## Headless test template

Keep important game rules outside rendering so they can be tested without a window.

```gdscript
extends SceneTree

func _init() -> void:
    var model = preload("res://scripts/game_model.gd").new()
    model.reset()
    assert(model.score == 0)
    model.apply_action("gain")
    assert(model.score == 1)
    print("TESTS_PASSED")
    quit(0)
```

Run:

```bash
godot --headless --path . --import --quit
godot --headless --path . --script res://tests/test_runner.gd
godot --headless --path . --quit-after 120
```

A headless pass proves only what those assertions/runtime paths cover.

## Minimal Web export

Keep one explicit runnable Web preset. For broad compatibility start with the compatibility renderer and no threads unless the project needs them.

Typical minimum:

```text
[preset.0]
name="Web"
platform="Web"
runnable=true

[preset.0.options]
variant/thread_support=false
html/canvas_resize_policy=1
```

Serve the generated export over HTTP for browser validation; do not treat opening `index.html` from disk as an equivalent player path.

## QA bridge safety

Instrumentation may expose state, scenario setup, replay, or injected input in debug builds. Ordinary release builds should not expose mutation/control hooks.

A safe guard is:

```gdscript
func qa_enabled() -> bool:
    return OS.is_debug_build() or OS.has_feature("qa")
```

The bundled starter uses this pattern.

## Common failures

| Symptom | First checks |
|---|---|
| Key works in editor but trace is empty | Recorder may accept only `InputEventAction`; match InputMap actions from Key/Joypad events |
| Button blocks movement input | Inspect `Control.mouse_filter`, focus, and whether gameplay uses `_unhandled_input` |
| Tween plays once | Create a new Tween per sequence; do not reuse a finished Tween |
| Headless import passes but game crashes | Run the project smoke path; import success is not runtime success |
| Browser shows tiny/clipped canvas | Check export resize policy, CSS size, viewport size, DPR, and backing-pixel budget |
| Chinese Windows script crashes decoding Godot output | Decode subprocess output as UTF-8 with replacement/error handling |
| New TileMap code conflicts with current docs | Check engine version; Godot 4.3+ new work should consider `TileMapLayer` |
| QA functions are reachable in release | Gate QA mutation/injection with debug/custom export features |
