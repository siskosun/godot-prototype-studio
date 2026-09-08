# Godot Prototype Studio 0.5.0 upgrade audit

## Requested changes

1. Improve strong-agent performance on genuinely new gameplay, especially for GPT-6/Astra-style autonomous engine work.
2. Require reference-image intake for new prototype requests.
3. Distinguish partial visual reference from pixel-accurate reference.
4. When images are already present, ask only how to use them.
5. Preserve the 0.4.4 delivery/evidence improvements and update README/tests.

## Implemented design

### Visual-reference contract

The first response resolves exactly one of four modes: `PARTIAL_REFERENCE`, `PIXEL_ACCURATE_REFERENCE`, `ORIGINAL_DELEGATED`, or `NOT_APPLICABLE`. Partial use binds only named visual properties. Pixel use binds a declared frame, state, camera, crop, viewport/backing resolution, authorized assets/fonts, allowed differences, and rights status. Existing images are not requested again, and already stated modes are not reopened.

### Novel-gameplay lab

The agent expresses a mechanic as a causal player loop, identifies a familiar anchor and one primary design delta, removes theme to test whether the difference survives, and states a falsifier. It rejects weak candidates through short state traces before production, then implements the smallest repeatable Godot kernel with authoritative observability.

The evidence loop is: reproduce through real input -> inspect state and screenshots -> trace the owning code -> change one causal relation -> rerun. Variant comparisons hold scenario, input, target, readability, and opportunity exposure constant. Spam, waiting, dominant-action, boundary, recovery, and second-run probes are explicit.

### 0.4.4 preservation

Version 0.5.0 retains 0.4.4's separation of craft quality from package form and evidence; early first-target smoke; Web display-fit/clickability checks; first-sample alpha/pivot inspection; package/change-impact tooling; and resumable session status. The new mechanic lab is optional and does not replace the mission brief.

### Human/model boundary

Automated policies diagnose rules and reachability. They do not prove enjoyment, preference, accessibility, or historical originality. Human playable comparisons remain the strongest available evidence for feel; absence is disclosed instead of converted into a model score.

## Instruction-economy review

The root `SKILL.md` remains under the repository's compact-router threshold. Detailed novelty and visual-intake logic lives in focused references. No fixed architecture, iteration count, model tier, or tool bridge was introduced.

## Verification boundary

Regression tests cover opt-in mechanic-lab initialization, preservation of user-owned records, visual-mode validation, and legacy mission-brief compatibility. These tests validate deterministic behavior and instruction consistency; they are not a live GPT-6/Astra benchmark, real Godot playtest, pixel-diff acceptance, or target-player study.
