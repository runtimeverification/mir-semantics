# Generator Record: Challenge 0002

Ownership:

- Generator owns this file and the implementation work for this challenge.
- Generator must not edit `evaluator.md` or `rubric.md`.
- Generator should treat planner and evaluator edits as authoritative inputs,
  not as files to rewrite.

## Inputs

- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0002-intrinsics-memory`
- Planner record: `docs/verify-rust-std/challenges/0002-intrinsics-memory/planner.md`
- Evaluator record: `docs/verify-rust-std/challenges/0002-intrinsics-memory/evaluator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0002-intrinsics-memory/rubric.md`

## Scope Boundary

- Authorized code area: this challenge branch only.
- Default repository scope: `runtimeverification/mir-semantics`
- Allowed secondary scope: `runtimeverification/stable-mir-json` when required
- Exceptional scope: `runtimeverification/haskell-backend` only with explicit
  justification logged here and in the evaluator record

## Work Log

- Bootstrap record created by orchestrator.
- Initial bootstrap reconnaissance recorded on 2026-04-09 after reading:
  - `kmir/src/tests/integration/data/verify-rust-std/0002-intrinsics-memory/README.md`
  - `docs/verify-rust-std/challenges/0002-intrinsics-memory/planner.md`
  - `docs/verify-rust-std/challenges/0002-intrinsics-memory/evaluator.md`
  - `/tmp/verify-rust-std-ref/doc/src/challenges/0002-intrinsics-memory.md`

## Initial Reconnaissance

- Likely semantics implementation hotspot:
  - `kmir/src/kmir/kdist/mir-semantics/intrinsics.md`
  - Observed existing rules relevant to this challenge: `volatile_store`,
    `volatile_load`, `ptr_offset_from`, `ptr_offset_from_unsigned`.
- Likely supporting semantics dependencies for memory-safety obligations:
  - `kmir/src/kmir/kdist/mir-semantics/alloc.md` (allocation / pointer
    validity behavior)
  - `kmir/src/kmir/kdist/mir-semantics/rt/data.md` and
    `kmir/src/kmir/kdist/mir-semantics/rt/value.md` (runtime memory/value
    representation)
  - `kmir/src/kmir/kdist/mir-semantics/body.md` (execution path where
    intrinsic dispatch interacts with statements/terminators)
- Likely proof/harness entry points:
  - Challenge-local artifacts under
    `kmir/src/tests/integration/data/verify-rust-std/0002-intrinsics-memory/`
  - Existing intrinsic proof patterns under
    `kmir/src/tests/integration/data/prove-rs/` (contains volatile and
    pointer-offset examples already exercised by integration tests)
  - Integration harness driver:
    `kmir/src/tests/integration/test_integration.py` (`test_prove` over
    `data/prove-rs`)
- Probable dependency pressure points from the challenge contract:
  - Coverage gap between the challenge intrinsic list and currently modeled
    intrinsics in `intrinsics.md` (to be confirmed during implementation).
  - Wrapper-level obligations for `std::ptr` APIs listed in the challenge
    (`copy_from_slice`, `parse_u64_into`, `swap`, `align_of_val`, `zeroed`)
    will likely require dedicated harness specs, not only intrinsic-level tests.

## Baseline Coordination Status

- Planner baseline: available (requirements and phased plan are populated).
- Evaluator baseline/rubric extension: not yet available.
- Generator status: waiting for evaluator baseline before implementation starts.

## Files Touched

- `docs/verify-rust-std/challenges/0002-intrinsics-memory/generator.md`

## Validation Evidence

- None yet.

## Commit Inventory

- None yet.

## Blockers

- Waiting for evaluator baseline/rubric expansion before implementation.
