# Execution Plan: Challenge 0011

Current objective:
- Move Challenge 11 toward a terminal portfolio state by adding the next narrow Part 1 unsafe-method proof slice on the current branch, now that `unchecked_mul_u64` has passed and the latest evaluator result at `71b2d625` still rates the branch `IN PROGRESS` at `2.96 / 3`, while preserving the float blocker as a separate, explicitly evidenced terminal constraint.

Next generator task:
- Prove `unchecked_shl_u8` end-to-end with a scoped `kmir prove-rs` run on `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_shl.rs`, then record whether the branch now has another passing Part 1 arithmetic slice beyond `unchecked_mul_u8`, `unchecked_mul_u16`, `unchecked_mul_u32`, `unchecked_mul_u64`, add/neg/sub, and the already-passing Part 2 slices.

Generator acceptance evidence:
- A concrete mapping from each published requirement to an artifact or an explicit blocker.
- Reproducible command(s) and file paths for the harness or proof re-execution, including the exact `start-symbol` used for `widening_mul_u8`.
- A clear statement of whether the Part 2 proof passes; if it does not, the result must name the exact missing support, unsupported hook, or artifact omission.

Plan slices:
1. Reconfirm the published function list and success criteria from the challenge page and PR #985.
2. Execute one new Part 1 proof slice, starting with `unchecked_shl_u8`, to continue widening the integer matrix on the already-validated shift path without broadening scope.
3. Hand the evaluator a refreshed frontier classification that distinguishes the remaining integer and safe-API breadth from the float-capability blocker.

Stop conditions:
- Stop at `BLOCKED` if the `unchecked_shl_u8` proof reveals an uncovered backend or harness defect that prevents any new Part 1 evidence.
- Stop after recording the `unchecked_shl_u8` outcome and hand the evaluator the updated frontier; do not widen the slice in the same delegation.
- Continue only if a concrete technical subtask remains with measurable value and can be delegated without broadening scope.
