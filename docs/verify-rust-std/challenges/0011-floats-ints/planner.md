# Planner Record: Challenge 0011

Ownership:

- Planner owns this file.
- Planner must not implement code, proofs, or evaluation.
- Planner may update challenge-local checklists only if the change is purely
  organizational and clearly documented here.

## Inputs

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0011-floats-ints.md
- Tracking issue: [#59](https://github.com/model-checking/verify-rust-std/issues/59)
- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints`
- Generator record: `docs/verify-rust-std/challenges/0011-floats-ints/generator.md`
- Evaluator record: `docs/verify-rust-std/challenges/0011-floats-ints/evaluator.md`

## Requirements Extraction

- Published goal: verify Challenge 11 from `model-checking/verify-rust-std`, covering Part 1 unsafe integer methods, Part 2 safe integer APIs, and Part 3 `to_int_unchecked` for `f16`, `f32`, `f64`, and `f128`.
- Published success criteria: each listed integer harness must satisfy its stated preconditions, the UB-fail harnesses must exhibit the expected failures, and the float-to-int conversion path must be either proved or blocked with exact backend evidence.
- Challenge-specific UB obligations: overflow, underflow, and shift-width violations for the unchecked integer methods, plus invalid float conversions and the generic UB list from the challenge page.
- Additional safety conditions from source docs or SAFETY comments: keep the proofs aligned with the `--terminate-on-thunk` execution model and the challenge assumptions; do not weaken the float path into a vacuous proof or a placeholder artifact.
- Historical guidance from PR #985: Parts 1 and 2 were intended to be complete, while Part 3 is explicitly blocked by missing KMIR / haskell-backend float-value support; the only review context visible on the PR is an LGTM comment, so the blocker signal comes from the PR body and the branch-local float artifacts, not from a deep review thread.

## Scope Contract

- In scope for current branch: challenge-local planning artifacts, a narrow execution plan, and handoff notes that preserve the float blocker evidence.
- Out of scope unless later justified: implementation in `library/*`, proof/harness edits, backend changes, and any cross-repo dependency work.
- Exceptional dependency escalation policy: if the float portion still depends on missing KMIR/haskell-backend float semantics, record that as a precise blocker and escalate only after confirming the blocker against the current code path and prior PR evidence.

## Sprint Contracts

| Sprint | Intended slice | Acceptance check | Status |
| --- | --- | --- | --- |
| 0 | Bootstrap challenge understanding | Requirements and blockers recorded | done |
| 1 | Narrow the generator target | One concrete next technical subtask and its required evidence are written in `plan.md` | done |
| 2 | Preserve evaluator evidence trail | `workpad.md` records blocker hypotheses, reusable rubric patterns, and handoff state | in progress |

## Dependencies And Blockers

- Current frontier: five direct proof slices pass on this branch, but the broader non-float matrix is still unconfirmed. The highest-leverage next step is `widening_mul_u8`, because it is the cheapest remaining safe-API slice, opens a new Part 2 family beyond the already green wrapping-shift pair, and is likely to reuse the existing unsigned multiplication support without any new backend work.
- Primary blocker remains the float path in Part 3: PR #985 states that KMIR lacks float-value support, and the ported `to_int_unchecked-fail` artifacts still show stuck float intrinsic hooks. That blocker should stay separate from any new integer proof work.
- Secondary dependency: if the new Part 2 slice passes, the evaluator can reassess whether the remaining gap is purely the known float blocker plus the still-broad Part 1/Part 2 matrix, or whether another artifact gap still exists.

## Cross-Challenge Notes

- Reuse candidate: PR #985 already records the intended harness split and the float blocker hypothesis; its review history is light, so the main reusable pattern is the challenge decomposition and evidence structure rather than a large review thread.
- Reuse candidate: challenge 13/28 work shows how the portfolio uses branch-local docs to isolate one challenge per evidence trail, but it does not change the float blocker for this challenge.
- Reuse candidate: the verify-rust-std challenge page itself is the authoritative success-criteria source, so the planner should keep the current frontier tied to published requirements rather than to incidental test discovery.

## History

- Bootstrap record created by orchestrator.
- Planner updated after reconfirming the challenge page, PR #985, and selecting `wrapping_shl_u8` as the first delegated proof slice.
- Planner updated after the `unchecked_sub_u8` pass and evaluator refresh; `wrapping_shr_u8` is now the next delegated proof slice.
- Planner refreshed after the `wrapping_shr_u8` pass; `widening_mul_u8` is now the next delegated proof slice.
