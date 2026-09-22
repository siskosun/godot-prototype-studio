# Runtime gameplay-logic verification

Use for gameplay rules where a valid final state can hide an invalid path, or where several interacting systems make a wrong implementation look runnable. Examples include cooldown/invulnerability windows, scoring opportunities, buffs/debuffs, entity lifecycle, resource bounds, combo state, simultaneous events, targeting, progression gates and multiplayer authority.

Do not turn every small edit into a benchmark harness. Use the cheapest observation that can falsify the consequential claim.

## Define behavior, not source shape

Before a consequential rule change, define the observable contract needed by that rule:

- legal starting scenario or precondition;
- player-level actions that exercise it;
- stable observable state or event fields;
- required outcomes and rejection behavior;
- relevant invariants across time or transitions;
- terminal/recovery condition when applicable.

Leave internal architecture open. Tests should accept materially different correct implementations. A setup hook may establish a legal precondition but must not perform the player action or directly write the expected success result. The observed test state must represent the same authoritative state used by visible gameplay.

For critical requirements, acceptance is conjunctive: every applicable core requirement must pass. Mean check rate, coverage or a mostly-green suite is diagnostic information, not permission to ignore one failed required behavior.

## Verify the path when the path matters

End-state assertions are sufficient only when intermediate violations cannot matter to the player or later state. Otherwise inspect the relevant physics ticks, frames, events or state transitions. Typical temporal invariants include:

- resource/cooldown values stay within legal bounds while changing;
- invulnerability exists only during the intended state/window;
- one opportunity cannot score repeatedly without a new lifecycle;
- a consumed/destroyed entity cannot act again;
- mutually exclusive states never overlap;
- authority/ownership changes only through legal transitions;
- simultaneous outcomes resolve according to the declared rule rather than update order accident.

Do not sample every tick by default. Instrument the smallest temporal surface that could expose the suspected failure. Presentation feel still requires real-time observation; a numerical invariant cannot prove that motion, timing or feedback feels good.

## Use a scenario ladder

Start with a visible baseline that proves the ordinary case. Add only perturbations likely to expose missing robustness:

1. **Baseline:** the representative development scenario.
2. **Perturbation:** different seed, timing, count, position, resource level, input order or viewport where the same rule should still hold.
3. **Same-rule harder scenario:** a combination chosen independently from the implementation when a separate evaluator or fixture system exists.

Keep rules stable across the ladder. Do not create hidden requirements. A secret seed is useful only when the generation and evaluation environments are genuinely separated; otherwise label the test honestly as another scenario.

For composite features, isolate important axes before the full combination when that makes failures attributable. For example, verify damage, shield interaction, death and drop rules separately before treating one integrated combat trace as the only oracle.

## Check the evaluator, not just the game

A passing correct-looking build does not establish that the evaluator can detect the failure it claims to detect. For consequential automated acceptance, use a disposable known-bad fixture or **mutant** that removes or corrupts one required capability. The evaluator should reject it for the intended reason.

Useful mutations include:

- remove a cooldown or resource cost;
- allow duplicate scoring on one opportunity;
- skip a collision/eligibility check;
- permit an illegal state combination;
- bypass normal input and write the terminal state directly.

Never introduce the mutation into the user's production artifact. Preserve the failing fixture or minimal reproduction separately when it remains useful. If the evaluator accepts the known-bad case, fix the oracle before trusting green results.

## Keep input and evidence provenance explicit

Distinguish logic calls, engine-injected events, browser/OS input and physical-device input. A direct model method proves rule logic only; it does not prove input routing. A scenario loader proves the local condition, not that a clean player path can reach it.

When a critical failure appears, classify it before redesigning: PRODUCT_DEFECT, TEST_HARNESS, ENVIRONMENT, PRESENTATION/READABILITY, OPPORTUNITY, or INCONCLUSIVE. If the failure would cause a major redesign, confirm it with a second adequate observation path when practical rather than treating one harness result as design truth.

Use [implementation testing](implementation-testing.md) for evidence levels, [game QA and replay](game-qa-and-replay.md) for normal-player paths and replay corpora, and [verification loop](verification-loop.md) for reviewer separation and artifact freezing.
