# Planner Record: Challenge 0014

Ownership:

- Planner owns this file.
- Planner must not implement code, proofs, or evaluation.
- Planner may update challenge-local checklists only if the change is purely
  organizational and clearly documented here.

## Inputs

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0014-convert-num.md
- Tracking issue: [#220](https://github.com/model-checking/verify-rust-std/issues/220)
- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0014-convert-num`
- Generator record: `docs/verify-rust-std/challenges/0014-convert-num/generator.md`
- Evaluator record: `docs/verify-rust-std/challenges/0014-convert-num/evaluator.md`

## Requirements Extraction

- Published goal: verify the safety of number conversions in
  `core::convert::num`.
- Published success criteria: prove the `NonZero` conversion macros and the
  float-to-int macro family listed in the challenge page, with generated
  contracts for each implementation.
- Challenge-specific UB obligations:
  - no dangling or misaligned loads/stores
  - no reading from uninitialized memory
  - no mutating immutable bytes
  - no producing invalid values
- Additional safety conditions from source docs or SAFETY comments:
  - `NonZero` conversions must preserve the `NonZero` invariant and avoid
    panic for widening `From` paths
  - `try_from` paths must be UB-free, and the out-of-range case must be
    observable as panic
  - float-to-int paths must check finiteness and in-range truncation

## Scope Contract

- In scope for current branch:
  - challenge-local verification harnesses under
    `kmir/src/tests/integration/data/verify-rust-std/0014-convert-num`
  - docs and replay metadata for Challenge 14
- Out of scope unless later justified:
  - semantic changes in `mir-semantics`
  - `stable-mir-json` changes unless a missing lowering or linking artifact is
    shown to block a harness
  - `haskell-backend` changes unless the evaluator proves the backend is the
    real blocker
- Exceptional dependency escalation policy:
  - keep the first wave harness-first
  - classify blockers only after a direct proof/replay command produces a
    concrete frontier

## Sprint Contracts

| Sprint | Intended slice | Acceptance check | Status |
| --- | --- | --- | --- |
| 0 | Bootstrap challenge understanding | Requirements and blockers recorded | complete |
| 1 | Breadth-first harness sweep | First verification-shaped harnesses and coverage table landed | in progress |
| 2 | First validation pass | Replay commands recorded and the initial frontier/state classified | pending |

## Dependencies And Blockers

- No semantic blocker recorded yet.
- Current risk is harness breadth: Challenge 14 fans out across macro-generated
  families, so the first pass should stay representative and auditable rather
  than trying to close the full matrix at once.

## Cross-Challenge Notes

- Reuse the 0011 numeric harness style for proof-shaped integer/float slices.
- Reuse the 0012 coverage-table format if a later numeric family needs more
  granular row-by-row evidence.

## History

- Bootstrap record created by orchestrator.
- First breadth-first harness sweep drafted for widening NonZero conversions,
  narrowing NonZero conversions, and float-to-int conversions.
