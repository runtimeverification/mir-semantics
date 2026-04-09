# Generator Record: Challenge 0012

Ownership:

- Generator owns this file and the implementation work for this challenge.
- Generator must not edit `evaluator.md` or `rubric.md`.
- Generator should treat planner and evaluator edits as authoritative inputs,
  not as files to rewrite.

## Inputs

- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0012-nonzero`
- Planner record: `docs/verify-rust-std/challenges/0012-nonzero/planner.md`
- Evaluator record: `docs/verify-rust-std/challenges/0012-nonzero/evaluator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0012-nonzero/rubric.md`

## Scope Boundary

- Authorized code area: this challenge branch only.
- Default repository scope: `runtimeverification/mir-semantics`
- Allowed secondary scope: `runtimeverification/stable-mir-json` when required
- Exceptional scope: `runtimeverification/haskell-backend` only with explicit
  justification logged here and in the evaluator record

## Work Log

- 2026-04-09: Ported the prerequisite semantic-fix slice from local branch
  `verify-rust-std/challenge-0012` via six ordered cherry-picks.
- 2026-04-09: Ran narrow collection and execution for the affected `prove-rs`
  regressions (`transmute-maybe-uninit-i128`, `unions`).
- 2026-04-09: Built local kdist definitions to satisfy integration-test
  fixture requirements before rerunning targeted proofs.
- 2026-04-09: Added the first challenge-local `0012-nonzero` artifacts for
  Part 1 semantics: `new`, `new_unchecked`, and `from_mut`.
- 2026-04-09: Added one low-risk Part 2 seed artifact (`count_ones`) with
  explicit semantic assertions.
- 2026-04-09: Ran direct `kmir prove-rs` checks on new challenge-local
  artifacts and collected concrete failing/stuck frontiers for follow-up.
- 2026-04-09: Reduced the Part 1 failure frontier beyond the symbolic
  transmute report by reproducing failures on concrete-input start symbols and
  isolating two cast-level obstructions (`castKindTransmute` and
  `castKindPtrToPtr`) inside `NonZero` APIs.
- 2026-04-09: Turned the untracked transparent-wrapper probe into a challenge-
  local comparison repro and reran the transmute slice against the exact
  `NonZero::new` shape (`u8 -> Option<NonZeroU8>`).

## Files Touched

- `kmir/src/kmir/kdist/mir-semantics/intrinsics.md`
- `kmir/src/kmir/kdist/mir-semantics/kmir.md`
- `kmir/src/kmir/kdist/mir-semantics/rt/data.md`
- `kmir/src/kmir/kdist/mir-semantics/rt/types.md`
- `kmir/src/tests/integration/data/prove-rs/show/transmute-maybe-uninit-i128.main.expected`
- `kmir/src/tests/integration/data/prove-rs/show/unions-fail.main.expected`
- `kmir/src/tests/integration/data/prove-rs/transmute-maybe-uninit-i128.rs`
- `kmir/src/tests/integration/data/prove-rs/unions.rs`
- `kmir/src/tests/integration/test_integration.py`
- `kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/README.md`
- `kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/new.rs`
- `kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/new_unchecked.rs`
- `kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/from_mut.rs`
- `kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/count_ones.rs`
- `kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/transmute_wrapper_u8.rs`
- `docs/verify-rust-std/challenges/0012-nonzero/generator.md`
- `docs/verify-rust-std/challenges/0012-nonzero/workpad.md`

## Validation Evidence

1. Command:
   `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_prove --collect-only -k "transmute-maybe-uninit-i128 or unions" -q`
   Result:
   selected exactly two tests:
   `test_prove[transmute-maybe-uninit-i128]` and `test_prove[unions]`.

2. Command:
   `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_prove -k "transmute-maybe-uninit-i128 or unions" -q`
   Result:
   failed at fixture setup because the local Haskell definition directory did
   not exist (`ValueError: Directory does not exist: ~/.cache/kdist-.../mir-semantics/haskell`).

3. Command:
   `make build`
   Result:
   succeeded; rebuilt `mir-semantics.haskell`, `mir-semantics.llvm`, and
   `mir-semantics.llvm-library`.

4. Command:
   `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_prove -k "transmute-maybe-uninit-i128 or unions" -q --maxfail=1`
   Result:
   `2 passed, 108 deselected in 122.64s`.

5. Command:
   `/home/zhaoji/.stable-mir-json/release.sh -Zno-codegen kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/new.rs`
   Result:
   compile succeeded.

6. Command:
   `/home/zhaoji/.stable-mir-json/release.sh -Zno-codegen kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/new_unchecked.rs`
   Result:
   compile succeeded.

7. Command:
   `/home/zhaoji/.stable-mir-json/release.sh -Zno-codegen kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/from_mut.rs`
   Result:
   compile succeeded.

8. Command:
   `/home/zhaoji/.stable-mir-json/release.sh -Zno-codegen kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/count_ones.rs`
   Result:
   compile succeeded after adding `#![feature(non_zero_count_ones)]` and
   adapting assertions to compare `NonZero<u32>::get()`.

9. Command:
   `timeout 180s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/new.rs --start-symbol part1_new_u8 --terminate-on-thunk --max-depth 200 --max-iterations 300 --proof-dir /tmp/kmir-0012-new-u8 --fail-fast`
   Result:
   `APRProof: new.part1_new_u8`, status `FAILED`, `failing: 1`.

10. Command:
    `timeout 180s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/new_unchecked.rs --start-symbol part1_new_unchecked_u8 --terminate-on-thunk --max-depth 200 --max-iterations 300 --proof-dir /tmp/kmir-0012-new-unchecked-u8 --fail-fast`
    Result:
    `APRProof: new_unchecked.part1_new_unchecked_u8`, status `FAILED`,
    `failing: 1`.

11. Command:
    `uv --project kmir run -- kmir show new.main --proof-dir /tmp/kmir-0012-new-main --leaves`
    Result:
    leaf frontier contains thunk at `std::num::NonZero::<u8>::new` transmute
    cast path.

12. Command:
    `timeout 180s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/new.rs --start-symbol part1_new_u8 --max-depth 200 --max-iterations 300 --proof-dir /tmp/kmir-0012-new-u8-no-terminate --fail-fast`
    Result:
    `APRProof: new.part1_new_u8`, status `FAILED`, with `pending: 6`,
    `failing: 1`, `stuck: 1`.

13. Command:
    `timeout 180s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/count_ones.rs --start-symbol part2_count_ones_u8 --max-depth 200 --max-iterations 300 --proof-dir /tmp/kmir-0012-count-ones-u8 --fail-fast`
    Result:
    `APRProof: count_ones.part2_count_ones_u8`, status `FAILED`, with
    `pending: 1`, `failing: 1`, `stuck: 1`.

14. Command:
    `timeout 240s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/new.rs --start-symbol part1_new_u8 --terminate-on-thunk --max-depth 200 --max-iterations 300 --proof-dir /tmp/kmir-0012-new-u8-frontier --fail-fast`
    Result:
    `APRProof: new.part1_new_u8`, status `FAILED`, `failing: 1`.

15. Command:
    `timeout 240s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/new.rs --start-symbol main --terminate-on-thunk --max-depth 200 --max-iterations 300 --proof-dir /tmp/kmir-0012-new-main-frontier --fail-fast`
    Result:
    `APRProof: new.main`, status `FAILED` even with concrete input path.
    `kmir show` leaf confirms thunk at
    `#cast ( Integer ( 1 , 8 , false ) , castKindTransmute , ... )` in
    `std::num::NonZero::<u8>::new`.

16. Command:
    `timeout 240s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/from_mut.rs --start-symbol main --terminate-on-thunk --max-depth 200 --max-iterations 300 --proof-dir /tmp/kmir-0012-from-mut-main-frontier --fail-fast`
    Result:
    `APRProof: from_mut.main`, status `FAILED`.
    `kmir show` leaf confirms thunk at
    `#cast ( PtrLocal ... , castKindPtrToPtr , ... )` in
    `std::num::NonZero::<u8>::from_mut`.

17. Command:
    `/home/zhaoji/.stable-mir-json/release.sh -Zno-codegen kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/transmute_wrapper_u8.rs`
    Result:
    compile succeeded for the narrowed transmute repro.

18. Command:
    `timeout 240s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/transmute_wrapper_u8.rs --start-symbol part1_transmute_wrapper_u8 --terminate-on-thunk --max-depth 200 --max-iterations 300 --proof-dir /tmp/kmir-0012-transmute-wrapper-u8-wrapper-final --fail-fast`
    Result:
    `APRProof: transmute_wrapper_u8.part1_transmute_wrapper_u8`, status
    `PASSED`. A same-size `u8 -> #[repr(transparent)] WrapU8` transmute closes
    under current semantics.

19. Command:
    `timeout 240s uv --project kmir run -- kmir prove-rs kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/transmute_wrapper_u8.rs --start-symbol part1_transmute_option_nonzero_u8 --terminate-on-thunk --max-depth 200 --max-iterations 300 --proof-dir /tmp/kmir-0012-transmute-wrapper-u8-option-nonzero --fail-fast`
    Result:
    `APRProof: transmute_wrapper_u8.part1_transmute_option_nonzero_u8`, status
    `FAILED`, `failing: 1`.

20. Command:
    `uv --project kmir run -- kmir show transmute_wrapper_u8.part1_transmute_option_nonzero_u8 --proof-dir /tmp/kmir-0012-transmute-wrapper-u8-option-nonzero --leaves`
    Result:
    leaf frontier is a thunk at
    `#cast ( Integer ( 1 , 8 , false ) , castKindTransmute , ... )` in
    `part1_transmute_option_nonzero_u8`, which matches the concrete
    integer-to-niche transmute shape used by `std::num::NonZero::<u8>::new`.

## Commit Inventory

- `a52729d7` — `fix(transmute): accept MaybeUninit reinterpretation`
- `a681af49` — `fix(unions): reinterpret payload on field reads`
- `4a8cdb0a` — `test(unions): rename passing union regression`
- `3c4138db` — `fix(intrinsics): prioritize assert_inhabited failure`
- `2d5916d6` — `fix(pointer-casts): support array-to-wrapper projections`
- `01416c6d` — `fix(pointer-casts): preserve wrapper projections for iterators`
- `d87eb4dc` — `test(verify-rust-std): add 0012 nonzero transmute probe`

## Blockers

- No external/tooling blocker was found in this frontier-reduction slice.
- Remaining work for Challenge 0012 is narrowed to cast semantics used by Part 1
  `NonZero` APIs:
  - Integer-to-wrapper transmute cast in `NonZero::new`
  - Wrapper pointer cast in `NonZero::from_mut`
- Current evidence shows these frontiers persist even on concrete-input `main`
  starts, so this is not only a symbolic-branching artifact.
- This slice sharpened the `NonZero::new` blocker further:
  - same-size `u8 -> #[repr(transparent)] WrapU8` transmute already passes
  - the exact `NonZero::new` shape (`u8 -> Option<NonZeroU8>`) still fails on
    `castKindTransmute`
  - therefore the generic same-size transmute story is not sufficient on this
    branch; the remaining blocker is specifically integer-to-niche / NonZero
    transmute semantics, not plain transparent-wrapper support
