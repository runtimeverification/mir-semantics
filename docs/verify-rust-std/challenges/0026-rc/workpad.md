# Challenge 0026 Workpad

## Current State

- Branch: `verify-rust-std/reexec-0026-rc`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0026-rc`
- Local status: planning docs only; no code or proof artifacts touched.

## Confirmed Inputs

- Challenge page: `https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0026-rc.md`
- Tracking issue: `#382`
- Artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0026-rc`
- Public guidance: issue #382 comments indicate most contracts were already written by the original contributor, with a possible remaining dependency on the Kani update referenced as `model-checking/kani#4427`.

## Next Action

- Build the raw-pointer/refcount proof matrix for `alloc::rc` and identify the first tranche to hand to the generator.

## What Needs To Be Captured

- Which of the 12 public unsafe APIs already has a clear source SAFETY comment.
- Which API cluster shares the same invariant set and therefore should be tackled together.
- Whether any chosen function depends on an upstream tool/backend update.

## Working Notes

- Keep the plan narrowed to one tranche only.
- Do not expand into code or proof implementation from this file.
- Use this workpad to record the chosen tranche before any generator work starts.
