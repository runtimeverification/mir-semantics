---
challenge: "0013-cstr"
status: "blocked"
priority: "high"
iteration: 1
last_updated: 2026-04-11
---

## Challenge Requirements

- Verify the safety of `CStr`.
- Cover the challenge's unsafe roots first: `CStr::from_ptr` and
  `CStr::from_bytes_with_nul_unchecked`.
- Preserve the branch-local `CloneToUninit` and `Index<RangeFrom<usize>>`
  slices already called out in the challenge README.
- Keep later expansion in view for the remaining safe methods and `strlen`,
  which are still listed as uncovered challenge scope.

## Success Criteria Matrix

| Harness | Requirement slice | Result | Notes |
| --- | --- | --- | --- |
| `clone_to_uninit` | `CloneToUninit` path through `CStr::from_bytes_with_nul` | FAIL | `failing: 1`, `stuck: 1`; still blocked on the shared donor-linked constructor/body frontier |
| `from_bytes_with_nul_unchecked` | `CStr::from_bytes_with_nul_unchecked` | FAIL | `failing: 1`; likely shares constructor dependencies with the blocked `CStr` path |
| `from_ptr` | `CStr::from_ptr` plus branch-local range indexing slice | FAIL | `failing: 1`; needs reclassification after the shared constructor frontier moves |

## Sprint Plan

1. Unblock the shared `CStr::from_bytes_with_nul` donor-link/body path because it is the highest-leverage frontier named in the README and already affects `clone_to_uninit`.
2. Re-run `clone_to_uninit` and `from_bytes_with_nul_unchecked` immediately after that semantic shift to determine whether they collapse onto the same fix or expose distinct downstream failures.
3. Re-run `from_ptr` after the shared fix and classify it as either resolved, newly frontiered, or independently blocked.
4. Once one current harness passes, add the next missing challenge-local proof slices for `strlen` and the remaining safe methods listed in the README.

## Blockers

- All three current harnesses fail, so there is no green baseline yet.
- `clone_to_uninit` is explicitly stuck on the donor-linked SMIR item
  qualification issue described in the README.
- The README scope is wider than the current harness set, so challenge
  completion still requires new harnesses after the current frontier moves.
