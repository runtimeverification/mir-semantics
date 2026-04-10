# Challenge 0012: Challenge 12: Safety of `NonZero`

Reference inputs:

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0012-nonzero.md
- Tracking issue: [#71](https://github.com/model-checking/verify-rust-std/issues/71)
- Tracking issue state at bootstrap: `OPEN`

Execution context:

- Branch: `verify-rust-std/reexec-0012-nonzero`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0012-nonzero`
- Planner record: `docs/verify-rust-std/challenges/0012-nonzero/planner.md`
- Generator record: `docs/verify-rust-std/challenges/0012-nonzero/generator.md`
- Evaluator record: `docs/verify-rust-std/challenges/0012-nonzero/evaluator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0012-nonzero/rubric.md`

Challenge-local artifact contract:

- Place harnesses, tests, expected output, and supporting files in this
  directory.
- Keep changes organized so proof or semantic commits can be cherry-picked
  cleanly later.
- Record any exceptional dependency change in the generator and evaluator logs
  before landing it.
- Keep the proof coverage map in
  `docs/verify-rust-std/challenges/0012-nonzero/success-criteria.md`.

Proof harnesses currently in scope:

- `new.rs` - Part 1 harness for `NonZero::new`
- `new_unchecked.rs` - Part 1 harness for `NonZero::new_unchecked`
- `from_mut.rs` - Part 1 harness for `NonZero::from_mut`
- `count_ones.rs` - Part 2 seed harness for `NonZero::count_ones`

Control reproducer:

- `transmute_wrapper_u8.rs` - transparent-wrapper control used to separate
  generic same-size transmute support from the exact `u8 -> Option<NonZeroU8>`
  niche-cast frontier. This file is not a published `NonZero` verification
  target.

Status board:

- Planner: started
- Generator: in progress
- Evaluator: started
- Draft PR: created

Artifact progress:

- Part 1 semantics (initial slice):
  - `new.rs`
  - `new_unchecked.rs`
  - `from_mut.rs`
- Part 2 low-risk seed:
  - `count_ones.rs`
- Control repro:
  - `transmute_wrapper_u8.rs`
