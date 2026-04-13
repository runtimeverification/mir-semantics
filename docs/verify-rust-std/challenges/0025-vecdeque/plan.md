---
challenge: "0025-vecdeque"
status: "planning"
priority: "p2"
iteration: 0
last_updated: 2026-04-11
---

## Requirements

- **Goal:** Verify the safety of `VecDeque` functions.
- **Source:** https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0025-vecdeque.md
- **Tracking Issue:** [#286](https://github.com/model-checking/verify-rust-std/issues/286) (`OPEN` at README bootstrap)
- Extract the exact `VecDeque` APIs and unsafe implementation sites from the challenge page before writing proofs.
- Separate simple front/back access from wrap-around growth or reordering operations so the first sprint isolates one ring-buffer invariant class.
- For every in-scope method, prove the head/tail, capacity, wrap-around indexing, and aliasing obligations required for safe ring-buffer manipulation.

## Success Criteria Matrix

| Slice | Initial Harness Target | Status | Notes |
| --- | --- | --- | --- |
| README bootstrap | -- | COMPLETE | README located and challenge metadata captured. |
| Function inventory | challenge-page `VecDeque` method list | TODO | Exact in-scope API set still needs extraction from upstream docs/source. |
| Harness baseline | first `VecDeque` harnesses | TODO | 0 existing harnesses in kmir/src/tests/integration/data/verify-rust-std/0025-vecdeque/. |
| Semantic triage | first failing frontier | TODO | No proof frontier yet because no harness has been written. |

## Sprint Plan

1. Inventory the exact `VecDeque` methods in scope and group them into front/back access, push/pop, rotation/reordering, growth, and slice-view families.
2. With 0 existing harnesses, start with the smallest front/back access tranche whose safety argument is mostly ring-index bounds preservation.
3. Add wrap-around mutation or growth harnesses only after the first frontier shows whether the blocker is modulo indexing, buffer layout, or alias-sensitive split views.
4. Record the first failing ring-buffer invariant so later harnesses can reuse a stable head/tail model.

## Blockers

- The README does not enumerate the exact `VecDeque` method list; the concrete scope still has to be extracted from the upstream challenge page and source.
- `VecDeque` proofs are likely to expose gaps in ring-buffer indexing, split-slice views, and growth/rotation semantics that do not appear in plain `Vec` work.
