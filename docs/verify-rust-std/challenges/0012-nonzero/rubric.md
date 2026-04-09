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

## Challenge 12 Reusable Patterns

- A prerequisite semantic-baseline port is supporting evidence only. It may
  justify the environment and reduce later risk, but it does not satisfy the
  Challenge 12 success criteria by itself.
- If branch-local `NonZero` artifacts exist but the first proofs fail on a
  concrete transmute or count-assert frontier, score that as partial readiness
  rather than missing evidence.
- If frontier reduction narrows `NonZero::new` to `castKindTransmute` or
  `NonZero::from_mut` to `castKindPtrToPtr`, treat that as actionable semantic
  evidence and keep the challenge `IN PROGRESS` until one frontier closes or is
  explicitly blocked.
- If a NonZero harness only proves "nonzero-ness" or absence of UB, that is not
  enough unless the published API has no stronger semantic relation to assert.
- For `isqrt`, any omission of wider unsigned types must be explicitly bounded
  or justified with a documented performance rationale.
- For `checked_pow` / `saturating_pow` on 128-bit types, bounded exponents are
  acceptable only when the bound and its verification rationale are explicit.
- Evaluator scoring should separate:
  - prerequisite semantic baseline readiness
  - challenge-specific `core::num::nonzero` artifact readiness
  - reproducible proof/test evidence for the published API list

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
