# Challenge 0013 Execution Plan

## Current Position

This branch is past bootstrap. It already contains challenge-local artifacts for
`from_ptr`, `Index<RangeFrom<usize>>`, and `from_bytes_with_nul_unchecked`,
but those proofs are still failing or incomplete, and `strlen` plus
`CloneToUninit` are still missing as dedicated challenge slices.

The highest-leverage next technical subtask is the exact-byte
`CloneToUninit` slice, because it is one of the final published criteria and it
touches the review-sensitive byte-exact destination-validity trap directly.

## Next Generator Task

Implement the `CloneToUninit` verification slice for `CStr`:

1. Add a dedicated challenge-local harness that exercises `CStr` through the
   `CloneToUninit` trait impl.
2. Validate the destination preconditions required by the trait contract, not
   just nullness.
3. Compare the exact written region against the source `CStr` bytes, including
   the trailing NUL byte.
4. Keep the harness bounded and defined even if the implementation is buggy.
5. Record the proof command and the resulting frontier or pass/fail state in
   the generator log.

## Evidence Expected

- file paths for the `CloneToUninit` harness and any contract update
- the exact destination validity check used by the harness
- evidence that the copied bytes are compared against the source `CStr`
- the proof command and the resulting status for the narrowed slice

## Stop Conditions

- mark the challenge `READY FOR SUBMISSION` only after the evaluator sees
  direct evidence for every published checklist item
- mark it `CONDITIONALLY READY` only if the remaining gap is now limited to a
  single explicit frontier with no broader artifact gap
- mark it `BLOCKED` only if the generator can prove a concrete tooling or
  dependency limitation

## Carry-Forward Notes

- Public PR `model-checking/verify-rust-std#543` shows the intended
  `CloneToUninit` / `Index<RangeFrom<usize>>` shape and highlights the
  byte-exact clone check.
- Public PR `model-checking/verify-rust-std#566` confirms the full challenge
  bar: nine safe methods, three unsafe contracts, `CloneToUninit`, and
  `Index<RangeFrom<usize>>`.
- The `strlen` and safe-method invariant slices remain queued after the
  `CloneToUninit` frontier is reduced.
