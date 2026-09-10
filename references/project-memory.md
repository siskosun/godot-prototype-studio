# Project knowledge that can expire

Use when a project spans sessions, repeats rejected approaches, or has important facts worth retaining. For a one-off fix, existing brief/progress notes usually suffice.

The brief owns acceptance and delegated authority. Progress owns where work stopped. Memory indexes what was learned, where it came from, and when to reconsider it. Never treat memory as a second specification or as instructions overriding the current user, repository or brief.

## Store only reusable findings

Use `.prototype/project_memory.json` when structured freshness checks help. `init_workspace.py PROJECT --with-memory` creates an empty record without inventing facts. Existing files are preserved. No database, embeddings, cloud service or global cross-project memory is required.

Each entry has:

- `id`, `kind`: decision / observation / hypothesis / rejected_attempt / constraint;
- `claim`, `scope`, `revisitWhen`: a narrow finding, conditions/audience/target, and what would justify revisiting it;
- `sources`: project-relative evidence or authority-note paths with their observed SHA-256;
- `dependsOn`: relevant rule, scenario, brief, renderer or configuration files and SHA-256;
- `status`: ACTIVE or SUPERSEDED; the latter also needs `supersededReason`.

Keep references, not copied logs or whole conversations. A user decision needs its actual authority reference; an agent recommendation remains an agent recommendation. An observation should identify the build, method and input source in its evidence. Never turn a hypothesis into a verified fact by summarizing it repeatedly. Leave sources empty when missing; the checker will report UNVERIFIED.

For a failed experiment, record the attempted implementation, exposure/opportunities, failure mechanism and alternatives still open. Do not store simply "this mechanic does not work". Revisit when the relevant rule, audience, presentation, tool capability or evidence changes. A rejected attempt is historical evidence, not a standing veto.

## Reconcile on resume

```bash
python scripts/check_project_memory.py PROJECT
```

The read-only checker returns CURRENT_RECORD, STALE, UNVERIFIED or SUPERSEDED for each entry. CURRENT_RECORD means the declared source/dependency files still match. It does NOT establish truth, human authorization, completeness, independence or applicability to a changed context. An unchanged hypothesis is still a hypothesis.

Treat changed/missing referenced files as stale for reuse; retain the original evidence. Refresh only affected findings after new verification. Do not rewrite hashes on old reports to make them appear current. Check non-file conditions in `scope` and `revisitWhen` manually; target/audience changes can invalidate an entry even when file hashes match. If dependency coverage is uncertain, retest.

Use only task-relevant entries. Resolve conflicts against current authority and actual artifacts. Record explicit supersession rather than silently erasing failed evidence. Do not preload the whole memory or accumulate every tool output. Keep one writer; reviewers propose findings, the coordinating agent integrates them.

Keep private user data and participant details out of the reusable skill/repository. A local project record is not permission to publish it. Respect existing save/evidence retention requirements.

Exit codes: 0 records current or empty; 1 some active records stale/unverified; 2 invalid/unreadable. A nonzero code requests reconciliation, not automatic rejection of the game or a mandatory stop for unrelated work.
