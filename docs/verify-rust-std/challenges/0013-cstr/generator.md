# Generator Record: Challenge 0013

Ownership:

- Generator owns this file and the implementation work for this challenge.
- Generator must not edit `evaluator.md` or `rubric.md`.
- Generator should treat planner and evaluator edits as authoritative inputs,
  not as files to rewrite.

## Inputs

- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0013-cstr`
- Planner record: `docs/verify-rust-std/challenges/0013-cstr/planner.md`
- Evaluator record: `docs/verify-rust-std/challenges/0013-cstr/evaluator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0013-cstr/rubric.md`

## Scope Boundary

- Authorized code area: this challenge branch only.
- Default repository scope: `runtimeverification/mir-semantics`
- Allowed secondary scope: `runtimeverification/stable-mir-json` when required
- Exceptional scope: `runtimeverification/haskell-backend` only with explicit
  justification logged here and in the evaluator record

## Work Log

- 2026-04-09: Ported the prerequisite cross-crate body-resolution slice from
  `verify-rust-std/challenge-0013-0028` into this re-execution branch.
- 2026-04-09: Added linked CStr SMIR fixture (`kmir/cstr.smir.json`) used by
  the prerequisite validation path.
- 2026-04-09: Ran narrow validation for linker body resolution and linked-SMIR
  prove entry on `test_from_ptr`.
- 2026-04-09: Added first challenge-local Challenge 0013 artifact file
  `from_ptr.rs` with a `CStr::from_ptr` proof/repro target and an exact-byte
  `Index<RangeFrom<usize>>` target.
- 2026-04-09: Ran narrow scoped `prove-rs` validation on the new challenge-local
  start symbols and recorded concrete failing/stuck proof states.
- 2026-04-09: Added a second required Challenge 0013 artifact,
  `from_bytes_with_nul_unchecked.rs`, and ran narrow scoped validation for
  `test_from_bytes_with_nul_unchecked_ok`.
- 2026-04-09: Reused the public Challenge 13 `CloneToUninit` guidance from
  `model-checking/verify-rust-std#543` and `#566`, then added a dedicated
  challenge-local exact-byte `CloneToUninit` artifact at
  `clone_to_uninit.rs`.
- 2026-04-09: Refined the new `CloneToUninit` harness to use an initialized
  destination buffer, an explicit `len <= dest.len()` validity guard beyond
  nullness, and exact byte-for-byte comparison against
  `cstr.to_bytes_with_nul()`.
- 2026-04-09: Replaced the standalone `c"hello"` literal in
  `clone_to_uninit.rs` with an explicit `CStr::from_bytes_with_nul(b"hello\0")`
  constructor so the challenge-local exact-byte path bypasses the local
  `#decodeConstant` thunk and reaches the same shared `from_bytes_with_nul`
  frontier as the linked-SMIR slice.
- 2026-04-09: Ran narrow validation on both the preexisting linked-SMIR
  `test_clone_to_uninit` symbol and the new challenge-local
  `test_clone_to_uninit_exact_bytes` symbol; both now reduce to the same
  concrete `core::ffi::CStr::from_bytes_with_nul` body frontier.
- 2026-04-09: Prototyped a donor-link body-supply path for
  `core::ffi::CStr::from_bytes_with_nul`, confirmed that a donor SMIR can
  export a body-bearing item for the stripped target symbol, then reverted the
  prototype after it broke `start_symbol` resolution before proof execution.

## Files Touched

- `kmir/cstr.smir.json`
- `kmir/src/kmir/kompile.py`
- `kmir/src/kmir/linker.py`
- `kmir/src/kmir/smir.py`
- `kmir/src/tests/integration/data/verify-rust-std/0013-cstr/from_ptr.rs`
- `kmir/src/tests/integration/data/verify-rust-std/0013-cstr/from_bytes_with_nul_unchecked.rs`
- `kmir/src/tests/integration/data/verify-rust-std/0013-cstr/clone_to_uninit.rs`
- `docs/verify-rust-std/challenges/0013-cstr/generator.md`
- `docs/verify-rust-std/challenges/0013-cstr/workpad.md`

## Validation Evidence

1. Command:
   `uv --project kmir run -- python - <<'PY' ...`
   (synthetic `resolve_bodies` check + `SMIRInfo.reduce_to()` check on
   `kmir/cstr.smir.json`)
   Result:
   - `resolve_bodies_ok=True`
   - `root=test_from_ptr`
   - `orig_items=61`
   - `reduced_items=61`
   - `keep_all_items=True`

2. Command:
   `timeout 180s uv --project kmir run -- kmir prove-rs kmir/cstr.smir.json --smir --start-symbol test_from_ptr --max-iterations 1 --max-depth 80 --proof-dir /tmp/kmir-cstr-proof --fail-fast`
   Result:
   command executed and produced an APR proof summary:
   `APRProof: cstr.smir.test_from_ptr`, status `PENDING`, `nodes: 3`,
   `pending: 1`, `terminal: 1` (exit code 1 due non-terminal proof state).

3. Command:
   `uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0013-cstr/from_ptr.rs --start-symbol test_from_ptr --terminate-on-thunk --max-depth 120 --max-iterations 60 --proof-dir /tmp/kmir-0013-from-ptr --fail-fast`
   Result:
   command executed and reached APR summary:
   `APRProof: from_ptr.test_from_ptr`, status `FAILED`, `nodes: 4`,
   `failing: 1`, `terminal: 2` (exit code 1).

4. Command:
   `uv --project kmir run -- kmir prove-rs /home/zhaoji/projs/mir-semantics-vrs/challenges/0013-cstr/kmir/src/tests/integration/data/verify-rust-std/0013-cstr/from_ptr.rs --start-symbol test_index_range_from_exact_bytes --terminate-on-thunk --max-depth 120 --max-iterations 80 --proof-dir /tmp/kmir-0013-index-range --fail-fast`
   Result:
   command executed and reached APR summary:
   `APRProof: from_ptr.test_index_range_from_exact_bytes`, status `FAILED`,
   `nodes: 3`, `failing: 1`, `stuck: 1`, `terminal: 1` (exit code 1).

5. Command:
   `timeout 240s uv --project kmir run -- kmir prove-rs /home/zhaoji/projs/mir-semantics-vrs/challenges/0013-cstr/kmir/src/tests/integration/data/verify-rust-std/0013-cstr/from_bytes_with_nul_unchecked.rs --start-symbol test_from_bytes_with_nul_unchecked_ok --terminate-on-thunk --max-depth 120 --max-iterations 80 --proof-dir /tmp/kmir-0013-from-bytes --fail-fast`
   Result:
   command executed and reached APR summary:
   `APRProof: from_bytes_with_nul_unchecked.test_from_bytes_with_nul_unchecked_ok`,
   status `FAILED`, `nodes: 4`, `failing: 1`, `terminal: 2` (exit code 1).

6. Command:
   `uv --project kmir run -- kmir show from_bytes_with_nul_unchecked.test_from_bytes_with_nul_unchecked_ok --proof-dir /tmp/kmir-0013-from-bytes --leaves`
   Result:
   failing leaf reduced to a thunk frontier at
   `std::ffi::CStr::from_bytes_with_nul_unchecked` around
   `#mkPtr ( toAlloc ( allocId ( 3 ) ) , ... )`.

7. Command:
   `timeout 240s uv --project kmir run -- kmir prove-rs kmir/cstr.smir.json --smir --start-symbol test_clone_to_uninit --max-depth 120 --max-iterations 80 --proof-dir /tmp/kmir-0013-cstr-smir-clone --fail-fast`
   Result:
   command executed and reached APR summary:
   `APRProof: cstr.smir.test_clone_to_uninit`, status `FAILED`, `nodes: 3`,
   `failing: 1`, `stuck: 1`, `terminal: 1` (exit code 1).

8. Command:
   `uv --project kmir run -- kmir show cstr.smir.test_clone_to_uninit --proof-dir /tmp/kmir-0013-cstr-smir-clone --leaves`
   Result:
   the failing leaf is a missing-body/stuck call to
   `core::ffi::c_str::CStr::from_bytes_with_nul` at the linked fixture's
   `test_clone_to_uninit` span.

9. Command:
   `timeout 240s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0013-cstr/clone_to_uninit.rs --start-symbol test_clone_to_uninit_exact_bytes --terminate-on-thunk --max-depth 120 --max-iterations 80 --proof-dir /tmp/kmir-0013-clone-to-uninit --fail-fast`
   Result:
   command executed and reached APR summary:
   `APRProof: clone_to_uninit.test_clone_to_uninit_exact_bytes`, status
   `FAILED`, `nodes: 3`, `failing: 1`, `stuck: 1`, `terminal: 1`
   (exit code 1).

10. Command:
    `uv --project kmir run -- kmir show clone_to_uninit.test_clone_to_uninit_exact_bytes --proof-dir /tmp/kmir-0013-clone-to-uninit --leaves`
    Result:
    the challenge-local exact-byte slice now reduces to the same stuck leaf:
    `core::ffi::c_str::CStr::from_bytes_with_nul::haa71ee97b79727bbE`,
    reported from
    `kmir/src/tests/integration/data/verify-rust-std/0013-cstr/clone_to_uninit.rs:17:18`.
    This means the harness reaches a concrete constructor/body frontier after
    encoding the intended destination-validity and exact-byte checks.

11. Harness evidence:
    `kmir/src/tests/integration/data/verify-rust-std/0013-cstr/clone_to_uninit.rs`
    now checks the narrowed reviewer-sensitive requirements directly:
    - destination pointer non-nullness via `!dest_ptr.is_null()`
    - destination region validity via `len <= dest.len()`
    - initialized destination storage via `let mut dest = [0xAAu8; 6]`
    - exact written-region comparison against `cstr.to_bytes_with_nul()`,
      including the trailing NUL byte

12. Command:
    `timeout 240s uv --project kmir run -- kmir prove-rs kmir/cstr.smir.json --smir --start-symbol test_clone_to_uninit --max-depth 120 --max-iterations 80 --proof-dir /tmp/kmir-0013-cstr-smir-clone-slice --fail-fast`
    Result:
    command executed and reached APR summary:
    `APRProof: cstr.smir.test_clone_to_uninit`, status `FAILED`, `nodes: 3`,
    `failing: 1`, `stuck: 1`, `terminal: 1` (exit code 1).

13. Command:
    `timeout 180s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0013-cstr/clone_to_uninit.rs --start-symbol test_clone_to_uninit_exact_bytes --terminate-on-thunk --max-depth 120 --max-iterations 80 --proof-dir /tmp/kmir-0013-clone-to-uninit-local-slice-2 --fail-fast`
    Result:
    command executed and reached APR summary:
    `APRProof: clone_to_uninit.test_clone_to_uninit_exact_bytes`, status
    `FAILED`, `nodes: 3`, `failing: 1`, `stuck: 1`, `terminal: 1`
    (exit code 1).

14. Command:
    `uv --project kmir run -- kmir show cstr.smir.test_clone_to_uninit --proof-dir /tmp/kmir-0013-cstr-smir-clone-slice --leaves`
    Result:
    the linked-SMIR leaf remains a missing-body/stuck call to
    `core::ffi::c_str::CStr::from_bytes_with_nul`, reported from
    `/home/zhaoji/projs/verify-rust-std/kmir-proofs/cstr/cstr.rs:189:16`.

15. Command:
    `uv --project kmir run -- kmir show clone_to_uninit.test_clone_to_uninit_exact_bytes --proof-dir /tmp/kmir-0013-clone-to-uninit-local-slice-2 --leaves`
    Result:
    the local exact-byte `CloneToUninit` leaf is now the same missing-body/stuck
    call to `core::ffi::c_str::CStr::from_bytes_with_nul`, reported from
    `kmir/src/tests/integration/data/verify-rust-std/0013-cstr/clone_to_uninit.rs:17:16`.
    The standalone `#decodeConstant` thunk on `c"hello"` no longer appears in
    the local proof path.

16. Prototype command:
    `python3 - <<'PY' ... augment_missing_symbol_bodies(SMIRInfo.from_file(Path("kmir/cstr.smir.json"))) ...`
    Result:
    the donor-link prototype produced a linked SMIR containing a body-bearing
    donor item for
    `_ZN4core3ffi5c_str4CStr19from_bytes_with_nul17h0000000000000000E`,
    alongside the original linked fixture items.

17. Prototype command:
    `timeout 240s uv --project kmir run -- kmir prove-rs kmir/cstr.smir.json --smir --start-symbol test_clone_to_uninit --max-depth 120 --max-iterations 80 --proof-dir /tmp/kmir-0013-cstr-smir-clone-donor3 --fail-fast`
    Result:
    the prototype did not reach the constructor body. After donor linking,
    proof setup failed in `make_call_config` with
    `ValueError: test_clone_to_uninit not found in program`.

18. Prototype command:
    `timeout 240s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0013-cstr/clone_to_uninit.rs --start-symbol test_clone_to_uninit_exact_bytes --terminate-on-thunk --max-depth 120 --max-iterations 80 --proof-dir /tmp/kmir-0013-clone-to-uninit-donor3 --fail-fast`
    Result:
    the same setup blocker appeared on the challenge-local path:
    `ValueError: test_clone_to_uninit_exact_bytes not found in program`.
    The donor link rewrote item names through `link()` qualification before
    `make_call_config` resolved the unqualified start symbol.

## Commit Inventory

- `80244466` — `feat(linker): port cross-crate body resolution for cstr`
- `13bcd786` — `feat(vrs-0013): add clone_to_uninit slice harness`
- `056ee1a7` — `refactor(vrs-0013): isolate clone_to_uninit slice frontier`
- `f33878dd` — `fix(vrs-0013): bypass cstr literal thunk`

## Blockers

- This branch now has a dedicated exact-byte `CloneToUninit` artifact, but the
  narrowed slice is still blocked by a concrete missing-body/stuck frontier at
  `core::ffi::CStr::from_bytes_with_nul`.
- Both the preexisting linked-SMIR `test_clone_to_uninit` and the new
  challenge-local `test_clone_to_uninit_exact_bytes` reduce to that same
  frontier, so the remaining gap is specific to CStr construction/body support
  on this branch rather than to missing exact-byte harness logic.
- A prototype donor-link fix can materialize a body-bearing donor item for the
  stripped `from_bytes_with_nul` symbol, but the current `link()` pipeline
  qualifies item names in the linked SMIR. That breaks later unqualified
  `start_symbol` lookup in `make_call_config`, so the proof never reaches the
  donated constructor body.
- The next focused action is therefore not another donor body experiment. It is
  a narrow plumbing fix that preserves or aliases original root item names
  across donor linking, or a link-mode variant that avoids qualifying the base
  crate's root items while still allowing the stripped-symbol body fallback.
- Core Challenge 0013 coverage remains incomplete beyond this narrowed slice:
  - `strlen` still lacks a dedicated contract artifact
  - the broader CStr method/invariant harness set is still missing
