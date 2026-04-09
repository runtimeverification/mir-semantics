# Execution Plan: Challenge 0012

## Objective

Turn the reviewed public NonZero baseline into a branch-local implementation that is strong enough for direct submission review.

## Next Generator Task

Close the concrete `castKindTransmute` frontier in `NonZero::new` by turning the existing transparent-wrapper probe into the smallest challenge-local transmute reproduction, then use that evidence to decide whether the same-size contract is sufficient for Part 1.

## Task Breakdown

1. Reproduce the `NonZero::new` transmute path with the checked transparent-wrapper probe shape in `kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/transmute_wrapper_u8.rs`.
2. Determine whether the frontier is closed by the existing same-size contract story or whether the proof still needs a narrower semantic blocker record.
3. Leave the `castKindPtrToPtr` `NonZero::from_mut` frontier and the broader Part 2 API matrix for the next slice after the transmute path is understood.

## Evidence The Evaluator Needs

- A precise note of the `NonZero::new` frontier that was targeted.
- A clear statement of how the transparent-wrapper probe changes the next-step choice.
- Proof or test commands only for the narrowed frontier slice.
- A blocker note if same-size transmute contracts are still not enough.

## Current Risk

The main risk is not missing coverage but insufficiently strong specifications. The prior public review already flagged thin harnesses, and the current frontier is still a cast-semantics failure, so the generator should isolate that cast before spending effort on the wider API matrix.
