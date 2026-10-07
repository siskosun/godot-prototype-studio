---
name: godot-prototype-studio
description: Build, improve, debug, test, polish, and deliver small Godot game prototypes and near-release slices. Use for Godot gameplay, experience design, runtime logic, visuals, playtests, multiplayer/LAN, Web export, QA, reuse, and tested delivery. Stay on Godot when already selected; compare stacks only when genuinely open.
---

# Godot Prototype Studio

Build the smallest complete Godot result that satisfies the player's intended experience. Preserve the existing project version, language, conventions, assets, and unrelated work.

## 1. Start from authority

Recover the user's brief, current project state, and repository instructions before editing.

If the project is managed by **game-exp**, read [game-exp integration](references/game-exp-integration.md) first. Treat game-exp's protected Ledger/Manifest as authoritative for experiment identity, lifecycle, branch, scope, Candidate identity, promotion, selection, integration, and archive state. GPS owns implementation and evidence, not experiment promotion.

Otherwise the mission brief is the delivery acceptance contract. See [brief and authority](references/brief-and-authority.md).

For a new prototype or material visual redesign, resolve visual-reference mode once using [visual reference intake](references/visual-reference-intake.md). Do not repeat the question after it is settled.

## 2. Keep the selected stack

If the user explicitly asks for Godot, the repository is already Godot, or game-exp binds a Godot prototype, stay on Godot.

Only compare Godot with H5/browser-native implementation when the user has not selected a stack and the request is genuinely stack-open. See [route and reuse](references/prototype-routing-and-reuse.md).

If the resolved stack is H5, hand the player-experience goal, route decision, and reuse conclusion to the `h5-game-prototype-agent` skill. If that skill is unavailable, tell the user and let them choose whether to install it or stay on Godot; do not recreate an H5 workflow inside GPS.

Before substantial new implementation, search for reusable same-stack source when reuse could materially save work. Use [reuse sources](references/reuse-sources.md) as discovery guidance; original source and license remain authoritative.

## 3. Build the playable path first

Implement the shortest complete player path before expanding content. For unsettled mechanics, state the causal hypothesis, invariants, observable falsifier, and smallest repeatable kernel. See [novel gameplay](references/novel-gameplay.md).

Use [Godot practical guide](references/godot-practical-guide.md) for concrete Godot 4.3+ patterns, headless tests, Web export basics, input/focus pitfalls, Tween lifecycle, and common fixes.

Run the intended target early. Verify representative text, input, audio, scene composition, and generated assets before batching content.

## 4. Separate evidence layers

Keep these distinct:

- source/static correctness;
- Godot import/runtime behavior;
- normal player-input reachability;
- presentation/browser behavior;
- human playtest observations.

Injected state or input is diagnostic evidence, not proof that the normal player path works. Runtime correctness does not prove fun, preference, fairness, accessibility, or market demand.

For consequential stateful rules, use [runtime logic verification](references/runtime-logic-verification.md). For repeated experience work, use [experience validation](references/experience-validation-loop.md). For replay/input evidence, use [evaluation interface](references/evaluation-interface.md) and [game QA](references/game-qa-and-replay.md).

When repeated repairs lose object/interaction ownership, use the optional [design-to-source repair loop](references/design-repair-loop.md): stable semantic IDs, source bindings, identity-bound execution feedback, smallest authorized patch, and the same checks again. This index never replaces the brief, expands game-exp scope, or grants Review/selection authority. Skip it for a trivial isolated edit.

The starter QA bridge is a **debug/test interface**. It must be unavailable in ordinary release play unless an explicit QA export feature is enabled.

## 5. Compare variants without stealing human decisions

Use [variant experiments](references/variant-experiments.md) only when an unresolved decision benefits from comparable alternatives.

GPS may choose ordinary local implementation/tuning variants inside delegated authority. In a game-exp-managed experiment, GPS must not select among game-exp Candidates, record human Review, promote to PROMISING/SELECTED, or reject a Candidate. It produces evidence and hands the decision back to game-exp.

## 6. Verify the requested delivery

A finished/high-completion playable request defaults to **NEAR_RELEASE_SLICE** when no narrower fidelity target is given. A rough mechanic probe or isolated fix remains narrow.

Quality does not imply a package. If no package is requested, deliver the tested in-place project. Add Web, ZIP, desktop, Android, or LAN only when requested or required by the receiver.

A Web artifact requires a served-browser check. Multiplayer/room/LAN promises require a joint client/server session at the highest promised layer. See [web delivery](references/web-delivery.md), [multiplayer verification](references/multiplayer-session-verification.md), and [release evidence](references/release-evidence.md).

## 7. Stop when the current uncertainty is resolved

**DONE** means the requested artifact exists, applicable checks support it, and no blocking/major defect remains.

**BLOCKED** means an essential permission, retained decision, capability, or hard constraint prevents a required condition after safe alternatives have been tried.

Do not add unrelated systems or more process after the current decision has enough evidence.

## Runtime references

Load only what the current task needs:

- gameplay/UX: [gameplay and UX](references/gameplay-and-ux.md)
- art/assets/audio: [art direction](references/art-direction.md), [assets and visuals](references/assets-and-visuals.md)
- architecture: [Godot architecture](references/godot-architecture.md)
- text/localization: [text rendering](references/text-rendering.md)
- persistence: [persistence](references/persistence.md)
- project memory: [project memory](references/project-memory.md)
- change-based retesting: [change impact](references/change-impact.md)
- tool behavior: [tool contracts](references/tool-contracts.md)

## Core utilities

Bundled scripts use Python 3. The thin starter requires Godot **4.3+**.

```bash
python scripts/init_workspace.py PROJECT
python scripts/run_godot_checks.py PROJECT --mode all
python scripts/detect_capabilities.py PROJECT --write
python scripts/change_impact.py --before-tree OLD --after-tree NEW
python scripts/serve_web_export.py export/web --runtime-record .prototype/evidence/web-server.json
python scripts/publish_github_pages.py --repo owner/repo --source export/web --version-key <source_sha> --producer godot-prototype-studio --json
python scripts/package_and_report.py PROJECT --out RELEASE_DIR
```

Run repository regression tests with:

```bash
python -m unittest discover -s tests -v
```

Utility tests do not substitute for live Godot/browser/player evidence.

For a game-exp-managed implementation pass, return one structured `iteration_delivery` object after completed source work. Include 1-8 player-visible changes, a verified playable descriptor or explicit `MISSING`, 1-3 playtest focus points, `producer=godot-prototype-studio`, optional build identity, and an optional real prior Candidate id. When the game-exp handoff requests a shareable URL for a public repository and the project has a compatible non-threaded Web export, prefer the bundled immutable GitHub Pages publisher backed by the managed game-exp Pages workflow, then run WEB_PREFLIGHT and real-browser player input against the deployed URL before setting `verified=true`. It is participant-reported implementation context only and never authorizes Review, PROMISING, SELECTED, REJECTED, Integration, or Archive.
