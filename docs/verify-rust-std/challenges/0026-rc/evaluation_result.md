# Evaluation Result: Challenge 0026

Status: `IN PROGRESS`

Overall score: `1.7/3`

## Reconfirmed Requirements

- Goal: verify `Rc` and `Weak`, the reference-counted cell implementation in `alloc::rc`.
- Published success criteria: annotate and verify the safety contracts for the 12 listed public `unsafe` APIs, prove or contract at least 75% of the listed internal unsafe functions, and keep the proofs limited to primitive `T` inputs and standard-library allocators (`Global`/`System`).
- Current success table: `docs/verify-rust-std/challenges/0026-rc/success-criteria.md` tracks the public surface explicitly and summarizes the internal unsafe list by invariant cluster in `contract-map.md`.
- Challenge-specific UB obligations: exclude dangling or misaligned pointer access, UB via compiler intrinsics, mutation of immutable bytes, and invalid values.
- Additional published safety conditions: `decrement_strong_count` does not need a proof that the count is greater than zero at call time, and `assume_init` may not be fully expressible in the current type system.
- Current branch state: the active `verify-rust-std/reexec-0026-rc` branch has a draft PR and mirrors the `Rc::from_raw_in` frontier in `kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-from-raw-in-frontier-fail.rs`; the stable `MaybeUninit` witness still terminates at the same `CastKind::Transmute` leaf.

## Scorecard

| Criterion | Score | Evidence | Gap |
| --- | --- | --- | --- |
| Published success criteria are mapped to concrete artifacts | 2 | `contract-map.md` traces all 12 public `unsafe` APIs to source anchors, source SAFETY summaries, proof entrypoints, and the first-tranche split; `plan.md` and `workpad.md` now pin the next subtask to the direct-witness `Rc::from_raw_in` leaf. | The 75% internal-unsafe target is still not mapped to concrete artifacts, and no proof has discharged any of the listed APIs yet. |
| Challenge-book rules are satisfied | 2 | The branch stays challenge-local, uses the documented `kmir` prove/show commands, and avoids stdlib runtime changes. | The current evidence is still evaluator-record evidence, not a completed PR with passing proof/test results. |
| Safety conditions are modeled faithfully | 2 | `contract-map.md` captures the source SAFETY summaries for allocator provenance, one-shot ownership recovery, aliasing, and type-identity conditions. | The models remain descriptive; they have not yet been validated by a successful proof. |
| Undefined behavior obligations are covered | 2 | `contract-map.md` names the UB families and separates the raw-pointer/refcount tranche from `assume_init`, `get_mut_unchecked`, and `downcast_unchecked`. | None of the UB obligations have been discharged against the backend; they are only tracked and triaged. |
| Evidence is reproducible | 2 | The branch records exact validation commands, proof-dir locations, the challenge-local frontier harness, and the terminal `proof.json` / `kcfg/nodes/4.json` evidence for the direct-witness frontier. | The stable `MaybeUninit` witness still stalls at the same cast frontier, so the evidence is reproducible but not yet successful. |
| Scope is challenge-local and cherry-pickable | 3 | The committed work stays inside `docs/verify-rust-std/challenges/0026-rc` plus the challenge-local harness file under `kmir/src/tests/integration/data/verify-rust-std/0026-rc/`. | None for this slice. |
| Review feedback patterns are incorporated | 1 | The latest plan update narrows the next step to the exact harness shape problem rather than widening to unrelated `Rc` APIs. | No external review thread or repeated solution-pattern feedback is yet reflected in a broader evaluator pattern. |
| Residual risk is explicit | 3 | The workpad, generator record, and rewrite commit all name the concrete direct-witness leaf and the narrow follow-up. | The blocker is explicit, but the fix is not yet implemented. |
| Public unsafe API surface is fully mapped | 2 | `contract-map.md` and `success-criteria.md` list all 12 public `unsafe` functions and classify each into a tranche or wrapper follow-on. | Mapping exists, but the tranche has not been proven and the internal-unsafe target remains open. |
| Raw-pointer/refcount tranche is isolated | 3 | `contract-map.md` and `plan.md` both select `Rc::from_raw_in`, `Rc::increment_strong_count_in`, `Rc::decrement_strong_count_in`, and `Weak::from_raw_in` as the first proof roots. | None for tranche selection. |
| Challenge-specific UB obligations are explicit | 3 | The UB families are named in `contract-map.md` and summarized again in `plan.md` and `workpad.md`. | None for explicitness; only discharge is missing. |
| External dependency risk is named precisely | 1 | `generator.md` still preserves the earlier note that a Kani update may be relevant, but the current blocker is now recorded as a harness-shape failure in `Rc::from_raw_in`. | No upstream dependency has been proven necessary for this blocker, and the possible Kani dependency is not yet tied to a specific API failure. |
| Evidence remains challenge-local | 3 | All cited paths, commands, and commit SHAs stay inside the challenge bundle and current branch. | None for locality. |

## Satisfied Criteria

- The public `unsafe` surface is fully enumerated and split into a usable tranche.
- The public `unsafe` surface is fully enumerated in the new success table and split into a usable tranche.
- The raw-pointer/refcount family is isolated as the first lever.
- The current blocker is named precisely enough to keep the next step narrow.
- Evidence stays local to the challenge branch.

## Missing Criteria

- No proof/test has succeeded yet for `Rc::from_raw_in`.
- The root harness no longer depends on `Rc::new_in` or `Box::<std::rc::RcInner<u32>, std::alloc::System>::try_new_uninit_in`, but it still stalls at the transmute leaf after proof construction.
- The internal-unsafe 75% requirement is still unmapped.
- None of the challenge UB obligations are discharged, only documented.

## Blockers

- The rewritten root harness now reaches a terminal direct-witness `#cast(_,_,_,_)_RT-DATA_Evaluation_Evaluation_CastKind_MaybeTy_Ty` thunk with `CastKind::Transmute` even after the stable `MaybeUninit` witness swap.
- That failure is still a harness-shape problem, not a semantic failure in the `Rc::from_raw_in` body.
- Until the direct witness is shrunk further or the cast leaf is discharged, the tranche cannot advance to `Rc::increment_strong_count_in`, `Rc::decrement_strong_count_in`, or `Weak::from_raw_in`.

## Evidence Base

- `docs/verify-rust-std/challenges/0026-rc/contract-map.md`
- `docs/verify-rust-std/challenges/0026-rc/plan.md`
- `docs/verify-rust-std/challenges/0026-rc/workpad.md`
- `docs/verify-rust-std/challenges/0026-rc/generator.md`
- `docs/verify-rust-std/challenges/0026-rc/evaluation_result.md`
- Commit `16cf76ad` `docs(verify-rust-std): narrow rc transmute blocker plan`
- Commit `23cb733f` `fix(verify-rust-std): rewrite rc from_raw_in witness`
- Commit `7abe7dcd` `test(verify-rust-std): seed rc from_raw_in root harness`
- Commit `7398e820` `docs(verify-rust-std): record rc from_raw_in blocker evidence`
- Commit `cc2f0e86` `docs(verify-rust-std): narrow rc harness next step`
- `git -C /home/zhaoji/projs/mir-semantics-vrs/challenges/0026-rc show 23cb733f:kmir/src/tests/integration/data/prove-rs/rc-from-raw-in.rs`
- `git -C /home/zhaoji/projs/mir-semantics-vrs/challenges/0026-rc show 23cb733f:docs/verify-rust-std/challenges/0026-rc/workpad.md`
- `git -C /home/zhaoji/projs/mir-semantics-vrs/challenges/0026-rc show 16cf76ad:docs/verify-rust-std/challenges/0026-rc/plan.md`
- `uv --project kmir run kmir prove /home/zhaoji/projs/mir-semantics-vrs/challenges/0026-rc/kmir/src/tests/integration/data/prove-rs/rc-from-raw-in.rs --proof-dir /tmp/rc-from-raw-in-proof --verbose --terminate-on-thunk`
- `sed -n '1,220p' /tmp/rc-from-raw-in-proof/rc-from-raw-in.main/proof.json`
- `sed -n '1,220p' /tmp/rc-from-raw-in-proof/rc-from-raw-in.main/kcfg/nodes/4.json`

## Verdict

- `IN PROGRESS`
- The challenge is not submission-ready because the first root harness still fails before a proof result, and the internal-unsafe requirement remains unmapped.
- This remains `IN PROGRESS` rather than `BLOCKED` because the blocker is a local harness-shape issue with a concrete next edit, not an external dead end.

## Exact Next Action

- Rewrite the `Rc::from_raw_in` root harness so it shrinks the current direct witness one step further, eliminates the `#cast(_,_,_,_)_RT-DATA_Evaluation_Evaluation_CastKind_MaybeTy_Ty` `CastKind::Transmute` leaf, and still preserves the same `System` provenance and raw-pointer/allocator pair.
