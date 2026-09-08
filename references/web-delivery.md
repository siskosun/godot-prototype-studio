# Web delivery, browser preflight, and LAN sharing

Use this guide whenever a Web build is requested, produced, shared, or used as near-release evidence. A Web export is a distinct runtime target, not a desktop build wrapped in HTML.

## Delivery modes

Keep these modes separate:

- **LOCAL_WEB_TEST**: developer-machine browser check. `http://localhost` or `http://127.0.0.1` is acceptable for local testing when the required browser features work. This is not shareable to another device.
- **WEB_SHARE**: lightweight handoff during development. Export Web, stamp a BUILD_ID, serve it, run `WEB_PREFLIGHT`, give the playable URL and limitations. Do not create a full `release_evidence.json` merely because the user asks “网页呢” or wants someone to try the current build.
- **LAN_SHARE**: share with another device on the same LAN without public hosting. Bind the server to `0.0.0.0`, use HTTPS for the non-loopback address, serve the game at `/`, and give second-computer instructions. Use this when the brief asks for another-device/local-network sharing or when it is the chosen handoff route. Near-release quality alone does not require LAN.
- **FIRST_TARGET**: early smoke on the intended Web target. Run as soon as one character, one required-language string, one button, and one sound exist. It checks engine start, display fit, visibility, a clickable control, and the promised glyphs/audio. It is not a complete level or a final release record.
- **NEAR_RELEASE**: final browser-verification profile for a release-like Web artifact. It may run on localhost for local final verification or on LAN HTTPS when LAN sharing is part of delivery. Public hosting remains separately authorized.

Do not substitute `file://`, a folder listing, a headless native run, or a desktop screenshot for a served Web build.

## Web export gate

Use the project’s pinned Godot version and its matching export templates. Prefer installing the selected Web templates for that version when the environment supports selective installation; do not download an all-platform TPZ merely by habit. Godot 4.3+ prefers single-threaded Web exports for compatibility. Keep `thread_support=false` unless the game actually needs Web threads or another feature that requires them. If threads are enabled, the server must provide the required cross-origin-isolation headers and the browser must confirm the resulting runtime works.

For ordinary 2D browser/LAN builds, default to:

- Compatibility renderer, because Godot 4 Web targets WebGL 2.0 through that renderer.
- `html/canvas_resize_policy=1` (Project) unless the brief deliberately requires Adaptive. If Adaptive is retained, declare and verify a backing-canvas/DPR budget so a high-DPI display cannot silently create an unnecessarily large render target.
- `vram_texture_compression/for_mobile=false` unless the target and imported texture pipeline actually require/support the mobile VRAM-compression path. Do not enable compression flags speculatively; always verify the resulting export files.
- Explicit bundled fonts for every required non-Latin script in the Web build. System-font and `ThemeDB.fallback_font` success on desktop is not evidence that the browser export contains the glyphs.
- A user gesture before judging Web audio. Godot 4.3+ defaults Web audio to Sample playback. Keep that for ordinary imported sound when it behaves correctly. Switch affected players or the Web default to Stream when the game needs procedural audio, unsupported Sample-mode effects, or behavior that the final browser run proves Sample cannot provide. Do not impose Stream on every Web project.

Export to a dedicated directory such as `export/web/` with `index.html` as the entry point. Do not serve the project root. After export, require nonempty `index.html`, at least one `.wasm`, at least one `.pck`, and the loader `.js`. A successful editor export command is not sufficient when these files are missing or zero bytes.

## BUILD_ID and separate identities

Before browser evidence, run:

`python <skill-root>/scripts/stamp_web_build.py export/web`

The script derives a BUILD_ID from the Web payload, writes `BUILD_ID.txt`, and stamps the HTML with the same visible identifier. Re-run it after every export. Then hash the Web directory. Hash the editable source/ZIP separately; never use one mixed source-plus-39MB-WASM tree hash as the identity for both artifacts. If `export/web/` lives under the working project, create the final source staging/ZIP **without** that generated directory before hashing it. The release validator rejects a source identity that contains generated `export/web` payloads.

Browser screenshots/logs must show or record the BUILD_ID and URL. A native/headless capture can support rule regression but cannot prove the page the player opened.

## Serving locally and on LAN

Use the bundled server rather than hand-writing `python -m http.server`:

`python <skill-root>/scripts/serve_web_export.py export/web`

It refuses a directory without the required Web payload (and refuses an accidental Godot project root), binds `0.0.0.0`, disables directory listings, serves `/` as the game entry point, sets WebAssembly MIME, disables development caching, generates a short-lived certificate with SANs for localhost and the selected LAN IP when no certificate is supplied, and prints the HTTPS LAN URL. It sends COOP/COEP only with `--cross-origin-isolation`, which should match a Web preset that actually enables threads or another isolation-dependent feature. It is a development/LAN server, not a public-production host.

A certificate warning is not itself evidence of a secure context. On the receiving browser, accept/trust the local certificate as appropriate, then verify `window.isSecureContext === true`. If it stays false, install/trust an appropriate local CA/certificate or provide a trusted certificate; do not fall back to LAN HTTP and call it verified.

For LAN sharing also check:

- host and receiver are on the same reachable subnet or network path;
- the OS firewall allows the selected TCP port;
- the URL is `https://<LAN-IP>:<port>/`, not `http://`, `127.0.0.1`, or `file://`;
- `/` returns the game HTML, not a directory index;
- hard refresh after a new export, especially if PWA/service-worker caching exists.

## WEB_PREFLIGHT

Run the service first, then:

`python <skill-root>/scripts/web_preflight.py export/web --url https://<LAN-IP>:8443/ --profile LAN_SHARE --browser-report <report.json> --project-root <project> --allow-self-signed`

For the first playable Web slice use `--profile FIRST_TARGET` with a real browser report. For a near-release Web artifact use `--profile NEAR_RELEASE`, pass the actual project root/preset, and declare a backing-canvas budget with `--max-backing-width` / `--max-backing-height`. Player-facing profiles also require CSS display size, viewport fit, full visibility, and a clickable primary control. A backing-canvas budget PASS does not prove the page fills the window. Near-release always enforces text-render integrity; add `--require-audio` when the brief promises audio. If the selected preset enables threads, use `--allow-threads` and serve with `--cross-origin-isolation`; otherwise do not require COOP/COEP. Enable `--allow-mobile-vram` only for an explicit ETC2/ASTC-capable target/import path. A custom Web release template requires separate version-compatibility verification before `--allow-custom-template`.

The preflight checks what can be established deterministically from files and HTTP(S):

- `/` returns HTML containing the Godot canvas and matching BUILD_ID, not a folder listing;
- `.wasm`, `.pck`, `.js`, and `index.html` are present and nonempty;
- `.wasm` is served as `application/wasm`;
- the exported canvas policy matches the selected Web preset; near-release also enforces the declared backing-canvas pixel budget so high-DPI displays cannot silently create an oversized target;
- player-facing reports include CSS size, viewport size, `fullyVisible`, `clipped=false`, and `primaryControlClickable`; a 640×360 CSS canvas on a much larger window fails even when backing pixels are inside budget;
- the selected Web preset explicitly records thread support and mobile VRAM compression; threads and ETC2/ASTC mobile compression require deliberate opt-in rather than accidental defaults;
- non-loopback URLs use HTTPS; LAN_SHARE specifically requires a non-loopback LAN address. A localhost NEAR_RELEASE check may use the browser's local secure-context treatment. COOP/COEP and `crossOriginIsolated` are required only when the selected Web preset actually requires cross-origin isolation;
- the served BUILD_ID matches the hashed export.

Browser-only facts come from a browser report produced by the available real-browser harness or a deliberate manual inspection. For WEB_SHARE/LAN_SHARE/NEAR_RELEASE, require `engineStarted=true`, a normal-input smoke path, no fatal console errors, matching URL/BUILD_ID, and `isSecureContext=true` for LAN. Require `crossOriginIsolated=true` only when the selected preset needs it. If the exported loader exposes a version-specific missing-feature API, record it and require no missing features; otherwise record equivalent capability checks rather than inventing an API. Require post-gesture audible output when audio is in scope. Near-release always records text/glyph/layout integrity; non-Latin/localized projects must use bundled font coverage rather than desktop system-font success.

`web_preflight.py` validates the report; it does not launch a browser itself. A PASS therefore means the supplied browser observations and service/file probes are mutually consistent, not that Python independently perceived the game.

## Lightweight WEB_SHARE versus final release

For an intermediate share, use `templates/web_share_record.json` plus the preflight output. Do not create `.prototype/evidence/manifest.json` and pretend it is a release record; do not run `validate_release_evidence.py` unless a final-artifact completion record is actually required.

For final `NEAR_RELEASE` handoff, create **separate** records:

1. source/project ZIP record with its own hash and source/runtime evidence; build it from a clean source-only staging tree that omits generated `export/web`;
2. Web export record with its own Web tree hash, BUILD_ID, the actual share mode used, `WEB_PREFLIGHT`, browser captures/logs, and the near-release quality review. Use LAN_SHARE only when that is the chosen/required delivery route.

Each record may name the other artifact as a paired identity, but its tests remain bound to the artifact actually exercised.

## Second-computer handoff

Write the instructions as if the receiver has none of the author’s paths or browser state:

1. Start `serve_web_export.py` from the documented export directory and note `https://<LAN-IP>:<port>/`.
2. On the receiver, open exactly that HTTPS URL. Never use `file://`, localhost, or the author’s 127.0.0.1 address.
3. If the local certificate is not trusted, follow the browser/OS trust flow. After proceeding, confirm the page actually reports a secure context; if not, trust/install the local certificate/CA properly.
4. Allow the host firewall port and keep both devices on the same reachable network.
5. After a new export, hard refresh or clear the site/service-worker cache when an old BUILD_ID persists.
6. If the Web target is materially slower than the supported requirement, report the measured Web limitation and use the native Godot/desktop build only as an explicitly separate fallback, not as proof that Web passed.

Evidence basis: current Godot stable Web documentation prefers single-threaded exports since 4.3, exposes `variant/thread_support`, `html/canvas_resize_policy`, and desktop/mobile VRAM-compression options, documents secure-context/cross-origin requirements for threaded exports, recommends `index.html`, defines `.wasm`/`.pck`/`.js` delivery, and documents Sample versus Stream audio tradeoffs. Browser secure-context detection uses `window.isSecureContext`; this workflow treats non-loopback LAN sharing as HTTPS-only. System fonts are not implemented uniformly on Web, so release fonts are bundled. Verify option behavior against the project's pinned Godot version.
