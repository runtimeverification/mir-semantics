---
challenge: "0005-linked-list"
status: "planning"
priority: "p2"
iteration: 0
last_updated: 2026-04-11
---

## Requirements

- **Goal:** Verify functions that iterate over the inductive `linked_list` data structure.
- **Source:** https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0005-linked-list.md
- **Tracking Issue:** [#29](https://github.com/model-checking/verify-rust-std/issues/29) (`CLOSED` at README bootstrap)
- Extract the exact iterator-related APIs and unsafe sites from the challenge page and target module before implementation.
- Start with the smallest list shapes and shortest iterator traces so the first frontier is easy to diagnose.
- Prove preservation of list-shape, aliasing, and element-validity invariants for every in-scope iterator or cursor operation.

## Success Criteria Matrix

| Slice | Initial Harness Target | Status | Notes |
| --- | --- | --- | --- |
| README bootstrap | -- | COMPLETE | README located and challenge metadata captured. |
| Function inventory | challenge-page iterator list | TODO | Exact iterator/cursor surface still needs extraction from upstream docs/source. |
| Harness baseline | first iterator harnesses | TODO | 0 existing harnesses in `kmir/src/tests/integration/data/verify-rust-std/0005-linked-list/`. |
| Semantic triage | first failing frontier | TODO | No proof frontier yet because no harness has been written. |

## Sprint Plan

1. Inventory the exact linked-list iterator and cursor APIs in scope, then classify them by read-only traversal, mutable traversal, and structural mutation.
2. With 0 existing harnesses, start with the simplest traversal harnesses first: `iter.rs`, `iter_mut.rs`, and a minimal front/back traversal harness if those APIs are in scope.
3. Add mutation-sensitive iterator cases only after the read-only traversal frontier is understood.
4. Keep the first sprint focused on tiny one-node and two-node lists so inductive invariants are explicit in the proof obligations.

## Blockers

- The README is not enough to recover the exact function list; the challenge page and module source still need to be inventoried.
- This challenge is likely to hit gaps in recursive-shape reasoning, aliasing through mutable iteration, and pointer updates during traversal.
