# Execution Plan: Challenge 0027

## Objective

Current planning focus for Challenge 0027 (`Arc`):

- start from the raw-pointer / refcounting family where `0026-rc` provides the
  strongest reusable pattern,
- keep the verification-shaped proof harness separate from the concrete
  frontier reproducer,
- and follow the shared helper-level `CastKind::Transmute` diagnosis on the
  Arc side rather than reopening the tranche selection.

## Confirmed Contract Surface

- Published goal: verify `Arc` and `Weak` in `alloc::sync`.
- Public success criteria: 12 public `unsafe` APIs must be annotated with
  safety contracts and those contracts must be verified.
- Additional coverage obligation: at least 75% of the listed non-public unsafe
  helpers should be proven unconditionally safe or given safety contracts.
- Proof limits from the challenge page:
  - `T` proofs may be limited to primitive types.
  - allocator proofs may be limited to standard-library allocators
    (`Global` and `System`).
- Challenge-specific UB obligations:
  - data races,
  - dangling or misaligned pointer access,
  - compiler intrinsic UB,
  - mutating immutable bytes,
  - invalid values.
- Arc-specific safety emphasis:
  - do not confuse raw-pointer recovery with a concrete witness trace;
  - proof artifacts must be symbolic or contract-shaped.

## Scope Contract

- In scope for the first tranche:
  - `Arc::from_raw_in`
  - `Arc::increment_strong_count_in`
  - `Arc::decrement_strong_count_in`
  - `Weak::from_raw_in`
  - the four thin `Global` wrappers that depend on those roots
- Out of scope unless later justified:
  - `Arc::assume_init` / `Arc<[MaybeUninit<T>],A>::assume_init`
  - `Arc::get_mut_unchecked`
  - `Arc::downcast_unchecked`
  - the large non-public helper surface outside the raw-pointer/refcount
    tranche
- Exceptional dependency escalation policy:
  - `runtimeverification/stable-mir-json` only if the challenge requires it for
    SMIR shape or contract plumbing;
  - `runtimeverification/haskell-backend` only with an explicit blocker note in
    the evaluator record.

## First Proof Target

- Highest-leverage first proof target: `Arc::from_raw_in`
- Why first:
  - it is the raw-recovery root for the allocator-general family;
  - it unlocks the three refcount follow-ons and the `Global` wrapper layer;
  - it already has both a symbolic harness and a smaller dedicated reproducer,
    so the next move can stay inside one precise blocker family.

## Current Proof State

- Verification harness:
  - `kmir/src/tests/integration/data/verify-rust-std/0027-arc/arc-from-raw-in.rs`
  - start symbol: `verify_arc_from_raw_in`
- Frontier reproducer:
  - `kmir/src/tests/integration/data/verify-rust-std/0027-arc/arc-from-raw-in-frontier-fail.rs`
  - start symbol: `main`
- Shared blocker family with `0026-rc`:
  - helper-level `CastKind::Transmute`
  - current Arc-side site:
    `#setUpCalleeData(monoItemFn(... name: symbol("malloc"), body: noBody), ...)`
    at node `3`

## Minimal Reproducer Policy

- Use `arc-from-raw-in-frontier-fail.rs` to keep the helper setup as small as
  possible while preserving the `Arc::from_raw_in` contract shape and the
  shared helper frontier.
- Keep `arc-from-raw-in.rs` symbolic and contract-shaped; do not turn it into a
  concrete reproducer.
- Do not widen into other Arc families until this shared transmute-family leaf
  is either narrowed further or explicitly blocked with a precise next action.

## Single Next Technical Subtask

- Validate whether the new `malloc` `noBody` leaf is the same shared wrapper
  frontier as `0026-rc`; if it is, keep `arc-from-raw-in-frontier-fail.rs`
  as the dedicated reproducer and do not widen the Arc tranche yet.

## Sprint Contracts

| Sprint | Intended slice | Acceptance check | Status |
| --- | --- | --- | --- |
| 0 | Bootstrap challenge understanding | Requirements, safety obligations, and first tranche recorded | complete |
| 1 | Raw-recovery root | `Arc::from_raw_in` has a selected verification shape, a separate reproducer file, and a precise shared transmute-family blocker | in progress |
| 2 | Refcount spine | `Arc::increment_strong_count_in`, `Arc::decrement_strong_count_in`, `Weak::from_raw_in` follow the root | pending |
| 3 | Wrapper layer | Thin `Global` wrappers are queued only after the allocator-general roots are stable | pending |

## Dependencies And Blockers

- `0026-rc` is the strongest reuse source for the contract-first split.
- Arc adds a data-race obligation that Rc did not have; the evaluator should
  fail closed if that obligation is only waved at.
- The current shared blocker family is no longer hypothetical: both the proof
  harness and the smaller reproducer now point to the shared `malloc`
  `noBody` leaf rather than the original helper-level transmute site.

## Cross-Challenge Notes

- Reuse `0026-rc` for:
  - contract-map structure,
  - proof/tracer separation,
  - the idea that a concrete frontier file is a reproducer, not a proof,
  - and the shared transmute-family diagnosis discipline.
- Reuse `0011-floats-ints` only for the audit pattern:
  - coverage tables must make per-function progress obvious,
  - but the raw-pointer tranche here should not copy float-oriented structure.

## History

- Bootstrap record created by orchestrator.
