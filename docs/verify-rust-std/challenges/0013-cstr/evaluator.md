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
| Published success criteria mapped to concrete artifacts | 2 | `generator.md` / `workpad.md` now show prerequisite linker-body-resolution evidence plus challenge-local `from_ptr.rs`, `from_bytes_with_nul_unchecked.rs`, and index-tail artifacts | full `CStr` artifact set still missing |
| Challenge-book rules satisfied | 2 | work stayed within the branch-local challenge path and used scoped `uv` / `kmir` validation | no completed challenge-local proof yet |
| Safety conditions modeled faithfully | 2 | `planner.md` records the exact-byte `CloneToUninit` and tail-preservation concerns from review history, and the new artifact exists for the index tail case | `CloneToUninit` still absent; index proof still fails |
| Undefined behavior obligations covered | 2 | prerequisite linked-SMIR proof path and the challenge-local `from_ptr` / index / `from_bytes_with_nul_unchecked` proof attempts are now recorded | no `strlen` artifact or trait-impl contracts yet |
| Evidence is reproducible | 3 | `generator.md` records commands and outcomes; `workpad.md` includes the same trail and the new proof failures | no full CStr proof rerun yet |
| Scope is challenge-local and cherry-pickable | 2 | commit `80244466` is a small prerequisite-port slice with its own follow-up doc commit `d0517441`; `5cd0bae4` and `91e6317f` add only challenge-local `CStr` artifacts | challenge-specific work still pending |
| Review feedback patterns are incorporated | 2 | rubric and planner/workpad now distinguish exact-byte evidence from “harness exists” evidence | no exact-byte `CloneToUninit` harness has landed yet |
| Residual risk is explicit | 3 | prerequisite infrastructure gap, missing artifacts, and failing proof frontiers are separately documented | none for this criterion |
| `CStr` invariant harness exists and is checked after all nine safe methods | 0 | not present on branch | missing challenge-specific harnesses |
| Unsafe contracts for `from_ptr`, `from_bytes_with_nul_unchecked`, and `strlen` are annotated and verified | 1 | challenge-local artifacts now exist for `from_ptr` and `from_bytes_with_nul_unchecked`, with reproducible proof frontiers on the branch | `strlen` remains missing and the contracts are not yet discharged |
| `CloneToUninit` validates the exact writable region and source bytes | 0 | not present on branch | missing exact-byte harness / contract evidence |
| `Index<RangeFrom<usize>>` preserves the invariant and source tail bytes | 1 | challenge-local exact-byte index artifact exists and proof failure is reproducible | proof still fails and needs refinement |
| Completed proof evidence exists for at least one challenge-local slice | 1 | `generator.md` records reproducible challenge-local proof runs that reach concrete failing/stuck frontiers rather than bootstrap-only setup | no proof is yet closed for a published `CStr` slice |

## Review Pattern Notes

- Prior solution/review history establishes a strong distinction between:
  - prerequisite linker/body-resolution support
  - actual challenge-local `CStr` harnesses/contracts
- `CloneToUninit` evidence must be byte-exact and destination-validity aware; a loose non-null check is not enough.
- A prerequisite fixture port can improve the verifier environment, but it does not satisfy Challenge 13 unless the branch also carries the published `CStr` artifacts.
- If a challenge-local artifact exists but the proof still fails, treat that as actionable branch-local frontier evidence, not as a missing-artifact gap.
- Once multiple challenge-local artifacts exist, remaining work should be classified as frontier reduction plus missing coverage, not bootstrap setup.

## Verdict

- Current status: `in progress`
- Current score: `1.9 / 3`

## Iteration Log

- Bootstrap record created by orchestrator.
