# Challenge 0014: Safety of Primitive Conversions

Reference inputs:

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0014-convert-num.md
- Tracking issue: [#220](https://github.com/model-checking/verify-rust-std/issues/220)
- Tracking issue state at bootstrap: `CLOSED`

Execution context:

- Branch: `verify-rust-std/reexec-0014-convert-num`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0014-convert-num`
- Coverage table: [success-criteria.md](../../../../../../../docs/verify-rust-std/challenges/0014-convert-num/success-criteria.md)
- Planner record: [planner.md](../../../../../../../docs/verify-rust-std/challenges/0014-convert-num/planner.md)
- Generator record: [generator.md](../../../../../../../docs/verify-rust-std/challenges/0014-convert-num/generator.md)
- Evaluator record: [evaluator.md](../../../../../../../docs/verify-rust-std/challenges/0014-convert-num/evaluator.md)
- Branch-local rubric: [rubric.md](../../../../../../../docs/verify-rust-std/challenges/0014-convert-num/rubric.md)

Challenge-local artifact contract:

- Keep proof harnesses and their replayable proof entrypoints in this
  directory.
- Keep minimal reproducers separate from proof harnesses; when a concrete
  frontier appears, prefer a dedicated `*-fail.rs` or other reproducer rather
  than widening the proof harness itself.
- Keep changes organized so proof or semantic commits can be cherry-picked
  cleanly later.
- Record any exceptional dependency change in the generator and evaluator logs
  before landing it.

Verification harnesses:

- `nonzero_from.rs` covers the first widening `NonZero` conversions with
  independent proof entrypoints such as `verify_nonzero_from_u8_to_u16` and
  `verify_nonzero_from_i8_to_i16`.
- `nonzero_try_from.rs` covers the first fallible `NonZero` conversions with
  independent proof entrypoints such as `verify_nonzero_try_from_u16_to_u8`
  and `verify_nonzero_try_from_i8_to_u8`.
- `to_int_unchecked.rs` covers the float-to-int family with independent proof
  entrypoints for `f16`, `f32`, `f64`, and `f128`.

Minimal reproducers:

- None yet on this branch. The current sweep is intentionally harness-first so
  the first artifact layer stays verification-shaped instead of test-shaped.

Replay commands:

```bash
uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0014-convert-num/nonzero_from.rs --start-symbol verify_nonzero_from_u8_to_u16 --proof-dir /tmp/kmir-0014-nonzero-from --reload --fail-fast
uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0014-convert-num/nonzero_try_from.rs --start-symbol verify_nonzero_try_from_u16_to_u8 --proof-dir /tmp/kmir-0014-nonzero-try-from --reload --fail-fast
uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0014-convert-num/to_int_unchecked.rs --start-symbol verify_to_int_unchecked_f32_i32 --proof-dir /tmp/kmir-0014-to-int-unchecked --reload --fail-fast
```

CI / broad replay:

- `make test-integration`
- `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py -q`

Status board:

- Planner: active
- Generator: active
- Evaluator: active
- Draft PR: open
