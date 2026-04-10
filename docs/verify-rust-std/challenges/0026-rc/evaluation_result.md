# Evaluation Result: Challenge 0026

Status: `IN PROGRESS`

Overall score: `1.7/3`

## Reconfirmed Requirements

- Goal: verify `Rc` and `Weak`, the reference-counted cell implementation in `alloc::rc`.
- Published success criteria: annotate and verify the safety contracts for the 12 listed public `unsafe` APIs, prove or contract at least 75% of the listed internal unsafe functions, and keep proofs limited to primitive `T` inputs and standard-library allocators (`Global` and `System`).
- Current success table: `docs/verify-rust-std/challenges/0026-rc/success-criteria.md`.
- Challenge-specific UB obligations: exclude dangling or misaligned pointer access, UB via compiler intrinsics, mutation of immutable bytes, and invalid values.
- Additional published safety conditions: `decrement_strong_count` does not need a proof that the count is greater than zero at call time, and `assume_init` may not be fully expressible in the current type system.
- Current branch state: `kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-from-raw-in.rs` remains the verification-shaped harness via `verify_rc_from_raw_in`, while `kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-new-in-frontier-fail.rs` has now been reduced to a single statement, `let _ = Rc::new_in(7u32, System);`, and still exposes the same helper-level frontier.

## Scorecard

| Criterion | Score | Evidence | Gap |
| --- | --- | --- | --- |
| Published success criteria are mapped to concrete artifacts | 2 | `contract-map.md`, `success-criteria.md`, and the challenge-local `README.md` still map the public surface to a proof harness plus explicit reproducers. `rc-from-raw-in.rs` stays the proof target, while `rc-new-in-frontier-fail.rs` is now the smallest helper reproducer. | The 75% internal-unsafe target is still summarized only by invariant cluster, and no public API has been discharged yet. |
| Challenge-book rules are satisfied | 2 | The branch remains challenge-local, uses documented `kmir` proof/show commands, and keeps the work reviewable in the draft PR without stdlib runtime changes. | The branch still lacks a passing proof or submission-ready review state. |
| Safety conditions are modeled faithfully | 2 | `contract-map.md` and `success-criteria.md` continue to carry allocator provenance, one-shot ownership recovery, and refcount obligations into the `Rc::from_raw_in` plan. | The safety model is still documented rather than proven. |
| Undefined behavior obligations are covered | 2 | `contract-map.md`, `plan.md`, and `success-criteria.md` still keep the raw-pointer/refcount tranche separate from initialization, aliasing, and dynamic-type work. | None of the challenge UB families are discharged yet. |
| Evidence is reproducible | 2 | `/tmp/rc-new-in-frontier-proof-mini/rc-new-in-frontier-fail.main` and `/tmp/rc-from-raw-in-proof-verify-shape-symbolic/rc-from-raw-in.verify_rc_from_raw_in` both reproduce terminal node 4, and `kmir show` now records the exact helper leaf and span for the minimized reproducer. | The evidence is cleaner than before, but still terminal at the same helper frontier rather than successful. |
| Scope is challenge-local and cherry-pickable | 3 | The work remains inside `docs/verify-rust-std/challenges/0026-rc` and challenge-local harness/test files under `kmir/src/tests/integration/data/verify-rust-std/0026-rc/`. | None for this slice. |
| Review feedback patterns are incorporated | 1 | The branch now uses a one-line reproducer to isolate the helper failure instead of mixing proof intent with audit-only statements. | No stronger reviewer-driven pattern is reflected beyond that minimization and artifact split. |
| Residual risk is explicit | 3 | `generator.md`, `workpad.md`, and the stored `kmir show` output now pinpoint the helper-level `CastKind::Transmute` leaf at `library/core/src/alloc/layout.rs:140`. | The risk is explicit, but not resolved. |
| Public unsafe API surface is fully mapped | 2 | `contract-map.md` and `success-criteria.md` still enumerate all 12 public `unsafe` APIs and classify the selected tranche plus wrapper follow-ons. | Mapping exists, but no tranche proof has succeeded and the internal-unsafe target remains open. |
| Raw-pointer/refcount tranche is isolated | 3 | `contract-map.md` and `plan.md` still keep `Rc::from_raw_in`, `Rc::increment_strong_count_in`, `Rc::decrement_strong_count_in`, and `Weak::from_raw_in` as the first proof roots. | None for tranche selection. |
| Challenge-specific UB obligations are explicit | 3 | The UB families remain named in the contract map and echoed in the plan, workpad, and success table. | Only discharge is missing. |
| External dependency risk is named precisely | 1 | The remaining failure is now isolated to helper setup inside `std::boxed::Box::<std::rc::RcInner<u32>, std::alloc::System>::try_new_uninit_in`, with exact leaf text and span evidence. | No specific upstream backend dependency or issue has been proven necessary yet, so this is still a soft risk rather than a confirmed external blocker. |
| Evidence remains challenge-local | 3 | The cited files, commands, proof dirs, and commit SHAs all stay within the branch-local challenge record. | None for locality. |

## Satisfied Criteria

- The public `unsafe` surface is still fully enumerated and tied to branch-local artifacts.
- The raw-pointer/refcount family remains the isolated first tranche.
- The minimal reproducer improved materially: it now contains only `Rc::new_in(7u32, System)`, so the remaining frontier can no longer be attributed to audit-only assertions or extra harness logic.
- `rc-from-raw-in.rs` remains the verification-shaped harness, so the branch still cleanly separates proof target from helper reproducer.

## Missing Criteria

- No proof has succeeded yet for `verify_rc_from_raw_in`.
- The verification-shaped harness and the minimized one-line reproducer still terminate at the same helper `CastKind::Transmute` frontier.
- The 75% internal-unsafe requirement is still not mapped to concrete per-function artifacts.
- None of the challenge UB obligations are discharged yet; they are only named and scoped.

## Blockers

- `rc-new-in-frontier-fail.rs` is now the canonical minimized reproducer, but it still terminates at node 4 with `#cast ( Integer ( 8 , 64 , false ) , castKindTransmute , ty ( 20 ) , ty ( 23 ) )`.
- `kmir show rc-new-in-frontier-fail.main --proof-dir /tmp/rc-new-in-frontier-proof-mini --nodes 4 --full-printer` identifies that leaf inside `std::boxed::Box::<std::rc::RcInner<u32>, std::alloc::System>::try_new_uninit_in` at `library/core/src/alloc/layout.rs:140`.
- `rc-from-raw-in.rs --start-symbol verify_rc_from_raw_in` still reaches the same helper-level leaf, so the challenge proof target remains blocked behind shared helper behavior rather than `Rc::from_raw_in` contract logic.
- This is still `IN PROGRESS`, not `BLOCKED`, because the new evidence proves isolation and precision, but it does not prove that an external dependency is required or that no repo-local semantic/backend fix is possible.

## Evidence Base

- `docs/verify-rust-std/challenges/0026-rc/contract-map.md`
- `docs/verify-rust-std/challenges/0026-rc/plan.md`
- `docs/verify-rust-std/challenges/0026-rc/workpad.md`
- `docs/verify-rust-std/challenges/0026-rc/generator.md`
- `docs/verify-rust-std/challenges/0026-rc/success-criteria.md`
- `kmir/src/tests/integration/data/verify-rust-std/0026-rc/README.md`
- `kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-from-raw-in.rs`
- `kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-new-in-frontier-fail.rs`
- Commit `056a7221` `docs(verify-rust-std): record minimized 0026 rc frontier`
- Commit `fa4b34d8` `test(verify-rust-std): minimize 0026 rc frontier reproducer`
- `uv --project kmir run kmir prove /home/zhaoji/projs/mir-semantics-vrs/challenges/0026-rc/kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-new-in-frontier-fail.rs --proof-dir /tmp/rc-new-in-frontier-proof-mini --verbose --terminate-on-thunk`
- `sed -n '1,220p' /tmp/rc-new-in-frontier-proof-mini/rc-new-in-frontier-fail.main/proof.json`
- `uv --project kmir run kmir show rc-new-in-frontier-fail.main --proof-dir /tmp/rc-new-in-frontier-proof-mini --nodes 4 --full-printer`
- `uv --project kmir run kmir prove /home/zhaoji/projs/mir-semantics-vrs/challenges/0026-rc/kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-from-raw-in.rs --start-symbol verify_rc_from_raw_in --proof-dir /tmp/rc-from-raw-in-proof-verify-shape-symbolic --verbose --terminate-on-thunk`
- `sed -n '1,220p' /tmp/rc-from-raw-in-proof-verify-shape-symbolic/rc-from-raw-in.verify_rc_from_raw_in/proof.json`
- `uv --project kmir run kmir show rc-from-raw-in.verify_rc_from_raw_in --proof-dir /tmp/rc-from-raw-in-proof-verify-shape-symbolic --nodes 4 --full-printer`

## Verdict

- `IN PROGRESS`
- The score stays `1.7/3`. This iteration improves diagnostic precision, but it does not move any critical rubric criterion closer to `3` because the proof target still fails at the same helper-level leaf.
- The branch is still not submission-ready because the first proof target has no successful result and the internal-unsafe requirement remains unmapped.

## Exact Next Action

- Treat `rc-new-in-frontier-fail.rs` as the canonical one-line reproducer for the shared helper frontier in `std::boxed::Box::<std::rc::RcInner<u32>, std::alloc::System>::try_new_uninit_in` at `library/core/src/alloc/layout.rs:140`. Only after that helper-level `CastKind::Transmute` leaf moves should the generator spend more effort on `verify_rc_from_raw_in`; until then, do not widen into other `Rc` APIs or further challenge-local harness reshaping.
