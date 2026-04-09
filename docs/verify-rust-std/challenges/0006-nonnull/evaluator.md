# Evaluator Record: Challenge 0006

Ownership:

- Evaluator owns this file and `rubric.md`.
- Evaluator must not implement code, proofs, or harnesses.
- Evaluator must fail closed on missing evidence.

## Inputs

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0006-nonnull.md
- Tracking issue: [#53](https://github.com/model-checking/verify-rust-std/issues/53)
- Planner record: `docs/verify-rust-std/challenges/0006-nonnull/planner.md`
- Generator record: `docs/verify-rust-std/challenges/0006-nonnull/generator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0006-nonnull/rubric.md`

## Baseline Tasks

- Extend the rubric with challenge-specific criteria.
- Incorporate patterns from resolved challenges, existing solution PRs, and
  review comments.
- Record concrete evidence paths and rerun commands.

## Scorecard

| Criterion | Score | Evidence | Gap |
| --- | --- | --- | --- |
| Published success criteria are mapped to concrete artifacts | 0 | pending | No function-to-artifact map recorded yet. |
| Challenge-book rules are satisfied | 0 | pending | No reviewer-facing evidence of automation, approved tooling, or scope compliance yet. |
| Safety conditions are modeled faithfully | 0 | pending | No contracts or harnesses recorded yet for source SAFETY obligations. |
| Undefined behavior obligations are covered | 0 | pending | The challenge UB list has not been discharged or blocked in the record. |
| Evidence is reproducible | 0 | pending | No rerun commands or expected outputs have been logged yet. |
| Scope is challenge-local and cherry-pickable | 0 | pending | No implementation commits exist yet to assess scope hygiene. |
| Review feedback patterns are incorporated | 0 | pending | No prior solution review patterns have been captured yet. |
| Residual risk is explicit | 0 | pending | No blockers or dependency notes have been recorded yet. |
| All 48 public `NonNull` APIs are accounted for | 0 | pending | No challenge-specific coverage matrix is available yet. |
| Construction and reference helpers carry faithful safety preconditions | 0 | pending | No evidence yet for `new_unchecked`, `new`, or reference-conversion contracts. |
| Raw-pointer arithmetic and provenance helpers are justified | 0 | pending | No evidence yet for offset, address, or cast semantics. |
| Memory-access helpers cover initialization, aliasing, overlap, and immutability | 0 | pending | No evidence yet for copy, read, write, swap, replace, or drop obligations. |
| Slice, DST, and metadata-bearing helpers are sound | 0 | pending | No evidence yet for slice metadata or length/index validity. |
| Challenge-local artifacts are reproducible and reviewable | 0 | pending | No artifact index or stable rerun recipe has been recorded yet. |
| Residual risk and dependency gaps are explicit | 0 | pending | No blocker log exists yet for unsupported semantics or cross-repo needs. |

## Review Pattern Notes

- No branch-local review comments were available at bootstrap.
- Expect reviewers to ask for a per-function coverage map, not just a grouped
  claim that `NonNull` was handled.
- Expect reviewers to reject proofs that pass only by overconstraining caller
  inputs unless the recorded contracts still reflect the source SAFETY
  obligations.
- Expect reviewers to scrutinize raw-pointer, slice, and `MaybeUninit`
  dependencies for explicit blocker handling if the current semantics cannot
  prove them.
- Expect reviewers to treat indirect downstream uses of `NonNull` as supporting
  evidence only, not as a substitute for direct module coverage.

## Verdict

- Current status: `not started`

## Iteration Log

- Bootstrap record created by orchestrator.
