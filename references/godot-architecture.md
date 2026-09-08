# Godot architecture and selective patterns

Preserve the existing project's language and ownership. For a blank 2D project, use Godot 4.x, typed GDScript and a renderer suitable for the target; do not upgrade Godot or switch C# to GDScript just to use sample code.

## Pattern selection

| Concrete need | Smallest useful pattern | Avoid |
|---|---|---|
| Few exclusive states | Enum and explicit transitions | Framework per trivial actor |
| Complex behavior with distinct lifecycle | Scene-local state objects/nodes | Hidden transitions scattered through UI |
| Local parent/child collaboration | Direct calls down; signals for events up | Global event bus for local state |
| Shared designer data | Resource or existing data format | Mutating a shared asset as live instance state |
| Cross-scene service | Focused existing/autoload service | Omniscient GameManager |
| High-churn spawning with measured cost | Targeted pool with complete reset | Pooling everything in advance |

The external `godot-gdscript-patterns` skill is a source of options, not a requirement to instantiate them all. Check copied examples against the actual version and lifecycle. Do not import save encryption, global buses, or component frameworks by default.

## Implementation invariants

Keep authoritative gameplay rules in one place. Tests must exercise the same logic, not a simplified duplicate. Use scene/physics tests when separating a pure model would reproduce Godot incorrectly.

Use InputMap for player verbs, `_physics_process` for physics, frame-rate-correct timing, and designer-facing exports for relevant tuning. Observe node lifetime across awaits, signal connection duplication, scene ownership, resource paths/UIDs, and shared Resource mutation. Give physics behavior to the engine rather than building a parallel simulator.

Edit simple text scenes/resources directly when appropriate and validate in Godot. Prefer engine-aware tools for fragile imported structures, animation tracks, TileSets, or live transforms. Never hand-edit `.godot/` cache state. Preserve formatting conventions instead of importing an upstream naming rule or ceremonial trailing `pass`.

Add only the minimum QA observation seam: state snapshot, useful events, deterministic setup where appropriate. Keep test-only control inaccessible in ordinary release play. Do not let a QA endpoint set the final victory state and count that as a playthrough.
