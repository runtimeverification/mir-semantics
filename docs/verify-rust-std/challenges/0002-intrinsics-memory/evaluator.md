# Evaluator Record: Challenge 0002

Ownership:

- Evaluator owns this file and `rubric.md`.
- Evaluator must not implement code, proofs, or harnesses.
- Evaluator must fail closed on missing evidence.

## Inputs

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0002-intrinsics-memory.md
- Tracking issue: [#16](https://github.com/model-checking/verify-rust-std/issues/16)
- Planner record: `docs/verify-rust-std/challenges/0002-intrinsics-memory/planner.md`
- Generator record: `docs/verify-rust-std/challenges/0002-intrinsics-memory/generator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0002-intrinsics-memory/rubric.md`

## Baseline Tasks

- Extend the rubric with challenge-specific criteria.
- Incorporate patterns from resolved challenges, existing solution PRs, and
  review comments.
- Record concrete evidence paths and rerun commands.

## Scorecard

| Criterion | Score | Evidence | Gap |
| --- | --- | --- | --- |
| Published success criteria are mapped to concrete artifacts | 0 | pending | No harness, proof, or blocker artifact is linked yet. |
| Challenge-book rules are satisfied | 0 | pending | No PR or automated verification evidence is available yet. |
| Safety conditions are modeled faithfully | 0 | pending | No contracts or SAFETY-comment trace has been recorded yet. |
| Undefined behavior obligations are covered | 0 | pending | The challenge UB list has not been discharged or blocked explicitly. |
| Evidence is reproducible | 0 | pending | No command log or rerunnable output has been captured yet. |
| Scope is challenge-local and cherry-pickable | 0 | pending | Only orchestration docs exist so far; no implementation commit inventory exists. |
| Review feedback patterns are incorporated | 0 | pending | No prior solution PR review patterns were found locally for this challenge. |
| Residual risk is explicit | 0 | pending | No blocker or dependency log has been recorded yet. |
| Published intrinsic coverage is complete | 0 | pending | No per-function mapping from the challenge list to artifacts exists yet. |
| `core` intrinsics and `std::ptr` wrappers are both covered | 0 | pending | No wrapper-vs-core separation is documented yet. |
| Fallback implementations are verified | 0 | pending | No fallback verification evidence exists yet. |
| Modeled intrinsics are explained against their definitions | 0 | pending | No implementation-vs-definition explanation is cited yet. |
| Per-function assumptions and guarantees are auditable | 0 | pending | No assumption or guarantee inventory exists yet. |
| Challenge UB obligations are discharged | 0 | pending | No UB-specific evidence or explicit blocker is recorded yet. |
| Evidence is rerunnable and challenge-local | 0 | pending | No command output, expected output, or artifact path is linked yet. |

## Likely Reviewer Concerns

- The challenge is broad, so partial intrinsic coverage is not enough; each listed function needs a direct artifact trail.
- `core::intrinsics` coverage and `std::ptr` wrapper coverage can be conflated unless they are tracked separately.
- Any unmodeled fallback path needs an explicit blocker, otherwise a reviewer may assume coverage that does not exist.
- The proof record needs assumptions and guarantees written out clearly enough for audit, not only as informal commentary.
- If later commits claim safety for pointer-based operations, they need to show how alignment, provenance, initialization, and mutability constraints were handled.
- No prior solution PRs or review comments were found in this branch history, so future review feedback should be added here as it appears.

## Verdict

- Current status: `not started`
- Rationale: the branch has only documentation scaffolding so far; no implementation, proof, or test evidence has been produced for the challenge.

## Iteration Log

- Bootstrap record created by orchestrator.
- Initial evaluator scorecard scaffolded on 2026-04-09.
