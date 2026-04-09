# Workpad: Challenge 0012

## Decision Log

- 2026-04-09 UTC: This narrowed slice ends as a blocker checkpoint, not a
  semantic fix. Two minimal `castKindTransmute` matcher attempts were
  recompiled and rerun, but the exact `u8 -> Option<NonZeroU8>` repro stayed on
  the identical top-level thunk.
- 2026-04-09 UTC: Chosen as the next active batch candidate because the public solution history is rich and the review feedback already points to the exact weakness to fix.
- 2026-04-09 UTC: The branch-local planning target is to convert the public NonZero baseline into a stricter semantic proof set, not to invent a new proof strategy.
- 2026-04-09 UTC: The next delegated slice is narrowed to the `NonZero::new` `castKindTransmute` frontier, with the untracked transparent-wrapper probe as the smallest evidence-bearing reproduction.
- 2026-04-09 UTC: The transparent-wrapper probe was refined into a two-point repro: a passing `u8 -> #[repr(transparent)] WrapU8` control and a failing exact `NonZero::new`-shape `u8 -> Option<NonZeroU8>` transmute.
- 2026-04-09 UTC: Evaluator verdict remains `IN PROGRESS`; the wrapper control passes, but the exact `u8 -> Option<NonZeroU8>` transmute still fails on `castKindTransmute`, so this is still a semantic frontier rather than submission-ready evidence.
- 2026-04-09 UTC: The next technical slice should not spend more time on generic same-size transmute support, because that is already closed by the wrapper control; it should isolate the exact niche-cast semantics in `NonZero::new` and stop if that exact shape still fails.

## Evidence Collected

- Branch-local SMIR JSON for `transmute_wrapper_u8.rs` confirms that
  `Option<NonZeroU8>` is a one-byte niche enum: zero encodes `None`, and
  `Some(NonZeroU8)` reuses the same one-byte scalar payload with nonzero valid
  range.
- Recompiling after two minimal `rt/data.md` matcher attempts did not change
  the exact proof leaf: `part1_transmute_option_nonzero_u8` still terminates at
  `#cast ( Integer ( 1 , 8 , false ) , castKindTransmute , ty ( 9 ) , ty ( 27 ) )`.
- This strengthens the blocker: the remaining issue is not just recognizing the
  niche layout at the JSON level. Either the runtime type shape visible to
  `lookupTy(TY_TO)` differs from the SMIR structure in a way the current matcher
  does not observe, or this cast needs a lower-level byte/layout-driven path.
- Upstream challenge page confirms the goal, the Part 1 correctness requirements, the full Part 2 API list, and the UB obligations.
- PR `#565` review feedback says the prior solution is "a solid first submission" but still too thin because most Part 2 harnesses only prove non-UB.
- PR `#544` review feedback points out that `isqrt` coverage is incomplete unless wider unsigned types are added or a bound/rationale is documented.
- The current branch frontier is concrete, not abstract: `NonZero::new` still fails on `castKindTransmute`, and `NonZero::from_mut` still fails separately on `castKindPtrToPtr`.
- The untracked probe `kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/transmute_wrapper_u8.rs` shows a minimal `#[repr(transparent)]` wrapper transmute from `u8` to a newtype, which is the closest local shape to the `NonZero::new` frontier and therefore the best next step for isolating the cast semantics.
- Rust's checked-in `core::num::nonzero.rs` source for the active toolchain confirms that `NonZero::new` is implemented as `unsafe { intrinsics::transmute_unchecked(n) }` returning `Option<Self>`, so the exact reduced target shape is `u8 -> Option<NonZeroU8>`, not just `u8 -> NonZeroU8`.
- Branch-local proof evidence now distinguishes two cases on concrete input `1u8`:
  - `u8 -> #[repr(transparent)] WrapU8` passes.
  - `u8 -> Option<NonZeroU8>` fails at `castKindTransmute`.

## Reuse Candidates

- Public solution PR `#544` is the best baseline for harness shape and coverage matrix.
- Public solution PR `#565` is the best baseline for the narrower Part 1 / Part 2 framing and for the review-driven readiness criteria.
- Small core-side verification helpers, if needed, should stay limited to `uint_macros.rs` and `int_macros.rs`.
- The transparent-wrapper probe is now the strongest local control, because it already passes and lets us separate generic same-size transmute support from the exact niche-cast semantics used by `NonZero::new`.

## Handoff To Generator

- Keep `kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/transmute_wrapper_u8.rs` as the passing control.
- Make the next challenge-local slice a minimal `NonZero::new` niche-cast reproduction that targets only the exact `u8 -> Option<NonZeroU8>` failure on `castKindTransmute`.
- If that exact shape still fails, write down the blocker precisely and do not widen to the Part 2 matrix or the `from_mut` pointer-cast frontier.

## Handoff To Evaluator

- Score semantic specificity separately from coverage.
- Require explicit evidence for any omitted wide-type case or bounded proof case.
- Treat any unsupported backend escalation as a last resort, not as the default path.

## Generator Retry Execution Log

- Ported six prerequisite semantic-fix commits from
  `verify-rust-std/challenge-0012` in chronological order:
  `01578d44`, `bb4813b2`, `22fd4eec`, `6f1c072a`, `9b55225b`, `8347764a`.
- Port included transmute reinterpretation handling, unions payload read fixes,
  union regression rename updates, `assert_inhabited` failure prioritization,
  and pointer-cast projection preservation updates.
- Narrow collection confirmed the expected affected tests:
  `test_prove[transmute-maybe-uninit-i128]` and `test_prove[unions]`.
- Initial targeted execution failed due to missing local compiled definitions.
  Ran `make build` and reran the same targeted tests successfully.

## Validation Snapshot

- `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_prove --collect-only -k "transmute-maybe-uninit-i128 or unions" -q`
  - Outcome: `2/110` selected, exact target tests collected.
- `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_prove -k "transmute-maybe-uninit-i128 or unions" -q`
  - Outcome: fixture setup error due to missing
    `~/.cache/kdist-.../mir-semantics/haskell`.
- `make build`
  - Outcome: success; required definitions rebuilt.
- `uv --project kmir run -- pytest kmir/src/tests/integration/test_integration.py::test_prove -k "transmute-maybe-uninit-i128 or unions" -q --maxfail=1`
  - Outcome: `2 passed, 108 deselected in 122.64s`.

## Remaining Gap After This Slice

- The prerequisite semantic/test slice now appears healthy and validated, but
  Challenge 0012 still lacks challenge-specific `NonZero` harness and contract
  artifacts on this re-execution branch.
- Evaluator should keep status at `IN PROGRESS` until branch-local NonZero
  verification work is implemented and validated.

## Generator Next Slice Execution Log

- Added first challenge-local `0012-nonzero` artifacts:
  `new.rs`, `new_unchecked.rs`, `from_mut.rs`.
- Added one low-risk Part 2 seed artifact:
  `count_ones.rs` (explicit semantic assertions on returned count value).
- Updated challenge-local artifact README status board to reflect active
  planner/generator/evaluator and initial artifact coverage.

## New Validation Snapshot

- Compile checks (stable-mir-json release driver):
  - `new.rs`: success
  - `new_unchecked.rs`: success
  - `from_mut.rs`: success
  - `count_ones.rs`: initial compile failed due unstable
    `non_zero_count_ones` and type mismatch; succeeded after adding feature
    gate and using `.get()` for comparisons.
- Proof checks (direct `kmir prove-rs`):
  - `new.part1_new_u8` with `--terminate-on-thunk`: `FAILED` (`failing: 1`)
  - `new_unchecked.part1_new_unchecked_u8` with `--terminate-on-thunk`:
    `FAILED` (`failing: 1`)
  - `new.part1_new_u8` without `--terminate-on-thunk`: `FAILED` with
    `pending: 6`, `failing: 1`, `stuck: 1`
  - `count_ones.part2_count_ones_u8`: `FAILED` with
    `pending: 1`, `failing: 1`, `stuck: 1`
- Leaf inspection:
  - `kmir show new.main --proof-dir /tmp/kmir-0012-new-main --leaves` shows a
    thunk frontier at `std::num::NonZero::<u8>::new` transmute cast path.

## Updated Remaining Gap

- Challenge-local artifacts now exist, but none of the new symbolic proofs are
  closing yet under current semantics.
- Next highest-value step is to reduce the concrete `NonZero::new`
  transmute frontier to a minimal wrapper-reproduction slice and either:
  - close it with the existing same-size contract story, or
  - record the exact blocker if the frontier still survives.

## Frontier Reduction Slice (Part 1)

- Reproduced `new.part1_new_u8` failure with a fresh proof directory:
  `/tmp/kmir-0012-new-u8-frontier`.
- Ran `new.main` (concrete argument path) and confirmed it still fails, then
  inspected leaves:
  thunk at `#cast ( Integer ( 1 , 8 , false ) , castKindTransmute , ... )` in
  `std::num::NonZero::<u8>::new`.
- Ran `from_mut.main` and confirmed independent failure frontier:
  thunk at `#cast ( PtrLocal ... , castKindPtrToPtr , ... )` in
  `std::num::NonZero::<u8>::from_mut`.

## Frontier Reduction Outcome

- This slice did not produce a passing Part 1 proof.
- It did reduce the blocker beyond the previous generic
  `NonZero::new transmute/thunk` report:
  - `new` fails even for concrete constant input (`1`), so the issue is not
    only symbolic branching.
  - `from_mut` reveals a second cast-level frontier (`castKindPtrToPtr`) tied
    to NonZero wrapper pointer conversion.
- Next action should target the `NonZero::new` cast frontier with the
  transparent-wrapper probe shape first; that is the highest-leverage slice
  because it is the closest local reproduction of the failing transmute path
  and it keeps the separate pointer-cast frontier out of scope for now.

## Transparent-Wrapper Probe Outcome

- Compile check for `transmute_wrapper_u8.rs` succeeded.
- `part1_transmute_wrapper_u8` passes under `kmir prove-rs`, so the current
  semantics already support a plain same-size transparent-wrapper transmute.
- `part1_transmute_option_nonzero_u8` fails under `kmir prove-rs` on a concrete
  `#cast ( Integer ( 1 , 8 , false ) , castKindTransmute , ... )` leaf.
- This means the frontier moved materially:
  - the blocker is no longer "same-size transmute support in general"
  - the blocker is now the exact integer-to-`Option<NonZero<T>>` niche cast
    shape used by `NonZero::new`
- Decision for Part 1 after this slice:
  - the challenge-page same-size contract story is already validated by the
    wrapper control, so it is not the next question
  - Part 1 remains blocked on the precise `castKindTransmute` niche-cast
    semantics for `NonZero::new`

## Final Checkpoint For This Slice

- The control still passes:
  `u8 -> #[repr(transparent)] WrapU8`.
- The exact target still fails unchanged:
  `u8 -> Option<NonZeroU8>` stays on the same top-level `castKindTransmute`
  thunk after recompilation.
- Finish condition for this slice:
  - experimental runtime edit reverted
  - docs updated with the precise blocker
  - no widening to `from_mut` or Part 2
