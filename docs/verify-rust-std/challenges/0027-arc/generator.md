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
- 2026-04-10: Ported the shared transparent-wrapper transmute rule from
  `0026-rc` into `kmir/src/kmir/kdist/mir-semantics/rt/data.md`. Validation on
  `arc-from-raw-in-frontier-fail.rs` and `arc-from-raw-in.rs` moved the proof
  frontier off the old helper-level `CastKind::Transmute` leaf and onto
  `#setUpCalleeData(monoItemFn(... name: symbol("malloc"), body: noBody), ...)`
  at node `3`.

## Files Touched

- `kmir/src/kmir/kdist/mir-semantics/rt/data.md`
- `docs/verify-rust-std/challenges/0027-arc/success-criteria.md`
- `docs/verify-rust-std/challenges/0027-arc/plan.md`
- `docs/verify-rust-std/challenges/0027-arc/workpad.md`
- `kmir/src/tests/integration/data/verify-rust-std/0027-arc/README.md`

## Validation Evidence

- `timeout 3600s make -C /home/zhaoji/projs/mir-semantics-vrs/challenges/0027-arc build PARALLEL=2`
- `uv --project /home/zhaoji/projs/mir-semantics-vrs/challenges/0027-arc/kmir run -- kmir prove /home/zhaoji/projs/mir-semantics-vrs/challenges/0027-arc/kmir/src/tests/integration/data/verify-rust-std/0027-arc/arc-from-raw-in-frontier-fail.rs --start-symbol main --proof-dir /tmp/arc-from-raw-in-frontier-proof-0027-fix1 --verbose --terminate-on-thunk`
- `uv --project /home/zhaoji/projs/mir-semantics-vrs/challenges/0027-arc/kmir run -- kmir show arc-from-raw-in-frontier-fail.main --proof-dir /tmp/arc-from-raw-in-frontier-proof-0027-fix1 --nodes 3 --full-printer`
- `uv --project /home/zhaoji/projs/mir-semantics-vrs/challenges/0027-arc/kmir run -- kmir prove /home/zhaoji/projs/mir-semantics-vrs/challenges/0027-arc/kmir/src/tests/integration/data/verify-rust-std/0027-arc/arc-from-raw-in.rs --start-symbol verify_arc_from_raw_in --proof-dir /tmp/arc-from-raw-in-proof-0027-fix1 --verbose --terminate-on-thunk`
- `uv --project /home/zhaoji/projs/mir-semantics-vrs/challenges/0027-arc/kmir run -- kmir show arc-from-raw-in.verify_arc_from_raw_in --proof-dir /tmp/arc-from-raw-in-proof-0027-fix1 --nodes 3 --full-printer`

## Commit Inventory

- Pending commit for the shared transmute-fix validation slice.

## Blockers

- Waiting for the next semantic narrowing candidate or a successful proof
  discharge on the Arc-side shared helper frontier.
