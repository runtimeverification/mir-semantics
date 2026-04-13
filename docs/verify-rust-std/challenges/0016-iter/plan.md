---
challenge: "0016-iter"
status: "planning"
priority: "p2"
iteration: 0
last_updated: 2026-04-11
---

## Requirements

- **Goal:** Verify the safety of `Iterator` functions.
- **Source:** https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0016-iter.md
- **Tracking Issue:** [#280](https://github.com/model-checking/verify-rust-std/issues/280) (`OPEN` at README bootstrap)
- Extract the exact iterator methods and adaptor families in scope from the challenge page before implementation starts.
- Split pure control-flow adaptors from stateful or alias-sensitive adaptors so the first sprint stays focused on one iterator invariant class.
- For every in-scope method, prove that internal state transitions preserve bounds, aliasing, and drop-safety obligations across repeated `next` calls.

## Success Criteria Matrix

| Slice | Initial Harness Target | Status | Notes |
| --- | --- | --- | --- |
| README bootstrap | -- | COMPLETE | README located and challenge metadata captured. |
| Function inventory | challenge-page `Iterator` method list | TODO | Exact in-scope API set still needs extraction from upstream docs/source. |
| Harness baseline | first iterator adaptor harnesses | TODO | 0 existing harnesses in kmir/src/tests/integration/data/verify-rust-std/0016-iter/. |
| Semantic triage | first failing frontier | TODO | No proof frontier yet because no harness has been written. |

## Sprint Plan

1. Inventory the exact iterator methods in scope and group them into stateless adaptors, stateful adaptors, consumers, and constructors.
2. With 0 existing harnesses, start with the smallest adaptor tranche whose safety argument is mostly index/state monotonicity rather than container mutation.
3. Add stateful combinators only after the first frontier makes clear whether the blocker is closure modeling, trait dispatch, or iterator-state encoding.
4. Record which iterator invariant fails first so later harnesses can reuse a stable state model instead of re-opening the same frontier.

## Blockers

- The README does not enumerate the exact method list; the concrete `Iterator` scope still has to be extracted from the upstream challenge page and source.
- Iterator proofs commonly depend on closure calls, trait dispatch, and precise state-machine modeling, any of which may become the first cross-cutting semantic blocker.
