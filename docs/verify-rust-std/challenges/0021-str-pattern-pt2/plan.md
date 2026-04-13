---
challenge: "0021-str-pattern-pt2"
status: "planning"
priority: "p2"
iteration: 0
last_updated: 2026-04-11
---

## Requirements

- **Goal:** Verify the safety of substring-related functions in `str::pattern`.
- **Source:** https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0021-str-pattern-pt2.md
- **Tracking Issue:** [#278](https://github.com/model-checking/verify-rust-std/issues/278) (`OPEN` at README bootstrap)
- Extract the exact substring-related `str::pattern` APIs and searcher types in scope from the challenge page before implementation starts.
- Separate literal-substring searchers from more stateful pattern helpers so the first sprint isolates one substring-boundary reasoning model.
- For every in-scope function, prove the substring match boundaries, UTF-8 index validity, and searcher-state invariants needed for memory-safe slicing.

## Success Criteria Matrix

| Slice | Initial Harness Target | Status | Notes |
| --- | --- | --- | --- |
| README bootstrap | -- | COMPLETE | README located and challenge metadata captured. |
| Function inventory | challenge-page substring-pattern function list | TODO | Exact in-scope API set still needs extraction from upstream docs/source. |
| Harness baseline | first substring-pattern harnesses | TODO | 0 existing harnesses in kmir/src/tests/integration/data/verify-rust-std/0021-str-pattern-pt2/. |
| Semantic triage | first failing frontier | TODO | No proof frontier yet because no harness has been written. |

## Sprint Plan

1. Inventory the exact substring-pattern APIs in scope and group them into forward search, reverse search, searcher construction, and helper predicates.
2. With 0 existing harnesses, start with the smallest literal-substring tranche whose obligations are primarily boundary validity and search progression.
3. Add richer searcher combinations only after the first frontier shows whether the blocker is substring scanning, UTF-8 boundary reconstruction, or trait dispatch.
4. Record the first failing searcher invariant so the remaining substring-related harnesses can reuse the same boundary model.

## Blockers

- The README does not enumerate the exact function/type list; the concrete `str::pattern` substring scope still has to be extracted from the upstream challenge page and source.
- Substring-pattern proofs are likely to depend on the same UTF-8 boundary and searcher-state machinery as part 1, plus additional substring scanning invariants.
