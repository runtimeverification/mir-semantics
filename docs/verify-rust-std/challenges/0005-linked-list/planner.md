# Planner Record: Challenge 0005

Ownership:

- Planner owns this file.
- Planner must not implement code, proofs, or evaluation.
- Planner may update challenge-local checklists only if the change is purely
  organizational and clearly documented here.

## Inputs

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0005-linked-list.md
- Tracking issue: [#29](https://github.com/model-checking/verify-rust-std/issues/29)
- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0005-linked-list`
- Generator record: `docs/verify-rust-std/challenges/0005-linked-list/generator.md`
- Evaluator record: `docs/verify-rust-std/challenges/0005-linked-list/evaluator.md`

## Requirements Extraction

- Published goal: verify the memory safety of `alloc::collections::linked_list`
  functions that iterate over the list's internal inductive data type.
- Published success criteria: prove memory safety for `clear`, `contains`,
  `split_off`, `remove`, `retain`, `retain_mut`, and `extract_if` in
  `alloc::collections::linked_list`, with the proof holding for linked lists of
  arbitrary shape.
- Challenge-specific UB obligations:
  - no access to dangling or misaligned places
  - no read of uninitialized memory except padding or unions
  - no mutation of immutable bytes
  - no production of invalid values
- Challenge-specific assumptions:
  - the internal representation is a bi-directional linked list
  - the verification target is safety only, not functional correctness
  - generic `T` may be assumed to be a primitive type such as `i32`, `u32`, or
    `bool`
  - the solution must satisfy the repository-wide challenge rules in addition
    to the published challenge page
- Additional safety conditions from source docs or SAFETY comments: not yet
  extracted into this planner; carry them forward only if they appear in the
  linked-list source or in local harness contracts.

## Scope Contract

- In scope for current branch:
  - challenge-local planning, harness alignment, and proof-scope documentation
  - any mir-semantics work needed to model unbounded traversal over
    doubly-linked list structure
  - shared lemmas or abstractions that reduce duplication across the seven
    published functions
  - docs-only updates in this challenge directory, plus the linked challenge
    README if it needs checklist alignment
- Out of scope unless later justified:
  - implementation of proofs, harnesses, tests, or evaluator logic
  - changes to `generator.md`, `evaluator.md`, or `rubric.md`
  - unrelated standard-library targets or broad refactors
  - runtime-logic changes to the standard library
- Exceptional dependency escalation policy:
  - if the proof needs a new semantics feature, new approved tool support, or a
    cross-repo change, stop at the blocker and record the dependency explicitly
    before expanding scope
  - any cross-repo dependency must be justified as necessary for the published
    success criteria, not as a convenience for the current proof shape

## Sprint Contracts

| Sprint | Intended slice | Acceptance check | Status |
| --- | --- | --- | --- |
| 0 | Baseline map | Published goal, success criteria, UB obligations, and assumptions are extracted into this plan | pending |
| 1 | Scope lock | In-scope/out-of-scope boundaries and escalation policy are explicit for mir-semantics | pending |
| 2 | Proof-shape design | Shared abstraction for arbitrary linked-list shape and iterator-style traversal is identified | pending |
| 3 | Function coverage plan | The seven published functions are grouped into proof slices with clear reuse points | pending |
| 4 | Handoff readiness | Dependencies, blockers, and cross-challenge reuse candidates are recorded for downstream implementation | pending |

## Dependencies And Blockers

- Current blocker class: the planner cannot assume the exact proof strategy
  until the local challenge artifacts and existing linked-list coverage are
  inspected against the current `mir-semantics` baseline.
- Likely dependencies:
  - a reusable representation of arbitrary doubly-linked-list shape
  - whatever alloc/collection invariants are already present in the current
    semantics branch
  - the exact `linked_list.rs` snapshot in the verification target tree
  - any SAFETY comments or doc constraints attached to the seven public
    functions
- If the local semantics only supports bounded or shape-specific reasoning for
  iterators today, that is the main proof blocker and must be resolved or
  documented before implementation starts.

## Cross-Challenge Notes

- Likely reuse candidates:
  - generic unbounded-traversal proof patterns for iterator-heavy standard
    library code
  - any existing collection or inductive-structure invariants that already live
    in `mir-semantics`
  - the challenge-local README checklist as a reusable contract template for
    later challenge re-executions
- No concrete cross-challenge implementation artifact is claimed yet; record
  only what is actually reusable once implementation evidence exists.

## History

- Bootstrap record created by orchestrator.
- Planner updated to capture the published linked-list verification contract
  and a mir-semantics-oriented sprint breakdown.
