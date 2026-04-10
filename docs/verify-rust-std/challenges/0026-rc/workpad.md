# Challenge 0026 Workpad

## Current State

- Branch: `verify-rust-std/reexec-0026-rc`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0026-rc`
- Draft PR: exists.
- Evaluator: active / in progress.
- Local status: first audit slice committed in `87a669dc`; the `Rc::from_raw_in` root harness remains the current branch frontier, and the same evidence is now mirrored by the challenge-local file `kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-from-raw-in-frontier-fail.rs`.
- Interrupt checkpoint: the worktree was restored to `HEAD`, `tmp.*` artifacts were removed, the missing `mir-semantics.haskell` and `mir-semantics.{llvm,llvm-library}` kdist targets were rebuilt, and `uv --project kmir run kmir prove ... --proof-dir /tmp/rc-from-raw-in-proof-rawalloc3 --verbose --terminate-on-thunk` was started but interrupted before any new proof leaf or terminal node was captured.
- Interrupt outcome: no new frontier was established and no code change was kept from that attempt.
- Latest blocker checkpoint: the newest `MaybeUninit`-backed witness attempt for `kmir/src/tests/integration/data/prove-rs/rc-from-raw-in.rs` passed `git diff --check -- kmir/src/tests/integration/data/prove-rs/rc-from-raw-in.rs` but failed before proof construction with `error[E0658]: use of unstable library feature 'box_uninit_write'` at `Box::write(...)`; no proof leaf or terminal node was reached and no code changes were retained.

## Confirmed Inputs

- Challenge page: `https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0026-rc.md`
- Tracking issue: `#382`
- Artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0026-rc`
- Success table: `docs/verify-rust-std/challenges/0026-rc/success-criteria.md`
- Public guidance: issue #382 comments indicate most contracts were already written by the original contributor, with a possible remaining dependency on the Kani update referenced as `model-checking/kani#4427`.

## Next Action

- The next exact boundary is the new direct-witness leaf at `#cast(_,_,_,_)_RT-DATA_Evaluation_Evaluation_CastKind_MaybeTy_Ty` with `CastKind::Transmute` in the root proof graph; if work continues, shrink the harness witness one step further instead of widening into other `Rc` APIs.

## What Needs To Be Captured

- Which of the 12 public unsafe APIs already has a clear source SAFETY comment.
- Which API cluster shares the same invariant set and therefore should be tackled together.
- Whether any chosen function depends on an upstream tool/backend update.

## Working Notes

- Keep the plan narrowed to one tranche only.
- Do not expand into code or proof implementation from this file.
- Use this workpad to record the chosen tranche before any generator work starts.
- The rewritten root harness no longer calls `Rc::new_in`; it allocates a `repr(C)` `RcInnerWitness<u32>` under `System`, converts it to a raw pointer, and feeds `Rc::from_raw_in` directly from the witness value field.
- The previous `std::boxed::Box::<std::rc::RcInner<u32>, std::alloc::System>::try_new_uninit_in` blocker is gone.
- The new frontier is the direct witness path itself, which terminates in `#cast(_,_,_,_)_RT-DATA_Evaluation_Evaluation_CastKind_MaybeTy_Ty` with `CastKind::Transmute` rather than inside `Rc::new_in`.
- The latest `MaybeUninit` witness revision never reached proof construction because `Box::write(...)` is still gated behind unstable library feature `box_uninit_write`.

## Audit Result

- Contract map recorded in `docs/verify-rust-std/challenges/0026-rc/contract-map.md`.
- Success criteria recorded in `docs/verify-rust-std/challenges/0026-rc/success-criteria.md`.
- Source basis pinned to `nightly-2024-11-29` `alloc/src/rc.rs` from the local toolchain.
- The 12 public `unsafe` APIs fall into four invariant families:
  - raw pointer recovery and refcount transition: 8 APIs
  - initialization transition: 2 APIs
  - aliasing and type identity: 1 API
  - dynamic type recovery: 1 API

## Proof Frontier

- Harness: `kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-from-raw-in-frontier-fail.rs`
- Validation command: `uv --project kmir run kmir prove /home/zhaoji/projs/mir-semantics-vrs/challenges/0026-rc/kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-from-raw-in-frontier-fail.rs --proof-dir /tmp/rc-from-raw-in-frontier-proof --verbose --terminate-on-thunk`
- Frontier evidence:
  - `proof.json` / `kcfg/nodes/3.json`
  - `proof.json` / `kcfg/nodes/4.json`
- Leaf 4 is now a terminal proof state whose `<k>` begins with `thunk(_)_RT-DATA_Value_Evaluation(#cast(_,_,_,_)_RT-DATA_Evaluation_Evaluation_CastKind_MaybeTy_Ty(..., CastKind::Transmute, ...))`.
- The interrupted `raw-memory-witness` rerun used `/tmp/rc-from-raw-in-proof-rawalloc3` but did not reach a new leaf or terminal node before being stopped.
- The later `MaybeUninit`-backed witness attempt never reached proof construction and therefore produced no proof leaf or terminal node.

## Selected First Tranche

- Proof roots:
  - `Rc::from_raw_in`
  - `Rc::increment_strong_count_in`
  - `Rc::decrement_strong_count_in`
  - `Weak::from_raw_in`
- Immediate wrapper follow-ons:
  - `Rc::from_raw`
  - `Rc::increment_strong_count`
  - `Rc::decrement_strong_count`
  - `Weak::from_raw`

## Selection Rationale

- This stays exactly inside the planner-selected raw-pointer/refcount family.
- Four proof roots advance eight of the twelve public `unsafe` contracts because the stable `Global` APIs are thin wrappers over the allocator-general `_in` bodies.
- `Rc::increment_strong_count_in` and `Rc::decrement_strong_count_in` both depend on successful ownership recovery from `Rc::from_raw_in`, so the tranche has one clear dependency spine.
- The remaining four public `unsafe` APIs would immediately widen scope into initialization, aliasing, or dynamic-type reasoning.

## Known Soft Risks

- Challenge guidance still flags `assume_init` as potentially hard to express in the current type system, but that does not block the selected tranche.
- The current root witness still needs a smaller direct allocator/raw-pointer shape if this proof is to advance past the `#cast` transmute leaf.
