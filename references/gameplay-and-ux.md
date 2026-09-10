# Improve gameplay and user experience through observed play

Here UE means user experience; use UX in records to avoid confusion with Unreal Engine. Apply only the parts relevant to the player's intended experience.

## Make the promise observable

Explain the main action, information available before it, consequence, feedback, and next action. Identify the differentiating interaction and why it should matter to this audience. For strategy, test meaningful tradeoffs and opportunity cost; for action, timing/position/response; for expressive toys, agency and interesting response; for narrative, comprehension and consequence. Do not force combat, multiple strategies, fail states or permanent progression onto every genre.

Choose the smallest complete session that demonstrates that promise. Plan purposeful encounters or situations: introduce a rule, use it, vary a relevant constraint, and combine or resolve it. A palette swap or larger health number alone is not proof of a new decision. Avoid mandatory content quotas and random complication. Reuse a mechanic in situations that change what the player does.

## First play and return play

Start a clean build without the designer's internal explanation. Can a player tell what to do, act, see the result and recover? Put guidance at the moment of need; teach through a safe action before pressure where appropriate. Do not frontload all rules, add compulsory long intro animation, or use instructions to conceal an unclear affordance.

Show interactable, focused, pressed, disabled and selected states as applicable. State-changing information must stay synchronized with the authoritative model. A failure should show its actionable cause and a low-friction restart. Make the actual interaction region visible when timing or placement depends on it. Test its entry, valid interval, exit and terminal response; never leave a failed round running until an unrelated late timer ends it.

Use the same input modality across gameplay, menus, results and settings. Check focus return, hover-free touch operation, accidental double activation, pointer cancellation, hold/release behavior and interrupted input. For timing-critical actions, choose and communicate the actuation edge deliberately; generic release-on-click menu advice must not silently move a timing mechanic's activation to a different instant.

For observed first-use confusion or an unclear session ending, use only the relevant section of [conditional design heuristics](design-heuristics.md). Preserve simultaneous goals, recoverable help and genre-appropriate endings; short rounds do not require permanent progression.

## Feel with causal discipline

Map input -> anticipation when intended -> execution -> impact -> recovery. Align animation, hit detection, sound, particles, camera and HUD with those events. Anticipation adds weight but can also create input lag; extra hit-stop or shake can hide information. Adjust within the designed response window, use fewer stronger semantic cues, and compare the same play path before/after. Keep accessibility alternatives for intense motion/flash when relevant.

Test forgiving input buffering, coyote time, snapping or aim assistance only where they support the intended skill and control scheme. Do not blindly add these to every game. Fix collision/readability problems before increasing forgiveness or making the game easier.

## Improve through targeted experiments

Pick the largest observed friction: unclear objective, inert choice, dominant tactic, pacing stall, unearned death, poor feedback, repetitive encounter, or control mismatch. State a causal hypothesis, alter one dimension or inseparable bundle, run the same scenario, and keep/revert based on evidence. Use isolated Resource/config alternatives instead of rewriting the game for each variant. See variant comparisons.

Test plausible policies against the same opportunities: cautious, aggressive, exploratory, idle or boundary input only when they expose different risks. Collect reachable states, outcomes, failure reasons, choice opportunities, use counts, time spent and recovery costs where useful. These are diagnostics, not universal fun scores. A player who did not choose an item may never have seen or been able to afford it; record opportunity before inferring preference or an unused mechanic.

Do not reward the generator for adding buttons, code length, particle count, choice count or longer session time. Do not maximize win rate at the cost of challenge. Preserve the best verified baseline, meaningful mechanic changes and failed hypotheses; reject a revision that looks richer but worsens the player promise or functional quality.

## Human evidence without routine interruption

When real participants are available, observe unassisted first action, confusion, decision reasoning, failure understanding and voluntary replay, under consent and a named build. Distinguish observations from statements and from interpretation. A tiny sample is diagnostic, not market validation. Automated tests and model reviewers can identify contradictions; they cannot certify fun, fairness or accessibility for the audience.

Finish all agent-verifiable improvements without waiting for optional participants. Report remaining experience hypotheses explicitly. Never simulate humans by role-playing them and record the output as user testing.

Evidence basis: S14-S19 support interaction-based evaluation and its limits; S09/S10 address input/access; S20 addresses opportunity-aware inference. Specific design decisions here are contextual recommendations, not empirically guaranteed improvements.
