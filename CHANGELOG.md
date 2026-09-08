# Changelog

## 0.5.0 - 2026-09-08

- Added one-time visual-reference intake for new prototypes and material visual redesigns. Missing images prompt for 1-3 references plus `PARTIAL_REFERENCE` or `PIXEL_ACCURATE_REFERENCE`; existing images prompt only for how they should be used; an already answered mode is never reopened.
- Defined `ORIGINAL_DELEGATED` and `NOT_APPLICABLE` paths so the intake does not stall original-art delegation or genuinely visual-irrelevant diagnostic work.
- Added frame-, viewport-, crop-, asset/font-, allowed-difference-, and rights-bound requirements for pixel-accurate targets.
- Added a novel-gameplay protocol: player-facing causal thesis, familiar anchor plus one design delta, theme-removal test, falsifier, decision trace, counterfactual choice, dominant/spam/wait probes, and recovery checks.
- Added an optional `templates/mechanic_lab.md` and `init_workspace.py --novel-gameplay`; the mission brief remains the single acceptance contract.
- Added authoritative-observability guidance so strong agents can reproduce, inspect state/screenshots, trace owning rules, modify, and rerun through real input.
- Preserved 0.4.4's completion/delivery/evidence split, early first-target smoke, Web display-fit checks, first-sample asset checks, change-impact/package tooling, and resumable session status.
- Updated English/Chinese README and added 0.5.0 regression tests while keeping legacy mission briefs valid.

## 0.4.4 - 2026-09-08

- Split completion, delivery, and evidence: NEAR_RELEASE_SLICE is a craft bar, not an automatic source-ZIP-plus-Web bundle.
- Require an early first-target smoke (one character, required-language text, one button, one sound) before a complete level exists.
- Web preflight now fails a postage-stamp CSS canvas, clipped view, or unclickable primary control even when the backing-pixel budget passes.
- Added `package_and_report.py` and `change_impact.py` so freeze/hash/ZIP/report and suite reuse share one entry; visual PASS stays a real review.
- First generated sample must pass real-alpha / pivot inspection before batching; baked checkerboards fail; chroma-key is an explicit fallback only.
- Session status is the resume surface: version, hashes, passed checks, open issues, commands, next step.

## 0.4.3 - 2026-09-07

- Re-audited the skill for stronger-agent/GPT-6-style instruction economy: keep outcome and evidence boundaries hard, move judgment-heavy routing back to the agent.
- Made NEAR_RELEASE_SLICE intent-sensitive: it defaults for requests to finish a playable/high-completion game, not merely because the task is a new “prototype”.
- Decoupled near-release Web quality from LAN delivery. Final Web browser verification remains mandatory; LAN_SHARE is enforced only when the brief selects it.
- Added quality-review schema v2 with PASS, FAIL, UNVERIFIED and NOT_APPLICABLE. Inapplicable requirements need a brief-linked rationale; unavailable evidence cannot masquerade as N/A.
- Downgraded current comparable-game research from a universal DONE dependency to a default design aid, except when research is explicitly contracted or needed to resolve rights/feasibility.
- Reduced duplicated Web/release instructions and updated behavioral tests for local final browser verification and contextual applicability.

## 0.4.2 - 2026-09-07

- Added separate LOCAL_WEB_TEST, WEB_SHARE, LAN_SHARE and NEAR_RELEASE delivery paths; lightweight Web sharing no longer requires final-release paperwork.
- Added deterministic Web BUILD_ID stamping, a bundled LAN HTTPS server, and browser/file/HTTP WEB_PREFLIGHT with root/MIME/payload checks.
- Made near-release Web delivery inspect the actual Web export preset, require a backing-canvas pixel budget, LAN HTTPS, browser startup/normal input, text rendering, and post-gesture audio when promised.
- Added explicit thread/mobile-VRAM gates; COOP/COEP is required for threaded/isolation-dependent exports instead of being imposed on every single-thread build.
- Added text-rendering integrity and automatic repair guidance for CJK/localized glyphs, layout and bundled Web fonts; unresolved player-facing text corruption blocks DONE.
- Split source and Web artifact identities, bound browser evidence to the served BUILD_ID, and require near-release Web records to pair the separately hashed source; source ZIP/pairs containing generated `export/web` are rejected to prevent mixed identities.
- Hardened final release schema to require declared Web audio/thread expectations and an audio hard gate when audio is promised.
- Added second-computer LAN handoff guidance for certificate trust, secure-context verification, firewall, same-network access, cache refresh and native fallback disclosure.
- Added Web delivery regression/integration tests, including a real local HTTPS fixture and certificate SAN validation; fixed BUILD_ID restamping drift found by those tests.

## 0.4.1 - 2026-09-07

- Made a tested Web export a default final artifact for complete new-game / NEAR_RELEASE_SLICE work, alongside the editable Godot project ZIP.
- Require serving the Web build over HTTP and exercising the normal browser play/recovery path; generated Web files alone do not satisfy DONE.
- Keep public hosting/deployment outside default authority; hand off the Web package with exact local serve instructions unless separately authorized.
- Bind player-facing near-release review to the Web artifact while preserving separate source ZIP/tree identity and traceability.
- Treat an unresolved required Web-export incompatibility as a real completion blocker after safe supported alternatives are exhausted.

## 0.4.0 - 2026-09-07

- Raised the complete-new-game default to a bounded NEAR_RELEASE_SLICE, preserving probe/bugfix scope.
- Retained brief delegation and DONE/BLOCKED; no first-implementation or taste-default stop.
- Added integrated art-quality exemplar, canonical-reference production, UI/theme, motion/audio and runtime composition reviews.
- Added genre-sensitive gameplay/UX repair, opportunity-aware diagnostics and shared-baseline variants.
- Distilled uploaded 0.3 engine context, risk QA, exploratory testing, replay and automated-policy methods without its document/approval stack.
- Added image/alpha/pivot/contact-sheet inspection and evidence-linked final quality validation.
- Fixed scene inventory to retain instanced/inherited nodes and script references; it remains static evidence.
- Hardened comparison records against NaN/bool/missing files and unequal conditions; delegated selection is allowed.
- Bound quality review, current retests and clean delivery to the final artifact; old failure traces remain identifiable.
- Added multiwave research ledger, contrary evidence, negative utility tests and behavioral audits.
- No claim of actual account installation, Godot runtime playtesting, independent-agent evaluation or perfection.

## 0.2.0 - 2026-09-07

- Changed the default from milestone-based supervision to completing the delegated prototype or reporting a genuine blocker.
- Replaced the long entrypoint with a compact router and explicit DONE/BLOCKED boundaries.
- Added brief/delegation alignment, verified released-game comparison, and complete bounded prototype design.
- Added scope discipline and effect-driven Godot Shaders sourcing, licensing, integration, and fallback guidance.
- Selectively incorporated Godot patterns, asset-processing discipline, and final-evaluator separation without importing upstream frameworks.
- Made human playtests, detailed experiment contracts, capability tiers, and approval templates conditional rather than automatic stops.
- Reduced default workspace generation to one brief and one progress record; retained detailed compatibility templates behind an explicit option.
- Hardened engine log handling and partial-check exit codes, artifact/evidence identity, clean ZIP-to-tested-tree correspondence, and symlink/path handling.
- Added utility regression tests, behavioral scenarios, provenance notes, and an instruction audit.
- No claim of live Godot playtesting, independent agent evaluation, or account-level installation is implied by this release.

## 0.1.0 — 2026-09-04

- Created a Codex-first, Godot 4.x 2D prototype workflow derived from the strongest transferable parts of the H5 Game Prototype Agent.
- Added capability-adaptive execution tiers without transferring human design authority.
- Added prototype-question contracts, selective decision gates, Foundation Slice discipline, Godot CLI checks, experiment logs, structured playtests, release evidence binding, and three stakeholder review lenses.
- Added an optional no-dependency instrumented Godot starter and deterministic validation utilities.
- Incorporated designer review by making design pillars optional for pure technical spikes and preferring playable alternatives at taste forks.
- Incorporated novice review with agent-owned records, a plain-language creator checkpoint, one open decision frontier, and clearer recovery guidance.
- Incorporated publisher review by requiring explicit evidence-stage labeling and preventing prototype verdicts from implying production or market proof.
- Added `E5_SUPERVISED_PROGRAM` and a validated program contract so stronger future agents can sequence bounded experiments without acquiring human decision authority.
- Clarified release hashing so workflow evidence cannot change the identity of the source tree under test.
