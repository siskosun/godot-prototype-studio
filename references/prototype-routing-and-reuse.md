# Pre-development route and reuse gate

Use for a new prototype after the player-facing content is clear and before scaffolding or substantive implementation. Do not reopen an explicit user-locked stack. The goal is to choose the cheapest adequate implementation and avoid rebuilding a prototype that already exists.

## Gate 1: decide whether Godot is actually needed

Judge the route from the accepted experience, delivery target and constraints, not from this skill's name. Treat **H5** here as a browser-native prototype using HTML/CSS/JavaScript with DOM or Canvas/WebGL/WebAudio and a small amount of supporting code as needed.

H5 is a strong candidate when all material requirements can be met with substantially less work, especially when the prototype is browser-first, 2D or UI-heavy, uses simple pointer/touch/keyboard input, has a small state model, needs fast sharing, and does not benefit materially from an engine editor or native export pipeline. A tiny WebSocket/HTTP service does not by itself disqualify H5, but if server/session complexity dominates the project, do not call the route "simple H5" merely because the client is JavaScript.

Prefer Godot when the project already exists in Godot or depends materially on engine scenes/resources, physics, tilemaps, animation tooling, complex 2D composition, shaders, editor-authored content, Godot plugins, large asset pipelines, or native/multi-platform exports. Prefer the user-locked technology when changing it would violate a retained decision or integration constraint.

Compare routes on the **same acceptance contract**:

- complete player path and interaction model;
- target devices, input and browser/native requirements;
- networking/session needs;
- visual/animation/physics complexity;
- asset/content production burden;
- test and delivery friction;
- expected amount of custom infrastructure.

If H5 is materially faster/simpler with no important acceptance loss and the stack is not user-locked, ask one explicit question before formal development: recommend H5, state the concrete reason and tradeoff, and ask whether to switch. Do not silently switch. If the user declines, continue Godot without repeatedly reopening the choice. If the user chooses H5, stop creating Godot-specific scaffolding and route to an H5/browser implementation workflow when available; preserve the same brief and evidence boundaries.

Record the resolved route in the brief's `Pre-development Route` section. `H5_CANDIDATE` or another unresolved offer is not authority to start the full implementation.

## Gate 2: search for reusable prototype code before building

After the stack choice is resolved and before substantive custom code, search for public source that already implements the same interaction or state model. Search by player verbs, information, viewpoint, input, session/social relationship and state transitions rather than by theme alone.

Search in this order while results can still change the implementation decision:

1. User-provided repositories, prior project links and known internal/local prototypes.
2. Current GPT-6/Astra game indexes, especially `MartinDelophy/awesome-gpt-6-astra`, then follow each promising entry to the original author/repository. Treat community lists as discovery indexes, not proof of quality, model attribution, license or source availability.
3. GitHub/GitLab and other open-source hosts using mechanic + stack terms such as `Godot`, `GDScript`, `HTML`, `Canvas`, `Three.js`, `WebSocket`, `multiplayer`, plus `GPT-6`, `Astra` when relevant.
4. Godot demos/Asset Library or other engine/community examples when they reduce implementation risk without importing unrelated product scope.

Use current web/GitHub connectors when available. If external search is unavailable after trying authorized alternatives, record the gap and proceed from user/local/known sources unless reuse research itself is an explicit deliverable; do not fabricate a negative search result.

Prefer direct source, an identifiable revision, a compatible license and a runnable baseline. A video, hosted game or README without source can inspire behavior but cannot be copied as code. Unknown or incompatible licensing means **REFERENCE_ONLY**, not reuse. Verify the original repository/author rather than trusting an aggregator's label.

For each serious candidate record only decision-relevant facts: source URL, revision/tag, stack, license, core-loop/state-model similarity, input/viewpoint, networking model if any, delivery target, important dependencies, whether it runs, and what would still need to change. Do not rank by stars or model branding.

### Reuse decisions

- **COPY_AND_ADAPT** — a very close same-stack source exists, is legally reusable, and is cheaper/safer than rebuilding. Copy/clone a pinned revision into a fresh working directory before editing; retain license/NOTICE and upstream provenance. Run the unmodified baseline first, then make the smallest adaptation that satisfies the brief. Do not edit an upstream checkout in place.
- **REFERENCE_ONLY** — useful behavior/architecture exists but source, license, quality or similarity is insufficient for wholesale reuse. Extract principles or small compatible patterns only.
- **BUILD_NEW** — no candidate materially reduces work or risk. Record the search gap and proceed without continuing an unbounded hunt.
- **CROSS_STACK_OFFER** — an extremely similar reusable project exists in another stack and would materially reduce work. Explain the evidence and ask once whether the user wants to change stack. If declined, keep the selected stack and use the candidate as a behavior/reference baseline; do not mechanically transliterate the whole codebase.

Use `templates/reuse_scan.md` when the search affects the implementation route. Keep it as research evidence, not a second acceptance contract.

## Copy safely

Before executing external code, inspect its license, dependency manifests, setup scripts, network calls and obvious secret/credential requirements. Prefer a disposable copy and a pinned commit/archive. Do not run install/post-install hooks merely to inspect source. Preserve required attribution. Remove unrelated analytics, credentials, deployment configuration and product-specific services before adapting them.

After copying, establish a baseline with the candidate's documented route. If the baseline does not actually run or the relevant mechanic is absent, downgrade the reuse decision instead of forcing the project to fit the source.

Astra provenance is useful for finding examples of strong-agent workflows; it is not evidence that the code is correct, maintainable, original or appropriate for this project.
