---
challenge: "0006-nonnull"
status: "planning"
priority: "p2"
iteration: 0
last_updated: 2026-04-11
---

## Requirements

- **Goal:** Verify the safety of `NonNull`.
- **Source:** https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0006-nonnull.md
- **Tracking Issue:** [#53](https://github.com/model-checking/verify-rust-std/issues/53) (`CLOSED` at README bootstrap)
- Extract the exact `NonNull` methods and unsafe call sites from the challenge page before harness work begins.
- Separate constructor/accessor coverage from cast and slice-like behaviors so the first sprint stays narrow.
- Prove the non-null, alignment, provenance, and valid-reference obligations required by each in-scope `NonNull` API.

## Success Criteria Matrix

| Slice | Initial Harness Target | Status | Notes |
| --- | --- | --- | --- |
| README bootstrap | -- | COMPLETE | README located and challenge metadata captured. |
| Function inventory | challenge-page `NonNull` list | TODO | Exact method scope still needs extraction from upstream docs/source. |
| Harness baseline | first `NonNull` harnesses | TODO | 0 existing harnesses in `kmir/src/tests/integration/data/verify-rust-std/0006-nonnull/`. |
| Semantic triage | first failing frontier | TODO | No proof frontier yet because no harness has been written. |

## Sprint Plan

1. Inventory the exact `NonNull` surface in scope and split it into constructors, raw-pointer views, and casts/derived references.
2. With 0 existing harnesses, start with the smallest constructor/accessor tranche first: `new.rs`, `new_unchecked.rs`, `as_ptr.rs`, and `cast.rs` if those methods are in scope.
3. Add slice/reference-derivation harnesses only after the core non-null and cast behavior is green or blocked with a clear frontier.
4. Record any need for pointer-to-pointer cast support or provenance rules before broadening the surface.

## Blockers

- The README does not enumerate the full method set; the exact scope still has to be extracted from the challenge page and std source.
- `NonNull` work commonly depends on pointer-cast semantics, provenance preservation, and niche/nonzero encodings when wrapped by other std abstractions.
