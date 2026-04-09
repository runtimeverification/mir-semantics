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

## Challenge 0004 Addenda

This challenge is narrower than the baseline rubric: the evaluator should
grade the concrete proof package against the published `btree::node` API list
and the memory-safety obligations on the challenge page.

| Criterion | Critical | Initial expectation |
| --- | --- | --- |
| Every published bounded API is covered by a direct proof artifact | yes | The submission names or otherwise maps proof artifacts to all 25 bounded functions listed in the challenge page, with no silent omissions. |
| Every published unbounded API is handled with an unbounded strategy | yes | `NodeRef::new_internal`, `Handle::insert_recursing`, and the `BalancingContext::*` routines are proven with an argument that is not limited to one finite tree shape or one loop iteration. |
| Safety contracts are sourced from the library docs and SAFETY comments | yes | Preconditions and assumptions come from the standard-library comments or module invariants, not from ad hoc strengthening that hides real obligations. |
| The challenge UB list is explicitly discharged or blocked | yes | The proof package addresses dangling or misaligned accesses, uninitialized reads, mutable-byte violations, and invalid values for the covered code paths. |
| Harness naming and claim text match the exercised API | yes | Proof names, helper names, and inline comments identify the exact API being checked; indirect coverage through a helper must be labeled so reviewers do not infer the wrong function was proven. |
| Evidence is replayable from the artifact directory | yes | The evaluator can rerun the documented command(s) from the challenge artifact directory and compare the resulting proof status or output with the recorded evidence. |
| Review comments are reflected in the proof package | no | Prior feedback about exact API mapping, unnecessary unsafe blocks, and misleading helper comments is incorporated into the submission. |
| Residual blockers are separated from completed proofs | no | Any function that remains unproved has a precise blocker, a scope note, and a proposed next step instead of being left implicit. |

## Evidence Expectations

The evaluator should look for the following evidence when scoring a submission:

- A file inventory in `kmir/src/tests/integration/data/verify-rust-std/0004-btree-node/` or an equivalent documented artifact directory.
- A one-to-one or clearly explained many-to-one mapping from challenge criteria to proof files, expected-output files, or harness modules.
- Exact rerun commands, including the working directory and any flags needed to reproduce the proof state.
- A short explanation for any intentionally unbounded proof, especially when it uses induction, recursion, or a proof-splitting strategy.
- Proof outputs that distinguish successful coverage from known blockers, rather than one generic "verified" statement for the whole challenge.
- If a proof is intentionally deferred, the blocker must name the missing semantic capability, missing harness input, or upstream dependency rather than a vague "not done yet" note.

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
