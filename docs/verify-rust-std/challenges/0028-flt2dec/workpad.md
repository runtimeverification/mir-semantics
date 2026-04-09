# Workpad: Challenge 0028

## Current handoff state

- Branch: `verify-rust-std/reexec-0028-flt2dec`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0028-flt2dec`
- Status at planner handoff: bootstrap docs existed only; no challenge-local implementation, proof, or evaluator evidence has been produced by this planner.

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

## Planning decisions

- Keep the first generator task to one representative probe instead of the full function list.
- Favor `digits_to_dec_str` as the initial signal source so the evaluator can classify backend support versus artifact wiring quickly.
- Do not expand scope into backend work unless the first probe shows a distinct, challenge-local artifact problem.

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

## Next handoff

- Generator completed the planner-selected first probe and should stop here.
- Evaluator can now classify Sprint 1 against concrete evidence:
  the first `digits_to_dec_str` probe did run, and its first meaningful result
  was a slice-index/pointer-offset stuck leaf rather than a float backend crash.
- Any follow-up generator work should stay narrow and focus on removing the
  wrapper's slice-index artifact if more direct `digits_to_dec_str` evidence is
  needed; backend float escalation is not yet justified from this record.
