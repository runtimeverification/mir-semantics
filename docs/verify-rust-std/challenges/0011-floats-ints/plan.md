# Execution Plan: Challenge 0011

Current objective:
- Move Challenge 11 toward a terminal portfolio state by adding the next narrow Part 1 unsafe-method proof slice on the current branch, now that `unchecked_shl_u8` has passed and the latest evaluator result at `05ebb42f` still rates the branch `IN PROGRESS` at `2.97 / 3` because the remaining gap is breadth in the integer/safe-API matrix, while preserving the float blocker as a separate, explicitly evidenced terminal constraint.

Next generator task:
- Do not blind-retry `unchecked_shr_u8`; the narrowest next move is a diagnostic pass over the `unchecked_shr` harness and expected-output surface to determine whether a smaller or more observable subcase exists, and only then decide whether another proof run is justified.

Generator acceptance evidence:
- A concrete mapping from each published requirement to an artifact or an explicit blocker.
- Reproducible command(s) and file paths for the harness or proof re-execution, including the exact `start-symbol` used for `widening_mul_u8`.
- A clear statement of whether the Part 2 proof passes; if it does not, the result must name the exact missing support, unsupported hook, or artifact omission.

Plan slices:
1. Reconfirm the published function list and success criteria from the challenge page and PR #985.
2. Inspect the `unchecked_shr` harness and associated expected-output artifacts to find the smallest diagnosable subcase or a concrete stuck frontier, so the next move is evidence-driven rather than another blind `kmir prove-rs` retry.
3. Hand the evaluator a refreshed frontier classification that distinguishes the remaining integer and safe-API breadth from the float-capability blocker once the next bounded action produces new evidence.

Stop conditions:
- Stop at `BLOCKED` if the discovery check shows `unchecked_shl_u16` is no longer collected or the harness wiring has regressed.
- Stop after the exit-143 `unchecked_shl_u16` attempt is recorded; do not repeat the same long-running proof blindly without a new bound or a new observation.
- Continue only if a concrete technical subtask remains with measurable value and can be delegated without broadening scope; if `unchecked_shr` still looks expensive after collection, keep the work at discovery or artifact-inspection level rather than re-queuing a timeout-prone proof slice.
