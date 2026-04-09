# Evaluator Record: Challenge 0011

Ownership:

- Evaluator owns this file and `rubric.md`.
- Evaluator must not implement code, proofs, or harnesses.
- Evaluator must fail closed on missing evidence.

## Inputs

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0011-floats-ints.md
- Tracking issue: [#59](https://github.com/model-checking/verify-rust-std/issues/59)
- Planner record: `docs/verify-rust-std/challenges/0011-floats-ints/planner.md`
- Generator record: `docs/verify-rust-std/challenges/0011-floats-ints/generator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0011-floats-ints/rubric.md`

## Baseline Tasks

- Extend the rubric with challenge-specific criteria.
- Incorporate patterns from resolved challenges, existing solution PRs, and
  review comments.
- Record concrete evidence paths and rerun commands.

## Scorecard

| Criterion | Score | Evidence | Gap |
| --- | --- | --- | --- |
| Integer methods have branch-local proof evidence | 1 | `generator.md` records artifact porting, `uv --project kmir run -- pytest ... --collect-only -k "unchecked_add and not fail"` selected `test_verify_rust_std[unchecked_add]`. | No completed passing proof result yet on the re-execution branch. |
| Non-float APIs are mapped to concrete artifacts | 3 | Ported `0011-floats-ints` harnesses and expected outputs under `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/`. | None. |
| Float path is classified with direct evidence | 3 | Ported `to_int_unchecked-fail.*.expected` files show stuck frontiers on float intrinsics such as `fabsf32` and `fabsf64`; PR #985 states the same blocker. | None. |
| Validation is replayable | 2 | Commands and outcomes are recorded in `generator.md` and `workpad.md`. | One end-to-end proof run still needs to complete successfully. |
| Residual risk is explicit | 3 | `generator.md` and `workpad.md` name the exact float-capability blocker and the remaining integer proof gap. | None. |

## Review Pattern Notes

- `pytest --collect-only` is discovery evidence only; it does not count as proof
  completion.
- A challenge can remain `IN PROGRESS` even with a structural float blocker if
  another slice still has a concrete next proof action.
- A float blocker should name the exact unsupported capability or hook, not
  just "floats unsupported."

## Verdict

- Current status: `IN PROGRESS`

## Iteration Log

- Bootstrap record created by orchestrator.
- 2026-04-09: Branch-local artifacts and runner support were ported from the
  historical Challenge 11 branch.
- 2026-04-09: Validation confirmed discovery and runtime launch for a scoped
  integer case, but no completed passing proof was recorded yet.
- 2026-04-09: Float path was reduced to a branch-local structural blocker
  (`fabsf32` / `fabsf64` stuck intrinsics in `to_int_unchecked-fail`).
