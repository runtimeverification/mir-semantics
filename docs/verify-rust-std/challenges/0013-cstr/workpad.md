# Challenge 0013 Workpad

## Handoff State

- Branch: `verify-rust-std/reexec-0013-cstr`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0013-cstr`
- Current stage: both `CloneToUninit` proof paths now stop at the shared
  `CStr::from_bytes_with_nul` frontier
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
  - both `test_clone_to_uninit_exact_bytes` and linked-SMIR
    `test_clone_to_uninit` now stop at the same
    `core::ffi::CStr::from_bytes_with_nul` missing-body frontier
- Immediate blocker:
  - the remaining blocker is now the shared `CStr::from_bytes_with_nul`
    constructor/body gap rather than any local harness materialization path

## Decisions

- Keep the next generator slice tightly focused on the shared
  `CStr::from_bytes_with_nul` constructor/body gap rather than widening
  immediately into the full nine-method invariant sweep.
- Treat the existing exact-byte `CloneToUninit` harness logic as sufficient and
  do not rework it unless the literal decoding issue exposes a concrete harness
  defect.
- Keep the exact-byte harness on an explicit
  `CStr::from_bytes_with_nul(b"hello\0")` construction, because it bypasses the
  unsupported `&CStr` literal constant while preserving the same byte-exact
  clone contract.
- Leave `strlen` and the safe-method matrix as follow-on work once the exact-
  byte `CloneToUninit` path is aligned to the shared `from_bytes_with_nul`
  frontier.

## Failed Attempts

- The first local `clone_to_uninit.rs` version constructed the source with
  `CStr::from_bytes_with_nul(b"hello\0")`; the proof stopped immediately at a
  missing-body/stuck `core::ffi::CStr::from_bytes_with_nul` call before
  reaching `clone_to_uninit`.
- Replacing the source constructor with both a raw `&[u8] -> &CStr` cast and a
  `c"hello"` C-string literal still reduced to the same
  `core::ffi::CStr::from_bytes_with_nul` frontier on this branch.
- After the edition-2024 compile fix, the standalone exact-byte path now stops
  one step earlier at a local `#decodeConstant` thunk on the `c"hello"` literal
  in `clone_to_uninit.rs`.
- A donor-link prototype successfully materialized a body-bearing synthetic
  item for the stripped `core::ffi::CStr::from_bytes_with_nul` symbol, but the
  linked SMIR then qualified item names before proof setup.
- After that donor link, both `kmir prove-rs ... --start-symbol test_clone_to_uninit`
  and `kmir prove-rs ... --start-symbol test_clone_to_uninit_exact_bytes`
  failed earlier in `make_call_config` with `ValueError: <start-symbol> not
  found in program`, so the prototype did not materially move the frontier.

## Donor-Link Checkpoint (2026-04-09)

### What Was Confirmed

- The existing shared frontier is unchanged on the branch state that remains
  committed: both the linked-SMIR and challenge-local `CloneToUninit` paths
  still meet at `core::ffi::CStr::from_bytes_with_nul`.
- A synthetic donor body is technically feasible: the prototype could compile a
  donor SMIR item for the stripped `from_bytes_with_nul` symbol and link it
  into the active SMIR.

### Exact Blocker

- The blocker is now one layer earlier than the constructor body itself:
  donor-linked SMIR currently rewrites item names through `link()` item
  qualification.
- That qualification loses the original unqualified roots
  `test_clone_to_uninit` and `test_clone_to_uninit_exact_bytes` that
  `make_call_config` expects, so proof setup aborts before it can execute the
  donated constructor body.

### Next Action

- Keep this slice closed as a checkpoint, not a code landing.
- The next minimal technical move is a plumbing fix that preserves or aliases
  original root item names across donor linking, or limits qualification to the
  donor side only.
- Do not widen into the safe-method matrix or `strlen` until that root-name
  preservation issue is resolved.

## Shared-Frontier Slice Result (2026-04-09)

### Harness Adjustment

- Updated `kmir/src/tests/integration/data/verify-rust-std/0013-cstr/clone_to_uninit.rs`
  to construct the source via `CStr::from_bytes_with_nul(b"hello\0")` instead
  of the standalone `c"hello"` literal.
- Kept the exact-byte `CloneToUninit` checks unchanged:
  initialized destination storage, explicit `len <= dest.len()` guard, and
  byte-for-byte comparison against `to_bytes_with_nul()`.

### Validation

- `timeout 240s uv --project kmir run -- kmir prove-rs kmir/cstr.smir.json --smir --start-symbol test_clone_to_uninit --max-depth 120 --max-iterations 80 --proof-dir /tmp/kmir-0013-cstr-smir-clone-slice --fail-fast`
  -> `FAILED`, `nodes: 3`, `failing: 1`, `stuck: 1`, `terminal: 1`
- `uv --project kmir run -- kmir show cstr.smir.test_clone_to_uninit --proof-dir /tmp/kmir-0013-cstr-smir-clone-slice --leaves`
  -> stuck leaf at `core::ffi::c_str::CStr::from_bytes_with_nul` from `/home/zhaoji/projs/verify-rust-std/kmir-proofs/cstr/cstr.rs:189:16`
- `timeout 180s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0013-cstr/clone_to_uninit.rs --start-symbol test_clone_to_uninit_exact_bytes --terminate-on-thunk --max-depth 120 --max-iterations 80 --proof-dir /tmp/kmir-0013-clone-to-uninit-local-slice-2 --fail-fast`
  -> `FAILED`, `nodes: 3`, `failing: 1`, `stuck: 1`, `terminal: 1`
- `uv --project kmir run -- kmir show clone_to_uninit.test_clone_to_uninit_exact_bytes --proof-dir /tmp/kmir-0013-clone-to-uninit-local-slice-2 --leaves`
  -> same stuck leaf at `core::ffi::c_str::CStr::from_bytes_with_nul` from `kmir/src/tests/integration/data/verify-rust-std/0013-cstr/clone_to_uninit.rs:17:16`

### Outcome

- The exact-byte challenge-local `CloneToUninit` slice now aligns with the
  linked-SMIR control path.
- The slice remains blocked, but now only by the shared
  `core::ffi::CStr::from_bytes_with_nul` missing-body frontier.

## Completed Generator Slice: Align `CloneToUninit` on the Shared Constructor Frontier (2026-04-09)

### Hand-off

- Implemented the smallest harness adjustment that lets
  `test_clone_to_uninit_exact_bytes` reach the same shared
  `CStr::from_bytes_with_nul` frontier as the linked-SMIR path.
- Kept the slice narrowly scoped to the shared constructor frontier and did
  not expand it into the nine safe methods or `strlen`.
- Preserved the existing exact-byte `CloneToUninit` harness logic so the result
  remains byte-exact and destination-validity aware.

### Validation Expectations

- Recorded the file path touched for the harness adjustment and the updated
  challenge docs.
- Re-ran the narrow linked-SMIR and challenge-local `CloneToUninit` proof
  commands.
- Confirmed both paths now reach the same shared frontier.

### Scope Notes

- Do not expand this slice into the nine safe-method invariant set.
- Do not spend this slice on `strlen` unless the shared constructor frontier
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
- The remaining blocker is the shared
  `core::ffi::CStr::from_bytes_with_nul` frontier, not a missing
  destination-validity or exact-byte comparison check in the harness.

## Evaluator Refresh (2026-04-09)

- Re-ran the narrow proofs on commit `c93bbe4a`, which compiles standalone
  prove targets as edition 2024.
- `kmir prove-rs kmir/cstr.smir.json --smir --start-symbol test_clone_to_uninit`
  still stops at the shared `core::ffi::CStr::from_bytes_with_nul` body
  frontier.
- `kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0013-cstr/clone_to_uninit.rs --start-symbol test_clone_to_uninit_exact_bytes --terminate-on-thunk`
  now reaches the same shared `core::ffi::CStr::from_bytes_with_nul` body
  frontier after replacing the `c"hello"` literal with an explicit
  `CStr::from_bytes_with_nul(b"hello\0")` construction.
