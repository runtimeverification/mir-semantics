# Evaluation Result: Challenge 0026

Status: `IN PROGRESS`

Overall score: `1.7/3`

## Reconfirmed Requirements

- Goal: verify `Rc` and `Weak`, the reference-counted cell implementation in `alloc::rc`.
- Published success criteria: annotate and verify the safety contracts for the 12 listed public `unsafe` APIs, prove or contract at least 75% of the listed internal unsafe functions, and keep proofs limited to primitive `T` inputs and standard-library allocators (`Global` and `System`).
- Current success table: `docs/verify-rust-std/challenges/0026-rc/success-criteria.md`.
- Challenge-specific UB obligations: exclude dangling or misaligned pointer access, UB via compiler intrinsics, mutation of immutable bytes, and invalid values.
- Additional published safety conditions: `decrement_strong_count` does not need a proof that the count is greater than zero at call time, and `assume_init` may not be fully expressible in the current type system.
- Current branch state: `kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-from-raw-in.rs` remains the verification-shaped harness via `verify_rc_from_raw_in`, `kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-new-in-frontier-fail.rs` now isolates the helper frontier, and `kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-from-raw-in-frontier-fail.rs` remains broader audit context only.

## Scorecard

| Criterion | Score | Evidence | Gap |
| --- | --- | --- | --- |
| Published success criteria are mapped to concrete artifacts | 2 | `contract-map.md` traces all 12 public `unsafe` APIs; `success-criteria.md` records the public surface; `README.md` now separates the verification harness from the minimal and broader reproducers. | The 75% internal-unsafe target is still summarized only by invariant cluster, and no public API has been discharged yet. |
| Challenge-book rules are satisfied | 2 | The branch stays challenge-local, uses documented `kmir` proof commands, and keeps the work reviewable in the existing draft PR without stdlib runtime changes. | The branch still lacks a passing proof or submission-ready review state. |
| Safety conditions are modeled faithfully | 2 | `contract-map.md` captures allocator provenance, one-shot ownership recovery, aliasing, and type-identity obligations; `success-criteria.md` carries the `Rc::from_raw_in` safety summary into the current harness plan. | The safety model is still only documented, not validated by a successful proof. |
| Undefined behavior obligations are covered | 2 | `contract-map.md`, `plan.md`, and `success-criteria.md` keep the raw-pointer/refcount tranche separate from initialization, aliasing, and dynamic-type work. | None of the challenge UB families are discharged yet. |
| Evidence is reproducible | 2 | `README.md` records exact proof commands for `rc-from-raw-in.rs`, `rc-new-in-frontier-fail.rs`, and `rc-from-raw-in-frontier-fail.rs`; `/tmp/rc-from-raw-in-proof-verify-shape-symbolic/rc-from-raw-in.verify_rc_from_raw_in` and `/tmp/rc-new-in-frontier-proof/rc-new-in-frontier-fail.main` both contain terminal node 4 artifacts. | The proof evidence is reproducible but still terminal at the same helper frontier rather than successful. |
| Scope is challenge-local and cherry-pickable | 3 | The work remains inside `docs/verify-rust-std/challenges/0026-rc` and challenge-local harness/test files under `kmir/src/tests/integration/data/verify-rust-std/0026-rc/`. | None for this slice. |
| Review feedback patterns are incorporated | 1 | The artifact split now distinguishes the verification harness from the isolated minimal reproducer instead of overloading one file for both roles. | No stronger reviewer-driven pattern is yet reflected beyond that cleanup. |
| Residual risk is explicit | 3 | `workpad.md`, `generator.md`, `README.md`, and the new minimal reproducer make the shared helper frontier explicit while preserving `rc-from-raw-in.rs` as the proof target. | The risk is named precisely, but not resolved. |
| Public unsafe API surface is fully mapped | 2 | `contract-map.md` and `success-criteria.md` enumerate all 12 public `unsafe` APIs and classify the selected tranche plus wrapper follow-ons. | Mapping exists, but no tranche proof has succeeded and the internal-unsafe target remains open. |
| Raw-pointer/refcount tranche is isolated | 3 | `contract-map.md` and `plan.md` still keep `Rc::from_raw_in`, `Rc::increment_strong_count_in`, `Rc::decrement_strong_count_in`, and `Weak::from_raw_in` as the first proof roots. | None for tranche selection. |
| Challenge-specific UB obligations are explicit | 3 | The UB families remain named in the contract map and echoed in the plan, workpad, and success table. | Only discharge is missing. |
| External dependency risk is named precisely | 1 | The branch now isolates the failing helper path to `Rc::new_in` / `Box::<std::rc::RcInner<u32>, std::alloc::System>::try_new_uninit_in`, which is more precise than the earlier mixed harness frontier. | No specific upstream backend dependency or issue has been proven necessary yet, so this remains a soft risk rather than a confirmed external blocker. |
| Evidence remains challenge-local | 3 | The cited files, commands, proof dirs, and commit SHAs all stay within the branch-local challenge record. | None for locality. |

## Satisfied Criteria

- The public `unsafe` surface is fully enumerated and tied to branch-local artifacts.
- The raw-pointer/refcount family remains the isolated first tranche.
- The new minimal reproducer cleanly isolates the shared helper frontier without redefining the proof target.
- `rc-from-raw-in.rs` remains the verification-shaped harness, so the branch no longer conflates audit reproducers with the intended proof entrypoint.

## Missing Criteria

- No proof has succeeded yet for `verify_rc_from_raw_in`.
- The verification-shaped harness and the minimal reproducer still terminate at the same helper `CastKind::Transmute` frontier.
- The 75% internal-unsafe requirement is still not mapped to concrete per-function artifacts.
- None of the challenge UB obligations are discharged yet; they are only named and scoped.

## Blockers

- `rc-new-in-frontier-fail.rs` isolates the current helper frontier: `/tmp/rc-new-in-frontier-proof/rc-new-in-frontier-fail.main/kcfg/nodes/4.json` is terminal with `#cast(_,_,_,_)_RT-DATA_Evaluation_Evaluation_CastKind_MaybeTy_Ty(..., CastKind::Transmute, ...)`.
- `rc-from-raw-in.rs --start-symbol verify_rc_from_raw_in` still terminates at the same leaf: `/tmp/rc-from-raw-in-proof-verify-shape-symbolic/rc-from-raw-in.verify_rc_from_raw_in/kcfg/nodes/4.json`.
- The new evidence narrows the failure to shared helper setup around `Rc::new_in` / `Box::<std::rc::RcInner<u32>, std::alloc::System>::try_new_uninit_in`, not to the `Rc::from_raw_in` contract body itself.
- This is not yet enough to classify the branch `BLOCKED`: the frontier is isolated, but no specific external dependency has been proven necessary and the branch still has a concrete next investigation step.

## Evidence Base

- `docs/verify-rust-std/challenges/0026-rc/contract-map.md`
- `docs/verify-rust-std/challenges/0026-rc/plan.md`
- `docs/verify-rust-std/challenges/0026-rc/workpad.md`
- `docs/verify-rust-std/challenges/0026-rc/generator.md`
- `docs/verify-rust-std/challenges/0026-rc/success-criteria.md`
- `kmir/src/tests/integration/data/verify-rust-std/0026-rc/README.md`
- `kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-from-raw-in.rs`
- `kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-new-in-frontier-fail.rs`
- `kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-from-raw-in-frontier-fail.rs`
- Commit `08a54a94` `test(verify-rust-std): add minimal rc new_in frontier reproducer`
- Commit `16cf76ad` `docs(verify-rust-std): narrow rc transmute blocker plan`
- `uv --project kmir run kmir prove /home/zhaoji/projs/mir-semantics-vrs/challenges/0026-rc/kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-from-raw-in.rs --start-symbol verify_rc_from_raw_in --proof-dir /tmp/rc-from-raw-in-proof-verify-shape-symbolic --verbose --terminate-on-thunk`
- `sed -n '1,220p' /tmp/rc-from-raw-in-proof-verify-shape-symbolic/rc-from-raw-in.verify_rc_from_raw_in/proof.json`
- `sed -n '1,220p' /tmp/rc-from-raw-in-proof-verify-shape-symbolic/rc-from-raw-in.verify_rc_from_raw_in/kcfg/nodes/4.json`
- `uv --project kmir run kmir prove /home/zhaoji/projs/mir-semantics-vrs/challenges/0026-rc/kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-new-in-frontier-fail.rs --proof-dir /tmp/rc-new-in-frontier-proof --verbose --terminate-on-thunk`
- `sed -n '1,220p' /tmp/rc-new-in-frontier-proof/rc-new-in-frontier-fail.main/proof.json`
- `sed -n '1,220p' /tmp/rc-new-in-frontier-proof/rc-new-in-frontier-fail.main/kcfg/nodes/4.json`

## Verdict

- `IN PROGRESS`
- The branch is still not submission-ready because the first proof target has no successful result and the internal-unsafe requirement remains unmapped.
- The new minimal reproducer improves diagnosis, but it does not by itself prove an external dead end. The conservative classification remains `IN PROGRESS`, not `BLOCKED`.

## Exact Next Action

- Use `rc-new-in-frontier-fail.rs` as the primary reproducer for the shared `Rc::new_in` / `Box::<std::rc::RcInner<u32>, std::alloc::System>::try_new_uninit_in` transmute frontier, then rerun `rc-from-raw-in.rs --start-symbol verify_rc_from_raw_in` to confirm whether the verification-shaped harness moves past the same leaf. Do not widen into other `Rc` APIs until that shared helper frontier is either discharged or cleanly bypassed with equivalent provenance-preserving setup.
