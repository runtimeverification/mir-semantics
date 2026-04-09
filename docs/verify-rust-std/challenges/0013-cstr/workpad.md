# Challenge 0013 Workpad

## Handoff State

- Branch: `verify-rust-std/reexec-0013-cstr`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0013-cstr`
- Current stage: generator slice focused on the shared
  `core::ffi::CStr::from_bytes_with_nul` frontier
- Implementation status: in progress; existing challenge-local CStr artifacts
  still have failing or incomplete proofs, and the evaluator is now at `2.0`
  with `IN PROGRESS` because the safe-method matrix and `strlen` are still
  missing

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
  `Index<RangeFrom<usize>>`, `from_bytes_with_nul_unchecked`, and
  `clone_to_uninit`, but those proofs are still not closed.
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
    `CloneToUninit` slice and the linked-SMIR `test_clone_to_uninit` slice can
    both execute past CStr construction cleanly

## Decisions

- Keep the next generator slice tightly focused on the shared constructor
  frontier rather than widening immediately into the full nine-method invariant
  sweep.
- Treat the existing exact-byte `CloneToUninit` harness logic as sufficient and
  do not rework it unless the constructor frontier exposes a concrete harness
  defect.
- Leave `strlen` and the safe-method matrix as follow-on work once the shared
  `from_bytes_with_nul` frontier is reduced.

## Failed Attempts

- The first local `clone_to_uninit.rs` version constructed the source with
  `CStr::from_bytes_with_nul(b"hello\0")`; the proof stopped immediately at a
  missing-body/stuck `core::ffi::CStr::from_bytes_with_nul` call before
  reaching `clone_to_uninit`.
- Replacing the source constructor with both a raw `&[u8] -> &CStr` cast and a
  `c"hello"` C-string literal still reduced to the same
  `core::ffi::CStr::from_bytes_with_nul` frontier on this branch.

## Generator NEXT SLICE: Shared `CStr::from_bytes_with_nul` Frontier Reduction (2026-04-09)

### Hand-off

- Implement the smallest constructor/frontier slice that lets
  `CStr::from_bytes_with_nul` advance far enough for both `test_clone_to_uninit`
  and `test_clone_to_uninit_exact_bytes` to move past CStr construction.
- Keep the slice narrowly scoped to the shared constructor gap; do not expand it
  into the nine safe methods or `strlen`.
- Preserve the existing exact-byte `CloneToUninit` harness logic so the result
  remains byte-exact and destination-validity aware.

### Validation Expectations

- Record the file path(s) touched for the constructor/frontier slice and any
  associated contract update.
- Run the narrowest proof commands that exercise both the linked-SMIR and
  challenge-local `CloneToUninit` paths.
- Capture whether the shared frontier moved, stayed stuck, or needs escalation.

### Scope Notes

- Do not expand this slice into the nine safe-method invariant set.
- Do not spend this slice on `strlen` unless the shared constructor work
  unexpectedly exposes a prerequisite.
- Keep the evidence trace reviewer-readable: commands, frontier, and the exact
  constructor/body gap that remains.

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
