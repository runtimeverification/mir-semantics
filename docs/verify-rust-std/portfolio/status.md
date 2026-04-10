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
- `0028-flt2dec` -> `IN PROGRESS` (`1.9 / 3`)
- `0026-rc` -> `IN PROGRESS` (`1.7 / 3`)

## Current Active State

- `0011-floats-ints`: fourteen branch-local proof slices now pass
  (`unchecked_add_u8`, `unchecked_neg_i8`, `unchecked_sub_u8`,
  `wrapping_shl_u8`, `wrapping_shr_u8`, `widening_mul_u8`,
  `carrying_mul_u8`, `unchecked_mul_u8`, `unchecked_mul_u16`,
  `unchecked_mul_u32`, `unchecked_mul_u64`, `unchecked_shl_u8`,
  `unchecked_shl_u16`, `unchecked_shl_u32`); float
  `to_int_unchecked` remains blocked by the precise `fabsf32` / `fabsf64`
  frontier, and the latest `unchecked_shr` diagnostics found no smaller
  branch-worthy subcase than `unchecked_shr_u8`, with the family collapsing to
  the same `binOpShrUnchecked` surface; the refreshed planner keeps
  `unchecked_shr` parked and retargets the next bounded slice to
  `unchecked_shl_u64`.
- `0028-flt2dec`: restoring the real prefix slice `&buf[..exp]` invalidates
  the earlier saved terminal taken-arm slice and moves the first validated
  stuck leaf to the copied `if exp >= buf.len()` `#selectBlock` at
  `digits_to_dec_str_probe.rs:76`, with predicate
  `#applyBinOp ( binOpGe , 2 , #applyUnOp ( unOpPtrMetadata , ... ) )`; this is
  still copied `flt2dec` control flow, not a backend float leaf, and the next
  bounded task is to simplify only that `buf.len()` test and record the first
  leaf beyond it.
- `0026-rc`: the first contract/entrypoint audit is committed, a direct
  `Rc::from_raw_in` witness harness now exists, and the current blocker has
  been narrowed to a direct-witness `CastKind::Transmute` leaf; the latest
  `MaybeUninit`-backed witness attempt failed before proof construction with
  unstable `Box::write(...)` (`E0658`), so the next action is a stable
  `MaybeUninit` plus raw-write `System` witness that avoids both the unstable
  helper and the same transmute shape.

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
  1. `0011-floats-ints`: run `unchecked_shl_u64` to completion with a scoped
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
  narrower than before, but the current evidence still needs one more bounded
  `unchecked_shl` extension before a stronger verdict is justified.
- `0028-flt2dec`: continues to yield reusable probe-narrowing patterns and is
  still producing reusable probe-narrowing patterns, but the restored-prefix
  slice shows the branch is not yet past copied control-flow scaffolding.
- `0026-rc`: the refcount family still matters for `0027-arc`, but current
  evidence says its next leverage point is a stable witness rewrite rather than
  immediate API expansion.

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
  `unchecked_shl_u32` slice and then retargeted to `unchecked_shl_u64`, while
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
