# Execution Plan: Challenge 0011

Current objective:
- Move Challenge 11 toward a terminal portfolio state by adding the next narrow Part 1 unsafe-method proof slice on the current branch, now that `unchecked_shl_u8` has passed, the latest evaluator result still rates the branch `IN PROGRESS` at `2.97 / 3`, and the `unchecked_shr` diagnostics recorded at `388acc64` established no smaller or more concrete frontier than `unchecked_shr_u8`, while preserving the float blocker as a separate, explicitly evidenced terminal constraint.

Next generator task:
- Prove `unchecked_shl_u16` end-to-end with a scoped `kmir prove-rs` run on `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/unchecked_shl.rs` using `--start-symbol unchecked_shl_u16`, then record whether the branch extends the already-passing `unchecked_shl` family beyond `unchecked_shl_u8` without reopening the exhausted `unchecked_shr` diagnostic path.

Generator acceptance evidence:
- A concrete mapping from each published requirement to an artifact or an explicit blocker.
- Reproducible command(s) and file paths for the harness or proof re-execution, including the exact `start-symbol` used for `widening_mul_u8`.
- A clear statement of whether the Part 2 proof passes; if it does not, the result must name the exact missing support, unsupported hook, or artifact omission.

Plan slices:
1. Reconfirm the published function list and success criteria from the challenge page and PR #985.
2. Execute one new Part 1 proof slice, starting with `unchecked_shl_u16`, because the completed `unchecked_shr` diagnostics still collapse to the same `binOpShrUnchecked` frontier and do not justify spending another generator turn there.
3. Hand the evaluator a refreshed frontier classification that distinguishes the remaining integer and safe-API breadth from the float-capability blocker once the next bounded action produces new evidence.

Stop conditions:
- Stop at `BLOCKED` if the discovery check shows `unchecked_shl_u16` is no longer collected or the harness wiring has regressed.
- Stop after the `unchecked_shl_u16` outcome is recorded; if it exits `143` again without a new frontier, do not repeat the same long-running proof blindly without a new bound or a new observation.
- Continue only if a concrete technical subtask remains with measurable value and can be delegated without broadening scope; do not reopen `unchecked_shl_u8`, and keep `unchecked_shr` parked until there is evidence stronger than the current shared `binOpShrUnchecked` frontier.
