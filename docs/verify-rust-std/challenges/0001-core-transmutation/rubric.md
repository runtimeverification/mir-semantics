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
| Spec-book guidance for transmutation exists and is referenced | yes | A new or updated spec-book entry explains the transmutation patterns, caller obligations, and how safe wrappers justify local reasoning. |
| Coverage threshold is evidenced for the published target set | yes | The evaluator can point to a coverage table showing at least 35 of the 47 listed intrinsics/functions have contracts, and non-intrinsics have verified bodies. |
| In-scope transmutation APIs have faithful contracts | yes | Each in-scope API encodes the relevant bit-validity, size/layout, and follow-on validity obligations, or is explicitly blocked with a documented reason. |
| Safe wrappers are wrapped with local assumptions and assertions | yes | Safe call sites around transmutation-related unsafe operations carry the preconditions/postconditions needed for the proof, without hiding real obligations. |
| Excluded categories stay explicitly excluded | yes | utf8-validation, ptr provenance APIs, core::num, ptr metadata/vtable, async, specialization, iterator get_unchecked, and formatting paths are either untouched or only used as documented supporting evidence. |
| Evidence bundles are reproducible | yes | Commands, target files, expected output, and proof/test results are recorded in the challenge artifact directory with enough detail for reruns. |
| Review feedback patterns are incorporated | no | Prior review comments about distinct artifact naming and explicit blocker disclosure are reflected in the branch output and evaluator notes. |
| Residual risk is explicit | no | Any unsupported hook, solver limitation, upstream dependency, or excluded method family is named directly instead of being left implicit. |

## Evidence Expectations

- The evaluator should be able to cite the challenge artifact directory:
  `kmir/src/tests/integration/data/verify-rust-std/0001-core-transmutation`.
- The evaluator should record the exact files that witness spec-book updates,
  harnesses, expected output, and any blocker notes.
- The evaluator should record the exact rerun command or commands used to
  validate the evidence, including any challenge-specific test selection.
- If the solution uses `Transmutability`, any new impls must be tracked as an
  upstream dependency rather than treated as locally complete evidence.
- If a method family is intentionally out of scope, the evaluator must record
  the reason and the artifact that names the exclusion.

Each evaluator iteration should end with:

- current score per criterion
- cited evidence paths and commands
- fail-closed gaps
- a clear verdict: `not started`, `in progress`, `blocked`, or `submission-ready`
