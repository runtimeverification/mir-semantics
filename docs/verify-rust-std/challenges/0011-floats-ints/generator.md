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
- 2026-04-09: Completed another scoped Part 1 proof slice end-to-end with
  `kmir prove-rs` for `unchecked_sub_u8`; the existing harness and runner
  support were already sufficient on this branch.
- 2026-04-09: Completed the next planner-selected Part 2 proof slice
  end-to-end with `kmir prove-rs` for `wrapping_shr_u8`; the existing harness,
  runner wiring, and shift support were already sufficient on this branch.
- 2026-04-09: Re-read public prior-art from mir-semantics PR `#985` before
  re-executing `widening_mul_u8`; the historical branch-local artifact already
  matched the current harness, so no new support was imported for this slice.
- 2026-04-09: Completed the next planner-selected Part 2 proof slice
  end-to-end with `kmir prove-rs` for `widening_mul_u8`; the existing harness,
  runner wiring, and unsigned multiplication support were already sufficient on
  this branch.
- 2026-04-09: Confirmed the branch-local runner still exposes
  `test_verify_rust_std[carrying_mul]` and re-executed the planner-selected
  `carrying_mul_u8` slice independently on this branch.
- 2026-04-09: Completed the next planner-selected Part 2 proof slice
  end-to-end with `kmir prove-rs` for `carrying_mul_u8`; the existing harness,
  runner wiring, and bigint-helper support were already sufficient on this
  branch.
- 2026-04-09: Confirmed the branch-local runner still exposes
  `test_verify_rust_std[unchecked_mul]` and re-executed the delegated
  `unchecked_mul_u8` slice independently on this branch.
- 2026-04-09: Completed the next Part 1 proof slice end-to-end with
  `kmir prove-rs` for `unchecked_mul_u8`; the existing harness and
  multiplication support were already sufficient on this branch.
- 2026-04-09: Completed the next Part 1 proof slice end-to-end with
  `kmir prove-rs` for `unchecked_mul_u16`; the existing harness and
  multiplication support were already sufficient on this branch.
- 2026-04-09: Completed the next Part 1 proof slice end-to-end with
  `kmir prove-rs` for `unchecked_mul_u32`; the existing harness and
  multiplication support were already sufficient on this branch.
- 2026-04-10: Completed the next Part 1 proof slice end-to-end with
  `kmir prove-rs` for `unchecked_mul_u64`; the existing harness and
  multiplication support were already sufficient on this branch.
- 2026-04-10: Started the next branch-local Part 1 attempt with
  `kmir prove-rs` for `unchecked_shl_u16`, but the run exited with status
  `143` before a terminal proof result was captured; no new frontier was
  established, and no code changes were kept.
- 2026-04-10: Completed the branch-local unchecked-shift proof slice end-to-end
  with `kmir prove-rs` for `unchecked_shl_u8`; the existing harness and shift
  support were already sufficient on this branch, and the next sibling width is
  now `unchecked_shl_u16`.
- 2026-04-10: Completed the next branch-local unchecked-shift proof slice
  end-to-end with `kmir prove-rs` for `unchecked_shl_u32`; the existing
  harness and shift support were already sufficient on this branch, and the
  unchecked-shl family now extends beyond `unchecked_shl_u16`.
- 2026-04-10: Completed the next branch-local unchecked-shift proof slice
  end-to-end with `kmir prove-rs` for `unchecked_shl_u64`; the existing
  harness and shift support were already sufficient on this branch, and the
  unchecked-shl family now extends beyond `unchecked_shl_u32`.
- 2026-04-10: Verified the `unchecked_shl_u64` replay in
  `/tmp/kmir-0011-unchecked-shl-u64` with
  `uv --project kmir run -- kmir show unchecked_shl.unchecked_shl_u64 --proof-dir /tmp/kmir-0011-unchecked-shl-u64 --statistics --leaves`;
  both split paths reached terminal `#EndProgram ~> .K`, with branches on
  `core::num::<impl u64>::checked_shl` and constraints including
  `notBool ARG_UINT2:Int <Int 64`, `ARG_UINT2:Int <Int 64`, and
  `ARG_UINT2:Int >=Int 0`.
- 2026-04-10: Completed the next branch-local unchecked-shift proof slice
  end-to-end with `kmir prove-rs` for `unchecked_shl_u128`; the existing
  harness and shift support were already sufficient on this branch, and the
  unchecked-shl family now covers every published unsigned width.
- 2026-04-10: Verified the `unchecked_shl_u128` replay in
  `/tmp/kmir-0011-unchecked-shl-u128` with
  `uv --project kmir run -- kmir show unchecked_shl.unchecked_shl_u128 --proof-dir /tmp/kmir-0011-unchecked-shl-u128 --statistics --leaves`;
  both split paths reached terminal `#EndProgram ~> .K`, with branches on
  `core::num::<impl u128>::checked_shl` and constraints including
  `notBool ARG_UINT2:Int <Int 128`, `ARG_UINT2:Int <Int 128`, and
  `ARG_UINT2:Int >=Int 0`.
- 2026-04-10: Ran the scoped discovery check for `unchecked_shl` on the
  verify-rust-std integration target with:
  `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_verify_rust_std --collect-only -k "unchecked_shl and not fail" -q`.
  Result: `test_verify_rust_std[unchecked_shl]` is still collected
  (`1/17 tests collected, 16 deselected`), so the next bounded move remains a
  narrow `kmir prove-rs` retry for `unchecked_shl_u16` if execution budget is
  available.
- 2026-04-10: Ran the scoped discovery check for `unchecked_shr` on the
  verify-rust-std integration target with:
  `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_verify_rust_std --collect-only -k "unchecked_shr and not fail" -q`.
  Result: `test_verify_rust_std[unchecked_shr]` is still collected
  (`1/17 tests collected, 16 deselected`), so the family remains branch-worthy.
- 2026-04-10: Started the smallest available `unchecked_shr` proof slice with:
  `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_shr.rs --start-symbol unchecked_shr_u8 --terminate-on-thunk --proof-dir /tmp/kmir-0011-unchecked-shr-u8 --reload --fail-fast --max-workers 1`.
  The run was interrupted before any terminal proof result was emitted, so no
  new frontier was established.
- 2026-04-10: Ran a diagnostics-only pass over
  `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_shr.rs`
  and the matching `show/unchecked_shr-fail.*.expected` artifacts. The harness
  has no smaller split point than `unchecked_shr_u8`, and the expected outputs
  all reduce to the same `binOpShrUnchecked` frontier plus the
  `ARG_UINT2:Int >=Int 0` guard. No narrower branch-worthy subcase was found,
  so another proof run is not justified from this checkpoint alone.

## Files Touched

- `Makefile`
- `kmir/src/tests/integration/test_integration.py`
- `kmir/src/kmir/kdist/mir-semantics/lemmas/kmir-lemmas.md`
- `kmir/src/tests/integration/data/verify-rust-std/README.md`
- `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/README.md`
- `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/*.rs`
- `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/show/*.expected`
- `docs/verify-rust-std/challenges/0011-floats-ints/plan.md`
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

9. Command:
   `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_verify_rust_std --collect-only -k "unchecked_sub and not fail" -q`
   Result:
   passed; exactly `test_verify_rust_std[unchecked_sub]` collected
   (`1/17 collected, 16 deselected`).

10. Command:
    `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_sub.rs --start-symbol unchecked_sub_u8 --terminate-on-thunk --proof-dir /tmp/kmir-0011-unchecked-sub-u8 --reload --fail-fast --max-workers 1`
    Result:
    passed with `ProofStatus.PASSED`; summary reported `nodes: 7`,
    `pending: 0`, `failing: 0`, `stuck: 0`, `terminal: 3`.

11. Command:
    `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_verify_rust_std --collect-only -k "wrapping_shr and not fail" -q`
    Result:
    passed; exactly `test_verify_rust_std[wrapping_shr]` collected
    (`1/17 collected, 16 deselected`).

12. Command:
    `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/wrapping_shr.rs --start-symbol wrapping_shr_u8 --terminate-on-thunk --proof-dir /tmp/kmir-0011-wrapping-shr-u8 --reload --fail-fast --max-workers 1`
   Result:
    passed with `ProofStatus.PASSED`; summary reported `nodes: 7`,
    `pending: 0`, `failing: 0`, `stuck: 0`, `terminal: 3`.

13. Command:
    `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_verify_rust_std --collect-only -k "widening_mul and not fail" -q`
    Result:
    passed; exactly `test_verify_rust_std[widening_mul]` collected
    (`1/17 collected, 16 deselected`).

14. Command:
    `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/widening_mul.rs --start-symbol widening_mul_u8 --terminate-on-thunk --proof-dir /tmp/kmir-0011-widening-mul-u8 --reload --fail-fast --max-workers 1`
    Result:
    passed with `ProofStatus.PASSED`; summary reported `nodes: 3`,
    `pending: 0`, `failing: 0`, `stuck: 0`, `terminal: 2`.

15. Command:
    `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_verify_rust_std --collect-only -k "carrying_mul and not fail" -q`
    Result:
    passed; exactly `test_verify_rust_std[carrying_mul]` collected
    (`1/17 collected, 16 deselected`).

16. Command:
    `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/carrying_mul.rs --start-symbol carrying_mul_u8 --terminate-on-thunk --proof-dir /tmp/kmir-0011-carrying-mul-u8 --reload --fail-fast --max-workers 1`
    Result:
    passed with `ProofStatus.PASSED`; summary reported `nodes: 3`,
    `pending: 0`, `failing: 0`, `stuck: 0`, `terminal: 2`.

17. Command:
    `uv --project kmir run -- kmir show unchecked_shl.unchecked_shl_u32 --proof-dir /tmp/kmir-0011-unchecked-shl-u32 --statistics --leaves`
    Result:
    reached terminal `#EndProgram ~> .K` on both split paths; branches are on
    `core::num::<impl u32>::checked_shl`, with constraints including
    `notBool ARG_UINT2:Int <Int 32`, `ARG_UINT2:Int <Int 32`, and
    `ARG_UINT2:Int >=Int 0`.

17. Command:
    `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_verify_rust_std --collect-only -k "unchecked_mul and not fail" -q`
    Result:
    passed; exactly `test_verify_rust_std[unchecked_mul]` collected
    (`1/17 collected, 16 deselected`).

18. Command:
    `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_mul.rs --start-symbol unchecked_mul_u8 --terminate-on-thunk --proof-dir /tmp/kmir-0011-unchecked-mul-u8 --reload --fail-fast --max-workers 1`
    Result:
    passed with `ProofStatus.PASSED`; summary reported `nodes: 7`,
    `pending: 0`, `failing: 0`, `stuck: 0`, `terminal: 3`.

19. Command:
    `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_mul.rs --start-symbol unchecked_mul_u16 --terminate-on-thunk --proof-dir /tmp/kmir-0011-unchecked-mul-u16 --reload --fail-fast --max-workers 1`
    Result:
    passed with `ProofStatus.PASSED`; summary reported `nodes: 7`,
    `pending: 0`, `failing: 0`, `stuck: 0`, `terminal: 3`.

20. Command:
    `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_mul.rs --start-symbol unchecked_mul_u32 --terminate-on-thunk --proof-dir /tmp/kmir-0011-unchecked-mul-u32 --reload --fail-fast --max-workers 1`
    Result:
    passed with `ProofStatus.PASSED`; summary reported `nodes: 7`,
    `pending: 0`, `failing: 0`, `stuck: 0`, `terminal: 3`.

21. Command:
    `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_mul.rs --start-symbol unchecked_mul_u64 --terminate-on-thunk --proof-dir /tmp/kmir-0011-unchecked-mul-u64 --reload --fail-fast --max-workers 1`
    Result:
    passed with `ProofStatus.PASSED`; summary reported `nodes: 7`,
    `pending: 0`, `failing: 0`, `stuck: 0`, `terminal: 3`.
22. Command:
    `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_shl.rs --start-symbol unchecked_shl_u16 --terminate-on-thunk --proof-dir /tmp/kmir-0011-unchecked-shl-u16 --reload --fail-fast --max-workers 1`
    Result:
    passed with `ProofStatus.PASSED`; replay in
    `/tmp/kmir-0011-unchecked-shl-u16` reached terminal `#EndProgram ~> .K`
    on both split paths. Branches were observed on
    `core::num::<impl u16>::checked_shl`, with constraints including
    `notBool ARG_UINT2:Int <Int 16`, `ARG_UINT2:Int <Int 16`, and
    `ARG_UINT2:Int >=Int 0`.

23. Command:
    `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_verify_rust_std --collect-only -k "unchecked_shr and not fail" -q`
    Result:
    passed; exactly `test_verify_rust_std[unchecked_shr]` collected
    (`1/17 collected, 16 deselected`).

24. Command:
    `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_shr.rs --start-symbol unchecked_shr_u8 --terminate-on-thunk --proof-dir /tmp/kmir-0011-unchecked-shr-u8 --reload --fail-fast --max-workers 1`
    Result:
    interrupted before any terminal proof result was emitted. The family is
    still collected, but this slice did not reach a proof verdict and no new
    frontier was established.

25. Command:
    `nl -ba kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_shr.rs | sed -n '1,220p'`
    Result:
    confirmed the harness has ten top-level wrappers and the smallest callable
    subcase is `unchecked_shr_u8` at lines 16-21.

26. Command:
    `for f in kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/show/unchecked_shr-fail.*.expected; do rg -n "#freezer|#free|thunk|constraint|truncate|modInt|binOpShrUnchecked" "$f"; done`
    Result:
    confirmed the unsigned `u8` expected output reaches
    `#applyBinOp ( binOpShrUnchecked ... ) ~> #freezer`, while the wider
    unsigned cases and all signed cases remain on the same frontier shape with
    the same `ARG_UINT2:Int >=Int 0` constraint.

27. Command:
    `uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_shl.rs --start-symbol unchecked_shl_u64 --terminate-on-thunk --proof-dir /tmp/kmir-0011-unchecked-shl-u64 --reload --fail-fast --max-workers 1`
    Result:
    passed with `ProofStatus.PASSED`; summary reported `nodes: 7`,
    `pending: 0`, `failing: 0`, `stuck: 0`, `terminal: 3`.

28. Command:
    `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_shl.rs --start-symbol unchecked_shl_u128 --terminate-on-thunk --proof-dir /tmp/kmir-0011-unchecked-shl-u128 --reload --fail-fast --max-workers 1`
    Result:
    passed with `ProofStatus.PASSED`; summary reported `nodes: 7`,
    `pending: 0`, `failing: 0`, `stuck: 0`, `terminal: 3`.

29. Command:
    `uv --project kmir run -- kmir show unchecked_shl.unchecked_shl_u128 --proof-dir /tmp/kmir-0011-unchecked-shl-u128 --statistics --leaves`
    Result:
    reached terminal `#EndProgram ~> .K` on both split paths; branches are on
    `core::num::<impl u128>::checked_shl`, with constraints including
    `notBool ARG_UINT2:Int <Int 128`, `ARG_UINT2:Int <Int 128`, and
    `ARG_UINT2:Int >=Int 0`.

## Commit Inventory

- `2e09185c` — `feat(verify-rust-std): port challenge 0011 harnesses and runner`

## Blockers

- Full proof execution across the full integer matrix is still runtime-heavy in
  this environment, but the prior "no completed proof" blocker is reduced:
  `unchecked_add_u8`, `unchecked_neg_i8`, `unchecked_sub_u8`,
  `wrapping_shl_u8`, `wrapping_shr_u8`, `widening_mul_u8`,
  `carrying_mul_u8`, `unchecked_mul_u8`, `unchecked_mul_u16`,
  `unchecked_mul_u32`, `unchecked_mul_u64`, `unchecked_shl_u8`,
  `unchecked_shl_u16`, `unchecked_shl_u32`, `unchecked_shl_u64`, and
  `unchecked_shl_u128` all pass end-to-end on this branch, with
  `unchecked_shl_u128` completing the unsigned half of the unchecked-shl
  family without any new support changes.
- Float-to-int path still appears blocked by backend capability in the current
  stack; the ported expected outputs still include stuck frontiers on float
  intrinsics (e.g., `fabsf32`, `fabsf64`) in
  `to_int_unchecked-fail.*.expected`.
- `unchecked_shr` diagnostics did not uncover a smaller branch-worthy target
  than `unchecked_shr_u8`; the family is still collected, but this checkpoint
  is evidence-only and does not justify another proof rerun yet.

## Next Step

- Exact next non-float proof step: `unchecked_shl_i8` in
  `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_shl.rs`.
- Keep `unchecked_shr` parked unless a new observation narrows the shared
  `binOpShrUnchecked` frontier.
- Keep the float blocker isolated in `to_int_unchecked-fail`.
