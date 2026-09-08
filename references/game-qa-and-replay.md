# Risk-driven QA, replay and automated playability

Use when runtime behavior matters. Scale to player impact, not file count. For a tiny game, a brief test list plus saved traces is enough; do not create a risk-register/matrix/charter stack by default.

## Choose tests that can expose failure

Connect brief criteria to state/transition, boundary input, scenario and expected outcome before running. Cover core input, distinct interaction, ordinary completion, failure/retry, interruption and stressful presentation. Include save, language, target export or accessibility cases only as applicable. Severity is observed player impact; do not invent numerical probabilities.

A check's oracle is what decides its outcome: actionable error, invariant, transition, reachability, terminal event, declared performance budget, actual presentation or human observation. Line coverage and clean exit codes do not prove a playable session. Distinguish PRODUCT_DEFECT, TEST_HARNESS, ENVIRONMENT, DESIGN_RISK and INCONCLUSIVE. Retain the first failure and the reproduction; a harness failure gives no game verdict.

## Two complementary execution paths

**Local rule checks:** construct a recorded state to examine a boundary/rare event cheaply, then run the normal action and assert consequences. State injection is legitimate setup, not a player trajectory. Tag it `LOCAL_STATE_TEST`.

**Normal-path checks:** start from clean launch and drive ordinary input through gameplay and result/recovery, without teleporting, writing a success flag or skipping transitions. Tag it `PLAYER_PATH`. At least one such path is required for each materially distinct promised session; local state tests do not replace it.

A normal path must exercise input routing. Calling the model's action method alone is a logic test. `Input.action_press` can affect polling but does not by itself prove GUI event routing; use real OS/device input or appropriate InputEvent dispatch and verify the downstream path. Synthetic runtime events establish only the layer actually exercised, not real-device ergonomics.

## Small replay corpus

Keep a shortest known completion path, failure/recovery, fixed major-bug traces and meaningful boundaries. Record case ID, build/compatible rule identity, seed/clock policy, initial state, input source, action timing, expected events and terminal condition. Use the existing harness or a project-specific minimal adapter; the skill does not pretend one replay protocol fits every Godot project.

If preconditions changed, mark the replay STALE and decide whether its expectation legitimately changes. A fixed-seed trace passing on its source build is not evidence across engines/devices or altered physics. Preserve seed/input/time where determinism is possible and tolerances where it is not.

Before trusting a harness, include a known-success case and an intentionally invalid case in disposable fixtures. Confirm it fails when its oracle is violated. Do not introduce the defect into user production files. Keep evaluation fixtures/logs separate from implementation, and do not rewrite an oracle merely to improve a score.

## Exploratory probes

Choose the highest unresolved risk, not a persona quota. Useful policies include rapid/contradictory input, hesitant first actions, resource optimization, boundary exploration, idle/focus interruption, or reduced-input accessibility paths. These are algorithms and constraints, not simulated evidence from novice/disabled humans.

Perturb a known replay's timing, order, viewport or resource boundary. Bound the run; detect no progress with a contextual threshold, not a universal timeout. Preserve a minimal failing trace and actual frequency across distinct trials. For choice-use claims, record opportunities. Deduplicate repeated failures rather than counting the same exploit many times.

Investigate a flake with a controlled rerun and stronger observation. Do not keep rerunning until green. An unresolved flaky **required** path remains blocking; quarantine is a tracking action, not permission to ship it. Optional unrelated flakes can be disclosed without expanding scope.

## Final pass

Use affected regressions during development. At freeze, test the clean deliverable's complete normal route, deliberate failure/retry and required target conditions; inspect output at actual play size and in motion. Optional real humans add experience evidence, not a routine waiting stage. See implementation testing, quality bar and release evidence.

Research basis: interaction-grounded game-generation studies support actual play; runtime-state injection complements reachability. Their benchmark performance does not establish this skill's end-to-end success or subjective fun (S14-S19).
