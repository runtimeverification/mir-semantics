# Execution Plan: Challenge 0011

Current objective:
- Move Challenge 11 toward a terminal portfolio state by adding the next narrow Part 1 unsafe-method proof slice on the current branch, now that `unchecked_shl_u8` has passed and the latest evaluator result at `05ebb42f` still rates the branch `IN PROGRESS` at `2.97 / 3` because the remaining gap is breadth in the integer/safe-API matrix, while preserving the float blocker as a separate, explicitly evidenced terminal constraint.

Next generator task:
- First reconfirm the `unchecked_shl` harness wiring with a cheap scoped discovery check (`pytest --collect-only -k "unchecked_shl and not fail"`), then only schedule another `kmir prove-rs` retry for `unchecked_shl_u16` if the case is still present and the retry can be bounded differently from the previous exit-143 attempt.

Generator acceptance evidence:
- A concrete mapping from each published requirement to an artifact or an explicit blocker.
- Reproducible command(s) and file paths for the harness or proof re-execution, including the exact `start-symbol` used for `widening_mul_u8`.
- A clear statement of whether the Part 2 proof passes; if it does not, the result must name the exact missing support, unsupported hook, or artifact omission.

Plan slices:
1. Reconfirm the published function list and success criteria from the challenge page and PR #985.
2. Reconfirm the `unchecked_shl` case wiring cheaply, then retry `unchecked_shl_u16` only if the discovery step shows the slice is still available and the retry can be made meaningfully more bounded than the previous long-running blind attempt.
3. Hand the evaluator a refreshed frontier classification that distinguishes the remaining integer and safe-API breadth from the float-capability blocker once the next bounded action produces new evidence.

Stop conditions:
- Stop at `BLOCKED` if the discovery check shows `unchecked_shl_u16` is no longer collected or the harness wiring has regressed.
- Stop after the exit-143 `unchecked_shl_u16` attempt is recorded; do not repeat the same long-running proof blindly without a new bound or a new observation.
- Continue only if a concrete technical subtask remains with measurable value and can be delegated without broadening scope.
