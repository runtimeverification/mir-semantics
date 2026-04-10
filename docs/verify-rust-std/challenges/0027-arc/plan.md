# Execution Plan: Challenge 0027

## Objective

Bootstrapping plan for Challenge 0027 (`Arc`):

- start from the raw-pointer / refcounting family where `0026-rc` provides the
  strongest reusable pattern,
- keep verification-shaped proof harnesses separate from concrete frontier
  reproducers,
- and preserve an auditable per-function success table from the start.

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
  - it is the best place to detect whether the branch needs a symbolic harness
    shape or a smaller reproducer before any wider Arc work.

## Minimal Reproducer Policy

- If the first proof target or one of its follow-ons hits a semantic frontier,
  first reduce to the smallest challenge-local reproducer that still exposes
  the stuck leaf.
- Keep the reproducer concrete and narrow.
- Keep the proof harness symbolic and contract-shaped.
- Do not widen into other Arc families until the root tranche is either proven
  or blocked with an explicit leaf and next action.

## Sprint Contracts

| Sprint | Intended slice | Acceptance check | Status |
| --- | --- | --- | --- |
| 0 | Bootstrap challenge understanding | Requirements, safety obligations, and first tranche recorded | complete |
| 1 | Raw-recovery root | `Arc::from_raw_in` has a selected verification shape and a separate reproducer file | in progress |
| 2 | Refcount spine | `Arc::increment_strong_count_in`, `Arc::decrement_strong_count_in`, `Weak::from_raw_in` follow the root | pending |
| 3 | Wrapper layer | Thin `Global` wrappers are queued only after the allocator-general roots are stable | pending |

## Dependencies And Blockers

- `0026-rc` is the strongest reuse source for the contract-first split.
- Arc adds a data-race obligation that Rc did not have; the evaluator should
  fail closed if that obligation is only waved at.
- No semantic blocker has been observed yet on this branch because no proof has
  been run yet.

## Cross-Challenge Notes

- Reuse `0026-rc` for:
  - contract-map structure,
  - proof/tracer separation,
  - and the idea that a concrete frontier file is a reproducer, not a proof.
- Reuse `0011-floats-ints` only for the audit pattern:
  - coverage tables must make per-function progress obvious,
  - but the raw-pointer tranche here should not copy float-oriented structure.

## History

- Bootstrap record created by orchestrator.
