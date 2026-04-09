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

- `0011-floats-ints` -> `IN PROGRESS`
- `0012-nonzero` -> `IN PROGRESS`
- `0013-cstr` -> `IN PROGRESS`

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

## Challenge State Index

See `docs/verify-rust-std/portfolio/current-states.tsv`.
