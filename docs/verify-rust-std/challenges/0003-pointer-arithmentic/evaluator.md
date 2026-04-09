# Evaluator Record: Challenge 0003

Ownership:

- Evaluator owns this file and `rubric.md`.
- Evaluator must not implement code, proofs, or harnesses.
- Evaluator must fail closed on missing evidence.

## Inputs

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0003-pointer-arithmentic.md
- Tracking issue: [#76](https://github.com/model-checking/verify-rust-std/issues/76)
- Planner record: `docs/verify-rust-std/challenges/0003-pointer-arithmentic/planner.md`
- Generator record: `docs/verify-rust-std/challenges/0003-pointer-arithmentic/generator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0003-pointer-arithmentic/rubric.md`

## Baseline Tasks

- Extend the rubric with challenge-specific criteria.
- Incorporate patterns from resolved challenges, existing solution PRs, and
  review comments.
- Record concrete evidence paths and rerun commands.

## Scorecard

| Criterion | Score | Evidence | Gap |
| --- | --- | --- | --- |
| Published success criteria are mapped to concrete artifacts | 0 | pending | No contracts, harnesses, proofs, or blockers have been linked yet. |
| Challenge-book rules are satisfied | 0 | pending | No PR evidence or automated verification evidence has been recorded yet. |
| Safety conditions are modeled faithfully | 0 | pending | No SAFETY-comment trace or contract inventory has been collected yet. |
| Undefined behavior obligations are covered | 0 | pending | The challenge UB list has not been discharged or blocked explicitly yet. |
| Evidence is reproducible | 0 | pending | No command log, proof id, or rerunnable output has been captured yet. |
| Scope is challenge-local and cherry-pickable | 0 | pending | Only orchestration docs exist so far; no implementation commit inventory exists. |
| Review feedback patterns are incorporated | 0 | pending | No prior review notes have been collected locally for this branch yet. |
| Residual risk is explicit | 0 | pending | No blocker or dependency log has been recorded yet. |
| Published raw-pointer API coverage is complete | 0 | pending | No per-function mapping from the challenge list to artifacts exists yet. |
| Pointer-arithmetic contracts are faithful for both API families | 0 | pending | No `*const T` versus `*mut T` contract trace exists yet, and byte-vs-element semantics are not audited yet. |
| Pointee coverage matches the published assumptions | 0 | pending | No evidence yet shows the required integer, trait-object, slice, unit, and composite representative coverage. |
| At least three downstream users are proven safe | 0 | pending | No proof or blocker evidence has been linked for `[u8]::is_ascii`, `String::remove`, `Vec::swap_remove`, `Option::as_slice`, or `VecDeque::swap`. |
| Challenge UB obligations are discharged | 0 | pending | No UB-specific evidence or explicit blocker is recorded yet. |
| Evidence is rerunnable and challenge-local | 0 | pending | No command output, expected output, or artifact path is linked yet. |
| Review feedback patterns are incorporated | 0 | pending | No prior solution PR review patterns have been reflected in the branch artifacts yet. |
| Residual risk is explicit | 0 | pending | No blocker notes have been written yet, so missing support would currently be implicit. |

## Likely Reviewer Concerns

- The challenge is broad, so partial pointer-API coverage is not enough; each
  named method must have a direct artifact trail or an explicit blocker.
- `*const T` and `*mut T` families can be accidentally double-counted unless the
  evaluator keeps them separate in the scorecard and evidence notes.
- `byte_*` methods are easy to under-model if the proof accidentally reasons in
  element counts instead of byte offsets.
- The one-past-the-end and same-allocation rules on `add`, `sub`, `offset`, and
  `offset_from` need to be explicit, or a reviewer may treat the proof as
  over-approximated.
- Proving only the primitive pointer methods is insufficient without at least
  three verified downstream users from the published list.
- If the branch narrows inputs, the justification must come from the challenge
  assumptions or standard-library safety text rather than proof convenience.
- No local review comments or prior solution notes have been collected yet, so
  any future feedback should be captured here as soon as it appears.

## Verdict

- Current status: `not started`
- Current verdict: `not started`
- Rationale: the branch currently has only orchestration docs and requirement
  extraction; no proof, test, or blocker evidence has been recorded yet.

## Iteration Log

- Bootstrap record created by orchestrator.
- Initial evaluator scorecard scaffolded for challenge 0003.
