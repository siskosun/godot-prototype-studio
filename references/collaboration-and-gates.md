# Human collaboration

Authority rules live in `brief-and-authority.md`; do not create a second approval system here. A human may retain important choices, delegate them, interrupt, or revise the brief. More capable execution does not enlarge external authority.

## Choose whether to ask

Continue when the next action is reversible and within the commission, including delegated taste and design choices. Inform the user about consequential defaults without turning every update into a question. Ask only when a reserved decision, hard-boundary conflict, or unapproved consequential action actually prevents progress.

If using an old `decision_gate.json`, treat `DIRECTION_GATE`, `TASTE_GATE`, and `COMMITMENT_GATE` as categories of a decision, not automatic stop conditions. `INFORM` remains non-blocking. An open gate with a decision already covered by recorded delegation uses status `SUPERSEDED` with `authorityReference` and `supersededAt`, not a fabricated `humanDecision`. Preserve any historical human decision in its original resolved record. Do not bypass an explicit retained gate. Creating a new hypothesis, expanding to already-promised content, or packaging an authorized build does not create a new gate.

## Explain an actual blocker

State the unmet requirement, why it blocks, evidence gathered, attempted alternatives, one recommendation, and at most three choices. Ask in player/product language. Finish safe independent work first. Never ask a novice to choose a node type, architecture pattern, file format, or test framework merely to proceed.

Adapt detail to the user: plain run instructions and recovery for novices; choices, dynamics, and tuning for designers; implementation evidence for technical users. Keep authorship clear: user constraint, agent decision within delegation, and proposal outside delegation are different statuses.

Human playtests remain valuable but do not become mandatory mid-build approvals unless contracted. Prepare a finished playable build for review; mark experience judgments as unverified when no target player has tested them.
