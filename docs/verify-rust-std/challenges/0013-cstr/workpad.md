# Challenge 0013 Workpad

## Handoff State

- Branch: `verify-rust-std/reexec-0013-cstr`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0013-cstr`
- Current stage: generator slice with first challenge-local `0013-cstr` artifacts
- Implementation status: in progress (initial `from_ptr` and exact-byte index
  artifact added; proofs not closed yet)

## Evidence Gathered

- Upstream challenge page for Challenge 13 defines the target as `CStr`
  safety/invariant verification plus contracts for the unsafe entry points.
- Public solution PRs `model-checking/verify-rust-std#543` and `#566` both
  show the final challenge shape: invariant harness, nine safe methods, three
  unsafe contracts, `CloneToUninit`, and `Index<RangeFrom<usize>>`.
- Review comments on `#543` and `#566` identify the main quality trap:
  `CloneToUninit` must be proven against the exact writable region and not via
  an oversized helper buffer or a harness that could go undefined on bugged
  implementations.
- The local reference branch `verify-rust-std/challenge-0013-0028` is a useful
  context source for CStr-related linker/body-resolution behavior, but it is
  not currently the primary path for this challenge.

## Decisions

- Keep the first generator slice focused on `CStr` verification artifacts rather
  than widening scope into unrelated std changes.
- Treat the `CloneToUninit` contract as the highest-risk technical point in the
  challenge.
- Prefer exact, reviewer-readable evidence in the eventual evaluator record:
  file paths, commands, and byte-level assertions.

## Failed Attempts

- None. This is still the initial planning pass.

## Generator NEXT SLICE: Challenge-Local Artifact Seed (2026-04-09)

### Implemented Artifacts

- Added
  `kmir/src/tests/integration/data/verify-rust-std/0013-cstr/from_ptr.rs`
  with:
  - `test_from_ptr` (`CStr::from_ptr` safety/shape repro target)
  - `test_index_range_from_exact_bytes` (exact-byte checks for
    `Index<RangeFrom<usize>>`)

### Validation Commands and Outcomes

1. Command:
   `uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0013-cstr/from_ptr.rs --start-symbol test_index_range_from_exact_bytes --terminate-on-thunk --max-depth 120 --max-iterations 80 --proof-dir /tmp/kmir-0013-index-range --fail-fast`
   Outcome:
   failed before proof with path-resolution error:
   `FileNotFoundError` on
   `/home/zhaoji/projs/mir-semantics-vrs/challenges/0013-cstr/from_ptr.smir.json`
   (relative path resolved to wrong stem).

2. Command:
   `uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0013-cstr/from_ptr.rs --start-symbol test_from_ptr --terminate-on-thunk --max-depth 120 --max-iterations 60 --proof-dir /tmp/kmir-0013-from-ptr --fail-fast`
   Outcome:
   `APRProof: from_ptr.test_from_ptr`, `ProofStatus.FAILED`,
   `nodes: 4`, `failing: 1`, `terminal: 2` (exit code 1).

3. Command:
   `uv --project kmir run -- kmir prove-rs /home/zhaoji/projs/mir-semantics-vrs/challenges/0013-cstr/kmir/src/tests/integration/data/verify-rust-std/0013-cstr/from_ptr.rs --start-symbol test_index_range_from_exact_bytes --terminate-on-thunk --max-depth 120 --max-iterations 80 --proof-dir /tmp/kmir-0013-index-range --fail-fast`
   Outcome:
   `APRProof: from_ptr.test_index_range_from_exact_bytes`,
   `ProofStatus.FAILED`, `nodes: 3`, `failing: 1`, `stuck: 1`, `terminal: 1`
   (exit code 1).

### Scope Notes

- No challenge-external support file changes were required for this slice.
- This slice is intentionally narrow: first challenge-local CStr artifacts plus
  proof/repro evidence.

### Remaining Gap After This Slice

- Add dedicated challenge-local artifacts for:
  - `strlen` contract
  - exact-byte `CloneToUninit`
- Refine current artifacts/lemmas/contracts until targeted proofs can close or
  reach evaluator-acceptable constrained states with clear blockers.

## Generator NEXT SLICE 2: Add `from_bytes_with_nul_unchecked` Artifact (2026-04-09)

### Implemented Artifact

- Added
  `kmir/src/tests/integration/data/verify-rust-std/0013-cstr/from_bytes_with_nul_unchecked.rs`
  with:
  - `test_from_bytes_with_nul_unchecked_ok` (unsafe
    `CStr::from_bytes_with_nul_unchecked` target)

### Validation Commands and Outcomes

1. Command:
   `timeout 240s uv --project kmir run -- kmir prove-rs /home/zhaoji/projs/mir-semantics-vrs/challenges/0013-cstr/kmir/src/tests/integration/data/verify-rust-std/0013-cstr/from_bytes_with_nul_unchecked.rs --start-symbol test_from_bytes_with_nul_unchecked_ok --terminate-on-thunk --max-depth 120 --max-iterations 80 --proof-dir /tmp/kmir-0013-from-bytes --fail-fast`
   Outcome:
   `APRProof: from_bytes_with_nul_unchecked.test_from_bytes_with_nul_unchecked_ok`,
   `ProofStatus.FAILED`, `nodes: 4`, `failing: 1`, `terminal: 2` (exit code 1).

2. Command:
   `uv --project kmir run -- kmir show from_bytes_with_nul_unchecked.test_from_bytes_with_nul_unchecked_ok --proof-dir /tmp/kmir-0013-from-bytes --leaves`
   Outcome:
   failing leaf reduced to a thunk frontier at
   `std::ffi::CStr::from_bytes_with_nul_unchecked` around
   `#mkPtr ( toAlloc ( allocId ( 3 ) ) , ... )`.

### Scope Notes

- No challenge-external support file changes were required for this slice.
- This slice adds one required unsafe-entry artifact and records the first
  branch-local frontier for it.

### Remaining Gap After This Slice

- `strlen` artifact still missing.
- exact-byte `CloneToUninit` artifact still missing.
- current `from_ptr`, `Index<RangeFrom>`, and
  `from_bytes_with_nul_unchecked` targets all have reproducible but unresolved
  proof frontiers.

## Generator Retry Execution Log

- Port source selected: local branch `verify-rust-std/challenge-0013-0028`,
  commit `16440d11` (`feat(linker): cross-crate body resolution for linked SMIR`).
- Ported files (prerequisite slice only):
  - `kmir/cstr.smir.json`
  - `kmir/src/kmir/kompile.py`
  - `kmir/src/kmir/linker.py`
  - `kmir/src/kmir/smir.py`
- Technical port commit on this branch:
  - `80244466` (`feat(linker): port cross-crate body resolution for cstr`)

## Validation Results

- `uv --project kmir run -- python - <<'PY' ...`
  - synthetic cross-crate `resolve_bodies` case resolved `noBody` to a donor body
  - fixture reduce check on `kmir/cstr.smir.json` kept all items
    (`orig_items=61`, `reduced_items=61`)
- `timeout 180s uv --project kmir run -- kmir prove-rs kmir/cstr.smir.json --smir --start-symbol test_from_ptr --max-iterations 1 --max-depth 80 --proof-dir /tmp/kmir-cstr-proof --fail-fast`
  - command executed against the linked CStr fixture
  - result reached proof state reporting (`APRProof: cstr.smir.test_from_ptr`,
    `PENDING`, `nodes: 3`, `pending: 1`, `terminal: 1`)
  - exit code was non-zero because proof did not close in one iteration

## Next Handoff

- Prerequisite cross-crate linker/body-resolution slice is now in this branch
  with direct validation evidence.
- Challenge-specific work still pending:
  - add `CStr` contracts/harnesses (`from_ptr`,
    `from_bytes_with_nul_unchecked`, `strlen`)
  - add `CloneToUninit` and `Index<RangeFrom<usize>>` exact-byte checks
- Evaluator should keep this challenge at `IN PROGRESS` until those
  challenge-local artifacts and proofs are present.
