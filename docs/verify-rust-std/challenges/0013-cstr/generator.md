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

## Files Touched

- `kmir/cstr.smir.json`
- `kmir/src/kmir/kompile.py`
- `kmir/src/kmir/linker.py`
- `kmir/src/kmir/smir.py`
- `kmir/src/tests/integration/data/verify-rust-std/0013-cstr/from_ptr.rs`
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

## Commit Inventory

- `80244466` — `feat(linker): port cross-crate body resolution for cstr`

## Blockers

- This retry only ports prerequisite linker/SMIR infrastructure.
- First challenge-local artifact file now exists, but core Challenge 0013
  coverage is still incomplete:
  - missing dedicated `from_bytes_with_nul_unchecked` and `strlen` contract
    artifacts
  - missing exact-byte `CloneToUninit` artifact
  - missing broader CStr method/invariant artifact set expected by
    verify-rust-std reviewers
