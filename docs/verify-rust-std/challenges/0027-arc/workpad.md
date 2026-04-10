# Challenge 0027 Workpad

## Current State

- Branch: `verify-rust-std/reexec-0027-arc`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0027-arc`
- Draft PR: exists.
- Evaluator: active / awaiting next reassessment.
- Success criteria map: `docs/verify-rust-std/challenges/0027-arc/success-criteria.md`
- Challenge-local README: `kmir/src/tests/integration/data/verify-rust-std/0027-arc/README.md`
- Current state: the first verification-shaped `Arc::from_raw_in` harness has
  been added, and the smallest concrete frontier reproducer for the same leaf
  has been split into its own file. The latest validation moved both the
  symbolic harness and the frontier reproducer off the old transmute leaf and
  onto the shared `malloc` `noBody` frontier at node `3`.

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
- Reproducer focus: capture the smallest meaningful semantic blocker in a
  challenge-local file without counting it as verification; the current file
  is smaller than the verification harness because it fixes the payload and
  uses `main`

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

- The bounded proof command was:
  `timeout 900s uv --project kmir run -- kmir prove /home/zhaoji/projs/mir-semantics-vrs/challenges/0027-arc/kmir/src/tests/integration/data/verify-rust-std/0027-arc/arc-from-raw-in.rs --start-symbol verify_arc_from_raw_in --proof-dir /tmp/arc-from-raw-in-proof-0027 --verbose --terminate-on-thunk`
- Result: `ProofStatus.FAILED`
- Frontier: leaf `4`, stuck at `castKindTransmute` in
  `Box::<alloc::sync::ArcInner<u32>, std::alloc::System>::new_uninit_in`
- New reproducer command:
  `timeout 900s uv --project kmir run -- kmir prove /home/zhaoji/projs/mir-semantics-vrs/challenges/0027-arc/kmir/src/tests/integration/data/verify-rust-std/0027-arc/arc-from-raw-in-frontier-fail.rs --start-symbol main --proof-dir /tmp/arc-from-raw-in-frontier-proof-0027 --verbose --terminate-on-thunk`
- Latest validation commands:
  `timeout 3600s make -C /home/zhaoji/projs/mir-semantics-vrs/challenges/0027-arc build PARALLEL=2`
  `uv --project /home/zhaoji/projs/mir-semantics-vrs/challenges/0027-arc/kmir run -- kmir prove /home/zhaoji/projs/mir-semantics-vrs/challenges/0027-arc/kmir/src/tests/integration/data/verify-rust-std/0027-arc/arc-from-raw-in-frontier-fail.rs --start-symbol main --proof-dir /tmp/arc-from-raw-in-frontier-proof-0027-fix1 --verbose --terminate-on-thunk`
  `uv --project /home/zhaoji/projs/mir-semantics-vrs/challenges/0027-arc/kmir run -- kmir show arc-from-raw-in-frontier-fail.main --proof-dir /tmp/arc-from-raw-in-frontier-proof-0027-fix1 --nodes 3 --full-printer`
  `uv --project /home/zhaoji/projs/mir-semantics-vrs/challenges/0027-arc/kmir run -- kmir prove /home/zhaoji/projs/mir-semantics-vrs/challenges/0027-arc/kmir/src/tests/integration/data/verify-rust-std/0027-arc/arc-from-raw-in.rs --start-symbol verify_arc_from_raw_in --proof-dir /tmp/arc-from-raw-in-proof-0027-fix1 --verbose --terminate-on-thunk`
  `uv --project /home/zhaoji/projs/mir-semantics-vrs/challenges/0027-arc/kmir run -- kmir show arc-from-raw-in.verify_arc_from_raw_in --proof-dir /tmp/arc-from-raw-in-proof-0027-fix1 --nodes 3 --full-printer`
- Next generator step is to determine whether the shared `malloc` `noBody`
  frontier is now the Arc-side canonical blocker or a separate wrapper edge
  that needs another narrowing pass.
