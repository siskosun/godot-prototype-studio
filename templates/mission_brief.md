# Mission Brief

## Outcome
[One player-facing result; identify user constraints and decisions delegated to the agent.]

## Visual Reference Intent
- Images: [List supplied image identities, or none supplied.]
- Mode: [PARTIAL_REFERENCE | PIXEL_ACCURATE_REFERENCE | ORIGINAL_DELEGATED | NOT_APPLICABLE]
- Partial scope: [For PARTIAL_REFERENCE, name the properties retained from each image; otherwise state not applicable.]
- Pixel targets: [For PIXEL_ACCURATE_REFERENCE, name each target frame/view, state, crop, viewport and backing resolution; otherwise state not applicable.]
- Rights status: [For PIXEL_ACCURATE_REFERENCE, record ownership or reproduction authorization; otherwise state not applicable.]
- Reason: [Required only for NOT_APPLICABLE.]

## Pre-development Route
- Stack constraint: [OPEN | USER_LOCKED_GODOT | USER_LOCKED_H5 | USER_LOCKED_OTHER]
- Selected route: [GODOT | H5 | OTHER]
- H5 decision: [NOT_SIMPLER | USER_SELECTED_H5 | USER_DECLINED_H5 | NOT_APPLICABLE]
- Route rationale: [Why the selected route is the cheapest adequate implementation for the same acceptance contract.]
- Reuse scan: [Path to the reuse scan or a concrete inline summary of sources checked.]
- Reuse decision: [COPY_AND_ADAPT | REFERENCE_ONLY | BUILD_NEW | CROSS_STACK_SELECTED | CROSS_STACK_DECLINED]
- Seed source: [For COPY_AND_ADAPT/CROSS_STACK_SELECTED, record source URL, pinned revision and compatible license; otherwise state none.]

## Delivery
- Quality profile: [NEAR_RELEASE_SLICE when the user asks to finish a playable/high-completion game without another fidelity target; this is craft, not a package list. Preserve mechanic spikes, quick grayboxes, technical proofs, isolated fixes, and explicitly rough experiments.]
- Target: [Choose from the request: LOCAL_PROJECT, GODOT_PROJECT_ZIP, WEB_EXPORT, DESKTOP_BUILD, ANDROID_BUILD. High completion does not imply Web or ZIP. If no package is requested, default to the tested in-place Godot project.]
- Web share: [Only when Web is a chosen target. Use LOCAL_WEB_TEST for local final browser verification, LAN_SHARE when another device needs access, and WEB_SHARE for lightweight interim sharing. Public hosting requires separate authorization.]
- Required languages/scripts: [List player-facing locales/scripts. Bundled font coverage and target-runtime text evidence are required for those scripts on the chosen deliveries.]
- Web audio: [If Web is a target: expected after a player gesture | intentionally silent.]
- Platform and input: [Exact target or declared default; preserve existing compatibility.]
- Session and presentation: [Complete play path and expected quality, not an unlimited full game.]

## Success
[Observable acceptance IDs covering relevant quality-bar dimensions; include required gameplay, recovery, presentation, and scope.]

## Evidence Required
[For each required claim, the runtime/interaction/presentation evidence that could expose failure. Separate optional human or independent review.]

## Boundaries
[Compatibility, rights, privacy, irreversible actions, performance/device constraints where material.]

## Non-goals
[Unrequested systems, content breadth, production claims, and public publishing.]

## Execution Authority
[User-retained decisions; scoped delegation; permitted reversible work; actions requiring permission. Do not label agent defaults user-approved.]

## Completion
[What supports DONE and what constitutes a genuine BLOCKED condition; no milestone approval unless requested.]
