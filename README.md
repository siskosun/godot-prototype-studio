# Godot Prototype Studio 0.8.0

[English](README.md) | [Chinese](README.zh-CN.md)

Build a small, complete game prototype or near-release slice with task-sized design, implementation, repair and verified delivery. Godot remains the primary engine, but new prototypes can route to simple browser-native H5 when that is clearly cheaper and sufficient. The skill is model-agnostic. It does not promise a full commercial game, historical originality or validated audience appeal.

## What changed

0.8.0 keeps the 0.7 routing, reuse and multiplayer baseline and closes the gap between "the feature runs" and "the intended player experience is actually supported."

- **Experience spine, only when useful:** preserve the player promise, core tension/verb, existing loop layers, retained design pillars and non-goals across repeated multi-system edits. Do not create a second GDD or force progression/meta onto games that do not need it.
- **Experience claims become hypotheses:** connect design intent -> observable player behavior -> correct runtime behavior -> human evidence when the claim is subjective. Model opinion, a bot policy or a green logic test cannot certify fun.
- **Runtime logic can be temporal:** for consequential stateful rules, define observable behavior contracts and inspect relevant ticks/transitions so a valid final state cannot hide an invalid path. Use baseline plus meaningful perturbations and treat every core requirement as required.
- **Test the evaluator too:** when an automated oracle materially controls acceptance, confirm it rejects a disposable deliberately broken fixture/mutant. Do not require this ceremony for narrow low-risk edits.
- **Behavior-first human playtests:** predeclare the question, observe cold-start behavior and expectation mismatches, and keep observations, participant statements, runtime facts and interpretation separate. No universal tester count or vote threshold is imposed.

See [experience validation](references/experience-validation-loop.md), [runtime logic verification](references/runtime-logic-verification.md), and the [0.8.0 audit](audit/v0.8.0-experience-validation.md). The 0.7 routing/reuse and multiplayer guidance remains in place.

## Use

Load `SKILL.md`, not the entire reference directory. Import the complete `skill.zip` through the host's supported skill flow; downloading or updating GitHub does not install it into an account. Preserve existing projects and history.

Example: "Build this idea as a small but complete Godot slice. Keep the core interaction, clarify the visual reference once, choose reversible details, test the actual target, repair observed issues and finish the requested delivery."

A rough mechanic probe or narrow repair stays narrow. Ordinary reversible choices are delegated within intent; retained creative decisions, explicit approval stops, paid actions, destructive changes, private-data uploads and public publishing keep their authorization boundaries.

## Visual references: resolve once

For a new prototype or material visual redesign, ask for one to three usable reference images when none are supplied, and clarify partial versus pixel-accurate use. If images already exist, ask only how each should be used. If mode and scope are already clear, do not ask again.

| Mode | Contract |
|---|---|
| `PARTIAL_REFERENCE` | Identify the properties each image controls; keep unspecified parts original |
| `PIXEL_ACCURATE_REFERENCE` | Fix target frame/state, viewport, resolution, crop, permitted assets/fonts, rights and allowed differences |
| `ORIGINAL_DELEGATED` | User delegates an original visual baseline without images |
| `NOT_APPLICABLE` | Genuinely visual-irrelevant work or an explicitly diagnostic graybox |

Pixel matching is scoped to the declared frame and environment, not proof of animation, responsiveness or every aspect ratio. Preserve reference scope when applying general design advice. See [intake](references/visual-reference-intake.md) and [art direction](references/art-direction.md).

## New gameplay

Define a player-facing causal difference, invariants and a falsifying observation. Use a familiar anchor when helpful, without forcing invention into an existing genre. Make the smallest repeatable kernel; inspect authoritative state, available actions, outcomes and real-input paths before multiplying content.

Remove cosmetic framing in the theme-removal test, not sensory information that causes the mechanic. Diagnose implementation, presentation, opportunity and harness failures before rejecting a design. Repetition or waiting may be intentional. Compare meaningful variants under comparable conditions, and preserve the scope and reason for rejected attempts.

A mechanically distinct candidate is not proven fun. Human observations, participant statements and interpretation remain separate. `DISTINCT_IN_THIS_PROJECT` and `DISTINCT_AMONG_VERIFIED_REFERENCES` require their respective evidence; `HISTORICALLY_NOVEL` needs dedicated research. See [novel gameplay](references/novel-gameplay.md) and the optional [mechanic lab](templates/mechanic_lab.md).

## Completion, delivery and evidence

A finished/high-completion request defaults to `NEAR_RELEASE_SLICE` when no narrower fidelity is given. This is a craft bar, not a package list. Without a requested package, hand off the tested in-place Godot project. Add `GODOT_PROJECT_ZIP`, `WEB_EXPORT`, desktop, Android or `LAN_SHARE` only for the requested runtime/receiver.

Preserve early first-target smoke, a live quality exemplar, real-alpha/pivot/scale checks before asset batches, complete-session UX/recovery, and final normal-input verification. Chosen Web builds need actual served-browser checks including display-fit/clickability, required text/audio and separate source/Web identities. LAN is optional; non-loopback LAN delivery uses HTTPS. Source staging excludes generated `export/web`.

The brief owns acceptance; progress supports resumption; optional memory indexes reusable knowledge. Human playtests do not routinely block delivery, but absent evidence cannot support enjoyment/preference claims. `DONE` requires the requested artifact and applicable evidence. `BLOCKED` reports a genuine unmet condition and the strongest usable partial result. Inapplicability needs a reason; unavailable evidence is `UNVERIFIED`.

## Optional utilities

Python 3 is required for bundled scripts; asset inspection/tests need Pillow. The LAN server can use an existing certificate or `openssl`. Scripts do not install dependencies, publish games or call paid services. Repository CI separately provisions its isolated test dependencies.

From the skill directory:

```bash
python scripts/init_workspace.py PROJECT
python scripts/init_workspace.py PROJECT --novel-gameplay --with-memory --reuse-scan
python scripts/init_workspace.py PROJECT --multiplayer
python scripts/run_godot_checks.py PROJECT --mode import
python scripts/check_project_memory.py PROJECT
python scripts/verification_checkpoint.py freeze PROJECT --plan .prototype/spec/mechanic_lab.md --out .prototype/evidence/review-01.json
python scripts/verification_checkpoint.py check PROJECT --record .prototype/evidence/review-01.json
python scripts/change_impact.py --before-tree OLD --after-tree NEW
python scripts/serve_web_export.py export/web --runtime-record .prototype/evidence/web-server.json
python scripts/package_and_report.py PROJECT --out RELEASE_DIR
```

Default initialization still creates only brief/progress. `--novel-gameplay` adds the mechanic lab; `--with-memory` adds an empty memory record; `--reuse-scan` adds the pre-development search record; `--multiplayer` adds the joint-session matrix; `--with-starter` is for blank projects; `--legacy-full` preserves detailed legacy records. Existing files are not overwritten. Fill the brief/plan before checkpointing. These commands are examples, not a required sequence.

Memory checker exit codes: 0 current/empty, 1 stale/unverified, 2 invalid. Checkpoint exit codes: 0 created/matching, 1 drift, 2 invalid. Neither reports game-quality PASS. Godot runner exit codes remain 0 PASS, 1 failure, 2 unavailable/invalid, 3 PARTIAL. See [tool contracts](references/tool-contracts.md) and [Web delivery](references/web-delivery.md) for existing utilities.

## Validation and limits

```bash
python -m unittest discover -s tests -v
```

CI runs utility tests and retains exact tracked-source/log artifacts. A pre-existing 0.5.0 checkerboard fixture overwrote its own test image; this release fixes setup order without changing the detector or relaxing assertions.

Utility/static/HTTP fixture tests are not live Godot, browser, agent or target-player trials. Checksums establish identity, not truth, authority, independent judgment, beauty or fun. The [controlled live-evaluation plan](audit/v0.6.0-evaluation.md) is explicitly not yet run; creative uplift is not claimed.
