# Godot Prototype Studio 0.6.0

[English](README.md) | [Chinese](README.zh-CN.md)

Build a small, complete Godot 2D prototype or near-release slice, with task-sized design, implementation, repair and verified delivery. The skill is model-agnostic. It does not promise a full commercial game, historical originality or validated audience appeal.

## What changed

0.6.0 builds on the exact GitHub 0.5.0 source. It adds evidence continuity and conditional design guidance without turning every task into a multi-agent production pipeline.

- **Project memory, optional:** retain narrow findings with sources, dependency hashes and revisit conditions. A hypothesis stays a hypothesis; a failed attempt is not a permanent ban. The read-only checker flags stale/unverified records.
- **Verification checkpoints, optional:** bind the existing brief, scenario plan and artifact before consequential review. Detect drift; do not confuse matching hashes with execution or sandbox enforcement. Separate reviewer responsibilities when useful, with a labeled self-review fallback.
- **Actual engine capabilities:** use existing CLI/editor/QA interfaces and probe the operations a task needs. Distinguish state injection, engine events and OS/browser input. The starter is still an instrumentation fixture, not an autonomous game-playing or remote-editor system.
- **Conditional design heuristics:** apply experience-to-visual rules, positive/negative examples, guidance transfer and session closure to relevant problems. No universal keyword count, style, tutorial cadence, permanent progression or fun score.

See the [upgrade and evaluation record](audit/v0.6.0-evaluation.md), [verification loop](references/verification-loop.md), [project memory](references/project-memory.md) and [design heuristics](references/design-heuristics.md).

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
python scripts/init_workspace.py PROJECT --novel-gameplay --with-memory
python scripts/run_godot_checks.py PROJECT --mode import
python scripts/check_project_memory.py PROJECT
python scripts/verification_checkpoint.py freeze PROJECT --plan .prototype/spec/mechanic_lab.md --out .prototype/evidence/review-01.json
python scripts/verification_checkpoint.py check PROJECT --record .prototype/evidence/review-01.json
python scripts/change_impact.py --before-tree OLD --after-tree NEW
python scripts/package_and_report.py PROJECT --out RELEASE_DIR
```

Default initialization still creates only brief/progress. `--novel-gameplay` adds the mechanic lab; `--with-memory` adds an empty memory record; `--with-starter` is for blank projects; `--legacy-full` preserves detailed legacy records. Existing files are not overwritten. Fill the brief/plan before checkpointing. These commands are examples, not a required sequence.

Memory checker exit codes: 0 current/empty, 1 stale/unverified, 2 invalid. Checkpoint exit codes: 0 created/matching, 1 drift, 2 invalid. Neither reports game-quality PASS. Godot runner exit codes remain 0 PASS, 1 failure, 2 unavailable/invalid, 3 PARTIAL. See [tool contracts](references/tool-contracts.md) and [Web delivery](references/web-delivery.md) for existing utilities.

## Validation and limits

```bash
python -m unittest discover -s tests -v
```

CI runs utility tests and retains exact tracked-source/log artifacts. A pre-existing 0.5.0 checkerboard fixture overwrote its own test image; this release fixes setup order without changing the detector or relaxing assertions.

Utility/static/HTTP fixture tests are not live Godot, browser, agent or target-player trials. Checksums establish identity, not truth, authority, independent judgment, beauty or fun. The [controlled live-evaluation plan](audit/v0.6.0-evaluation.md) is explicitly not yet run; creative uplift is not claimed.
