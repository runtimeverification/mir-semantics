# Generator Record: Challenge 0014

Ownership:

- Generator owns this file and the implementation work for this challenge.
- Generator must not edit `evaluator.md` or `rubric.md`.
- Generator should treat planner and evaluator edits as authoritative inputs,
  not as files to rewrite.

## Inputs

- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0014-convert-num`
- Planner record: `docs/verify-rust-std/challenges/0014-convert-num/planner.md`
- Evaluator record: `docs/verify-rust-std/challenges/0014-convert-num/evaluator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0014-convert-num/rubric.md`

## Scope Boundary

- Authorized code area: this challenge branch only.
- Default repository scope: `runtimeverification/mir-semantics`
- Allowed secondary scope: `runtimeverification/stable-mir-json` when required
- Exceptional scope: `runtimeverification/haskell-backend` only with explicit
  justification logged here and in the evaluator record

## Work Log

- 2026-04-10: Added the first branch-local breadth-first harness sweep for
  Challenge 14:
  - `kmir/src/tests/integration/data/verify-rust-std/0014-convert-num/nonzero_from.rs`
  - `kmir/src/tests/integration/data/verify-rust-std/0014-convert-num/nonzero_try_from.rs`
  - `kmir/src/tests/integration/data/verify-rust-std/0014-convert-num/to_int_unchecked.rs`
- 2026-04-10: Added the branch-local success-criteria coverage table so each
  macro family has an auditable row with a harness file and start symbol.
- 2026-04-10: Updated the challenge README to separate proof harnesses from
  minimal reproducers and to include replay / CI commands.

## Files Touched

- `docs/verify-rust-std/challenges/0014-convert-num/success-criteria.md`
- `docs/verify-rust-std/challenges/0014-convert-num/planner.md`
- `docs/verify-rust-std/challenges/0014-convert-num/generator.md`
- `kmir/src/tests/integration/data/verify-rust-std/0014-convert-num/README.md`
- `kmir/src/tests/integration/data/verify-rust-std/0014-convert-num/nonzero_from.rs`
- `kmir/src/tests/integration/data/verify-rust-std/0014-convert-num/nonzero_try_from.rs`
- `kmir/src/tests/integration/data/verify-rust-std/0014-convert-num/to_int_unchecked.rs`

## Validation Evidence

- `deps/.stable-mir-json/release.sh -Zno-codegen` succeeded for:
  - `kmir/src/tests/integration/data/verify-rust-std/0014-convert-num/nonzero_from.rs`
  - `kmir/src/tests/integration/data/verify-rust-std/0014-convert-num/nonzero_try_from.rs`
  - `kmir/src/tests/integration/data/verify-rust-std/0014-convert-num/to_int_unchecked.rs`
- A targeted `kmir prove-rs` run was started for
  `verify_nonzero_from_u8_to_u16`; it has not yet been allowed to settle into a
  recorded frontier state.

## Commit Inventory

- Pending first commit.

## Blockers

- No semantic blocker recorded yet.
- The first proof replay is still pending frontier classification.
