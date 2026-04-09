# Evaluation Result: Challenge 0028

Status: `IN PROGRESS`

Overall score: `1.5/3`

## Reconfirmed Requirements

- Goal: verify `core::num::flt2dec`, the float-to-decimal conversion module used by the standard library for human-readable float formatting.
- Published success criteria: prove the safe bodies of `digits_to_dec_str`, `digits_to_exp_str`, `to_shortest_str`, `to_shortest_exp_str`, `to_exact_exp_str`, `to_exact_fixed_str`, `format_shortest_opt`, `format_shortest`, `format_exact_opt`, `format_exact`, plus the dragon-strategy `format_shortest` and `format_exact`.
- Challenge-specific safety obligations: show `assume_init()` is only used on fully initialized values, and show the lifetime-laundering pattern does not create UB.
- UB obligations: no dangling or misaligned loads/stores, no compiler-intrinsic UB, no mutation of immutable bytes, and no invalid values.

## Scorecard

| Criterion | Score | Evidence | Gap |
| --- | --- | --- | --- |
| Published `flt2dec` coverage is concrete | 1 | The branch contains a representative `digits_to_dec_str` probe and a narrowed rerun in `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs`; the workpad and generator logs record both probe outcomes. | Only one representative function has been probed; the rest of the published target list is still unmapped. |
| Safety conditions are carried through | 1 | The probe exercises `MaybeUninit<Part<'_>>` and raw-slice construction, which is the right safety surface for this module. | No proof result yet discharges `assume_init()` or lifetime-laundering safety for the actual `flt2dec` bodies. |
| UB obligations are tracked explicitly | 1 | The planner and challenge page enumerate the UB list, and the current probe is narrow enough to expose blockers before any real `flt2dec` behavior. | The branch has not yet established absence of dangling/misaligned access, intrinsic UB, immutable-byte mutation, or invalid values. |
| Evidence is reproducible and challenge-local | 3 | The generator log records the exact `rustc`, `make build`, `uv --project kmir run kmir prove`, and `uv ... show` commands together with the observed leaves. | None for this slice. |
| Harness frontiers are separated from module frontiers | 3 | The first blocker was `<std::ops::Range<usize> as std::slice::SliceIndex<[u8]>>::index` at `library/core/src/slice/index.rs:440`; the follow-up moved to `std::slice::from_raw_parts::<'_, u8>` at `library/core/src/slice/raw.rs:138`; the latest rerun now stops at `std::array::equality::<impl std::cmp::PartialEq<[u8; 4]> for [u8]>::eq` at `/library/core/src/slice/mod.rs:871`, all still in challenge-local scaffolding. | No `flt2dec`-owned leaf has been reached yet. |
| Residual risk is actionable | 2 | The next narrowing step is now precise: remove the helper's `assert!(buf == b"1234")`-style equality check, or replace it with a check that does not route through array/slice equality, then rerun to see whether the proof finally reaches `flt2dec`-owned code. | The current frontier is still harness-level, but the next probe should be able to distinguish a helper artifact from module behavior. |
| Challenge-book rules are satisfied | 2 | The work is challenge-local, uses the documented kmir/uv workflow, and avoids runtime-library edits. | No PR/review pass exists yet, so this is not submission-ready. |
| Scope is challenge-local and cherry-pickable | 3 | The branch changes are confined to the challenge artifact area plus its docs, and the commit history is narrow enough to cherry-pick cleanly. | None for this slice. |
| Review feedback patterns are incorporated | 0 | No prior review comments or solved-challenge feedback are recorded for this branch yet. | Nothing concrete to incorporate yet. |

## Verdict

- `IN PROGRESS`
- The branch has made real progress by removing the original `SliceIndex::index` blocker and then the raw-slice construction blocker, but the current frontier is still harness-level at helper array equality rather than `flt2dec`-owned behavior.
- The exact next narrowing step is to eliminate the helper's array-equality assertion, or otherwise avoid the overloaded `[u8]`/`[u8; 4]` equality path, so the next failure can distinguish a harness artifact from a genuine module limitation.

## Evidence Base

- `docs/verify-rust-std/challenges/0028-flt2dec/planner.md`
- `docs/verify-rust-std/challenges/0028-flt2dec/generator.md`
- `docs/verify-rust-std/challenges/0028-flt2dec/workpad.md`
- `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs`
- `git log --oneline --decorate -n 8`
