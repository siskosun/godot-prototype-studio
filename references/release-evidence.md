# Exact delivery and completion

The brief defines the target and required claims. NEAR_RELEASE_SLICE is the craft bar for the chosen player-facing artifact; it does not by itself require a source ZIP or a Web export. Keep source and Web identities separate when both exist. A chosen Web artifact must be served and browser-verified, including display fit and clickability; LAN_SHARE is required only when that route is chosen. Read [web delivery](web-delivery.md) for share modes and WEB_PREFLIGHT, [change impact](change-impact.md) before reusing suites, and [text rendering](text-rendering.md) when localized/non-Latin text exists.

Use `package_and_report.py PROJECT --out DIR` as the freeze/hash/ZIP/report entry. It stages clean source, writes identities, packages the ZIP, restamps Web when asked, and links validator outputs. Hashes and file associations are generated; visual PASS is not.

## Two final artifact records, not one mixed tree

Create separate records from `templates/release_evidence.json`:

- **Source record** — target `GODOT_PROJECT_ZIP`, its archive hash plus clean extracted-tree hash, source/runtime checks, and paired Web identity when Web is required.
- **Web record** — target `WEB_EXPORT`, quality profile `NEAR_RELEASE_SLICE` when Web is the player-facing delivery, Web directory tree hash, BUILD_ID, the **actual** share mode used, NEAR_RELEASE WEB_PREFLIGHT (pixel budget **and** display fit), browser evidence, quality review, and paired source identity.

Do not hash source files and generated `export/web` together. If Web output lives under the working project, stage final editable source without that generated directory before packaging and hashing it. The validator rejects mixed source/Web identities. For an intermediate “give me a webpage” request, use WEB_SHARE and `templates/web_share_record.json`; do not fabricate final-release paperwork.

## Freeze and test

Finish implementation and required polish. Remove secrets, caches, unused downloaded code, and unrelated artifacts. Freeze source and Web separately.

For the source ZIP, package a clean source-only staging tree, extract it to another clean directory, then test/hash the extracted copy; record both archive SHA-256 and extracted tree hash. For Web, export from the same frozen source, run `stamp_web_build.py`, serve it, run the applicable browser path, and hash the Web directory. Gameplay/content/export changes invalidate affected evidence. Re-exporting Web changes its BUILD_ID and Web identity even when source did not change. Record `gameContent`, `testHarness`, and `package` hashes so a harness-only edit cannot force a full rules battery.

The bundled tree hash excludes `.git`, `.godot`, `__pycache__`, `.DS_Store`, and root `.prototype` workflow records. Do not place promised game files under an excluded path. Symlinks are rejected.

## Web preflight is a completion gate

A final Web artifact is not complete because export returned zero. Use `web-delivery.md` to select the share route and run `web_preflight.py` with `--profile NEAR_RELEASE` for near-release evidence. That profile enforces the final Web preset, browser startup/normal path, BUILD_ID, text integrity, backing-canvas budget, CSS display fit, visibility, primary-control clickability, and audio/isolation when applicable. It may run against localhost for a local final browser check, or against LAN HTTPS when LAN sharing is required.

The release record links the PASS preflight whose `exportSha256` and BUILD_ID match the artifact. `shareMode` records how the validated page was actually served (`LOCAL_WEB_TEST`, `LAN_SHARE`, or an explicitly authorized `PUBLIC_HOSTED` route). `--required-share-mode` is an external contract assertion; use it only when the brief requires that route.

## Exact completion evidence

Use `templates/release_evidence.json`. Required checks must be explicit, actually executed, and PASS. Evidence files must exist and match their hashes and artifact identity. Presentation claims need actual captures. A near-release record binds the quality review to this player-facing artifact. When that artifact is Web, also require:

- a separately hashed source artifact pair;
- a NEAR_RELEASE preflight bound to this Web hash and BUILD_ID, including display fit as well as pixel budget;
- declared Web audio and thread expectations from the brief/preset;
- required hard gates for web preflight, interaction, presentation and text rendering, plus audio when promised;
- a linked quality review whose **applicable** dimensions PASS, `NOT_APPLICABLE` dimensions are justified, and no required dimension is `FAIL` or `UNVERIFIED`.

Validate with:

`python <skill-root>/scripts/validate_release_evidence.py export/web --evidence release-web.json --required-profile NEAR_RELEASE_SLICE`

If the brief specifically requires LAN sharing, also pass:

`--required-share-mode LAN_SHARE`

The validator checks consistency, not whether Godot or a human truly performed the recorded observation. Browser/player evidence must still be produced by the real available environment.

## Handoff to another computer

When the selected delivery is LAN_SHARE, follow the second-computer instructions in `web-delivery.md`: use the HTTPS LAN URL, handle the local certificate, allow the firewall port, remain on a reachable LAN, hard-refresh after re-export, and state the native fallback if Web limitations matter. Do not include LAN instructions for a local-only delivery merely to satisfy a template.

## Completion language

Report only what was executed. A validated prototype is not store-certified, market-proven, penetration-tested, or independently reviewed unless those steps actually happened. If an applicable required check is unavailable, keep it `UNVERIFIED` and report BLOCKED for that requested quality claim while still delivering the strongest usable artifact.
