---
name: godot-prototype-studio
description: Build, invent, improve, debug, and verify 2D Godot games from ideas or existing projects, including original gameplay experiments, reference-image-directed art, near-release-quality vertical slices, gameplay iteration, and tested delivery. Use for new Godot prototypes, novel mechanics, feature changes, bug fixes, polish, review, or release packaging.
---

# Godot Prototype Studio

Deliver a small but finished-feeling game when the user asks for one. Preserve creative intent, project version/language/conventions/assets, and unrelated work. Do not turn a prototype into unbounded commercial production.

## Establish the result and visual intent

For new games or material redesigns, read [brief and authority](references/brief-and-authority.md). Recover prior decisions, then state the player promise, complete play path, target/input, delivery, quality bar, scope exclusions, required evidence, and delegated choices.

For every new prototype, resolve visual-reference mode in the first response. Read [visual reference intake](references/visual-reference-intake.md). With no usable image, ask once for 1-3 reference images and `PARTIAL_REFERENCE` versus `PIXEL_ACCURATE_REFERENCE`; offer `ORIGINAL_DELEGATED`. If images already exist, do not request them again—ask only how they should be used. If mode and scope are already clear, proceed. Do not turn this into recurring approval.

Ordinary reversible design, art, tuning, implementation, and repair decisions are delegated within the requested intent. Ask only for genuinely blocking choices plus the one visual-reference intake above. Silence never authorizes purchases, public release, private-data upload, destructive changes, exact copying without rights, or changes to retained decisions.

Judge separately:

1. **Completion** — finished/high-completion playable work defaults to **NEAR_RELEASE_SLICE** when no other fidelity target is given; rough probes and narrow fixes keep their scope.
2. **Delivery** — quality does not imply ZIP/Web. If no package is requested, default to the tested in-place project; add Web, ZIP, desktop, Android, or LAN only when requested by runtime/receiver.
3. **Evidence** — collect what the chosen delivery needs. A chosen Web artifact still requires a served browser check; LAN is not a quality requirement.

## Load only what changes this task

| Need | Guide |
|---|---|
| New prototype / material visual redesign | [visual reference intake](references/visual-reference-intake.md), [brief](references/brief-and-authority.md) |
| New or unsettled mechanic | [novel gameplay](references/novel-gameplay.md), [reference games](references/reference-games-and-design.md) |
| Build/change/polish/review | [workflow](references/workflow.md) |
| Near-release acceptance | [quality bar](references/quality-bar.md) |
| Gameplay/UX | [gameplay and UX](references/gameplay-and-ux.md) |
| Art/assets/audio | [art direction](references/art-direction.md), [asset integration](references/assets-and-visuals.md) |
| Text/localization | [text rendering](references/text-rendering.md) |
| Shader | [shader sourcing](references/shader-sourcing.md) |
| Godot architecture/runtime | [architecture](references/godot-architecture.md), [production lessons](references/godot-production-lessons.md) |
| Tool/engine uncertainty | [capabilities](references/capability-adaptation.md), [engine evidence](references/godot-engine-intelligence.md) |
| Risk/replay/player probes | [game QA](references/game-qa-and-replay.md) |
| Evidence/variants | [implementation testing](references/implementation-testing.md), [variants](references/variant-experiments.md) |
| Scope/debug/resume | [scope](references/scope-discipline.md), [debugging](references/debugging-and-experiments.md) |
| Web/first-target/LAN | [web delivery](references/web-delivery.md) |
| Rerun selection | [change impact](references/change-impact.md) |
| Package identity | [release evidence](references/release-evidence.md) |

Conditional references: [collaboration](references/collaboration-and-gates.md), [human playtests](references/playtest-and-player-qa.md), [saves](references/persistence.md), [research experiments](references/design-and-prototype-contract.md), [review lenses](references/review-lenses.md), [Codex](references/codex-harness.md). Maintenance: [instruction audit](references/instruction-audit.md), [source ledger](references/research-basis.md), [provenance](references/research-basis-previous.md), [tool contracts](references/tool-contracts.md). Do not preload the library.

## Build, observe, and revise

For a new idea, verify the closest useful released comparisons when current research is available, then establish the differentiating interaction before multiplying content. When a mechanic is intended to be new or remains unclear, define one familiar anchor, one primary causal design delta, invariants, and a falsifier. Reject cosmetic variants. Build the smallest repeatable playable kernel that can expose counterfactual choices and collapse under spam/wait/dominant strategies if the idea is weak. Never use the agent's prose rating as evidence of fun or originality.

Make the game inspectable: expose useful authoritative state, legal actions/state deltas/outcome reasons, opportunity counts when relevant, named repeatable scenarios, captures, and a clean real-input path. Iterate reproduce -> inspect -> trace cause -> change -> rerun. Debug state injection may accelerate diagnosis but cannot prove normal-path reachability.

As soon as one character, one required-language string, one button, and one sound exist, run the intended target. Before batching generated art, inspect one real sample for alpha, pivot, scale, occlusion, and action. Keep `.prototype/progress.md` current so interrupted work resumes instead of restarting.

Continue through the contracted session, presentation, UX/recovery, real input, repair, chosen-target export, player-facing verification, and exact-package validation. A working core loop or attractive screenshot is only a milestone. Keep implementation small, not the experience incomplete; do not add unrelated systems.

## Stop at completion or a genuine blocker

**DONE** means the requested artifact exists, applicable criteria are supported, no blocking/major defect remains, and run instructions/limits accompany it. `NOT_APPLICABLE` needs a real reason; inability to test is `UNVERIFIED`. Missing human play evidence does not automatically block delivery, but enjoyment/preferences remain unvalidated.

**BLOCKED** means an essential permission, retained decision, tool capability, hard constraint, or host/resource boundary prevents a required condition after safe alternatives. Missing optional MCP, unavailable comparison browsing, ordinary uncertainty, or one failed test is not itself a blocker.

Continue while a material evidenced gap has an authorized repair path. Change the hypothesis or observation method after a failed repair. When criteria hold, run a fresh-start player path and hand off; do not chase hypothetical perfection.

## Evidence and handoff

Keep source, editor, runtime, normal-input, rendered/audio, browser, and human evidence distinct. Automated personas are test policies, not participants; validators establish consistency, not execution or enjoyment.

Lead with the deliverable and run path, then DONE/BLOCKED, implemented scope, observed tests/quality, exact artifact identity, and remaining limits. Never claim installation, tested export, audience preference, commercial readiness, pixel accuracy, originality, or perfection without corresponding evidence.
