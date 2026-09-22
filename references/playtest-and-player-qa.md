# Player-facing QA and optional human playtests

Use [gameplay and UX](gameplay-and-ux.md) for design iteration, [game QA and replay](game-qa-and-replay.md) for reproducible machine checks, and [experience validation](experience-validation-loop.md) when the decision depends on subjective player experience.

## Agent-executable QA

On the actual build, try the experience from launch rather than a privileged internal state. Check that the player can identify the goal, perform the first action, see consequences, reach the distinguishing mechanic, understand failure, and retry without a softlock. Inspect appropriate viewport sizes, input methods, feedback timing, dense scenes, audio triggers, and persistence when required.

Do not treat "all controls wired" as complete communication. Look for unclear targets, offscreen objectives, inconsistent art, unreadable text, missing pressed/disabled states, stale HUD, accidental double input, transitions that lose focus, or effects that conceal hazards. Correct defects within the brief without asking for aesthetic approval already delegated.

Bot/agent probes can test reachability, robustness, dominant policies and regressions. They are diagnostic algorithms, not novice, expert or target-player participants.

## Design a human playtest around a decision

Use a human playtest when available, contracted, or when a subjective experience claim materially affects the next investment. Before the session, define a few questions that are observable, actionable and answerable in the planned play window. Record the exact build, participant profile/familiarity, task, stop condition, intervention rule and any recording/data consent.

There is no universal minimum tester count. One or a few people can expose a concrete confusion or broken expectation; estimating how common a reaction is across an audience requires a study designed for that claim. Do not convert a convenient sample into a prevalence or market conclusion.

During the session, prefer unassisted evidence: first meaningful action, hesitation, ignored affordance, repeated failed input, expectation mismatch, strategy change, failure/recovery understanding and voluntary continuation or stopping. If the facilitator helps, record the intervention and do not treat dependent behavior as cold-start evidence.

Keep four evidence types separate:

- **Observed behavior:** what the participant actually did.
- **Participant statement:** what they said or reported.
- **Runtime fact:** game state, input, timing, error or event data.
- **Interpretation:** the designer/agent's explanation of why it happened.

Do not infer an internal emotion, intent or diagnosis from facial expression, posture or input force as fact. These may motivate a neutral follow-up question but are not self-validating evidence.

After play, ask neutral questions tied to the tested decision: what were you trying to do, what did you expect an action to do, what caused the last success/failure, when did you change your plan, and what would you try next? Avoid leading questions that reveal the intended answer. A generic "did you like it?" can be recorded but should not be the primary oracle.

Optional `playtest_plan.md`, `playtest_report.json`, and the validator support a real test. Do not invent participants or subjective ratings. If no participant is available and human testing is not required for delivery, finish the agent-verifiable work and disclose the remaining experience hypothesis without stopping for approval.

## Turn findings into the next experiment

Prioritize findings by player impact and decision relevance, not by a fixed vote threshold. Preserve the observation that supports each material finding, plausible alternative explanations, and the smallest change expected to alter the behavior. Re-run comparable conditions after the change when the decision matters.

A small playtest can falsify a design hypothesis. It does not by itself prove audience-wide fun, retention, accessibility, monetization or market demand.
