---
challenge: "0002-intrinsics-memory"
status: "planning"
priority: "p2"
iteration: 0
last_updated: 2026-04-11
---

## Requirements

- **Goal:** Verify the memory safety of `core` intrinsics that operate on raw pointers.
- **Source:** https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0002-intrinsics-memory.md
- **Tracking Issue:** [#16](https://github.com/model-checking/verify-rust-std/issues/16) (`OPEN` at README bootstrap)
- Extract the exact intrinsic list and caller obligations from the challenge page before implementation starts.
- Keep harness-only work separate from any cross-cutting semantic changes so fixes remain cherry-pickable.
- For every in-scope intrinsic, prove the relevant pointer preconditions: alignment, initialization, non-overlap when required, and no invalid-value UB.

## Success Criteria Matrix

| Slice | Initial Harness Target | Status | Notes |
| --- | --- | --- | --- |
| README bootstrap | -- | COMPLETE | README located and challenge metadata captured. |
| Function inventory | challenge-page intrinsic list | TODO | Exact intrinsic set still needs extraction from upstream docs/source. |
| Harness baseline | first intrinsic-family harnesses | TODO | 0 existing harnesses in `kmir/src/tests/integration/data/verify-rust-std/0002-intrinsics-memory/`. |
| Semantic triage | first failing frontier | TODO | No proof frontier yet because no harness has been written. |

## Sprint Plan

1. Confirm the exact intrinsic set from the challenge page and std source, then map each intrinsic to its raw-pointer safety obligations.
2. With 0 existing harnesses, start with the smallest copy/write intrinsics first: `copy_nonoverlapping.rs`, `copy.rs`, and `write_bytes.rs`.
3. Add the next raw-memory tranche after that: read/write-style harnesses and any volatile variants that are explicitly in scope.
4. Wire the first tranche into integration test discovery and record the first semantic blocker before expanding breadth.

## Blockers

- The README does not enumerate the full intrinsic/function list; that inventory still has to be extracted from the upstream challenge page and source.
- Raw-pointer intrinsics commonly surface cross-challenge gaps in provenance, overlap checks, and uninitialized-memory modeling; the first harnesses should be chosen to isolate which of those appears first.
