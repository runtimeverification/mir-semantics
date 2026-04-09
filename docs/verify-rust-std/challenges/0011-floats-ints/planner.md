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

- Published goal: verify Challenge 11 from `model-checking/verify-rust-std`, covering the numeric primitive methods in Part 1 and Part 2 plus the float-to-int conversion target in Part 3.
- Published success criteria: all listed integer-method harnesses must pass under their stated preconditions, the UB-fail cases must produce the expected failures, and `to_int_unchecked` must be covered for the float types listed in the challenge page.
- Challenge-specific UB obligations: overflow and shift-width violations for the unchecked integer methods, plus the invalid-float-conversion cases for `to_int_unchecked`.
- Additional safety conditions from source docs or SAFETY comments: keep the proofs aligned with the `--terminate-on-thunk` execution model and the challenge assumptions; do not weaken the float path into a vacuous proof.

## Scope Contract

- In scope for current branch: challenge-local planning artifacts, a narrow execution plan, and handoff notes that preserve the float blocker evidence.
- Out of scope unless later justified: implementation in `library/*`, proof/harness edits, backend changes, and any cross-repo dependency work.
- Exceptional dependency escalation policy: if the float portion still depends on missing KMIR/haskell-backend float semantics, record that as a precise blocker and escalate only after confirming the blocker against the current code path and prior PR evidence.

## Sprint Contracts

| Sprint | Intended slice | Acceptance check | Status |
| --- | --- | --- | --- |
| 0 | Bootstrap challenge understanding | Requirements and blockers recorded | done |
| 1 | Narrow the generator target | One concrete next technical subtask and its required evidence are written in `plan.md` | pending |
| 2 | Preserve evaluator evidence trail | `workpad.md` records blocker hypotheses, reusable rubric patterns, and handoff state | pending |

## Dependencies And Blockers

- Primary suspected blocker: the float subtask is still constrained by KMIR / haskell-backend float-value support, as stated in PR #985. That limits any direct progress on `to_int_unchecked` unless the backend gap is already closed in the current branch.
- Secondary dependency: the evaluator should confirm whether the integer harnesses can be re-executed independently and whether the challenge is therefore `CONDITIONALLY READY` for the integer portion while the float path remains blocked.

## Cross-Challenge Notes

- Reuse candidate: PR #985 already records the intended harness split and the float blocker hypothesis; its review history is light, so the main reusable pattern is the challenge decomposition and evidence structure rather than a large review thread.
- Reuse candidate: challenge 13/28 work shows how the portfolio uses branch-local docs to isolate one challenge per evidence trail, but it does not change the float blocker for this challenge.

## History

- Bootstrap record created by orchestrator.
- Planner updated after reconfirming PR #985 and selecting the next generator focus.
