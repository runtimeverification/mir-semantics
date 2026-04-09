# Planner Record: Challenge 0003

Ownership:

- Planner owns this file.
- Planner must not implement code, proofs, or evaluation.
- Planner may update challenge-local checklists only if the change is purely
  organizational and clearly documented here.

## Inputs

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0003-pointer-arithmentic.md
- Tracking issue: [#76](https://github.com/model-checking/verify-rust-std/issues/76)
- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0003-pointer-arithmentic`
- Generator record: `docs/verify-rust-std/challenges/0003-pointer-arithmentic/generator.md`
- Evaluator record: `docs/verify-rust-std/challenges/0003-pointer-arithmentic/evaluator.md`

## Requirements Extraction

- Published goal: verify the safety of code that relies on raw pointer arithmetic and eventual raw pointer access, with contracts strong enough to support safe use both inside `core` and by downstream crates.
- Published success criteria:
  - Annotate and verify safety contracts for all listed raw pointer arithmetic methods on `*const T` and `*mut T`: `add`, `sub`, `offset`, `offset_from`, `byte_add`, `byte_sub`, `byte_offset`, and `byte_offset_from`.
  - Prove at least 3 of the listed standard-library users safe: `[u8]::is_ascii`, `String::remove`, `Vec::swap_remove`, `Option::as_slice`, and `VecDeque::swap`.
  - Ensure the proofs automatically rule out the published UB classes and satisfy the general challenge-book requirements.
- Challenge-specific UB obligations:
  - Accessing a dangling or misaligned place is forbidden.
  - Any place projection that violates in-bounds pointer arithmetic is forbidden, including field, tuple-index, and array/slice-index projections.
  - UB through compiler intrinsics is forbidden.
  - Invalid values are forbidden, including in private fields and locals.
- Additional safety conditions from source docs or SAFETY comments:
  - `ptr::offset`, `ptr::add`, and `ptr::sub` require both the starting and resulting pointer to be in bounds or one byte past the end of the same allocated object.
  - Wrapping pointer arithmetic is safe to call, but the resulting pointer still must not be used to read or write across unrelated allocations.
  - Challenge verification is only required for the published pointee coverage: all integer types, at least one `dyn Trait`, at least one slice, `()`, and at least one composite type with multiple non-ZST fields.

## Scope Contract

- In scope for current branch:
  - Planner-only documentation that translates the published challenge into an execution contract.
  - Challenge-local notes that help the generator/evaluator sequence pointer-arithmetic contracts, proof targets, and evidence collection.
  - Optional checklist alignment in `kmir/src/tests/integration/data/verify-rust-std/0003-pointer-arithmentic/README.md` if it is needed to keep the branch-local contract consistent.
- Out of scope unless later justified:
  - Any implementation changes in `kmir`, K semantics, Stable MIR generation, or Rust standard-library sources.
  - Any proof, harness, evaluator, rubric, or test execution work.
  - Any rewrite of `generator.md`, `evaluator.md`, or `rubric.md`.
- Exceptional dependency escalation policy:
  - Record the dependency in this planner first, then require generator/evaluator acknowledgement before any non-local change is introduced.
  - Prefer reuse of existing mir-semantics semantics, lemmas, and integration patterns over new tooling or cross-repo scope expansion.
  - Escalate outside `mir-semantics` only if a missing upstream artifact blocks the challenge contract itself.

## Sprint Contracts

| Sprint | Intended slice | Acceptance check | Status |
| --- | --- | --- | --- |
| 0 | Contract capture | Published goal, success criteria, UB obligations, and assumptions are extracted into this planner | done |
| 1 | Scope shaping | In-scope / out-of-scope boundaries and escalation policy are explicit enough for generator work | pending |
| 2 | Proof decomposition | Pointer-arithmetic contracts are grouped into reusable slices for const/mut and typed coverage | pending |
| 3 | Usage coverage | At least three downstream standard-library users are mapped to proof or blocker candidates | pending |
| 4 | Evidence handoff | Dependencies, blockers, and reuse candidates are precise enough for evaluator baselining | pending |

## Dependencies And Blockers

- `stable-mir-json` must be initialized and buildable in the branch worktree before any real verification work can start.
- The challenge expects support for multiple pointee categories, so the proof plan depends on whatever generic-pointer and projection infrastructure already exists in `mir-semantics`.
- The published success criteria name eight const-pointer APIs and eight mut-pointer APIs; any missing semantic coverage for one family will block the full contract.
- The three-user minimum means the challenge cannot stop after pointer primitive proofs alone.
- Tracking issue `#76` is closed, so clarification must come from the published challenge text and local branch artifacts rather than issue discussion.

## Cross-Challenge Notes

- Reuse candidate: a single contract schema for `add`/`sub`/`offset` and `byte_*` methods should amortize across both const and mut pointer variants.
- Reuse candidate: existing proof patterns for slice indexing, composite-field access, and collection helpers can likely be adapted for `[u8]::is_ascii`, `Option::as_slice`, `Vec::swap_remove`, and `VecDeque::swap`.
- Reuse candidate: any prior raw-pointer or in-bounds-projection lemmas in `mir-semantics` should be cataloged for downstream challenge work, especially if they already encode one-past-the-end or allocation-bound reasoning.
- Reuse candidate: the branch-local README and future evaluator rubric can share the same function inventory and UB checklist wording to keep evidence paths consistent.

## History

- Bootstrap record created by orchestrator.
