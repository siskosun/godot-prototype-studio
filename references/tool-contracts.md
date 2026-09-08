# Optional tools and what they actually establish

Read when running or maintaining a listed utility. Scripts are conveniences, not mandatory phases. Python 3 is required; only asset image inspection uses Pillow. No bundled script installs dependencies, invokes paid services, publishes files, or downloads third-party code.

| Tool | Purpose / invocation | Limit |
|---|---|---|
| init_workspace.py | `PROJECT [--with-starter]` | Minimal brief/progress; starter is instrumentation, not finished art |
| detect_capabilities.py | `PROJECT --write` | Detection is not a successful runtime/input test |
| inspect_engine_context.py | `PROJECT --write` | Text declarations, not full engine parsing/live observation |
| run_godot_checks.py | `PROJECT --mode import|test|smoke|all` | Engine/log checks, not an end-to-end player test |
| inspect_asset_set.py | `MANIFEST --root PROJECT [--contact-sheet FILE]` | Image/declared-pivot/real-alpha/checkerboard consistency, no aesthetic score |
| package_and_report.py | `PROJECT --out DIR [--web-export DIR]` | Stage/hash/ZIP/identity report; does not invent visual PASS |
| change_impact.py | `--before-tree A --after-tree B` or `--changed-paths ...` | Suite selection and reuse proof, not a playtest |
| compare_prototypes.py | `COMPARISON.json` | Record and finite-metric comparison, no taste authority |
| validate_quality_review.py | `REVIEW.json --artifact ARTIFACT` | Minimum dimensions, evidence hashes, defects and human-label consistency |
| tree_hash.py | `ARTIFACT --write HASH.json` | Identity only; root .prototype and caches excluded for project trees |
| stamp_web_build.py | `export/web` | Deterministic payload BUILD_ID + visible HTML stamp; rerun after every export |
| serve_web_export.py | `export/web [--port N] [--cross-origin-isolation]` | LAN development HTTPS server, not public hosting; COOP/COEP only when requested |
| web_preflight.py | `export/web --url URL --profile ... --browser-report REPORT --project-root PROJECT ...` | File/preset/HTTP consistency plus supplied browser observations; does not launch/perceive the browser |
| validate_release_evidence.py | `ARTIFACT --evidence RECORD.json [--required-profile NEAR_RELEASE_SLICE] [--required-share-mode LAN_SHARE]` | Exact artifact/pair/preflight/evidence agreement, not proof of test honesty |

Other retained validators support optional experiments, saves, assets and human reports. They are not a list of forms every game must fill. Main behavioral rules and delegation are authoritative over legacy template vocabulary.

## Asset-set manifest

Use schemaVersion 1 and `assets`: unique `id`, project-relative `path`, `kind` (`sprite`, `frame`, `ui`, `background`, `other`), optional `group`, `expectedSize: [w,h]`, `requireTransparency`, and `pivot: [x,y]` in source-image pixels. A declared frame group must have matching dimensions/pivots; represent intentionally variable canvases as different groups or normalize them. `requireTransparency` means a real alpha channel; a painted checkerboard fails. `chromaKey` plus `allowChromaKeyFallback` is an explicit fallback after that failure, not the default. The tool cannot infer an undeclared anatomical anchor or validate identity. It rejects paths escaping the project and symlinks. Contact sheets are review aids, not runtime captures.

## Quality review

Use schemaVersion 2, profile NEAR_RELEASE_SLICE, artifactSha256, reviewer, all nine named dimensions and findings, and humanExperience. Each dimension has unique `id`, `criterionRefs`, `status` `PASS`/`FAIL`/`UNVERIFIED`/`NOT_APPLICABLE`, `observation`, and evidence files with `path`, `sha256`, `kind` and `artifactSha256`. `NOT_APPLICABLE` needs a brief-linked rationale and no pass evidence; `UNVERIFIED` blocks near-release completion. Evidence paths resolve relative to the review. Runtime/presentation artifacts must be actual files, not URLs or empty declarations. Evidence kinds identify what was inspected, not who agrees.

Kinds: runtime_log, input_trace, image, video, audio, measurement, source_record, human_report. A gameplay PASS needs input_trace declaring entry=NORMAL_START and terminalObserved=true; art needs image/video; motion_audio needs video/audio; reliability needs runtime_log/input_trace; performance needs measurement; UX and platform_access need input_trace plus image/video; text_render needs source_record plus image/video; delivery_rights needs source_record/runtime_log. These minima are evidence categories, not guarantees. A declared silent game can use video for motion_audio. Image/video/audio kind must match a supported extension and basic file signature (not a full media decode); empty files are rejected. Each dimension can link the same relevant trace without copying it.

A findings item has unique id, dimension, severity BLOCKER/MAJOR/MINOR, status OPEN/FIXED/REJECTED, description and evidence. Optional observedArtifactSha256 preserves the original failing build identity; final retest and resolution evidence must match the delivered build. FIXED needs retest evidence and REJECTED needs a supported rationale. Human experience is UNTESTED with a limitation, or OBSERVED with nonempty participant reports (participantId, observation, isHuman=true) and linked human_report evidence. A human reviewer also declares isHuman=true; these declarations cannot independently prove identity. An agent reviewer cannot be relabeled human. Independent review requires an explicit provenance note. Artifact hashes bind observations to a build but cannot prevent fabricated data.

## Web delivery records

`stamp_web_build.py` derives the visible BUILD_ID from the exported payload while excluding its own stamp, so restamping an unchanged export is idempotent. `serve_web_export.py` refuses missing Web payloads and accidental Godot project roots, serves `/` as `index.html`, disables directory listing/caching, uses HTTPS on LAN, and can generate a short-lived SAN certificate with `openssl`. It does not make a public deployment.

`web_preflight.py` supports LOCAL_WEB_TEST, FIRST_TARGET, WEB_SHARE, LAN_SHARE and NEAR_RELEASE. It reads the selected Web preset when a project root is supplied, verifies thread/mobile-VRAM/canvas choices, checks nonempty HTML/WASM/PCK/JS and MIME/service behavior, and compares a supplied real-browser report with the delivered BUILD_ID. Player-facing profiles require CSS size, viewport size, full visibility, unclipped canvas, and a clickable primary control. A backing-canvas budget PASS is not display-fit. NEAR_RELEASE also requires the project preset, an explicit backing-canvas budget, a served real-browser path, a browser capture, and glyph/layout integrity; LAN HTTPS is required only for LAN_SHARE/non-loopback delivery; audio is required when the brief says so. Thread support triggers cross-origin-isolation requirements. A custom template must be explicitly allowed only after version compatibility is checked outside the script.

The browser report is an observation record, not an automation claim. `missingFeatures` is optional because no undocumented Godot JavaScript method is assumed. Secure-context and cross-origin isolation are browser facts; a self-signed certificate warning does not by itself prove either one.

## Comparison compatibility

The attachment's comparison schema 1.0 remains supported with fixed finite-number validation and explicit AGENT_SELECTED_WITHIN_BRIEF authority. Human-selected records need a human decision reference; agent-selected records need a brief authority reference. All variant runs need real evidence paths and comparable baseline/scenario/conditions declarations. The checker does not execute Godot or interpret aesthetic metrics.
