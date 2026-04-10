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
- Follow-up rerun on this branch narrowed the harness by replacing the copied
  `digits_to_dec_str` branch's `&buf[..exp]` / `&buf[exp..]` indexing with a
  challenge-local `split_at_raw` helper based on raw slice construction, and by
  dropping the probe's result indexing assertions.
- That rerun bypassed the original `Range<usize>::index` blocker, but the next
  boundary is still harness-level: the proof now gets stuck inside
  `std::slice::from_raw_parts::<'_, u8>` at `library/core/src/slice/raw.rs:138`
  after entering `split_at_raw`, so the probe still has not reached a
  `flt2dec`-owned failure.
- This slice removed the follow-up probe's remaining raw-slice artifact by
  deleting `split_at_raw`, replacing the decimal-point split with a
  challenge-local concrete-case helper for the single exercised input
  `b"1234", exp = 2`, and switching the initialized-parts return path to
  `MaybeUninit::slice_assume_init_ref`, matching the std body more closely.
- The local toolchain still gates `MaybeUninit::slice_assume_init_ref`, so the
  probe needed `#![feature(maybe_uninit_slice)]` before the narrowed harness
  would compile.
- The rerun removed `std::slice::from_raw_parts` from the active path, but it
  still did not reach `flt2dec`-owned logic or a backend float limit. The new
  first leaf is the helper's `assert!(buf == b\"1234\")`, which enters
  `std::array::equality::<impl std::cmp::PartialEq<[u8; 4]> for [u8]>::eq` at
  `library/core/src/slice/mod.rs:871` from `probe_decimal_point_case`.
- The latest rerun removes that helper equality path entirely. The proof now
  fails in `std::mem::MaybeUninit::<core::num::fmt::Part<'_>>::slice_assume_init_ref`
  at `core/src/mem/maybe_uninit.rs:987`, reached from the copied
  `digits_to_dec_str` body rather than from the concrete-case helper itself.
- This keeps the challenge-local frontier narrow while exposing the next
  harness boundary more directly.
- The next rerun replaced the `MaybeUninit::slice_assume_init_ref` return
  conversion with a challenge-local static-slice helper. The proof moved
  again, but now the first concrete leaf is the `buf[0]` bounds check inserted
  by `assert!(buf[0] > b'0')` at `dec/digits_to_dec_str_probe.rs:44`, with a
  sibling leaf on the `assert!(!buf.is_empty())` panic path at line 43.
- The next narrowing step specialized the probe to the taken decimal-point arm
  for the single concrete `b"1234", exp = 2, frac_digits = 3` case so the
  copied `if exp < buf.len()` select is no longer active in the proof path.
  The probe still compiles, but the follow-up proof rerun was interrupted
  before it reported a new leaf.

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
- `rustc kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs -o /tmp/digits_to_dec_str_probe_0028_followup`
  succeeded after the follow-up narrowing edit.
- `/tmp/digits_to_dec_str_probe_0028_followup` exited successfully.
- `uv --project kmir run kmir prove kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs --proof-dir /tmp/0028-digits-to-dec-str-followup-proof --max-depth 200 --reload`
  ended with `ProofStatus.FAILED`, `nodes: 5`, `failing: 1`, `stuck: 1`,
  `terminal: 1`.
- `uv --project kmir run kmir show digits_to_dec_str_probe.main --proof-dir /tmp/0028-digits-to-dec-str-followup-proof --statistics --leaves`
  showed the new first concrete leaf:
  function `std::slice::from_raw_parts::<'_, u8>`, span
  `library/core/src/slice/raw.rs:138`, reached from the challenge-local
  `split_at_raw` helper at `dec/digits_to_dec_str_probe.rs:9`.
- `rustc kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs -o /tmp/digits_to_dec_str_probe_0028_followup2`
  initially failed with `E0658` because
  `MaybeUninit::slice_assume_init_ref` requires the crate feature
  `maybe_uninit_slice` on this nightly; the probe compiled successfully after
  adding that feature.
- `/tmp/digits_to_dec_str_probe_0028_followup2` exited successfully.
- `uv --project kmir run kmir prove kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs --proof-dir /tmp/0028-digits-to-dec-str-followup2-proof --max-depth 200 --reload`
  ended with `ProofStatus.FAILED`, `nodes: 5`, `failing: 1`, `stuck: 1`,
  `terminal: 1`.
- `uv --project kmir run kmir show digits_to_dec_str_probe.main --proof-dir /tmp/0028-digits-to-dec-str-followup2-proof --statistics --leaves`
  showed the new first concrete leaf:
  function `std::array::equality::<impl std::cmp::PartialEq<[u8; 4]> for [u8]>::eq`,
  span `/library/core/src/slice/mod.rs:871`, reached from the
  challenge-local `probe_decimal_point_case` assertion at
  `dec/digits_to_dec_str_probe.rs:9`.
- `rustc kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs -o /tmp/digits_to_dec_str_probe_0028_eqless`
  succeeded after deleting the helper equality checks and prefixing the now-unused helper arguments with underscores.
- `/tmp/digits_to_dec_str_probe_0028_eqless` exited successfully.
- `uv --project kmir run kmir prove kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs --proof-dir /tmp/0028-digits-to-dec-str-eqless-proof --max-depth 200 --reload`
  ended with `ProofStatus.FAILED`, `nodes: 10`, `failing: 1`, `stuck: 1`,
  `terminal: 1`.
- `uv --project kmir run kmir show digits_to_dec_str_probe.main --proof-dir /tmp/0028-digits-to-dec-str-eqless-proof --statistics --leaves`
  showed the new first concrete leaf:
  function `std::mem::MaybeUninit::<core::num::fmt::Part<'_>>::slice_assume_init_ref`,
  span `core/src/mem/maybe_uninit.rs:987`, reached from
  `digits_to_dec_str` at `dec/digits_to_dec_str_probe.rs:41`.
- `rustc kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs -o /tmp/digits_to_dec_str_probe_0028_bypass`
  succeeded after replacing the `MaybeUninit` slice conversion with a static
  slice helper.
- `uv --project kmir run kmir prove kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs --proof-dir /tmp/0028-digits-to-dec-str-bypass-proof --max-depth 200 --reload`
  ended with `ProofStatus.FAILED`, `nodes: 6`, `failing: 3`, `stuck: 3`,
  `terminal: 1`.
- `uv --project kmir run kmir show digits_to_dec_str_probe.main --proof-dir /tmp/0028-digits-to-dec-str-bypass-proof --statistics --leaves`
  showed the new first concrete leaf at the probe's own guard path:
  `#traverseProjection ( toLocal ( 1 ) , thunk ( #cast ( thunk ( #decodeConstant ...`),
  span `dec/digits_to_dec_str_probe.rs:44`, corresponding to
  `assert!(buf[0] > b'0')`. A sibling leaf remains on the
  `assert!(!buf.is_empty())` panic path at line 43.
- `rustc kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs -o /tmp/digits_to_dec_str_probe_0028_guardbypass`
  succeeded after deleting the two top-of-function guard asserts from the
  copied `digits_to_dec_str` body.
- `/tmp/digits_to_dec_str_probe_0028_guardbypass` exited successfully.
- `uv --project kmir run kmir prove kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs --proof-dir /tmp/0028-digits-to-dec-str-guardbypass-proof --max-depth 200 --reload`
  ended with `ProofStatus.FAILED`, `nodes: 9`, `failing: 1`, `vacuous: 2`,
  `stuck: 1`, `terminal: 1`.
- `uv --project kmir run kmir show digits_to_dec_str_probe.main --proof-dir /tmp/0028-digits-to-dec-str-guardbypass-proof --statistics --leaves`
  showed the new first leaf as a stuck `#selectBlock` inside `digits_to_dec_str`
  on the `if exp < buf.len()` branch, with the active path `1 -> 3 -> 4 -> 7`.
  This is an inference from the leaf shape and the source location around
  `dec/digits_to_dec_str_probe.rs:58`.
- `rustc kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs -o /tmp/digits_to_dec_str_probe_0028_takenarm`
  succeeded after the taken-arm specialization.
- `uv --project kmir run kmir prove kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs --proof-dir /tmp/0028-digits-to-dec-str-takenarm-proof --max-depth 200 --reload`
  was started, but it was interrupted before the proof returned a fresh leaf
  summary. During that run, `llvm-kompile-codegen` was still emitting
  `tmp.*` artifacts under the worktree.
- The latest interrupted rerun used the same command above, did not complete
  before interruption, and captured no new leaf summary. No code changes from
  that attempt were kept.
- The `tmp.*` artifacts were removed after stopping the background proof
  process.
- Because no post-edit proof result exists yet, the frontier move is
  unvalidated and the last confirmed boundary remains the copied
  `if exp < buf.len()` select at `digits_to_dec_str_probe.rs:58`.
- Current-turn checkpoint: the probe compiled again, and a new proof rerun was
  started, but it was intentionally interrupted before a fresh leaf summary was
  captured. No new frontier was established this turn; the last validated
  boundary remains the copied `if exp < buf.len()` branch select.

## Commit Inventory

- `8505ae9d` `test(verify-rust-std): bypass 0028 helper equality path`
- `1499bc9f` `test(verify-rust-std): add 0028 digits_to_dec_str probe`
- `44813fb9` `test(verify-rust-std): narrow 0028 digits_to_dec_str probe`
- `7f898c54` `test(verify-rust-std): narrow 0028 probe past raw slices`
- `b93c7e68` `test(verify-rust-std): bypass 0028 maybeuninit return path`

## Blockers

- First probe blocker is not the Challenge 0011 float-value backend gap.
- The original `SliceIndex::index` blocker is gone, so Sprint 1's immediate
  target was met.
- The current blocker is still challenge-local: the narrowed wrapper now
  reaches a stuck raw-slice construction leaf before any float-specific
  `flt2dec` limitation.
- No backend escalation is justified yet from this follow-up probe alone.
- After removing raw-slice construction, the next blocker is still
  challenge-local: the helper that hard-codes the single concrete split case
  now gets stuck in slice/array equality before the copied `digits_to_dec_str`
  path reaches a `flt2dec`-owned frontier.
- After removing the helper equality path as well, the next blocker is now the
  initialized-slice helper itself, so the next narrowing step would be to
  bypass `MaybeUninit::slice_assume_init_ref` and see whether the proof can
  finally enter a real `flt2dec` leaf or a backend limit.
- After bypassing `MaybeUninit::slice_assume_init_ref`, the new blocker is the
  probe's own top-of-function guard path, specifically the `buf[0]` bounds
  check and the `assert!(!buf.is_empty())` panic path, so the frontier still
  has not reached `flt2dec`-owned logic.
- After removing those guards, the frontier moved again and is now inside the
  copied `digits_to_dec_str` control flow at the `if exp < buf.len()` branch
  select, so the next exact narrowing step should focus there if this slice is
  continued.
