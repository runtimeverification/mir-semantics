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
- 2026-04-09: Rewrote `kmir/src/tests/integration/data/prove-rs/rc-from-raw-in.rs` to remove the `Rc::new_in` / `Rc::into_raw` detour. The harness now allocates a local `#[repr(C)] RcInnerWitness<u32>` under `System`, takes the raw pointer to its `value` field, and passes that pointer directly to `Rc::from_raw_in`.
- 2026-04-09: The rewritten harness no longer hits `std::boxed::Box::<std::rc::RcInner<u32>, std::alloc::System>::try_new_uninit_in`; instead, the proof frontier moves to a terminal state whose `<k>` begins with `thunk(_)_RT-DATA_Value_Evaluation(#cast(_,_,_,_)_RT-DATA_Evaluation_Evaluation_CastKind_MaybeTy_Ty(..., CastKind::Transmute, ...))`.
- 2026-04-09: Current decision: stop at this exact boundary. Do not widen into `Rc::increment_strong_count_in`, `Rc::decrement_strong_count_in`, or `Weak::from_raw_in` until the direct witness is reduced further or the cast leaf is discharged.
- 2026-04-10: Restored the worktree to `HEAD`, removed `tmp.*` artifacts, rebuilt the missing `mir-semantics.haskell` and `mir-semantics.{llvm,llvm-library}` kdist targets, and restarted `uv --project kmir run kmir prove ... --proof-dir /tmp/rc-from-raw-in-proof-rawalloc3 --verbose --terminate-on-thunk`.
- 2026-04-10: That rerun was interrupted before any new proof leaf or terminal node was captured. No new frontier was established, and no code change was kept.
- 2026-04-10: Replaced the unstable `Box::write(...)` witness path with a stable `Box::new_uninit_in(System)` + raw `ptr::write` + `assume_init` witness in both `kmir/src/tests/integration/data/prove-rs/rc-from-raw-in.rs` and the challenge-local mirror `kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-from-raw-in-frontier-fail.rs`. Running `uv --project kmir run kmir prove /home/zhaoji/projs/mir-semantics-vrs/challenges/0026-rc/kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-from-raw-in-frontier-fail.rs --proof-dir /tmp/rc-from-raw-in-frontier-proof-stablemaybeuninit --verbose --terminate-on-thunk` reached proof construction but still terminated at the same `#cast(_,_,_,_)_RT-DATA_Evaluation_Evaluation_CastKind_MaybeTy_Ty` / `CastKind::Transmute` frontier in node 4. No semantic fix was introduced.
- 2026-04-10: Added `kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-new-in-frontier-fail.rs` as the smallest challenge-local reproducer for the current `Box::<std::rc::RcInner<u32>, std::alloc::System>::try_new_uninit_in` transmute frontier. Running `uv --project kmir run kmir prove /home/zhaoji/projs/mir-semantics-vrs/challenges/0026-rc/kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-new-in-frontier-fail.rs --proof-dir /tmp/rc-new-in-frontier-proof --verbose --terminate-on-thunk` still failed, and the terminal node 4 shows the same `#cast(_,_,_,_)_RT-DATA_Evaluation_Evaluation_CastKind_MaybeTy_Ty` / `CastKind::Transmute` leaf. No semantic fix was introduced.

## Files Touched

- `docs/verify-rust-std/challenges/0026-rc/contract-map.md`
- `docs/verify-rust-std/challenges/0026-rc/workpad.md`
- `docs/verify-rust-std/challenges/0026-rc/generator.md`
- `kmir/src/tests/integration/data/prove-rs/rc-from-raw-in.rs`
- `kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-from-raw-in-frontier-fail.rs`

## Validation Evidence

- `rustc --print sysroot`
- `cat rust-toolchain.toml`
- `nl -ba /home/zhaoji/.rustup/toolchains/nightly-2024-11-29-x86_64-unknown-linux-gnu/lib/rustlib/src/rust/library/alloc/src/rc.rs | sed -n '1160,1695p'`
- `nl -ba /home/zhaoji/.rustup/toolchains/nightly-2024-11-29-x86_64-unknown-linux-gnu/lib/rustlib/src/rust/library/alloc/src/rc.rs | sed -n '1730,2025p'`
- `nl -ba /home/zhaoji/.rustup/toolchains/nightly-2024-11-29-x86_64-unknown-linux-gnu/lib/rustlib/src/rust/library/alloc/src/rc.rs | sed -n '3048,3278p'`
- `git diff --check -- docs/verify-rust-std/challenges/0026-rc/contract-map.md docs/verify-rust-std/challenges/0026-rc/workpad.md`
- `uv --project kmir run kmir prove /home/zhaoji/projs/mir-semantics-vrs/challenges/0026-rc/kmir/src/tests/integration/data/prove-rs/rc-from-raw-in.rs --proof-dir /tmp/rc-from-raw-in-proof --verbose --terminate-on-thunk`
- `uv --project kmir run kmir prove /home/zhaoji/projs/mir-semantics-vrs/challenges/0026-rc/kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-from-raw-in-frontier-fail.rs --proof-dir /tmp/rc-from-raw-in-frontier-proof-stablemaybeuninit --verbose --terminate-on-thunk`
- `sed -n '1,240p' /tmp/rc-from-raw-in-proof/rc-from-raw-in.main/proof.json`
- `sed -n '1,260p' /tmp/rc-from-raw-in-proof/rc-from-raw-in.main/kcfg/nodes/3.json`
- `sed -n '1,260p' /tmp/rc-from-raw-in-proof/rc-from-raw-in.main/kcfg/nodes/4.json`
- `uv --project kmir run kmir prove ... --proof-dir /tmp/rc-from-raw-in-proof-rawalloc3 --verbose --terminate-on-thunk`
- `sed -n '1,240p' /tmp/rc-from-raw-in-frontier-proof-stablemaybeuninit/rc-from-raw-in-frontier-fail.main/proof.json`
- `sed -n '1,260p' /tmp/rc-from-raw-in-frontier-proof-stablemaybeuninit/rc-from-raw-in-frontier-fail.main/kcfg/nodes/4.json`

## Commit Inventory

- `87a669dc` `docs(verify-rust-std): map challenge 0026 rc contracts`
- `7abe7dcd` `test(verify-rust-std): seed rc from_raw_in root harness`
- `pending` `test(verify-rust-std): rewrite rc from_raw_in root harness to stable MaybeUninit witness`

## Blockers

- No confirmed blocker for the selected raw-pointer/refcount tranche on this branch.
- New exact blocker for the stable `MaybeUninit` witness shape:
  - the proof graph still terminates at a `#cast(_,_,_,_)_RT-DATA_Evaluation_Evaluation_CastKind_MaybeTy_Ty` thunk with `CastKind::Transmute`
  - the terminal node evidence is in `/tmp/rc-from-raw-in-frontier-proof-stablemaybeuninit/rc-from-raw-in-frontier-fail.main/kcfg/nodes/4.json`
- Soft risks intentionally left out of tranche 1:
  - `assume_init` may still need expressivity beyond the current type system.
  - `Rc::get_mut_unchecked` likely needs stronger alias and lifetime reasoning than the raw-pointer tranche.
