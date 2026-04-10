# Workpad: Challenge 0011

## Current handoff state

- Branch: `verify-rust-std/reexec-0011-floats-ints`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0011-floats-ints`
- Status after generator slice: the challenge-local docs and ported artifacts
  exist, twelve direct proof slices pass on the branch, and the latest
  evaluator refresh before this slice left the challenge `IN PROGRESS` at
  `2.9 / 3` pending a broader reassessment. The planner-selected
  `carrying_mul_u8` slice is complete, the follow-up `unchecked_mul_u8`
  slice also passed without any support changes, and the new
  `unchecked_mul_u16` slice passed as well, and `unchecked_mul_u32` now also
  passes on this branch. The latest branch-local `unchecked_shl_u8` proof
  also passed, and the scoped discovery check for `unchecked_shl` still
  collects the case, so the next bounded move remains `unchecked_shl_u16`.
  The current checkpoint adds a cheap `unchecked_shr` discovery check that
  still collects exactly one case, and the smallest proof slice
  (`unchecked_shr_u8`) was interrupted before any terminal proof status was
  emitted.

## Evidence gathered

- Challenge 11 on the verify-rust-std site is resolved and lists three concrete requirement families: Part 1 integer methods, Part 2 safe APIs, and Part 3 float-to-int conversion.
- PR #985 states that the integer-method portion and the safe APIs were intended to complete, while Part 3 is blocked by missing KMIR float-value support.
- PR #985’s visible review context is thin; the only public review signal currently accessible is an LGTM comment, so the blocker signal comes from the PR body and the branch-local float artifacts.
- PR #985’s file list confirms that `wrapping_shl` relied on the already-ported
  shift-mask simplification lemmas; this branch-local re-execution therefore
  tests whether that support is sufficient here without importing new logic.
- Re-reading the historical challenge branch for `widening_mul` showed that the
  current branch already matched the prior harness shape and runner wiring, so
  this slice could be re-executed independently without importing more logic.
- `carrying_mul.rs` is wired in the same branch-local harness set and was
  confirmed by scoped collection, so the next cheapest Part 2 slice was
  `carrying_mul_u8`.
- `unchecked_mul.rs` and its fail artifact are already present in the same
  challenge-local harness set, so the next cheapest remaining Part 1 slice is
  `unchecked_mul_u8`.
- `unchecked_shr.rs` is a single-file harness with ten wrappers and no smaller
  split points; the smallest callable subcase is `unchecked_shr_u8` at lines
  16-21, so there is no narrower diagnostic target inside the harness itself.
- The branch now has twelve passing direct proof slices
  (`unchecked_add_u8`, `unchecked_neg_i8`, `unchecked_sub_u8`,
  `wrapping_shl_u8`, `wrapping_shr_u8`, `widening_mul_u8`,
  `carrying_mul_u8`, `unchecked_mul_u8`, `unchecked_mul_u16`, and
  `unchecked_mul_u32`, plus `unchecked_mul_u64`),
  confirming that the first carrying-mul Part 2 slice and the unsigned
  unchecked-mul slices also execute cleanly on this branch with the
  already-ported support.
- The refreshed evaluator result stays at `IN PROGRESS` with score `2.9 / 3`,
  so the branch still needs more non-float breadth before any terminal state
  can be justified.

## Planning decisions

- Treat the integer portion and float portion as separate evidence-bearing slices.
- `widening_mul_u8` was the correct delegated slice: it was the cheapest
  remaining safe-API case, broadened Part 2 beyond the existing wrapping-shift
  pair, and re-used the already-ported unsigned multiplication support without
  introducing float work.
- `carrying_mul_u8` was the correct delegated slice: it is the remaining
  safe-API family in Part 2, and the branch-local harness already exposes the
  `carrying_mul` runner.
- `unchecked_mul_u8` is the next best slice: it stays on the already-covered
  `u8` width, reuses the multiplication support proven by `widening_mul_u8`
  and `carrying_mul_u8`, and advances the core unsafe-method matrix more
  directly than widening scope to a new safe-API width.
- Do not escalate to backend changes from this slice; it passed cleanly, so
  the next step is evaluator/planner reassessment rather than widening scope
  inside this generator turn.

## Reusable rubric patterns for evaluator

- Successful evaluation must tie every published requirement to a concrete artifact or an explicit blocker.
- A float-specific blocker should mention the exact missing capability, not just "floats are hard."
- Terminal classification should distinguish `CONDITIONALLY READY` from `BLOCKED` based on whether the remaining gap is narrow and external versus structural and unimplemented.
- A new passing proof in an additional safe-API slice is the strongest low-cost signal that the branch is moving beyond bootstrap evidence without consuming float-blocker budget.

## Failed-attempt log

- 2026-04-10: Latest branch-local attempt started
  `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_shl.rs --start-symbol unchecked_shl_u16 --terminate-on-thunk --proof-dir /tmp/kmir-0011-unchecked-shl-u16 --reload --fail-fast --max-workers 1`, but the run exited with status `143` before any terminal proof result was captured. No new frontier was established, and no code changes were kept.
- 2026-04-10: Latest branch-local attempt started
  `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_shr.rs --start-symbol unchecked_shr_u8 --terminate-on-thunk --proof-dir /tmp/kmir-0011-unchecked-shr-u8 --reload --fail-fast --max-workers 1`, but the run was interrupted before any terminal proof result was captured. No new frontier was established, and no code changes were kept.
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
- 2026-04-09: Scoped discovery check for the delegated Part 1 slice collected
  exactly `test_verify_rust_std[unchecked_sub]` using:
  `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_verify_rust_std --collect-only -k "unchecked_sub and not fail" -q`.
- 2026-04-09: Direct proof follow-up run completed with
  `ProofStatus.PASSED` for `unchecked_sub_u8` using:
  `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_sub.rs --start-symbol unchecked_sub_u8 --terminate-on-thunk --proof-dir /tmp/kmir-0011-unchecked-sub-u8 --reload --fail-fast --max-workers 1`.
- 2026-04-09: Scoped discovery check for the planner-selected Part 2 follow-up
  collected exactly `test_verify_rust_std[wrapping_shr]` using:
  `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_verify_rust_std --collect-only -k "wrapping_shr and not fail" -q`.
- 2026-04-09: Direct proof follow-up run completed with
  `ProofStatus.PASSED` for `wrapping_shr_u8` using:
  `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/wrapping_shr.rs --start-symbol wrapping_shr_u8 --terminate-on-thunk --proof-dir /tmp/kmir-0011-wrapping-shr-u8 --reload --fail-fast --max-workers 1`.
- 2026-04-09: Scoped discovery check for the planner-selected widening-mul
  follow-up collected exactly `test_verify_rust_std[widening_mul]` using:
  `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_verify_rust_std --collect-only -k "widening_mul and not fail" -q`.
- 2026-04-09: Direct proof follow-up run completed with
  `ProofStatus.PASSED` for `widening_mul_u8` using:
  `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/widening_mul.rs --start-symbol widening_mul_u8 --terminate-on-thunk --proof-dir /tmp/kmir-0011-widening-mul-u8 --reload --fail-fast --max-workers 1`.
- 2026-04-09: Scoped discovery check for the next Part 2 slice collected
  exactly `test_verify_rust_std[carrying_mul]` using:
  `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_verify_rust_std --collect-only -k "carrying_mul and not fail" -q`.
- 2026-04-09: Direct proof follow-up run completed with
  `ProofStatus.PASSED` for `carrying_mul_u8` using:
  `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/carrying_mul.rs --start-symbol carrying_mul_u8 --terminate-on-thunk --proof-dir /tmp/kmir-0011-carrying-mul-u8 --reload --fail-fast --max-workers 1`.
- 2026-04-09: Scoped discovery check for the delegated unchecked-mul slice
  collected exactly `test_verify_rust_std[unchecked_mul]` using:
  `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_verify_rust_std --collect-only -k "unchecked_mul and not fail" -q`.
- 2026-04-09: Direct proof follow-up run completed with
  `ProofStatus.PASSED` for `unchecked_mul_u8` using:
  `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_mul.rs --start-symbol unchecked_mul_u8 --terminate-on-thunk --proof-dir /tmp/kmir-0011-unchecked-mul-u8 --reload --fail-fast --max-workers 1`.

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
- Confirmed the delegated unchecked-sub case is wired through the same runner:
  `test_verify_rust_std[unchecked_sub]` is selected by
  `-k "unchecked_sub and not fail"`.
- Re-executed the delegated Part 1 slice directly with `kmir prove-rs`;
  `unchecked_sub_u8` passed without any new support changes, broadening the
  integer-side evidence while keeping the float blocker isolated.
- Confirmed the next safe-API sibling is wired through the same runner:
  `test_verify_rust_std[wrapping_shr]` is selected by
  `-k "wrapping_shr and not fail"`.
- Re-executed the planner-selected Part 2 follow-up directly with
  `kmir prove-rs`; `wrapping_shr_u8` passed without any new support changes,
  broadening the safe-API evidence while preserving the existing float blocker
  boundary.
- Confirmed the next safe-API family is wired through the same runner:
  `test_verify_rust_std[widening_mul]` is selected by
  `-k "widening_mul and not fail"`.
- Re-executed the planner-selected widening-mul slice directly with
  `kmir prove-rs`; `widening_mul_u8` passed without any new support changes,
  broadening the safe-API evidence beyond the wrapping-shift pair while
  preserving the existing float blocker boundary.
- Re-executed the planner-selected carrying-mul slice directly with
  `kmir prove-rs`; `carrying_mul_u8` passed without any new support changes,
  broadening the safe-API evidence beyond wrapping shifts and widening-mul
  while preserving the existing float blocker boundary.
- Re-executed the next Part 1 multiplication slice directly with
  `kmir prove-rs`; `unchecked_mul_u64` passed without any new support changes,
  widening the integer evidence one step further while preserving the existing
  float blocker boundary.

## Evidence for next evaluator step

- Technical port commit exists: `2e09185c`.
- Challenge 0011 artifact set now exists under
  `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints`.
- Validation now includes branch-local passing proof evidence in two published
  requirement families:
  `unchecked_add_u8`, `unchecked_neg_i8`, `unchecked_sub_u8`,
  `unchecked_mul_u8`, `unchecked_mul_u16`, `unchecked_mul_u32`, and
  `unchecked_mul_u64` pass in Part 1, and
  `wrapping_shl_u8`, `wrapping_shr_u8`, `widening_mul_u8`, plus
  `carrying_mul_u8` pass in Part 2.
- Float blocker signal remains present in ported evidence:
  `to_int_unchecked-fail` expected outputs include stuck float intrinsic hooks.

## Next handoff

- The planner-selected `carrying_mul_u8` slice is complete and passed.
- The planner-selected `unchecked_mul_u8` slice is complete and passed.
- The planner-selected `unchecked_mul_u16` slice is complete and passed.
- The planner-selected `unchecked_mul_u32` slice is complete and passed.
- The planner-selected `unchecked_mul_u64` slice is complete and passed.
- If the generator continues in the same file, the next concrete target is
  the next available `unchecked_mul_*` width beyond `u64`, if any is present
  in the branch-local harness.
- Evaluator should reassess whether the branch’s twelve direct proof passes
  across Part 1 and Part 2 materially change the non-float readiness signal,
  while keeping the remaining float blocker tied to the precise
  `fabsf32` / `fabsf64` frontier.
- If the planner delegates another generator slice after that reassessment, it
  should choose a new explicit non-float target rather than revisiting the
  now-completed `carrying_mul_u8` slice.
- Exact next step from this checkpoint: hold on `unchecked_shr`; the
  diagnostics did not produce a branch-worthy frontier change, so do not queue
  another proof run unless a new bound or a new observation is introduced.

## Evaluator Note

- 2026-04-09: `wrapping_shl_u8` is strong evidence, but the remaining
  unverified integer and safe-API surface is still broad; `unchecked_sub_u8`
  improves the Part 1 evidence, but the strongest justified verdict remains
  `IN PROGRESS` rather than `CONDITIONALLY READY`.
- 2026-04-09: After the `unchecked_sub_u8` pass, the evaluator score is now
  `2.8 / 3`; the breadth gap is still the limiting factor, and the float
  blocker remains the precise `fabsf32` / `fabsf64` frontier in
  `to_int_unchecked`.
- 2026-04-09: After the `wrapping_shr_u8` pass, the strongest updated evaluator
  question is whether the non-float evidence is now broad enough to move past
  `IN PROGRESS`; the remaining technical blocker is still the precise
  `fabsf32` / `fabsf64` float frontier in `to_int_unchecked`, not a new Part 2
  regression.
- 2026-04-09: Re-evaluation after `wrapping_shr_u8` keeps the verdict at
  `IN PROGRESS`; the branch is stronger, but the remaining integer and safe-API
  matrix is still broad enough that `CONDITIONALLY READY` would overstate the
  present evidence.
- 2026-04-09: After the `unchecked_mul_u16` pass, the branch now has ten
  direct proof slices and still needs broader non-float coverage before the
  float blocker can be treated as the only remaining gap.
- 2026-04-10: Interrupted `kmir prove-rs` attempt started for
  `unchecked_shr_u8` using:
  `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_shr.rs --start-symbol unchecked_shr_u8 --terminate-on-thunk --proof-dir /tmp/kmir-0011-unchecked-shr-u8 --reload --fail-fast --max-workers 1`;
  no terminal proof result was captured before interruption, no new frontier
  was established, and no code changes were kept.
- 2026-04-10: Direct proof follow-up run completed with
  `ProofStatus.PASSED` for `unchecked_shl_u8` using:
  `timeout 900s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_shl.rs --start-symbol unchecked_shl_u8 --terminate-on-thunk --proof-dir /tmp/kmir-0011-unchecked-shl-u8 --reload --fail-fast --max-workers 1`.
  The summary reported `nodes: 7`, `pending: 0`, `failing: 0`, `stuck: 0`,
  `terminal: 3`.
- 2026-04-10: Scoped discovery check for the next `unchecked_shl` sibling
  collected exactly `test_verify_rust_std[unchecked_shl]` using:
  `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_verify_rust_std --collect-only -k "unchecked_shl and not fail" -q`.
  The target is still present in collection, so the next bounded move remains
  `unchecked_shl_u16`.
- 2026-04-10: Scoped discovery check for `unchecked_shr` collected exactly
  `test_verify_rust_std[unchecked_shr]` using:
  `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_verify_rust_std --collect-only -k "unchecked_shr and not fail" -q`.
  The family is still present in collection.
- 2026-04-10: Diagnostic pass over `unchecked_shr.rs` and the matching
  `show/unchecked_shr-fail.*.expected` files showed that the harness already
  bottoms out at `unchecked_shr_u8`; the other widths are only width variants
  of the same `binOpShrUnchecked` frontier. The smallest observed frontier is
  the `unchecked_shr_u8` expected state, which reaches
  `#applyBinOp ( binOpShrUnchecked , Integer ( ARG_UINT1:Int , 8 , false ) ,
  Integer ... ) ~> #freezer` with the `ARG_UINT2:Int >=Int 0` constraint.
  No narrower branch-worthy subcase was found, so another proof run is not
  justified from this checkpoint alone.
