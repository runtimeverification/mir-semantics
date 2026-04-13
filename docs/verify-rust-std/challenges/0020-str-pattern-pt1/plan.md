---
challenge: "0020-str-pattern-pt1"
status: "planning"
priority: "p2"
iteration: 0
last_updated: 2026-04-11
---

## Requirements

- **Goal:** Verify the safety of char-related functions in `str::pattern`.
- **Source:** https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0020-str-pattern-pt1.md
- **Tracking Issue:** [#277](https://github.com/model-checking/verify-rust-std/issues/277) (`OPEN` at README bootstrap)
- Extract the exact char-related `str::pattern` APIs and matcher types in scope from the challenge page before implementation starts.
- Keep single-char search/match operations separate from multi-step searcher state machines so the first sprint isolates one UTF-8 boundary discipline.
- For every in-scope function, prove the UTF-8 boundary, index-range, and matcher-state obligations required to return valid substring boundaries.

## Success Criteria Matrix

| Slice | Initial Harness Target | Status | Notes |
| --- | --- | --- | --- |
| README bootstrap | -- | COMPLETE | README located and challenge metadata captured. |
| Function inventory | challenge-page char-pattern function list | TODO | Exact in-scope API set still needs extraction from upstream docs/source. |
| Harness baseline | first `str::pattern` char harnesses | TODO | 0 existing harnesses in kmir/src/tests/integration/data/verify-rust-std/0020-str-pattern-pt1/. |
| Semantic triage | first failing frontier | TODO | No proof frontier yet because no harness has been written. |

## Sprint Plan

1. Inventory the exact char-related pattern APIs in scope and group them into forward search, reverse search, predicate helpers, and searcher construction.
2. With 0 existing harnesses, start with the narrowest char-pattern tranche whose safety story is mostly UTF-8 boundary preservation.
3. Add richer searcher-state harnesses only after the first frontier shows whether the blocker is Unicode scalar handling, searcher trait dispatch, or substring slicing.
4. Record which boundary or searcher invariant fails first so part 2 can build on a stable model instead of revisiting the same uncertainty.

## Blockers

- The README does not enumerate the exact function/type list; the concrete `str::pattern` scope still has to be extracted from the upstream challenge page and source.
- Char-pattern work is likely to expose dependencies on UTF-8 boundary reasoning, pattern-searcher state machines, and string/slice interoperability.
