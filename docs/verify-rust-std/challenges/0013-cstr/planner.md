# Planner Record: Challenge 0013

Ownership:

- Planner owns this file.
- Planner must not implement code, proofs, or evaluation.
- Planner may update challenge-local checklists only if the change is purely
  organizational and clearly documented here.

## Inputs

- Challenge page:
  https://model-checking.github.io/verify-rust-std/challenges/0013-cstr.html
- Tracking issue: [#150](https://github.com/model-checking/verify-rust-std/issues/150)
- Challenge artifact directory:
  `kmir/src/tests/integration/data/verify-rust-std/0013-cstr`
- Generator record: `docs/verify-rust-std/challenges/0013-cstr/generator.md`
- Evaluator record: `docs/verify-rust-std/challenges/0013-cstr/evaluator.md`

## Requirements Extraction

- Published goal: verify that `CStr` safely represents a borrowed reference to
  a null-terminated byte sequence and that the implementation preserves the
  `CStr` safety invariant.
- Published success criteria:
  - implement `Invariant` for `CStr`
  - verify the invariant after the nine safe public methods:
    `from_bytes_until_nul`, `from_bytes_with_nul`, `count_bytes`, `is_empty`,
    `to_bytes`, `to_bytes_with_nul`, `bytes`, `to_str`, and `as_ptr`
  - annotate and verify safety contracts for `from_ptr`,
    `from_bytes_with_nul_unchecked`, and `strlen`
  - verify the `CloneToUninit` trait impl and `ops::Index<RangeFrom<usize>>`
    for `CStr`
- Challenge-specific UB obligations:
  - no dangling or misaligned loads/stores
  - no out-of-bounds pointer arithmetic / projection
  - no mutation of immutable bytes
  - no access to uninitialized memory
- Additional safety conditions from source docs or SAFETY comments:
  - `CloneToUninit` must validate the destination pointer according to the
    trait contract, not merely against null
  - the indexed `CStr` result must preserve the invariant and correspond to the
    source tail bytes
  - bounded harnesses are allowed, but the bound must be justified by the
    exercised safety property

## Current Frontier

- Existing challenge-local artifacts:
  - `from_ptr.rs` with `test_from_ptr` and
    `test_index_range_from_exact_bytes`
  - `from_bytes_with_nul_unchecked.rs` with
    `test_from_bytes_with_nul_unchecked_ok`
- Current proof state:
  - `test_from_ptr` fails
  - `test_index_range_from_exact_bytes` fails
  - `test_from_bytes_with_nul_unchecked_ok` fails at a thunk frontier
- Missing challenge slices:
  - dedicated `strlen` artifact
  - dedicated exact-byte `CloneToUninit` artifact
  - the nine-method invariant harness set

The exact current frontier that should be delegated next is the exact-byte
`CloneToUninit` slice. It is the tightest missing published criterion, and it is
the piece that most directly tests the destination-validity and byte-exactness
trap highlighted by the public reviews.

## Scope Contract

- In scope for current branch:
  - `library/core/src/ffi/c_str.rs`
  - `library/core/src/clone.rs` only if required for `CloneToUninit`
  - challenge-local docs and integration artifacts under
    `kmir/src/tests/integration/data/verify-rust-std/0013-cstr`
- Out of scope unless later justified:
  - `runtimeverification/stable-mir-json`
  - `runtimeverification/haskell-backend`
  - any unrelated refactor outside the `CStr` challenge path
- Exceptional dependency escalation policy:
  - escalate to `stable-mir-json` only if the generator can show a missing JSON
    or linking artifact blocks the challenge
  - escalate to `haskell-backend` only if the generator can show a verifier
    limitation prevents the required contracts or harnesses from being
    expressed in `mir-semantics`

## Sprint Contracts

| Sprint | Intended slice | Acceptance check | Status |
| --- | --- | --- | --- |
| 0 | Bootstrap challenge understanding | Requirements and blockers recorded | complete |
| 1 | Narrow generator target | Next technical subtask and evidence path identified | complete |
| 2 | Technical execution | Harnesses/contracts added and validation evidence recorded | in progress |
| 3 | Evaluation loop | Rubric updated and readiness scored with explicit gaps | pending |

## Dependencies And Blockers

- No hard blocker recorded yet.
- Likely risk: `CloneToUninit` verification may need a stronger destination
  validity contract than a non-null precondition, based on prior review
  comments.

## Cross-Challenge Notes

- Reuse candidates:
  - PR `model-checking/verify-rust-std#543` for the byte-exact
    `CloneToUninit` / `Index<RangeFrom<usize>>` shape and review comments
  - PR `model-checking/verify-rust-std#566` for the full Challenge 13
    structure and review comments
  - local `verify-rust-std/challenge-0013-0028` branch for any linker or
    CStr-resolution context if the generator needs it
- Evaluator should prefer a rubric item that distinguishes "a harness exists"
  from "the harness exercises the exact bytes and destination validity the trait
  contract requires".

## History

- Bootstrap record created by orchestrator.
- Planner checkpoint: extracted the published challenge bar, confirmed the
  current challenge-local frontiers, and narrowed the next generator task to
  the exact-byte `CloneToUninit` slice.
