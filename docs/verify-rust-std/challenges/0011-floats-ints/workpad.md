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

- None yet. This is the first challenge-local planning pass on the re-execution branch.

## Next handoff

- Generator should produce the first challenge-local technical attempt and attach command/file evidence.
- Evaluator should update the rubric only after that evidence is available.
