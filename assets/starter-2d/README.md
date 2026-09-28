# Thin instrumented Godot 4.3+ 2D starter

This is not a finished game template. It provides a minimal launchable structure for a blank prototype:

- one authoritative `RefCounted` game model;
- a simple `Node2D` presentation and InputMap actions;
- a debug-only QA autoload that exposes compact state and domain events and records mapped keyboard/gamepad/input-action events with their source class;
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

The starter targets Godot 4.3+ GDScript. QA mutation/injection methods are inert in non-debug exports unless the custom `qa` feature is explicitly enabled. Verify the project with its actual Godot version before claiming success.
