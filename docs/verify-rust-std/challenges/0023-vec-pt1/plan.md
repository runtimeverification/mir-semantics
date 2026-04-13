---
challenge: "0023-vec-pt1"
status: "planning"
priority: "p2"
iteration: 0
last_updated: 2026-04-11
---

## Requirements

- **Goal:** Verify the safety of `Vec` functions part 1.
- **Source:** https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0023-vec-pt1.md
- **Tracking Issue:** [#284](https://github.com/model-checking/verify-rust-std/issues/284) (`OPEN` at README bootstrap)
- Extract the exact part 1 `Vec` APIs and unsafe implementation sites from the challenge page before writing proofs.
- Separate constructor/basic-access work from growth or element-movement operations so the first sprint isolates one raw-buffer contract family.
- For every in-scope method, prove the capacity, initialization, aliasing, and ownership-transfer obligations required for safe `Vec` manipulation.

## Success Criteria Matrix

| Slice | Initial Harness Target | Status | Notes |
| --- | --- | --- | --- |
| README bootstrap | -- | COMPLETE | README located and challenge metadata captured. |
| Function inventory | challenge-page `Vec` part 1 method list | TODO | Exact in-scope API set still needs extraction from upstream docs/source. |
| Harness baseline | first `Vec` part 1 harnesses | TODO | 0 existing harnesses in kmir/src/tests/integration/data/verify-rust-std/0023-vec-pt1/. |
| Semantic triage | first failing frontier | TODO | No proof frontier yet because no harness has been written. |

## Sprint Plan

1. Inventory the exact part 1 `Vec` methods in scope and group them into constructors/basic access, raw-buffer exposure, mutation, and capacity-management families.
2. With 0 existing harnesses, start with the smallest constructor/basic-access tranche whose proof obligations are structural and reuse `RawVec` invariants directly.
3. Add growth or element-movement harnesses only after the first frontier shows whether the blocker is raw-buffer ownership, layout arithmetic, or slice interoperability.
4. Record the first failing `Vec` invariant so part 2 can build on a stable buffer model rather than duplicating exploratory work.

## Blockers

- The README does not enumerate the exact part 1 method list; the concrete `Vec` scope still has to be extracted from the upstream challenge page and source.
- `Vec` proofs are likely to depend on `RawVec` allocation semantics, slice/raw-pointer interoperability, and element initialization/drop invariants.
