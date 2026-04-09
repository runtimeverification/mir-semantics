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
- A dedicated exact-byte `CloneToUninit` slice now exists at
  `kmir/src/tests/integration/data/verify-rust-std/0013-cstr/clone_to_uninit.rs`.
- There is still no dedicated `strlen` slice on this branch.

## Current Frontier

- Existing frontier artifacts:
  - `kmir/src/tests/integration/data/verify-rust-std/0013-cstr/from_ptr.rs`
  - `kmir/src/tests/integration/data/verify-rust-std/0013-cstr/from_bytes_with_nul_unchecked.rs`
  - `kmir/src/tests/integration/data/verify-rust-std/0013-cstr/clone_to_uninit.rs`
- Exact frontier status:
  - `test_from_ptr` remains failing
  - `test_index_range_from_exact_bytes` remains failing
  - `test_from_bytes_with_nul_unchecked_ok` still hits a thunk frontier
  - `test_clone_to_uninit_exact_bytes` now reaches a concrete stuck call to
    `core::ffi::CStr::from_bytes_with_nul`
- Highest-leverage next task:
  - reduce the shared `CStr::from_bytes_with_nul` frontier so the new exact-byte
    `CloneToUninit` slice can execute past CStr construction and into the trait
    body cleanly

## Decisions

- Keep the next generator slice tightly focused on `CloneToUninit` rather than
  widening immediately into the full nine-method invariant sweep.
- Treat the exact written region, destination validity, and source-byte
  comparison as the core evidence requirements for that slice.
- Encode destination validity beyond nullness with an explicit
  `len <= dest.len()` guard and an initialized destination buffer so the slice
  stays defined even if `clone_to_uninit` underwrites.
- Leave `strlen` and the safe-method invariant harness set as follow-on work
  once the `CloneToUninit` frontier is reduced.

## Failed Attempts

- The first local `clone_to_uninit.rs` version constructed the source with
  `CStr::from_bytes_with_nul(b"hello\0")`; the proof stopped immediately at a
  missing-body/stuck `core::ffi::CStr::from_bytes_with_nul` call before
  reaching `clone_to_uninit`.
- Replacing the source constructor with both a raw `&[u8] -> &CStr` cast and a
  `c"hello"` C-string literal still reduced to the same
  `core::ffi::CStr::from_bytes_with_nul` frontier on this branch.

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

## CloneToUninit Slice Update (2026-04-09)

### Artifact

- Added `kmir/src/tests/integration/data/verify-rust-std/0013-cstr/clone_to_uninit.rs`.
- The harness uses an initialized `[0xAAu8; 6]` destination buffer, guards
  `!dest_ptr.is_null()` and `len <= dest.len()`, calls
  `CloneToUninit::clone_to_uninit`, and compares the exact written region
  against `cstr.to_bytes_with_nul()` byte-for-byte, including the trailing NUL.

### Validation

- `timeout 240s uv --project kmir run -- kmir prove-rs kmir/cstr.smir.json --smir --start-symbol test_clone_to_uninit --max-depth 120 --max-iterations 80 --proof-dir /tmp/kmir-0013-cstr-smir-clone --fail-fast`
  -> `FAILED`, `nodes: 3`, `failing: 1`, `stuck: 1`, `terminal: 1`
- `uv --project kmir run -- kmir show cstr.smir.test_clone_to_uninit --proof-dir /tmp/kmir-0013-cstr-smir-clone --leaves`
  -> stuck leaf at `core::ffi::c_str::CStr::from_bytes_with_nul`
- `timeout 240s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0013-cstr/clone_to_uninit.rs --start-symbol test_clone_to_uninit_exact_bytes --terminate-on-thunk --max-depth 120 --max-iterations 80 --proof-dir /tmp/kmir-0013-clone-to-uninit --fail-fast`
  -> `FAILED`, `nodes: 3`, `failing: 1`, `stuck: 1`, `terminal: 1`
- `uv --project kmir run -- kmir show clone_to_uninit.test_clone_to_uninit_exact_bytes --proof-dir /tmp/kmir-0013-clone-to-uninit --leaves`
  -> same stuck leaf at `core::ffi::c_str::CStr::from_bytes_with_nul`

### Outcome

- The exact-byte `CloneToUninit` slice is now implemented and reviewer-readable.
- The slice is materially advanced but not closed: the remaining blocker is a
  specific shared frontier at `core::ffi::CStr::from_bytes_with_nul`, not a
  missing destination-validity or exact-byte comparison check in the harness.
