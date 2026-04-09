# Generator Record: Challenge 0028

Ownership:

- Generator owns this file and the implementation work for this challenge.
- Generator must not edit `evaluator.md` or `rubric.md`.
- Generator should treat planner and evaluator edits as authoritative inputs,
  not as files to rewrite.

## Inputs

- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec`
- Planner record: `docs/verify-rust-std/challenges/0028-flt2dec/planner.md`
- Evaluator record: `docs/verify-rust-std/challenges/0028-flt2dec/evaluator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0028-flt2dec/rubric.md`

## Scope Boundary

- Authorized code area: this challenge branch only.
- Default repository scope: `runtimeverification/mir-semantics`
- Allowed secondary scope: `runtimeverification/stable-mir-json` when required
- Exceptional scope: `runtimeverification/haskell-backend` only with explicit
  justification logged here and in the evaluator record

## Work Log

- Confirmed the branch was clean on top of planner commit `14bfaf69` and that
  the 0028 artifact directory only contained the bootstrap `README.md`.
- Checked local float-history context before editing. The current branch
  integration suite still documents the known Haskell-side float hook gap, but
  the first 0028 probe stayed intentionally below that surface.
- Added a challenge-local probe at
  `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs`.
  The probe copies only the private `digits_to_dec_str` body from
  `core/src/num/flt2dec/mod.rs` and asserts one concrete decimal-layout case:
  `b"1234", exp = 2, frac_digits = 3` must yield parts
  `[Copy(b"12"), Copy(b"."), Copy(b"34"), Zero(1)]`.
- The first harness compile surfaced a setup-only issue:
  `std::num::fmt::Part` is test-gated out, so the probe had to use
  `core::num::fmt::Part` directly with `extern crate core;`.
- The first `kmir prove` attempt also surfaced a setup-only issue:
  `/home/zhaoji/.cache/kdist-d250b97/mir-semantics/haskell` did not exist in
  this worktree yet. Running `make build` fixed that prerequisite.
- After setup was fixed, the first probe-specific result was a stuck proof leaf
  in slice-index pointer offset logic, not a float-value crash. The leaf is in
  `<std::ops::Range<usize> as std::slice::SliceIndex<[u8]>>::index` at
  `library/core/src/slice/index.rs:440`, with the stuck term rooted at
  `thunk ( #applyBinOp ( binOpOffset , ... ) )`.
- This means the first 0028 probe currently maps to an artifact/setup path
  issue around the challenge-local wrapper's use of slice indexing, not to the
  earlier Challenge 0011 float backend blocker.

## Files Touched

- `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs`
- `docs/verify-rust-std/challenges/0028-flt2dec/generator.md`
- `docs/verify-rust-std/challenges/0028-flt2dec/workpad.md`

## Validation Evidence

- `rustc kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs -o /tmp/digits_to_dec_str_probe`
  succeeded after switching the probe from `std::num::fmt::Part` to
  `core::num::fmt::Part` and adding `extern crate core;`.
- `/tmp/digits_to_dec_str_probe` exited successfully.
- `uv --project kmir run kmir prove kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs --proof-dir /tmp/0028-digits-to-dec-str-proof --max-depth 50 --max-iterations 3 --reload`
  stopped with `ProofStatus.PENDING`, showing the first capped run was
  insufficient and not itself a semantic blocker.
- `make build` succeeded and populated the missing K definition cache under
  `/home/zhaoji/.cache/kdist-d250b97/mir-semantics/`.
- `uv --project kmir run kmir prove kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs --proof-dir /tmp/0028-digits-to-dec-str-proof --max-depth 200 --reload`
  ended with `ProofStatus.FAILED`, `nodes: 6`, `failing: 1`, `stuck: 1`,
  `terminal: 1`.
- `uv --project kmir run kmir show digits_to_dec_str_probe.main --proof-dir /tmp/0028-digits-to-dec-str-proof --statistics --leaves`
  identified the first concrete leaf:
  function `<std::ops::Range<usize> as std::slice::SliceIndex<[u8]>>::index`,
  span `library/core/src/slice/index.rs:440`, stuck on
  `thunk ( #applyBinOp ( binOpOffset , ... ) )`.

## Commit Inventory

- `1499bc9f` `test(verify-rust-std): add 0028 digits_to_dec_str probe`

## Blockers

- First probe blocker is not the Challenge 0011 float-value backend gap.
- Current blocker is challenge-local: the wrapper probe reaches a stuck
  slice-index pointer-offset leaf before any float-specific backend limitation.
- No backend escalation is justified yet from this first probe alone.
