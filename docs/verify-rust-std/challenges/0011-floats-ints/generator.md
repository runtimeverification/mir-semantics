# Generator Record: Challenge 0011

Ownership:

- Generator owns this file and the implementation work for this challenge.
- Generator must not edit `evaluator.md` or `rubric.md`.
- Generator should treat planner and evaluator edits as authoritative inputs,
  not as files to rewrite.

## Inputs

- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints`
- Planner record: `docs/verify-rust-std/challenges/0011-floats-ints/planner.md`
- Evaluator record: `docs/verify-rust-std/challenges/0011-floats-ints/evaluator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0011-floats-ints/rubric.md`

## Scope Boundary

- Authorized code area: this challenge branch only.
- Default repository scope: `runtimeverification/mir-semantics`
- Allowed secondary scope: `runtimeverification/stable-mir-json` when required
- Exceptional scope: `runtimeverification/haskell-backend` only with explicit
  justification logged here and in the evaluator record

## Work Log

- 2026-04-09: Ported Challenge 0011 harness/test artifacts and runner support
  from `origin/verify-rust-std/challenge-0011` into this re-execution branch.
- 2026-04-09: Initialized missing `deps/stable-mir-json` submodule for this
  worktree to enable scoped integration-test execution.
- 2026-04-09: Ran filtered `test_verify_rust_std` validation and collected
  concrete evidence for test discovery and runtime behavior.
- 2026-04-09: Completed one direct integer proof slice end-to-end with
  `kmir prove-rs` for `unchecked_add_u8`.
- 2026-04-09: Completed a second direct integer proof slice from a different
  requirement bucket with `kmir prove-rs` for `unchecked_neg_i8`.
- 2026-04-09: Re-read public prior-art from mir-semantics PR `#985` before
  re-executing this branch-local slice; the existing shift-mask lemmas and
  runner wiring already matched the historical support needed for
  `wrapping_shl`.
- 2026-04-09: Completed the first scoped Part 2 proof slice end-to-end with
  `kmir prove-rs` for `wrapping_shl_u8`; no additional harness or support
  changes were required on this branch.

## Files Touched

- `Makefile`
- `kmir/src/tests/integration/test_integration.py`
- `kmir/src/kmir/kdist/mir-semantics/lemmas/kmir-lemmas.md`
- `kmir/src/tests/integration/data/verify-rust-std/README.md`
- `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/README.md`
- `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/*.rs`
- `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/show/*.expected`
- `docs/verify-rust-std/challenges/0011-floats-ints/generator.md`
- `docs/verify-rust-std/challenges/0011-floats-ints/workpad.md`

## Validation Evidence

1. Command:
   `make test-verify-rust-std PARALLEL=1 TEST_ARGS="-k '0011-floats-ints and unchecked_add'"`
   Result:
   runner invoked but filter matched zero parametrized cases; pytest reported
   `no tests ran` and make exited with status 5.

2. Command:
   `git submodule update --init deps/stable-mir-json`
   Result:
   submodule initialized at `885ab4a9f6dd1b5416b57e914082fbb341c89f97`.

3. Command:
   `make test-verify-rust-std PARALLEL=1 TEST_ARGS="-k 'unchecked_add and not fail'"`
   Result:
   one scoped case (`test_verify_rust_std[unchecked_add]`) was dispatched and
   executed for an extended period. The run was terminated to keep this retry
   bounded; make exited with status 143.

4. Command:
   `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_verify_rust_std --collect-only -k "unchecked_add and not fail" -q`
   Result:
   passed; exactly `test_verify_rust_std[unchecked_add]` collected
   (`1/17 collected, 16 deselected`).

5. Command:
   `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_add.rs --start-symbol unchecked_add_u8 --terminate-on-thunk --proof-dir /tmp/kmir-0011-unchecked-add-u8 --reload --fail-fast --max-workers 1`
   Result:
   passed with `ProofStatus.PASSED`; summary reported `nodes: 7`,
   `pending: 0`, `failing: 0`, `stuck: 0`, `terminal: 3`.

6. Command:
   `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_neg.rs --start-symbol unchecked_neg_i8 --terminate-on-thunk --proof-dir /tmp/kmir-0011-unchecked-neg-i8 --reload --fail-fast --max-workers 1`
   Result:
   passed with `ProofStatus.PASSED`; summary reported `nodes: 7`,
   `pending: 0`, `failing: 0`, `stuck: 0`, `terminal: 3`.

7. Command:
   `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_verify_rust_std --collect-only -k "wrapping_shl and not fail" -q`
   Result:
   passed; exactly `test_verify_rust_std[wrapping_shl]` collected
   (`1/17 collected, 16 deselected`).

8. Command:
   `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/wrapping_shl.rs --start-symbol wrapping_shl_u8 --terminate-on-thunk --proof-dir /tmp/kmir-0011-wrapping-shl-u8 --reload --fail-fast --max-workers 1`
   Result:
   passed with `ProofStatus.PASSED`; summary reported `nodes: 7`,
   `pending: 0`, `failing: 0`, `stuck: 0`, `terminal: 3`.

## Commit Inventory

- `2e09185c` — `feat(verify-rust-std): port challenge 0011 harnesses and runner`

## Blockers

- Full proof execution across the full integer matrix is still runtime-heavy in
  this environment, but the prior "no completed proof" blocker is reduced:
  `unchecked_add_u8`, `unchecked_neg_i8`, and now `wrapping_shl_u8` all pass
  end-to-end on this branch, with `wrapping_shl_u8` providing the first
  branch-local Part 2 pass.
- Float-to-int path still appears blocked by backend capability in the current
  stack; the ported expected outputs still include stuck frontiers on float
  intrinsics (e.g., `fabsf32`, `fabsf64`) in
  `to_int_unchecked-fail.*.expected`.
