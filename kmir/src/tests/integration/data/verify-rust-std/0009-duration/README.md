# Challenge 0009: Challenge 9: Safe abstractions for `core::time::Duration`

Reference inputs:

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0009-duration.md
- Tracking issue: [#72](https://github.com/model-checking/verify-rust-std/issues/72)
- Tracking issue state at bootstrap: `CLOSED`

Execution context:

- Branch: `verify-rust-std/reexec-0009-duration`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0009-duration`
- Planner record: `docs/verify-rust-std/challenges/0009-duration/planner.md`
- Generator record: `docs/verify-rust-std/challenges/0009-duration/generator.md`
- Evaluator record: `docs/verify-rust-std/challenges/0009-duration/evaluator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0009-duration/rubric.md`

Challenge-local artifact contract:

- Place harnesses, tests, expected output, and supporting files in this
  directory.
- Keep changes organized so proof or semantic commits can be cherry-picked
  cleanly later.
- Record any exceptional dependency change in the generator and evaluator logs
  before landing it.

Status board:

- Planner: done (requirements extracted, blockers identified)
- Generator: done (15 harnesses created, 9 pass, 5 expected-fail, 1 blocked)
- Evaluator: not started
- Draft PR: not created
