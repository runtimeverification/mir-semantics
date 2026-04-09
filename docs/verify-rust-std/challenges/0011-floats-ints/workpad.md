# Workpad: Challenge 0011

## Current handoff state

- Branch: `verify-rust-std/reexec-0011-floats-ints`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0011-floats-ints`
- Status at planner handoff: bootstrap artifacts exist; no challenge-local implementation, proof, or evaluation has been performed by this planner.

## Evidence gathered

- PR #985 states that the integer-method portion is complete and that the float portion is blocked by missing KMIR float-value support.
- PR #985 includes a concrete split between integer methods, safe APIs, and `to_int_unchecked` for `f16`, `f32`, `f64`, and `f128`.
- Review history on PR #985 is thin; the main reusable signal is the challenge decomposition and the explicit float-support blocker.

## Planning decisions

- Treat the integer portion and float portion as separate evidence-bearing slices.
- Keep the next generator task narrow so the evaluator can distinguish a real backend blocker from a missing artifact or a bad harness decomposition.
- Do not escalate to backend changes yet; first confirm whether the current branch can independently re-execute the published workload.

## Reusable rubric patterns for evaluator

- Successful evaluation must tie every published requirement to a concrete artifact or an explicit blocker.
- A float-specific blocker should mention the exact missing capability, not just "floats are hard."
- Terminal classification should distinguish `CONDITIONALLY READY` from `BLOCKED` based on whether the remaining gap is narrow and external versus structural and unimplemented.

## Failed-attempt log

- 2026-04-09: First filtered run used
  `-k '0011-floats-ints and unchecked_add'` and matched zero cases in pytest
  parametrization (`no tests ran`, exit 5).
- 2026-04-09: Second filtered run used
  `-k 'unchecked_add and not fail'`; the test case started but did not complete
  in a bounded runtime window and was terminated (exit 143).
- 2026-04-09: Direct proof follow-up run completed with
  `ProofStatus.PASSED` for `unchecked_add_u8` using:
  `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_add.rs --start-symbol unchecked_add_u8 --terminate-on-thunk --proof-dir /tmp/kmir-0011-unchecked-add-u8 --reload --fail-fast --max-workers 1`.
- 2026-04-09: Follow-up 2 run completed with `ProofStatus.PASSED` for
  `unchecked_neg_i8` using:
  `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_neg.rs --start-symbol unchecked_neg_i8 --terminate-on-thunk --proof-dir /tmp/kmir-0011-unchecked-neg-i8 --reload --fail-fast --max-workers 1`.

## Generator retry execution log

- Ported historical Challenge 0011 files from
  `origin/verify-rust-std/challenge-0011` into this branch for scoped paths:
  challenge artifact directory, test runner entrypoint, and shift-mask lemmas.
- Added dedicated make entrypoint `test-verify-rust-std` (from historical
  branch) and parameterized `test_verify_rust_std` integration coverage with
  challenge start symbols and show-output handling.
- Initialized `deps/stable-mir-json` in this worktree to satisfy build/test
  prerequisites.
- Confirmed scoped case discovery with collect-only:
  `test_verify_rust_std[unchecked_add]` is selected by
  `-k "unchecked_add and not fail"`.

## Evidence for next evaluator step

- Technical port commit exists: `2e09185c`.
- Challenge 0011 artifact set now exists under
  `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints`.
- Validation now includes one completed integer proof slice:
  `unchecked_add_u8` and `unchecked_neg_i8` both pass end-to-end in direct
  `kmir prove-rs` mode.
- Float blocker signal remains present in ported evidence:
  `to_int_unchecked-fail` expected outputs include stuck float intrinsic hooks.

## Next handoff

- Generator follow-up should either:
  - add one more completed small integer slice from a new bucket
    (preferred: `wrapping_shl_u8`),
    or
  - run a tightly scoped fail-case (`unchecked_add-fail`) to verify UB-detection
    behavior on this branch.
- Evaluator should classify readiness based on:
  integer artifact completeness vs. completed-proof evidence, and whether
  float-to-int remains a structural backend blocker.
