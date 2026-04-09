# Execution Plan: Challenge 0012

## Objective

Turn the reviewed public NonZero baseline into a branch-local implementation that is strong enough for direct submission review.

## Next Generator Task

Rebuild the Challenge 12 harness matrix from the public `verify-rust-std` solutions and tighten every remaining weak spot so each API has an explicit semantic assertion, not just a nonzero check.

## Task Breakdown

1. Rehydrate the reviewed public baseline from PR `#544` and PR `#565`.
2. Map every published `NonZero` API to a concrete harness or contract in `library/core/src/num/nonzero.rs`, including the `max` / `min` / `clamp` trio and the signed-only / unsigned-only cases.
3. Add the smallest supporting `core` annotations needed to make the proofs go through, especially if `checked_pow` or related helpers still need invariant help.
4. Keep any wide-type or bounded proof strategy explicit in the artifact text so the evaluator can separate acceptable bounds from missing coverage.

## Evidence The Evaluator Needs

- A file-to-function coverage map for the published API list.
- Proof or test commands for the full harness set.
- A note for any intentionally bounded case, including why the bound is acceptable.
- A clear record of any core annotations added only to support verification.

## Current Risk

The main risk is not missing coverage but insufficiently strong specifications. The prior public review already flagged thin harnesses, so the generator should prove semantic properties directly wherever the API allows it.

