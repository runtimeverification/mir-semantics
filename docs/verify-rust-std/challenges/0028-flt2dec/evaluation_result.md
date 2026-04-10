# Evaluation Result: Challenge 0028

Status: `IN PROGRESS`

Overall score: `1.9/3`

## Reconfirmed Requirements

- Goal: verify `core::num::flt2dec`, the float-to-decimal conversion module used by the standard library for human-readable float formatting.
- Published success criteria: prove the safe bodies of `digits_to_dec_str`, `digits_to_exp_str`, `to_shortest_str`, `to_shortest_exp_str`, `to_exact_exp_str`, `to_exact_fixed_str`, `format_shortest_opt`, `format_shortest`, `format_exact_opt`, `format_exact`, plus the dragon-strategy `format_shortest` and `format_exact`.
- Challenge-specific safety obligations: show `assume_init()` is only used on fully initialized values, and show the lifetime-laundering pattern does not create UB.
- UB obligations: no dangling or misaligned loads/stores, no compiler-intrinsic UB, no mutation of immutable bytes, and no invalid values.
- Current validated frontier: commit `2b760c78` restores the real prefix slice `&buf[..exp]`, invalidates the earlier saved terminal slice, and the proof in `/tmp/0028-digits-to-dec-str-prefixslice-proof` now stops at the copied `if exp >= buf.len()` `#selectBlock` at `dec/digits_to_dec_str_probe.rs:76`, with stuck predicate `#applyBinOp ( binOpGe , 2 , #applyUnOp ( unOpPtrMetadata , ... ) )`.

## Scorecard

| Criterion | Score | Evidence | Gap |
| --- | --- | --- | --- |
| Published `flt2dec` coverage is concrete | 1 | The branch still has only a representative `digits_to_dec_str` probe, and `2b760c78` adds a concrete new frontier after restoring the real prefix slice rather than a durable proof of module coverage. | The rest of the published target list remains unmapped by concrete harnesses or proofs. |
| Safety conditions are carried through | 1 | Prior work already peeled away `MaybeUninit::slice_assume_init_ref` and earlier wrapper guards, and the new proof keeps the active frontier inside copied `digits_to_dec_str` control flow instead of backend float handling. | No proof result discharges `assume_init()` or the lifetime-laundering pattern for the actual `flt2dec` bodies. |
| UB obligations are tracked explicitly | 1 | The rubric, workpad, and generator still enumerate the UB list, and the new prefix-slice result remains narrow enough to avoid confusing copied control-flow artifacts with UB closure. | The branch has not yet established absence of dangling/misaligned access, intrinsic UB, immutable-byte mutation, or invalid values. |
| Evidence is reproducible and challenge-local | 3 | The checkpoint commit `2b760c78` and proof directory `/tmp/0028-digits-to-dec-str-prefixslice-proof` identify the exact rerun, first stuck leaf, and stuck predicate for the restored prefix-slice experiment. | None for this slice. |
| Harness frontiers are separated from module frontiers | 3 | Restoring the real prefix slice breaks the earlier saved terminal slice and moves the first stuck leaf to the copied `if exp >= buf.len()` `#selectBlock` at `dec/digits_to_dec_str_probe.rs:76`, with predicate `#applyBinOp ( binOpGe , 2 , #applyUnOp ( unOpPtrMetadata , ... ) )`. This is a copied control-flow frontier, not a backend float leaf. | No `flt2dec`-owned leaf has been reached yet. |
| Residual risk is actionable | 3 | The next narrowing step is explicit: keep `b"1234", exp = 2, frac_digits = 3`, preserve the restored real prefix slice, and isolate the copied `if exp >= buf.len()` branch select so the rerun records the first leaf beyond line 76. | The current frontier is still copied control flow, but the follow-up slice is precisely identified. |
| Challenge-book rules are satisfied | 2 | The work stays challenge-local, uses the documented kmir/uv workflow, and records the proof evidence in the branch docs. | No PR/review pass exists yet, so this is not submission-ready. |
| Scope is challenge-local and cherry-pickable | 3 | The branch changes are confined to the challenge artifact area plus its docs, and the commit history is narrow enough to cherry-pick cleanly. | None for this slice. |
| Review feedback patterns are incorporated | 0 | No prior review comments or solved-challenge feedback are recorded for this branch yet. | Nothing concrete to incorporate yet. |

## Verdict

- `IN PROGRESS`
- New result does not strengthen readiness. Restoring the real prefix slice removes the earlier saved terminal slice as a reliable readiness signal and exposes another copied control-flow frontier instead.
- Satisfied criteria: reproducible evidence, challenge-local scope, and clear separation between copied control-flow leaves and backend/module leaves.
- Missing criteria: concrete coverage for the published `flt2dec` target list, discharged safety obligations on the actual formatter bodies, explicit UB closure, and any review-pattern reuse.
- Blockers: the current first stuck leaf is the copied `if exp >= buf.len()` `#selectBlock` at `dec/digits_to_dec_str_probe.rs:76`, with stuck predicate `#applyBinOp ( binOpGe , 2 , #applyUnOp ( unOpPtrMetadata , ... ) )`; no `flt2dec`-owned leaf or backend float limit has been reached yet.
- Exact next action: keep `b"1234", exp = 2, frac_digits = 3`, preserve the restored real prefix slice, narrow the probe past the copied `if exp >= buf.len()` branch select at line 76, and classify the first new leaf before widening scope.

## Evidence Base

- `docs/verify-rust-std/challenges/0028-flt2dec/plan.md`
- `docs/verify-rust-std/challenges/0028-flt2dec/generator.md`
- `docs/verify-rust-std/challenges/0028-flt2dec/workpad.md`
- `docs/verify-rust-std/challenges/0028-flt2dec/evaluation_result.md`
- `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs`
- `/tmp/0028-digits-to-dec-str-prefixslice-proof`
- `git -C /home/zhaoji/projs/mir-semantics-vrs/challenges/0028-flt2dec log --oneline --decorate -n 12` showing `2b760c78`
