# Compare only decision-relevant alternatives

Use for an unresolved gameplay, UX, visual or performance hypothesis. Do not generate multiple full games or force A/B testing when the current fix is clear.

Record one baseline, changed dimension or coupled bundle, invariants, common scenario, observations and rollback. Hold target conditions and opportunities comparable. Changes to art must not secretly change timing/rules. Reuse configuration/Resource overrides where possible. Report which components cannot be separated causally.

Prefer actual before/after play and concrete observations. Numerical measures need declared units, direction and sufficient comparable runs. Do not rank aesthetic quality by an invented score or infer a robust winner from a tiny timing difference. A variant that fails a required condition cannot win on a weighted average.

Within delegated design/art authority, retain the best justified **local implementation variant** or the strongest baseline and continue the build. Call that choice an agent decision, not a human preference.

If game-exp manages the work, this autonomy stops at the Candidate boundary. GPS may compare Candidates or experiment branches, but it must not select one, record Review PASS/FAIL, promote to PROMISING/SELECTED, or reject a Candidate. Return the evidence to the game-exp human gate.

The optional `compare_prototypes.py` reads an existing comparison record, checks fields and evidence references, and reports deterministic metric dominance among complete finite measurement sets. It cannot select taste, prove execution, or judge noise/significance. Use its script contract for exact fields; do not create the record for an obvious local fix.
