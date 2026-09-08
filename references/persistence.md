# Persistence and save evolution

Add persistence only when the brief, existing game, intended session, or promised settings/progression requires it. Do not add a save architecture to a disposable one-round toy; do not omit requested continuation just to keep the implementation small.

Keep run state and persistent profile/settings distinct when both exist. Serialize stable identifiers and values rather than transient node references. Use the project's established format. For a small prototype, native FileAccess plus shape-validated JSON may suffice; do not invent encryption or cloud sync without a requirement.

Version the payload from its first implementation. Validate types and ranges, reject corrupt/incompatible data safely, and define supported migrations. Preserve material user data and use platform-appropriate atomic writing when loss matters. Do not store credentials in game saves.

Exercise only applicable failure paths: checkpoint/reload/continue, settings round trip, completion/settlement, duplicate settlement, corrupt/truncated payload, incompatible schema, missing optional fields, target-platform storage, and reset/overwrite behavior. Record the identified build, actions, expected and actual state, and recovery result. A successful write alone does not prove safe persistence. `templates/save_matrix.md` is an optional coverage aid, not a requirement to implement rewards or meta progression.
