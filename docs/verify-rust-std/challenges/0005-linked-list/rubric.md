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

## Challenge 0005 Criteria

The evaluator should apply the baseline criteria above and also check the
challenge-specific criteria below.

| Criterion | Critical | Evidence expectation |
| --- | --- | --- |
| All seven published functions are individually accounted for | yes | `clear`, `contains`, `split_off`, `remove`, `retain`, `retain_mut`, and `extract_if` each map to a proof artifact, a test harness, or a named blocker in this challenge directory. |
| The proof is unbounded over arbitrary linked-list shape | yes | Evidence shows the result is not limited to a fixed depth or canonical topology; the reasoning must cover arbitrary-length bidirectional chains and the relevant inductive structure. |
| Linked-list invariants are modeled explicitly | yes | Contracts or harness assumptions capture the list head/tail relationship, predecessor/successor consistency, initialized node fields, and any allocator or alignment preconditions needed by the proof. |
| Challenge UB obligations are discharged or explicitly blocked | yes | Evidence addresses dangling or misaligned access, uninitialized reads, mutation of immutable bytes, and invalid values, with any missing obligation logged as a blocker. |
| Evidence is reproducible from the recorded command line | yes | Commands, tool versions, target files, and expected outputs are stored under `kmir/src/tests/integration/data/verify-rust-std/0005-linked-list` or referenced from this branch-local documentation. |
| Upstream `linked_list.rs` drift is controlled | yes | If a proof copy, stripped file, or generated diff is used, the docs must explain how it is compared against the upstream snapshot and how CI fails on drift. |
| Prior review concerns are explicitly handled | yes | The docs record whether shared doubly-linked-list theory is isolated from per-function proofs, whether any `assume` is used, and whether unwind-path limitations are fully verified or clearly scoped out. |
| Challenge-specific blockers are explicit | no | Solver limits, unsupported semantics features, unstable dependencies, or omitted proof obligations are named with the next action required, together with the exact function or artifact they affect. |

## Required Evidence

For a submission to be scoreable, the evaluator should be able to point at:

- the challenge-local artifact directory and any proof or harness files stored
  there
- the upstream challenge page and the resolved issue/PR trail that defines the
  challenge contract
- the exact rerun command used to produce the proof or test output
- a file-level explanation of how each of the seven functions is covered
- any explicit blocker for a function or obligation that is still not proven

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
