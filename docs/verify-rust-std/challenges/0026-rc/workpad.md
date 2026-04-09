# Challenge 0026 Workpad

## Current State

- Branch: `verify-rust-std/reexec-0026-rc`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0026-rc`
- Local status: doc-only audit in progress; no code or proof artifacts touched.

## Confirmed Inputs

- Challenge page: `https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0026-rc.md`
- Tracking issue: `#382`
- Artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0026-rc`
- Public guidance: issue #382 comments indicate most contracts were already written by the original contributor, with a possible remaining dependency on the Kani update referenced as `model-checking/kani#4427`.

## Next Action

- Turn the selected raw-pointer/refcount tranche into proof or harness seeds rooted at `Rc::from_raw_in`.

## What Needs To Be Captured

- Which of the 12 public unsafe APIs already has a clear source SAFETY comment.
- Which API cluster shares the same invariant set and therefore should be tackled together.
- Whether any chosen function depends on an upstream tool/backend update.

## Working Notes

- Keep the plan narrowed to one tranche only.
- Do not expand into code or proof implementation from this file.
- Use this workpad to record the chosen tranche before any generator work starts.

## Audit Result

- Contract map recorded in `docs/verify-rust-std/challenges/0026-rc/contract-map.md`.
- Source basis pinned to `nightly-2024-11-29` `alloc/src/rc.rs` from the local toolchain.
- The 12 public `unsafe` APIs fall into four invariant families:
  - raw pointer recovery and refcount transition: 8 APIs
  - initialization transition: 2 APIs
  - aliasing and type identity: 1 API
  - dynamic type recovery: 1 API

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
