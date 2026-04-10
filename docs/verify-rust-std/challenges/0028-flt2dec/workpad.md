# Workpad: Challenge 0028

## Current handoff state

- Branch: `verify-rust-std/reexec-0028-flt2dec`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0028-flt2dec`
- Status at planner handoff: the challenge-local minimal reproducer is the copied `digits_to_dec_str_probe.rs` frontier, and the branch-local evidence is now being audited against `docs/verify-rust-std/challenges/0028-flt2dec/success_criteria.md`.
- Current checkpoint: the restored-prefix rerun keeps `&buf[..exp]` in place, the suffix stub remains narrow, and the exact frontier is now the underlying `core::slice::index` leaf `<std::ops::Range<usize> as std::slice::SliceIndex<[u8]>>::index` at `library/core/src/slice/index.rs:440`.
- Replay confirmation from `/tmp/0028-digits-to-dec-str-minslice-proof`: `uv --project kmir run kmir show digits_to_dec_str_probe.main --proof-dir /tmp/0028-digits-to-dec-str-minslice-proof --statistics --leaves` still reports the same leaf at `<std::ops::Range<usize> as std::slice::SliceIndex<[u8]>>::index` (`library/core/src/slice/index.rs:440`), so the current reproducer is already the smallest evidence-bearing frontier for now.
- The saved-proof audit for the unchanged taken-arm specialization reaches the terminal target leaf `#EndProgram ~> .K` via `/tmp/0028-digits-to-dec-str-current-proof`.
- The current branch evidence is still challenge-local rather than module-wide: the proof at `/tmp/0028-digits-to-dec-str-prefixslice-step2-proof` ends with `ProofStatus.FAILED`, `nodes: 10`, `failing: 3`, `vacuous: 0`, `stuck: 3`, `terminal: 1`, and the frontier has moved into the underlying `core::slice::index` path at `<std::ops::Range<usize> as std::slice::SliceIndex<[u8]>>::index` (`library/core/src/slice/index.rs:440`) after concretizing the copied branch test.
- The branch-local discoverability check now replays that same probe with `kmir.prove_program` and asserts the proof still fails at the copied frontier instead of only checking for file presence.
- After concretizing the copied branch test for `b"1234", exp = 2`, the replay now fails in the underlying `core::slice::index` path at `<std::ops::Range<usize> as std::slice::SliceIndex<[u8]>>::index` (`library/core/src/slice/index.rs:440`) instead of at the copied branch select itself.

## Evidence gathered

- The published challenge goal is to verify `core::num::flt2dec`, the float-to-decimal conversion module.
- The published success criteria are captured in `docs/verify-rust-std/challenges/0028-flt2dec/success_criteria.md`, which lists the safe entry points `digits_to_dec_str`, `digits_to_exp_str`, `to_shortest_str`, `to_shortest_exp_str`, `to_exact_exp_str`, `to_exact_fixed_str`, and the `grisu` and `dragon` strategy wrappers `format_shortest_opt`, `format_shortest`, `format_exact_opt`, and `format_exact`.
- The challenge also requires the standard UB exclusions: no dangling or misaligned memory access, no compiler-intrinsic UB, no mutation of immutable bytes, and no invalid values.
- Challenge 0011 records the reusable float warning: the float-sensitive path previously stalled on missing KMIR / haskell-backend float-value support, so any new probe should determine whether 0028 hits the same boundary or a different artifact issue.
- The 0028 artifact directory now contains a first probe harness:
  `kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs`.
- The published challenge function list is now captured in
  `docs/verify-rust-std/challenges/0028-flt2dec/success_criteria.md`.
- Because `digits_to_dec_str` is private inside `core::num::flt2dec`, the
  first probe had to copy only that function body into a challenge-local
  wrapper rather than call the std item directly from an external crate.
- The first compile/setup issues were both artifact-level:
  `std::num::fmt::Part` was unavailable outside `cfg(test)`, and this worktree
  lacked the compiled K definition cache until `make build` was run.
- After clearing those setup issues, the first concrete proof failure was a
  stuck leaf in slice indexing, not a float builtins crash:
  `<std::ops::Range<usize> as std::slice::SliceIndex<[u8]>>::index`
  at `library/core/src/slice/index.rs:440`, stuck on
  `thunk ( #applyBinOp ( binOpOffset , ... ) )`.
- This first result is therefore distinct from Challenge 0011: it did not
  reproduce the earlier float-value/backend gap.
- A follow-up rerun on this branch replaced the copied function's
  `&buf[..exp]` / `&buf[exp..]` path with a raw helper `split_at_raw`, and
  removed result indexing from `main`, so the probe no longer depends on the
  old `Range<usize>::index` route.
- The narrower rerun still did not reach a `flt2dec`-owned boundary. Its first
  new stuck leaf is `std::slice::from_raw_parts::<'_, u8>` at
  `library/core/src/slice/raw.rs:138`, reached from `split_at_raw` at
  `dec/digits_to_dec_str_probe.rs:9`.
- This slice removed both `split_at_raw` and `std::slice::from_raw_parts` from
  the narrowed probe path by replacing the decimal-point split with a single
  concrete-case helper for `b"1234", exp = 2` and by switching the initialized
  parts return path to `MaybeUninit::slice_assume_init_ref`.
- The probe needed one local setup adjustment after that change:
  `MaybeUninit::slice_assume_init_ref` is still feature-gated on this nightly,
  so the challenge-local crate now declares `#![feature(maybe_uninit_slice)]`.
- The newest rerun still does not reach a `flt2dec`-owned boundary or a float
  backend limit. Its first new stuck leaf is
  `std::array::equality::<impl std::cmp::PartialEq<[u8; 4]> for [u8]>::eq` at
  `/library/core/src/slice/mod.rs:871`, reached from the helper assertion
  `buf == b"1234"` inside `probe_decimal_point_case`.
- The current evidence therefore says the next boundary remains harness-level,
  but it has moved past raw-slice construction to the helper's concrete-case
  equality check.
- The next rerun removed that helper equality path entirely. The probe now
  compiles cleanly and the proof no longer stops in the helper assertion; the
  new first leaf is
  `std::mem::MaybeUninit::<core::num::fmt::Part<'_>>::slice_assume_init_ref`
  at `core/src/mem/maybe_uninit.rs:987`, reached from the copied
  `digits_to_dec_str` body in `dec/digits_to_dec_str_probe.rs:41`.
- This is still harness-side rather than `flt2dec`-owned behavior, but it is a
  more informative frontier than the removed array/slice equality path.

## Planning decisions

- Keep the first generator task to one representative probe instead of the full function list.
- Favor `digits_to_dec_str` as the initial signal source, but strip raw-slice
  construction so the evaluator can classify backend support versus harness
  artifact cleanly.
- Do not expand scope into backend work unless the follow-up probe shows a distinct, challenge-local float limitation.

## Reusable rubric patterns for evaluator

- Every published success criterion needs a concrete artifact or an explicit blocker, not a generic status note.
- A float-related blocker should name the exact missing capability.
- The evaluator should distinguish a narrow external dependency from a structural missing implementation.

## Failed-attempt log

- Initial plain compile of the probe failed while importing
  `std::num::fmt::Part`; the harness was adjusted to use
  `core::num::fmt::Part` and `extern crate core;`.
- Initial `kmir prove` failed before proving anything because
  `/home/zhaoji/.cache/kdist-d250b97/mir-semantics/haskell` did not exist.
  Running `make build` resolved that branch-local prerequisite.
- A capped probe run with `--max-iterations 3` stopped at `ProofStatus.PENDING`
  and was discarded as a driver-limit artifact rather than the first semantic result.
- The narrowed follow-up rerun bypassed `SliceIndex::index`, but then failed in
  `std::slice::from_raw_parts::<'_, u8>` from the challenge-local
  `split_at_raw` helper, so it still does not expose a real `flt2dec`
  frontier.
- The raw-slice-removal rerun bypassed `std::slice::from_raw_parts`, but the
  concrete-case helper now fails earlier in
  `std::array::equality::<impl std::cmp::PartialEq<[u8; 4]> for [u8]>::eq`,
  so the path is still stuck in challenge scaffolding.
- The equality-free rerun now reaches
  `std::mem::MaybeUninit::<core::num::fmt::Part<'_>>::slice_assume_init_ref`
  at `core/src/mem/maybe_uninit.rs:987` instead of the helper assertion, so
  the remaining blocker is now the initialized-slice conversion itself rather
  than the concrete-case probe wrapper.
- The next rerun replaced that return conversion with a challenge-local static
  slice helper. The proof moved again, but the first concrete leaf is now the
  `buf[0]` bounds check inserted by `assert!(buf[0] > b'0')` at
  `dec/digits_to_dec_str_probe.rs:44`, with a sibling leaf on the
  `assert!(!buf.is_empty())` panic path at line 43.

- The guard-bypass rerun removed those top-of-function asserts from the active
  path and compiled/runs cleanly:
  `rustc kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs -o /tmp/digits_to_dec_str_probe_0028_guardbypass`
  followed by `/tmp/digits_to_dec_str_probe_0028_guardbypass`.
- The corresponding proof command:
  `uv --project kmir run kmir prove kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs --proof-dir /tmp/0028-digits-to-dec-str-guardbypass-proof --max-depth 200 --reload`
  finished with `ProofStatus.FAILED`, `nodes: 9`, `failing: 1`, `vacuous: 2`,
  `stuck: 1`, `terminal: 1`.
- The first leaf in `uv --project kmir run kmir show digits_to_dec_str_probe.main --proof-dir /tmp/0028-digits-to-dec-str-guardbypass-proof --statistics --leaves`
  is a stuck `#selectBlock` inside `digits_to_dec_str` on the `if exp < buf.len()`
  branch. This is the next exact frontier after the probe-local guard checks
  were bypassed.
- The taken-arm specialization keeps the same concrete case but removes that
  branch select from the active path. The proof rerun did not finish before the
  turn was interrupted, so the exact post-edit leaf is still unknown.
- Restoring the real prefix slice `&buf[..exp]` is enough to break the saved
  terminal slice. The first new concrete leaf is not inside slice indexing yet;
  it is the copied `if exp >= buf.len()` select itself at line 76.

## Next handoff

- Generator has now completed the `MaybeUninit::slice_assume_init_ref`
  bypass slice and rerun it.
- Evaluator can classify the new outcome against concrete evidence:
  `split_at_raw` / `from_raw_parts` are gone from the active path, the helper
  equality path is gone as well, and the current blocker is now the probe's
  own guard path rather than the old `MaybeUninit` return conversion.
- The next exact narrowing step, if continued, is to focus on the copied
  `digits_to_dec_str` branch select at `if exp >= buf.len()` rather than
  reopening the already-bypassed wrapper preconditions.
- The next generator decision is to preserve this reproducer as the current
  minimum unless a smaller replay can keep the same post-select path while
  moving the first leaf past `core::slice::index`.
- Current-turn checkpoint: the probe compiled again, but the follow-up proof
  rerun was interrupted before a new leaf summary was captured. No new frontier
  was introduced, and the last established boundary remains the copied
  `if exp < buf.len()` select at `dec/digits_to_dec_str_probe.rs:58`.
- Current-turn checkpoint update: the branch-specializing rewrite is now in
  place, but the interrupted proof rerun means the smallest exact blocker is
  still the unvalidated post-edit frontier, not a newly recorded leaf.
- Latest interrupted rerun: `uv --project kmir run kmir prove kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs --proof-dir /tmp/0028-digits-to-dec-str-takenarm-proof --max-depth 200 --reload` did not complete before interruption, no new leaf was captured, and no code changes were kept from that attempt.
- The last confirmed blocker remains the copied `if exp < buf.len()` `#selectBlock` at `digits_to_dec_str_probe.rs:58`.
- Current-turn checkpoint: `uv --project kmir run kmir prove kmir/src/tests/integration/data/verify-rust-std/0028-flt2dec/digits_to_dec_str_probe.rs --proof-dir /tmp/0028-digits-to-dec-str-takenarm-proof2 --max-depth 200 --reload` was launched again on the taken-arm specialization, but it was interrupted before a fresh leaf or boundary was reported.
- Because no post-edit leaf was captured this turn, the frontier did not move; the smallest exact blocker is still the copied `if exp < buf.len()` select in `digits_to_dec_str_probe.rs:58`.
- Audit note: this turn recorded only the interrupted taken-arm rerun above; there is no fresh proof leaf to promote, so the work remains checkpointed at the same copied branch select.
- Saved-proof audit: `uv --project /home/zhaoji/projs/mir-semantics-vrs/challenges/0028-flt2dec/kmir run kmir show digits_to_dec_str_probe.main --proof-dir /tmp/0028-digits-to-dec-str-current-proof --statistics --leaves` now reaches the terminal target leaf `#EndProgram ~> .K` on path `1 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 2`. No source changes were made in that turn; this note records the proof-artifact success for branch-local auditing only.
- Current frontier update: with the restored real prefix slice, the first exact
  boundary is now the stuck `if exp >= buf.len()` `#selectBlock` at
  `dec/digits_to_dec_str_probe.rs:76`, not the older taken-arm terminal slice.
- The next exact narrowing step is to keep the real `&buf[..exp]` restoration
  in place and determine why `buf.len()` no longer simplifies to the concrete
  `4` at that branch test before restoring additional decimal-point operations.
