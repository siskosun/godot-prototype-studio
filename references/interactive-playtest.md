# Capability-probed interactive playtesting

OhMyGame's Web `game_use` illustrates a small set of operations: **open**, **act**, **inspect**, **capture**, **close**, and optional **reset/seed/step**. This document is a capability contract, not an installed native Godot controller.

Probe the actual available Godot CLI, evaluation interface, engine adapter or permitted Web browser before using an operation. Record execution environment, exact build identity, input source (physical input, engine InputEvent or direct state injection), step or seed provenance, output evidence, failure class and session cleanup. A script that compiles but never drives player input has not completed an interactive playtest.

Classify verified normal-input trajectories as PLAYER_PATH; injected setup is SETUP_ONLY or LOCAL_STATE_TEST. Input.action_press alone does not prove Node._input or device ergonomics. Screenshots must come from the running target at the asserted scene/viewport. A test bridge may provide diagnostics but must not ship as an unrestricted release control interface.

If the host cannot launch/control the game or local browsing is blocked, mark that layer UNVERIFIED or ENVIRONMENT, not PASS or PRODUCT_DEFECT. Use existing replay, runtime checks and a real human playtest where required; do not silently install a controller or assume Godot support from a Web-only tool.