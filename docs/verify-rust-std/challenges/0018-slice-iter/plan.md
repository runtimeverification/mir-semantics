---
challenge: "0018-slice-iter"
status: "planning"
priority: "p2"
iteration: 0
last_updated: 2026-04-11
---

## Requirements

- **Goal:** Verify the safety of `slice` iterator functions.
- **Source:** https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0018-slice-iter.md
- **Tracking Issue:** [#282](https://github.com/model-checking/verify-rust-std/issues/282) (`OPEN` at README bootstrap)
- Extract the exact `slice` iterator methods and iterator structs in scope from the challenge page before implementation starts.
- Keep immutable iterators separate from mutable, chunked, or split iterators so the first sprint isolates one aliasing model.
- For every in-scope iterator, prove that pointer movement, yielded references, and termination conditions preserve bounds and aliasing invariants.

## Success Criteria Matrix

| Slice | Initial Harness Target | Status | Notes |
| --- | --- | --- | --- |
| README bootstrap | -- | COMPLETE | README located and challenge metadata captured. |
| Function inventory | challenge-page `slice` iterator list | TODO | Exact in-scope API set still needs extraction from upstream docs/source. |
| Harness baseline | first slice-iterator harnesses | TODO | 0 existing harnesses in kmir/src/tests/integration/data/verify-rust-std/0018-slice-iter/. |
| Semantic triage | first failing frontier | TODO | No proof frontier yet because no harness has been written. |

## Sprint Plan

1. Inventory the exact `slice` iterator APIs in scope and bucket them into immutable, mutable, chunked, and split-style iterators.
2. With 0 existing harnesses, start with the narrowest immutable iterator tranche whose invariants are monotone cursor movement and bounds preservation.
3. Add mutable or split iterators only after the first frontier reveals whether the blocker is yielded-reference aliasing, iterator state, or trait dispatch.
4. Record the first iterator-state invariant that fails so subsequent harnesses can reuse the same cursor model.

## Blockers

- The README does not enumerate the exact iterator list; the concrete scope still has to be extracted from the upstream challenge page and source.
- `slice` iterator work is likely to depend on stable models for fat pointers, cursor arithmetic, and aliasing of yielded references, especially for mutable variants.
