# Design-to-source local repair

Use when repeated generation/debugging loses track of which designed object or interaction owns a failure. Skip this record for a trivial isolated edit. Keep the existing brief as acceptance; this is an implementation index, not a second design contract.

## Minimal representation

Create `.prototype/spec/design_map.json` using `templates/design_map.json`. The example maps the thin starter; adapt it before using it on another project. Keep only consequential objects/interactions and scenarios:

- `objective.success` / `failure`: observable completion or failure, including an explicit not-applicable condition for a sandbox;
- `elements`: stable semantic `id`, `role`, source `bindings`;
- `interactions`: stable `id`, participant element IDs, trigger, preconditions, state change, source bindings;
- `scenarios`: stable `id`, interaction IDs, check (`import`, `test`, `smoke`), literal failure marker, test-source bindings.

Each binding has a normalized project-relative `path` and a literal `anchor` that occurs exactly once in that file. Bind a Godot scene declaration, script/state field, or logic function as applicable. Logical entities drawn procedurally need not become artificial Nodes. Add existing placement/accessibility constraints to the role or rule text only when relevant; this tool does not solve spatial constraints or interpret a new gameplay language.

Keep semantic IDs when a file, Node or implementation changes. Update bindings on an explicit new baseline. Validation checks references/files/anchors; it does not establish runtime Node identity, collision, reachability, correct behavior, or design quality.

## Observe → localize → repair → replay

1. Validate the map against current source.
2. Run the actual checks with `--design-map`; preserve the failing report/plan before the next run replaces logs.
3. Inspect `localRepair`: a matched failing scenario identifies its interactions and participant elements; an engine `res://` path produces file-level candidates, not a confirmed root cause.
4. Make the smallest justified implementation change inside authoritative project/game-exp scope. The suggested files narrow diagnosis; they never grant edit authority. Leave the failing oracle and semantic IDs intact.
5. Run the same commands against the repaired source, then verify against the saved plan. Rerun the affected real player/browser path separately when the change requires that evidence.

The command snapshots editable project files plus a separate design-map digest before execution. An old/unbound report, changed full log, source change during the run, unknown failure or environment/tool failure cannot produce a verified repair. First Godot import may create `.gd.uid` files; establish that import baseline, then rerun checks to bind evidence to the resulting source.

`verify` requires a fresh source-bound report, unchanged map, changes only in the suggested implementation files, the original check commands, and executed PASS for required checks. A skipped test, alternate always-passing script or smoke-only rerun cannot replace the original gameplay test. Scenario/oracle files are excluded from suggested repair paths. A confirmed harness defect needs its own diagnosis and baseline.

Statuses:

| Status | Meaning |
|---|---|
| `MAP_VALID` | Static index is internally consistent |
| `REPAIRABLE` | Observed failures have implementation candidates; inspect before editing |
| `INCONCLUSIVE` | Identity, localization, environment, scope or reproduction is insufficient |
| `NO_FAILURES` | This identified check run reported no failure |
| `LOCAL_REPAIR_VERIFIED` | Local file scope and same-command regression checks match the saved plan |

All records remain `PARTICIPANT_REPORTED`. File-granularity checks cannot prove only one function changed or that the patch caused the improvement. They do not record human Review, change game-exp lifecycle, replace trusted replay, select a Candidate, or authorize publishing. If the authoritative scope conflicts with a suggested path, obey that scope and return the conflict. Published builds remain immutable; a repaired source needs a new build identity and the existing publication flow.

## Commands

Run from the prototype root; substitute the installed skill's absolute path for `GPS`:

```bash
python GPS/scripts/design_repair.py validate . --map .prototype/spec/design_map.json
python GPS/scripts/run_godot_checks.py . --mode all --design-map .prototype/spec/design_map.json
python GPS/scripts/design_repair.py plan . --map .prototype/spec/design_map.json --report .prototype/evidence/godot-checks/report.json --write .prototype/evidence/repair-before.json
# Inspect the candidates and edit only the responsible source inside the authorized scope.
python GPS/scripts/run_godot_checks.py . --mode all --design-map .prototype/spec/design_map.json
python GPS/scripts/design_repair.py verify . --map .prototype/spec/design_map.json --plan .prototype/evidence/repair-before.json --report .prototype/evidence/godot-checks/report.json --write .prototype/evidence/repair-after.json
```

Keep the first failure and saved plan outside any served artifact. After this implementation pass, use the existing GPS → game-exp evidence handoff; do not copy the map into the protected Ledger or change its schemas.
