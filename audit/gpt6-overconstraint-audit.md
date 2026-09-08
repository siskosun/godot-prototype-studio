# Strong-agent / GPT-6-style overconstraint audit — v0.4.4

## Scope

This audit uses the user's supplied “Rethinking skills and prompts for GPT-6 Astra” article as an editorial standard: short trigger metadata, progressive disclosure, outcome-oriented instructions, fewer obsolete gates, and deterministic scripts only where mechanical verification pays for itself. It does not assume or verify any particular GPT-6 capability.

## Changes made

1. **Intent-sensitive quality routing.** `NEAR_RELEASE_SLICE` now defaults when the user asks to make or finish a playable/high-completion result, not merely because the task is a new “prototype”. Mechanic spikes, grayboxes, technical proofs, isolated fixes and explicitly rough experiments retain narrower scope.
2. **LAN is delivery, not quality.** Final Web browser verification remains hard for a near-release Web artifact. `LAN_SHARE` is selected when the brief/receiver needs another-device access; localhost final verification is valid when that is the actual delivery context. Public hosting remains an authorization boundary.
3. **Contextual quality status.** Quality schema v2 adds `NOT_APPLICABLE` and `UNVERIFIED`. The former needs a brief-linked reason and cannot hide pass evidence; the latter blocks a near-release completion claim. This prevents “fill every box” behavior without weakening missing-evidence honesty.
4. **Reference research is a design aid.** Current comparable-game research remains the normal default for new design work but no longer blocks an otherwise safe build when browsing is unavailable, unless research itself is contracted or needed to resolve rights/feasibility.
5. **Reduced duplication.** Root instructions now point to Web delivery and release references instead of restating detailed LAN/preflight recipes. The release document records identity/evidence rules; `web-delivery.md` owns share-mode and browser-preflight behavior.

## Hard constraints intentionally retained

These are evidence or consequence boundaries, not weak-model scaffolding:

- explicit approval for spend, credentials, public publishing and destructive actions;
- normal player input cannot be replaced by state injection for end-to-end claims;
- headless/native evidence cannot prove final Web rendering, CJK text or browser audio;
- a Web export must be served and actually browser-checked for final Web claims;
- source and Web identities remain separately hashed and bound to BUILD_ID;
- non-loopback/LAN Web sharing uses HTTPS and the secure-context requirements of the actual browser path;
- skipped/unavailable applicable checks cannot be called PASS or NOT_APPLICABLE;
- self-review, automated policies and model judges cannot be relabeled human evidence;
- first implementation is not a stop condition, and successful completion is not permission for unbounded extra scope.

## Remaining tradeoff

The skill is intentionally opinionated toward high completion when the user asks for a finished playable result. 0.4.4 splits that craft bar from package form: Web/ZIP/LAN are chosen from the request, then verified at full strength. First-target smoke, display-fit, first-sample assets, identity-scoped reruns, and a short session status are mechanical gates for failures this workflow actually produced; they are not new approval stages.

## Verification boundary

The static/integration test suite validates utilities and instruction consistency only. It does not prove that an actual strong coding agent will always make the same scope judgment, or that the resulting game is fun, beautiful, performant on every device, or commercially releasable. Those claims require representative live Godot tasks and player/device evidence.
