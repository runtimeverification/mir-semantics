---
challenge: "0022-str-iter"
status: "planning"
priority: "p2"
iteration: 0
last_updated: 2026-04-11
---

## Requirements

- **Goal:** Verify the safety of `str` iterator functions.
- **Source:** https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0022-str-iter.md
- **Tracking Issue:** [#279](https://github.com/model-checking/verify-rust-std/issues/279) (`OPEN` at README bootstrap)
- Extract the exact `str` iterator APIs and iterator structs in scope from the challenge page before implementation starts.
- Keep UTF-8-decoding iterators separate from boundary-only iterators so the first sprint isolates one string-iteration invariant class.
- For every in-scope iterator, prove that cursor movement, yielded values or subslices, and termination conditions preserve valid UTF-8 boundaries and bounds.

## Success Criteria Matrix

| Slice | Initial Harness Target | Status | Notes |
| --- | --- | --- | --- |
| README bootstrap | -- | COMPLETE | README located and challenge metadata captured. |
| Function inventory | challenge-page `str` iterator list | TODO | Exact in-scope API set still needs extraction from upstream docs/source. |
| Harness baseline | first `str` iterator harnesses | TODO | 0 existing harnesses in kmir/src/tests/integration/data/verify-rust-std/0022-str-iter/. |
| Semantic triage | first failing frontier | TODO | No proof frontier yet because no harness has been written. |

## Sprint Plan

1. Inventory the exact `str` iterator APIs in scope and group them into char-decoding, boundary-only, split-style, and reverse-iteration families.
2. With 0 existing harnesses, start with the narrowest boundary-preserving iterator tranche before taking on iterators that decode multi-byte characters.
3. Add decoding-heavy or split iterators only after the first frontier shows whether the blocker is UTF-8 decoding, iterator state, or substring slicing semantics.
4. Record the first string-iterator invariant that fails so later harnesses share a stable cursor/boundary model.

## Blockers

- The README does not enumerate the exact iterator list; the concrete `str` iterator scope still has to be extracted from the upstream challenge page and source.
- `str` iterator proofs are likely to depend on UTF-8 boundary reasoning, char decoding support, and substring/slice interoperability.
