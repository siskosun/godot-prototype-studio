# Visual reference intake

Use for every new prototype request and every material visual redesign. For an isolated logic bug, data repair, or explicitly text-only review, apply it only when the requested change affects presentation.

## Ask once, immediately

Resolve visual reference intent in the first response before committing the art direction or producing a large asset set.

If the user has not supplied a usable reference image, ask in the user's language:

> Please provide 1-3 reference images and choose how each should be used: **PARTIAL_REFERENCE** for selected properties only, or **PIXEL_ACCURATE_REFERENCE** for declared target frames at a declared resolution. For partial reference, name the parts to retain, such as composition, camera, proportions, palette, UI, material, lighting, animation, or effects. For pixel-accurate reference, identify the exact target frame/view and resolution and confirm that you own or are authorized to reproduce it. If you do not want to provide images, choose **ORIGINAL_DELEGATED** and I will establish an original visual baseline.

If usable images are already present but the mode is not stated, do not ask the user to upload them again. Ask only:

> Should these images be used as **PARTIAL_REFERENCE** or **PIXEL_ACCURATE_REFERENCE**? For partial reference, specify the properties to retain from each image. For pixel-accurate reference, specify the target frame/view and resolution and confirm reproduction rights.

If the user has already supplied the mode and sufficient scope, record it and proceed without repeating the question. Combine this with other genuinely material intake questions rather than opening a second questionnaire. This visual-reference question is an intentional intake requirement; it is not permission to add recurring taste approvals.

Useful branch-independent work may continue while a reply is pending: recover prior decisions, inspect the project, research mechanics, or draft a reversible graybox plan. Do not lock a visual identity, generate a large asset family, or claim visual acceptance before the mode is resolved. If the user declines images or delegates the choice, record `ORIGINAL_DELEGATED` and proceed.

## Reference modes

### PARTIAL_REFERENCE

Treat each image as a source of named properties, not as a whole-image reproduction target. Record the role of every image and ignore unselected properties. Examples:

- composition and camera, but not characters or palette;
- character proportion and silhouette, but not costume identity;
- UI density and hierarchy, but not logos, wording, or proprietary icons;
- lighting/material response, but not level layout;
- animation timing or effect intensity, but not protected assets.

Everything outside the declared scope should be original and coherent with the player promise. When several references conflict, name the conflict and choose one canonical source for each property rather than averaging them into a collage.

### PIXEL_ACCURATE_REFERENCE

Treat only the declared frame, crop, viewport, scale, and state as a pixel-comparison target. Record:

- source image identity and rights status;
- exact target state and camera;
- viewport and backing resolution;
- crop/safe area and expected UI/text content;
- assets/fonts that must be identical or authorized equivalents;
- allowed differences, if any, such as platform antialiasing, font rasterization, dynamic particles, or responsive layout outside the target viewport.

Use overlays, image diffs, or side-by-side captures when available, then inspect the actual running Godot scene. A single pixel target cannot prove animation, input, readability during action, or responsiveness at other aspect ratios. Add separate targets for materially different states rather than calling one screenshot universal.

Pixel-accurate reproduction of third-party protected expression requires confirmed authorization. If rights are unknown or absent, preserve only unprotected principles under `PARTIAL_REFERENCE` or create an original equivalent. This rights gap blocks exact copying, not safe independent gameplay work.

### ORIGINAL_DELEGATED

Use when the user explicitly supplies no image and delegates visual direction. Establish a small original reference set or concept baseline, explain what each image controls, and continue within the brief. Do not describe an agent-selected target as user-approved.

### NOT_APPLICABLE

Use only when visuals genuinely do not affect the requested result, such as a text-only review or a logic-only experiment whose handoff is explicitly allowed to remain a diagnostic graybox. State the reason. Do not use `NOT_APPLICABLE` merely because obtaining references is inconvenient.

## Keep gameplay and visual references separate

A visual reference does not define the mechanic, and a gameplay reference does not authorize copying its protected art, characters, levels, audio, names, or UI expression. Record visual intent in the mission brief or visual canon and mechanic comparisons in the design record.
