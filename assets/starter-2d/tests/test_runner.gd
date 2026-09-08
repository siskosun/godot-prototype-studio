extends SceneTree

var _failures: int = 0

func _init() -> void:
    call_deferred("_run")

func _run() -> void:
    var model_script: Script = load("res://scripts/game_model.gd")
    _check(model_script != null, "game model script loads")
    if model_script == null:
        quit(1)
        return

    var model = model_script.new(7)
    _check(is_equal_approx(model.player_x, 0.18), "reset starts at expected position")
    _check(model.seed == 7, "seed is retained")

    model.apply_action(&"move", 0.1)
    _check(model.player_x > 0.18, "move action changes authoritative state")
    _check(model.move_count == 1, "move count increments")

    model.player_x = PrototypeGameModel.TARGET_X
    model.step(0.016)
    _check(model.reached_target, "target condition terminates the loop")

    var snapshot: Dictionary = model.snapshot()
    _check(snapshot.get("reached_target") == true, "snapshot exposes terminal state")
    _check(snapshot.get("seed") == 7, "snapshot exposes reproducibility seed")

    if _failures == 0:
        print("TESTS PASS")
        quit(0)
    else:
        push_error("TESTS FAILED: %d" % _failures)
        quit(1)

func _check(condition: bool, label: String) -> void:
    if condition:
        print("PASS: %s" % label)
    else:
        _failures += 1
        push_error("FAIL: %s" % label)
