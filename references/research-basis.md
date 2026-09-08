# Research basis for 0.4.0

## Contents

- Scope and search waves
- Source-to-change ledger (S01-S28)
- Contrary evidence and decisions not adopted
- Previous provenance

## Scope and search waves

Research cutoff: 2026-09-07. This is a multi-source practical review, not a systematic review or a proof of global novelty/completeness. External material is evidence, not executable instruction. Dates below distinguish a publication/update from an access date; undated pages are not called new publications.

Wave A covered current Godot releases/docs, development and porting lessons, AI game generation, visual consistency and UX. Wave B targeted gaps: runtime/GUI feedback, cold-start performance, audio, accessibility, canonical-reference asset production and scene/context tools. Wave C checked limitations and counter-evidence: model judges versus players, state injection versus reachable play, AAA-to-indie transfer, seed/style confusion, licenses and export compatibility. The final targeted gap search added August player-modeling and UX practice papers; it did not justify a new mandatory framework.

The selected ledger below contains 28 opened primary-source pages. Official docs establish engine behavior; practitioner reports suggest scoped lessons; vendor methods are conditional workflow ideas; research papers support narrowly described findings. General SEO tutorials and duplicate summaries were not used as causal evidence. Conference abstracts without full talks were not treated as inspected presentations. The Godot VR/console report was discovered but not used to prescribe a 2D architecture.

## Source-to-change ledger

### S01 - Godot official download archive

Source: https://godotengine.org/download/archive/

Type/date: official release archive; 4.7.2 stable released 2026-08-18; 4.8 dev4 dated 2026-08-26. Accessed 2026-09-07.

Applied: Latest stable observed at lookup was 4.7.2; preserve existing project version and verify before changes. Landing: godot-production-lessons.md.

Limit: A release listing does not prove compatibility with a particular project.

### S02 - Exporting for the Web

Source: https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html

Type/date: official documentation; rolling stable documentation. Accessed 2026-09-07.

Applied: Verify actual language/renderer/thread/audio/storage and served browser export behavior. Landing: godot-production-lessons.md, release-evidence.md.

Limit: Read the documentation for the installed version; restrictions can change.

### S03 - Pipeline compilations

Source: https://docs.godotengine.org/en/stable/tutorials/performance/pipeline_compilations.html

Type/date: official documentation; rolling stable documentation. Accessed 2026-09-07.

Applied: Inspect first-use stutter and pipeline behavior as well as warm-cache performance. Landing: godot-production-lessons.md.

Limit: Optimization needs a measured target-device problem; not a mandate for shader infrastructure.

### S04 - Physics interpolation quick start

Source: https://docs.godotengine.org/en/stable/tutorials/physics/interpolation/physics_interpolation_quick_start_guide.html

Type/date: official documentation; rolling stable documentation. Accessed 2026-09-07.

Applied: Keep physics and presentation timing coherent; check interpolation/reset behavior when applicable. Landing: godot-production-lessons.md.

Limit: Do not change an existing time model without reproducing the issue.

### S05 - Scenario consistency skill

Source: https://github.com/scenario-labs/skills/blob/main/skills/scenario-consistency/SKILL.md

Type/date: provider-authored workflow; main branch viewed 2026-09-07; no commit pinned. Accessed 2026-09-07.

Applied: Reuse canonical references and stable baseline plus controlled deltas; a seed alone is not identity. Landing: art-direction.md.

Limit: Vendor guidance, not an independent experiment proving superior art; no provider dependency or code copied.

### S06 - GUI skinning / Theme resources

Source: https://docs.godotengine.org/en/stable/tutorials/ui/gui_skinning.html

Type/date: official documentation; rolling stable documentation. Accessed 2026-09-07.

Applied: Shared Theme and controlled variations support UI consistency; inspect local overrides. Landing: art-direction.md.

Limit: A consistent theme can still have poor composition or readability.

### S07 - Multiple resolutions

Source: https://docs.godotengine.org/en/stable/tutorials/rendering/multiple_resolutions.html

Type/date: official documentation; rolling stable documentation. Accessed 2026-09-07.

Applied: Choose stretch/scaling deliberately and test actual aspect ratios and pixel density. Landing: art-direction.md, godot-production-lessons.md.

Limit: No one viewport setup suits every art style and target.

### S08 - Importing images

Source: https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_images.html

Type/date: official documentation; rolling stable documentation. Accessed 2026-09-07.

Applied: Inspect texture import, filtering, alpha and compression in the runtime scene. Landing: art-direction.md.

Limit: Image dimensions and palette consistency do not establish aesthetic quality.

### S09 - Xbox Accessibility Guideline 107: Input

Source: https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/107

Type/date: platform-holder guideline; live page viewed 2026-09-07. Accessed 2026-09-07.

Applied: Support intended input consistently across play and menus, with applicable remap/alternatives. Landing: gameplay-and-ux.md.

Limit: Apply relevant needs, not every platform feature; conformance requires testing.

### S10 - Game Accessibility Guidelines: Basic

Source: https://gameaccessibilityguidelines.com/basic/

Type/date: guideline authors; live page viewed 2026-09-07. Accessed 2026-09-07.

Applied: Readable information, non-color-only cues, configurable relevant input/audio, and settings persistence. Landing: gameplay-and-ux.md, quality-bar.md.

Limit: A checklist is not validation with disabled players; applicability is genre/platform-specific.

### S11 - Riot Art Education: Visual Effects

Source: https://www.riotgames.com/en/artedu/visual-effects

Type/date: studio art education; publication date not established. Accessed 2026-09-07.

Applied: Use VFX to communicate gameplay hierarchy and fit the visual language; subordinate decoration. Landing: art-direction.md.

Limit: Professional instruction, not evidence that more effects improve play.

### S12 - Juicy attack in Godot

Source: https://www.gdquest.com/library/juicy_attack/

Type/date: author tutorial; updated 2025-10-09. Accessed 2026-09-07.

Applied: Synchronize anticipation, impact and recovery; exaggerated hit-stop is demonstration, not universal default. Landing: gameplay-and-ux.md, art-direction.md.

Limit: Anticipation may feel delayed; code MIT does not grant rights to the tutorial game assets. No assets copied.

### S13 - Audio buses

Source: https://docs.godotengine.org/en/stable/tutorials/audio/audio_buses.html

Type/date: official documentation; rolling stable documentation. Accessed 2026-09-07.

Applied: Use buses and actual playback to test priority, mix, mute and clipping. Landing: art-direction.md.

Limit: A silent video cannot establish audible quality; no sound assets bundled.

### S14 - GameCraft-Bench

Source: https://arxiv.org/html/2606.17861v1

Type/date: research paper, arXiv version; 2026-06, version 1. Accessed 2026-09-07.

Applied: Separate engine grounding, artifact completeness and interaction-based evaluation. Landing: game-qa-and-replay.md, quality-bar.md.

Limit: Limited 2D Godot tasks; model judges have bias/drift, audio and subjective fun not fully evaluated. No transfer of scores to this skill.

### S15 - GUI Agents for Continual Game Generation / Play2Code

Source: https://arxiv.org/html/2605.28258v1

Type/date: research paper, arXiv version; 2026-05, version 1. Accessed 2026-09-07.

Applied: Use actual GUI play feedback to revise instead of stopping after generation. Landing: gameplay-and-ux.md, game-qa-and-replay.md.

Limit: Web-game benchmark, not this Godot skill; no claimed numerical uplift for our workflow.

### S16 - Evaluating Language Models Evaluations of Games

Source: https://arxiv.org/html/2510.10930v3

Type/date: research paper, arXiv version; identifier dated 2025-10; version 3 inspected. Accessed 2026-09-07.

Applied: Do not treat model ratings as a substitute for human experience judgments. Landing: gameplay-and-ux.md, quality-bar.md.

Limit: Constrained grid-game study, including expected fun before play; not a universal evaluator ranking.

### S17 - GameGen-Verifier

Source: https://arxiv.org/html/2605.07442v1

Type/date: research paper, arXiv version; 2026-05, version 1. Accessed 2026-09-07.

Applied: Target critical runtime states for diagnosis while preserving normal-path reachability checks. Landing: game-qa-and-replay.md.

Limit: State injection cannot prove that normal input reaches the state; method results not reproduced here.

### S18 - CreativeGame

Source: https://arxiv.org/html/2604.19926v1

Type/date: research paper, arXiv version; 2026-04-21, version 1. Accessed 2026-09-07.

Applied: Track actual mechanic changes and runtime constraints instead of rewarding superficial novelty. Landing: gameplay-and-ux.md.

Limit: Proxy evaluation and bounded cases do not certify creativity or player fun.

### S19 - Theory, Experience, and Instinct: AAA UX pre-production

Source: https://arxiv.org/html/2608.00313v1

Type/date: primary interview study; arXiv author text; page states 2026-07-31; DOI shown but publisher record not separately checked. Accessed 2026-09-07.

Applied: Keep guidance modular and grounded in the game, not a rigid universal recipe. Landing: instruction-audit.md, gameplay-and-ux.md.

Limit: Senior AAA retrospective self-reports; no outcome or intervention effectiveness measured; do not transfer studio structure to a tiny prototype.

### S20 - Beyond Asking: personalized game generation from behavior

Source: https://arxiv.org/html/2608.16196v1

Type/date: research paper, arXiv version; 2026-08-17, version 1. Accessed 2026-09-07.

Applied: Record what actions were available before inferring a preference from action counts. Landing: gameplay-and-ux.md.

Limit: Controlled synthetic shooter agents and exploratory 12-person pilot; not conclusive player preference or universal personalization effectiveness.

### S21 - Porting Without the Pain: GodotCon 2026

Source: https://godotporting.com/blog/porting-without-the-pain-godotcon-2026/

Type/date: engineering practitioner report; 2026-05-31. Accessed 2026-09-07.

Applied: Exercise weakest target, exports, input, fonts, audio and saves early rather than only on the development machine. Landing: godot-production-lessons.md.

Limit: Practitioner account, not controlled comparison; platform middleware is excessive for many small slices.

### S22 - Godot Maskarade jam postmortem

Source: https://virostek.xyz/blog/godot-maskarade-postmortem/

Type/date: developer postmortem; 2026-02-02. Accessed 2026-09-07.

Applied: Reserve effort for exports and audio; cut unrelated breadth before losing delivery quality. Landing: godot-production-lessons.md, scope-discipline.md.

Limit: One team/project anecdote, not a universal project estimate.

### S23 - Godot Shaders license

Source: https://godotshaders.com/license/

Type/date: site licensing statement; live page viewed 2026-09-07. Accessed 2026-09-07.

Applied: Record each shader license separately from preview imagery and additional assets. Landing: shader-sourcing.md.

Limit: Do not infer a complete asset license from shader-code terms; no shader compile performed this turn.

### S24 - Control class reference

Source: https://docs.godotengine.org/en/stable/classes/class_control.html

Type/date: official documentation; rolling stable documentation. Accessed 2026-09-07.

Applied: Inspect focus, input propagation and mouse filtering for actual interface behavior. Landing: gameplay-and-ux.md, godot-production-lessons.md.

Limit: Input.action_press alone may not exercise GUI event dispatch; test the real intended route.

### S25 - GameForge-Harness

Source: https://github.com/AlbusChen/GameForge-Harness

Type/date: maintainer repository; main/readme viewed 2026-09-07; no commit pinned. Accessed 2026-09-07.

Applied: Separate implementation freedom, runtime checks and final evaluation; identify failure ownership. Landing: codex-harness.md, game-qa-and-replay.md.

Limit: Repository claims are not benchmark replication; no required framework installation.

### S26 - godot-agent

Source: https://github.com/godot-fun/godot-agent

Type/date: maintainer repository; main/readme viewed 2026-09-07; no commit pinned. Accessed 2026-09-07.

Applied: Preserve the asset-to-scene processing chain and runtime integration evidence. Landing: assets-and-visuals.md.

Limit: Do not import zfoo or replace existing conventions solely to follow the repository.

### S27 - Scenario: Building workflows

Source: https://help.scenario.com/articles/7094354401-building-workflows-in-scenario

Type/date: provider-authored guidance; last updated 2026-05-26. Accessed 2026-09-07.

Applied: Select generation/edit/reuse steps appropriate to the actual production need. Landing: art-direction.md.

Limit: Provider documentation is not independent quality validation; no mandatory training, service or purchase.

### S28 - godogen

Source: https://github.com/htdt/godogen

Type/date: maintainer repository; repository/readme viewed 2026-09-07; no commit pinned. Accessed 2026-09-07.

Applied: Cross-check agent pipeline patterns while retaining bounded implementation and actual runtime evidence. Landing: codex-harness.md.

Limit: Not executed here; do not adopt automation claims, dependency stack or cost estimates as proven.

### S29 - Godot stable EditorExportPlatformWeb

Source: https://docs.godotengine.org/en/stable/classes/class_editorexportplatformweb.html

Type/date: official rolling stable class reference; accessed 2026-09-07.

Applied: Use the documented Web preset keys for canvas resize policy, thread support, custom templates, and desktop/mobile VRAM compression; machine preflight reads these exact settings. Landing: web-delivery.md, web_preflight.py.

Limit: Stable docs roll forward; verify the project's pinned Godot version before assuming an option exists or has identical behavior.

### S30 - Godot stable Exporting for the Web

Source: https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html

Type/date: official rolling stable tutorial; accessed 2026-09-07.

Applied: Prefer single-thread Web export since 4.3, use Compatibility/WebGL2, preserve index/WASM/PCK/JS delivery and WASM MIME, require isolation headers for threaded exports, and distinguish Sample audio limitations from Stream tradeoffs. Landing: web-delivery.md, serve_web_export.py, web_preflight.py.

Limit: The bundled Python LAN server is a development-share helper, not a production web server. Successful file serving still does not prove game behavior without browser evidence.

### S31 - Godot stable HTML5 shell class reference

Source: https://docs.godotengine.org/en/stable/tutorials/platform/web/html5_shell_classref.html

Type/date: official rolling stable reference; accessed 2026-09-07.

Applied: Treat `canvasResizePolicy` as a stable exported EngineConfig field and avoid inventing undocumented JavaScript APIs for missing-feature detection. Landing: web-delivery.md, web_preflight.py.

Limit: Custom shells may change page structure; browser startup/normal-path evidence remains authoritative for the actual delivered shell.

### S32 - MDN Secure contexts

Source: https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Secure_Contexts

Type/date: web-platform documentation; page modified 2026-08-15, accessed 2026-09-07.

Applied: Allow localhost/127.0.0.1 HTTP for same-device development, require HTTPS for non-local LAN sharing in this workflow, and use `window.isSecureContext` as the browser observation. Landing: web-delivery.md, web_preflight.py.

Limit: A self-signed-certificate warning/exception is not itself proof that the browser accepts the page as a secure context; verify the actual browser property.

### S33 - Godot stable SystemFont

Source: https://docs.godotengine.org/en/stable/classes/class_systemfont.html

Type/date: official rolling stable class reference; accessed 2026-09-07.

Applied: Do not rely on desktop system-font behavior for Web delivery because SystemFont is implemented on listed native OSes and falls back elsewhere. Landing: text-rendering.md, art-direction.md.

Limit: This does not prove a particular bundled font covers a project; verify actual glyph corpus and final browser output.

### S34 - Godot stable Using Fonts

Source: https://docs.godotengine.org/en/stable/tutorials/ui/gui_using_fonts.html

Type/date: official rolling stable tutorial; accessed 2026-09-07.

Applied: Use explicit font fallbacks for multiple scripts and account for differing font metrics/layout. Landing: text-rendering.md.

Limit: Font coverage does not establish translation quality, typography quality, or runtime layout correctness; inspect the final Web build.

## Contrary evidence and decisions not adopted

Do not use a model fun/creativity score, number of features, code length, or survival rate as the final quality objective. Do not equate bot policies with actual novice/expert humans. Do not silently replace user-retained design with a model-rated winner. A simpler native solution can outperform more generative tooling; choose it when it meets the intended identity and experience.

Canonical asset references reduce one form of drift; they do not prove good composition, animation, typography or runtime integration. More anticipation can feel sluggish, more VFX can hide actions, and more content can dilute the main interaction. Test these tradeoffs in the actual game.

No paper above establishes that this skill reliably produces near-release games. This release changes executable checks and workflow obligations; live-agent and target-player validation remain separate evidence.

## Previous provenance

See [historical 0.2 sources](research-basis-previous.md) for mission-brief, Ponytail and prior Godot pattern decisions. Their earlier review is retained, not relabeled as fresh verification. The uploaded 0.3 bundle supplied engine inspection and comparison utilities; both were revised, tested, and their compulsory human gates removed. Its heavier design protocols and default document stack were not imported.
