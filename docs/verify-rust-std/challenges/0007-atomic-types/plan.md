---
challenge: "0007-atomic-types"
status: "planning"
priority: "p2"
iteration: 0
last_updated: 2026-04-11
---

## Requirements

- **Goal:** Verify the safety of methods for atomic types and their atomic intrinsics.
- **Source:** https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0007-atomic-types.md
- **Tracking Issue:** [#83](https://github.com/model-checking/verify-rust-std/issues/83) (`OPEN` at README bootstrap)
- Extract the exact atomic APIs, orderings, and intrinsic dependencies from the challenge page before implementation starts.
- Keep the first tranche focused on single-location atomic operations before attempting more complex compare/exchange workflows.
- Prove the safety obligations around valid atomic storage, allowed memory orderings, and any intrinsic-level UB constraints.

## Success Criteria Matrix

| Slice | Initial Harness Target | Status | Notes |
| --- | --- | --- | --- |
| README bootstrap | -- | COMPLETE | README located and challenge metadata captured. |
| Function inventory | challenge-page atomic-method list | TODO | Exact method and ordering scope still needs extraction from upstream docs/source. |
| Harness baseline | first atomic harnesses | TODO | 0 existing harnesses in `kmir/src/tests/integration/data/verify-rust-std/0007-atomic-types/`. |
| Semantic triage | first failing frontier | TODO | No proof frontier yet because no harness has been written. |

## Sprint Plan

1. Inventory the exact atomic methods in scope and group them by load/store, read-modify-write, and compare/exchange families.
2. With 0 existing harnesses, start with the smallest single-location harnesses first: `load_store.rs`, `swap.rs`, and a minimal `compare_exchange.rs` if those APIs are in scope.
3. Add fetch-style arithmetic/bitwise operations after the first ordering-related blocker is understood.
4. Defer broader concurrency narratives; the first sprint should isolate memory-ordering and intrinsic support requirements on one atomic cell.

## Blockers

- The README does not list the exact atomic API surface; that still has to be extracted from the challenge page and target source.
- This challenge may be blocked early by missing modeling for atomic intrinsics or by insufficient treatment of ordering preconditions.
