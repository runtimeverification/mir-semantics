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
| Published NonZero requirements are mapped to concrete artifacts | 1 | Challenge page parsed into planner/workpad; prerequisite semantic baseline validated in `generator.md` | no branch-local NonZero harnesses/contracts yet |
| Challenge-book rules are satisfied | 3 | Work remains in `runtimeverification/mir-semantics`, scoped to the challenge branch, and is tracked by committed docs and cherry-pickable commits | none for current evidence set |
| Safety conditions are modeled faithfully | 1 | Challenge assumptions and review notes recorded in planner/workpad; prerequisite baseline confirms environment readiness | no NonZero-specific contracts yet |
| Undefined behavior obligations are covered | 1 | baseline `prove-rs` regressions validate the current branch can execute the affected stack | published NonZero UB obligations still need branch-local proofs |
| Evidence is reproducible | 2 | `collect-only`, `make build`, and targeted `pytest` evidence recorded in `generator.md` | challenge-specific `NonZero` commands/results absent |
| Scope is challenge-local and cherry-pickable | 3 | prerequisite slice landed in coherent commits without portfolio churn | none |
| Review feedback patterns are incorporated | 2 | rubric now tracks the "semantic baseline is not completion" pattern and the thin-harness warning from public reviews | no challenge-specific harness strengthening yet |
| Residual risk is explicit | 3 | missing layer is called out as challenge-specific `NonZero` work, not unresolved baseline semantics | none |

## Challenge-Specific Criteria

| Criterion | Score | Evidence | Gap |
| --- | --- | --- | --- |
| Part 1 `new` / `new_unchecked` correctness is implemented and verified | 0 | none | no `core::num::nonzero` artifacts on this branch yet |
| Part 2 `NonZero` APIs are covered with semantic assertions, not just UB-free harnesses | 0 | none | no challenge-specific harness matrix yet |
| Wide-type / bounded-case decisions are explicit for `isqrt` and `128-bit` pow-family cases | 0 | none | no challenge-specific coverage map yet |
| Reproducible proof/test evidence exists for the actual NonZero suite | 0 | none | no scoped `nonzero` proof/test run yet |

## Review Pattern Notes

- Public review feedback on Challenge 12 now has two reusable patterns:
  - "Semantic baseline" ports are valuable but do not satisfy challenge completion by themselves.
  - Any harness that only proves nonzero-ness or UB-freedom is insufficient if the published function has an expected semantic relation.

## Verdict

- Current status: `in progress`

## Iteration Log

- Bootstrap record created by orchestrator.
- 2026-04-09 UTC: prerequisite semantic baseline validated on the re-execution branch, but the actual NonZero harness/contract layer is still missing.
