# Challenge 0028: Challenge 28: Verify float to decimal conversion module

Reference inputs:

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0028-flt2dec.md
- Tracking issue: [#524](https://github.com/model-checking/verify-rust-std/issues/524)
- Tracking issue state at bootstrap: `OPEN`

Execution context:

- Branch: `verify-rust-std/reexec-0028-flt2dec`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0028-flt2dec`
- Planner record: `docs/verify-rust-std/challenges/0028-flt2dec/planner.md`
- Generator record: `docs/verify-rust-std/challenges/0028-flt2dec/generator.md`
- Evaluator record: `docs/verify-rust-std/challenges/0028-flt2dec/evaluator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0028-flt2dec/rubric.md`
- Published success criteria: `docs/verify-rust-std/challenges/0028-flt2dec/success_criteria.md`

Challenge-local artifact contract:

- Place harnesses, tests, expected output, and supporting files in this
  directory.
- Keep changes organized so proof or semantic commits can be cherry-picked
  cleanly later.
- Record any exceptional dependency change in the generator and evaluator logs
  before landing it.

Status board:

- Planner: success criteria table published
- Generator: checkpointed at the minimal `digits_to_dec_str_probe.rs` frontier
- Evaluator: captured in `docs/verify-rust-std/challenges/0028-flt2dec/evaluation_result.md`
- Draft PR: not created

Current minimal reproducer:

- `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs`
- This file is the challenge-local verification frontier for `flt2dec`, not a
  generic test.
- The current exact frontier is the copied `if exp >= buf.len()` select in
  `digits_to_dec_str_probe.rs:76`, with the unsimplified predicate
  `#applyBinOp ( binOpGe , 2 , #applyUnOp ( unOpPtrMetadata , ... ) )`.

Replay commands:

- `uv --project kmir run kmir prove kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs --proof-dir /tmp/0028-digits-to-dec-str-prefixslice-proof --max-depth 200 --reload`
- `uv --project kmir run kmir show digits_to_dec_str_probe.main --proof-dir /tmp/0028-digits-to-dec-str-prefixslice-proof --statistics --leaves`

Audit link:

- The minimal reproducer maps to `docs/verify-rust-std/challenges/0028-flt2dec/success_criteria.md`.
