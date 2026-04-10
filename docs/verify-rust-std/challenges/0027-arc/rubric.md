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
| Success-criteria coverage is auditable in the branch and PR | yes | The branch keeps a `Function | Location | Status | Specification | Notes`-style table, and the draft PR mirrors the same live coverage state. |
| Challenge-book rules are satisfied | yes | The work is automated, reviewable in a PR, uses approved tooling, and does not change standard-library runtime logic unless externally justified. |
| Safety conditions are modeled faithfully | yes | SAFETY comments and standard-library docs are reflected in contracts, assumptions, and harness inputs without over-constraining away real risk. |
| Undefined behavior obligations are covered | yes | The challenge-specific UB list plus any additional published safety obligations are checked or explicitly blocked with evidence. |
| Verification harnesses are distinguished from reproducers | yes | Symbolic or contract-shaped proof entrypoints are kept separate from concrete frontier reproducers or fail harnesses, and only the former count as verification evidence. |
| Semantic blockers are minimized before repair | yes | When a frontier is encountered, the branch first records the smallest useful reproducer before attempting a wider semantic repair. |
| Evidence is reproducible | yes | Commands, target files, expected output, and proof/test results are recorded so another agent or reviewer can rerun them. |
| Scope is challenge-local and cherry-pickable | yes | Commits are intentional, unrelated churn is avoided, and any exceptional cross-repo change is justified. |
| Review feedback patterns are incorporated | no | Prior review comments on similar work are reflected in naming, test organization, and explanation quality. |
| Residual risk is explicit | no | Open blockers, solver limitations, unsupported hooks, or dependency escalations are called out precisely. |

## Required Evaluator Updates

Each evaluator must append challenge-specific criteria for:

- the exact published success criteria from the challenge page
- the current success-criteria coverage table in the branch-local docs and PR
- challenge-specific UB obligations
- challenge-specific artifact expectations
- review patterns learned from prior solution PRs and comments

## Challenge 0027 Addendum

Use the following challenge-specific criteria alongside the baseline rubric.

| Criterion | Critical | 3 means |
| --- | --- | --- |
| Public unsafe API surface is fully mapped | yes | All 12 listed public `unsafe` `Arc`/`Weak` functions are traced to source safety notes and a proof root, wrapper follow-on, or explicit blocker. |
| Internal unsafe tranche is quantified | yes | At least 75% of the non-public unsafe functions are either proven safe or given a contract with a precise blocker note. |
| Primitive `T` and standard allocators are respected | yes | Proofs are limited to primitive `T` inputs and `Global`/`System` allocator instances, matching the published challenge scope. |
| Arc/Weak data-race obligations are explicit | yes | The evaluator names the atomic/data-race obligation and tracks whether it is discharged or deferred with evidence. |
| Reproducer-vs-proof split is maintained | yes | Any concrete frontier file is labeled as a reproducer or fail harness, and the verification harness remains symbolic or contract-shaped. |
| Evidence remains challenge-local | yes | Paths, commands, and commits stay inside the challenge branch unless a justified secondary repository is explicitly logged. |

## Review Pattern Notes

- 0026 showed that a per-public-API coverage table makes review progress legible.
- 0026 also showed that a concrete witness file should be kept separate from a symbolic proof harness.
- 0026 established the value of a precise blocker note with one concrete next action before widening scope.

Each evaluator iteration should end with:

- current score per criterion
- cited evidence paths and commands
- fail-closed gaps
- a clear verdict: `not started`, `in progress`, `blocked`, or `submission-ready`
