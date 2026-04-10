# Planner Record: Challenge 0029

Ownership:

- Planner owns this file.
- Planner must not implement code, proofs, or evaluation.
- Planner may update challenge-local checklists only if the change is purely
  organizational and clearly documented here.

## Inputs

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0029-boxed.md
- Tracking issue: [#526](https://github.com/model-checking/verify-rust-std/issues/526)
- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0029-boxed`
- Generator record: `docs/verify-rust-std/challenges/0029-boxed/generator.md`
- Evaluator record: `docs/verify-rust-std/challenges/0029-boxed/evaluator.md`

## Requirements Extraction

- Published goal:
  verify the `boxed` module, including `Box` and related types such as
  `ThinBox`, so that the unsafe code in the module is shown free of the
  challenge-book UB surface.
- Published success criteria:
  - all 9 published unsafe rows must carry verified safety contracts
  - at least 75% of the listed safe-but-unsafe-in-body rows must either be
    proven unconditionally safe or be covered by added safety contracts
  - for generic `T`, primitive instantiations are acceptable
- Challenge-specific UB obligations:
  - no loads/stores through dangling or misaligned places
  - no UB through compiler intrinsics
  - no mutation of immutable bytes
  - no production of invalid values
- Additional safety conditions from source docs or SAFETY comments:
  - raw/`NonNull` recovery rows require the pointer to originate from the
    correct `Box` layout and allocator and be consumed exactly once
  - `assume_init` rows require the pointee or every slice element to be fully
    initialized before conversion
  - `downcast_unchecked` rows require exact dynamic-type agreement
  - ThinBox rows require correct header/metadata layout and dereference
    reconstruction

## Scope Contract

- In scope for current branch:
  - challenge-local harnesses and reproducers under
    `kmir/src/tests/integration/data/verify-rust-std/0029-boxed`
  - `success-criteria.md`, `plan.md`, `workpad.md`, README, planner/generator
    updates, and PR metadata
  - the first breadth-first root proof tranche only
- Out of scope unless later justified:
  - deep semantic repair in `mir-semantics`
  - any `stable-mir-json` or `haskell-backend` change
  - non-boxed challenge artifacts
- Exceptional dependency escalation policy:
  only after a challenge-local harness or minimal reproducer demonstrates that
  the blocker is not in the boxed API construction itself

## Sprint Contracts

| Sprint | Intended slice | Acceptance check | Status |
| --- | --- | --- | --- |
| 0 | Bootstrap challenge understanding | Requirements and blockers recorded | completed |
| 1 | First boxed harness sweep | Per-function table plus root boxed harnesses committed and replay commands recorded | in progress |

## Dependencies And Blockers

- No semantic blocker has been classified yet on this branch.
- Existing generic context: `prove-rs/box_heap_alloc-fail.rs` on this branch
  already shows a constructor-side frontier, so the first harness sweep is
  deliberately shaped to bypass `Box::new*` where possible.

## Cross-Challenge Notes

- Raw ownership recovery for `Box` is structurally adjacent to the `Rc`/`Arc`
  raw recovery tranche, but the first boxed sweep should remain challenge-local
  and evidence-first before reusing any semantic fix.

## History

- Bootstrap record created by orchestrator.
- 2026-04-10: first harness-sweep worker extracted the full success surface and
  selected raw ownership plus initialization conversion as tranche 1.
