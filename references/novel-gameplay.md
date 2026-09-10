# Novel gameplay discovery and proof

Use when the user asks for an original/new mechanic, when the differentiating interaction is unsettled, or when an implementation merely reskins an existing loop. The goal is not to certify historical originality. It is to produce a playable design delta that changes what the player perceives, decides, does, or can do next.

## Start from an experience, not a feature list

Write one mechanic thesis in player terms:

> The player reads **[information]**, chooses **[action]** under **[constraint]**, changes **[state or relationship]**, receives **[feedback]**, and therefore faces a different next decision.

Name the closest known-good anchor, the single primary novelty axis, the rules/experience that must remain invariant, and the smallest observation that would show the idea is cosmetic, opaque, dominated, tedious, or infeasible.

Use the **theme-removal test** as a diagnostic: remove cosmetic names and unrelated polish, not information or feedback that makes the mechanic work. Perceptual, spatial, narrative and social signals can be causal parts of gameplay. If only the decoration changes, label presentation novelty honestly; do not reject a perception-based mechanic by deleting its input.

## Generate differences in causality

Use the agent for breadth, but vary causal relationships rather than adding systems. Useful axes include what the player can act on and transform; what information is visible, delayed, hidden, shared, or inferred; timing/commitment/reversibility; spatial propagation; resource conversion and opportunity cost; social option changes; and how history changes future affordances.

When the design is unsettled, sketch a small set of causally distinct mechanic kernels. Use only enough candidates to expose the important alternatives; no fixed candidate count is required. Reject candidates that differ only in theme, quantity, reward values, VFX, or content. Implement only the few whose difference genuinely requires play to decide.

Prefer one understandable anchor plus a strong design delta where useful. Treat an inseparable bundle explicitly; do not force an unfamiliar mechanic into an existing genre or forbid multiple necessary relationships merely to satisfy an axis count.

Compare candidate and anchor before implementation with the same trace: observed information, legal actions, chosen action, state transition, feedback, and next legal actions. If renaming objects makes the traces equivalent and the same dominant policy solves them, the candidate is probably a reskin or parameter change.

Run an adversarial pass that tries to collapse each candidate into a trivial policy where that would violate the player promise. Repetition or waiting can be intentional in rhythm, idle or expressive play. Do not let the proposing pass defend the idea with future content, progression, narrative, or polish. Revise or reject when the weakness is structural.

## Reject weak ideas before expensive production

Trace a few concrete turns or seconds. Check:

- **Counterfactual choice:** Is there a reachable state where at least two plausible actions lead to meaningfully different futures?
- **State consequence:** Does the action alter later possibilities, information, position, timing, relationships, or value—not only add points?
- **Model formation:** Can a player predict from feedback and revise after an exception?
- **Exploit resistance:** Does spam, waiting, one dominant action, or a trivial sequence solve most states?
- **Teachability:** Can the relation be learned through action and feedback without a long explanation?
- **Content independence:** Does it remain interesting in a small sandbox, or require content volume to hide repetition?
- **Recovery:** Can a failed experiment lead quickly to another informed attempt?

Do not prove a design by verbal elegance. A candidate that cannot survive a short state trace should not receive a broad production pass.

## Build a mechanic kernel in Godot

Create the shortest repeatable playable loop that exposes the causal relation. Keep only assets, UI, opponents, or content needed to read and exercise it. Preserve the visual-reference contract, but do not let pixel polish delay discovery of an uncertain rule unless visual perception is itself the mechanic.

Build observability early. Expose the smallest useful authoritative state through debug UI, structured logs, test hooks, or a project-native bridge:

- current state and legal actions;
- action, precondition, state delta, and outcome reason;
- opportunities shown, not just selections made;
- timing windows and actual activation edge;
- key resources, positions, relationships, and terminal condition;
- a repeatable named scenario or seed;
- performance counters only when they affect experience.

Use named test scenes or fixtures to return to important situations cheaply. Keep at least one clean-launch path using real controls so injected states do not masquerade as reachability.

## Compare playable causal variants

When evidence is needed, hold the player promise, scenario, target, input, art readability, and content opportunity constant. Change one causal link or an explicitly inseparable bundle. Reuse Resources/configuration or small branches rather than cloning full games.

Probe the same build with policies that expose different failure modes: hesitant first action, aggressive optimization, exploratory play, idle/waiting, rapid contradictory input, and boundary use. These are diagnostic algorithms, not simulated human opinions.

Record concrete observations such as time/actions to first meaningful decision, prediction of result direction, distinct reachable states/recoveries, dominant-action frequency against opportunities, no-progress/softlock states, and whether a second run supports a materially different plan.

Do not invent a universal fun, originality, or creativity score. A variant that violates a required condition cannot win because it has more features or prettier output.

## Use human judgment at the right boundary

The agent can establish execution, reachability, clarity failures, causal differences, and many degenerate strategies. It cannot certify delight, tension, surprise, fairness, social comfort, or voluntary replay for the target audience.

When a human is available, put playable variants in front of them rather than asking them to choose from prose or screenshots. Ask what they expected an action to do, when they changed plan and why, which consequence felt earned/arbitrary, what they would try differently, and whether the new relation created a decision or only extra work.

Separate observed behavior, participant statements, and interpretation. A small playtest can eliminate weak hypotheses; it does not prove market demand.

For consequential claims, use [verification separation](verification-loop.md) and bind the review to fixed conditions. Classify harness/implementation/presentation failures before rejecting a design; lack of opportunity to exercise a rule is not evidence it has no value.

## Integrate without erasing the experiment

Retain the strongest verified baseline, rejected hypothesis and failure reason under its tested conditions, and selected design delta. Use [project memory](project-memory.md) when cross-session reuse is worthwhile; record what would justify revisiting an unsuccessful attempt. Once the mechanic is stable enough for the brief, freeze authoritative rules, add regression scenarios, then expand representative content and the live quality exemplar. Do not keep generating alternatives after decision-relevant uncertainty is resolved.

Use claim language proportionate to evidence:

- `DISTINCT_IN_THIS_PROJECT` for a verified internal difference;
- `DISTINCT_AMONG_VERIFIED_REFERENCES` after direct comparison with named released games;
- `HISTORICALLY_NOVEL` only after dedicated research capable of supporting that claim.

A successful prototype supports the narrow mechanic claim and requested delivery. It does not establish universal fun, commercial potential, or historical originality.
