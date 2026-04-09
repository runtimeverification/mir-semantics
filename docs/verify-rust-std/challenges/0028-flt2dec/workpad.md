# Workpad: Challenge 0028

## Current handoff state

- Branch: `verify-rust-std/reexec-0028-flt2dec`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0028-flt2dec`
- Status at planner handoff: the first `digits_to_dec_str` probe has already run and produced a concrete wrapper-artifact blocker; no code, proof, or evaluator changes are in scope for this planner.

## Evidence gathered

- The published challenge goal is to verify `core::num::flt2dec`, the float-to-decimal conversion module.
- The published success criteria cover the safe entry points `digits_to_dec_str`, `digits_to_exp_str`, `to_shortest_str`, `to_shortest_exp_str`, `to_exact_exp_str`, `to_exact_fixed_str`, and the `grisu` and `dragon` strategy wrappers `format_shortest_opt`, `format_shortest`, `format_exact_opt`, and `format_exact`.
- The challenge also requires the standard UB exclusions: no dangling or misaligned memory access, no compiler-intrinsic UB, no mutation of immutable bytes, and no invalid values.
- Challenge 0011 records the reusable float warning: the float-sensitive path previously stalled on missing KMIR / haskell-backend float-value support, so any new probe should determine whether 0028 hits the same boundary or a different artifact issue.
- The 0028 artifact directory now contains a first probe harness:
  `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs`.
- Because `digits_to_dec_str` is private inside `core::num::flt2dec`, the
  first probe had to copy only that function body into a challenge-local
  wrapper rather than call the std item directly from an external crate.
- The first compile/setup issues were both artifact-level:
  `std::num::fmt::Part` was unavailable outside `cfg(test)`, and this worktree
  lacked the compiled K definition cache until `make build` was run.
- After clearing those setup issues, the first concrete proof failure was a
  stuck leaf in slice indexing, not a float builtins crash:
  `<std::ops::Range<usize> as std::slice::SliceIndex<[u8]>>::index`
  at `library/core/src/slice/index.rs:440`, stuck on
  `thunk ( #applyBinOp ( binOpOffset , ... ) )`.
- This first result is therefore distinct from Challenge 0011: it did not
  reproduce the earlier float-value/backend gap.
- A follow-up rerun on this branch replaced the copied function's
  `&buf[..exp]` / `&buf[exp..]` path with a raw helper `split_at_raw`, and
  removed result indexing from `main`, so the probe no longer depends on the
  old `Range<usize>::index` route.
- The narrower rerun still did not reach a `flt2dec`-owned boundary. Its first
  new stuck leaf is `std::slice::from_raw_parts::<'_, u8>` at
  `library/core/src/slice/raw.rs:138`, reached from `split_at_raw` at
  `dec/digits_to_dec_str_probe.rs:9`.
- The current evidence therefore says the next boundary is still harness-level,
  but it is now a narrower raw-slice artifact rather than the original
  slice-index/pointer-offset artifact.

## Planning decisions

- Keep the first generator task to one representative probe instead of the full function list.
- Favor `digits_to_dec_str` as the initial signal source, but strip the wrapper
  indexing so the evaluator can classify backend support versus harness artifact
  cleanly.
- Do not expand scope into backend work unless the follow-up probe shows a distinct, challenge-local float limitation.

## Reusable rubric patterns for evaluator

- Every published success criterion needs a concrete artifact or an explicit blocker, not a generic status note.
- A float-related blocker should name the exact missing capability.
- The evaluator should distinguish a narrow external dependency from a structural missing implementation.

## Failed-attempt log

- Initial plain compile of the probe failed while importing
  `std::num::fmt::Part`; the harness was adjusted to use
  `core::num::fmt::Part` and `extern crate core;`.
- Initial `kmir prove` failed before proving anything because
  `/home/zhaoji/.cache/kdist-d250b97/mir-semantics/haskell` did not exist.
  Running `make build` resolved that branch-local prerequisite.
- A capped probe run with `--max-iterations 3` stopped at `ProofStatus.PENDING`
  and was discarded as a driver-limit artifact rather than the first semantic result.
- The narrowed follow-up rerun bypassed `SliceIndex::index`, but then failed in
  `std::slice::from_raw_parts::<'_, u8>` from the challenge-local
  `split_at_raw` helper, so it still does not expose a real `flt2dec`
  frontier.

## Next handoff

- Generator has now produced the narrower `digits_to_dec_str` probe and rerun
  it.
- Evaluator can now classify Sprint 1 against concrete evidence:
  the original slice-index artifact is gone, but the next meaningful result is
  still harness-level at raw-slice construction rather than a float backend
  crash.
- Any further generator work should stay narrow and only target the
  `split_at_raw` / `from_raw_parts` artifact if another follow-up slice is
  explicitly requested.
