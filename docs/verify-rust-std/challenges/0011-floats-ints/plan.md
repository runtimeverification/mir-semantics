# Execution Plan: Challenge 0011

Current objective:
- Move Challenge 11 toward a terminal portfolio state by adding one new Part 2 integer proof slice on the current branch and preserving the float blocker as a separate, explicitly evidenced terminal constraint.

Next generator task:
- Prove `wrapping_shl_u8` end-to-end with a scoped `kmir prove-rs` run on `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/wrapping_shl.rs`, then record whether the branch now has proof evidence in a second challenge family beyond the completed Part 1 slices.

Generator acceptance evidence:
- A concrete mapping from each published requirement to an artifact or an explicit blocker.
- Reproducible command(s) and file paths for the harness or proof re-execution, including the exact `start-symbol` used for `wrapping_shl_u8`.
- A clear statement of whether the Part 2 proof passes; if it does not, the result must name the exact missing support, unsupported hook, or artifact omission.

Plan slices:
1. Reconfirm the published function list and success criteria from the challenge page and PR #985.
2. Execute one new Part 2 proof slice, starting with `wrapping_shl_u8`, to widen the proof evidence beyond the two completed Part 1 slices.
3. Hand the evaluator a refreshed frontier classification that distinguishes the remaining integer breadth from the float-capability blocker.
4. Keep the float path evidence separate so the evaluator can still classify the branch as blocked on backend capability rather than on an ambiguous artifact gap.

Stop conditions:
- Stop at `BLOCKED` if the `wrapping_shl_u8` proof reveals an uncovered backend or harness defect that prevents any new Part 2 evidence.
- Stop at `CONDITIONALLY READY` if the new Part 2 proof passes and the remaining gap is only the previously documented float-capability blocker.
- Continue only if a concrete technical subtask remains with measurable value and can be delegated without broadening scope.
