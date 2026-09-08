# Near-release quality in a bounded slice

NEAR_RELEASE_SLICE is the default when the user asks for a finished playable game, high-completion prototype, or release-like vertical slice without naming a fidelity target. It is not the default for a mechanic spike, quick graybox, technical proof, isolated fix, or explicitly rough experiment. It means release-like craft within a deliberately small playable scope, not full content, certification, security review, market fit, or proven human enjoyment.

## One acceptance source

Set concrete criteria in the existing brief before implementation. Identify target device/window range, supported input, representative session, content boundaries, and performance expectations appropriate to that game. The dimensions below are a coverage map, not a second contract. A quality review links brief IDs to evidence. Do not invent universal FPS, session-length, win-rate, asset-count, or aesthetic-score thresholds.

| Dimension ID | Evidence that matters | Typical major failure |
|---|---|---|
| gameplay | Real input realizes the player promise and distinct interaction; representative content has purposeful variation | Core action is trivial/broken, forced choice dressed as strategy, unreachable advertised content |
| ux | First action, guidance, information hierarchy, controls, feedback and outcome are intelligible at play size | Hidden objective, stale HUD, invisible timing region, mouse-only modal in controller gameplay |
| art | In-engine composition matches the chosen visual identity across hero, world, UI, icons and states | Style collage, accidental placeholders, misleading silhouette, clipped or drifting sprites |
| motion_audio | Applicable animation/event timing, cue hierarchy, mix and recovery agree with rules and style | Animation lies about hit timing, unreadable effects, silent required feedback, overlapping/clipped audio |
| reliability | Launch, complete session, failure/reset, interruption and relevant persistence paths pass | Crash, softlock, stuck input, duplicated rewards, progress loss |
| performance | Target-condition measurements cover cold start and the busiest representative play | Warm-cache-only check, frame-time spikes during decisions, runaway memory |
| platform_access | Supported input, viewport range, focus, applicable accessibility paths, and each chosen runtime work | Offscreen control, color-only essential cue, mouse-only required modal, chosen Web files produced but never run in a browser |
| text_render | Required scripts/glyphs are bundled and render correctly in the final Web BUILD_ID at supported sizes | Tofu/replacement glyphs, desktop-only system fallback, clipped Chinese/localized labels, stale cached font/export |
| delivery_rights | Clean exact package opens; controls/settings/credits are present when required; actual asset/code rights tracked | Missing runtime asset, secrets, incompatible plugin, preview art treated as licensed source |

Assess all nine dimensions, but do not manufacture work for an inapplicable dimension. Record one of:

- `PASS`: applicable and supported by the required evidence.
- `FAIL`: applicable and observed to violate the brief.
- `UNVERIFIED`: applicable, but the required observation could not be obtained. This blocks a near-release DONE claim.
- `NOT_APPLICABLE`: the delivered experience genuinely has no requirement in this dimension. Link the brief and explain why. Lack of tools, time, evidence, or a failed test is never `NOT_APPLICABLE`.

A silent design may make audio-specific checks inapplicable while motion remains applicable. A game with no player-facing text can mark text rendering `NOT_APPLICABLE`. A peaceful toy can satisfy gameplay through expressive actions and response rather than combat or winning. Applicability comes from the experience and brief, not from convenience after a failure.

## Finish quality, not feature quantity

Complete the chosen player journey: entry, guidance in context, representative middle, satisfying result or stable sandbox state, recovery and return. Include required settings and controls. An elegant start directly into play is valid; title screen, trailer, economy, achievements, backend, or meta progression are not mandatory decorations.

Before content multiplication, build a live quality exemplar with representative actor, environment, UI, interaction feedback, motion, and sound where appropriate. As soon as one character, one required-language string, one button, and one sound exist, run that slice on the intended target; do not wait for a complete level. Before final DONE, inspect the finished experience on each chosen player-facing runtime. A Web delivery uses the share mode and WEB_PREFLIGHT in web-delivery.md, including CSS display size, viewport fit, full visibility, and button clickability—not backing-canvas size alone. LAN sharing is required only when that route is chosen. Run the text-render gate whenever player-facing non-Latin/localized text is present. Judge concrete readability, coherence, response and polish defects, not whether the illustration looks expensive.

## Review and convergence

Review from three perspectives without pretending to spawn independent people: a new player tries the normal route, an art/design reviewer checks the promise and coherence, and a release tester checks robustness and packaging. Actual separate reviewers are optional unless specified. Ask what observed defect would stop the player, confuse the intended action, or make the scene look unfinished.

Use BLOCKER for an unusable required path or serious rights/security/data-loss issue, MAJOR for a materially broken or visibly unfinished requirement, and MINOR for a local defect that does not prevent the stated quality. Repair blockers and majors, rerun their reproductions, and do a fresh-start end-to-end pass after content freeze. A changed area invalidates its evidence and relevant regressions, not every unrelated test.

No fixed round count or score proves perfection. Stop when the brief is met, all applicable dimensions pass, explicitly inapplicable dimensions are justified, the fresh review reveals no unresolved blocker/major within scope, and remaining minor limitations are explicit. If an essential applicable test is unavailable, record `UNVERIFIED`; do not relabel it `NOT_APPLICABLE` or claim near-release verification.

## Record and claim boundary

For NEAR_RELEASE_SLICE, use `templates/quality_review.json` at final handoff (or an existing equivalent with these fields); do not create it after every edit. Link every dimension to brief IDs. `validate_quality_review.py REVIEW --artifact ARTIFACT` checks status semantics, evidence identities, defects and human-label consistency. It does not decide whether the agent's applicability judgment is aesthetically or commercially correct.

Art/UX passes are named observations by an agent or human, not objective measurements of beauty or audience response. `humanExperience.status=UNTESTED` remains valid for an autonomously delivered candidate; then label player appeal unvalidated. Do not fill that gap with an LLM fun score.

When the brief selects NEAR_RELEASE_SLICE, run release validation with `--required-profile NEAR_RELEASE_SLICE` so omission of the profile cannot silently fall back to weaker checks. Add `--required-share-mode LAN_SHARE` only when LAN sharing is actually part of the brief.
