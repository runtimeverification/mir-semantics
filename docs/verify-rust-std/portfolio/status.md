# Portfolio Status

Last orchestrator checkpoint: 2026-04-10 UTC

## V2 Operating Mode

- Phase order is now breadth-first:
  1. quickly define challenge-local proof harnesses and per-function coverage
     tables across the portfolio,
  2. run those harnesses to obtain the first real frontier or passing result,
  3. classify failures by likely owning repository,
  4. only then prioritize deeper shared semantic fixes.
- Proof harnesses and minimal reproducers must remain separate. Concrete-value
  reproducers do not count as verification.
- Draft PR descriptions, challenge-local docs, and portfolio trackers must all
  expose per-function coverage status, blocker class, and replay commands.

## Portfolio Trackers

- Harness coverage:
  `docs/verify-rust-std/portfolio/harness_coverage.tsv`
- Blocker classification:
  `docs/verify-rust-std/portfolio/blocker_classification.tsv`
- Shared blocker families:
  `docs/verify-rust-std/portfolio/shared_blockers.md`

## Terminal-State Rule

The portfolio is complete only when every published challenge is in one of:

- `BLOCKED`
- `CONDITIONALLY READY`
- `READY FOR SUBMISSION`
- `SUBMITTED / CLOSED`

`BOOTSTRAP` and `IN PROGRESS` are explicitly non-terminal.

## Current Batch

- `0026-rc` -> `IN PROGRESS` (`1.9 / 3`)
- `0028-flt2dec` -> `IN PROGRESS` (`1.9 / 3`)
- `0027-arc` -> `IN PROGRESS` (`2.0 / 3`)

## Current Breadth-First Priority

- Keep the current technical batch (`0026`, `0027`, `0028`) because it is
  already producing frontier movement.
- In parallel, backfill missing per-function coverage docs on already-active
  blocked challenges (`0012`, `0013`).
- Then start the first harness-sweep wave on bootstrap challenges with the best
  expected leverage for reusable patterns:
  `0029-boxed`, `0001-core-transmutation`, `0014-convert-num`.

## Current Active State

- `0026-rc`: the branch now has a verification-shaped symbolic proof harness
  `rc-from-raw-in.rs` plus a canonical one-line frontier reproducer
  `rc-new-in-frontier-fail.rs` and the broader audit reproducer
  `rc-from-raw-in-frontier-fail.rs`; a small transparent-wrapper transmute
  rule moved both the one-line reproducer and `verify_rc_from_raw_in` past the
  old helper-level transmute leaf to node `3` at
  `#setUpCalleeData(monoItemFn(... name: symbol("malloc"), body: noBody), ...)`.
  The challenge remains `IN PROGRESS` at `1.9 / 3`.
- `0028-flt2dec`: success table, stronger replay collector, and explicit CI
  discoverability now exist; the copied `if exp >= buf.len()` select was
  passed; then a narrow follow-up rule moved the probe from the old thunked
  unsize-cast leaf to the concrete dereference frontier
  `#traverseProjection ( toLocal ( 2 ) , AllocRef (...) , projectionElemDeref .ProjectionElems , .Contexts )`.
  Score remains `1.9 / 3`; the next action is to identify which value in local
  `2` is being dereferenced and classify or fix that concrete `AllocRef` leaf.
- `0027-arc`: activated into the current batch because it is the strongest
  reuse candidate from `0026-rc`; the first symbolic proof harness for
  `Arc::from_raw_in` now exists, and it is now paired with a dedicated
  smaller frontier reproducer `arc-from-raw-in-frontier-fail.rs`; after
  replaying the same transparent-wrapper transmute fix from `0026`, both proof
  paths now stop at the same node `3` `malloc/noBody` frontier. The challenge
  remains `IN PROGRESS` at `2.0 / 3`, and the next action is to use that
  reproducer to validate any shared allocator-body fix candidate before
  widening the Arc tranche.

## Cross-Challenge Semantic Pattern

- `0026-rc` and `0027-arc` now expose the same allocator-body failure mode:
  after the shared transparent-wrapper transmute fix, both proof-harness
  symbols now bottom out at node `3` on
  `#setUpCalleeData(monoItemFn(... name: symbol("malloc"), body: noBody), ...)`.
  `0026` remains the canonical lead reproducer because its current frontier
  case is one line long; `0027` is the follower validation branch for the same
  allocator-body family.
- `0012-nonzero` remains a separate niche-cast family until a lower-level
  byte/layout path or `lookupTy(TY_TO)`-shape explanation is available.
- `0013-cstr` remains a linker/body-supply plumbing family until donor-linked
  root-name preservation is repaired.
- `0028-flt2dec` currently exposes a concrete `AllocRef` dereference frontier
  in library scaffolding rather than a formatter-owned leaf.

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

- Resume the current technical batch: `0026-rc`, `0028-flt2dec`, `0027-arc`.
- Restart priority inside the current batch:
  1. `0026-rc`: continue from the split proof-harness / reproducer shape and
     attack the remaining node `3` allocator-body frontier reached by
     `verify_rc_from_raw_in`, starting from the canonical one-line
     `rc-new-in-frontier-fail.rs` witness.
  2. `0027-arc`: preserve `arc-from-raw-in.rs` as the verification harness and
     use `arc-from-raw-in-frontier-fail.rs` to validate any shared allocator-
     body fix candidate for the `malloc/noBody` family.
  3. `0028-flt2dec`: keep `digits_to_dec_str_probe.rs` fixed and classify or
     fix the concrete `AllocRef` dereference leaf on local `2`.
- `0011` is now terminal and should not be returned to the active batch unless
  the user explicitly reopens it.
- `0012` and `0013` are terminal and should not be returned to the active batch
  unless the user explicitly asks to reopen blocked challenges.
- In parallel with the technical batch, continue the v2 harness-sweep queue:
  1. backfill per-function coverage docs for `0012-nonzero` and `0013-cstr`
  2. launch harness-definition work on `0029-boxed`
  3. then `0001-core-transmutation`
  4. then `0014-convert-num`

## Batch Selection Rationale

- `0026-rc`: the refcount family still matters for `0027-arc`, and the current
  leverage point is now sharper because the proof harness / reproducer split is
  correct and the frontier is isolated to a canonical one-line reproducer on
  the proper symbol, now at a shared allocator-body leaf rather than the old
  transmute thunk.
- `0028-flt2dec`: the copied branch select is no longer the frontier; the
  current leverage point is the concrete `AllocRef` dereference, and the
  evaluator has now confirmed the existing probe is already minimal enough.
- `0027-arc`: activated immediately after `0011` closed because it is the
  strongest reuse target from the `Rc` raw-pointer / refcount contract family,
  and it now confirms the shared allocator-helper transmute blocker family with
  a dedicated reproducer rather than remaining at bootstrap.

## Next Harness-Sweep Queue

- `0029-boxed`
- `0001-core-transmutation`
- `0014-convert-num`
- `0015-intrinsics-simd`
- `0016-iter`

Rationale:

- `0029-boxed` can reuse allocator/raw-pointer patterns already active in
  `0026` and `0027`.
- `0001-core-transmutation` is the strongest reusable transmute-family target
  once the portfolio has explicit coverage tables everywhere.
- `0014-convert-num` and `0015-intrinsics-simd` are still bootstrap-only and
  benefit from early harness definition before deeper semantic work.
- `0016-iter` is the next breadth-first candidate after the initial sweep set.

## Portfolio Inventory

- Challenge worktrees created: `29`
- Challenge draft PRs opened: `29`
- Dedicated challenge branches created: `29`
- Observed agent thread cap: `6`

## Current Run Constraint

- The portfolio rubric and templates now require explicit Success Criteria
  coverage tables, a verification-harness versus frontier-reproducer split,
  and minimal reproducer evidence before semantic fixes.
- The v2 operating mode additionally requires per-function harness/spec
  coverage to be visible in branch docs, PR descriptions, and portfolio-level
  trackers before deeper semantic diagnosis is treated as complete.
- Long proof / linkage loops on `0012-nonzero` and `0013-cstr` required
  checkpoint-style finishes to avoid leaving dirty experimental state in the
  worktrees.
- The observed live-agent cap remains `6`, which forced repeated close/reopen
  cycles for planner/generator/evaluator passes.
- In the latest cycle, `0011` was closed by user direction as superseded by
  `#985`; `0026` moved from the old helper transmute frontier to a shared
  `malloc/noBody` allocator-body frontier; `0027` independently confirmed the
  same frontier after replaying the fix; and `0028` moved from the old thunked
  unsize-cast leaf to a concrete `AllocRef` dereference frontier.
- If this run stops here, treat that as an external runtime/tool constraint for
  this turn, not as a challenge-level terminal verdict.

## Challenge State Index

See `docs/verify-rust-std/portfolio/current-states.tsv`.
