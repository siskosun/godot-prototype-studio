# Text rendering integrity

Use whenever the game contains Chinese, Japanese, Korean, Arabic, Cyrillic, emoji, localization, or any player-facing characters beyond the guaranteed bundled font set. Treat text rendering as a release property, not a desktop-editor convenience.

## Hard rule for Web delivery

Do not rely on a host-installed `SystemFont`, automatic system fallback, or `ThemeDB.fallback_font` to prove a Web build is complete. Godot system-font loading is not implemented uniformly on Web, and a desktop machine can hide missing glyphs that become tofu boxes or blanks in the browser. Bundle authorized font data that covers the scripts actually shipped.

Use a shared Theme or deliberately connected Font/FontVariation fallback chain. Keep essential labels as text, not baked into generated art.

## Build a real character corpus

Collect the actual strings reachable in the delivered scope: menus, buttons, HUD, tutorials, result screens, item names, punctuation, digits, currency/symbols, and every included locale. Include dynamic format characters that will appear after substitution.

For important bundled fonts, verify coverage against this corpus with Godot `Font.has_char()` or an equivalent engine-level check. If multiple fallback fonts are used, verify the effective chain, not just the first font file. Record the corpus and missing-codepoint result as source evidence.

A source coverage check is necessary but not sufficient. Shaping, line breaking, fallback selection, import settings, scale, and containers can still fail at runtime.

## Runtime and Web gate

Exercise representative text in the actual final browser build and inspect at least the smallest and largest supported layout states. Check:

- missing-glyph boxes, numbered tofu, replacement character `�`, blank labels, or unexpected fallback style;
- Chinese/Japanese/Korean punctuation, mixed Latin/CJK baseline and line height;
- clipping, ellipsis, wrapping, overlap, button expansion, and modal overflow;
- bold/weight variants and icons/symbols that silently fall back to a mismatched face;
- high-DPI/browser zoom and the delivered viewport range;
- the final Web export after cache refresh, not only the editor/native build.

For `NEAR_RELEASE`, `WEB_PREFLIGHT` always links a browser report with `glyphsOk=true`, `replacementGlyphsDetected=false`, and `textOverflowDetected=false`, plus a browser capture from the matching BUILD_ID. Non-Latin/localized projects additionally require source evidence that authorized bundled fonts/fallbacks cover the shipped character corpus. A self-review can establish visible rendering defects; it does not establish linguistic translation quality.

## Automatic repair loop

When a text defect is observed, continue without asking for routine permission:

1. identify the affected string, active Theme/font chain, viewport, and final Web BUILD_ID;
2. distinguish missing glyph coverage from layout, import, shaping, or stale-cache failure;
3. add/replace an authorized bundled font or fallback only where needed; preserve the art direction;
4. update shared Theme/layout constraints rather than patching many labels independently when the cause is systemic;
5. re-run font coverage, re-export Web, restamp BUILD_ID, hard-refresh, and repeat the same browser path;
6. keep the repair only when the final Web capture and browser report pass.

A player-facing missing glyph, blank essential label, or unreadable overflow is MAJOR or BLOCKER according to whether the required path remains usable. Do not mark `DONE` with unresolved required-language text corruption.
