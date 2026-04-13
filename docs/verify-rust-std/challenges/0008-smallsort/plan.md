---
challenge: "0008-smallsort"
status: "planning"
priority: "p2"
iteration: 0
last_updated: 2026-04-11
---

## Requirements

- **Goal:** Write contracts for `SmallSort`.
- **Source:** https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0008-smallsort.md
- **Tracking Issue:** [#56](https://github.com/model-checking/verify-rust-std/issues/56) (`OPEN` at README bootstrap)
- Extract the exact `SmallSort` entry points and unsafe helpers from the challenge page and target module before implementation.
- Start with the smallest sort kernels first so comparison and swap obligations are isolated.
- Prove both the safety side conditions and the intended postconditions for the in-scope sort routines, especially around element movement and temporary storage.

## Success Criteria Matrix

| Slice | Initial Harness Target | Status | Notes |
| --- | --- | --- | --- |
| README bootstrap | -- | COMPLETE | README located and challenge metadata captured. |
| Function inventory | challenge-page `SmallSort` list | TODO | Exact routine/helper scope still needs extraction from upstream docs/source. |
| Harness baseline | first sorting harnesses | TODO | 0 existing harnesses in `kmir/src/tests/integration/data/verify-rust-std/0008-smallsort/`. |
| Semantic triage | first failing frontier | TODO | No proof frontier yet because no harness has been written. |

## Sprint Plan

1. Inventory the exact `SmallSort` routines in scope and split them into fixed-size kernels, partitioning helpers, and shared unsafe utilities.
2. With 0 existing harnesses, start with the smallest fixed-size kernels first: `sort2.rs`, `sort3.rs`, and `sort4.rs` if those routines are in scope.
3. Add any helper-level harnesses for swap or temporary-buffer logic after the first kernel proofs establish the initial frontier.
4. Keep the first sprint on tiny concrete arrays so the safety obligations are visible before attempting more generic sort paths.

## Blockers

- The README does not enumerate the exact routines; the function list still has to be extracted from the challenge page and source.
- This challenge may expose gaps around array/slice mutation, element permutation reasoning, and helper intrinsics used by small fixed-size sorts.
