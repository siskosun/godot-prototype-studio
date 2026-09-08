# Task-sized workflow

Choose the relevant branch; these are obligations, not a fixed sequence or approval itinerary. Do not force an existing-project repair through discovery.

## Common opening

Read applicable repository instructions, current brief and relevant progress if present, then inspect the affected project surface. Check version, main scene, input, assets, or exports only as needed. Preserve unrelated work. Establish a baseline before a change whose effect needs comparison.

For a new prototype, perform the one-time visual reference intake in the first response. Ask for images plus `PARTIAL_REFERENCE` versus `PIXEL_ACCURATE_REFERENCE` when none are present; when images are already present, ask only for the mode and scope. Do not repeat an already answered question. Branch-independent inspection, research, and design may continue, but do not lock or mass-produce art before the reference intent is resolved.

## NEW_PROTOTYPE

Align the brief, research released mechanic references, resolve visual reference intent, and complete a buildable design. Use the optional starter only if it saves work; it is instrumentation, not a finished game.

When originality or differentiation is material, read `novel-gameplay.md`. Define one familiar anchor, one primary causal design delta, invariants, and a falsifier. Sketch causally distinct kernels, reject cosmetic variants, and implement only the few that need actual play to resolve. Use `templates/mechanic_lab.md` when the experiment benefits from a durable record; it is not a second acceptance contract.

Build the differentiating interaction as the smallest repeatable playable kernel. Add enough authoritative state, named scenarios, input traces, screenshots, and outcome reasons for the agent to inspect its own work. Test counterfactual choices, dominant/spam/wait strategies, recovery, and whether feedback lets the player form a useful model. Preserve a clean real-input path; local state fixtures accelerate diagnosis but do not establish reachability.

Select or revise the strongest kernel from play evidence, not a prose creativity score. Then create an integrated live quality exemplar before broad content. Read quality-bar.md for a near-release slice. Representative scenarios should cover normal play, the differentiating interaction, failure/recovery, and a stress/boundary case; select their count from the mechanic rather than a fixed quota. Make objective, input, consequences, and retry understandable at actual play size.

As soon as one character, one required-language string, one button, and one sound exist, export and run that slice on the intended target (`FIRST_TARGET` for Web). Do not wait for a complete level. Native-looking output does not prove a later Web or packaged runtime.

Use gameplay-and-ux.md and art-direction.md to improve observed weaknesses. Continue into complete-session content, integrated art/audio, animation, UI, controls, and polish. Exercise real player input and inspect rendered presentation. Use game-qa-and-replay.md for proportionate risk/replay checks. Repair defects and retest the suites named by [change impact](change-impact.md); do not rerun an unrelated seed battery because a harness or document changed. Package and test the requested targets only. When Web is a chosen delivery, stamp a BUILD_ID, serve it, run the applicable WEB_PREFLIGHT, and exercise the required browser path. Choose LOCAL_WEB_TEST or LAN_SHARE from the receiver context; LAN is not a quality prerequisite. Keep source and Web hashes/evidence separate; when the working tree contains `export/web`, stage/package the editable source without that generated directory before source hashing. Use `package_and_report.py` as the freeze/hash/report entry so identities are not filled by hand. Public hosting is a separate action. Neither a foundation verdict nor an optional human review interrupts this commission.

## FEATURE_CHANGE / BUGFIX

Reproduce the baseline through the user's path. Find the owning rule/scene and relevant callers; avoid a repository-wide map without need. Fix the cause rather than hiding the symptom. Classify the change, rerun the matching suite, and reuse earlier evidence only when the relevant identity hash is unchanged. Update design only when the rule actually changes. Preserve unrelated features and files. Do not reopen visual-reference intake for an unrelated fix.

## POLISH_QA

Capture the relevant baseline. Resolve visual-reference mode if the task materially changes the art and it was never recorded. Improve readability, response, timing, layout, motion, audio, pacing, or coherence within the design. Choose reversible aesthetic details when delegated. Inspect the changed result in motion or at actual play size. If a change alters core rules or scope, resolve it against the brief rather than disguising it as polish.

## EXPERIMENT

Define the question, baseline, variable, bounds, and evidence that would change the next action. For a new mechanic, compare causal links rather than theme skins or feature counts. Run the same scenario before/after, retain or revert, and record consequential findings. A negative hypothesis result can complete an experiment-only request; it is not a reason to abandon a still-feasible build request.

## DISCOVERY / REVIEW_ONLY

Deliver the requested comparison, design, brief, diagnosis, or review without unrequested implementation. End when that deliverable is complete. Do not label an unbuilt idea playable or a review a hands-on playtest.

## RELEASE_REVIEW

Check the brief against the actual final build; use the requested stakeholder lens. Freeze, run, and bind evidence to the exact delivery. Packaging is already authorized when requested; public release is a separate action.
