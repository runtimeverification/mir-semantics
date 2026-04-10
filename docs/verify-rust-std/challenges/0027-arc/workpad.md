# Challenge 0027 Workpad

## Current State

- Branch: `verify-rust-std/reexec-0027-arc`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0027-arc`
- Draft PR: exists.
- Evaluator: bootstrap only.
- Success criteria map: `docs/verify-rust-std/challenges/0027-arc/success-criteria.md`
- Challenge-local README: `kmir/src/tests/integration/data/verify-rust-std/0027-arc/README.md`
- Current state: workspace prepared for active generator work, but no proof or semantic work has started yet.

## Confirmed Inputs

- Challenge page: `https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0027-arc.md`
- Tracking issue: `#383`
- Artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0027-arc`
- Branch-local rubric: `docs/verify-rust-std/challenges/0027-arc/rubric.md`
- Reusable comparison branch: `verify-rust-std/reexec-0026-rc`

## Reusable Lessons From 0026

- Keep the proof harness and the frontier reproducer in separate files.
- Treat a concrete witness driver as audit evidence, not as the verification target.
- Make the proof entrypoint symbolic over the primitive payload and keep the
  allocator concrete when the challenge bounds allow it.
- Record the smallest frontier reproducer before attempting semantic repairs.
- Keep a current success-criteria table so PR descriptions can show progress by
  function, not just by broad status.

## First Intended Split

- Verification harness target: `arc-from-raw-in.rs`
- Frontier reproducer target: `arc-from-raw-in-frontier-fail.rs`
- Proof focus: `Arc::from_raw_in` first, then the refcount recovery spine it
  enables
- Reproducer focus: capture the current `CastKind::Transmute` frontier in a
  challenge-local file without counting it as verification

## Planning Notes

- The first tranche should stay on the raw-pointer and refcount family before
  widening to initialization or dynamic-type reasoning.
- `assume_init` is explicitly called out by the challenge page as a likely
  type-system boundary, so it should remain outside tranche 1 unless evidence
  forces a narrower dependency.
- The branch-local docs should remain easy to compare against `0026`, but the
  exact `Rc` structure should not be copied blindly because `Arc` introduces
  atomic and data-race obligations.

## Handoff State

- No proof commands have been run on this challenge yet.
- The next generator step is to create the first proof/reproducer files once
  the planner and evaluator have the same narrowed tranche.
