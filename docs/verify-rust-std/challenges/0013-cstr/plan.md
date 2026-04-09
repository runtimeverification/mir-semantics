# Challenge 0013 Execution Plan

## Current Position

This branch is past bootstrap. It already contains challenge-local artifacts for
`from_ptr`, `Index<RangeFrom<usize>>`, `from_bytes_with_nul_unchecked`, and the
exact-byte `CloneToUninit` slice, but those proofs are still failing or
incomplete. `strlen` and the broader safe-method matrix are still missing as
dedicated challenge slices.

The highest-leverage next technical subtask is now to reduce the shared
`core::ffi::CStr::from_bytes_with_nul` constructor/body frontier itself. Both
the linked-SMIR and challenge-local exact-byte `CloneToUninit` paths already
meet at that same frontier, so the next slice should focus on whichever shared
body-resolution or constructor support is needed to push that common edge
forward.

## Next Generator Task

Advance the shared `CStr::from_bytes_with_nul` frontier:

1. Reconfirm the exact frontier with the linked-SMIR and challenge-local
   `CloneToUninit` proofs so the branch record stays grounded in the current
   shared stopping point.
2. Make the smallest shared-side change needed to move
   `core::ffi::CStr::from_bytes_with_nul` past the current body gap.
3. Keep the work scoped to that single constructor frontier; do not widen it
   into the nine safe-method matrix or `strlen`.

## Evidence Expected

- file path(s) for the exact-byte harness adjustment and any contract update
- the exact shared-side change used to advance `core::ffi::CStr::from_bytes_with_nul`
- evidence that both the linked-SMIR and challenge-local `CloneToUninit`
  harnesses still meet at the same frontier before and after the change, or a
  precise statement of the remaining stuck point
- the proof commands and resulting status for the narrowed slice

## Stop Conditions

- mark the challenge `READY FOR SUBMISSION` only after the evaluator sees
  direct evidence for every published checklist item
- mark the challenge `CONDITIONALLY READY` only if the remaining gap is now
  limited to a single explicit frontier with no broader artifact gap
- mark the challenge `BLOCKED` only if the generator can prove a concrete
  tooling or dependency limitation

## Carry-Forward Notes

- Public PR `model-checking/verify-rust-std#543` shows the intended
  `CloneToUninit` / `Index<RangeFrom<usize>>` shape and highlights the
  byte-exact clone check.
- Public PR `model-checking/verify-rust-std#566` confirms the full challenge
  bar: nine safe methods, three unsafe contracts, `CloneToUninit`, and
  `Index<RangeFrom<usize>>`.
- The `strlen` and safe-method-matrix slices remain queued after the exact-byte
  `CloneToUninit` path is aligned to the shared constructor frontier.
