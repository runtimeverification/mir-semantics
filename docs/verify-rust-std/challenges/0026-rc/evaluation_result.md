# Evaluation Result: Challenge 0026

Status: `IN PROGRESS`

Overall score: `1.9/3`

## Reconfirmed Requirements

- Goal: verify `Rc` and `Weak`, the reference-counted cell implementation in `alloc::rc`.
- Published success criteria: annotate and verify the safety contracts for the 12 listed public `unsafe` APIs, prove or contract at least 75% of the listed internal unsafe functions, and keep proofs limited to primitive `T` inputs and standard-library allocators (`Global` and `System`).
- Current success table: `docs/verify-rust-std/challenges/0026-rc/success-criteria.md`.
- Challenge-specific UB obligations: exclude dangling or misaligned pointer access, UB via compiler intrinsics, mutation of immutable bytes, and invalid values.
- Additional published safety conditions: `decrement_strong_count` does not need a proof that the count is greater than zero at call time, and `assume_init` may not be fully expressible in the current type system.
- Current branch state: `kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-from-raw-in.rs` remains the verification-shaped harness via `verify_rc_from_raw_in`, while `kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-new-in-frontier-fail.rs` remains the one-line helper reproducer, `let _ = Rc::new_in(7u32, System);`. After `1b67d068`, both artifacts now move past the old helper `CastKind::Transmute` leaf and stop together at allocator-call setup.

## Scorecard

| Criterion | Score | Evidence | Gap |
| --- | --- | --- | --- |
| Published success criteria are mapped to concrete artifacts | 2 | `contract-map.md`, `success-criteria.md`, and the challenge-local `README.md` still map the public surface to a proof harness plus explicit reproducers. `rc-from-raw-in.rs` stays the proof target, while `rc-new-in-frontier-fail.rs` is now the smallest helper reproducer. | The 75% internal-unsafe target is still summarized only by invariant cluster, and no public API has been discharged yet. |
| Challenge-book rules are satisfied | 2 | The branch remains challenge-local, uses documented `kmir` proof/show commands, and keeps the work reviewable in the draft PR without stdlib runtime changes. | The branch still lacks a passing proof or submission-ready review state. |
| Safety conditions are modeled faithfully | 2 | `contract-map.md` and `success-criteria.md` continue to carry allocator provenance, one-shot ownership recovery, and refcount obligations into the `Rc::from_raw_in` plan. | The safety model is still documented rather than proven. |
| Undefined behavior obligations are covered | 2 | `contract-map.md`, `plan.md`, and `success-criteria.md` still keep the raw-pointer/refcount tranche separate from initialization, aliasing, and dynamic-type work. | None of the challenge UB families are discharged yet. |
| Evidence is reproducible | 2 | `/tmp/rc-new-in-frontier-proof-fix1/rc-new-in-frontier-fail.main` and `/tmp/rc-from-raw-in-proof-fix1/rc-from-raw-in.verify_rc_from_raw_in` both reproduce open node 3 with terminal node 2, and `kmir show` records the shared `#setUpCalleeData(monoItemFn(... name: symbol("malloc"), body: noBody), ...)` frontier in both runs. | The evidence now captures a strictly deeper shared frontier, but it is still an open allocator-call setup leaf rather than a successful proof. |
| Scope is challenge-local and cherry-pickable | 3 | The work remains inside `docs/verify-rust-std/challenges/0026-rc` and challenge-local harness/test files under `kmir/src/tests/integration/data/verify-rust-std/0026-rc/`. | None for this slice. |
| Review feedback patterns are incorporated | 2 | The branch now keeps a strict split between the verification-shaped harness and the one-line helper reproducer, and `1b67d068` documents the semantic movement on both artifacts instead of only on the reducer. | The branch still has not converted that cleaner evidence split into a passing tranche proof. |
| Residual risk is explicit | 3 | `generator.md`, `workpad.md`, and the stored `kmir show` output now pinpoint the shared allocator-call setup leaf `#setUpCalleeData(monoItemFn(... name: symbol("malloc"), body: noBody), ...)` in both proof artifacts. | The risk is explicit, but not resolved. |
| Public unsafe API surface is fully mapped | 2 | `contract-map.md` and `success-criteria.md` still enumerate all 12 public `unsafe` APIs and classify the selected tranche plus wrapper follow-ons. | Mapping exists, but no tranche proof has succeeded and the internal-unsafe target remains open. |
| Raw-pointer/refcount tranche is isolated | 3 | `contract-map.md` and `plan.md` still keep `Rc::from_raw_in`, `Rc::increment_strong_count_in`, `Rc::decrement_strong_count_in`, and `Weak::from_raw_in` as the first proof roots. | None for tranche selection. |
| Challenge-specific UB obligations are explicit | 3 | The UB families remain named in the contract map and echoed in the plan, workpad, and success table. | Only discharge is missing. |
| External dependency risk is named precisely | 2 | The remaining failure is now isolated to allocator-call setup for `malloc` in `std::boxed::Box::<std::rc::RcInner<u32>, std::alloc::System>::try_new_uninit_in`, affecting both the one-line reproducer and `verify_rc_from_raw_in` at the same node. | It is still unproven whether this needs upstream foreign/no-body support or a repo-local allocator model, so the branch cannot yet claim a confirmed external blocker. |
| Evidence remains challenge-local | 3 | The cited files, commands, proof dirs, and commit SHAs all stay within the branch-local challenge record. | None for locality. |

## Satisfied Criteria

- The public `unsafe` surface is still fully enumerated and tied to branch-local artifacts.
- The raw-pointer/refcount family remains the isolated first tranche.
- The minimal reproducer improved materially: it now contains only `Rc::new_in(7u32, System)`, so the remaining frontier can no longer be attributed to audit-only assertions or extra harness logic.
- `rc-from-raw-in.rs` remains the verification-shaped harness, so the branch still cleanly separates proof target from helper reproducer.
- `1b67d068` clears the prior helper `CastKind::Transmute` frontier for both proof artifacts, so the current branch state is strictly ahead of the previous evaluator snapshot.

## Missing Criteria

- No proof has succeeded yet for `verify_rc_from_raw_in`.
- The verification-shaped harness and the minimized one-line reproducer still stop at the same allocator-call setup frontier.
- The 75% internal-unsafe requirement is still not mapped to concrete per-function artifacts.
- None of the challenge UB obligations are discharged yet; they are only named and scoped.

## Blockers

- `rc-new-in-frontier-fail.rs` is still the canonical minimized reproducer, but it now stops at node 3 with `#setUpCalleeData ( monoItemFn ( ... name: symbol ( "malloc" ) , id: defId ( 40 ) , body: noBody ) , ... )`.
- `kmir show rc-new-in-frontier-fail.main --proof-dir /tmp/rc-new-in-frontier-proof-fix1 --nodes 3 --full-printer` records that allocator-call setup leaf directly.
- `kmir show rc-from-raw-in.verify_rc_from_raw_in --proof-dir /tmp/rc-from-raw-in-proof-fix1 --nodes 3 --full-printer` reaches the same `malloc`/`noBody` setup leaf, so the proof target is still blocked behind shared helper behavior rather than `Rc::from_raw_in` contract logic.
- This is still `IN PROGRESS`, not `BLOCKED`, because the branch has made forward semantic progress and the new evidence still does not prove that a repo-external dependency is required.

## Evidence Base

- `docs/verify-rust-std/challenges/0026-rc/contract-map.md`
- `docs/verify-rust-std/challenges/0026-rc/plan.md`
- `docs/verify-rust-std/challenges/0026-rc/workpad.md`
- `docs/verify-rust-std/challenges/0026-rc/generator.md`
- `docs/verify-rust-std/challenges/0026-rc/success-criteria.md`
- `kmir/src/tests/integration/data/verify-rust-std/0026-rc/README.md`
- `kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-from-raw-in.rs`
- `kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-new-in-frontier-fail.rs`
- Commit `1b67d068` `fix(verify-rust-std): move 0026 rc frontier past transmute`
- Commit `056a7221` `docs(verify-rust-std): record minimized 0026 rc frontier`
- `uv --project kmir run kmir prove /home/zhaoji/projs/mir-semantics-vrs/challenges/0026-rc/kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-new-in-frontier-fail.rs --proof-dir /tmp/rc-new-in-frontier-proof-fix1 --verbose --terminate-on-thunk`
- `sed -n '1,220p' /tmp/rc-new-in-frontier-proof-fix1/rc-new-in-frontier-fail.main/proof.json`
- `uv --project kmir run kmir show rc-new-in-frontier-fail.main --proof-dir /tmp/rc-new-in-frontier-proof-fix1 --nodes 3 --full-printer`
- `uv --project kmir run kmir prove /home/zhaoji/projs/mir-semantics-vrs/challenges/0026-rc/kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-from-raw-in.rs --start-symbol verify_rc_from_raw_in --proof-dir /tmp/rc-from-raw-in-proof-fix1 --verbose --terminate-on-thunk`
- `sed -n '1,220p' /tmp/rc-from-raw-in-proof-fix1/rc-from-raw-in.verify_rc_from_raw_in/proof.json`
- `uv --project kmir run kmir show rc-from-raw-in.verify_rc_from_raw_in --proof-dir /tmp/rc-from-raw-in-proof-fix1 --nodes 3 --full-printer`

## Verdict

- `IN PROGRESS`
- The score rises to `1.9/3`. This iteration clears the prior helper `CastKind::Transmute` frontier and moves both artifacts to a deeper shared allocator-call setup node, but no critical rubric criterion reaches `3` because the proof target still does not pass.
- The branch is still not submission-ready because the first proof target has no successful result and the internal-unsafe requirement remains unmapped.

## Exact Next Action

- Treat node 3 at `#setUpCalleeData(monoItemFn(... name: symbol("malloc"), body: noBody), ...)` as the sole next frontier. First determine whether `malloc` should be handled by existing foreign/no-body call machinery or needs a dedicated allocator-call model, validate that on `rc-new-in-frontier-fail.rs`, and only then rerun `verify_rc_from_raw_in` without widening into other `Rc` APIs or reshaping the harness again.
