# Evaluation Result: Challenge 0028

Status: `IN PROGRESS`

Overall score: `1.9/3`

## Reconfirmed Requirements

- Goal: verify `core::num::flt2dec`, the float-to-decimal conversion module used by the standard library for human-readable float formatting.
- Published success criteria: prove the safe bodies of `digits_to_dec_str`, `digits_to_exp_str`, `to_shortest_str`, `to_shortest_exp_str`, `to_exact_exp_str`, `to_exact_fixed_str`, `format_shortest_opt`, `format_shortest`, `format_exact_opt`, `format_exact`, plus the dragon-strategy `format_shortest` and `format_exact`.
- Challenge-specific safety obligations: show `assume_init()` is only used on fully initialized values, and show the lifetime-laundering pattern does not create UB.
- UB obligations: no dangling or misaligned loads/stores, no compiler-intrinsic UB, no mutation of immutable bytes, and no invalid values.
- Current validated frontier: the challenge still relies on `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs` as the narrowed probe, and HEAD commit `bc78434e` advances that probe from the old thunked unsize-cast leaf to the concrete `AllocRef` dereference leaf `#traverseProjection ( toLocal ( 2 ) , AllocRef (...) , projectionElemDeref .ProjectionElems , .Contexts )`.

Audit anchor:

- `docs/verify-rust-std/challenges/0028-flt2dec/success_criteria.md`
- `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/README.md`

## Scorecard

| Criterion | Score | Evidence | Gap |
| --- | --- | --- | --- |
| Published `flt2dec` coverage is concrete | 1 | The branch still has only a representative `digits_to_dec_str` probe, and `bc78434e` advances that one probe to a more concrete memory-access frontier. | The rest of the published target list remains unmapped by concrete harnesses or proofs. |
| Safety conditions are carried through | 1 | Prior work already peeled away `MaybeUninit::slice_assume_init_ref` and earlier wrapper guards, and the new `AllocRef` dereference leaf still stops before any proof discharges the actual `flt2dec` safety obligations. | No proof result discharges `assume_init()` or the lifetime-laundering pattern for the actual `flt2dec` bodies. |
| UB obligations are tracked explicitly | 1 | The rubric, workpad, and generator still enumerate the UB list, and the concrete `AllocRef` dereference makes the active memory-access frontier more explicit without yet closing the UB obligations. | The branch has not yet established absence of dangling/misaligned access, intrinsic UB, immutable-byte mutation, or invalid values. |
| Evidence is reproducible and challenge-local | 3 | HEAD commit `bc78434e` records the exact frontier shift from the old thunked unsize-cast leaf to the concrete `AllocRef` dereference leaf `#traverseProjection ( toLocal ( 2 ) , AllocRef (...) , projectionElemDeref .ProjectionElems , .Contexts )`. | None for this slice. |
| Harness frontiers are separated from module frontiers | 3 | The active frontier is now the concrete dereference leaf `#traverseProjection ( toLocal ( 2 ) , AllocRef (...) , projectionElemDeref .ProjectionElems , .Contexts )`, which is more specific than the prior thunked unsize-cast frontier but still not a `flt2dec`-owned leaf or backend float leaf. | No `flt2dec`-owned leaf has been reached yet. |
| Residual risk is actionable | 3 | The next narrowing step is explicit: keep `digits_to_dec_str_probe.rs` as the active slice and classify or fix the concrete `AllocRef` dereference on local `2` so the rerun gets past `projectionElemDeref` before widening scope. | The current frontier is still challenge-local scaffolding, but the follow-up action is now tied to one precise dereference leaf. |
| Challenge-book rules are satisfied | 2 | The work stays challenge-local, uses the documented kmir/uv workflow, and records the proof evidence in the branch docs. | No PR/review pass exists yet, so this is not submission-ready. |
| Scope is challenge-local and cherry-pickable | 3 | The branch changes are confined to the challenge artifact area plus its docs, and the commit history is narrow enough to cherry-pick cleanly. | None for this slice. |
| Review feedback patterns are incorporated | 0 | No prior review comments or solved-challenge feedback are recorded for this branch yet. | Nothing concrete to incorporate yet. |

## Verdict

- `IN PROGRESS`
- New result strengthens frontier concreteness, not readiness. It replaces the old thunked unsize-cast leaf with a concrete `AllocRef` dereference leaf, but the proof still stops in challenge-local scaffolding rather than `flt2dec`-owned logic.
- Satisfied criteria: reproducible evidence, challenge-local scope, and clear separation between copied control-flow leaves and the deeper concrete dereference path.
- Missing criteria: concrete coverage for the published `flt2dec` target list, discharged safety obligations on the actual formatter bodies, explicit UB closure, and any review-pattern reuse.
- Blockers: the current first stuck leaf is now `#traverseProjection ( toLocal ( 2 ) , AllocRef (...) , projectionElemDeref .ProjectionElems , .Contexts )`; no `flt2dec`-owned leaf or backend float limit has been reached yet.
- Exact next action: keep `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs` as the active slice, identify which value in local `2` must be dereferenced at `projectionElemDeref`, and classify or fix that concrete `AllocRef` dereference before widening scope.

## Evidence Base

- `docs/verify-rust-std/challenges/0028-flt2dec/plan.md`
- `docs/verify-rust-std/challenges/0028-flt2dec/generator.md`
- `docs/verify-rust-std/challenges/0028-flt2dec/workpad.md`
- `docs/verify-rust-std/challenges/0028-flt2dec/evaluation_result.md`
- `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs`
- `git -C /home/zhaoji/projs/mir-semantics-vrs/challenges/0028-flt2dec log --oneline --decorate -n 12` showing `bc78434e`, `cd5f1d3b`, and `2b760c78`
