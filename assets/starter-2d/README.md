# Thin instrumented Godot 4.x 2D starter

This is not a finished game template. It provides a minimal launchable structure for a blank prototype:

- one authoritative `RefCounted` game model;
- a simple `Node2D` presentation and InputMap actions;
- a QA autoload that exposes compact state and domain events;
- deterministic scenario setup;
- a dependency-free headless GDScript test runner;
- compatibility renderer defaults.

Use only for a new blank project. Replace the sample movement loop with the real prototype while preserving one authoritative rule implementation and the observation seam when useful.

Suggested checks:

```bash
godot --headless --path . --import --quit
godot --headless --path . --script res://tests/test_runner.gd
godot --headless --path . --quit-after 120
```

The starter targets Godot 4.x GDScript. Verify it with the actual project Godot version before claiming success.
