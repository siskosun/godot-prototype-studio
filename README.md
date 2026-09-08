# Godot Prototype Studio 0.5.0

[English](README.md) · [中文](README.zh-CN.md)

Turn an idea into a small, complete Godot 2D prototype or near-release slice. Version 0.5.0 adds two strong-agent workflows on top of 0.4.4's delivery/evidence split: a one-time visual-reference contract for every new prototype, and a mechanic lab for discovering and falsifying genuinely different gameplay instead of merely reskinning familiar loops.

The skill remains model-agnostic. It gives capable agents room to choose ordinary implementation details, drive Godot, inspect runtime state and captures, compare variants, and repair failures. It does not let the model certify its own fun, historical originality, pixel accuracy, or player preference.

## First-turn visual reference intake

For every new prototype or material visual redesign, resolve visual intent once before locking the art direction.

When no usable image is present, ask the user to provide one to three reference images and choose one mode:

- `PARTIAL_REFERENCE`: retain only named properties such as composition, camera, proportions, palette, UI hierarchy, material, lighting, animation timing, or effects. Everything outside that scope remains original.
- `PIXEL_ACCURATE_REFERENCE`: reproduce declared target frames at declared resolutions. Record the exact state, camera, crop, viewport, authorized assets/fonts, allowed differences, and ownership or reproduction permission.
- `ORIGINAL_DELEGATED`: the user supplies no image and delegates an original visual baseline.
- `NOT_APPLICABLE`: only for a genuinely visual-irrelevant task or an explicitly diagnostic graybox.

When images are already attached, do not ask for them again. Ask only whether they are partial or pixel-accurate references and what each image controls. When the user already supplied the mode and scope, proceed without repeating the question.

Pixel matching applies only to the declared frame and viewport. Runtime overlays or image diffs can support the claim, but one screenshot cannot prove motion, responsiveness, input, readability during play, or other aspect ratios. Unknown rights block exact copying of protected third-party expression, not safe partial reference or original gameplay work.

See [visual reference intake](references/visual-reference-intake.md), [art direction](references/art-direction.md), and [assets and visuals](references/assets-and-visuals.md).

## New gameplay workflow

A new mechanic is treated as a causal change in what the player perceives, decides, does, changes, or can do next. A different theme, content set, reward number, or VFX treatment is not gameplay novelty by itself.

The workflow is deliberately small:

1. State the mechanic thesis as information -> action under constraint -> state or relationship change -> feedback -> changed next decision.
2. Name one familiar anchor, one primary causal design delta, the invariants, and the smallest falsifying observation.
3. Apply the theme-removal test and reject candidates whose difference disappears without their presentation.
4. Trace a few turns before production. Check counterfactual choice, state consequence, teachability, recovery, and dominant spam/wait strategies.
5. Build the shortest repeatable Godot mechanic kernel. Expose legal actions, state deltas, outcome reasons, opportunities, timing edges, and a repeatable scenario or seed.
6. Let the agent reproduce, inspect state/screenshots, trace the owning code, change it, and rerun through real input.
7. Compare only causally different variants under equivalent scenarios, art readability, content opportunities, target, and input.
8. Use a small playable human comparison for feel and preference when available. Keep enjoyment unvalidated when it is absent.

Use claim levels honestly: `DISTINCT_IN_THIS_PROJECT`, `DISTINCT_AMONG_VERIFIED_REFERENCES`, or `HISTORICALLY_NOVEL`. The last requires dedicated broad research; model confidence is not evidence.

See [novel gameplay discovery](references/novel-gameplay.md), [task workflow](references/workflow.md), [variant experiments](references/variant-experiments.md), and the optional [mechanic lab template](templates/mechanic_lab.md).

## Scope, delivery, and evidence

Completion, runtime/package form, and evidence are separate decisions. A request to finish a playable or high-completion prototype with no narrower fidelity target defaults to `NEAR_RELEASE_SLICE`: one bounded, coherent session with integrated gameplay, art, UI, motion/audio, recovery, and real input. High craft does **not** automatically imply a source ZIP or Web export. If no package is requested, the default handoff is the tested in-place Godot project. Add `GODOT_PROJECT_ZIP`, `WEB_EXPORT`, `DESKTOP_BUILD`, `ANDROID_BUILD`, or `LAN_SHARE` only when the request needs that runtime or receiver.

A chosen Web artifact must still be served and browser-tested. LAN sharing is selected only when another device/person needs it. Public hosting/release, purchases, private-data uploads, destructive changes, and exact third-party visual reproduction retain their authorization boundaries.

For a new build, run an early first-target smoke as soon as one character, one required-language string, one button, and one sound exist; do not wait for a complete level. Before batching generated art, inspect one real sample for alpha, pivot, scale, occlusion, and action. Keep the short session status current so interrupted work resumes instead of restarting.

One mission brief owns acceptance and delegation. The optional mechanic lab records discovery evidence without becoming a second acceptance contract. Human playtests do not automatically block a deliverable, but their absence prevents claims about audience enjoyment or preference.

## Optional utilities

Python 3 is used by the bundled scripts. The asset-inspection utility and its test module use Pillow; the environment must provide it. No utility installs dependencies, publishes to the public Internet, or calls paid services.

```bash
python scripts/init_workspace.py PROJECT
python scripts/init_workspace.py PROJECT --novel-gameplay
python scripts/init_workspace.py PROJECT --with-starter --novel-gameplay
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

The initializer creates only the mission brief and progress record by default. `--novel-gameplay` additionally creates `.prototype/spec/mechanic_lab.md`; `--legacy-full` retains the detailed legacy records. Existing files are preserved. The commands above are examples, not a compulsory sequence.

`run_godot_checks` exits 0 for PASS, 1 for failure, 2 for unavailable/invalid execution, and 3 for PARTIAL. Static and headless checks do not establish actual interaction, rendered quality, audible output, pixel identity, novelty, or player enjoyment.

## Evidence and limits

`DONE` requires the requested artifact and its applicable evidence. A genuine unresolved required capability or defect yields `BLOCKED` with the strongest verified partial result and a precise unblock condition.

For a chosen Web build, preserve 0.4.4's delivery discipline: first-target smoke, display-fit/clickability checks, BUILD_ID stamping, separate source/Web hashes, and browser verification of the required player path. Near-release Web verification may run on served localhost; non-loopback LAN routes use HTTPS. Source staging must omit generated `export/web` files.

Validators check structure, records, hashes, and basic media signatures. They do not prove that a log is truthful, a scene is beautiful, a visual is pixel-identical, an idea is historically original, a reviewer is independent, or a player enjoyed the game. State injection helps diagnosis but does not prove normal-path reachability.

## Maintenance

```bash
python -m unittest discover -s tests -v
```

See the [0.5.0 upgrade audit](audit/novel-gameplay-upgrade.md), [strong-agent overconstraint audit](audit/gpt6-overconstraint-audit.md), [research basis](references/research-basis.md), [behavioral scenarios](tests/scenarios.md), and [tool contracts](references/tool-contracts.md). Recorded tests are utility fixtures and static instruction checks, not live Godot, GPT-6/Astra, Codex, browser, or target-player trials.
