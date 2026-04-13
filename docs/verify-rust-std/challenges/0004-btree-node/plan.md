---
challenge: "0004-btree-node"
status: "planning"
priority: "p2"
iteration: 0
last_updated: 2026-04-11
---

## Requirements

- **Goal:** Verify memory safety for `BTreeMap`'s `btree::node` module.
- **Source:** https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0004-btree-node.md
- **Tracking Issue:** [#77](https://github.com/model-checking/verify-rust-std/issues/77) (`OPEN` at README bootstrap)
- Extract the exact node APIs and unsafe sites from the challenge page and target module before implementation.
- Keep harnesses focused on localized node operations before attempting larger end-to-end tree workflows.
- Prove preservation of node-layout, parent/child, and initialized-slot invariants for every in-scope unsafe operation.

## Success Criteria Matrix

| Slice | Initial Harness Target | Status | Notes |
| --- | --- | --- | --- |
| README bootstrap | -- | COMPLETE | README located and challenge metadata captured. |
| Function inventory | challenge-page node-op list | TODO | Exact node entry points still need extraction from upstream docs/source. |
| Harness baseline | first node-operation harnesses | TODO | 0 existing harnesses in `kmir/src/tests/integration/data/verify-rust-std/0004-btree-node/`. |
| Semantic triage | first failing frontier | TODO | No proof frontier yet because no harness has been written. |

## Sprint Plan

1. Inventory the smallest unsafe node entry points and document the node invariants each one assumes and preserves.
2. With 0 existing harnesses, start with minimal leaf-node manipulations first: a small constructor/setup harness, a single edge-navigation harness, and a single slot write/read harness.
3. Expand next into split/merge or parent-link operations only after the first leaf-level proofs expose the initial semantics frontier.
4. Keep any larger tree-shape harnesses out of the first sprint unless the smaller node-local cases are already green.

## Blockers

- The README does not include the exact function list; the concrete scope still has to be extracted from the challenge page and module source.
- `btree::node` work is likely to depend on precise modeling of nested aggregates, raw-pointer field projection, and aliasing across parent/child links.
