# Brief and delegated authority

## One contract, before implementation

Use `templates/mission_brief.md` for a new prototype or substantial redesign; write a short inline equivalent for a small change. Recover user decisions and the relevant project baseline first. Research may inform the design before implementation; it does not make a reference game authoritative.

When the user asks for a finished playable game, high-completion prototype, or release-like slice and gives no fidelity target, use NEAR_RELEASE_SLICE and concretize quality-bar.md. That profile is the craft bar, not a delivery bundle. A mechanic spike, quick graybox, technical proof, isolated fix, or explicitly rough experiment does not inherit the full bar merely because it is a new project. The brief states the outcome, observable success, falsifying evidence, hard boundaries, non-goals, and authority. Record quality profile, chosen runtime/package targets, and the evidence those targets need as three separate decisions. Do not prescribe architecture or a tool itinerary. Preserve an existing contract instead of replacing it with this template.

A design document explains *how the game works*. The brief explains *what this delivery must achieve*. Acceptance lives only in the brief; the design links to it. Mark statements as user constraints, observed project facts, or agent choices within delegated scope. Do not turn discussion examples or discarded ideas into obligations.

## Align without unnecessary interruption

For a request to refine an idea and implement it, make a recommended complete design within that idea. Choose reversible details such as layout, tuning, a fitting original visual style, and an unspecified local package format. State the main defaults and continue. Do not call those choices user-approved.

Ask at most three coupled questions only when the answers materially change the promised result and are neither discoverable nor delegated. Examples: mutually inconsistent required platforms; a retained art choice; an essential paid server lacking authorization. Complete useful branch-independent work while a real decision is pending. An explicit 'show the brief and wait' overrides autonomous continuation.

If no package form is specified, keep the tested in-place Godot project. Add a source ZIP, Web export, desktop/Android build, or LAN share only when the request asks for that runtime, receiver, or handoff. When Web is chosen, verify it in an actual served browser path and pick LOCAL_WEB_TEST or LAN_SHARE from the receiver context; LAN is not implied by near-release quality. Do not infer public web deployment, account upload, Android signing, or store release.

## Authority boundary

| Action | Default treatment |
|---|---|
| Reversible local edits, permitted tests, scenario runs, capture, fixes | Proceed |
| Delegated game design, coherent art direction, tuning inside the promise | Decide, record, proceed |
| Public reference lookup or licensed local asset acquisition without secrets/spend | Proceed within available network permissions; inspect before execution |
| Tool/environment setup | Use existing tools first; local setup only within current permissions and policy |
| Changing audience, core promise, reserved decisions, or contracted platform | Needs authorization unless explicitly delegated |
| Spending, credentials, publishing, destructive migration, production promotion | Needs specific authorization |
| Independent review or human fun testing | Required only when specified; otherwise disclose its absence |

Do not request approval merely because alternatives exist. Do not use 'continue until done' to bypass safety, license, or privacy boundaries. A lower-fidelity fallback must preserve the contracted experience; a change that weakens success requires authorization.

## Brief amendment

Keep scope stable while implementation changes freely. Update delegated details without asking; preserve the reason in progress when consequential. Amend acceptance only for a user-authorized change or an explicitly delegated tradeoff, never solely because a test failed. Link expensive research rather than repeating it.

`validate_mission_brief.py` checks structure and unresolved fields. It cannot establish that the user authorized a choice or that the design is good.
