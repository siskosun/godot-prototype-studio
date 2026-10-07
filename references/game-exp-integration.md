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

An optional [design/source repair map](design-repair-loop.md) stays in GPS execution state. Its diagnostic candidates never expand Manifest scope. `LOCAL_REPAIR_VERIFIED` is participant-reported implementation evidence; use the existing exact-source evidence handoff and trusted checks. Do not add it as a Ledger lifecycle, Review outcome or immutable-playable mutation.

## Variant rule

Local implementation variants inside one Candidate may be resolved by GPS when the choice is delegated and evidence is adequate.

Variants that correspond to different game-exp Candidates or experiment branches are comparison evidence only. Return observations to game-exp and wait for the human-owned selection gate.

## Iteration delivery

After each completed GPS implementation pass, return one `iteration_delivery` object for game-exp:

```json
{
  "changes": ["player-visible change"],
  "playable": {
    "kind": "SHAREABLE_URL | LOCAL_URL | ARTIFACT_ONLY | MISSING",
    "verified": true,
    "url": "https://... or http://127.0.0.1:...",
    "artifact_url": "https://...",
    "launch_hint": "optional short instruction"
  },
  "focus_points": ["1-3 things the human should feel/check"],
  "producer": "godot-prototype-studio",
  "build_id": "optional build identity",
  "previous_candidate_id": "optional real prior Candidate id"
}
```

Rules:

- report only URLs or artifacts verified against this exact source/build;
- use `SHAREABLE_URL` only for an intended cross-device URL;
- use `LOCAL_URL` for localhost/LAN or another environment-bound URL;
- use `ARTIFACT_ONLY` when a verified downloadable artifact exists but there is no direct playable URL;
- use `MISSING` with `verified=false` when no verified playable entry exists; never invent a URL;
- include `previous_candidate_id` only when it names a real Candidate from this experiment;
- this object is `participant_reported`; it cannot create trusted Review or lifecycle evidence.

When releasing the game-exp Work Claim, place this object under `delivery`. game-exp may project it as `experiment_panel.delivery_card`.

## Public shareable playable

When the game-exp handoff includes `delivery_request.prefer_shareable_url=true`, the repository is public, and this implementation pass has a compatible Web target:

1. export the exact pushed source to `export/web/`;
2. finish all post-export mutations and stamp the final BUILD_ID;
3. run the normal local Web/browser checks first;
4. require a non-threaded Pages-compatible Web preset (`variant/thread_support=false`);
5. use the exact pushed `result_source_sha` as the immutable version key;
6. publish with:

```bash
python <skill-root>/scripts/publish_github_pages.py \
  --repo owner/repo \
  --source export/web \
  --version-key <result_source_sha> \
  --producer godot-prototype-studio \
  --json
```

The publisher writes only the dedicated `gh-pages` delivery branch, then dispatches the managed `.github/workflows/game-exp-pages.yml` workflow from the repository default branch. It never edits the canonical experiment branch, protected Ledger, Candidate refs, or lifecycle state. Each version is retained under `play/<result_source_sha>/`; the same version key with different bytes is rejected instead of overwritten.

The publisher's served marker/index check proves deployment identity, not Godot runtime behavior. Open the returned HTTPS URL in a real browser and run `WEB_PREFLIGHT` against that URL with the matching browser report before returning `playable.kind=SHAREABLE_URL` with `verified=true`.

GitHub Pages is not the route for a Web export that requires thread support/cross-origin isolation. If Pages is unavailable, the managed Pages workflow is missing, already configured to another source, permission is insufficient, the Web target is incompatible, or remote browser verification fails, do not rewrite unrelated hosting. Return the strongest actually verified fallback: `LOCAL_URL`, `ARTIFACT_ONLY`, or `MISSING`.

## Handoff

Report the current experiment/Candidate identity alongside GPS evidence. If game-exp is unavailable, preserve the evidence locally but mark Candidate/lifecycle linkage as unverified rather than inventing experiment state.
