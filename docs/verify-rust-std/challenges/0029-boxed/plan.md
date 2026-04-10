# Plan: Challenge 0029

## Objective

Complete the v2 harness sweep for `0029-boxed` by first making the success
surface auditable and then landing root verification entrypoints for the raw
ownership and initialization-conversion APIs.

## Current Slice

1. Maintain the full per-function success table in `success-criteria.md`.
2. Add verification-shaped root harnesses for:
   - `Box<T>::from_raw`
   - `Box<T, A>::from_raw_in`
   - `Box<T>::from_non_null`
   - `Box<T, A>::from_non_null_in`
   - `Box<MaybeUninit<T>, A>::assume_init`
   - `Box<[MaybeUninit<T>], A>::assume_init`
3. Run compile validation for the new harnesses and at least one narrow proof
   to capture the first passing result or first frontier.
4. Refresh the challenge-local README and PR `#1054` so they expose the current
   coverage state and exact replay commands.

## Deferred After This Slice

- Constructor proofs such as `new_in`, `try_new_in`, and slice constructors.
- Outgoing raw ownership proofs such as `into_raw_with_allocator`.
- Dynamic-type `downcast` / `downcast_unchecked` proofs.
- ThinBox metadata and layout proofs.
- Any semantic repair beyond capturing a concrete first frontier.
