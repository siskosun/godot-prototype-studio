# game-exp integration

Use this file only when the current Godot project is controlled by game-exp.

## Authority split

game-exp is the experiment control plane. Its protected Ledger and Manifest own:

- experiment id, subject, lifecycle, and canonical experiment branch;
- `scope.allowed` and `scope.avoid`;
- success/kill criteria and experiment-level review protocol;
- Candidate identity and retention;
- human Review, PROMISING, SELECTED, REJECTED decisions;
- Rehearsal, Integration, and Archive state.

GPS owns the game-development execution layer:

- design and implementation inside the allowed scope;
- Godot/runtime/debugging work;
- gameplay/UX/art/audio polish;
- automated checks, browser checks, replay traces, and playtest preparation;
- evidence describing exactly what artifact was observed.

The mission brief is the implementation-and-delivery contract **inside** the game-exp Manifest. It must not override the Manifest or become a second experiment lifecycle.

## Start work

Before editing, resolve the authoritative:

1. experiment id and lifecycle;
2. `subject.id`, name, and root path;
3. canonical `exp/<issue>` branch;
4. allowed/avoided scope;
5. current Candidate id when one exists;
6. experiment criteria relevant to this implementation pass.

Do not infer these from local labels, filenames, branch descriptions, or a rendered Board when game-exp state is available.

If the lifecycle or branch does not permit the requested source edit, stop the edit and return to the valid game-exp gate.

## Evidence handoff

When evidence will support a game-exp Candidate, bind it to the exact artifact where possible:

```text
experiment_id
candidate_id
source_sha
artifact_identity
scenario
evidence_type
generated_at
```

Do not relabel agent/self-reported observations as trusted human evidence.

GPS checks may establish implementation or runtime facts. They never by themselves authorize Review PASS/FAIL, PROMISING, SELECTED, or REJECTED.

## Variant rule

Local implementation variants inside one Candidate may be resolved by GPS when the choice is delegated and evidence is adequate.

Variants that correspond to different game-exp Candidates or experiment branches are comparison evidence only. Return observations to game-exp and wait for the human-owned selection gate.

## Handoff

Report the current experiment/Candidate identity alongside GPS evidence. If game-exp is unavailable, preserve the evidence locally but mark Candidate/lifecycle linkage as unverified rather than inventing experiment state.
