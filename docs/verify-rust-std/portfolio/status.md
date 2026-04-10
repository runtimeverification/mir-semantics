# Portfolio Status

Last orchestrator checkpoint: 2026-04-09 UTC

## Terminal-State Rule

The portfolio is complete only when every published challenge is in one of:

- `BLOCKED`
- `CONDITIONALLY READY`
- `READY FOR SUBMISSION`
- `SUBMITTED / CLOSED`

`BOOTSTRAP` and `IN PROGRESS` are explicitly non-terminal.

## Current Batch

- `0011-floats-ints` -> `IN PROGRESS` (`2.96 / 3`)
- `0028-flt2dec` -> `IN PROGRESS` (`1.9 / 3`)
- `0026-rc` -> `IN PROGRESS` (`1.7 / 3`)

## Current Active State

- `0011-floats-ints`: eleven branch-local proof slices now pass
  (`unchecked_add_u8`, `unchecked_neg_i8`, `unchecked_sub_u8`,
  `wrapping_shl_u8`, `wrapping_shr_u8`, `widening_mul_u8`,
  `carrying_mul_u8`, `unchecked_mul_u8`, `unchecked_mul_u16`,
  `unchecked_mul_u32`, `unchecked_mul_u64`); float `to_int_unchecked` remains
  blocked by the precise `fabsf32` / `fabsf64` frontier, and the next breadth
  gap is now the `unchecked_shl` / `unchecked_shr` family; next action is
  `unchecked_shl_u8`.
- `0028-flt2dec`: successive probe rewrites have cleared helper equality,
  `MaybeUninit::slice_assume_init_ref`, and the probe-local top guards, and the
  current stuck leaf is now the copied `if exp < buf.len()` branch select in
  `digits_to_dec_str_probe.rs`; the latest taken-arm probe was checkpointed but
  did not validate a new leaf, so the last validated boundary remains that same
  `#selectBlock`; next action is still to isolate the taken arm and classify
  the first leaf beyond it.
- `0026-rc`: the first contract/entrypoint audit is committed, a direct
  `Rc::from_raw_in` witness harness now exists, and the current blocker has
  been narrowed to a direct-witness `CastKind::Transmute` leaf; next action is
  to shrink that witness to the smallest raw-memory / `System` provenance setup
  that avoids introducing the same transmute; the latest rerun rebuilt the
  missing kdist targets but was interrupted before it yielded any new node.

## Newly Terminal This Run

- `0012-nonzero` -> `BLOCKED`
  Exact blocker: `u8 -> Option<NonZeroU8>` still stops at the same top-level
  `castKindTransmute` thunk even after SMIR-confirmed zero-niche layout
  inspection and two reverted matcher attempts.
- `0013-cstr` -> `BLOCKED`
  Exact blocker: donor-linked SMIR item qualification rewrites root item names
  and breaks `start_symbol` lookup in `make_call_config`, so the donated
  `core::ffi::CStr::from_bytes_with_nul` body cannot execute.

## Exact Restart Point If The Run Stops Now

- Resume the current batch: `0011-floats-ints`, `0028-flt2dec`, `0026-rc`.
- Restart priority inside the current batch:
  1. `0011-floats-ints`: run `unchecked_shl_u8`, then reassess whether the
     remaining `unchecked_shl` / `unchecked_shr` breadth is finally narrow
     enough to justify a stronger verdict without touching the still-blocked
     float path.
  2. `0028-flt2dec`: isolate the taken arm past the copied
     `if exp < buf.len()` branch select and record the first leaf beyond that
     `#selectBlock`; the most recent taken-arm probe did not validate a new
     leaf.
  3. `0026-rc`: retry the smaller raw-memory witness after the restored rerun;
     the last attempt rebuilt the required kdist targets but still did not
     complete far enough to observe a new node.
- `0012` and `0013` are terminal and should not be returned to the active batch
  unless the user explicitly asks to reopen blocked challenges.

## Batch Selection Rationale

- `0011-floats-ints`: now sits at `2.96 / 3`; the multiplication side is
  stronger, but the evaluator explicitly redirected the next step to the still
  unproven `unchecked_shl` / `unchecked_shr` family.
- `0028-flt2dec`: continues to yield reusable probe-narrowing patterns and is
  the active challenge most likely to convert scaffolding progress into the
  first `flt2dec`-owned leaf.
- `0026-rc`: the refcount family still matters for `0027-arc`, but current
  evidence says its next leverage point is a more surgical witness rewrite
  rather than immediate API expansion.

## Exact Next Batch If Interrupted After The Current Batch

- `0027-arc`
- `0014-convert-num`
- `0015-intrinsics-simd`

Rationale:

- `0027-arc` is the strongest immediate reuse target from the new `0026-rc`
  contract map.
- `0014-convert-num` is the next numeric-conversion challenge that can reuse
  the widening / conversion findings from `0011`.
- `0015-intrinsics-simd` is still unstarted but is a better next candidate than
  the remaining bootstrap queue once the current batch yields another terminal
  verdict.

## Portfolio Inventory

- Challenge worktrees created: `29`
- Challenge draft PRs opened: `29`
- Dedicated challenge branches created: `29`
- Observed agent thread cap: `6`

## Current Run Constraint

- Long proof / linkage loops on `0012-nonzero` and `0013-cstr` required
  checkpoint-style finishes to avoid leaving dirty experimental state in the
  worktrees.
- The observed live-agent cap remains `6`, which forced repeated close/reopen
  cycles for planner/generator/evaluator passes.
- In the latest cycle, fresh `0011` / `0028` generator attempts consumed time
  and produced only cleaned worktrees without new committed evidence before
  interruption, so the restart point below intentionally reuses the last
  committed branch states rather than any uncommitted subagent context.
- In this cycle, a fresh `0011` multiplication slice was validated and
  checkpointed, but the follow-up `unchecked_shl_u8` run and the latest `0026`
  raw-memory-witness rerun were both interrupted before producing a new proof
  result, so they were preserved as docs-only checkpoints rather than promoted
  into new evaluation evidence.
- If this run stops here, treat that as an external runtime/tool constraint for
  this turn, not as a challenge-level terminal verdict.

## Challenge State Index

See `docs/verify-rust-std/portfolio/current-states.tsv`.
