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

- `0011-floats-ints` -> `IN PROGRESS` (`2.9 / 3`)
- `0028-flt2dec` -> `IN PROGRESS` (`1.5 / 3`)
- `0026-rc` -> `IN PROGRESS` (`1.5 / 3`)

## Current Active State

- `0011-floats-ints`: seven branch-local proof slices now pass
  (`unchecked_add_u8`, `unchecked_neg_i8`, `unchecked_sub_u8`,
  `wrapping_shl_u8`, `wrapping_shr_u8`, `widening_mul_u8`,
  `carrying_mul_u8`); float `to_int_unchecked` remains blocked by the precise
  `fabsf32` / `fabsf64` frontier; next action is `unchecked_mul_u8`.
- `0028-flt2dec`: two successive probe rewrites removed the initial
  `SliceIndex::index` and `from_raw_parts` frontiers, but the probe still dies
  in challenge-local scaffolding (`array::equality`); next action is to remove
  the helper equality path and rerun until a real `flt2dec` boundary or backend
  limit appears.
- `0026-rc`: the first contract/entrypoint audit is committed and now maps all
  12 public `unsafe` `Rc` APIs, with a first tranche rooted at
  `Rc::from_raw_in`; next action is to start proof work on that raw-pointer /
  refcount spine.

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
  1. `0028-flt2dec`: remove the helper equality path from the narrowed probe
     and rerun until the failure is inside `flt2dec` or a real backend limit.
  2. `0026-rc`: start the first proof tranche rooted at `Rc::from_raw_in`,
     then extend to the paired refcount transitions.
  3. `0011-floats-ints`: run `unchecked_mul_u8`, then reassess whether the
     remaining non-float matrix is finally narrow enough for a stronger verdict.
- `0012` and `0013` are terminal and should not be returned to the active batch
  unless the user explicitly asks to reopen blocked challenges.

## Batch Selection Rationale

- `0011-floats-ints`: already near the top of the scale (`2.9 / 3`) and cheap
  to widen with one more slice at a time.
- `0028-flt2dec`: directly reuses numeric / float instincts from `0011`, but
  now appears to have its own probe-scaffolding ladder rather than the same
  backend blocker.
- `0026-rc`: first contract map is committed and the next tranche is concrete;
  this also sets up reuse for `0027-arc`.

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
- If this run stops here, treat that as an external runtime/tool constraint for
  this turn, not as a challenge-level terminal verdict.

## Challenge State Index

See `docs/verify-rust-std/portfolio/current-states.tsv`.
