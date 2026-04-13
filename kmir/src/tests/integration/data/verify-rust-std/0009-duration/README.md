# Challenge 0009: Challenge 9: Safe abstractions for `core::time::Duration`

Reference inputs:

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0009-duration.md
- Tracking issue: [#72](https://github.com/model-checking/verify-rust-std/issues/72)
- Tracking issue state at bootstrap: `CLOSED`

Execution context:

- Branch: `verify-rust-std/reexec-0009-duration`
- Planner record: `docs/verify-rust-std/challenges/0009-duration/plan.md`
- Evaluator record: `docs/verify-rust-std/challenges/0009-duration/evaluation_result.md`
- Workpad: `docs/verify-rust-std/challenges/0009-duration/workpad.md`

Challenge-local artifact contract:

- Place harnesses, tests, expected output, and supporting files in this
  directory.
- Keep changes organized so proof or semantic commits can be cherry-picked
  cleanly later.
- Record any exceptional dependency change in the generator and evaluator logs
  before landing it.

Status board:

- Planner: done (requirements extracted, blockers identified)
- Generator: done (29 harnesses, 22 pass, 5 expected-fail, 4 blocked on niche decoding)
- Evaluator: done (16/16 required methods verified)
- PR: runtimeverification/mir-semantics#1034
