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

- `0011-floats-ints` -> `IN PROGRESS` (`2.7 / 3`)
- `0012-nonzero` -> `IN PROGRESS` (`2.0 / 3`)
- `0013-cstr` -> `IN PROGRESS` (`2.0 / 3`)

## Current Active State

- `0011-floats-ints`: branch-local proof passes now cover
  `unchecked_add_u8`, `unchecked_neg_i8`, `unchecked_sub_u8`, and
  `wrapping_shl_u8`; float `to_int_unchecked` remains precisely blocked by the
  stuck `fabsf32` / `fabsf64` frontier; next action is another narrow integer
  slice or a stronger integer-readiness boundary against the float blocker.
- `0012-nonzero`: prerequisite semantic baseline is ported and validated;
  the exact `u8 -> Option<NonZeroU8>` reproduction now isolates the
  `NonZero::new` blocker beyond plain transparent-wrapper support; next action
  is a lower-level byte/layout-driven transmute investigation or a runtime
  `lookupTy(TY_TO)` shape check for the niche cast.
- `0013-cstr`: prerequisite cross-crate support is ported; the exact-byte
  `CloneToUninit` harness exists and standalone prove targets now compile as
  edition 2024; the remaining shared frontier is linked-SMIR body supply for
  `core::ffi::CStr::from_bytes_with_nul`; next action is a minimal donor-link
  path or a precise blocker checkpoint for that constructor body gap.

## Exact Restart Point If The Run Stops Now

- Resume the current batch: `0011-floats-ints`, `0012-nonzero`,
  `0013-cstr`.
- Restart priority inside the current batch:
  1. `0012-nonzero`: continue from the checkpointed niche-transmute blocker
     with a layout-driven or `lookupTy(TY_TO)`-driven investigation on the
     exact `u8 -> Option<NonZeroU8>` cast.
  2. `0013-cstr`: continue from the edition-2024 checkpoint and either land a
     focused donor-link path for `core::ffi::CStr::from_bytes_with_nul` or
     record that constructor-body gap as the exact blocker.
  3. `0011-floats-ints`: run the next cheapest narrow integer slice after
     `unchecked_sub_u8` to keep widening the integer matrix while the float
     blocker stays unchanged.
- Do not reseat the batch until these three leave `IN PROGRESS`.

## Batch Selection Rationale

- `0011-floats-ints`: direct `mir-semantics` reference PR exists in [#985](https://github.com/runtimeverification/mir-semantics/pull/985); likely to yield either a precise float-capability blocker or a near-terminal readiness assessment quickly.
- `0012-nonzero`: strong public solution set exists in verify-rust-std and a local historical branch exists; high probability of moving to `READY FOR SUBMISSION`.
- `0013-cstr`: strong public solution set exists and the historical local branch includes linker/body-resolution work that may accelerate later challenges.

## Exact Next Batch If Interrupted After The Current Batch

- `0028-flt2dec`
- `0026-rc`
- `0027-arc`

Rationale:

- `0028-flt2dec` reuses float-support findings from `0011`.
- `0026-rc` and `0027-arc` share reference-counting patterns and both have strong public solution material for reuse.

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
