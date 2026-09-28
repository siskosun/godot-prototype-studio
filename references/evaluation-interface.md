# Evaluation interface and replay evidence

Use this guide when a prototype must be compared under a fixed evaluation contract or when agent-discovered failures should be turned into reproducible evidence.

The goal is not to build a universal remote controller. Prefer an existing project QA hook. The bundled starter exposes a small optional interface through `QA`.

## Separate exploration from replay

Two kinds of run have different evidence meaning:

- **Exploratory run**: an agent, human, script or policy searches for useful behavior. It may be stochastic. Its observations are diagnostic and participant-reported unless independently replayed.
- **Replay run**: a declared input trace is executed against an identified build under a declared seed/scenario/frame policy. A trusted environment may use this to produce trusted observed evidence.

Never call an exploratory rerun "reproducible" merely because it used the same prompt.

## Starter evaluation interface

`assets/starter-2d/qa/qa_bridge.gd` provides:

- `setup_scenario(name)`
- `configure_seed(value)`
- `start_input_recording()`
- `stop_input_recording()`
- `inject_action(action, pressed, strength)`
- `step_frames(n)`
- `snapshot()`
- `replay_trace(trace)`
- `print_trace()`

The interface records named `InputEventAction` events with physics-frame offsets.

### Seed modes

`SCENE_CONTROLLED` means the current scene implements `qa_set_seed(seed)` and owns the relevant RNGs.

`GLOBAL_RNG_ONLY` means only Godot's global random seed was set. This does not prove project-specific `RandomNumberGenerator` instances, physics or external systems are deterministic.

`UNSET` means no seed contract was established.

### Frame-step modes

`SCENE_CONTROLLED` means the current scene implements `qa_step_frames(n)` and is responsible for deterministic stepping semantics.

`REALTIME_PHYSICS_WAIT` only waits for natural Godot physics frames. It is useful for replay timing but is **not** deterministic manual stepping. Evidence must retain this mode instead of upgrading it to stronger determinism.

A project that needs strict step control should implement `qa_step_frames` in its own test harness. GPS does not pretend the stock SceneTree exposes a universal deterministic manual-step API.

## Replay Trace v1

Use `templates/replay_trace.json` as the portable record. The schema contains:

- explicit schema version;
- seed value and seed-control mode;
- scenario name;
- physics-frame-offset timing policy;
- named input actions with press/release and strength.

Validate the record with:

```bash
python scripts/validate_replay_trace.py path/to/replay_trace.json
```

Schema validation proves only record consistency. It does not prove the game executed the trace.

## Evidence classes

Keep these classes distinct when handing evidence to an external control plane such as game-exp:

### TRUSTED_OBSERVED

A trusted clean workflow starts from an identified build, runs a declared replay or check in a fresh environment, observes the result itself, and binds the evidence to the build/profile/trace identities.

### PARTICIPANT_REPORTED

An agent/player/VLM reports what it saw, tried or inferred. This is valuable for finding risks and producing candidate traces, but cannot by itself prove a required criterion passed or failed.

A concrete agent-found failure should preferably be reduced to a trace and independently replayed. If the trusted replay reproduces the defect, the runtime fact can be upgraded to trusted observed evidence.

### HUMAN_REPORTED

A real participant's behavior, statement or preference tied to an exact build and test conditions. Keep observed behavior, participant statement, runtime fact and interpretation separate.

## Three-way screening

When evidence is later used for screening, preserve three outcomes:

- `PASS`: required trusted observations passed.
- `FAIL_PRODUCT_DEFECT`: a required product condition failed under trusted observation.
- `INCONCLUSIVE`: harness/environment/tooling failure, unavailable evidence, unresolved flake, or an exploratory agent failing to discover a path.

An agent failing to find a route is not automatically a product defect. If a trusted replay proves the route is reachable, the failure may be a discoverability design risk instead.

## Comparable variants

For 2-4 internal variants, continue using `prototype_comparison.json` and `compare_prototypes.py`.

Keep scenario, conditions and invariants comparable. `MACHINE_DOMINATED` applies only to complete declared finite metrics. It is not a fun judgment and does not authorize an external experiment lifecycle decision.

Do not add Elo for a small complete pairwise set. Record dimension-level outcomes, order effects and human observations instead.
