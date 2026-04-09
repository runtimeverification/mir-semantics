# Planner Record: Challenge 0012

Ownership:

- Planner owns this file.
- Planner must not implement code, proofs, or evaluation.
- Planner may update challenge-local checklists only if the change is purely
  organizational and clearly documented here.

## Inputs

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0012-nonzero.md
- Tracking issue: [#71](https://github.com/model-checking/verify-rust-std/issues/71)
- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0012-nonzero`
- Generator record: `docs/verify-rust-std/challenges/0012-nonzero/generator.md`
- Evaluator record: `docs/verify-rust-std/challenges/0012-nonzero/evaluator.md`

## Requirements Extraction

- Published goal: verify the safety of `NonZero` in `core::num`.
- Published success criteria:
  - Part 1: verify `NonZero::new` and `NonZero::new_unchecked` with the stated preconditions.
  - Part 1 correctness: an object is created iff the input is nonzero, and the resulting value equals the input.
  - Part 2: verify the full published `core::num::nonzero` API list, including `max`, `min`, `clamp`, `bitor` (all 3 impls), bit operations, byte-order conversions, arithmetic, powers, signed-only ops, unsigned-only ops, and `from_mut` / `from_mut_unchecked`.
- Challenge-specific UB obligations:
  - no compiler-intrinsic UB
  - no reads from uninitialized memory
  - no invalid values
- Additional safety conditions from source docs or SAFETY comments:
  - `new` and `get` rely on transmute safety assumptions; the challenge page permits using same-size contracts instead of proving the full transmutation story
  - `ZeroablePrimitive` assumptions are allowed for the integer primitives used by `NonZeroInner`

## Scope Contract

- In scope for current branch:
  - `library/core/src/num/nonzero.rs`
  - minimal supporting contracts or loop-invariant adjustments in `library/core/src/num/uint_macros.rs` and `library/core/src/num/int_macros.rs` if proof obligations require them
  - challenge-local docs and proof artifacts
- Out of scope unless later justified:
  - `runtimeverification/stable-mir-json`
  - `runtimeverification/haskell-backend`
- Exceptional dependency escalation policy:
  - only escalate outside `core` if a proof failure is clearly attributable to missing backend support rather than a missing contract, harness, or bounded proof strategy

## Sprint Contracts

| Sprint | Intended slice | Acceptance check | Status |
| --- | --- | --- | --- |
| 0 | Bootstrap challenge understanding | Requirements, review feedback, and likely proof hazards recorded | complete |
| 1 | Rebuild the reviewed NonZero baseline | Generator has a branch-local implementation plan that maps every published API to explicit semantic assertions and evidence | pending |
| 2 | Tighten the remaining review-sensitive cases | Evaluator can point to exact harnesses, bounds, and any justified exclusions | pending |

## Dependencies And Blockers

- Public review feedback on the existing solution PRs indicates the obvious baseline is not enough unless the harnesses assert semantic behavior, not just nonzero-ness.
- Wider `isqrt` and 128-bit `pow` cases may need explicit bounds or a documented performance rationale.
- No backend escalation is known yet.

## Cross-Challenge Notes

- Challenge 11 showed that small `uint_macros.rs` / `int_macros.rs` adjustments can be justified when they unblock proof obligations.
- Challenge 12 has strong reuse potential from public PRs `#544` and `#565`, but the evaluator should score explicit semantic assertions separately from pure UB-safety checks.
- Any bounded 128-bit proof strategy should carry its own documented rationale so later review can distinguish accepted scope limits from missing coverage.

## History

- Bootstrap record created by orchestrator.
- Requirements extraction updated from the upstream challenge page and public review history on 2026-04-09 UTC.
