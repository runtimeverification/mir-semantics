# Generator Record: Challenge 0029

Ownership:

- Generator owns this file and the implementation work for this challenge.
- Generator must not edit `evaluator.md` or `rubric.md`.
- Generator should treat planner and evaluator edits as authoritative inputs,
  not as files to rewrite.

## Inputs

- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0029-boxed`
- Planner record: `docs/verify-rust-std/challenges/0029-boxed/planner.md`
- Evaluator record: `docs/verify-rust-std/challenges/0029-boxed/evaluator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0029-boxed/rubric.md`

## Scope Boundary

- Authorized code area: this challenge branch only.
- Default repository scope: `runtimeverification/mir-semantics`
- Allowed secondary scope: `runtimeverification/stable-mir-json` when required
- Exceptional scope: `runtimeverification/haskell-backend` only with explicit
  justification logged here and in the evaluator record

## Work Log

- Bootstrap record created by orchestrator.
- 2026-04-10: started breadth-first harness sweep with direct root harnesses for
  `from_raw*`, `from_non_null*`, and scalar/slice `assume_init`.
- 2026-04-10: added v2 challenge-local documentation:
  `success-criteria.md`, `plan.md`, and `workpad.md`.

## Files Touched

- `docs/verify-rust-std/challenges/0029-boxed/success-criteria.md`
- `docs/verify-rust-std/challenges/0029-boxed/plan.md`
- `docs/verify-rust-std/challenges/0029-boxed/workpad.md`
- `docs/verify-rust-std/challenges/0029-boxed/planner.md`
- `docs/verify-rust-std/challenges/0029-boxed/generator.md`
- `kmir/src/tests/integration/data/verify-rust-std/0029-boxed/README.md`
- `kmir/src/tests/integration/data/verify-rust-std/0029-boxed/box-from-raw.rs`
- `kmir/src/tests/integration/data/verify-rust-std/0029-boxed/box-from-raw-in.rs`
- `kmir/src/tests/integration/data/verify-rust-std/0029-boxed/box-from-non-null.rs`
- `kmir/src/tests/integration/data/verify-rust-std/0029-boxed/box-from-non-null-in.rs`
- `kmir/src/tests/integration/data/verify-rust-std/0029-boxed/box-assume-init.rs`
- `kmir/src/tests/integration/data/verify-rust-std/0029-boxed/box-slice-assume-init.rs`

## Validation Evidence

- `/home/zhaoji/.stable-mir-json/release.sh -Zno-codegen` succeeded for all six
  first-pass harness files under
  `kmir/src/tests/integration/data/verify-rust-std/0029-boxed`.
- `uv --project kmir run kmir prove ... box-from-raw.rs --start-symbol verify_box_from_raw ... --terminate-on-thunk`
  produced `APRProof: box-from-raw.verify_box_from_raw` with
  `ProofStatus.FAILED`; inspected leaf `4` via `kmir show`.
- `uv --project kmir run kmir prove ... box-from-raw-in.rs --start-symbol verify_box_from_raw_in ... --terminate-on-thunk`
  produced `APRProof: box-from-raw-in.verify_box_from_raw_in` with
  `ProofStatus.FAILED`; inspected leaf `4` via `kmir show`.
- Both proof leaves converge on the same transmute thunk in
  `std::alloc::Layout::new::<u32>`.

## Commit Inventory

- Pending first local harness-sweep commit.

## Blockers

- No blocker classified yet in this file.
