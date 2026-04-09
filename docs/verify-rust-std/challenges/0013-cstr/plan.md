# Challenge 0013 Execution Plan

## Current Position

The branch is still at bootstrap. No implementation, proofs, or evaluator scoring
exist yet. The next generator step should therefore target the smallest slice
that can establish a trustworthy evidence chain for the rest of the challenge.

## Next Generator Task

Implement the `CStr` verification core in the challenge branch:

1. Add or refine the `CStr` invariant harnesses so the result of each safe API is
   checked with `is_safe()` and matched against the expected byte view.
2. Add the unsafe contracts and proof harnesses for `from_ptr`,
   `from_bytes_with_nul_unchecked`, and `strlen`.
3. Add the `CloneToUninit` and `Index<RangeFrom<usize>>` checks in a way that
   exercises the exact bytes the contract promises, not an oversized helper
   buffer.
4. Record proof/test commands and outputs in the generator log.

## Evidence Expected

- file paths for each harness and contract change
- commands used to run the scoped verification
- confirmation that the bytes copied by `CloneToUninit` are compared against the
  source `CStr`
- confirmation that the indexed `CStr` preserves the invariant and byte tail
- any failing proof output, if the challenge is not yet green

## Stop Conditions

- mark the challenge `READY FOR SUBMISSION` only after the evaluator sees direct
  evidence for the published checklist items
- mark it `CONDITIONALLY READY` only if the remaining gap is narrow, explicit,
  and tied to a single missing proof or contract
- mark it `BLOCKED` only if the generator can prove a concrete tooling or
  dependency limitation

## Carry-Forward Notes

- The public PR comments on `model-checking/verify-rust-std#543` highlight two
  important verification traps:
  - `CloneToUninit` must be checked against the exact written region
  - the harness must remain defined even if the implementation is buggy
- The older public PR `#566` is still useful as a documentation map, but its
  review comments should be treated as the authoritative readiness hints.
