# Evaluator Rubric

This is the portfolio baseline rubric. Each challenge branch starts from this
file, then the evaluator extends it with challenge-specific criteria and lessons
from prior reviews.

Scoring guidance:

- `0`: missing or contradicted
- `1`: partial or weakly evidenced
- `2`: acceptable but still has explicit follow-up risk
- `3`: submission-ready with direct evidence

Critical criteria must score `3` before the evaluator can mark a challenge
submission-ready.

## Baseline Criteria

| Criterion | Critical | Initial expectation |
| --- | --- | --- |
| Published success criteria are mapped to concrete artifacts | yes | Every required function, module, or property is traced to harnesses, proofs, tests, or explicit blockers. |
| Challenge-book rules are satisfied | yes | The work is automated, reviewable in a PR, uses approved tooling, and does not change standard-library runtime logic unless externally justified. |
| Safety conditions are modeled faithfully | yes | SAFETY comments and standard-library docs are reflected in contracts, assumptions, and harness inputs without over-constraining away real risk. |
| Undefined behavior obligations are covered | yes | The challenge-specific UB list plus any additional published safety obligations are checked or explicitly blocked with evidence. |
| Evidence is reproducible | yes | Commands, target files, expected output, and proof/test results are recorded so another agent or reviewer can rerun them. |
| Scope is challenge-local and cherry-pickable | yes | Commits are intentional, unrelated churn is avoided, and any exceptional cross-repo change is justified. |
| Review feedback patterns are incorporated | no | Prior review comments on similar work are reflected in naming, test organization, and explanation quality. |
| Residual risk is explicit | no | Open blockers, solver limitations, unsupported hooks, or dependency escalations are called out precisely. |

## Challenge-Specific Criteria: Challenge 0011

| Criterion | Critical | Initial expectation |
| --- | --- | --- |
| Integer methods have branch-local proof evidence | yes | At least one scoped integer proof completes on this branch, not just collection or harness wiring. |
| Non-float APIs are mapped to concrete artifacts | yes | `unchecked_add`, `unchecked_sub`, `unchecked_mul`, `unchecked_shl`, `unchecked_shr`, `unchecked_neg`, `wrapping_shl`, `wrapping_shr`, `widening_mul`, and `carrying_mul` each have direct harness or expected-output artifacts. |
| Float path is classified with direct evidence | yes | `to_int_unchecked` is either proven or blocked by branch-local evidence that names the missing float capability/hook. |
| Validation is replayable | yes | Commands distinguish discovery, collection, and execution so another evaluator can reproduce the same reading of the branch. |

## Reusable Evaluator Patterns

- A `pytest --collect-only` result is evidence of discovery only; it is not proof completion.
- A challenge may still be `IN PROGRESS` even when one subpath is structurally blocked, if another subpath still has a concrete next proof action.
- A float blocker should be recorded against the exact missing backend capability or intrinsic hook, not as a vague "floats unsupported" note.

## Required Evaluator Updates

Each evaluator must append challenge-specific criteria for:

- the exact published success criteria from the challenge page
- challenge-specific UB obligations
- challenge-specific artifact expectations
- review patterns learned from prior solution PRs and comments

Each evaluator iteration should end with:

- current score per criterion
- cited evidence paths and commands
- fail-closed gaps
- a clear verdict: `not started`, `in progress`, `blocked`, or `submission-ready`
