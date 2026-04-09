# Evaluator Record: Challenge 0013

Ownership:

- Evaluator owns this file and `rubric.md`.
- Evaluator must not implement code, proofs, or harnesses.
- Evaluator must fail closed on missing evidence.

## Inputs

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0013-cstr.md
- Tracking issue: [#150](https://github.com/model-checking/verify-rust-std/issues/150)
- Planner record: `docs/verify-rust-std/challenges/0013-cstr/planner.md`
- Generator record: `docs/verify-rust-std/challenges/0013-cstr/generator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0013-cstr/rubric.md`

## Baseline Tasks

- Extend the rubric with challenge-specific criteria.
- Incorporate patterns from resolved challenges, existing solution PRs, and
  review comments.
- Record concrete evidence paths and rerun commands.

## Scorecard

| Criterion | Score | Evidence | Gap |
| --- | --- | --- | --- |
| Published success criteria mapped to concrete artifacts | 1 | `generator.md` / `workpad.md` show prerequisite linker-body-resolution evidence on `kmir/cstr.smir.json` | actual `CStr` contracts/harnesses still missing |
| Challenge-book rules satisfied | 2 | work stayed within the branch-local challenge path and used scoped `uv` / `kmir` validation | no completed challenge-local proof yet |
| Safety conditions modeled faithfully | 1 | `planner.md` records the exact-byte `CloneToUninit` and tail-preservation concerns from review history | those concerns are not yet discharged by artifacts |
| Undefined behavior obligations covered | 1 | prerequisite linked-SMIR proof path was validated on `test_from_ptr` | no `from_ptr`, `from_bytes_with_nul_unchecked`, `strlen`, or trait-impl contracts yet |
| Evidence is reproducible | 2 | `generator.md` records commands and outcomes; `workpad.md` includes the same evidence trail | no full CStr proof rerun yet |
| Scope is challenge-local and cherry-pickable | 2 | commit `80244466` is a small prerequisite-port slice with its own follow-up doc commit `d0517441` | challenge-specific work still pending |
| Review feedback patterns are incorporated | 2 | rubric and planner/workpad now distinguish exact-byte evidence from “harness exists” evidence | no exact-byte harness has landed yet |
| Residual risk is explicit | 3 | backend float blocker and CStr artifact gap are separately documented | none for this criterion |
| `CStr` invariant harness exists and is checked after all nine safe methods | 0 | not present on branch | missing challenge-specific harnesses |
| Unsafe contracts for `from_ptr`, `from_bytes_with_nul_unchecked`, and `strlen` are annotated and verified | 0 | not present on branch | missing contracts and proofs |
| `CloneToUninit` validates the exact writable region and source bytes | 0 | not present on branch | missing exact-byte harness / contract evidence |
| `Index<RangeFrom<usize>>` preserves the invariant and source tail bytes | 0 | not present on branch | missing indexing harness evidence |

## Review Pattern Notes

- Prior solution/review history establishes a strong distinction between:
  - prerequisite linker/body-resolution support
  - actual challenge-local `CStr` harnesses/contracts
- `CloneToUninit` evidence must be byte-exact and destination-validity aware; a loose non-null check is not enough.
- A prerequisite fixture port can improve the verifier environment, but it does not satisfy Challenge 13 unless the branch also carries the published `CStr` artifacts.

## Verdict

- Current status: `in progress`

## Iteration Log

- Bootstrap record created by orchestrator.
