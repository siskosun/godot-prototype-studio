# Verification without a compulsory agent organization

Use for a consequential mechanic change, repeated failures, a separate reviewer, or final acceptance. A narrow fix needs its affected check, not every step below.

## Separate responsibilities, not just names

The builder changes the implementation. The reviewer tries to falsify a stated claim against the brief, fixed scenarios and an identified artifact. Give the reviewer the necessary rule specification and run instructions, but not a persuasive defense of the proposed design. Do not hide context needed to evaluate the mechanic.

Use a separate worker only when available and worth its context/coordination cost. Give it a disposable project copy, separate save directory and read-only source/acceptance where the host supports them. It may write observations outside the tested source, not repair the game, lower thresholds or rewrite earlier failures. Parallelize isolated checks, not competing edits of one project or input to one runtime.

A second agent using the same model can share the same blind spots; role separation does not prove independent judgment. With one agent, make a fresh-start self-review and label it as such. No available reviewer is not a routine stop, unless independent review was explicitly contracted. Do not install a multi-agent framework solely to complete this workflow.

Before a consequential review, fix the claim, relevant scenarios, expected observations, falsifier, artifact and review scope. Reuse the brief and mechanic lab instead of creating another acceptance contract. Optionally run:

```bash
python scripts/verification_checkpoint.py freeze PROJECT --plan .prototype/spec/mechanic_lab.md --out .prototype/evidence/review-01.json
python scripts/verification_checkpoint.py check PROJECT --record .prototype/evidence/review-01.json
```

The checkpoint binds artifact, brief and plan hashes. It is NOT a sandbox, a permission mechanism or evidence that tests ran. Check before and after review; changes require a new checkpoint and affected retest. Keep logs/captures separately identified. Use existing release identities for exact source/Web delivery; this checkpoint does not replace them.

## Match observations to actual capabilities

Use existing Godot CLI, editor, project-native QA hooks or an already working bridge. Do not build a universal controller by default. The optional starter currently offers snapshots, event records and scenario setup, not autonomous play, screenshot capture or a remote editor.

For each needed operation, record the actual adapter/command, a successful probe and its evidence level. Unsupported operations remain UNVERIFIED, not imaginary API methods.

| Operation | Evidence contract |
|---|---|
| Start / stop / restart | Confirm the actual process and current artifact; reset only disposable test saves |
| State / legal actions / events | Read authoritative rules; distinguish unavailable data from an empty valid set |
| Input / replay | Record event source, press/release edge, timing and application focus; observe the resulting transition |
| Named scenario setup | Mark SETUP_ONLY; also run a clean-launch path without privileged setup |
| Screenshot / audio / performance | Bind to scene, viewport, artifact and timestamp; inspect actual output, not merely file existence |

Distinguish OS/device input, browser automation, engine-injected InputEvents, Input.action_press polling and direct model/state mutation. Godot's action_press does not invoke Node._input; parse_input_event does, but does not operate the OS. Engine event injection therefore cannot alone prove window focus, browser gestures or physical-device input. Label what was actually tested.

Keep test hooks local and limited to declared operations. Do not open a network listener, remote shell or arbitrary script executor for convenience. If a separate integration is commissioned, specify authentication, binding, cleanup and export removal before implementing it.

## Diagnose before changing direction

A failure can belong to the mechanic, implementation, presentation, scenario opportunity, test harness or host. Reproduce and classify it before rejecting the design. A bot failing to find a strategy is not proof no strategy exists; repeated actions can be intentional in rhythm, idle or expressive play.

Use RETAIN / REVISE / REJECT / INCONCLUSIVE from the mechanic lab. Rejection is scoped to the tested hypothesis and conditions, never a permanent ban on an entire mechanic. If evidence is unavailable, choose INCONCLUSIVE rather than inventing a pass or kill threshold. A candidate surviving probes is not proven fun, historically novel or marketable.

Expand repeated content only after a representative instance works in context. Keep its relevant rules/interfaces stable, check mechanically verifiable properties across the batch, sample presentation where adequate, and inspect every critical outlier. Recheck the exemplar when a shared dependency changes. One good enemy or asset does not certify every variant.

Source: Godot Input reference, https://docs.godotengine.org/en/4.6/classes/class_input.html (consult the project's version when different). Verification separation and checkpoints are this skill's engineering choices, not measured creative-uplift claims.
