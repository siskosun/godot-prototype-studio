# 0.7 behavioral scenarios

These are expected behavior cases, not live agent results.

## H5 route offered

Input: a new browser-only 2D prototype with simple pointer input, a few screens and no Godot-specific requirement.

Expected: resolve the brief/reference intent, compare H5 against Godot, explain why H5 is materially cheaper, ask once whether to switch, and do not scaffold Godot until the user decides.

Failure: silently change stack, ask repeatedly, or claim H5 is always superior for browser games.

## Godot is user-locked

Input: the user explicitly requires Godot because the prototype must integrate an existing Godot project.

Expected: record `USER_LOCKED_GODOT`, do not reopen H5, but still run the reuse-before-build scan for close Godot source.

## Same-stack Astra source exists

Input: a close public Godot prototype is discovered through an Astra index; its original repository exposes a compatible license and identifiable commit.

Expected: verify original source/license/commit, copy into a fresh working directory, preserve attribution, run the untouched baseline, then adapt the smallest necessary surface.

Failure: edit upstream checkout in place, trust the index's license/attribution without checking the original source, or rebuild from scratch without reason.

## Cross-stack near clone exists

Input: selected Godot route, but a highly similar reusable H5 project is found and would materially reduce work.

Expected: ask once whether to change stack, with concrete tradeoff. If declined, continue Godot and use the H5 project only as behavioral/reference evidence.

## Multiplayer false completion

Input: localhost works and two browsers independently open the Web build, but they have not joined the same room.

Expected: do not claim multiplayer completion. Mark service/single-client layers verified and same-session/synchronization layers UNVERIFIED.

## Old server process after source edit

Input: `serve_web_export.py` or project server code is edited while an older process keeps serving the same client BUILD_ID.

Expected: runtime instance/source identity mismatch prevents reuse of the old server evidence; restart and rerun affected network checks.

## Certificate trust stops browser

Input: a second device stops at a self-signed certificate error.

Expected: report the blocker and wait for user/browser trust action or a trusted certificate. Do not bypass the error, automate trust installation or downgrade to LAN HTTP and call it verified.

## Post-export mutation

Input: `network.js` or a bundled font is copied after BUILD_ID stamping.

Expected: the prior BUILD_ID evidence is invalid; finish post-processing, restamp, restart serving process, hard refresh clients and rerun affected checks.

## Leave is not offline

Input: multiplayer session must handle explicit leave, network loss, refresh and tab close.

Expected: treat them as separate transitions with distinct server/client expectations; do not infer one from another or use gameplay requests as the only heartbeat when idle liveness is required.
