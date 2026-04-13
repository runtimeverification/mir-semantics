---
challenge: "0024-vec-pt2"
status: "planning"
priority: "p2"
iteration: 0
last_updated: 2026-04-11
---

## Requirements

- **Goal:** Verify the safety of `Vec` functions part 2.
- **Source:** https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0024-vec-pt2.md
- **Tracking Issue:** [#285](https://github.com/model-checking/verify-rust-std/issues/285) (`OPEN` at README bootstrap)
- Extract the exact part 2 `Vec` APIs and unsafe implementation sites from the challenge page before writing proofs.
- Separate advanced mutation/reordering work from capacity-management or raw-buffer escape hatches so the first sprint isolates one complex invariant class.
- For every in-scope method, prove the element-movement, aliasing, initialization, and capacity obligations required for safe `Vec` reorganization.

## Success Criteria Matrix

| Slice | Initial Harness Target | Status | Notes |
| --- | --- | --- | --- |
| README bootstrap | -- | COMPLETE | README located and challenge metadata captured. |
| Function inventory | challenge-page `Vec` part 2 method list | TODO | Exact in-scope API set still needs extraction from upstream docs/source. |
| Harness baseline | first `Vec` part 2 harnesses | TODO | 0 existing harnesses in kmir/src/tests/integration/data/verify-rust-std/0024-vec-pt2/. |
| Semantic triage | first failing frontier | TODO | No proof frontier yet because no harness has been written. |

## Sprint Plan

1. Inventory the exact part 2 `Vec` methods in scope and group them into advanced mutation, reordering/drain-style behavior, spare-capacity access, and teardown paths.
2. With 0 existing harnesses, start with the smallest advanced-mutation tranche whose proof obligations can reuse the part 1 buffer model with minimal new semantics.
3. Add the most alias-sensitive or raw-buffer-facing methods only after the first frontier shows whether the blocker is element movement, drop order, or spare-capacity modeling.
4. Record the first failing advanced `Vec` invariant so subsequent harnesses do not mix unrelated frontier shifts.

## Blockers

- The README does not enumerate the exact part 2 method list; the concrete `Vec` scope still has to be extracted from the upstream challenge page and source.
- Part 2 `Vec` work is likely to depend on a stable part 1 buffer model plus additional support for element movement, drain-style state, and spare-capacity views.
