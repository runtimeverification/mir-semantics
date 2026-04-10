# Challenge 0027: Challenge 27: Verify atomically reference-counted Cell implementation

Reference inputs:

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0027-arc.md
- Tracking issue: [#383](https://github.com/model-checking/verify-rust-std/issues/383)
- Tracking issue state at bootstrap: `OPEN`

Execution context:

- Branch: `verify-rust-std/reexec-0027-arc`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0027-arc`
- Planner record: `docs/verify-rust-std/challenges/0027-arc/planner.md`
- Generator record: `docs/verify-rust-std/challenges/0027-arc/generator.md`
- Evaluator record: `docs/verify-rust-std/challenges/0027-arc/evaluator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0027-arc/rubric.md`
- Success criteria: `docs/verify-rust-std/challenges/0027-arc/success-criteria.md`
- Workpad: `docs/verify-rust-std/challenges/0027-arc/workpad.md`

Challenge-local artifact contract:

- Keep verification harnesses and frontier reproducers in separate files.
- A symbolic proof harness should encode the `Arc` contract under verification.
- A frontier reproducer should remain concrete and narrow so semantic blockers
  stay auditable without being counted as verification progress.
- Place harnesses, tests, expected output, and supporting files in this
  directory.
- Keep changes organized so proof or semantic commits can be cherry-picked
  cleanly later.
- Record any exceptional dependency change in the generator and evaluator logs
  before landing it.

Status board:

- Planner: bootstrap complete
- Generator: proof harness added; bounded proof attempt recorded frontier leaf `4`
- Evaluator: bootstrap complete
- Draft PR: not created

Proof evidence:

- Harness: `arc-from-raw-in.rs`
- Start symbol: `verify_arc_from_raw_in`
- Result: `ProofStatus.FAILED`
- Frontier leaf: `4`
- Frontier site: `Box::<alloc::sync::ArcInner<u32>, std::alloc::System>::new_uninit_in`
