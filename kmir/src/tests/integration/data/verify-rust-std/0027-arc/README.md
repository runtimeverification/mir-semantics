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

- Planner: updated to shared frontier / `malloc` noBody follow-up
- Generator: proof harness added; frontier reproducer split recorded; latest
  validation moved both proofs to the shared `malloc` `noBody` leaf at node 3
- Evaluator: active / awaiting reassessment
- Draft PR: open and current

Proof evidence:

- Harness: `arc-from-raw-in.rs`
- Start symbol: `verify_arc_from_raw_in`
- Result: `ProofStatus.FAILED`
- Frontier leaf: `3`
- Frontier site: `#setUpCalleeData(monoItemFn(... name: symbol("malloc"), body: noBody), ...)`
- Frontier reproducer: `arc-from-raw-in-frontier-fail.rs`
- Frontier reproducer start symbol: `main`
- Frontier reproducer note: smaller than the symbolic harness because it fixes
  the payload and uses `main`

Validation commands:

- `timeout 3600s make -C /home/zhaoji/projs/mir-semantics-vrs/challenges/0027-arc build PARALLEL=2`
- `uv --project /home/zhaoji/projs/mir-semantics-vrs/challenges/0027-arc/kmir run -- kmir prove /home/zhaoji/projs/mir-semantics-vrs/challenges/0027-arc/kmir/src/tests/integration/data/verify-rust-std/0027-arc/arc-from-raw-in-frontier-fail.rs --start-symbol main --proof-dir /tmp/arc-from-raw-in-frontier-proof-0027-fix1 --verbose --terminate-on-thunk`
- `uv --project /home/zhaoji/projs/mir-semantics-vrs/challenges/0027-arc/kmir run -- kmir show arc-from-raw-in-frontier-fail.main --proof-dir /tmp/arc-from-raw-in-frontier-proof-0027-fix1 --nodes 3 --full-printer`
- `uv --project /home/zhaoji/projs/mir-semantics-vrs/challenges/0027-arc/kmir run -- kmir prove /home/zhaoji/projs/mir-semantics-vrs/challenges/0027-arc/kmir/src/tests/integration/data/verify-rust-std/0027-arc/arc-from-raw-in.rs --start-symbol verify_arc_from_raw_in --proof-dir /tmp/arc-from-raw-in-proof-0027-fix1 --verbose --terminate-on-thunk`
- `uv --project /home/zhaoji/projs/mir-semantics-vrs/challenges/0027-arc/kmir run -- kmir show arc-from-raw-in.verify_arc_from_raw_in --proof-dir /tmp/arc-from-raw-in-proof-0027-fix1 --nodes 3 --full-printer`
