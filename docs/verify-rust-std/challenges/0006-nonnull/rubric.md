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

Each evaluator iteration should end with:

- current score per criterion
- cited evidence paths and commands
- fail-closed gaps
- a clear verdict: `not started`, `in progress`, `blocked`, or `submission-ready`

## Challenge-Specific Criteria

This challenge is only reviewable when the published `NonNull` surface is
covered directly. Grouped proof families are acceptable, but only if the
evaluation record still maps every published function to a concrete artifact or
an explicit blocker.

| Criterion | Critical | Initial expectation | Evidence expected |
| --- | --- | --- | --- |
| All 48 public `NonNull` APIs are accounted for | yes | Every function on the challenge page appears in a coverage matrix that points to a harness, proof node, regression test, or explicit blocker. | A function-to-artifact map under `kmir/src/tests/integration/data/verify-rust-std/0006-nonnull/`, plus rerun commands showing the map is current. |
| Construction and reference helpers carry faithful safety preconditions | yes | `new_unchecked`, `new`, `as_ref`, `as_mut`, `as_uninit_ref`, `as_uninit_mut`, and related helpers preserve non-null, dereferenceability, lifetime, and alignment obligations from the source docs. | Contracts or assumptions attached to the relevant proofs, with source-aligned SAFETY evidence. |
| Raw-pointer arithmetic and provenance helpers are justified | yes | `add`, `byte_add`, `byte_offset_from`, `byte_offset`, `byte_sub`, `offset_from`, `offset`, `sub_ptr`, `sub`, `align_offset`, `addr`, `with_addr`, `map_addr`, and `cast` are checked against the underlying pointer semantics, not hidden by overconstrained inputs. | Proof logs or harnesses showing the arithmetic and provenance obligations that were actually discharged. |
| Memory-access helpers cover initialization, aliasing, overlap, and immutability | yes | `copy_from`, `copy_from_nonoverlapping`, `copy_to`, `copy_to_nonoverlapping`, `read`, `read_unaligned`, `read_volatile`, `write`, `write_unaligned`, `write_volatile`, `write_bytes`, `replace`, `swap`, and `drop_in_place` address the challenge UB list directly. | Targeted harnesses and proof outputs showing the memory-effect family was verified or cleanly blocked with justification. |
| Slice, DST, and metadata-bearing helpers are sound | yes | `from_raw_parts`, `to_raw_parts`, `slice_from_raw_parts`, `len`, `is_empty`, and `get_unchecked_mut` preserve metadata, length, and index validity for sized and unsized `NonNull` values. | Evidence that slice/DST construction, derived length claims, and indexing assumptions were verified or explicitly blocked. |
| Challenge-local artifacts are reproducible and reviewable | yes | The artifact directory contains stable inputs, outputs, and rerun commands that another reviewer can execute without guessing the intended proof shape. | Concrete file paths, command lines, and expected outputs under `kmir/src/tests/integration/data/verify-rust-std/0006-nonnull/`. |
| Residual risk and dependency gaps are explicit | no | Any unsupported semantics, tool gap, or cross-repo dependency is recorded as a narrow blocker instead of being implied by missing artifacts. | Evaluator notes or blocker entries naming the exact missing capability and why it blocks final approval. |

## Review-Pattern Expectations

- Reviewers will look for a per-function coverage map, not only a claim that
  the `NonNull` family was handled.
- Reviewers will reject proofs that succeed by overconstraining callers unless
  the source `SAFETY` obligations are still visible in the recorded contracts.
- Reviewers will expect downstream `NonNull` users to remain out of scope for
  this rubric unless the branch explicitly claims them as supporting evidence.
- Reviewers will treat any missing raw-pointer, slice, or `MaybeUninit`
  semantics as an explicit blocker, not as an implicit pass.
