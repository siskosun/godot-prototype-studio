# Godot Prototype Studio 0.4.4

[English](README.md) · [中文](README.zh-CN.md)

Turn an idea into a small, complete, near-release-quality Godot 2D slice when the user asks for a finished/high-completion playable result. Mechanic spikes, grayboxes, technical proofs and narrow fixes keep their natural scope. Completion, runtime/package form, and evidence are judged separately: high craft does not automatically mean a source ZIP plus Web export. The near-release path covers complete design, an early target smoke, integrated quality exemplar, full session, art/UX/feel, real input, repair, and tested delivery of the requested artifacts. It does not promise a full commercial game or validated audience appeal.

## Use

Load SKILL.md, not the entire reference directory. Replace the old skill bundle through the host's supported import flow; packaging alone does not install it into an account. Preserve project files/history. The updated archive contains one skill.

Example request:

> Build this idea as a near-release-quality Godot slice: [idea]. Keep the scope small but complete. Verify the closest released games, improve the design, and choose reversible details within the idea. Continue through art, user experience, gameplay tuning, actual interaction, repairs, final Web export/browser check, and packaging. Stop only at completion or a real blocker.

Explicit brief approval, retained art decisions, a rough experiment, a targeted bug fix, and a required platform remain authoritative. Finished/high-completion commissions default to near-release craft on the requested runtimes. Add a source ZIP or Web export only when that handoff is asked for; a chosen Web artifact must be served and browser-tested for display fit as well as pixel budget. LAN sharing is selected only when the receiver needs it. Purchases, public hosting/release, private-data uploads and destructive changes need their existing authorization. No paid backend or external framework is required by default.

## Quality rather than more process

One brief owns acceptance and delegation; one progress note supports resumption. Final near-release reviews consider nine dimensions by referencing that brief: gameplay, UX, art, motion/audio, reliability, performance, platform/access, text rendering and delivery/rights. Applicable dimensions must PASS; a genuinely absent requirement may be `NOT_APPLICABLE` with a brief-linked rationale, while unavailable evidence is `UNVERIFIED` and cannot be used to claim near-release completion. A quality exemplar is a live scene, not an illustration.

Use task-specific references only when relevant. Engine intelligence, risk tests, replay, automated policies and variants are conditional tools, not compulsory approval stages. Human playtests do not automatically block a delivered candidate; without them, user enjoyment remains explicitly unvalidated.

## Optional utilities

Python 3 is used by the bundled scripts. The asset-inspection utility and the corresponding test module use Pillow; the environment must provide it. The LAN server can use an existing certificate/key or `openssl` to generate a short-lived self-signed development certificate. No utility installs dependencies, publishes to the public Internet, or calls paid services. A full regression suite with Pillow missing is incomplete and must not be called fully passing.

```bash
python scripts/init_workspace.py PROJECT
python scripts/detect_capabilities.py PROJECT --write
python scripts/run_godot_checks.py PROJECT --mode import
python scripts/inspect_engine_context.py PROJECT --write
python scripts/inspect_asset_set.py MANIFEST --root PROJECT --contact-sheet REVIEW.png
python scripts/stamp_web_build.py export/web
python scripts/serve_web_export.py export/web
python scripts/web_preflight.py export/web --url http://127.0.0.1:8000/ --profile FIRST_TARGET --browser-report BROWSER.json --project-root PROJECT --require-glyphs --require-audio
python scripts/web_preflight.py export/web --url http://127.0.0.1:8000/ --profile NEAR_RELEASE --browser-report BROWSER.json --project-root PROJECT --max-backing-width 1920 --max-backing-height 1080
python scripts/package_and_report.py PROJECT --out release
python scripts/change_impact.py --before-tree OLD --after-tree NEW
python scripts/validate_quality_review.py REVIEW.json --artifact ARTIFACT
python scripts/validate_release_evidence.py ARTIFACT --evidence RELEASE.json
```

These are examples, not a required sequence. run_godot_checks exits 0 PASS, 1 failure, 2 unavailable/invalid execution, or 3 PARTIAL. It does not exercise all real inputs, render/audio paths or target exports. The optional starter is an instrumentation fixture, not a finished game or art template.

## Evidence and limits

DONE requires the requested artifact and its required quality/evidence. A genuine unresolved required capability or defect yields BLOCKED with usable partial work and a precise unblock condition. Preserve original failure traces and final retest identities. A project ZIP must match the clean tested tree. A chosen Web build must be exported from the frozen final source, stamped, and browser-tested through the required player path, including CSS display fit and clickability. Near-release Web verification may run on a served localhost route; non-loopback/LAN routes use HTTPS. LAN sharing adds secure-context, certificate/firewall/network checks when that route is actually part of delivery. Source and Web hashes remain separate. Final source ZIP/staging must omit generated `export/web`; the validator rejects a mixed source+Web identity. The near-release quality review binds to the chosen player-facing artifact.

Validators check record/file/hash consistency and basic media signatures; they cannot establish that a log is truthful, a scene is beautiful, a reviewer independent, or a player enjoyed the game. Never turn a self-review into human evidence or an injected state into normal-path reachability.

## Maintenance

```bash
python -m unittest discover -s tests -v
```

See the [upgrade audit](audit/upgrade-audit.md), [strong-agent overconstraint audit](audit/gpt6-overconstraint-audit.md), [research](references/research-basis.md), [behavioral scenarios](tests/scenarios.md) and [tool contracts](references/tool-contracts.md). The recorded tests are utility fixtures and static instruction reviews, not live Godot/Codex or target-player trials. Run the appropriate real-engine acceptance in the deployment environment.
