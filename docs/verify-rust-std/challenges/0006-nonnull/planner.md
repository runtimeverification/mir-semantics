# Planner Record: Challenge 0006

Ownership:

- Planner owns this file.
- Planner must not implement code, proofs, or evaluation.
- Planner may update challenge-local checklists only if the change is purely
  organizational and clearly documented here.

## Inputs

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0006-nonnull.md
- Tracking issue: [#53](https://github.com/model-checking/verify-rust-std/issues/53)
- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0006-nonnull`
- Generator record: `docs/verify-rust-std/challenges/0006-nonnull/generator.md`
- Evaluator record: `docs/verify-rust-std/challenges/0006-nonnull/evaluator.md`

## Requirements Extraction

- Published goal: verify absence of undefined behavior in the
  [`ptr::NonNull`](https://github.com/rust-lang/rust/blob/master/library/core/src/ptr/non_null.rs)
  module, which is heavily reused by other `std` modules.
- Published success criteria: prove absence of UB for the 48 public `NonNull`
  functions listed on the challenge page, with the option to use
  preconditions, postconditions, and harnesses where needed.
- Challenge-specific UB obligations:
  - no access to dangling or misaligned places
  - no read from uninitialized memory
  - no mutation of immutable bytes
  - no production of invalid values
- Challenge-specific assumptions:
  - the verification target is `library/core/src/ptr/non_null.rs`
  - the goal is safety verification only, not functional correctness
  - the published function list is the implementation target for this branch
  - proof contracts must remain reusable across the many downstream callers of
    `NonNull` in the standard library
  - this is a re-execution branch, so the planner should assume the published
    challenge contract is fixed and avoid scope creep into unrelated std code
- Additional safety conditions from source docs or SAFETY comments:
  - `new_unchecked` still requires non-null input
  - reference-conversion helpers require pointer validity / dereferenceability
    appropriate to the reference type they create
  - copy, read, write, replace, swap, and drop helpers inherit the usual raw
    pointer requirements around initialization, alignment, aliasing, and
    overlap
  - slice and DST helpers require metadata and length to match the constructed
    view
  - offset and address-manipulation helpers inherit the underlying raw pointer
    arithmetic and provenance contracts

## Scope Contract

- In scope for current branch:
  - challenge-local planning and contract documentation
  - challenge-local checklist alignment in `README.md` if needed to keep the
    execution record coherent
  - mir-semantics-specific scoping decisions needed to prepare proofs for the
    48 published `NonNull` functions
  - dependency and blocker logging for any required semantics or tool gap
- Out of scope unless later justified:
  - implementation of proofs, harnesses, tests, or evaluator logic
  - edits to `generator.md`, `evaluator.md`, or `rubric.md`
  - unrelated standard-library targets, refactors, or runtime-logic changes
  - cross-repo changes unless they are strictly necessary to satisfy the
    published challenge contract
- Exceptional dependency escalation policy:
  - stop and record the blocker if the proof shape needs a new semantics
    feature, new approved tool support, or a cross-repo dependency
  - do not expand scope to convenience changes; only escalate when required to
    reach the published success criteria
  - if a blocker is confirmed, log the evidence and the narrowest viable
    dependency before any implementation work begins

## Sprint Contracts

| Sprint | Intended slice | Acceptance check | Status |
| --- | --- | --- | --- |
| 0 | Baseline map | Published goal, success criteria, UB obligations, and assumptions are recorded in this plan | done |
| 1 | Scope lock | In-scope/out-of-scope boundaries and escalation policy are explicit for mir-semantics | done |
| 2 | Function clustering | The 48 functions are grouped into reusable proof slices with shared contracts identified | pending |
| 3 | Safety-model design | Common `NonNull` obligations are mapped to the raw-pointer, slice, and `MaybeUninit` semantics they depend on | pending |
| 4 | Handoff readiness | Likely blockers, dependencies, and cross-challenge reuse candidates are captured for downstream implementation | pending |

## Dependencies And Blockers

- Current blocker class: the planner can identify the published contract, but
  it cannot assert the final proof shape until the branch-local artifact set
  and the current `mir-semantics` baseline are compared against the `NonNull`
  source contracts.
- Likely dependencies:
  - existing raw-pointer, provenance, and `MaybeUninit` semantics already in
    this branch
  - any slice/DST helpers needed to model `NonNull<[T]>` and metadata-bearing
    pointers
  - proof harness patterns that can express the caller obligations inherited
    from `NonNull`'s `unsafe` APIs without over-constraining inputs
  - any upstream challenge-local evidence already embedded in the execution
    records for this branch
- Likely blockers:
  - missing semantics for one of the pointer operations used by the published
    `NonNull` APIs
  - a need for approved-tool support that is not already integrated in
    `mir-semantics`
  - any required cross-repo change that would alter the scope boundary of this
    re-execution branch

## Cross-Challenge Notes

- Likely reuse candidates:
  - raw-pointer and provenance proof patterns from earlier pointer-focused
    verify-rust-std challenges
  - `MaybeUninit`, slice, copy, and volatile-memory contract shapes already
    used by other `mir-semantics` integration coverage
  - existing `kmir` integration fixtures that model pointer validity,
    alignment, and write/read side effects
  - the challenge-local README checklist as a template for later re-execution
    branches
- No concrete cross-challenge artifact is claimed yet; this section records
  only the candidate reuse lanes the implementation stage should inspect first.

## History

- Bootstrap record created by orchestrator.
- Planner updated to extract the published `NonNull` contract and establish a
  mir-semantics-oriented planning scope.
