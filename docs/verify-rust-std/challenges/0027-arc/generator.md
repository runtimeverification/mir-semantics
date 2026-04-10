# Generator Record: Challenge 0027

Ownership:

- Generator owns this file and the implementation work for this challenge.
- Generator must not edit `evaluator.md` or `rubric.md`.
- Generator should treat planner and evaluator edits as authoritative inputs,
  not as files to rewrite.

## Inputs

- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0027-arc`
- Planner record: `docs/verify-rust-std/challenges/0027-arc/planner.md`
- Evaluator record: `docs/verify-rust-std/challenges/0027-arc/evaluator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0027-arc/rubric.md`

## Scope Boundary

- Authorized code area: this challenge branch only.
- Default repository scope: `runtimeverification/mir-semantics`
- Allowed secondary scope: `runtimeverification/stable-mir-json` when required
- Exceptional scope: `runtimeverification/haskell-backend` only with explicit
  justification logged here and in the evaluator record

## Work Log

- Bootstrap record created by orchestrator.
- 2026-04-10: Workspace prep completed for the active batch handoff. Added
  `workpad.md` for the challenge-local planning/evidence log, added a
  challenge-local README note that separates verification harnesses from
  frontier reproducers, and created `success-criteria.md` as the branch-local
  surface map for the published `Arc`/`Weak` APIs.

## Files Touched

- `docs/verify-rust-std/challenges/0027-arc/success-criteria.md`
- `docs/verify-rust-std/challenges/0027-arc/workpad.md`
- `kmir/src/tests/integration/data/verify-rust-std/0027-arc/README.md`

## Validation Evidence

- Docs-only workspace prep. No proof commands run.

## Commit Inventory

- Pending commit.

## Blockers

- Waiting for planner contract and evaluator baseline.
