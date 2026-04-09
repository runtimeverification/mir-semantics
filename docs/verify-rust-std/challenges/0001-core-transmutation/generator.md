# Generator Record: Challenge 0001

Ownership:

- Generator owns this file and the implementation work for this challenge.
- Generator must not edit `evaluator.md` or `rubric.md`.
- Generator should treat planner and evaluator edits as authoritative inputs,
  not as files to rewrite.

## Inputs

- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0001-core-transmutation`
- Planner record: `docs/verify-rust-std/challenges/0001-core-transmutation/planner.md`
- Evaluator record: `docs/verify-rust-std/challenges/0001-core-transmutation/evaluator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0001-core-transmutation/rubric.md`

## Scope Boundary

- Authorized code area: this challenge branch only.
- Default repository scope: `runtimeverification/mir-semantics`
- Allowed secondary scope: `runtimeverification/stable-mir-json` when required
- Exceptional scope: `runtimeverification/haskell-backend` only with explicit
  justification logged here and in the evaluator record

## Work Log

- Bootstrap record created by orchestrator.
- 2026-04-09 bootstrap reconnaissance completed (docs-only):
  - Read challenge artifact README, planner record, evaluator record, and
    `/tmp/verify-rust-std-ref/doc/src/challenges/0001-core-transmutation.md`.
  - Confirmed challenge scope is broad (`transmute`/`transmute_unchecked` plus
    transmute-adjacent APIs), but this branch starts with no challenge-local
    harness files yet beyond the artifact README.
  - Identified likely implementation/test touchpoints for later sprints:
    - `kmir/src/tests/integration/data/verify-rust-std/0001-core-transmutation/`
      for challenge-local prove-rs harness inputs and expected outputs.
    - `kmir/src/tests/integration/test_integration.py` for integration wiring
      and prove/show expectations (already contains transmute-themed cases under
      general prove-rs data).
    - `kmir/src/kmir/kdist/mir-semantics/rt/data.md` for runtime transmute cast
      behavior (`#cast(..., castKindTransmute, ...)`, array/range transmute
      helpers, and related TODO notes).
    - `kmir/src/kmir/kdist/mir-semantics/lemmas/kmir-lemmas.md` for lemma
      support on byte/bit-level transmute reasoning.
- 2026-04-09 probable dependency map (pre-implementation):
  - Primary repo: `runtimeverification/mir-semantics` (challenge-local artifacts
    and semantics/proof rules).
  - Likely build/test dependencies: `stable-mir-json` submodule plus existing
    `kmir` integration/prove infrastructure.
  - Optional reference dependency: verify-rust-std challenge docs and issue
    history for acceptance interpretation.
  - No exceptional dependency escalation requested at bootstrap.

## Files Touched

- None yet.

## Validation Evidence

- None yet.

## Commit Inventory

- None yet.

## Blockers

- Waiting for planner contract and evaluator baseline.
- Planner and evaluator are both at bootstrap templates; waiting for their
  concrete baselines before implementation/harness work starts.
