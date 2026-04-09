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

## Files Touched

- `kmir/cstr.smir.json`
- `kmir/src/kmir/kompile.py`
- `kmir/src/kmir/linker.py`
- `kmir/src/kmir/smir.py`
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

## Commit Inventory

- `80244466` — `feat(linker): port cross-crate body resolution for cstr`

## Blockers

- This retry only ports prerequisite linker/SMIR infrastructure.
- Challenge 0013 still lacks challenge-specific `CStr` harness/contract
  artifacts on this branch, so readiness cannot advance past `IN PROGRESS`
  yet.
