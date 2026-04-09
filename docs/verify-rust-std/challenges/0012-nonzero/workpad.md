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

## Generator Retry Execution Log

- Ported six prerequisite semantic-fix commits from
  `verify-rust-std/challenge-0012` in chronological order:
  `01578d44`, `bb4813b2`, `22fd4eec`, `6f1c072a`, `9b55225b`, `8347764a`.
- Port included transmute reinterpretation handling, unions payload read fixes,
  union regression rename updates, `assert_inhabited` failure prioritization,
  and pointer-cast projection preservation updates.
- Narrow collection confirmed the expected affected tests:
  `test_prove[transmute-maybe-uninit-i128]` and `test_prove[unions]`.
- Initial targeted execution failed due to missing local compiled definitions.
  Ran `make build` and reran the same targeted tests successfully.

## Validation Snapshot

- `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_prove --collect-only -k "transmute-maybe-uninit-i128 or unions" -q`
  - Outcome: `2/110` selected, exact target tests collected.
- `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_prove -k "transmute-maybe-uninit-i128 or unions" -q`
  - Outcome: fixture setup error due to missing
    `~/.cache/kdist-.../mir-semantics/haskell`.
- `make build`
  - Outcome: success; required definitions rebuilt.
- `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_prove -k "transmute-maybe-uninit-i128 or unions" -q --maxfail=1`
  - Outcome: `2 passed, 108 deselected in 122.64s`.

## Remaining Gap After This Slice

- The prerequisite semantic/test slice now appears healthy and validated, but
  Challenge 0012 still lacks challenge-specific `NonZero` harness and contract
  artifacts on this re-execution branch.
- Evaluator should keep status at `IN PROGRESS` until branch-local NonZero
  verification work is implemented and validated.
