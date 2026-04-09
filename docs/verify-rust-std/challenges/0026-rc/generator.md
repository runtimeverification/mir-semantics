# Generator Record: Challenge 0026

Ownership:

- Generator owns this file and the implementation work for this challenge.
- Generator must not edit `evaluator.md` or `rubric.md`.
- Generator should treat planner and evaluator edits as authoritative inputs,
  not as files to rewrite.

## Inputs

- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0026-rc`
- Planner record: `docs/verify-rust-std/challenges/0026-rc/planner.md`
- Evaluator record: `docs/verify-rust-std/challenges/0026-rc/evaluator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0026-rc/rubric.md`

## Scope Boundary

- Authorized code area: this challenge branch only.
- Default repository scope: `runtimeverification/mir-semantics`
- Allowed secondary scope: `runtimeverification/stable-mir-json` when required
- Exceptional scope: `runtimeverification/haskell-backend` only with explicit
  justification logged here and in the evaluator record

## Work Log

- Bootstrap record created by orchestrator.
- 2026-04-09: Audited the latest challenge page and the local `nightly-2024-11-29` `alloc/src/rc.rs` source for all 12 public `unsafe` `alloc::rc` APIs.
- 2026-04-09: Added `docs/verify-rust-std/challenges/0026-rc/contract-map.md` with a source-grounded contract matrix, invariant clustering, and proof-entrypoint mapping.
- 2026-04-09: Selected the smallest first tranche inside the planner-approved raw-pointer/refcount family:
  - proof roots: `Rc::from_raw_in`, `Rc::increment_strong_count_in`, `Rc::decrement_strong_count_in`, `Weak::from_raw_in`
  - immediate wrapper follow-ons: `Rc::from_raw`, `Rc::increment_strong_count`, `Rc::decrement_strong_count`, `Weak::from_raw`

## Files Touched

- `docs/verify-rust-std/challenges/0026-rc/contract-map.md`
- `docs/verify-rust-std/challenges/0026-rc/workpad.md`
- `docs/verify-rust-std/challenges/0026-rc/generator.md`

## Validation Evidence

- `rustc --print sysroot`
- `cat rust-toolchain.toml`
- `nl -ba /home/zhaoji/.rustup/toolchains/nightly-2024-11-29-x86_64-unknown-linux-gnu/lib/rustlib/src/rust/library/alloc/src/rc.rs | sed -n '1160,1695p'`
- `nl -ba /home/zhaoji/.rustup/toolchains/nightly-2024-11-29-x86_64-unknown-linux-gnu/lib/rustlib/src/rust/library/alloc/src/rc.rs | sed -n '1730,2025p'`
- `nl -ba /home/zhaoji/.rustup/toolchains/nightly-2024-11-29-x86_64-unknown-linux-gnu/lib/rustlib/src/rust/library/alloc/src/rc.rs | sed -n '3048,3278p'`
- `git diff --check -- docs/verify-rust-std/challenges/0026-rc/contract-map.md docs/verify-rust-std/challenges/0026-rc/workpad.md`

## Commit Inventory

- `87a669dc` `docs(verify-rust-std): map challenge 0026 rc contracts`

## Blockers

- No confirmed blocker for the selected raw-pointer/refcount tranche on this branch.
- Soft risks intentionally left out of tranche 1:
  - `assume_init` may still need expressivity beyond the current type system.
  - `Rc::get_mut_unchecked` likely needs stronger alias and lifetime reasoning than the raw-pointer tranche.
