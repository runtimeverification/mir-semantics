# Evaluation Result: Challenge 0028

Status: `IN PROGRESS`

Overall score: `1.9/3`

## Reconfirmed Requirements

- Goal: verify `core::num::flt2dec`, the float-to-decimal conversion module used by the standard library for human-readable float formatting.
- Published success criteria: prove the safe bodies of `digits_to_dec_str`, `digits_to_exp_str`, `to_shortest_str`, `to_shortest_exp_str`, `to_exact_exp_str`, `to_exact_fixed_str`, `format_shortest_opt`, `format_shortest`, `format_exact_opt`, `format_exact`, plus the dragon-strategy `format_shortest` and `format_exact`.
- Challenge-specific safety obligations: show `assume_init()` is only used on fully initialized values, and show the lifetime-laundering pattern does not create UB.
- UB obligations: no dangling or misaligned loads/stores, no compiler-intrinsic UB, no mutation of immutable bytes, and no invalid values.
- Current validated frontier: HEAD commit `cd5f1d3b` confirms no smaller challenge-local reproducer was found beyond `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs`, and the frontier remains the underlying `core::slice::index` path at `<std::ops::Range<usize> as std::slice::SliceIndex<[u8]>>::index` (`library/core/src/slice/index.rs:440`) via `slice_end_index_len_fail`.

Audit anchor:

- `docs/verify-rust-std/challenges/0028-flt2dec/success_criteria.md`
- `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/README.md`

## Scorecard

| Criterion | Score | Evidence | Gap |
| --- | --- | --- | --- |
| Published `flt2dec` coverage is concrete | 1 | The branch still has only a representative `digits_to_dec_str` probe, and the new minimality evidence says `digits_to_dec_str_probe.rs` is the smallest found challenge-local reproducer for this slice. | The rest of the published target list remains unmapped by concrete harnesses or proofs. |
| Safety conditions are carried through | 1 | Prior work already peeled away `MaybeUninit::slice_assume_init_ref` and earlier wrapper guards, and the confirmed minimal reproducer still stops before any proof discharges the actual `flt2dec` safety obligations. | No proof result discharges `assume_init()` or the lifetime-laundering pattern for the actual `flt2dec` bodies. |
| UB obligations are tracked explicitly | 1 | The rubric, workpad, and generator still enumerate the UB list, and the minimality check avoids confusing “we have not shrunk enough” with actual UB closure. | The branch has not yet established absence of dangling/misaligned access, intrinsic UB, immutable-byte mutation, or invalid values. |
| Evidence is reproducible and challenge-local | 3 | HEAD commit `cd5f1d3b` confirms both the lack of a smaller challenge-local reproducer and the exact frontier leaf `<std::ops::Range<usize> as std::slice::SliceIndex<[u8]>>::index` at `library/core/src/slice/index.rs:440` via `slice_end_index_len_fail`. | None for this slice. |
| Harness frontiers are separated from module frontiers | 3 | The active frontier remains the library slice helper `<std::ops::Range<usize> as std::slice::SliceIndex<[u8]>>::index` at `library/core/src/slice/index.rs:440`, and the minimality evidence shows this is not just a missing smaller wrapper. It is still not a `flt2dec`-owned leaf or backend float leaf. | No `flt2dec`-owned leaf has been reached yet. |
| Residual risk is actionable | 3 | The next narrowing step is explicit: stop searching for smaller challenge-local reproducers, keep `digits_to_dec_str_probe.rs` as the minimal slice, and classify or fix `slice_end_index_len_fail` on the restored `&buf[..exp]` path before widening scope. | The current frontier is still challenge-local scaffolding, but the follow-up action is now more tightly constrained. |
| Challenge-book rules are satisfied | 2 | The work stays challenge-local, uses the documented kmir/uv workflow, and records the proof evidence in the branch docs. | No PR/review pass exists yet, so this is not submission-ready. |
| Scope is challenge-local and cherry-pickable | 3 | The branch changes are confined to the challenge artifact area plus its docs, and the commit history is narrow enough to cherry-pick cleanly. | None for this slice. |
| Review feedback patterns are incorporated | 0 | No prior review comments or solved-challenge feedback are recorded for this branch yet. | Nothing concrete to incorporate yet. |

## Verdict

- `IN PROGRESS`
- New result strengthens blocker minimality, not readiness. It shows `digits_to_dec_str_probe.rs` is already the smallest found challenge-local reproducer, but the proof still stops in challenge-local/library scaffolding rather than `flt2dec`-owned logic.
- Satisfied criteria: reproducible evidence, challenge-local scope, and clear separation between copied control-flow leaves and the deeper `core::slice::index` failure path.
- Missing criteria: concrete coverage for the published `flt2dec` target list, discharged safety obligations on the actual formatter bodies, explicit UB closure, and any review-pattern reuse.
- Blockers: the current first stuck leaf remains the `core::slice::index` failure `<std::ops::Range<usize> as std::slice::SliceIndex<[u8]>>::index` at `library/core/src/slice/index.rs:440` via `slice_end_index_len_fail`; no `flt2dec`-owned leaf or backend float limit has been reached yet.
- Exact next action: stop searching for smaller challenge-local reproducers, keep `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs` as the minimal slice, and classify or fix `slice_end_index_len_fail` on the restored `&buf[..exp]` path before widening scope.

## Evidence Base

- `docs/verify-rust-std/challenges/0028-flt2dec/plan.md`
- `docs/verify-rust-std/challenges/0028-flt2dec/generator.md`
- `docs/verify-rust-std/challenges/0028-flt2dec/workpad.md`
- `docs/verify-rust-std/challenges/0028-flt2dec/evaluation_result.md`
- `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs`
- `git -C /home/zhaoji/projs/mir-semantics-vrs/challenges/0028-flt2dec log --oneline --decorate -n 12` showing `cd5f1d3b` and `2b760c78`
