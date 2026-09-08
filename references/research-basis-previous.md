# Historical research basis for 0.2.0

Historical provenance only, not current execution instructions. Not reverified wholesale in 0.4.0.

Reviewed on 2026-09-07. These are provenance notes, not extra operational instructions. The upstream pages were inspected through live web retrieval. Commit SHAs were not resolved in this environment; these links are moving branches, not reproducible pinned snapshots. No third-party implementation or shader code was copied into this upgrade.

## Requested sources and selective adoption

| Source | Inspected material | Adopted | Deliberately not adopted |
|---|---|---|---|
| wshobson/agents: godot-gdscript-patterns | Skill entry and detailed patterns | Typed, scene-owned GDScript; signals; Resources; selective state machines, components, and pools | A compulsory architecture, global event bus, encrypted save manager, or every example pasted into each project |
| godot-fun/godot-agent | AGENTS.md and asset-processing skill overview | Real runtime asset integration; preserve originals; sprite/audio processing only as needed | The zfoo framework, project-specific naming rules, mandatory trailing `pass`, API-key services, and wholesale directory replacement |
| AlbusChen/GameForge-Harness | Architecture, evaluation index, security | Solver freedom, exact final artifact, separate evaluator when available, engine/input/log evidence, failure attribution | Mandatory harness installation, a fixed tool itinerary, simulated independence, or treating a disposable folder as a sandbox |
| sumo91/mission-brief | mission-brief and mission-align | Outcome/success/evidence/boundaries; one authority source; scoped delegation; distinguish discussion from adopted instructions | A required multi-skill ceremony, standalone brief-only endpoint, or asking again for already delegated choices |
| DietrichGebert/ponytail | Skill body | Need check; reuse; native/stdlib first; no speculative abstractions; root-cause fixes | Every-response activation, shortest-code extremism, automatic scope reduction, or sacrificing required quality/safety |
| Godot Shaders | License page and an actual 2D dissolve shader post | Effect-driven code search, per-post license/provenance, version/renderer/dependency checks, actual runtime integration | Treating preview images/assets as licensed with the code, copying uninspected snippets, or claiming tested compatibility from a screenshot |
| User-provided skill/prompt audit article | Full supplied text | Short specific description, progressive disclosure, proportional repo reading/testing, clear decision boundaries and completion | Claims that a named model inherently guarantees judgment, autonomy, testing, or game quality |

## Primary-source pointers

- Pattern entry: https://github.com/wshobson/agents/blob/main/plugins/game-development/skills/godot-gdscript-patterns/SKILL.md
- Pattern detail: https://raw.githubusercontent.com/wshobson/agents/main/plugins/game-development/skills/godot-gdscript-patterns/references/details.md
- Godot agent: https://github.com/godot-fun/godot-agent
- Agent conventions: https://raw.githubusercontent.com/godot-fun/godot-agent/main/AGENTS.md
- Asset-processing overview: https://raw.githubusercontent.com/godot-fun/godot-agent/main/.cursor/skills/README.md
- GameForge architecture: https://raw.githubusercontent.com/AlbusChen/GameForge-Harness/main/docs/architecture.md
- GameForge evaluation index: https://raw.githubusercontent.com/AlbusChen/GameForge-Harness/main/docs/harness-evaluation-index.md
- GameForge security: https://raw.githubusercontent.com/AlbusChen/GameForge-Harness/main/docs/security.md
- Mission brief: https://raw.githubusercontent.com/sumo91/mission-brief/main/mission-brief/SKILL.md
- Mission alignment: https://raw.githubusercontent.com/sumo91/mission-brief/main/mission-align/SKILL.md
- Ponytail: https://raw.githubusercontent.com/DietrichGebert/ponytail/main/skills/ponytail/SKILL.md
- Shader license: https://godotshaders.com/license/
- Inspected shader example: https://godotshaders.com/shader/2d-dissolve-with-burn-edge/
- Official CanvasItem shader documentation inspected as an example: https://docs.godotengine.org/en/4.6/tutorials/shaders/shader_reference/canvas_item_shader.html
- Official screen-reading shader documentation: https://docs.godotengine.org/en/4.6/tutorials/shaders/screen-reading_shaders.html
- Official skill-building guidance: https://developers.openai.com/plugins/build/skills.md

The Godot documentation version above records the page inspected, not a requirement to upgrade projects to that version. Check the actual project's version when implementing. The dissolve post was a concrete source-inspection example, not a bundled or engine-tested shader.

## Inherited work

Version 0.1.0 supplied the existing-project discipline, optional starter, game-rule ownership, replayable experiments, saves, asset provenance, evidence levels, and designer/novice/publisher perspectives. Those useful mechanisms are retained conditionally. Its mandatory human gates, capability promotion prerequisites, full-document initialization, and fixed repair cutoff are replaced by the current brief and completion rules. Older source lists were not reverified wholesale and are not presented as current findings.
