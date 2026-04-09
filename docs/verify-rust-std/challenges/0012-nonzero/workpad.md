# Workpad: Challenge 0012

## Decision Log

- 2026-04-09 UTC: Chosen as the next active batch candidate because the public solution history is rich and the review feedback already points to the exact weakness to fix.
- 2026-04-09 UTC: The branch-local planning target is to convert the public NonZero baseline into a stricter semantic proof set, not to invent a new proof strategy.

## Evidence Collected

- Upstream challenge page confirms the goal, the Part 1 correctness requirements, the full Part 2 API list, and the UB obligations.
- PR `#565` review feedback says the prior solution is "a solid first submission" but still too thin because most Part 2 harnesses only prove non-UB.
- PR `#544` review feedback points out that `isqrt` coverage is incomplete unless wider unsigned types are added or a bound/rationale is documented.

## Reuse Candidates

- Public solution PR `#544` is the best baseline for harness shape and coverage matrix.
- Public solution PR `#565` is the best baseline for the narrower Part 1 / Part 2 framing and for the review-driven readiness criteria.
- Small core-side verification helpers, if needed, should stay limited to `uint_macros.rs` and `int_macros.rs`.

## Handoff To Generator

- Start by reconstructing the reviewed public baseline in this branch.
- Strengthen any harness that only checks `get() != 0` so it also asserts the expected semantic relation when the API has one.
- Keep any bounded 128-bit proof strategy explicit and documented.

## Handoff To Evaluator

- Score semantic specificity separately from coverage.
- Require explicit evidence for any omitted wide-type case or bounded proof case.
- Treat any unsupported backend escalation as a last resort, not as the default path.

