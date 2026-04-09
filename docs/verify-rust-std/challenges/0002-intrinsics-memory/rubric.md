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

## Challenge-Specific Criteria

| Criterion | Critical | Initial expectation |
| --- | --- | --- |
| Published intrinsic coverage is complete | yes | Every intrinsic named in the challenge page is either modeled with a safety contract or recorded as an explicit blocker. |
| `core` intrinsics and `std::ptr` wrappers are both covered | yes | The `core::intrinsics` definitions and the exposed `std::ptr` wrappers each point to concrete proof or test artifacts, with no accidental double-counting. |
| Fallback implementations are verified | yes | Any intrinsic that relies on fallback Rust or MIR code has a passing proof or an explicit blocker identifying the unverified fallback path. |
| Modeled intrinsics are explained against their definitions | yes | The PR description or a book entry explains how the modeled behavior matches the published intrinsic definition and where abstraction boundaries are intentionally introduced. |
| Per-function assumptions and guarantees are auditable | yes | Each intrinsic proof records its assumptions, audit path, and the explicit and implicit guarantees it establishes. |
| Challenge UB obligations are discharged | yes | The evidence covers the challenge UB list and any extra safety conditions from source docs or SAFETY comments. |
| Evidence is rerunnable and challenge-local | yes | Commands, paths, and expected output are recorded so another reviewer can rerun the exact check from the worktree. |
| Review feedback is reflected in the artifact shape | no | Any recurring concerns from earlier intrinsic and raw-pointer reviews are translated into clearer names, narrower harnesses, or explicit gap notes. |

## Evidence Expectations

- The evaluator should be able to point to concrete artifacts under `kmir/src/tests/integration/data/verify-rust-std/0002-intrinsics-memory`.
- Proof and test claims should cite the command used, the expected result, and the file or output path that captures it.
- Any explanation of modeled intrinsics should cite the semantic implementation location, such as `kmir/src/kmir/kdist/mir-semantics/intrinsics.md`, or a PR/book entry that states the same correspondence.
- Missing intrinsic coverage, missing wrapper coverage, or missing fallback evidence should be recorded as explicit blockers rather than inferred from surrounding context.

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
