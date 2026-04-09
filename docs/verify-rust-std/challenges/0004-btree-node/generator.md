# Generator Record: Challenge 0004

Ownership:

- Generator owns this file and the implementation work for this challenge.
- Generator must not edit `evaluator.md` or `rubric.md`.
- Generator should treat planner and evaluator edits as authoritative inputs,
  not as files to rewrite.

## Inputs

- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0004-btree-node`
- Planner record: `docs/verify-rust-std/challenges/0004-btree-node/planner.md`
- Evaluator record: `docs/verify-rust-std/challenges/0004-btree-node/evaluator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0004-btree-node/rubric.md`

## Scope Boundary

- Authorized code area: this challenge branch only.
- Default repository scope: `runtimeverification/mir-semantics`
- Allowed secondary scope: `runtimeverification/stable-mir-json` when required
- Exceptional scope: `runtimeverification/haskell-backend` only with explicit
  justification logged here and in the evaluator record

## Work Log

- Bootstrap record created by orchestrator.
- 2026-04-09: Completed bootstrap reconnaissance from the challenge README,
  planner record, evaluator record, and
  `/tmp/verify-rust-std-ref/doc/src/challenges/0004-btree-node.md`.

## Initial Reconnaissance (2026-04-09)

Likely code/test areas for this challenge:

- Challenge-local artifacts:
  `kmir/src/tests/integration/data/verify-rust-std/0004-btree-node/`
  (currently README-only; this is the designated location for harnesses,
  expected outputs, and proof evidence for this branch).
- Integration proof runner likely to be reused/extended:
  `kmir/src/tests/integration/test_integration.py` (current prove fixture points
  at `data/prove-rs`; any challenge-local replay path will need to align with
  this test infrastructure).
- Semantics and UB behavior likely to be stress points for `btree::node`:
  `kmir/src/kmir/kdist/mir-semantics/rt/types.md` and
  `kmir/src/kmir/kdist/mir-semantics/rt/data.md`
  (raw pointers, `MaybeUninit`, and invalid-value handling are directly relevant
  to the challenge UB list).
- Upstream source of truth for API and safety obligations:
  `library/alloc/src/collections/btree/node.rs` in the Rust std snapshot
  referenced by the challenge document.

Probable dependencies and constraints:

- Standard local build/test toolchain in this repo:
  `make stable-mir-json`, `make build`, and `uv --project kmir ...`.
- `deps/stable-mir-json` submodule/tooling availability is a prerequisite for
  SMIR generation and integration-style proof execution.
- No exceptional cross-repo dependency is identified at bootstrap time.

Planner/evaluator baseline status:

- Planner baseline is present and no longer a bootstrap blocker; sprinted scope
  and invariants are now recorded in `planner.md`.
- Evaluator baseline scorecard and challenge addenda are present, but scoring is
  still `not started` (expected at this stage).
- Generator is not blocked on missing baseline docs; implementation remains
  intentionally deferred for this docs-only bootstrap commit.

## Files Touched

- `docs/verify-rust-std/challenges/0004-btree-node/generator.md`

## Validation Evidence

- None yet.

## Commit Inventory

- None yet.

## Blockers

- No bootstrap blocker on missing planner/evaluator baselines.
- Implementation remains paused by task contract (docs-only bootstrap step).
