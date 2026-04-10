# Portfolio Status

Last orchestrator checkpoint: 2026-04-10 UTC

## Terminal-State Rule

The portfolio is complete only when every published challenge is in one of:

- `BLOCKED`
- `CONDITIONALLY READY`
- `READY FOR SUBMISSION`
- `SUBMITTED / CLOSED`

`BOOTSTRAP` and `IN PROGRESS` are explicitly non-terminal.

## Current Batch

- `0026-rc` -> `IN PROGRESS` (`1.7 / 3`)
- `0028-flt2dec` -> `IN PROGRESS` (`1.9 / 3`)
- `0027-arc` -> `IN PROGRESS` (`1.8 / 3`)

## Current Active State

- `0026-rc`: the branch now has a verification-shaped symbolic proof harness
  `rc-from-raw-in.rs` plus a canonical one-line frontier reproducer
  `rc-new-in-frontier-fail.rs` and the broader audit reproducer
  `rc-from-raw-in-frontier-fail.rs`; the correct proof target
  `verify_rc_from_raw_in` and the one-line reproducer still reach the same
  `CastKind::Transmute` frontier at node 4 inside
  `Box::<std::rc::RcInner<u32>, std::alloc::System>::try_new_uninit_in` at
  `library/core/src/alloc/layout.rs:140`, so the challenge remains
  `IN PROGRESS`.
- `0028-flt2dec`: success table, stronger replay collector, and explicit CI
  discoverability now exist; the copied `if exp >= buf.len()` select was
  passed; the new first leaf is deeper in `core::slice::index` at
  `<std::ops::Range<usize> as std::slice::SliceIndex<[u8]>>::index`
  (`slice_end_index_len_fail`); score remains `1.9 / 3`; evaluator evidence
  now confirms the current probe is already minimal enough, so the next action
  is to classify or fix that slice-index frontier rather than keep shrinking
  the reproducer.
- `0027-arc`: activated into the current batch because it is the strongest
  reuse candidate from `0026-rc`; the first symbolic proof harness for
  `Arc::from_raw_in` now exists, and it is now paired with a dedicated
  smaller frontier reproducer `arc-from-raw-in-frontier-fail.rs`, which still
  records the same leaf `4` inside
  `Box::<alloc::sync::ArcInner<u32>, std::alloc::System>::new_uninit_in`.
  The challenge remains `IN PROGRESS` at `1.8 / 3`, and the next action is to
  use that reproducer to validate any shared fix candidate before widening the
  Arc tranche.

## Cross-Challenge Semantic Pattern

- `0026-rc` and `0027-arc` now expose the same helper-family failure mode:
  proof-harness symbols are correct and challenge-local, but witness
  construction still bottoms out at a helper-level `CastKind::Transmute`
  frontier inside allocator-backed `*_new_uninit_in` / `try_new_uninit_in`
  paths. `0026` is now the canonical lead reproducer because its current
  frontier case is one line long; `0027` is the follower validation branch for
  the same semantic family.

## Newly Terminal This Run

- `0011-floats-ints` -> `CLOSED`
  Exact reason: closed per user instruction because the challenge was already
  being pursued in `runtimeverification/mir-semantics#985`; draft PR `#1036`
  was updated and closed. The last validated local checkpoint before closure
  was `unchecked_shl_i8` passing in `/tmp/kmir-0011-unchecked-shl-i8`.
- `0012-nonzero` -> `BLOCKED`
  Exact blocker: `u8 -> Option<NonZeroU8>` still stops at the same top-level
  `castKindTransmute` thunk even after SMIR-confirmed zero-niche layout
  inspection and two reverted matcher attempts.
- `0013-cstr` -> `BLOCKED`
  Exact blocker: donor-linked SMIR item qualification rewrites root item names
  and breaks `start_symbol` lookup in `make_call_config`, so the donated
  `core::ffi::CStr::from_bytes_with_nul` body cannot execute.

## Exact Restart Point If The Run Stops Now

- Resume the current batch: `0026-rc`, `0028-flt2dec`, `0027-arc`.
- Restart priority inside the current batch:
  1. `0026-rc`: continue from the split proof-harness / reproducer shape and
     attack the remaining `CastKind::Transmute` leaf reached by
     `verify_rc_from_raw_in`, starting from the canonical one-line
     `rc-new-in-frontier-fail.rs` witness.
  2. `0027-arc`: preserve `arc-from-raw-in.rs` as the verification harness and
     use `arc-from-raw-in-frontier-fail.rs` to validate any shared fix
     candidate for the helper-level transmute family.
  3. `0028-flt2dec`: stop shrinking the probe and classify or fix
     `slice_end_index_len_fail` at
     `<std::ops::Range<usize> as std::slice::SliceIndex<[u8]>>::index` on the
     restored `&buf[..exp]` path.
- `0011` is now terminal and should not be returned to the active batch unless
  the user explicitly reopens it.
- `0012` and `0013` are terminal and should not be returned to the active batch
  unless the user explicitly asks to reopen blocked challenges.

## Batch Selection Rationale

- `0026-rc`: the refcount family still matters for `0027-arc`, and the current
  leverage point is now sharper because the proof harness / reproducer split is
  correct and the frontier is isolated to a canonical one-line reproducer on
  the proper symbol.
- `0028-flt2dec`: the copied branch select is no longer the frontier; the
  current leverage point is the deeper `core::slice::index` failure, and the
  evaluator has now confirmed the existing probe is already minimal enough.
- `0027-arc`: activated immediately after `0011` closed because it is the
  strongest reuse target from the `Rc` raw-pointer / refcount contract family,
  and it now confirms the shared allocator-helper transmute blocker family with
  a dedicated reproducer rather than remaining at bootstrap.

## Exact Next Batch If Interrupted After The Current Batch

- `0014-convert-num`
- `0015-intrinsics-simd`
- `0001-core-transmutation`

Rationale:

- `0014-convert-num` is the next numeric-conversion challenge that can reuse
  the widening / conversion findings from `0011`.
- `0015-intrinsics-simd` is still unstarted but is a better next candidate than
  the remaining bootstrap queue once the current batch yields another terminal
  verdict.
- `0001-core-transmutation` is a stronger generic fallback than reopening
  already-active `0027-arc` in the next-batch list.

## Portfolio Inventory

- Challenge worktrees created: `29`
- Challenge draft PRs opened: `29`
- Dedicated challenge branches created: `29`
- Observed agent thread cap: `6`

## Current Run Constraint

- The portfolio rubric and templates now require explicit Success Criteria
  coverage tables, a verification-harness versus frontier-reproducer split,
  and minimal reproducer evidence before semantic fixes.
- Long proof / linkage loops on `0012-nonzero` and `0013-cstr` required
  checkpoint-style finishes to avoid leaving dirty experimental state in the
  worktrees.
- The observed live-agent cap remains `6`, which forced repeated close/reopen
  cycles for planner/generator/evaluator passes.
- In the latest cycle, `0011` was closed by user direction as superseded by
  `#985`, `0026` reduced its canonical helper reproducer to a single line,
  `0027` added a dedicated Arc-side frontier reproducer and updated plan/eval
  accordingly, and `0028` confirmed its current probe is already minimal
  enough, so further work should target `slice_end_index_len_fail` itself.
- If this run stops here, treat that as an external runtime/tool constraint for
  this turn, not as a challenge-level terminal verdict.

## Challenge State Index

See `docs/verify-rust-std/portfolio/current-states.tsv`.
