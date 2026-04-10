# Evaluation Result: Challenge 0027

## Verdict

`IN PROGRESS`

## Score

`2.0 / 3`

## Status Summary

Challenge 0027 now has evidence-bearing branch-local proof work. The first
symbolic proof harness for `Arc::from_raw_in` exists, and the bounded proof
attempt is recorded as a frontier with a separate concrete reproducer. This is
past bootstrap: the branch now has a symbolic proof harness, a smaller
frontier-only reproducer, and a reproducible failure site. The latest branch
evidence moves both paths past the old helper-level `CastKind::Transmute` leaf
to a shared allocator-call frontier at node `3`.

## Scorecard

| Criterion | Score | Evidence | Gap |
| --- | --- | --- | --- |
| Published success criteria are mapped to concrete artifacts | 2 | `docs/verify-rust-std/challenges/0027-arc/success-criteria.md` now names the first proof target and records both the proof frontier and the separate reproducer at the newer shared `malloc` call leaf. | Only the first tranche is mapped so far; the rest of the Arc/Weak surface is still unmapped. |
| Success-criteria coverage is auditable in the branch and PR | 3 | The branch-local success table and README now expose the first proof slice and reproducer split, and the PR body mirrors the per-function coverage table. | The branch still lacks broader per-function proof depth beyond the first tranche. |
| Challenge-book rules are satisfied | 2 | The work remains branch-local and automation-backed, with no stdlib runtime edits. | The challenge is still in early proof-slice form, so review-grade proof/test evidence is limited. |
| Safety conditions are modeled faithfully | 2 | The harness is symbolic over `u32` and uses the concrete `System` allocator. | The frontier now sits at allocator-call setup rather than the old witness transmute, but the contract is still not validated. |
| Undefined behavior obligations are covered | 1 | The branch now has a concrete raw-pointer/refcount proof root under audit. | None of the published UB obligations have been discharged yet. |
| Verification harnesses are distinguished from reproducers | 3 | `arc-from-raw-in.rs` is the symbolic proof harness, and `arc-from-raw-in-frontier-fail.rs` is the separate concrete reproducer. | None for separation; the remaining gap is proof progress. |
| Semantic blockers are minimized before repair | 3 | The recorded frontier reproducer is explicitly smaller and concrete, and it now isolates the same shared `malloc` `noBody` leaf as the symbolic harness. | The next semantic narrowing step still needs to be chosen. |
| Evidence is reproducible | 3 | The proof result, start symbol, frontier leaf, reproducer start symbol, and proof commands are all recorded in branch-local docs. | None for reproducibility. |
| Scope is challenge-local and cherry-pickable | 2 | The new evidence lives in the challenge-local `0027-arc` worktree and files. | The branch is still early enough that no broader review-ready commit story exists yet. |
| Review feedback patterns are incorporated | 2 | The branch is now using a per-target success table and a proof-vs-reproducer split, matching the reusable review pattern from `0026-rc`. | Only the first proof slice has been exercised, so broader review-pattern reuse is not yet visible. |
| Residual risk is explicit | 3 | The workpad records both the proof frontier and the reproducer frontier site at `#setUpCalleeData(monoItemFn(... name: symbol("malloc"), body: noBody), ...)`. | The exact next narrowing step still needs to be confirmed by further proof slicing. |
| Public unsafe API surface is fully mapped | 2 | `Arc<T, A>::from_raw_in` has the first proof slice and the separate reproducer note, and the public unsafe surface is tracked in the success table. | The remaining 11 public `unsafe` APIs are still unstarted. |
| Internal unsafe tranche is quantified | 0 | bootstrap-level tranche evidence only | The 75% internal unsafe target has not been measured yet. |
| Primitive `T` and standard allocators are respected | 2 | The harness uses primitive `u32` and the standard `System` allocator. | The tranche has not yet progressed far enough to validate broader allocator/refcount behavior. |
| Arc/Weak data-race obligations are explicit | 1 | The branch-local docs keep Arc-specific obligations in view while the first raw-pointer/refcount slice is being advanced. | Arc-specific atomic/data-race obligations have not yet been exercised. |
| Reproducer-vs-proof split is maintained | 3 | The current artifact pair is split into a symbolic proof harness and a dedicated frontier reproducer. | None for separation. |
| Evidence remains challenge-local | 3 | All cited paths and the proof/reproducer result are confined to the `0027-arc` branch-local workspace. | None for locality. |

## Satisfied Criteria

- Dedicated branch, worktree, and challenge-local docs scaffold exist.
- The branch now carries a first symbolic proof harness for `Arc::from_raw_in`.
- The success-criteria table and README give a branch-local audit trail for the first proof slice.
- The proof result is reproducible from the recorded harness, start symbol, and frontier leaf.
- The dedicated frontier reproducer now confirms the same shared node-`3`
  allocator-call frontier as the symbolic harness.

## Missing Criteria

- The proof did not pass; `Arc::from_raw_in` now fails at node `3`.
- The branch has not yet advanced past the first raw-pointer/refcount leaf.
- The remaining 11 public `unsafe` APIs are still unmapped in evidence-bearing form.
- The internal unsafe tranche and Arc-specific data-race obligations remain unaddressed.

## Blocking Issues

- `ProofStatus.FAILED` on `arc-from-raw-in.rs` with start symbol `verify_arc_from_raw_in`.
- The frontier is now node `3` at `#setUpCalleeData(monoItemFn(... name: symbol("malloc"), body: noBody), ...)`.
- Both the symbolic harness and the dedicated reproducer stop at that same allocator-call setup frontier.
- Until that shared allocator-call blocker is classified or discharged, the raw-pointer/refcount spine cannot advance to the follow-on Arc/Weak roots.

## Evidence

- `docs/verify-rust-std/challenges/0027-arc/success-criteria.md`
- `kmir/src/tests/integration/data/verify-rust-std/0027-arc/README.md`
- `kmir/src/tests/integration/data/verify-rust-std/0027-arc/arc-from-raw-in.rs`
- `kmir/src/tests/integration/data/verify-rust-std/0027-arc/arc-from-raw-in-frontier-fail.rs`
- `kmir/src/tests/integration/test_integration.py`
- Commit `1fa0ab79` `0027 arc-from-raw-in first proof slice`
- Commit `19c6fb6f` `0027 split arc frontier reproducer`
- Commit `677ce7f6` `fix(verify-rust-std): move 0027 arc frontier past transmute`

## Next Action Required To Improve State

- Use the dedicated frontier reproducer to determine whether the shared
  `#setUpCalleeData(... symbol("malloc"), body: noBody)` node is now the
  canonical allocator-body blocker; if it is, wire or expose the relevant
  allocator callee body once and then rerun both the reproducer and the
  symbolic `Arc::from_raw_in` harness from that node.
