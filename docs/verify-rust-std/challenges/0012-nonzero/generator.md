# Generator Record: Challenge 0012

Ownership:

- Generator owns this file and the implementation work for this challenge.
- Generator must not edit `evaluator.md` or `rubric.md`.
- Generator should treat planner and evaluator edits as authoritative inputs,
  not as files to rewrite.

## Inputs

- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0012-nonzero`
- Planner record: `docs/verify-rust-std/challenges/0012-nonzero/planner.md`
- Evaluator record: `docs/verify-rust-std/challenges/0012-nonzero/evaluator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0012-nonzero/rubric.md`

## Scope Boundary

- Authorized code area: this challenge branch only.
- Default repository scope: `runtimeverification/mir-semantics`
- Allowed secondary scope: `runtimeverification/stable-mir-json` when required
- Exceptional scope: `runtimeverification/haskell-backend` only with explicit
  justification logged here and in the evaluator record

## Work Log

- 2026-04-09: Ported the prerequisite semantic-fix slice from local branch
  `verify-rust-std/challenge-0012` via six ordered cherry-picks.
- 2026-04-09: Ran narrow collection and execution for the affected `prove-rs`
  regressions (`transmute-maybe-uninit-i128`, `unions`).
- 2026-04-09: Built local kdist definitions to satisfy integration-test
  fixture requirements before rerunning targeted proofs.

## Files Touched

- `kmir/src/kmir/kdist/mir-semantics/intrinsics.md`
- `kmir/src/kmir/kdist/mir-semantics/kmir.md`
- `kmir/src/kmir/kdist/mir-semantics/rt/data.md`
- `kmir/src/kmir/kdist/mir-semantics/rt/types.md`
- `kmir/src/tests/integration/data/prove-rs/show/transmute-maybe-uninit-i128.main.expected`
- `kmir/src/tests/integration/data/prove-rs/show/unions-fail.main.expected`
- `kmir/src/tests/integration/data/prove-rs/transmute-maybe-uninit-i128.rs`
- `kmir/src/tests/integration/data/prove-rs/unions.rs`
- `kmir/src/tests/integration/test_integration.py`
- `docs/verify-rust-std/challenges/0012-nonzero/generator.md`
- `docs/verify-rust-std/challenges/0012-nonzero/workpad.md`

## Validation Evidence

1. Command:
   `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_prove --collect-only -k "transmute-maybe-uninit-i128 or unions" -q`
   Result:
   selected exactly two tests:
   `test_prove[transmute-maybe-uninit-i128]` and `test_prove[unions]`.

2. Command:
   `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_prove -k "transmute-maybe-uninit-i128 or unions" -q`
   Result:
   failed at fixture setup because the local Haskell definition directory did
   not exist (`ValueError: Directory does not exist: ~/.cache/kdist-.../mir-semantics/haskell`).

3. Command:
   `make build`
   Result:
   succeeded; rebuilt `mir-semantics.haskell`, `mir-semantics.llvm`, and
   `mir-semantics.llvm-library`.

4. Command:
   `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_prove -k "transmute-maybe-uninit-i128 or unions" -q --maxfail=1`
   Result:
   `2 passed, 108 deselected in 122.64s`.

## Commit Inventory

- `a52729d7` — `fix(transmute): accept MaybeUninit reinterpretation`
- `a681af49` — `fix(unions): reinterpret payload on field reads`
- `4a8cdb0a` — `test(unions): rename passing union regression`
- `3c4138db` — `fix(intrinsics): prioritize assert_inhabited failure`
- `2d5916d6` — `fix(pointer-casts): support array-to-wrapper projections`
- `01416c6d` — `fix(pointer-casts): preserve wrapper projections for iterators`

## Blockers

- No blocker for this prerequisite slice.
- Remaining work for Challenge 0012 is challenge-specific NonZero harness and
  contract work; this port only establishes the semantic/test baseline needed
  before that layer.
