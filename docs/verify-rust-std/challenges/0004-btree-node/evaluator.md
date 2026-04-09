# Evaluator Record: Challenge 0004

Ownership:

- Evaluator owns this file and `rubric.md`.
- Evaluator must not implement code, proofs, or harnesses.
- Evaluator must fail closed on missing evidence.

## Inputs

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0004-btree-node.md
- Tracking issue: [#77](https://github.com/model-checking/verify-rust-std/issues/77)
- Planner record: `docs/verify-rust-std/challenges/0004-btree-node/planner.md`
- Generator record: `docs/verify-rust-std/challenges/0004-btree-node/generator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0004-btree-node/rubric.md`

## Baseline Tasks

- Extend the rubric with challenge-specific criteria.
- Incorporate patterns from resolved challenges, existing solution PRs, and
  review comments.
- Record concrete evidence paths and rerun commands.

## Scorecard

| Criterion | Score | Evidence | Gap |
| --- | --- | --- | --- |
| Every published bounded API is covered by a direct proof artifact | 0 | none yet | No proof inventory or harness mapping has been recorded. |
| Every published unbounded API is handled with an unbounded strategy | 0 | none yet | No unbounded proof strategy has been documented. |
| Safety contracts are sourced from the library docs and SAFETY comments | 0 | none yet | No contracts or assumptions have been reviewed against the source comments. |
| The challenge UB list is explicitly discharged or blocked | 0 | none yet | No evidence yet for dangling, alignment, initialization, mutability, or invalid-value coverage. |
| Harness naming and claim text match the exercised API | 0 | none yet | No harness names, helper names, or proof labels exist to audit yet. |
| Evidence is replayable from the artifact directory | 0 | none yet | No rerun commands, proof outputs, or artifact paths have been captured. |

## Review Pattern Notes

- Prior review comments on the earlier BTreeMap node PR favored exact API
  mapping over broad labels; a proof named for `LeafNode::new` should not call
  a different constructor unless the relationship is explained.
- Reviewers also flagged unnecessary `unsafe` in harnesses and doc comments
  that described a different value sequence than the code actually built.
- For this challenge, a finite example is not enough for the recursive or
  looping functions called out as unbounded on the challenge page.
- Any missing proof should be marked with a concrete blocker rather than being
  implied by a generic summary row.

## Verdict

- Current status: `not started`
- Current risk level: `high` because there is no recorded proof evidence yet.
- Submission posture: `fail closed` until the scorecard has direct artifacts.

## Iteration Log

- Bootstrap record created by orchestrator.
