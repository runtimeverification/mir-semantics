# Challenge 0001: Challenge 1: Verify `core` transmuting methods

Reference inputs:

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0001-core-transmutation.md
- Tracking issue: [#19](https://github.com/model-checking/verify-rust-std/issues/19)
- Tracking issue state at bootstrap: `CLOSED`

Execution context:

- Branch: `verify-rust-std/reexec-0001-core-transmutation`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0001-core-transmutation`
- Planner record: `docs/verify-rust-std/challenges/0001-core-transmutation/planner.md`
- Generator record: `docs/verify-rust-std/challenges/0001-core-transmutation/generator.md`
- Evaluator record: `docs/verify-rust-std/challenges/0001-core-transmutation/evaluator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0001-core-transmutation/rubric.md`

Challenge-local artifact contract:

- Place harnesses, tests, expected output, and supporting files in this
  directory.
- Keep changes organized so proof or semantic commits can be cherry-picked
  cleanly later.
- Record any exceptional dependency change in the generator and evaluator logs
  before landing it.
- Keep the branch-local coverage map in
  `docs/verify-rust-std/challenges/0001-core-transmutation/success-criteria.md`.

Proof harnesses currently in scope:

- `transmute_roundtrip.rs` - proof entrypoints for `core::mem::transmute`
- `transmute_unchecked_maybeuninit.rs` - proof entrypoints for
  `core::intrinsics::transmute_unchecked` and the `MaybeUninit` bridge
- `maybeuninit_array_assume_init.rs` - proof entrypoint for
  `MaybeUninit<T>::array_assume_init`

Minimal reproducers / controls:

- None yet for this first breadth-first sweep. The current branch is using
  proof-shaped harnesses first so the coverage table can be populated before
  deeper semantic classification.

Replay / CI commands:

- Update proof expected output for the first harness sweep:
  `cd /home/zhaoji/projs/mir-semantics-vrs/challenges/0001-core-transmutation/kmir && uv run pytest src/tests/integration/test_integration.py -v --timeout=600 -k "transmute_roundtrip or transmute_unchecked_maybeuninit or maybeuninit_array_assume_init" --update-expected-output`
- Run the targeted verification sweep without rewriting expected output:
  `cd /home/zhaoji/projs/mir-semantics-vrs/challenges/0001-core-transmutation/kmir && uv run pytest src/tests/integration/test_integration.py -v --timeout=600 -k "transmute_roundtrip or transmute_unchecked_maybeuninit or maybeuninit_array_assume_init"`
- Run the full integration suite when the sweep is stable:
  `cd /home/zhaoji/projs/mir-semantics-vrs/challenges/0001-core-transmutation/kmir && uv run pytest src/tests/integration/test_integration.py -v --timeout=600`

Validation checkpoint:

- `transmute_roundtrip.rs`: passed and emitted show output for both start symbols.
- `transmute_unchecked_maybeuninit.rs`: reached a backend runtime error on `FLOAT.int2float`.
- `maybeuninit_array_assume_init.rs`: needed `#![feature(maybe_uninit_array_assume_init)]` and still fails in proof, so it remains a frontier item.

Status board:

- Planner: not started
- Generator: waiting for planner and evaluator baselines
- Evaluator: not started
- Draft PR: not created

Artifact progress:

- Primitive transmutation seeds:
  - `transmute_roundtrip.rs`
  - `transmute_unchecked_maybeuninit.rs`
- MaybeUninit seed:
  - `maybeuninit_array_assume_init.rs`
