# Evaluator Record: Challenge 0012

Ownership:

- Evaluator owns this file and `rubric.md`.
- Evaluator must not implement code, proofs, or harnesses.
- Evaluator must fail closed on missing evidence.

## Inputs

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0012-nonzero.md
- Tracking issue: [#71](https://github.com/model-checking/verify-rust-std/issues/71)
- Planner record: `docs/verify-rust-std/challenges/0012-nonzero/planner.md`
- Generator record: `docs/verify-rust-std/challenges/0012-nonzero/generator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0012-nonzero/rubric.md`

## Baseline Tasks

- Extend the rubric with challenge-specific criteria.
- Incorporate patterns from resolved challenges, existing solution PRs, and
  review comments.
- Record concrete evidence paths and rerun commands.

## Scorecard

| Criterion | Score | Evidence | Gap |
| --- | --- | --- | --- |
| Published NonZero requirements are mapped to concrete artifacts | 2 | Challenge page parsed into planner/workpad; branch-local `NonZero` artifacts now exist for `new`, `new_unchecked`, `from_mut`, and `count_ones` | full Part 2 matrix and remaining published APIs still missing |
| Challenge-book rules are satisfied | 3 | Work remains in `runtimeverification/mir-semantics`, scoped to the challenge branch, and is tracked by committed docs and cherry-pickable commits | none for current evidence set |
| Safety conditions are modeled faithfully | 2 | Challenge assumptions and review notes recorded in planner/workpad; Part 1 artifacts now encode explicit `NonZero` semantics and fail on concrete frontiers | no completed NonZero proofs yet |
| Undefined behavior obligations are covered | 2 | baseline `prove-rs` regressions validate the current branch can execute the affected stack; `NonZero` artifacts now reproduce proof frontiers for `new` / `new_unchecked` / `count_ones` | published NonZero UB obligations still need passing proofs |
| Evidence is reproducible | 3 | `collect-only`, `make build`, compile checks, and direct `kmir prove-rs` evidence are recorded in `generator.md` | broader `NonZero` proof matrix still unrun |
| Scope is challenge-local and cherry-pickable | 3 | prerequisite slice landed in coherent commits without portfolio churn | none |
| Review feedback patterns are incorporated | 3 | rubric tracks the "semantic baseline is not completion" pattern, the thin-harness warning from public reviews, and the new distinction between artifact existence and failing proof frontiers | none |
| Residual risk is explicit | 3 | missing layer is called out as challenge-specific `NonZero` work, not unresolved baseline semantics | none |

## Challenge-Specific Criteria

| Criterion | Score | Evidence | Gap |
| --- | --- | --- | --- |
| Part 1 `new` / `new_unchecked` correctness is implemented and verified | 1 | `new.rs` and `new_unchecked.rs` exist; `kmir prove-rs` reproduces concrete `FAILED` frontiers at `NonZero::new` transmute paths | no passing proof yet |
| Part 2 `NonZero` APIs are covered with semantic assertions, not just UB-free harnesses | 1 | `count_ones.rs` seeds the Part 2 matrix with explicit `.get()` assertions; broader Part 2 matrix still absent | no full semantic matrix yet |
| Wide-type / bounded-case decisions are explicit for `isqrt` and `128-bit` pow-family cases | 0 | none | no challenge-specific coverage map yet |
| Reproducible proof/test evidence exists for the actual NonZero suite | 1 | `release.sh` compile checks and direct `kmir prove-rs` failures are recorded for the new challenge-local artifacts | no scoped proof pass for the full suite yet |

## Review Pattern Notes

- Public review feedback on Challenge 12 now has two reusable patterns:
  - "Semantic baseline" ports are valuable but do not satisfy challenge completion by themselves.
  - Any harness that only proves nonzero-ness or UB-freedom is insufficient if the published function has an expected semantic relation.
- New pattern from this re-execution branch:
  - If challenge-local `NonZero` artifacts exist but the first proof frontier fails reproducibly, keep the challenge `IN PROGRESS` and treat the frontier as actionable evidence rather than missing setup.

## Verdict

- Current status: `in progress`

## Iteration Log

- Bootstrap record created by orchestrator.
- 2026-04-09 UTC: prerequisite semantic baseline validated on the re-execution branch, but the actual NonZero harness/contract layer is still missing.
- 2026-04-09 UTC: branch-local `NonZero` artifacts landed and reproducible proof frontiers were recorded; readiness remains `in progress` because no NonZero proof has passed end-to-end yet.
