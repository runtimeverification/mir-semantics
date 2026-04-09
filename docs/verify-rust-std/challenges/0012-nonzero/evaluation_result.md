# Evaluation Result: Challenge 0012

Checkpoint date: 2026-04-09 UTC

This evaluation pass counts the prerequisite semantic baseline, the first
branch-local `NonZero` artifacts, and the transparent-wrapper control as real
progress, but it does not count as challenge completion because the exact
`u8 -> Option<NonZeroU8>` niche-cast repro still fails on the same top-level
`castKindTransmute` frontier.

## Verdict

`BLOCKED`

## Score

`2.0 / 3`

## Satisfied Criteria

- Dedicated branch, worktree, and draft PR exist.
- The branch now contains a validated prerequisite semantic baseline ported from
  `verify-rust-std/challenge-0012`.
- Branch-local `NonZero` artifacts now exist for `new`, `new_unchecked`,
  `from_mut`, and `count_ones`.
- The prerequisite slice was rerun with concrete evidence:
  `transmute-maybe-uninit-i128` and `unions` collected, built, and passed.
- Compile checks for the new `NonZero` artifacts succeeded.
- The new `NonZero` proof attempts are reproducible and fail on explicit branch
  frontiers rather than missing setup.
- The Part 1 frontier has been narrowed from a generic transmute report to
  concrete cast semantics in `NonZero::new` and `NonZero::from_mut`.
- The transparent-wrapper probe now separates generic same-size transmute
  support from the exact `u8 -> Option<NonZeroU8>` niche-cast shape used by
  `NonZero::new`.
- The transparent-wrapper control passes, confirming that generic same-size
  transmute support is already available on this branch.
- Branch-local docs now distinguish prerequisite baseline progress from actual
  Challenge 12 work.

## Missing Criteria

- No passing proof exists yet for `NonZero::new`, `NonZero::new_unchecked`, or
  `NonZero::from_mut`.
- No passing proof exists yet for the Part 2 `NonZero` API seed.
- The Part 2 API matrix is still mostly absent.
- No branch-local coverage map exists for the `isqrt` wide-type question or any
  bounded `128-bit` proof strategy.
- No scoped `nonzero` proof/test run has passed end-to-end.
- The exact `NonZero::new` niche-cast reproduction still fails on
  `castKindTransmute`, even though the transparent-wrapper control passes.
- The exact `u8 -> Option<NonZeroU8>` transmute remains the current blocker.

## Blocking Issues

- The exact `u8 -> Option<NonZeroU8>` niche-cast path still terminates at the
  same top-level `castKindTransmute` thunk after the transparent-wrapper
  control passed, so the remaining gap is now a precise semantic blocker rather
  than missing setup.
- Next action: deeper runtime/semantic investigation of the niche-cast path in
  `NonZero::new`, then rerun the narrow Part 1 slice and reassess whether the
  blocker closes or needs to be carried forward as a documented limitation.

## Evidence

- Branch head `5555ddba` records the latest niche-blocker checkpoint on top of
  the prerequisite baseline, and `generator.md` / `workpad.md` record the
  precise `castKindTransmute` frontier together with the passing transparent-
  wrapper control.
- `generator.md` records compile success for `new.rs`, `new_unchecked.rs`,
  `from_mut.rs`, and `count_ones.rs`.
- `generator.md` also records direct proof frontiers:
  `new.part1_new_u8` fails at the `NonZero::new` transmute path,
  `new_unchecked.part1_new_unchecked_u8` fails, and
  `from_mut.main` fails at `castKindPtrToPtr`, while
  `count_ones.part2_count_ones_u8` fails.
- `generator.md` and `workpad.md` now record the transparent-wrapper control:
  `u8 -> #[repr(transparent)] WrapU8` passes, while the exact
  `u8 -> Option<NonZeroU8>` repro still fails on the same `castKindTransmute`
  leaf.
- `workpad.md` records the review-driven distinction between baseline readiness
  and challenge-specific `NonZero` work.
- The latest workpad checkpoint records two reverted minimal matcher attempts
  against the same leaf, which confirms the blocker is stable rather than a
  transient harness issue.

## Next Action Required To Improve State

- Investigate the exact `u8 -> Option<NonZeroU8>` niche-cast semantics in
  `NonZero::new`, then rerun the narrow Part 1 slice and decide whether the
  blocker can be closed or must remain documented.
