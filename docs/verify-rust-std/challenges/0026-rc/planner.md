# Planner Record: Challenge 0026

Ownership:

- Planner owns this file.
- Planner must not implement code, proofs, or evaluation.
- Planner may update challenge-local checklists only if the change is purely
  organizational and clearly documented here.

## Inputs

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0026-rc.md
- Tracking issue: [#382](https://github.com/model-checking/verify-rust-std/issues/382)
- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0026-rc`
- Generator record: `docs/verify-rust-std/challenges/0026-rc/generator.md`
- Evaluator record: `docs/verify-rust-std/challenges/0026-rc/evaluator.md`
- Public guidance: issue #382 comments note that most contracts had already been written by the original contributor, with the remaining public-unsafe contracts waiting on a Kani update referenced as model-checking/kani#4427.

## Requirements Extraction

- Published goal: verify `Rc` and `Weak`, the reference-counted cell implementation in `alloc::rc`.
- Published success criteria: annotate and verify the safety contracts for the 12 listed public `unsafe` APIs, prove or contract at least 75% of the listed internal unsafe functions, and keep the proofs limited to primitive `T` inputs and standard-library allocators (`Global`/`System`).
- Challenge-specific UB obligations: automatically exclude dangling or misaligned pointer access, UB via compiler intrinsics, mutation of immutable bytes, and invalid values.
- Additional safety conditions from source docs or SAFETY comments: `decrement_strong_count` does not need a proof that the count is greater than zero at call time, and `assume_init` may not be fully expressible in the current type system.

## Scope Contract

- In scope for current branch: planning artifacts that define the first proof tranche, the evidence matrix, and the exact challenge contract surface.
- Out of scope unless later justified: code edits, proof artifacts, evaluator updates, and any cross-repo dependency changes.
- Exceptional dependency escalation policy: if the chosen tranche needs an upstream tool or backend update, record the dependency, the specific affected function(s), and the reason it is required before touching any non-local repository.

## Sprint Contracts

| Sprint | Intended slice | Acceptance check | Status |
| --- | --- | --- | --- |
| 0 | Map the `Rc`/`Weak` raw-pointer and refcount-transition APIs into a proof-order matrix | The matrix names each function, its source SAFETY comment, and the smallest first tranche that best advances the public-unsafe contract set | in_progress |

## Dependencies And Blockers

- No branch-local blocker is confirmed yet.
- Public guidance suggests a possible dependency on the Kani update referenced in issue #382 comments, but that remains a soft dependency until the selected tranche is checked against the current backend.

## Cross-Challenge Notes

- Challenge 27 is the paired `Arc`/`Weak` effort and may be useful later for pattern comparison, but it is not part of the current tranche.

## History

- Bootstrap record created by orchestrator.
- Planner updated to narrow the branch to one concrete next proof-order subtask.
