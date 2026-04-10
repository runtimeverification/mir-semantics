# Evaluation Result: Challenge 0028

Status: `IN PROGRESS`

Overall score: `2.0/3`

## Reconfirmed Requirements

- Goal: verify `core::num::flt2dec`, the float-to-decimal conversion module used by the standard library for human-readable float formatting.
- Published success criteria: prove the safe bodies of `digits_to_dec_str`, `digits_to_exp_str`, `to_shortest_str`, `to_shortest_exp_str`, `to_exact_exp_str`, `to_exact_fixed_str`, `format_shortest_opt`, `format_shortest`, `format_exact_opt`, `format_exact`, plus the dragon-strategy `format_shortest` and `format_exact`.
- Challenge-specific safety obligations: show `assume_init()` is only used on fully initialized values, and show the lifetime-laundering pattern does not create UB.
- UB obligations: no dangling or misaligned loads/stores, no compiler-intrinsic UB, no mutation of immutable bytes, and no invalid values.
- Current plan retarget: commit `eaa29120` retargets the next probe after the now-terminal taken-arm specialization; commit `c50c0128` records the saved-proof evidence that `digits_to_dec_str_probe.main` reaches terminal `#EndProgram ~> .K` for the current `b"1234", exp = 2, frac_digits = 3` case.

## Scorecard

| Criterion | Score | Evidence | Gap |
| --- | --- | --- | --- |
| Published `flt2dec` coverage is concrete | 2 | The challenge now has a saved-proof terminal result for the representative `digits_to_dec_str` taken-arm specialization, and the branch retarget has been updated to push past that leaf rather than reopen cleared wrapper scaffolding. | The rest of the published target list remains unmapped by concrete harnesses or proofs. |
| Safety conditions are carried through | 1 | The `MaybeUninit::slice_assume_init_ref` return-path helper and earlier wrapper guards have already been peeled away in prior work, so the remaining probe is no longer blocked on those artifacts. | No proof result discharges `assume_init()` or the lifetime-laundering pattern for the actual `flt2dec` bodies. |
| UB obligations are tracked explicitly | 1 | The rubric, workpad, and generator still enumerate the UB list, and the saved terminal proof keeps the focus on challenge-local control flow instead of hiding the obligations behind wrapper noise. | The branch has not yet established absence of dangling/misaligned access, intrinsic UB, immutable-byte mutation, or invalid values. |
| Evidence is reproducible and challenge-local | 3 | The generator log records the exact `rustc`, `make build`, `uv --project kmir run kmir prove`, and `uv ... show` commands together with the saved terminal leaf `#EndProgram ~> .K` for `digits_to_dec_str_probe.main`. | None for this slice. |
| Harness frontiers are separated from module frontiers | 3 | The saved proof now reaches the terminal `#EndProgram ~> .K` leaf for the taken-arm specialization, which confirms the challenge-local wrapper scaffolding has been exhausted on that slice. | The next probe still needs to establish the first `flt2dec`-owned successor path. |
| Residual risk is actionable | 3 | The next narrowing step is explicit: retarget the same `b"1234", exp = 2, frac_digits = 3` case past the terminal leaf and record the first unproven `flt2dec`-owned successor path. | The current frontier is terminal, but the follow-up probe is precisely identified. |
| Challenge-book rules are satisfied | 2 | The work stays challenge-local, uses the documented kmir/uv workflow, and records the proof evidence in the branch docs. | No PR/review pass exists yet, so this is not submission-ready. |
| Scope is challenge-local and cherry-pickable | 3 | The branch changes are confined to the challenge artifact area plus its docs, and the commit history is narrow enough to cherry-pick cleanly. | None for this slice. |
| Review feedback patterns are incorporated | 0 | No prior review comments or solved-challenge feedback are recorded for this branch yet. | Nothing concrete to incorporate yet. |

## Verdict

- `IN PROGRESS`
- Satisfied criteria: reproducible evidence, challenge-local scope, and a terminal proof for the current taken-arm specialization.
- Missing criteria: concrete coverage for the published `flt2dec` target list, discharged safety obligations on the actual formatter bodies, explicit UB closure, and any review-pattern reuse.
- Blockers: the current slice is now terminal at `#EndProgram ~> .K`, so the next probe must be retargeted to the first unproven `flt2dec`-owned successor path instead of reopening cleared wrapper scaffolding.
- Exact next action: follow commit `eaa29120`, keep `b"1234", exp = 2, frac_digits = 3`, and rerun the narrowest challenge-local probe that steps past the terminal `#EndProgram ~> .K` leaf into the next unproven `flt2dec`-owned successor.

## Evidence Base

- `docs/verify-rust-std/challenges/0028-flt2dec/plan.md`
- `docs/verify-rust-std/challenges/0028-flt2dec/generator.md`
- `docs/verify-rust-std/challenges/0028-flt2dec/workpad.md`
- `docs/verify-rust-std/challenges/0028-flt2dec/evaluation_result.md`
- `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs`
- `git -C /home/zhaoji/projs/mir-semantics-vrs/challenges/0028-flt2dec log --oneline --decorate -n 12` showing `c50c0128` and `eaa29120`
