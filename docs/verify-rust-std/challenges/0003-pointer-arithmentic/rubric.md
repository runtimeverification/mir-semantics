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

## Required Evaluator Updates

Each evaluator must append challenge-specific criteria for:

- the exact published success criteria from the challenge page
- challenge-specific UB obligations
- challenge-specific artifact expectations
- review patterns learned from prior solution PRs and comments

## Challenge-Specific Criteria

| Criterion | Critical | Initial expectation |
| --- | --- | --- |
| Published raw-pointer API coverage is complete | yes | Every function named in the challenge page is mapped to a contract, proof, test, or explicit blocker, with `*const T` and `*mut T` tracked separately. |
| Pointer-arithmetic contracts are faithful for both API families | yes | `add`, `sub`, `offset`, `offset_from`, `byte_add`, `byte_sub`, `byte_offset`, and `byte_offset_from` each carry safety conditions that match the standard-library docs, including same-allocation and one-past-the-end constraints. |
| Pointee coverage matches the published assumptions | yes | The evaluator can point to evidence for all integer types, at least one `dyn Trait`, at least one slice, `()`, and at least one composite type with multiple non-ZST fields. |
| At least three downstream users are proven safe | yes | The branch names exactly which three of `[u8]::is_ascii`, `String::remove`, `Vec::swap_remove`, `Option::as_slice`, and `VecDeque::swap` are covered and cites direct proof or test artifacts. |
| Challenge UB obligations are discharged | yes | The evidence explicitly rules out dangling or misaligned access, invalid in-bounds projections, intrinsic UB, and invalid values, or names each category as a blocker. |
| Evidence is rerunnable and challenge-local | yes | Commands, proof/test identifiers, and artifact paths under the challenge directory are specific enough that another reviewer can rerun the exact checks. |
| Review feedback patterns are incorporated | no | Prior raw-pointer or collection-proof concerns are reflected in naming, blocker handling, and explanation structure rather than only in the final summary. |
| Residual risk is explicit | no | Any unsupported path, missing proof obligation, solver limitation, or dependency escalation is called out directly instead of being left implicit. |

## Evidence Expectations

- The evaluator should be able to cite artifacts under
  `kmir/src/tests/integration/data/verify-rust-std/0003-pointer-arithmentic`.
- The evaluator should record the exact files that witness pointer contracts,
  harnesses, expected output, and explicit blocker notes.
- The evaluator should record the exact rerun command or commands used to
  validate the evidence, including any challenge-specific proof selection.
- The evaluator should distinguish `*const T` from `*mut T` evidence even if the
  same lemma or harness family is reused for both.
- If a proof narrows inputs, the narrowing must be justified by the published
  challenge assumptions or standard-library `SAFETY` text, not by convenience.
- If any named API, pointee class, or downstream user is intentionally not
  covered, the exclusion must be recorded as a blocker or explicit out-of-scope
  note.

Each evaluator iteration should end with:

- current score per criterion
- cited evidence paths and commands
- fail-closed gaps
- a clear verdict: `not started`, `in progress`, `blocked`, or `submission-ready`
