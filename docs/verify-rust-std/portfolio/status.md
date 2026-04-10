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

- `0011-floats-ints` -> `IN PROGRESS` (`2.98 / 3`)
- `0026-rc` -> `IN PROGRESS` (`1.7 / 3`)
- `0028-flt2dec` -> `IN PROGRESS` (`1.9 / 3`)

## Current Active State

- `0011-floats-ints`: explicit success table, README, and CI shard now exist
  on the challenge branch; `unchecked_shl_u128` passed at commit `c02477f8`;
  score remains `2.98 / 3`; next action is `unchecked_shl_i8`.
- `0026-rc`: success table, challenge-local frontier harness, and CI shard now
  exist; the stable `MaybeUninit` witness now reaches proof construction, but
  node 4 still ends at the same `CastKind::Transmute` leaf; score remains
  `1.7 / 3`; next action is to attack that transmute leaf directly.
- `0028-flt2dec`: success table, stronger replay collector, and explicit CI
  discoverability now exist; the copied `if exp >= buf.len()` select was
  passed; the new first leaf is deeper in `core::slice::index`
  (`slice_end_index_len_fail`); score remains `1.9 / 3`; next action is to
  reduce that new slice-index frontier.

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
  1. `0011-floats-ints`: run `unchecked_shl_u128` to completion with a scoped
     `kmir prove-rs` rerun, then reassess whether the remaining non-float
     breadth is finally narrow enough for a stronger verdict.
  2. `0028-flt2dec`: keep the restored real prefix slice in place, simplify
     only the copied `if exp >= buf.len()` test so `buf.len()` becomes concrete
     for `b"1234", exp = 2`, and capture the first leaf beyond that select.
  3. `0026-rc`: replace the unstable `Box::write(...)` witness setup with a
     stable `MaybeUninit` plus raw-write / cast-free projection path that keeps
     the same `System` provenance.
- `0012` and `0013` are terminal and should not be returned to the active batch
  unless the user explicitly asks to reopen blocked challenges.

## Batch Selection Rationale

- `0011-floats-ints`: now sits at `2.98 / 3`; the remaining non-float gap is
  narrower than before, and the next bounded slice is now `unchecked_shl_i8`.
- `0026-rc`: the refcount family still matters for `0027-arc`, but the current
  leverage point is the direct `CastKind::Transmute` leaf.
- `0028-flt2dec`: the copied branch select is no longer the frontier; the
  current leverage point is the deeper `core::slice::index` failure.

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
- In the latest cycle, `0011` and `0028` both produced new committed evidence:
  `0011` extended the `unchecked_shl` family through a passing
  `unchecked_shl_u64` slice and then retargeted to `unchecked_shl_u128`, while
  `0028` restored the
  real prefix slice and moved the frontier to the copied
  `if exp >= buf.len()` select at line 76.
- `0026` still remains bottlenecked on the witness-construction path: the
  newest `MaybeUninit` rewrite attempt failed before proof construction because
  `Box::write(...)` is unstable on this toolchain, so the restart point below
  now targets a stable raw-write alternative rather than another blind rerun.
- If this run stops here, treat that as an external runtime/tool constraint for
  this turn, not as a challenge-level terminal verdict.

## Challenge State Index

See `docs/verify-rust-std/portfolio/current-states.tsv`.
