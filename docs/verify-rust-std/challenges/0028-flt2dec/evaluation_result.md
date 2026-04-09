# Evaluation Result: Challenge 0028

Status: `IN PROGRESS`

Overall score: `1.8/3`

## Reconfirmed Requirements

- Goal: verify `core::num::flt2dec`, the float-to-decimal conversion module used by the standard library for human-readable float formatting.
- Published success criteria: prove the safe bodies of `digits_to_dec_str`, `digits_to_exp_str`, `to_shortest_str`, `to_shortest_exp_str`, `to_exact_exp_str`, `to_exact_fixed_str`, `format_shortest_opt`, `format_shortest`, `format_exact_opt`, `format_exact`, plus the dragon-strategy `format_shortest` and `format_exact`.
- Challenge-specific safety obligations: show `assume_init()` is only used on fully initialized values, and show the lifetime-laundering pattern does not create UB.
- UB obligations: no dangling or misaligned loads/stores, no compiler-intrinsic UB, no mutation of immutable bytes, and no invalid values.
- Current plan retarget: commit `4ba24f00c3847fd41007e7246716f5774111b7d3` narrows the next probe to the `MaybeUninit::slice_assume_init_ref` frontier after removing the helper equality path.

## Scorecard

| Criterion | Score | Evidence | Gap |
| --- | --- | --- | --- |
| Published `flt2dec` coverage is concrete | 1 | The branch still has only a representative `digits_to_dec_str` probe in `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs`; the workpad now records the latest rerun and the new frontier. | The rest of the published target list remains unmapped by concrete harnesses or proofs. |
| Safety conditions are carried through | 1 | The probe now reaches `std::mem::MaybeUninit::<core::num::fmt::Part<'_>>::slice_assume_init_ref`, which is the relevant safety surface for the challenge. | No proof result discharges `assume_init()` or the lifetime-laundering pattern for the actual `flt2dec` bodies. |
| UB obligations are tracked explicitly | 1 | The planner and workpad still enumerate the UB list, and the current frontier is narrow enough to isolate harness behavior from module behavior. | The branch has not yet established absence of dangling/misaligned access, intrinsic UB, immutable-byte mutation, or invalid values. |
| Evidence is reproducible and challenge-local | 3 | The generator log records the exact `rustc`, `make build`, `uv --project kmir run kmir prove`, and `uv ... show` commands together with the observed leaves. | None for this slice. |
| Harness frontiers are separated from module frontiers | 3 | The frontier has moved in sequence from `<std::ops::Range<usize> as std::slice::SliceIndex<[u8]>>::index` at `library/core/src/slice/index.rs:440`, to `std::slice::from_raw_parts::<'_, u8>` at `library/core/src/slice/raw.rs:138`, to `std::array::equality::<impl std::cmp::PartialEq<[u8; 4]> for [u8]>::eq` at `/library/core/src/slice/mod.rs:871`, and now to `std::mem::MaybeUninit::<core::num::fmt::Part<'_>>::slice_assume_init_ref` at `core/src/mem/maybe_uninit.rs:987`. All leaves are still in challenge-local scaffolding. | No `flt2dec`-owned leaf has been reached yet. |
| Residual risk is actionable | 2 | The next narrowing step is explicit: bypass `MaybeUninit::slice_assume_init_ref` in the challenge-local probe and rerun the same single case to see whether the proof enters real `flt2dec` code or exposes a backend limit. | The current frontier is still harness-level, so the next probe is necessary before any stronger reclassification. |
| Challenge-book rules are satisfied | 2 | The work stays challenge-local, uses the documented kmir/uv workflow, and avoids runtime-library edits. | No PR/review pass exists yet, so this is not submission-ready. |
| Scope is challenge-local and cherry-pickable | 3 | The branch changes are confined to the challenge artifact area plus its docs, and the commit history is narrow enough to cherry-pick cleanly. | None for this slice. |
| Review feedback patterns are incorporated | 0 | No prior review comments or solved-challenge feedback are recorded for this branch yet. | Nothing concrete to incorporate yet. |

## Verdict

- `IN PROGRESS`
- The branch has made real progress by removing the original `SliceIndex::index` blocker, then the raw-slice construction blocker, and now the helper equality path as well, but the current frontier is still harness-level at `MaybeUninit::slice_assume_init_ref` rather than `flt2dec`-owned behavior.
- The exact next narrowing step is to bypass `MaybeUninit::slice_assume_init_ref` in the challenge-local probe, rerun the same single case, and use the first new leaf to decide whether the challenge has reached real `flt2dec` code or hit a backend limit.

## Evidence Base

- `docs/verify-rust-std/challenges/0028-flt2dec/planner.md`
- `docs/verify-rust-std/challenges/0028-flt2dec/generator.md`
- `docs/verify-rust-std/challenges/0028-flt2dec/workpad.md`
- `docs/verify-rust-std/challenges/0028-flt2dec/plan.md`
- `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs`
- `git -C /home/zhaoji/projs/mir-semantics-vrs/challenges/0028-flt2dec log --oneline --decorate -n 12`
