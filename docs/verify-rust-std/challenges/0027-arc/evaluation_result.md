# Evaluation Result: Challenge 0027

## Verdict

`IN PROGRESS`

## Score

`1.5 / 3`

## Status Summary

Challenge 0027 now has evidence-bearing branch-local proof work. The first
symbolic proof harness for `Arc::from_raw_in` exists, and the bounded proof
attempt is recorded as a frontier rather than a bootstrap placeholder.

## Scorecard

| Criterion | Score | Evidence | Gap |
| --- | --- | --- | --- |
| Published success criteria are mapped to concrete artifacts | 2 | `docs/verify-rust-std/challenges/0027-arc/success-criteria.md` now names the first proof target and records the frontier leaf. | Only the first tranche is mapped so far; the rest of the Arc/Weak surface is still unmapped. |
| Success-criteria coverage is auditable in the branch and PR | 1 | The branch-local success table and README now expose the first proof slice. | The draft PR does not yet mirror a mature per-function coverage table. |
| Challenge-book rules are satisfied | 1 | The work remains branch-local and automation-backed, with no stdlib runtime edits. | The challenge is still in early proof-slice form, so review-grade proof/test evidence is limited. |
| Safety conditions are modeled faithfully | 1 | The harness is symbolic over `u32` and uses the concrete `System` allocator. | The frontier shows the witness construction is still too wide, so the contract is not yet validated. |
| Undefined behavior obligations are covered | 1 | The branch now has a concrete raw-pointer/refcount proof root under audit. | None of the published UB obligations have been discharged yet. |
| Verification harnesses are distinguished from reproducers | 2 | `arc-from-raw-in.rs` is a symbolic proof harness, not a concrete witness driver. | No separate reproducer file exists yet for the current frontier. |
| Semantic blockers are minimized before repair | 2 | The recorded frontier is the smallest known leaf so far, at node `4`. | The branch has not yet produced a dedicated minimal reproducer file for the blocker. |
| Evidence is reproducible | 2 | The proof result, start symbol, and frontier leaf are recorded in branch-local docs. | A rerun command and proof-dir evidence still need to be mirrored into a more mature audit table. |
| Scope is challenge-local and cherry-pickable | 2 | The new evidence lives in the challenge-local `0027-arc` worktree and files. | The branch is still early enough that no broader review-ready commit story exists yet. |
| Review feedback patterns are incorporated | 1 | The branch is now using a per-target success table, matching the reusable review pattern from `0026-rc`. | Only the first proof slice has been exercised, so broader review-pattern reuse is not yet visible. |
| Residual risk is explicit | 2 | The workpad records the frontier at `Box::<alloc::sync::ArcInner<u32>, std::alloc::System>::new_uninit_in`. | The exact next narrowing step still needs to be confirmed by further proof slicing. |
| Public unsafe API surface is fully mapped | 1 | `Arc<T, A>::from_raw_in` has the first proof slice and frontier note. | The remaining 11 public `unsafe` APIs are still unstarted. |
| Internal unsafe tranche is quantified | 0 | bootstrap-level tranche evidence only | The 75% internal unsafe target has not been measured yet. |
| Primitive `T` and standard allocators are respected | 2 | The harness uses primitive `u32` and the standard `System` allocator. | The tranche has not yet progressed far enough to validate broader allocator/refcount behavior. |
| Arc/Weak data-race obligations are explicit | 0 | bootstrap-level notes only | Arc-specific atomic/data-race obligations have not yet been exercised. |
| Reproducer-vs-proof split is maintained | 1 | The current artifact is a proof harness, and the workpad reserves reproducer splitting if needed. | There is not yet a separate frontier reproducer file for the current blocker. |
| Evidence remains challenge-local | 3 | All cited paths and the proof result are confined to the `0027-arc` branch-local workspace. | None for locality. |

## Satisfied Criteria

- Dedicated branch, worktree, and challenge-local docs scaffold exist.
- The branch now carries a first symbolic proof harness for `Arc::from_raw_in`.
- The success-criteria table and README give a branch-local audit trail for the first proof slice.
- The proof result is reproducible from the recorded harness, start symbol, and frontier leaf.

## Missing Criteria

- The proof did not pass; `Arc::from_raw_in` still fails at leaf `4`.
- The branch has not yet produced a separate minimal frontier reproducer file.
- The remaining 11 public `unsafe` APIs are still unmapped in evidence-bearing form.
- The internal unsafe tranche and Arc-specific data-race obligations remain unaddressed.

## Blocking Issues

- `ProofStatus.FAILED` on `arc-from-raw-in.rs` with start symbol `verify_arc_from_raw_in`.
- The frontier is leaf `4` at `Box::<alloc::sync::ArcInner<u32>, std::alloc::System>::new_uninit_in`, which reaches `castKindTransmute`.
- Until that witness construction is narrowed, the raw-pointer/refcount spine cannot advance to the follow-on Arc/Weak roots.

## Evidence

- `docs/verify-rust-std/challenges/0027-arc/success-criteria.md`
- `docs/verify-rust-std/challenges/0027-arc/workpad.md`
- `kmir/src/tests/integration/data/verify-rust-std/0027-arc/README.md`
- `kmir/src/tests/integration/data/verify-rust-std/0027-arc/arc-from-raw-in.rs`
- `kmir/src/tests/integration/test_integration.py`
- Commit `1fa0ab79` `0027 arc-from-raw-in first proof slice`

## Next Action Required To Improve State

- Narrow the `Arc::from_raw_in` witness one step further or split out the
  smallest concrete frontier reproducer for the `castKindTransmute` leaf, then
  re-evaluate the raw-pointer/refcount tranche.
