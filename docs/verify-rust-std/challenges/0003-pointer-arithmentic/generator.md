# Generator Record: Challenge 0003

Ownership:

- Generator owns this file and the implementation work for this challenge.
- Generator must not edit `evaluator.md` or `rubric.md`.
- Generator should treat planner and evaluator edits as authoritative inputs,
  not as files to rewrite.

## Inputs

- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0003-pointer-arithmentic`
- Planner record: `docs/verify-rust-std/challenges/0003-pointer-arithmentic/planner.md`
- Evaluator record: `docs/verify-rust-std/challenges/0003-pointer-arithmentic/evaluator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0003-pointer-arithmentic/rubric.md`

## Scope Boundary

- Authorized code area: this challenge branch only.
- Default repository scope: `runtimeverification/mir-semantics`
- Allowed secondary scope: `runtimeverification/stable-mir-json` when required
- Exceptional scope: `runtimeverification/haskell-backend` only with explicit
  justification logged here and in the evaluator record

## Work Log

- Bootstrap record created by orchestrator.
- 2026-04-09 bootstrap reconnaissance completed from:
  - `kmir/src/tests/integration/data/verify-rust-std/0003-pointer-arithmentic/README.md`
  - `docs/verify-rust-std/challenges/0003-pointer-arithmentic/planner.md`
  - `docs/verify-rust-std/challenges/0003-pointer-arithmentic/evaluator.md`
  - `/tmp/verify-rust-std-ref/doc/src/challenges/0003-pointer-arithmentic.md`

## Initial Reconnaissance

### Likely Implementation Areas

- Challenge-local harness/proof artifacts:
  - `kmir/src/tests/integration/data/verify-rust-std/0003-pointer-arithmentic/`
- Existing integration proof corpus likely reusable for pattern matching and
  quick repros:
  - `kmir/src/tests/integration/data/prove-rs/`
  - Notable existing pointer arithmetic negative tests:
    - `test_offset_from-fail.rs`
    - `offset-u8-fail.rs`
    - `ref-ptr-cast-elem-offset-fail.rs`
- Integration test driver likely to require registration/wiring updates once
  implementation starts:
  - `kmir/src/tests/integration/test_integration.py` (currently keyed to
    `prove-rs` dataset)
- Semantics documentation/behavior reference for pointer-difference operations:
  - `kmir/src/kmir/kdist/mir-semantics/intrinsics.md` (`ptr_offset_from`,
    `ptr_offset_from_unsigned`)

### Probable Dependencies

- `stable-mir-json` readiness is a stated prerequisite in planner notes.
- Existing KMIR support for pointer arithmetic and in-bounds projection checks
  will determine whether challenge-local harnesses are sufficient or whether
  semantics updates are needed.
- Pointee coverage obligations likely require typed fixture expansion across:
  integers, one `dyn Trait`, one slice, `()`, and one composite non-ZST type.
- At least three std-usage proofs are required in addition to pointer primitive
  contracts, so challenge-local tests must include usage-level targets (for
  example `[u8]::is_ascii`, `Option::as_slice`, `Vec::swap_remove`,
  `String::remove`, `VecDeque::swap`).

### Planner/Evaluator Baseline Status

- Planner baseline: partially established (requirements + blockers captured;
  sprint status still mostly pending).
- Evaluator baseline: bootstrap-only; rubric/scorecard not yet populated.
- Generator execution posture at bootstrap: hold implementation until planner
  and evaluator baselines are sufficiently populated for acceptance alignment.

## Files Touched

- `docs/verify-rust-std/challenges/0003-pointer-arithmentic/generator.md`

## Validation Evidence

- None yet.

## Commit Inventory

- None yet.

## Blockers

- Waiting for planner sprint decomposition and evaluator rubric baseline before
  implementation/proof work starts.
