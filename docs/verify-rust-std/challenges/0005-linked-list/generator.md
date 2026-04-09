# Generator Record: Challenge 0005

Ownership:

- Generator owns this file and the implementation work for this challenge.
- Generator must not edit `evaluator.md` or `rubric.md`.
- Generator should treat planner and evaluator edits as authoritative inputs,
  not as files to rewrite.

## Inputs

- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0005-linked-list`
- Planner record: `docs/verify-rust-std/challenges/0005-linked-list/planner.md`
- Evaluator record: `docs/verify-rust-std/challenges/0005-linked-list/evaluator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0005-linked-list/rubric.md`

## Scope Boundary

- Authorized code area: this challenge branch only.
- Default repository scope: `runtimeverification/mir-semantics`
- Allowed secondary scope: `runtimeverification/stable-mir-json` when required
- Exceptional scope: `runtimeverification/haskell-backend` only with explicit
  justification logged here and in the evaluator record

## Work Log

- Bootstrap record created by orchestrator.
- Bootstrap reconnaissance completed from:
  - `kmir/src/tests/integration/data/verify-rust-std/0005-linked-list/README.md`
  - `docs/verify-rust-std/challenges/0005-linked-list/planner.md`
  - `docs/verify-rust-std/challenges/0005-linked-list/evaluator.md`
  - `/tmp/verify-rust-std-ref/doc/src/challenges/0005-linked-list.md`

## Initial Reconnaissance

### Likely Code / Test Areas

- Challenge-local artifacts will live under:
  `kmir/src/tests/integration/data/verify-rust-std/0005-linked-list/`
  (currently only `README.md` exists there).
- Proof harness wiring will likely integrate with existing prove test plumbing in:
  - `kmir/src/tests/integration/test_integration.py` (`PROVE_DIR`, `test_prove`)
  - `kmir/src/tests/integration/data/prove-rs/` (existing proof fixture pattern)
- Depending on harness shape, optional CLI snapshot coverage may touch:
  `kmir/src/tests/integration/test_cli.py` and `.../data/prove-rs/show/`.
- If challenge-specific semantics gaps appear during implementation, likely
  semantic touchpoints are in:
  - `kmir/src/kmir/kdist/mir-semantics/body.md`
  - `kmir/src/kmir/kdist/mir-semantics/lib.md`
  - related runtime/type/alloc modules in `kmir/src/kmir/kdist/mir-semantics/rt/`

### Probable Dependencies

- Unbounded linked-structure traversal support for arbitrary bi-directional list
  shape (required by challenge success criteria).
- Adequate modeling of pointer validity and mutation/read constraints needed to
  discharge UB obligations:
  - dangling or misaligned access
  - uninitialized memory reads (except allowed cases)
  - immutable-byte mutation
  - invalid value production
- A proof strategy for the seven target linked-list APIs in the challenge doc:
  `clear`, `contains`, `split_off`, `remove`, `retain`, `retain_mut`,
  `extract_if`.
- Reuse of existing prove-rs harness conventions to keep integration with
  `test_prove` deterministic.

### Planner / Evaluator Baseline Status

- Planner baseline: present and sufficiently populated for generator bootstrap.
- Evaluator baseline: present (bootstrap-level); rubric details are still to be
  expanded by evaluator.
- Generator waiting state: no blocker for reconnaissance; implementation start
  remains deferred by task instruction (docs-only bootstrap).

## Files Touched

- `docs/verify-rust-std/challenges/0005-linked-list/generator.md`

## Validation Evidence

- Docs-only bootstrap; no code/proof/test execution performed.

## Commit Inventory

- None yet.

## Blockers

- No immediate blocker for bootstrap documentation.
- Remaining functional work is intentionally deferred until implementation phase.
