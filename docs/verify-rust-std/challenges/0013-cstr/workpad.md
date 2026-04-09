# Challenge 0013 Workpad

## Handoff State

- Branch: `verify-rust-std/reexec-0013-cstr`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0013-cstr`
- Current stage: generator slice focused on the exact-byte `CloneToUninit`
  frontier
- Implementation status: in progress; existing challenge-local CStr artifacts
  still have failing or incomplete proofs

## Evidence Gathered

- Upstream challenge page for Challenge 13 defines the bar as `CStr`
  invariant verification, nine safe-method checks, unsafe contracts for
  `from_ptr`, `from_bytes_with_nul_unchecked`, and `strlen`, plus safe trait
  verification for `CloneToUninit` and `Index<RangeFrom<usize>>`.
- Public solution PR `model-checking/verify-rust-std#543` captures the final
  missing-trait slice and makes the key review point explicit: `CloneToUninit`
  must be checked against the exact written region, not a loose helper buffer.
- Public solution PR `model-checking/verify-rust-std#566` confirms the full
  challenge shape: invariant, nine safe methods, three unsafe contracts, and
  the two trait impls.
- The current branch already has narrow local artifacts for `from_ptr`,
  `Index<RangeFrom<usize>>`, and `from_bytes_with_nul_unchecked`, but those
  proofs are still not closed.
- There is still no dedicated `strlen` slice and no dedicated exact-byte
  `CloneToUninit` slice on this branch.

## Current Frontier

- Existing frontier artifacts:
  - `kmir/src/tests/integration/data/verify-rust-std/0013-cstr/from_ptr.rs`
  - `kmir/src/tests/integration/data/verify-rust-std/0013-cstr/from_bytes_with_nul_unchecked.rs`
- Exact frontier status:
  - `test_from_ptr` remains failing
  - `test_index_range_from_exact_bytes` remains failing
  - `test_from_bytes_with_nul_unchecked_ok` still hits a thunk frontier
- Highest-leverage next task:
  - exact-byte `CloneToUninit`, because it is the last published criterion with
    the strongest review sensitivity and the cleanest path to a terminal
    evidence slice

## Decisions

- Keep the next generator slice tightly focused on `CloneToUninit` rather than
  widening immediately into the full nine-method invariant sweep.
- Treat the exact written region, destination validity, and source-byte
  comparison as the core evidence requirements for that slice.
- Leave `strlen` and the safe-method invariant harness set as follow-on work
  once the `CloneToUninit` frontier is reduced.

## Failed Attempts

- None. The current state is a planning refresh, not a proof-development loop.

## Generator NEXT SLICE: Exact-Byte `CloneToUninit` (2026-04-09)

### Hand-off

- Implement a dedicated `CloneToUninit` harness/contract slice for `CStr`.
- Validate the destination preconditions required by the trait contract.
- Compare the exact region written by `clone_to_uninit` against the source
  `CStr` bytes, including the trailing NUL.
- Keep the harness bounded and defined even if the implementation is buggy.

### Validation Expectations

- Record the file path(s) touched for the trait contract and harness.
- Run the narrowest proof command that exercises the new slice.
- Capture whether the result is a pass, a concrete failing frontier, or a
  blocker that needs escalation.

### Scope Notes

- Do not expand this slice into the nine safe-method invariant set.
- Do not spend this slice on `strlen` unless `CloneToUninit` unexpectedly
  exposes a shared prerequisite.
- Keep the evidence trace reviewer-readable: commands, frontier, and exact
  byte comparisons.
