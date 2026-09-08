# Change impact and evidence reuse

Use the cheapest adequate suite for what actually changed. Exact delivery still needs the evidence required by the brief. Reused evidence is valid only when the matching identity hash is unchanged.

## Three identities

Compute them with `package_and_report.py` or `artifact_identities` in `_identities.py`:

| Identity | Typical files | Reuse meaning |
|---|---|---|
| `gameContent` | scenes, game scripts, runtime assets | Rule/replay evidence may be reused |
| `testHarness` | `tests/`, `qa/`, browser/harness scripts | Harness edits do not invalidate game rules |
| `package` | source ZIP or delivery archive | Packaging/docs edits need contents/hash checks |

Also record `displaySet` (fonts, themes, UI) and `packaging` (docs, release notes) so a theme change does not look like a mechanic change.

## Suites

| Changed class | Rerun | Do not rerun by default |
|---|---|---|
| `rules` | Logic, seed/replay, and the affected player path | Unrelated display or packaging paperwork |
| `display` | Fonts, UI, canvas, text, Web display-fit | Full seed batteries whose `gameContent` hash is unchanged |
| `harness` | The edited tests/preflight scripts | Game-rule suites whose `gameContent` hash is unchanged |
| `packaging` | ZIP membership, hashes, run instructions | Gameplay or display suites whose identities are unchanged |

`python <skill-root>/scripts/change_impact.py --before-tree OLD --after-tree NEW` lists `rerun` and `reused`. `--changed-paths` is enough when the file list is already known; supply before/after identity JSON to prove reuse.

Two source packages that differ only in browser test scripts keep the same `gameContent` hash. Record that hash and rerun the harness, not an unchanged 200-seed rules battery.

## Resume

Keep `.prototype/progress.md` or the delivery `session_status.md` to: version, current artifact/BUILD_ID/source hash, passed checks, open issues, run commands, next step. On interrupt recovery, reconcile that status with current identities before doing any work. Do not restart brief, research, and packaging from scratch.
