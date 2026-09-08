# Scope discipline without under-delivery

Optimize the smallest complete result, not minimum lines of code or minimum effort. A presentable prototype can have few systems and still require careful controls, animation, sound, feedback, recovery, and layout.

Before adding a system or dependency, ask which brief requirement or observed defect it resolves. Prefer, in order: omit an unnecessary feature; reuse the project; use native Godot behavior; use an already justified dependency; write small local code; add a dependency only when its net benefit is concrete. This is a decision habit, not a mandatory research pass before each edit.

## Practical Godot defaults

Use Control containers and themes for UI before custom layout engines; Timer/Tween/AnimationPlayer for timing and animation; InputMap for player verbs; ordinary scenes and signals for composition. Use a local enum before a state-machine framework when the behavior is small. Use Resources when shared content truly benefits. Pool objects only after profiling or a known high-churn requirement supports it.

Do not install a global framework to gain a toast, sound effect, or transition. Do not introduce an ECS, event bus, networking stack, dependency container, save framework, generic editor, or plugin ecosystem without a current requirement. Preserve justified existing architecture rather than replacing it just to make a smaller diff.

## What may be cut

Cut speculative modes, extra content breadth, unused abstractions, premature optimization, unrelated refactors, duplicate documents, and showcase tooling unrelated to the user's deliverable. Record only important deferrals and the condition that would justify them.

## What may not be cut

Do not remove an explicit mechanic, supported input, accessibility condition, critical visual feedback, failure/retry path, required persistence, safety guard, or target-platform test. Never silently substitute a mock for required real networking or a static image for an animated gameplay object. Do not declare 'minimal prototype' after the user requested a presentable one.

The first complete loop is a foundation, not completion. After it works, prioritize the largest remaining gap to the brief: unclear action, weak response, missing recovery, inconsistent art, incomplete session, or delivery failure. Add further content only when needed to expose the promised experience.

Stop polishing when the stated quality conditions are met and another pass would be speculative preference churn. Keep code readable; one-liners, fewer files, and deletion are not independent goals.
