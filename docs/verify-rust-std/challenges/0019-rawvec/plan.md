---
challenge: "0019-rawvec"
status: "planning"
priority: "p2"
iteration: 0
last_updated: 2026-04-11
---

## Requirements

- **Goal:** Verify the safety of `RawVec` functions.
- **Source:** https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0019-rawvec.md
- **Tracking Issue:** [#283](https://github.com/model-checking/verify-rust-std/issues/283) (`CLOSED` at README bootstrap)
- Extract the exact `RawVec` methods and allocation-related invariants from the challenge page before implementation starts.
- Separate allocation/layout constructors from growth/reallocation operations so the first sprint isolates one allocator-facing contract family.
- For every in-scope method, prove the layout, capacity, dangling-pointer, and ownership-transfer obligations that make raw-buffer manipulation memory safe.

## Success Criteria Matrix

| Slice | Initial Harness Target | Status | Notes |
| --- | --- | --- | --- |
| README bootstrap | -- | COMPLETE | README located and challenge metadata captured. |
| Function inventory | challenge-page `RawVec` function list | TODO | Exact in-scope API set still needs extraction from upstream docs/source. |
| Harness baseline | first `RawVec` harnesses | TODO | 0 existing harnesses in kmir/src/tests/integration/data/verify-rust-std/0019-rawvec/. |
| Semantic triage | first failing frontier | TODO | No proof frontier yet because no harness has been written. |

## Sprint Plan

1. Inventory the exact `RawVec` methods in scope and group them into constructors, capacity/growth, raw-buffer access, and teardown operations.
2. With 0 existing harnesses, start with the smallest constructor/layout tranche whose proof obligations focus on allocation metadata rather than element movement.
3. Add reallocation and growth harnesses only after the first frontier shows whether the blocker is allocator modeling, layout arithmetic, or ownership transfer.
4. Record the first failing allocation invariant before expanding into `Vec`-adjacent behavior that would obscure the root cause.

## Blockers

- The README does not enumerate the exact `RawVec` method list; the concrete scope still has to be extracted from the upstream challenge page and source.
- `RawVec` proofs are likely to depend on allocator/layout modeling, capacity arithmetic, and raw-buffer ownership semantics that are shared with later `Vec` work.
