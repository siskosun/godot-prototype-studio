# Save Matrix

Adapt the rows to the actual project while preserving equivalent coverage.

| Scenario | Expected run state | Expected meta state | Result | Evidence |
|---|---|---|---|---|
| Stable checkpoint -> reload | restored | preserved | TBD | |
| Settings/navigation round trip | preserved | preserved | TBD | |
| Completion and settlement | cleared/archived by contract | preserved/updated | TBD | |
| Repeat settlement same runId | no duplicate reward | unchanged after first settlement | TBD | |
| Corrupt or truncated save | safe fallback | safe fallback | TBD | |
| Incompatible schema | migrate or safe reject | migrate or safe reject | TBD | |
