# Challenge 0026: Verify reference-counted Cell implementation

Reference inputs:

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0026-rc.md
- Tracking issue: [#382](https://github.com/model-checking/verify-rust-std/issues/382)
- Tracking issue state at bootstrap: `OPEN`

Execution context:

- Branch: `verify-rust-std/reexec-0026-rc`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0026-rc`
- Success table: `docs/verify-rust-std/challenges/0026-rc/success-criteria.md`
- Planner record: `docs/verify-rust-std/challenges/0026-rc/planner.md`
- Generator record: `docs/verify-rust-std/challenges/0026-rc/generator.md`
- Evaluator record: `docs/verify-rust-std/challenges/0026-rc/evaluator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0026-rc/rubric.md`

Current verification tranche:

- Root proofs selected by the contract map: `Rc::from_raw_in`, `Rc::increment_strong_count_in`, `Rc::decrement_strong_count_in`, and `Weak::from_raw_in`.
- Immediate wrapper follow-ons: `Rc::from_raw`, `Rc::increment_strong_count`, `Rc::decrement_strong_count`, and `Weak::from_raw`.
- The remaining public `unsafe` APIs stay out of tranche 1 and are tracked as separate initialization, aliasing, or dynamic-type work.

Current frontier:

- Challenge-local minimal reproducer: `rc-from-raw-in-frontier-fail.rs`
- Root repro mirror: `../../prove-rs/rc-from-raw-in.rs`
- Frontier summary: the direct `Rc::from_raw_in` witness still terminates at the current `CastKind::Transmute` leaf.

How to run:

- Exact proof command:
  `uv --project kmir run kmir prove /home/zhaoji/projs/mir-semantics-vrs/challenges/0026-rc/kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-from-raw-in-frontier-fail.rs --proof-dir /tmp/rc-from-raw-in-frontier-proof --verbose --terminate-on-thunk`
- Narrow collector:
  `make test-verify-rust-std`
- Direct pytest form:
  `uv --project kmir run pytest kmir/src/tests/integration/test_integration.py -k test_verify_rust_std -v`

How this maps to the success table:

- `Rc::from_raw_in` is the only row with a live branch frontier.
- The four wrapper rows are pending the allocator-general root proof.
- The remaining public `unsafe` APIs are still unstarted and remain tracked in the success table and contract map.

Challenge-local artifact contract:

- Place harnesses, tests, expected output, and supporting files in this directory.
- Keep changes organized so proof or semantic commits can be cherry-picked cleanly later.
- Record any exceptional dependency change in the generator and evaluator logs before landing it.

Status board:

- Branch: active on `verify-rust-std/reexec-0026-rc`
- Frontier: challenge-local minimal reproducer exists at `rc-from-raw-in-frontier-fail.rs`
- Evaluator: active / in progress
- Draft PR: exists
