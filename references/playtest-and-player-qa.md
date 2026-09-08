# Player-facing QA and optional human playtests

Use gameplay-and-ux.md for design iteration and game-qa-and-replay.md for reproducible tests.

## Agent-executable QA

On the actual build, try the experience from launch rather than a privileged internal state. Check that the player can identify the goal, perform the first action, see consequences, reach the distinguishing mechanic, understand failure, and retry without a softlock. Inspect appropriate viewport sizes, input methods, feedback timing, dense scenes, audio triggers, and persistence when required.

Do not treat 'all controls wired' as complete communication. Look for unclear targets, offscreen objectives, inconsistent art, unreadable text, missing pressed/disabled states, stale HUD, accidental double input, transitions that lose focus, or effects that conceal hazards. Correct defects within the brief without asking for aesthetic approval already delegated.

## Human evidence

Use a human playtest when available or contracted. Provide the exact build, plain controls, a short task, and focused questions about observable confusion or decisions rather than only 'is it fun?'. Separate observed behavior, participant statements, runtime facts, and agent interpretation. Label sample and build; do not generalize one person's opinion to the audience.

Optional `playtest_plan.md`, `playtest_report.json`, and the validator support a real test. Do not invent a participant or populate subjective ratings from the agent's imagination. If no participant is available and human testing is not required for delivery, finish the agent-verifiable work and disclose this gap without stopping for approval.

Use one clear next action and recovery path when a novice actually must act. Do not delegate routine debugging or document maintenance to them.
