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
- 2026-04-09: Added `kmir/src/tests/integration/data/prove-rs/rc-from-raw-in.rs` as the first root harness for the tranche. It round-trips a `Rc<u32>` through `Rc::into_raw` and `Rc::from_raw_in` using `std::alloc::System`.
- 2026-04-09: Proof frontier for the root harness: the run reaches `std::boxed::Box::<std::rc::RcInner<u32>, std::alloc::System>::try_new_uninit_in` and stalls on the `castKindTransmute` thunk in `core/src/alloc/layout.rs:140`. This is a precise blocker on the current harness shape, not a tranche-wide semantic failure.
- 2026-04-09: Decision: keep scope inside the raw-pointer/refcount tranche and stop before touching increment/decrement or weak recovery. The next step is to remove the `Rc::new_in` / `Box::try_new_uninit_in` dependency so `Rc::from_raw_in` is exercised directly against a raw-pointer/allocator witness.

## Files Touched

- `docs/verify-rust-std/challenges/0026-rc/contract-map.md`
- `docs/verify-rust-std/challenges/0026-rc/workpad.md`
- `docs/verify-rust-std/challenges/0026-rc/generator.md`
- `kmir/src/tests/integration/data/prove-rs/rc-from-raw-in.rs`

## Validation Evidence

- `rustc --print sysroot`
- `cat rust-toolchain.toml`
- `nl -ba /home/zhaoji/.rustup/toolchains/nightly-2024-11-29-x86_64-unknown-linux-gnu/lib/rustlib/src/rust/library/alloc/src/rc.rs | sed -n '1160,1695p'`
- `nl -ba /home/zhaoji/.rustup/toolchains/nightly-2024-11-29-x86_64-unknown-linux-gnu/lib/rustlib/src/rust/library/alloc/src/rc.rs | sed -n '1730,2025p'`
- `nl -ba /home/zhaoji/.rustup/toolchains/nightly-2024-11-29-x86_64-unknown-linux-gnu/lib/rustlib/src/rust/library/alloc/src/rc.rs | sed -n '3048,3278p'`
- `git diff --check -- docs/verify-rust-std/challenges/0026-rc/contract-map.md docs/verify-rust-std/challenges/0026-rc/workpad.md`
- `uv --project kmir run kmir prove /home/zhaoji/projs/mir-semantics-vrs/challenges/0026-rc/kmir/src/tests/integration/data/prove-rs/rc-from-raw-in.rs --proof-dir /tmp/rc-from-raw-in-proof --verbose --terminate-on-thunk`
- `uv --project kmir run kmir show rc-from-raw-in.main --proof-dir /tmp/rc-from-raw-in-proof --leaves --statistics`

## Commit Inventory

- `87a669dc` `docs(verify-rust-std): map challenge 0026 rc contracts`
- `7abe7dcd` `test(verify-rust-std): seed rc from_raw_in root harness`

## Blockers

- No confirmed blocker for the selected raw-pointer/refcount tranche on this branch.
- Soft risks intentionally left out of tranche 1:
  - `assume_init` may still need expressivity beyond the current type system.
  - `Rc::get_mut_unchecked` likely needs stronger alias and lifetime reasoning than the raw-pointer tranche.
- Current root harness blocker:
  - `Rc::new_in` pulls in `std::boxed::Box::<std::rc::RcInner<u32>, std::alloc::System>::try_new_uninit_in`
  - the proof leaf stops at `core/src/alloc/layout.rs:140` in a `castKindTransmute` thunk
  - the blocker is harness shape, not the `Rc::from_raw_in` body itself
