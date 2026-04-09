# Challenge 0013 Execution Plan

## Current Position

This branch is past bootstrap. It already contains challenge-local artifacts for
`from_ptr`, `Index<RangeFrom<usize>>`, `from_bytes_with_nul_unchecked`, and the
exact-byte `CloneToUninit` slice, but those proofs are still failing or
incomplete. `strlen` and the broader safe-method matrix are still missing as
dedicated challenge slices.

The highest-leverage next technical subtask is now to eliminate the standalone
`#decodeConstant` thunk on the `c"hello"` literal in the challenge-local exact-
byte `CloneToUninit` slice so that both proof paths can reach the same shared
`core::ffi::CStr::from_bytes_with_nul` frontier. That is the narrowest change
that restores a comparable proof shape across the linked-SMIR and
challenge-local evidence.

## Next Generator Task

Remove the standalone `#decodeConstant` thunk from the exact-byte
`CloneToUninit` slice:

1. Make `kmir/src/tests/integration/data/verify-rust-std/0013-cstr/clone_to_uninit.rs`
   reach the shared `CStr::from_bytes_with_nul` frontier without stopping at a
   local constant-decoding thunk.
2. Keep the change scoped to the exact-byte harness shape; do not widen it into
   the nine safe-method matrix or `strlen`.
3. Re-run the linked-SMIR and challenge-local `CloneToUninit` proofs so the
   next log entry shows whether both paths now share the same constructor/body
   frontier or whether a second frontier remains.

## Evidence Expected

- file path(s) for the exact-byte harness adjustment and any contract update
- the exact harness change used to remove the local `#decodeConstant` thunk
- evidence that both the linked-SMIR and challenge-local `CloneToUninit`
  harnesses now reach the same `CStr::from_bytes_with_nul` frontier, or a
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
