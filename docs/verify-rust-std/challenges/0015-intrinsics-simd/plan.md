---
challenge: "0015-intrinsics-simd"
status: "planning"
priority: "p2"
iteration: 0
last_updated: 2026-04-11
---

## Requirements

- **Goal:** Verify the safety of SIMD intrinsics.
- **Source:** https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0015-intrinsics-simd.md
- **Tracking Issue:** [#173](https://github.com/model-checking/verify-rust-std/issues/173) (`CLOSED` at README bootstrap)
- Extract the exact intrinsic set, lane-shape assumptions, and caller obligations from the challenge page before implementation starts.
- Keep lane-wise arithmetic/compare intrinsics separate from shuffle/cast operations so the first proof tranche isolates one semantic family.
- For every in-scope intrinsic, prove the relevant layout, alignment, lane-count, and raw-pointer preconditions without introducing UB through vector reinterpretation.

## Success Criteria Matrix

| Slice | Initial Harness Target | Status | Notes |
| --- | --- | --- | --- |
| README bootstrap | -- | COMPLETE | README located and challenge metadata captured. |
| Function inventory | challenge-page SIMD intrinsic list | TODO | Exact in-scope API set still needs extraction from upstream docs/source. |
| Harness baseline | first SIMD intrinsic harnesses | TODO | 0 existing harnesses in kmir/src/tests/integration/data/verify-rust-std/0015-intrinsics-simd/. |
| Semantic triage | first failing frontier | TODO | No proof frontier yet because no harness has been written. |

## Sprint Plan

1. Confirm the exact intrinsic inventory from the challenge page and std source, then bucket it into arithmetic, comparison, shuffle, and cast-style operations.
2. With 0 existing harnesses, start from the narrowest lane-wise operations whose contracts are mostly structural rather than data-dependent.
3. Add shuffle or reinterpretation harnesses only after the first SIMD frontier shows whether the blocker is vector typing, layout, or intrinsic dispatch support.
4. Record whether the first failure comes from SIMD type construction, lane extraction, or unsupported intrinsic lowering before broadening coverage.

## Blockers

- The README does not enumerate the exact intrinsic/function list; that inventory still has to be extracted from the upstream challenge page and source.
- SIMD intrinsics are likely to surface gaps in vector-type layout, lane-wise reasoning, and intrinsic dispatch support before function-specific proof obligations can be tackled.
