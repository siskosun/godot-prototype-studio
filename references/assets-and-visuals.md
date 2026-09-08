# Integrated presentation and assets

A normal new prototype defaults to a coherent presentable slice, not a diagnostic gray box. A deliberately rough technical/mechanic probe is valid when the brief calls for it. Use temporary placeholders during construction, not as a silent downgrade at handoff.

Read art-direction.md for identity, a live quality exemplar and cross-asset consistency.

## Visual direction

Choose a consistent palette, silhouette language, materials, typography, camera, UI shapes, and feedback intensity within delegated taste. Preserve an explicitly supplied visual reference. A concise direction in the blueprint normally suffices; use `visual_canon.json` only for a multi-asset workflow that benefits from it.

Prioritize actual play: readable objective and hazards, distinguishable actors, clear interaction regions, responsive buttons, visible success/failure, transitions, retry, and a fitting result state. Add audio and motion where they communicate the promise; offer mute and reduced intense effects when relevant. Do not let effects obscure the next decision.

## Asset pipeline

Check available generation, editing, licensed libraries, and user assets. Produce or acquire actual assets; do not use ASCII/emoji or an unrelated screenshot as the principal art for a requested polished character game. An intentional coherent vector/procedural style can be appropriate within the brief.

Keep originals; derive runtime-ready copies. For sprites, check **real** background removal (alpha channel, not a painted checkerboard), trim bounds, foot/contact pivot, sheet dimensions, frame order, atlas filtering, occlusion, and scale in scene. Run that inspection on the first sample before batch generation. A green-screen plate plus shader key is an explicit color-constrained fallback after real alpha fails; do not make it the default. For audio, check leading silence, clipping, loudness consistency, loop seams, and triggered playback. For video, process only what the game needs; do not mandate 4K, frame interpolation, or a publishing pipeline.

Borrow the asset-to-runtime discipline from godot-fun/godot-agent without installing its global framework or asset tool collection. Inspect the relevant tool and dependency only when needed. Never treat a contact sheet as an animated character or a preview image as the licensed asset.

Track external sources, licenses, local files, and significant modifications. Use the optional asset manifest for a nontrivial pipeline. Verify that each critical asset is imported, assigned to the intended runtime node, and visible/audible in the final play path.

## Missing assets

Seek a licensed alternative or create an original equivalent within the authorized style. Do not spend money, upload private assets, clone a person's voice, or claim rights without authorization. When the specific identity is essential and unavailable, preserve the limitation rather than passing a generic replacement as the requested result.

Read `shader-sourcing.md` when a visual effect may benefit from shader code. Shader effects are optional implementations, not a requirement to make every game use shaders.
