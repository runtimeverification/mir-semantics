# Challenge 0026 Plan

## Objective

Turn the published `Rc`/`Weak` challenge requirements into a verification-shaped harness plan: a symbolic contract harness for `Rc::from_raw_in` plus a separate temporary frontier reproducer, so the generator can start from the highest-leverage API cluster instead of spreading across the whole `alloc::rc` surface.

## Confirmed Contract Surface

- Published goal: verify `Rc` and `Weak` in `alloc::rc`.
- Public unsafe APIs: 12 listed functions must have safety contracts and verified contracts.
- Internal unsafe APIs: at least 75% of the listed non-public unsafe functions must be either proven unconditionally safe or given safety contracts.
- Proof limits: primitive `T` only; allocators only from the standard library (`Global` and `System`).
- UB coverage: dangling or misaligned pointer access, compiler intrinsic UB, mutating immutable bytes, and invalid values.
- Challenge-book rules still apply: automation, PR-based workflow, approved tools, and no stdlib runtime changes unless separately justified.

## Single Next Technical Subtask

Keep `rc-from-raw-in.rs` as the verification-shaped symbolic proof harness, and keep `rc-new-in-frontier-fail.rs` as the canonical one-line reproducer while the new post-transmute frontier is classified. The transmute leaf is gone for both proof paths; the current blocker is `#setUpCalleeData(... symbol("malloc"), body: noBody ...)`.

## Why This Comes First

The old `Rc::new_in` / `Box::<std::rc::RcInner<u32>, std::alloc::System>::try_new_uninit_in` transmute detour is now gone. The current concrete witness is one line long and the first semantic fix already moved both proof paths to the same allocator setup leaf, so the narrowest useful follow-up is to classify or model the `malloc` `noBody` boundary rather than widening into `Rc::increment_strong_count_in`, `Rc::decrement_strong_count_in`, or `Weak::from_raw_in`.

## Exit Criteria

- The success table in `docs/verify-rust-std/challenges/0026-rc/success-criteria.md` stays aligned with the public `unsafe` surface and the branch-local evidence.
- The `Rc::from_raw_in` challenge-local frontier file is clearly demoted to a temporary reproducer, not the verification target.
- The smallest challenge-local reproducer remains `rc-new-in-frontier-fail.rs` with only `let _ = Rc::new_in(7u32, System);`; the broader `rc-from-raw-in-frontier-fail.rs` remains available for audit context.
- The verification-shaped harness should be symbolic over the payload value, keep `System` concrete, and prove the preconditions around the stable `MaybeUninit` witness helper.
- The frontier reproducer remains separate while the new `malloc` `noBody` leaf is classified.
- Any remaining blocker is recorded as a precise backend dependency or semantic gap, not as a widened Rc API search.
