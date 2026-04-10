# Challenge 0029: Safety of boxed

Reference inputs:

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0029-boxed.md
- Tracking issue: [#526](https://github.com/model-checking/verify-rust-std/issues/526)
- Tracking issue state at bootstrap: `OPEN`

Execution context:

- Branch: `verify-rust-std/reexec-0029-boxed`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0029-boxed`
- Success table: `docs/verify-rust-std/challenges/0029-boxed/success-criteria.md`
- Plan: `docs/verify-rust-std/challenges/0029-boxed/plan.md`
- Workpad: `docs/verify-rust-std/challenges/0029-boxed/workpad.md`
- Planner record: `docs/verify-rust-std/challenges/0029-boxed/planner.md`
- Generator record: `docs/verify-rust-std/challenges/0029-boxed/generator.md`
- Evaluator record: `docs/verify-rust-std/challenges/0029-boxed/evaluator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0029-boxed/rubric.md`

Current verification tranche:

- Root raw-ownership proofs:
  `Box<T>::from_raw`, `Box<T, A>::from_raw_in`, `Box<T>::from_non_null`, and
  `Box<T, A>::from_non_null_in`
- Root initialization-conversion proofs:
  scalar and slice `assume_init`
- Remaining constructor, conversion, dynamic-type, and ThinBox rows stay
  deferred until the first root tranche is classified.

Verification entrypoints:

- `box-from-raw.rs`
  `verify_box_from_raw`
- `box-from-raw-in.rs`
  `verify_box_from_raw_in`
- `box-from-non-null.rs`
  `verify_box_from_non_null`
- `box-from-non-null-in.rs`
  `verify_box_from_non_null_in`
- `box-assume-init.rs`
  `verify_box_assume_init_u32`
- `box-slice-assume-init.rs`
  `verify_box_slice_assume_init_u32_pair`

Success-criteria coverage snapshot:

- Independent proof harnesses added in this pass: 6 rows
- Proofs run in this pass so far:
  `verify_box_from_raw` and `verify_box_from_raw_in`
- Current concrete frontier:
  both proof runs fail at the same
  `thunk(#cast(Integer(4,64,false), castKindTransmute, ...))` leaf in
  `std::alloc::Layout::new::<u32>`
- Full per-function coverage map:
  `docs/verify-rust-std/challenges/0029-boxed/success-criteria.md`

Replay / validation commands:

- Compile-check `Box<T>::from_raw` harness via proof:
  `uv --project kmir run kmir prove /home/zhaoji/projs/mir-semantics-vrs/challenges/0029-boxed/kmir/src/tests/integration/data/verify-rust-std/0029-boxed/box-from-raw.rs --start-symbol verify_box_from_raw --proof-dir /tmp/boxed-from-raw-proof --verbose --terminate-on-thunk`
- Compile-check `Box<T, A>::from_raw_in` harness via proof:
  `uv --project kmir run kmir prove /home/zhaoji/projs/mir-semantics-vrs/challenges/0029-boxed/kmir/src/tests/integration/data/verify-rust-std/0029-boxed/box-from-raw-in.rs --start-symbol verify_box_from_raw_in --proof-dir /tmp/boxed-from-raw-in-proof --verbose --terminate-on-thunk`
- Compile-check `Box<T>::from_non_null` harness:
  `/home/zhaoji/.stable-mir-json/release.sh -Zno-codegen /home/zhaoji/projs/mir-semantics-vrs/challenges/0029-boxed/kmir/src/tests/integration/data/verify-rust-std/0029-boxed/box-from-non-null.rs`
- Compile-check `Box<T, A>::from_non_null_in` harness:
  `/home/zhaoji/.stable-mir-json/release.sh -Zno-codegen /home/zhaoji/projs/mir-semantics-vrs/challenges/0029-boxed/kmir/src/tests/integration/data/verify-rust-std/0029-boxed/box-from-non-null-in.rs`
- Compile-check scalar `assume_init` harness:
  `/home/zhaoji/.stable-mir-json/release.sh -Zno-codegen /home/zhaoji/projs/mir-semantics-vrs/challenges/0029-boxed/kmir/src/tests/integration/data/verify-rust-std/0029-boxed/box-assume-init.rs`
- Compile-check slice `assume_init` harness:
  `/home/zhaoji/.stable-mir-json/release.sh -Zno-codegen /home/zhaoji/projs/mir-semantics-vrs/challenges/0029-boxed/kmir/src/tests/integration/data/verify-rust-std/0029-boxed/box-slice-assume-init.rs`

CI status:

- No challenge-dedicated CI shard exists yet on this branch.
- Current replay is manual and command-based; PR `#1054` now records the exact
  harness and validation commands.

Challenge-local artifact contract:

- Place harnesses, tests, expected output, and supporting files in this
  directory.
- Keep changes organized so proof or semantic commits can be cherry-picked
  cleanly later.
- Record any exceptional dependency change in the generator and evaluator logs
  before landing it.

Status board:

- Planner: tranche 1 defined
- Generator: first harness sweep in progress
- Evaluator: not started on this slice
- Draft PR: exists and should reflect the current success-table snapshot
