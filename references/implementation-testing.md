# Evidence that challenges the result

Use the cheapest adequate check for the affected claim, not a full suite after every edit. Classify the change first: rules → rule/replay regression; fonts/UI/canvas → display regression; docs/ZIP wrappers → package contents; harness-only → rerun the harness. Reused evidence must show the relevant `gameContent`, `testHarness`, or `package` hash is unchanged. Final delivery still needs the evidence required by the brief. Keep acceptance stable; do not change tests or screenshots solely to make a failed result appear successful. See [change impact](change-impact.md).

## Evidence levels

| Level | Establishes | Does not establish |
|---|---|---|
| STATIC | Files, parse/import, resource references | Gameplay |
| LOGIC | Tested rules and invariants | Device input or rendering |
| HEADLESS_RUNTIME | Exercised engine scene path | Presentation or feel |
| INTERACTION | Actual input causes expected state/outcome | Human enjoyment |
| PRESENTATION | Observed runtime frames/motion/audio | Unobserved sessions/platforms |
| HUMAN_EXPERIENCE | Stated participant's observations | Market demand |

For a presentable new prototype, final evidence normally includes successful import/runtime, actual input through the principal loop and retry, and inspected presentation. An experiment or isolated fix needs only affected evidence plus relevant regression. Headless and logic checks never replace required visual/interaction evidence.

Use existing tests, a small GDScript runner, or a proven runtime bridge. `scripts/run_godot_checks.py PROJECT --mode import|test|smoke|all` is a convenience for engine checks, not a complete playtest. Inspect both exit status and actionable log errors. The runner returns 0 for PASS, 1 for failed checks, 2 for unavailable/invalid execution, and 3 for PARTIAL with skipped checks. A missing optional unit-test file does not require inventing a suite; choose applicable checks and record coverage.

## Real interaction

Drive normal InputMap/OS/touch events through the game, not privileged calls that jump to the expected outcome. Setup hooks may construct a scenario but cannot stand in for player actions. Record input source, scenario/seed, observation, and resulting state. Inspect representative states: first action, differentiating choice, success or session completion, failure, retry, and stressful layout. Sandbox loops need creation/use/reset rather than arbitrary victory.

## Separate construction from final review

When a separate agent/evaluator is available and justified, give it the brief, immutable artifact, run path, and clean fixtures. Let it report failures against requirements without editing the implementation or silently lowering the bar. Preserve that report; return to implementation to repair, then rerun affected checks and final artifact review. Do not require installing GameForge for every task.

If only one agent is available, perform a distinct fresh-start final check against the frozen artifact and label it self-review. Do not claim solver-invisible, external, blind, or independent verification. If independent evaluation is a contractual requirement, this fallback cannot satisfy it.

Categorize failures: implementation, import/build, runtime behavior, input/presentation, host/tooling, evaluator, or unknown. An evaluator failure is not evidence that the game passed or failed gameplay. Keep raw evidence to support the classification.

A JSON validator checks consistency and hashes, not the truth of logs or fun. Protect evaluation evidence from casual rewrites; distinguish trusted external tests from agent-authored tests. No skill-level protocol alone makes hostile code safe.
