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

- `0011-floats-ints` -> `IN PROGRESS` (`2.4 / 3`)
- `0012-nonzero` -> `IN PROGRESS` (`1.8 / 3`)
- `0013-cstr` -> `IN PROGRESS` (`1.9 / 3`)

## Current Active State

- `0011-floats-ints`: historical artifact set ported; two distinct integer
  proof slices pass (`unchecked_add_u8`, `unchecked_neg_i8`); float path
  remains structurally blocked by backend float intrinsic support; next action
  is broader integer coverage.
- `0012-nonzero`: prerequisite semantic baseline is ported and validated;
  challenge-local Part 1 artifacts exist; current narrowed frontiers are
  `castKindTransmute` in `NonZero::new` and `castKindPtrToPtr` in
  `NonZero::from_mut`; next action is a minimal semantic-fix or sharper blocker
  reduction on one of those cast frontiers.
- `0013-cstr`: prerequisite cross-crate support is ported; challenge-local
  artifacts exist for `from_ptr`, `Index<RangeFrom<usize>>`, and
  `from_bytes_with_nul_unchecked`; remaining required coverage includes
  `strlen` and exact-byte `CloneToUninit`; next action is remaining coverage
  plus proof-frontier reduction.

## Exact Restart Point If The Run Stops Now

- Resume the current batch: `0011-floats-ints`, `0012-nonzero`,
  `0013-cstr`.
- Restart priority inside the current batch:
  1. `0012-nonzero`: continue the interrupted semantic-fix attempt on the
     `NonZero::new` / `NonZero::from_mut` cast frontier.
  2. `0013-cstr`: add remaining `CStr` coverage (`strlen`, exact-byte
     `CloneToUninit`) or discharge one of the current proof frontiers.
  3. `0011-floats-ints`: run another narrow integer proof slice to broaden
     coverage beyond the two completed proofs.
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

- One additional semantic-fix attempt on `0012-nonzero` remained live after a
  full wait window and was stopped to preserve a clean interruption checkpoint.
- This is treated as an external runtime/tool constraint for this turn, not as
  a challenge-level terminal verdict.

## Challenge State Index

See `docs/verify-rust-std/portfolio/current-states.tsv`.
