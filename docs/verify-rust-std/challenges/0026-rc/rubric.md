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

## Challenge 0026 Addendum

Use the following challenge-specific criteria alongside the baseline rubric.

| Criterion | Critical | 3 means |
| --- | --- | --- |
| Public unsafe API surface is fully mapped | yes | All 12 listed public `unsafe` functions are traced to a source safety summary and either a proof root, wrapper follow-on, or explicit blocker note. |
| Raw-pointer/refcount tranche is isolated | yes | The chosen first tranche preserves the `from_raw_in` -> increment/decrement -> weak raw recovery dependency spine and is the smallest leverage-preserving slice. |
| Challenge-specific UB obligations are explicit | yes | The evaluator names the relevant UB families and notes whether they are discharged or deferred. |
| External dependency risk is named precisely | no | Any upstream tool/backend dependency is identified with the specific affected API(s) and treated as a soft risk until tested. |
| Evidence remains challenge-local | yes | File paths, commands, and commit SHAs are recorded in the branch-local docs. |

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
