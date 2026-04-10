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

Keep `rc-from-raw-in.rs` as the verification-shaped symbolic proof harness, and keep shrinking the temporary concrete reproducer chain only as long as it preserves the same helper-family `CastKind::Transmute` frontier. The current minimal reproducer is `rc-new-in-frontier-fail.rs` with only `let _ = Rc::new_in(7u32, System);`; `rc-from-raw-in-frontier-fail.rs` remains the broader audit reproducer.

## Why This Comes First

The old `Rc::new_in` / `Box::<std::rc::RcInner<u32>, std::alloc::System>::try_new_uninit_in` detour is already gone. The unstable `Box::write(...)` blocker is gone too, and the current concrete witness has now been minimized once more by removing the audit-only assert. The narrowest useful follow-up remains to keep the symbolic proof entrypoint separate from the concrete reproducer, rather than widening into `Rc::increment_strong_count_in`, `Rc::decrement_strong_count_in`, or `Weak::from_raw_in`.

## Exit Criteria

- The success table in `docs/verify-rust-std/challenges/0026-rc/success-criteria.md` stays aligned with the public `unsafe` surface and the branch-local evidence.
- The `Rc::from_raw_in` challenge-local frontier file is clearly demoted to a temporary reproducer, not the verification target.
- The smallest challenge-local reproducer for the current transmute frontier is `rc-new-in-frontier-fail.rs` with only `let _ = Rc::new_in(7u32, System);`; the broader `rc-from-raw-in-frontier-fail.rs` remains available for audit context.
- The verification-shaped harness should be symbolic over the payload value, keep `System` concrete, and prove the preconditions around the stable `MaybeUninit` witness helper.
- The frontier reproducer remains separate until the new proof entrypoint is in place and collected.
- Any remaining blocker is recorded as a precise backend dependency or semantic gap, not as a widened Rc API search.
