---
challenge: "0017-slice"
status: "planning"
priority: "p2"
iteration: 0
last_updated: 2026-04-11
---

## Requirements

- **Goal:** Verify the safety of `slice` functions.
- **Source:** https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0017-slice.md
- **Tracking Issue:** [#281](https://github.com/model-checking/verify-rust-std/issues/281) (`OPEN` at README bootstrap)
- Extract the exact `slice` APIs and unsafe implementation sites from the challenge page before writing proofs.
- Separate read-only indexing/splitting operations from mutation or raw-pointer conversions so the first sprint isolates one bounds discipline.
- For every in-scope method, prove the necessary bounds, aliasing, initialization, and provenance obligations for the resulting subslices or raw accesses.

## Success Criteria Matrix

| Slice | Initial Harness Target | Status | Notes |
| --- | --- | --- | --- |
| README bootstrap | -- | COMPLETE | README located and challenge metadata captured. |
| Function inventory | challenge-page `slice` method list | TODO | Exact in-scope API set still needs extraction from upstream docs/source. |
| Harness baseline | first slice operation harnesses | TODO | 0 existing harnesses in kmir/src/tests/integration/data/verify-rust-std/0017-slice/. |
| Semantic triage | first failing frontier | TODO | No proof frontier yet because no harness has been written. |

## Sprint Plan

1. Inventory the exact `slice` methods in scope and group them into indexing/splitting, search, mutation, and raw-pointer conversion families.
2. With 0 existing harnesses, start with the smallest read-only subslice operations whose safety story is primarily bounds preservation.
3. Add mutation or raw-pointer-facing harnesses only after the first frontier shows whether the blocker is bounds reasoning, aliasing, or slice-fat-pointer support.
4. Capture the first failing slice invariant explicitly so later harnesses can share that model rather than duplicating exploratory work.

## Blockers

- The README does not enumerate the exact `slice` function list; the concrete scope still has to be extracted from the upstream challenge page and source.
- `slice` proofs are likely to expose shared gaps in fat-pointer manipulation, subrange bounds reasoning, and alias-sensitive mutation semantics.
