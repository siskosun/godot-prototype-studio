# Experience validation loop

Use when work changes what the player should perceive, decide, feel or want to do across a mechanic, encounter, session or larger system. Do not load it for a narrow bug whose player-facing intent is already settled.

## Keep a lightweight experience spine

For repeated or multi-system work, retain only the identity needed to prevent local optimization from drifting the game:

- **Player promise:** the experience the build is trying to deliver.
- **Core tension / core verb:** the recurring decision pressure and primary player action when they are useful descriptions of this game.
- **Loop stack:** only the layers that actually exist, such as moment-to-moment -> encounter/session -> progression -> meta.
- **Design pillars:** a small set of retained principles that resolve real tradeoffs.
- **Explicit non-goals:** tempting additions that would weaken scope or identity.

The mission brief remains the acceptance contract. The spine is project memory, not a second GDD. Do not invent progression, economy, meta, combat, fail states or replay loops merely to fill a framework.

Before a design-touching addition, ask what existing player decision or loop it strengthens, what tension it changes, and what it costs. A locally attractive feature should be revised or removed when it erases a retained tension, trivializes a downstream decision, or adds maintenance/content work without changing the intended experience.

## Move claims through an evidence ladder

Treat experience design as hypotheses with different evidence requirements:

1. **Design hypothesis:** why a mechanic/system should create the intended decision or feeling.
2. **Observable behavior:** what the player should notice, attempt, avoid, reconsider or repeat if the hypothesis is working.
3. **Runtime behavior:** whether the implementation actually creates the opportunities, constraints, outcomes and feedback required by the hypothesis.
4. **Human experience:** what real participants did, said and reported under the named build and conditions.

Lower layers cannot prove higher ones. Correct runtime logic does not prove delight, tension, fairness, accessibility or voluntary replay. A model critique or bot policy is not human evidence.

## Check the loop stack only where it exists

For multi-system prototypes, trace value and decisions across the relevant layers. Check whether:

- rewards or losses from one layer change a later decision rather than only increase a number;
- progression preserves or intentionally transforms the core tension instead of deleting it;
- economy/inventory/loadout choices create opportunity cost rather than obvious accumulation;
- onboarding exposes the actual core loop rather than delaying it behind explanation;
- session closure leaves the intended result, learning, comparison, creation or progression state;
- meta systems support replay when replay is part of the promise, rather than hiding a weak core behind retention mechanics.

Do not require every layer. A finite puzzle, toy, narrative slice, pure competition or short arcade loop can be complete without persistent progression or meta.

## Iterate on the smallest causal variable

When the experience misses its target, name the largest observed gap: unclear objective, inert choice, dominant tactic, pacing stall, unearned failure, unreadable feedback, repetitive opportunity, weak reward consequence, or control mismatch. State one causal hypothesis and change the smallest variable or inseparable bundle likely to affect it. Re-run the same relevant scenario before broadening content.

Keep opportunity counts separate from choice counts. A player cannot reject an option they never saw, could not afford, or could not understand. Preserve failed hypotheses and the conditions under which they failed so future work does not rediscover them as facts.

For unsettled mechanics, use [novel gameplay](novel-gameplay.md). For implementation truth, use [runtime logic verification](runtime-logic-verification.md). For micro-level response and feedback, use [gameplay and UX](gameplay-and-ux.md).

## Human playtests answer the subjective boundary

Before a playtest, define a few specific questions whose answers could change a design decision. Record the exact build, participant familiarity, task, observation window and intervention rule. There is no universal minimum participant count: one or a few players can expose a concrete failure, while prevalence, segmentation or market claims need a study sized for those claims.

During play, prioritize unassisted behavior:

- first meaningful action and time/attempts to it when relevant;
- hesitation and ignored affordances;
- expectation mismatch between action and outcome;
- strategy change after feedback or failure;
- recovery understanding and retry friction;
- voluntary continuation, exploration or abandonment within the agreed session.

Record **observation**, **participant statement**, **runtime fact**, and **interpretation** separately. Do not infer a participant's internal emotion or intent from facial expression or posture as fact. If a facilitator intervenes, mark subsequent evidence that depends on the intervention.

After play, ask neutral questions tied to decisions, for example: what were you trying to do, what did you expect that action to do, when did you change your plan and why, what would you try next? A direct "did you like it?" answer can be recorded, but it should not replace behavioral evidence or a more specific experience question.

A small playtest is diagnostic. It can falsify or revise a design hypothesis; it does not establish audience-wide preference, retention or market demand.

## Stop when the uncertainty that matters is resolved

Do not keep adding variants, frameworks or testers after the evidence is sufficient for the current decision. Preserve remaining subjective uncertainty explicitly and continue with the best supported baseline. If the user has not contracted human testing, finish all machine-verifiable work rather than blocking delivery on an unavailable participant.
