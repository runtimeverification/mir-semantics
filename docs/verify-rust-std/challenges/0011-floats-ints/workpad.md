# Workpad: Challenge 0011

## Current handoff state

- Branch: `verify-rust-std/reexec-0011-floats-ints`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0011-floats-ints`
- Status after generator slice: the challenge-local docs and ported artifacts
  exist, two direct Part 1 proof slices still pass, and `wrapping_shl_u8` now
  adds one passing Part 2 proof slice from a different requirement family.

## Evidence gathered

- Challenge 11 on the verify-rust-std site is resolved and lists three concrete requirement families: Part 1 integer methods, Part 2 safe APIs, and Part 3 float-to-int conversion.
- PR #985 states that the integer-method portion and the safe APIs were intended to complete, while Part 3 is blocked by missing KMIR float-value support.
- PR #985’s visible review context is thin; the only public review signal currently accessible is an LGTM comment, so the blocker signal comes from the PR body and the branch-local float artifacts.
- PR #985’s file list confirms that `wrapping_shl` relied on the already-ported
  shift-mask simplification lemmas; this branch-local re-execution therefore
  tests whether that support is sufficient here without importing new logic.

## Planning decisions

- Treat the integer portion and float portion as separate evidence-bearing slices.
- Make `wrapping_shl_u8` the next delegated slice because it crosses into Part 2, exercises the existing shift-mask lemma path, and is the smallest proof action that materially broadens branch-local evidence.
- Do not escalate to backend changes yet; first confirm whether the current branch can independently add one more passing proof family before reclassifying the remaining float gap.

## Reusable rubric patterns for evaluator

- Successful evaluation must tie every published requirement to a concrete artifact or an explicit blocker.
- A float-specific blocker should mention the exact missing capability, not just "floats are hard."
- Terminal classification should distinguish `CONDITIONALLY READY` from `BLOCKED` based on whether the remaining gap is narrow and external versus structural and unimplemented.
- A new passing proof in a second requirement family is the strongest low-cost signal that the branch is moving beyond bootstrap evidence without consuming float-blocker budget.

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
- 2026-04-09: Scoped discovery check for the next Part 2 slice collected
  exactly `test_verify_rust_std[wrapping_shl]` using:
  `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_verify_rust_std --collect-only -k "wrapping_shl and not fail" -q`.
- 2026-04-09: Direct proof follow-up run completed with
  `ProofStatus.PASSED` for `wrapping_shl_u8` using:
  `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/wrapping_shl.rs --start-symbol wrapping_shl_u8 --terminate-on-thunk --proof-dir /tmp/kmir-0011-wrapping-shl-u8 --reload --fail-fast --max-workers 1`.

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
- Confirmed the next safe-API case is wired through the same runner:
  `test_verify_rust_std[wrapping_shl]` is selected by
  `-k "wrapping_shl and not fail"`.
- Re-executed the branch-local Part 2 slice directly with `kmir prove-rs`;
  `wrapping_shl_u8` passed without any new support changes, so the prior
  shift-mask lemma port was already sufficient on this branch.

## Evidence for next evaluator step

- Technical port commit exists: `2e09185c`.
- Challenge 0011 artifact set now exists under
  `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints`.
- Validation now includes branch-local passing proof evidence in two published
  requirement families:
  `unchecked_add_u8` and `unchecked_neg_i8` pass in Part 1, and
  `wrapping_shl_u8` passes in Part 2.
- Float blocker signal remains present in ported evidence:
  `to_int_unchecked-fail` expected outputs include stuck float intrinsic hooks.

## Next handoff

- Evaluator should reassess terminal state now that `wrapping_shl_u8` passes
  branch-locally and the integer evidence spans both Part 1 and Part 2.
- Remaining generator work, if any, should stay scoped to documenting or
  confirming the already-recorded float blocker rather than widening back into
  unrelated integer symbols.
