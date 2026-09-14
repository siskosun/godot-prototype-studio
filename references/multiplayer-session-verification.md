# Multi-client and session verification

Use when the promised experience involves two or more browser/device identities, rooms, shared authoritative state, LAN play, WebSockets, host/client roles, reconnects, or server-owned session state. Single-client Web success cannot prove this contract.

## Freeze the joint acceptance object

Treat the tested unit as a **joint runtime**, not a set of individually green clients:

- exact client/Web BUILD_ID and source identity;
- exact server process/code identity and endpoint;
- client A identity/device/browser and client B identity/device/browser;
- network route, TLS/certificate state and room/session identity;
- authoritative round/session state;
- required synchronized player path and round count.

Use `templates/multiplayer_session_matrix.md` when these states matter. A localhost run, HTTP 200, one connected browser, accepted Python TLS request or two independent single-client passes cannot be promoted into multi-client completion evidence.

## Evidence ladder: never infer the next layer

1. **Service** — the intended server process is alive and serving the expected build/endpoint.
2. **Single client** — one real browser/device opens the exact URL, starts the engine/client and performs the normal input path.
3. **Two identities** — two distinct browser/device identities join through the intended route without overwriting each other.
4. **Shared session** — both are in the same room/session and observe the same authoritative round/version with role-specific state where expected.
5. **Synchronized interaction** — actions on one side produce the specified server transition and the corresponding observation on the other side without a manual refresh workaround.
6. **Lifecycle/recovery** — required leave/offline/refresh/tab-close/reconnect/server-restart cases behave as specified.
7. **Physical target proof** — when the brief requires two real devices on the same LAN, repeat the contracted rounds on those devices after certificate acceptance/trust and bind the evidence to their build/session identity.

Passing a lower layer never proves a higher one. Keep unavailable layers `UNVERIFIED`.

## Distinguish lifecycle events

Model these separately when applicable:

- explicit **leave**: client intentionally tells the server it is leaving;
- **network loss/offline**: client disappears without a clean leave;
- **refresh**: page/runtime is recreated, possibly preserving browser storage;
- **tab/window close**: browser identity/storage semantics may differ from refresh;
- **reconnect**: define whether identity/seat/room can be reclaimed and within what window;
- **server restart**: define whether room state is intentionally volatile or persisted.

Do not let a local-only cleanup strand a server seat. Do not use a gameplay request (ready/submit/next-question) as the only liveness signal when the product requires idle clients to remain present; heartbeat/liveness must be independently testable from gameplay actions. A timeout value is a design choice to verify, not a universal constant.

For every required transition record: pre-state, triggering event/input source, expected server state, expected view on each client, timeout/recovery rule, and actual observation. Distinguish server-authoritative state from client UI state.

## Bind evidence to the running server instance

For the bundled static LAN server, use `serve_web_export.py --runtime-record PATH`. The record includes the BUILD_ID, process ID, start time, advertised URL, server code hashes and a per-process instance ID. The server returns the same instance ID in `X-GPS-Instance-ID`. Pass the record to `web_preflight.py --runtime-record PATH` when server-instance identity matters.

A runtime record is start evidence, not proof the process is still healthy. The preflight binds the URL/build to the instance header it actually receives. If server source changes, restart before relying on the record. For a project-specific game/session server, implement an equivalent instance identity rather than pretending the bundled static server proves authoritative multiplayer logic.

Port bind failure must fail before reporting SERVING. Certificates must cover the advertised LAN address. Browser acceptance/trust is a browser fact; a Python client that accepts a PEM does not prove the user browser accepted it.

## Build and post-export identity

If the delivered Web client needs extra files or patches after Godot export (for example `network.js`, HTML shell edits, generated configuration or bundled fonts), the order is:

1. export from the frozen source;
2. copy/generate all required external files;
3. apply declared HTML/JS patches;
4. verify required files and versions;
5. **then** stamp BUILD_ID;
6. hash the final Web payload;
7. start/restart the serving process;
8. hard refresh receiving browsers and verify the new BUILD_ID;
9. run single- and multi-client acceptance.

Any change to a player-delivered file after stamping invalidates the BUILD_ID evidence and requires restamping/retest. Any change to authoritative server code requires a new server instance before claiming that change is live.

## Mixed Godot canvas and HTML controls

When a Web prototype overlays DOM `input`/`textarea` or other HTML controls on a Godot canvas, test them as a separate surface. Verify focus transfer, blur/cancel, IME composition (including required CJK input), Enter/confirm behavior, mobile keyboard where targeted, resize/DPR alignment and pointer/touch hit regions. Correct Godot glyph rendering does not prove an HTML input works; correct layout does not prove IME composition works.

## Completion language

For a multiplayer/LAN claim, DONE requires the highest layer explicitly required by the brief on the exact build/server instance. If two physical devices or a specified number of synchronized rounds have not been observed, say so directly and leave that claim UNVERIFIED/BLOCKED rather than substituting editor, localhost or simulated-state evidence.
