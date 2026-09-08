# Art direction and consistent high-craft production

Use for a new visual identity, a material art pass, or a repeated asset pipeline. Build the game as a coherent designed object, not a collection of individually attractive generations. Preserve supplied identity constraints; select reversible details within delegation.

## Establish an art target the tools can actually execute

Resolve visual reference intent first. For every new prototype, follow `visual-reference-intake.md`: ask for reference images and `PARTIAL_REFERENCE` versus `PIXEL_ACCURATE_REFERENCE` when none are present; if images are already present, ask only how to use them; if the user delegates or declines images, record `ORIGINAL_DELEGATED`. Never repeat a resolved intake question.

Translate the player promise into a specific visual language: shape/silhouette, composition and focal hierarchy, palette roles, value separation, camera/perspective, scale/pixel density, light/material rules, typography and UI geometry, animation rhythm, and sound character. Distinguish a deliberately simple style from raw debugging shapes. Do not silently substitute geometric placeholders for a requested character-led illustrated game.

Choose a small set of actual reference images and one canonical character/asset sheet. For `PARTIAL_REFERENCE`, state exactly which properties each image controls and make everything else original. For `PIXEL_ACCURATE_REFERENCE`, record the target frame/state, crop, viewport/backing resolution, rights, required assets/fonts, and allowed renderer differences; compare captured runtime output rather than merely imitating the style. Do not copy a competitor's protected identity or combine incompatible styles. For complex production use `templates/visual_canon.json`; otherwise keep these decisions in the blueprint. Record agent-selected versus user-retained choices accurately.

Create one **in-engine quality exemplar**: hero/primary object, representative background, key UI, action effect, transition and audio. Judge it at actual play size and in motion before generating the rest. The exemplar is a repeatable visual target, not a new approval gate. A concept painting or contact sheet cannot satisfy the live exemplar.

Before multiplying a generated series, inspect **one** sample with `inspect_asset_set.py` and a live scene placement. Require real alpha (not a painted checkerboard or a prompt that says "transparent PNG"), a foot/contact pivot, intended in-engine scale, correct occlusion, and a readable action pose. Only then generate siblings from the same anchors. A chroma-key/green-screen plate is a fallback after that sample fails real alpha, and only with an explicit `chromaKey` color; it is not the default production path.

## Generate around one stable anchor

Prefer reuse, authored edits and native procedural elements where they fit. When using generative assets, keep a stable baseline description and the same canonical source images; specify only the intended delta for a new pose/prop. Never chain each new asset to the previous generated variant as the sole reference. Seeds help reproducibility of supported generators, not cross-asset identity by themselves.

Keep master images, generation tool/model/version when observable, inputs, important parameters, output identity, and the declared role of every reference. Do not invent seed control or reference slots a tool does not expose. A custom style model is justified by repeat volume and available authorized tooling, not a mandatory dependency. Private reference uploads and paid generation retain their permission boundary.

For a pixel-accurate target, establish one canonical capture route and compare the same state at the same viewport. Use overlays or pixel diffs when available, but inspect dynamic play separately. Antialiasing, font rasterization, shader time, particles, and adaptive layout can prevent literal equality unless the environment is fixed; disclose the measured conditions rather than claiming universal pixel accuracy.

Produce one family in small inspectable batches. Compare every critical item to the canonical sheet and the live scene. Reject or edit changes in face/proportions, camera, light, outline, palette role, edge quality, or material vocabulary. Preserve pivot, transparent margins, frame order and contact points across animation frames. Avoid independently regenerated frames that boil, morph, or drift; use aligned sprite sheets, rigged parts, or native animation where these preserve the intended look.

## Cohesion is necessary; composition and craft make it good

Inspect foreground/background separation, silhouette at thumbnail size, focal point, negative space, density and readable hierarchy during the busiest real interaction. Essential hazards must remain readable under overlays, particles, damage flashes, and alternate backgrounds. Compare quiet, action, failure and result states, not only the best frame. Check grayscale/color-independent cues where color conveys rules.

Let action importance govern effect emphasis. Deliberately subordinate decoration. Improve a weak scene by editing composition, scale, contrast, texture noise or layout before adding glow, shake or particles. Introduce limited variation within the identity rather than random palette/style changes per level. Theme consistency does not mean identical assets or uniformly loud feedback.

## Godot implementation

Use a shared Theme resource and deliberate type variations for related UI; use Containers/anchors and tested viewport scaling. Audit local theme overrides that defeat consistency. Render text in Godot rather than baking essential labels into generated illustrations. For Web delivery, bundle authorized font data for every required script and verify the effective font/fallback chain against the actual string corpus; desktop system fallback or `ThemeDB.fallback_font` is not sufficient evidence. Inspect glyphs, shaping, line height, wrapping and overflow again in the final served Web BUILD_ID. Follow [text rendering](text-rendering.md). Never redistribute host-installed font files.

Separate presentation transforms from collision/game-rule ownership. Animation, sprites and hit regions must agree in runtime coordinates. Match sprite filtering and integer/fractional scaling to the chosen art. Avoid nonuniform scaling and shader effects that introduce unwanted colors/edges. Check material-sharing so flashing one actor does not recolor all actors unintentionally.

Use a small audio vocabulary matching the material/world: action, confirmation, failure, ambience/music if appropriate. Mix by semantic priority, avoid doubled transients and restart artifacts, inspect actual output, and include applicable mute/volume controls. An event log cannot establish an audible clean mix.

`inspect_asset_set.py MANIFEST --root PROJECT` checks image dimensions, real alpha, baked-checkerboard preview backgrounds, declared pivots and related frame consistency. Its optional contact sheet supports visual comparison; it does not score style or replace the runtime pass. Follow [asset integration](assets-and-visuals.md) for provenance/import checks and [shader sourcing](shader-sourcing.md) for effects.

Evidence basis: Scenario's official consistency workflow supports canonical-reference reuse, not seed-as-style assumptions; Godot's Theme/import/scaling docs support implementation choices; Riot's art education and GDQuest support communication-first VFX. These are production methods, not evidence that this particular game's art is excellent. See source ledger S05-S13.
