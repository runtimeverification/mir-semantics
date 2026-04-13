---
challenge: "0003-pointer-arithmentic"
status: "planning"
priority: "p2"
iteration: 0
last_updated: 2026-04-11
---

## Requirements

- **Goal:** Verify raw pointer arithmetic operations.
- **Source:** https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0003-pointer-arithmentic.md
- **Tracking Issue:** [#76](https://github.com/model-checking/verify-rust-std/issues/76) (`CLOSED` at README bootstrap)
- Extract the exact pointer-arithmetic APIs and proof obligations from the challenge page before harness work begins.
- Keep proof harnesses and any required semantics changes in separate commits.
- Prove that each in-scope operation preserves the required arithmetic and memory-safety side conditions, especially bounds, alignment, and provenance-sensitive behavior.

## Success Criteria Matrix

| Slice | Initial Harness Target | Status | Notes |
| --- | --- | --- | --- |
| README bootstrap | -- | COMPLETE | README located and challenge metadata captured. |
| Function inventory | challenge-page pointer-op list | TODO | Exact `offset`/`add`/`sub`/wrapping scope still needs extraction. |
| Harness baseline | first arithmetic harnesses | TODO | 0 existing harnesses in `kmir/src/tests/integration/data/verify-rust-std/0003-pointer-arithmentic/`. |
| Semantic triage | first failing frontier | TODO | No proof frontier yet because no harness has been written. |

## Sprint Plan

1. Inventory the exact in-scope raw-pointer arithmetic methods and group them by plain, checked-by-precondition, and wrapping behavior.
2. With 0 existing harnesses, start with the smallest arithmetic surfaces first: `offset.rs`, `add_sub.rs`, and `byte_offset.rs` if those are in scope.
3. Add a second tranche for wrapping variants and signed/unsigned offset cases once the first frontier is known.
4. Capture the first blocker in pointer-provenance, integer-to-pointer cast, or bounds reasoning before scaling out to the full surface.

## Blockers

- The README is only a bootstrap pointer; the exact operation list still has to be confirmed from the challenge page and std source.
- This challenge is likely to expose missing semantics around pointer provenance, pointer-plus-integer casts, and in-bounds offset reasoning.
