---
challenge: "0010-string"
status: "planning"
priority: "p2"
iteration: 0
last_updated: 2026-04-11
---

## Requirements

- **Goal:** Verify the memory safety of `String`.
- **Source:** https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0010-string.md
- **Tracking Issue:** [#61](https://github.com/model-checking/verify-rust-std/issues/61) (`OPEN` at README bootstrap)
- Extract the exact `String` methods and unsafe implementation sites from the challenge page before writing proofs.
- Separate constructor/conversion work from growth and mutation work so the first sprint stays narrow.
- Prove the UTF-8, capacity/layout, aliasing, and raw-buffer safety obligations for every in-scope operation.

## Success Criteria Matrix

| Slice | Initial Harness Target | Status | Notes |
| --- | --- | --- | --- |
| README bootstrap | -- | COMPLETE | README located and challenge metadata captured. |
| Function inventory | challenge-page `String` list | TODO | Exact method scope still needs extraction from upstream docs/source. |
| Harness baseline | first `String` harnesses | TODO | 0 existing harnesses in `kmir/src/tests/integration/data/verify-rust-std/0010-string/`. |
| Semantic triage | first failing frontier | TODO | No proof frontier yet because no harness has been written. |

## Sprint Plan

1. Inventory the exact `String` APIs in scope and group them into constructors/conversions, raw-buffer access, and mutation/growth operations.
2. With 0 existing harnesses, start with the smallest constructor/conversion tranche first: `from_utf8_unchecked.rs`, `into_bytes.rs`, and `as_mut_vec.rs` if those methods are in scope.
3. Add mutation-oriented harnesses such as `push_str.rs` or reserve/growth cases only after the first raw-buffer frontier is clear.
4. Record whether the first blocker is UTF-8 decoding, vector/raw-buffer semantics, or pointer/slice mutation before expanding coverage.

## Blockers

- The README does not enumerate the exact method list; the concrete scope still has to be extracted from the challenge page and std source.
- `String` work is likely to depend on string/UTF-8 decoding support, raw `Vec<u8>` interoperability, and slice mutation semantics.
