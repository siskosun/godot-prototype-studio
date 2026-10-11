# Optional asset lineage

For multi-asset character families, optionally add **designRef** (a project-relative design file), **derivedFrom** (parent IDs in the current manifest), and **runtimeEvidence** (a list of file paths and optional SHA-256 hashes) to asset entries. Keep the original Godot asset manifest and licensing fields intact.

Run `python scripts/validate_asset_links.py MANIFEST PROJECT_ROOT` only when these fields are present. The validator checks source ID uniqueness, project-local reference existence, derivation cycles and optional screenshot checksums. It does not prove asset loading, presentation, animations, ownership or artistic consistency. Inspect real Godot scenes at intended size and follow affected descendants only.

An external Canvas editor is optional, not a required dependency.