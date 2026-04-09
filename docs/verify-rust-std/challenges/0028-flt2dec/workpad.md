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

## Planning decisions

- Keep the first generator task to one representative probe instead of the full function list.
- Favor `digits_to_dec_str` as the initial signal source so the evaluator can classify backend support versus artifact wiring quickly.
- Do not expand scope into backend work unless the first probe shows a distinct, challenge-local artifact problem.

## Reusable rubric patterns for evaluator

- Every published success criterion needs a concrete artifact or an explicit blocker, not a generic status note.
- A float-related blocker should name the exact missing capability.
- The evaluator should distinguish a narrow external dependency from a structural missing implementation.

## Failed-attempt log

- None yet.

## Next handoff

- Generator should build and rerun one minimal challenge-local probe for `digits_to_dec_str`, then record the exact failure mode or first passing evidence.
- Evaluator should wait for that evidence before extending `rubric.md`.
