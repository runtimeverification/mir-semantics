# Challenge 0026 Plan

## Objective

Turn the published `Rc`/`Weak` challenge requirements into one concrete proof-order matrix so the generator can start from the highest-leverage API cluster instead of spreading across the whole `alloc::rc` surface.

## Confirmed Contract Surface

- Published goal: verify `Rc` and `Weak` in `alloc::rc`.
- Public unsafe APIs: 12 listed functions must have safety contracts and verified contracts.
- Internal unsafe APIs: at least 75% of the listed non-public unsafe functions must be either proven unconditionally safe or given safety contracts.
- Proof limits: primitive `T` only; allocators only from the standard library (`Global` and `System`).
- UB coverage: dangling or misaligned pointer access, compiler intrinsic UB, mutating immutable bytes, and invalid values.
- Challenge-book rules still apply: automation, PR-based workflow, approved tools, and no stdlib runtime changes unless separately justified.

## Single Next Technical Subtask

Rewrite the `Rc::from_raw_in` root harness so it no longer constructs the witness through `Rc::new_in` and `Box::<std::rc::RcInner<u32>, std::alloc::System>::try_new_uninit_in`; instead, feed `from_raw_in` the smallest direct raw-pointer/allocator witness that preserves the current `System` provenance and stays inside the raw-pointer/refcount tranche.

## Why This Comes First

The current proof frontier is not a `Rc::from_raw_in` semantic failure. It is a harness-shape failure caused by the `Rc::new_in` detour into `Box::<std::rc::RcInner<u32>, std::alloc::System>::try_new_uninit_in`, which stalls at `castKindTransmute` in `core/src/alloc/layout.rs:140`. Removing that detour is the narrowest change most likely to unblock the existing root without widening scope.

## Exit Criteria

- The `Rc::from_raw_in` harness takes a direct raw-pointer/allocator witness and no longer depends on `Rc::new_in` or `Box::try_new_uninit_in`.
- The existing `System` provenance is preserved in the root harness.
- Any remaining blocker is recorded as a precise backend dependency or semantic gap, not as a widened Rc API search.
