# Challenge 0026 Plan

## Objective

Turn the published `Rc`/`Weak` challenge requirements into one auditable success-criteria table plus one challenge-local frontier harness, so the generator can start from the highest-leverage API cluster instead of spreading across the whole `alloc::rc` surface.

## Confirmed Contract Surface

- Published goal: verify `Rc` and `Weak` in `alloc::rc`.
- Public unsafe APIs: 12 listed functions must have safety contracts and verified contracts.
- Internal unsafe APIs: at least 75% of the listed non-public unsafe functions must be either proven unconditionally safe or given safety contracts.
- Proof limits: primitive `T` only; allocators only from the standard library (`Global` and `System`).
- UB coverage: dangling or misaligned pointer access, compiler intrinsic UB, mutating immutable bytes, and invalid values.
- Challenge-book rules still apply: automation, PR-based workflow, approved tools, and no stdlib runtime changes unless separately justified.

## Single Next Technical Subtask

Replace the current `RcInnerWitness<u32>` field-address witness with a stable `MaybeUninit`-backed `System` allocation witness that writes the witness value through raw memory operations (`MaybeUninit` plus `ptr::write` or equivalent stable pointer writes, not `Box::write`) and then computes the target pointer through explicit raw provenance operations (`addr_of!` / cast-free field projection) so the challenge-local harness can keep the same allocator/raw-pointer pair without re-entering the committed `#cast(..., CastKind::Transmute, ...)` leaf.

## Why This Comes First

The old `Rc::new_in` / `Box::<std::rc::RcInner<u32>, std::alloc::System>::try_new_uninit_in` detour is already gone. The remaining blocker is now the witness-construction path itself: the attempted `MaybeUninit` route fails before proof construction because `Box::write(...)` is unstable on this toolchain, so the narrowest useful follow-up is to keep the raw-memory witness shape but switch to stable pointer writes instead of widening into `Rc::increment_strong_count_in`, `Rc::decrement_strong_count_in`, or `Weak::from_raw_in`.

## Exit Criteria

- The success table in `docs/verify-rust-std/challenges/0026-rc/success-criteria.md` stays aligned with the public `unsafe` surface and the branch-local evidence.
- The `Rc::from_raw_in` challenge-local harness no longer needs the `Box::new_in` witness wrapper to establish the raw pointer.
- The witness setup uses a raw `MaybeUninit`-backed `System` allocation path, avoids unstable library calls like `Box::write`, and no longer introduces the committed `CastKind::Transmute` leaf.
- The existing `System` provenance is preserved in the root harness and mirrored by the challenge-local frontier file.
- Any remaining blocker is recorded as a precise backend dependency or semantic gap, not as a widened Rc API search.
