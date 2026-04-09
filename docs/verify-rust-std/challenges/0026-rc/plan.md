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

Shrink the rewritten `Rc::from_raw_in` root harness one step further by replacing the current `Box::new_in`-backed `RcInnerWitness<u32>` setup with the smallest direct `System`-provenance raw-memory witness that does not introduce the committed `#cast(..., CastKind::Transmute, ...)` leaf, while still feeding `from_raw_in` the same allocator/raw-pointer pair.

## Why This Comes First

The old `Rc::new_in` / `Box::<std::rc::RcInner<u32>, std::alloc::System>::try_new_uninit_in` detour is already gone. The remaining blocker is now the witness-construction path itself, which terminates in a `#cast(..., CastKind::Transmute, ...)` leaf, so the narrowest useful follow-up is to simplify that witness shape instead of widening into `Rc::increment_strong_count_in`, `Rc::decrement_strong_count_in`, or `Weak::from_raw_in`.

## Exit Criteria

- The `Rc::from_raw_in` harness no longer needs the `Box::new_in` witness wrapper to establish the raw pointer.
- The witness setup no longer introduces the committed `CastKind::Transmute` leaf.
- The existing `System` provenance is preserved in the root harness.
- Any remaining blocker is recorded as a precise backend dependency or semantic gap, not as a widened Rc API search.
