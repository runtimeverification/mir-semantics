# Challenge 0013 Execution Plan

## Current Position

This branch is past bootstrap. It already contains challenge-local artifacts for
`from_ptr`, `Index<RangeFrom<usize>>`, `from_bytes_with_nul_unchecked`, and the
exact-byte `CloneToUninit` slice, but those proofs are still failing or
incomplete. `strlen` and the broader safe-method matrix are still missing as
dedicated challenge slices.

The highest-leverage next technical subtask is the shared
`core::ffi::CStr::from_bytes_with_nul` frontier reduction. Both the linked-SMIR
proof path and the challenge-local exact-byte `CloneToUninit` slice stop at the
same constructor/body gap, so one fix can advance two existing slices at once.

## Next Generator Task

Reduce the shared `core::ffi::CStr::from_bytes_with_nul` frontier:

1. Add the smallest proof-oriented slice or contract adjustment that lets
   `CStr::from_bytes_with_nul` move past the current stuck frontier.
2. Keep the change scoped to constructor/frontier reduction only; do not widen
   it into the nine safe-method matrix or `strlen`.
3. Re-run the linked-SMIR and challenge-local `CloneToUninit` proofs so the
   next log entry shows whether the shared frontier moved, stayed stuck, or
   needs escalation.

## Evidence Expected

- file paths for the constructor/frontier slice and any contract update
- the exact `CStr::from_bytes_with_nul` body or contract change used to reduce
  the frontier
- evidence that both the linked-SMIR and challenge-local `CloneToUninit`
  harnesses now advance past the constructor frontier, or a precise statement of
  the remaining stuck point
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
- The `strlen` and safe-method-matrix slices remain queued after the shared
  constructor frontier is reduced.
