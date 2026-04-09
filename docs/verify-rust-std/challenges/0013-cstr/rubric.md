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

## Challenge 0013 Additions

| Criterion | Critical | Initial expectation |
| --- | --- | --- |
| `CStr` invariant harness is present | yes | The branch contains challenge-local harnesses that re-check the invariant after the nine listed safe APIs. |
| Unsafe entry points are contracted and verified | yes | `from_ptr`, `from_bytes_with_nul_unchecked`, and `strlen` have explicit contracts or proof-backed harnesses. |
| `CloneToUninit` is byte-exact | yes | Evidence compares the exact written region against the source `CStr` bytes and validates destination preconditions beyond nullness. |
| `Index<RangeFrom<usize>>` preserves tail bytes | yes | Evidence shows the indexed result preserves the `CStr` invariant and matches the expected source tail. |
| Prerequisite linker/body-resolution work does not count as completion | yes | Fixture or linker ports can unblock execution, but they do not satisfy Challenge 13 without the actual `CStr` artifacts. |
| Completed proof evidence exists for at least one challenge-local slice | yes | A proof or validation command reaches a concrete non-bootstrap outcome on the challenge branch. |

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

## Challenge 0013 Notes

- Prior review comments indicate that `CloneToUninit` must be checked against the exact writable region, not just against null or a broad helper buffer.
- A branch-local prerequisite for cross-crate body resolution is useful evidence, but it is not a substitute for the published `CStr` harnesses/contracts.
- For this challenge, the evaluator should fail closed if the branch lacks the `CStr` artifacts even when prerequisite linker infrastructure has landed.
