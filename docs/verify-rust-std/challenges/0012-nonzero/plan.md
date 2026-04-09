# Execution Plan: Challenge 0012

## Objective

Turn the reviewed public NonZero baseline into a branch-local implementation that is strong enough for direct submission review.

## Next Generator Task

Close the concrete `castKindTransmute` frontier in `NonZero::new` by treating the transparent-wrapper probe as the passing control and then isolating the exact `u8 -> Option<NonZeroU8>` niche-cast shape that still fails. Use that one slice to decide whether the remaining blocker is a precise niche-cast semantic gap or a recordable proof frontier.

## Task Breakdown

1. Reproduce the `NonZero::new` transmute path with the checked transparent-wrapper probe shape in `kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/transmute_wrapper_u8.rs`.
2. Isolate the exact `u8 -> Option<NonZeroU8>` reproduction and determine whether it still fails on `castKindTransmute` after the transparent-wrapper control passes.
3. If the exact niche-cast still fails, record the blocker precisely and leave the `castKindPtrToPtr` `NonZero::from_mut` frontier and the broader Part 2 API matrix for a later slice.

## Evidence The Evaluator Needs

- A precise note of the `NonZero::new` frontier that was targeted.
- A clear statement that the transparent-wrapper probe now serves as the passing control, while the exact `Option<NonZeroU8>` cast remains the frontier.
- Proof or test commands only for the narrowed frontier slice.
- A blocker note if the exact niche-cast still fails even after the same-size wrapper control passes.

## Current Risk

The main risk is not missing coverage but spending effort on the wrong frontier. The prior public review already flagged thin harnesses, and the current evidence shows plain same-size transmute support is already available, so the generator should isolate the exact niche-cast before spending effort on the wider API matrix.
