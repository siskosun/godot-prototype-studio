# Godot production lessons to apply selectively

Use the detected project version's official documentation, target renderer and actual exports. The research snapshot in the source ledger is not a required engine upgrade. Preserve a working pinned version; inspect release notes and regressions before a justified migration, with a reversible baseline.

| Failure pattern | Prevent or diagnose | Evidence |
|---|---|---|
| Editor works, export fails | Make a thin target export early; repeat after platform-sensitive changes; use matching export templates | Clean exported launch, not editor screenshot |
| Web target assumed equivalent to desktop | Use web-delivery.md: version-matched templates, dedicated export dir, single-thread default when appropriate, declared canvas/DPR policy, explicit texture-compression choice, bundled non-Latin fonts, BUILD_ID, HTTPS LAN serve and WEB_PREFLIGHT | Final served browser report/capture plus Web hash |
| UI click leaks into gameplay | Inspect Control mouse_filter, input propagation, modal ownership and focus; decorative overlays must not consume intended input | Click/key/touch across modal boundaries |
| Consistent source, inconsistent runtime | Check inherited scene values, shared Resource/material instances, signal duplication and spawn ownership | Runtime instance/state plus rendered result |
| Timing/hit feedback disagrees | Separate authoritative rule clock from presentation; avoid competing tweens/animations; reset on pause, death, restart or teleport | Boundary replay, event timeline and clip |
| Smooth on developer machine only | Measure the lowest supported target and the busiest representative scene; track frame-time spikes and memory, not only average FPS | Environment, cold/warm runs and profiler capture |
| First-use effect stutter | Check target-renderer pipeline/shader behavior; prewarm only where useful and supported; do not claim import compiles all runtime pipelines | Cold first-use replay |
| Pixel art blurs or sprites bleed | Match filter/mipmap/atlas padding and scaling to the art; inspect smallest/odd viewport and motion | Actual scaled frames |
| Resource paths fail on another OS | Preserve Godot-managed references/UIDs; use correct case; include runtime dependencies and exported data | Clean copy/export on claimed platform |
| Save works only on happy path | Use user storage, schema/version checks and recoverable writes; test interruption/corruption where saves matter | Round trip plus adverse path |
| Audio arrives as final decoration | Integrate cues in the first quality exemplar; manage buses, overlap and restart state. On Web, test after a player gesture; keep Sample for ordinary audio that works, but use Stream when procedural audio/effects require capabilities Sample mode does not provide | Actual browser listen/capture, not trigger logs |
| Huge system to solve a local problem | Prefer native nodes, direct ownership, typed rules and local tests; profile before pooling/threading or framework changes | Smaller change reproduces and fixes issue |

Physics interpolation, UI APIs, web exports, shader support and imported assets vary by engine/renderer. Look up exact properties rather than copying stale Godot 3 or a different renderer's tutorial. With interpolation, follow current physics-tick/reset guidance; do not independently animate a physics body's transform from multiple loops.

Use project-native test frameworks when present. Add the smallest adequate runner otherwise. Prefer observable state/events over pixel guessing for rules, while retaining rendered/audio checks for presentation. Do not buy a framework or add a custom engine fork merely to satisfy the skill.

Console/online production anecdotes can identify risks but do not justify reproducing a studio's platform middleware in a local 2D slice. Native settings and a small adapter often suffice. Source ledger S01-S04, S06-S08, S11-S13, S21-S25 identifies docs and scoped practitioner reports.
