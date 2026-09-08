# Godot Shaders sourcing and integration

When a requested aesthetic or feedback effect plausibly needs a shader, search https://godotshaders.com/ for implementations before inventing a complex one. Do not add a shader merely because the website is available. Native animation, particles, lighting, or materials may already solve the requirement more simply.

## Search by effect and constraints

Describe the effect in concrete visual terms: 2D outline/hit flash, dissolve, water/refraction, grass sway, pixelation, CRT, glow, or UI highlight. Combine the term with the detected Godot major/minor version, `canvas_item` versus `spatial`, renderer, and target constraints. Inspect actual code, setup notes, dependencies, license, update date, and relevant compatibility comments. A search snippet or appealing preview is insufficient.

Compare only the few candidates that could change implementation. Select by visual fit, version/renderer support, dependencies, performance risk, and licensing rather than likes or date alone. Keep a native/simple fallback when it preserves the visual promise.

## Rights and provenance

The site's license applies per post to code, not automatically to its images, videos, textures, characters, or demo assets. Check the original page and upstream attribution, especially ports. Prefer clearly compatible CC0/MIT options when they meet the brief; preserve required copyright and license notices. Do not treat GPL code as interchangeable with a permissive option or make a legal compatibility claim without review. Unknown rights: find an alternative or leave the affected required feature blocked.

Record the source URL, author, title, retrieval date, stated license and notice, original file checksum when downloaded, local destination, dependencies, edits, renderer/version tested, and evidence. Use `templates/shader_record.json` for a consequential external shader; omit unused fields rather than invent them. No vendor shader code is bundled by this skill.

## Integrate and test

Use a project-local `.gdshader` and appropriate ShaderMaterial. Verify type (`canvas_item` for the relevant 2D node), uniforms, required noise/texture assets, alpha behavior, UV assumptions, texture filtering, and parameter animation. Check version-matched Godot docs rather than blindly renaming Godot 3 built-ins.

For screen-reading effects, check `hint_screen_texture`, draw order/back-buffer behavior, and UI exclusion as applicable. Renderer-specific depth/normal techniques cannot be presumed to work in Compatibility or a web target. Do not change the project's renderer merely to accommodate a decorative shader.

Compare before/after on the actual sprite, background, and busy scene at target scale. Check edges, transparency, scaling, batching/material sharing, readability, pause/time behavior, and repeated transitions. Use the target runtime for compatibility claims and baseline measurement for performance claims. A headless parse cannot prove a shader renders correctly.

## Reference example, not an embedded dependency

'2D dissolve with burn edge' is an example of a source page that includes code and setup requirements. Its parameters, noise dependency, licensing, and current version suitability must be checked afresh when adopted:
https://godotshaders.com/shader/2d-dissolve-with-burn-edge/

Site terms: https://godotshaders.com/license/
Version-matched docs: https://docs.godotengine.org/en/4.6/tutorials/shaders/shader_reference/canvas_item_shader.html and https://docs.godotengine.org/en/4.6/tutorials/shaders/screen-reading_shaders.html . Replace the version path to match the project; 4.6 is not a forced baseline.
