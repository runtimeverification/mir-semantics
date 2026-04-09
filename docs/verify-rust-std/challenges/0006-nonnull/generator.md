# Generator Record: Challenge 0006

Ownership:

- Generator owns this file and the implementation work for this challenge.
- Generator must not edit `evaluator.md` or `rubric.md`.
- Generator should treat planner and evaluator edits as authoritative inputs,
  not as files to rewrite.

## Inputs

- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0006-nonnull`
- Planner record: `docs/verify-rust-std/challenges/0006-nonnull/planner.md`
- Evaluator record: `docs/verify-rust-std/challenges/0006-nonnull/evaluator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0006-nonnull/rubric.md`

## Scope Boundary

- Authorized code area: this challenge branch only.
- Default repository scope: `runtimeverification/mir-semantics`
- Allowed secondary scope: `runtimeverification/stable-mir-json` when required
- Exceptional scope: `runtimeverification/haskell-backend` only with explicit
  justification logged here and in the evaluator record

## Work Log

- Bootstrap record created by orchestrator.
- 2026-04-09: Completed bootstrap reconnaissance by reading:
  - branch and challenge README inputs
  - planner and evaluator records
  - `/tmp/verify-rust-std-ref/doc/src/challenges/0006-nonnull.md`

## Initial Reconnaissance

- Likely challenge-local artifact area:
  - `kmir/src/tests/integration/data/verify-rust-std/0006-nonnull/`
  - currently contains only `README.md`; harness/proof/coverage artifacts will
    need to be introduced here.
- Likely integration entry points for proof and regression wiring:
  - `kmir/src/tests/integration/test_integration.py`
  - existing integration fixture patterns under
    `kmir/src/tests/integration/data/prove-rs/` and
    `kmir/src/tests/integration/data/exec-smir/`
- Likely semantics dependency areas for `NonNull` obligations:
  - pointer/provenance and memory operations in
    `kmir/src/kmir/kdist/mir-semantics/rt/data.md` and related runtime modules
    under `kmir/src/kmir/kdist/mir-semantics/rt/`
  - MIR body and pointer behavior definitions in
    `kmir/src/kmir/kdist/mir-semantics/body.md` and
    `kmir/src/kmir/kdist/mir-semantics/lib.md`
  - potential slice/DST and `MaybeUninit` interactions noted by planner and
    evaluator baselines.
- Published challenge shape confirmed from reference doc:
  - 48 public `NonNull` APIs in scope
  - UB obligations: dangling/misaligned access, uninitialized reads, mutation
    of immutable bytes, invalid values.

## Baseline Readiness

- Planner baseline: present with requirements extraction and scope contract.
- Evaluator baseline: present with challenge-specific rubric scorecard seeded.
- Waiting status: not blocked on missing planner/evaluator baselines; ready to
  start implementation in a later step.

## Files Touched

- `docs/verify-rust-std/challenges/0006-nonnull/generator.md`

## Validation Evidence

- None yet.

## Commit Inventory

- None yet.

## Blockers

- No active blocker at bootstrap reconnaissance stage.
