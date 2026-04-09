# Evaluator Record: Challenge 0005

Ownership:

- Evaluator owns this file and `rubric.md`.
- Evaluator must not implement code, proofs, or harnesses.
- Evaluator must fail closed on missing evidence.

## Inputs

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0005-linked-list.md
- Tracking issue: [#29](https://github.com/model-checking/verify-rust-std/issues/29)
- Planner record: `docs/verify-rust-std/challenges/0005-linked-list/planner.md`
- Generator record: `docs/verify-rust-std/challenges/0005-linked-list/generator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0005-linked-list/rubric.md`

## Baseline Tasks

- Extend the rubric with challenge-specific criteria.
- Incorporate patterns from resolved challenges, existing solution PRs, and
  review comments.
- Record concrete evidence paths and rerun commands.

## Scorecard

This is an initial skeleton. Keep scores at `0` until there is direct evidence
from the branch-local artifacts or a documented blocker.

| Criterion | Score | Evidence | Gap |
| --- | --- | --- | --- |
| Published success criteria are mapped to concrete artifacts | 0 | pending | No proof, test, or blocker artifacts are recorded yet. |
| Challenge-book rules are satisfied | 0 | pending | No rerun command or tool-chain evidence is recorded yet. |
| Safety conditions are modeled faithfully | 0 | pending | No contracts or SAFETY-note mapping has been documented yet. |
| Undefined behavior obligations are covered | 0 | pending | The challenge-specific UB list has not been checked against artifacts yet. |
| Evidence is reproducible | 0 | pending | No command line, tool version, or output log has been captured yet. |
| Scope is challenge-local and cherry-pickable | 0 | pending | No implementation commit or scope evidence exists yet. |
| Review feedback patterns are incorporated | 0 | pending | No solution artifact has been assessed against the prior review comments yet. |
| Challenge-specific blockers are explicit | 0 | pending | No blocker log or solver limitation note has been written yet. |
| All seven published functions are individually accounted for | 0 | pending | Function-by-function coverage has not been recorded yet. |
| The proof is unbounded over arbitrary linked-list shape | 0 | pending | No evidence of an unbounded inductive proof has been captured yet. |
| Linked-list invariants are modeled explicitly | 0 | pending | No list-shape contract or invariant evidence is recorded yet. |
| Challenge UB obligations are discharged or explicitly blocked | 0 | pending | No UB obligation matrix exists yet. |
| Evidence is reproducible from the recorded command line | 0 | pending | No reproducible rerun command or output capture exists yet. |
| Upstream `linked_list.rs` drift is controlled | 0 | pending | No proof-copy/upstream synchronization evidence exists yet. |
| Prior review concerns are explicitly handled | 0 | pending | No explicit discussion of shared theory, `assume`, or unwind coverage exists yet. |
| Residual risk is explicit | 0 | pending | No blocker's list has been assembled yet. |

## Review Pattern Notes

- The upstream solution PR for this challenge surfaced three recurring review
  concerns that should be checked explicitly in later iterations:
  - keep shared doubly-linked-list theory separate from function-by-function
    proof code when possible
  - fail the proof or CI if the proof copy, stripped file, or generated diff
    drifts from the upstream `linked_list.rs` snapshot
  - do not claim full safety coverage if unwind paths are skipped, and call out
    any `assume`-based escape hatches directly
- Review comments also pushed back on cosmetic-only proof-file edits, so the
  evaluator should require a reasoned link between each doc or proof artifact
  and the published challenge criteria.

## Verdict

- Current status: `not started`
- Current gating condition: no implementation artifacts have been supplied for
  scoring yet.

## Iteration Log

- Bootstrap record created by orchestrator.
- Rubric expanded with linked-list-specific criteria and evidence expectations.
- Scorecard left at zero because no proof or test artifacts exist yet in the
  challenge-local directory.
