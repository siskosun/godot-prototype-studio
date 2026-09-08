# Instruction audit for maintainers

Use the user's supplied 'Rethinking skills and prompts' article as an editorial lens, not evidence of a particular model's capability. Do not encode a model release name as a permission or testing assumption.

## Audit questions

1. Is the description a short, specific trigger rather than a workflow, sales pitch, or catch-all?
2. Does the root route only necessary references, with one-hop links and no compulsory bulk reading?
3. Does each recurring rule have one authoritative home? Remove competing scope, permission, completion, and evidence definitions.
4. Is a step a real result constraint or an obsolete recipe? Retain only procedures that prevent a concrete failure.
5. Does every 'ask', 'approve', 'stop', or gate have a reason grounded in authority or unavailable evidence? Aesthetic uncertainty inside delegation and a first implementation must not force a stop.
6. Do autonomy and simplicity instructions preserve the explicit requested quality, safety, and platform target?
7. Is testing proportionate to changes yet sufficient for final claims? Are unavailable tests reported rather than passed?
8. Do scripts enforce the documented rule? Look for exit-code-only success, skipped checks counted as passing, missing files, stale hashes, and unsupported independence claims.
9. Does each long-lived document still help a real decision or reproducible action? Prefer one brief and one concise progress record over stacks of overlapping templates.
10. Can the skill complete or give an evidenced blocker without asking the user to operate the workflow?

## Behavioral regression cases

Review `tests/scenarios.md` after material changes. Check one-idea completion, brief-approval reservation, targeted bug fix, current-game research failure, shader licensing/renderer mismatch, missing optional tooling, unavailable required platform, self-review versus independent review, late artifact changes, and scope pressure. Record whether this was a static walkthrough or an actual agent run.

Run `python -m unittest discover -s tests -v` and the skill packager. These tests check tools and instruction structure; they do not establish real-game completion rates. Report any untested engine or live-agent behavior explicitly.

## Near-release regression audit

Check the quality profile against intent: requests to finish a playable/high-completion game get the higher bar; mechanic spikes, quick grayboxes, technical proofs and narrow fixes do not inherit it from the word “prototype”. Check all nine dimensions for applicability. `NOT_APPLICABLE` must describe a genuinely absent requirement, while unavailable evidence is `UNVERIFIED`. Optional human evidence must not become routine interruption or a false fun claim. Verify that findings use severity honestly and keep old failure identity plus current retest.

Stress-test the art process against drift, collage, unreadability, animation boiling and weak in-engine composition; canonical references alone do not pass this audit. Stress-test gameplay against trivial choices, over-easing, purely decorative content and evaluator gaming. Cold start, recovery, supported input, text rendering and exact export are part of the actual player journey. For Web, stress-test accidental project-root serving, LAN HTTP, insecure/self-signed context assumptions, stale BUILD_ID/cache, oversized backing canvas, missing payload files, promised audio silence, desktop-only CJK fallback, and unnecessary COOP/COEP on single-thread builds.

Run focused negative cases before broad repetition. Prefer correcting a concrete gap over adding another protocol. A final audit with no unresolved material finding is a bounded review result, never proof of perfection.
