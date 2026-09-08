# Ground scene claims in the engine

Use when a problem depends on scene ownership, transforms, UI, collisions, animation, resources, or runtime state. Inspect the smallest owning scene and expand only when needed; a repository-wide map is not a prerequisite to every edit.

**STATIC_PROJECT** describes declarations in project.godot, scenes, scripts and resources. **EDITOR_OBSERVED** requires an exercised editor/bridge path. **RUNTIME_OBSERVED** requires an actual run and observed state, events, input or captures. Static node paths do not establish live instance ownership, collisions, appearance or reachability.

`inspect_engine_context.py PROJECT --write` optionally inventories text declarations. It does not parse Godot's full resource language, resolve inherited scenes/UIDs, inspect binary resources, or operate an editor. It labels instanced nodes and unresolved declarations rather than silently guessing types. Use the real engine to resolve ambiguity; do not introduce an editor dependency for safe plain-text edits.

For a reported bug, connect the player's symptom to scene, rule owner, input path, transforms, camera/UI layer, signal and relevant resource. Capture a state/call path that could disprove the diagnosis. Query only observations supported by the available bridge; never invent MCP methods. Reuse recent validated context, but refresh after relevant edits or scene transitions.

The inspector writes `engine_static_context.json` by default, separate from prior manually collected runtime/editor observations. Do not overwrite or relabel those observations as fresh without re-exercising them.
