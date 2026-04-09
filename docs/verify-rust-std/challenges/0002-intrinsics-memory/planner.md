# Planner Record: Challenge 0002

Ownership:

- Planner owns this file.
- Planner must not implement code, proofs, or evaluation.
- Planner may update challenge-local checklists only if the change is purely
  organizational and clearly documented here.

## Inputs

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0002-intrinsics-memory.md
- Tracking issue: [#16](https://github.com/model-checking/verify-rust-std/issues/16)
- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0002-intrinsics-memory`
- Generator record: `docs/verify-rust-std/challenges/0002-intrinsics-memory/generator.md`
- Evaluator record: `docs/verify-rust-std/challenges/0002-intrinsics-memory/evaluator.md`

## Requirements Extraction

- Published goal: annotate the raw-pointer-manipulating `core::intrinsics` functions with explicit safety contracts and verify that the standard-library call sites that use them are safe.
- Published success criteria:
  - Every intrinsic in the published list gets a safety contract.
  - Any fallback intrinsic implementation is verified.
  - For modeled intrinsics, the implementation-vs-definition relationship is documented clearly enough to audit.
  - Every proof records its assumptions, audit trail, and the explicit and implicit properties it guarantees.
  - The documented safety conditions are shown to be sufficient for safe usage.
- Challenge-specific UB obligations:
  - No undefined behavior through compiler intrinsics.
  - No access through dangling or misaligned pointers.
  - No reads from uninitialized memory except allowed padding or unions.
  - No mutation of immutable bytes.
  - No production of invalid values.
- Additional safety conditions from source docs or SAFETY comments:
  - Safety contracts for the intrinsic wrappers must match the Rust standard library documentation for the exposed APIs.
  - Proof obligations should cover the preconditions that make the intrinsic call safe, not just the post-state after execution.
  - The challenge requires evidence for both `core`-level intrinsic definitions and any `std::ptr` wrappers that expose them.

## Scope Contract

- In scope for current branch:
  - Planner-only documentation for challenge 0002.
  - A staged verification plan for the published intrinsic set and the `std::ptr` wrappers named in the challenge.
  - Cross-reference notes for reusable intrinsic-handling patterns already present in `mir-semantics`.
- Out of scope unless later justified:
  - Any code change in `kmir` or the semantics.
  - Any proof development, test authoring, or evaluator updates.
  - Any expansion of the challenge target beyond the published intrinsic and wrapper list.
- Exceptional dependency escalation policy:
  - If a required intrinsic is not currently modeled or the proof path depends on an unverified fallback, record it as a blocker rather than widening scope silently.
  - If a blocker requires a semantics change, defer it to a separate implementation step and keep this planner unchanged except for dependency notes.

## Sprint Contracts

| Sprint | Intended slice | Acceptance check | Status |
| --- | --- | --- | --- |
| 0 | Requirements lock-in | Goal, success criteria, UB obligations, and assumptions extracted into planner | complete |
| 1 | Surface map | Categorize the intrinsic list into direct models, fallback implementations, and `std::ptr` wrappers | pending |
| 2 | Proof-plan partitioning | Define the likely proof order, shared lemmas, and audit points for each intrinsic family | pending |
| 3 | Dependency closure | Record blockers, prerequisites, and reuse candidates that should be lifted from prior intrinsic work | pending |
| 4 | Handoff readiness | Planner and README status board stay aligned with the intended execution path | pending |

## Dependencies And Blockers

- Current blockers are expected to be semantic rather than documentary: the intrinsic set mixes pointer-copy, volatile-memory, offset, and size/alignment queries, so the proof plan depends on which ones already have executable semantics or fallback coverage in `kmir`.
- Verification of the `std::ptr` wrappers depends on the corresponding `core` intrinsic contracts being precise enough to justify the wrapper preconditions.
- The documentation should remain consistent with any future challenge harnesses that reuse existing `verify-rust-std` proving conventions.

## Cross-Challenge Notes

- Reuse candidates likely include prior intrinsic and raw-pointer work from challenges 0001, 0003, 0015, 0017, and 0019 because they exercise transmutation, pointer arithmetic, slice operations, and intrinsic modeling patterns.
- The `docs/dev/adding-intrinsics.md` guidance in this repository is the most likely local reference for how `kmir` expects intrinsic support to be staged and documented.
- If later work needs a proof skeleton, the challenge directory should prefer reusing existing `prove-rs` and intrinsic-testing patterns instead of inventing a new harness shape.

## History

- Bootstrap record created by orchestrator.
- Planner requirements extracted and staged plan recorded on 2026-04-09.
