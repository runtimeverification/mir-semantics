---
challenge: "0029-boxed"
status: "tranche_1_complete"
priority: "medium"
iteration: 1
last_updated: 2026-04-11
---

## Challenge Requirements

- Verify the first boxed-ownership tranche defined in the README.
- Keep coverage on the raw ownership roots:
  `Box::from_raw`, `Box::from_raw_in`, `Box::from_non_null`,
  and `Box::from_non_null_in`.
- Keep coverage on the initialization-conversion roots:
  scalar and slice `assume_init`.
- Use the fully green tranche as the launch point for follow-on constructor,
  conversion, and dynamic-type work.

## Success Criteria Matrix

| Harness | Requirement slice | Result | Notes |
| --- | --- | --- | --- |
| `box-assume-init` | Scalar `Box<MaybeUninit<T>, A>::assume_init` | PASS | Green |
| `box-from-non-null-in` | `Box<T, A>::from_non_null_in` | PASS | Green |
| `box-from-non-null` | `Box<T>::from_non_null` | PASS | Green |
| `box-from-raw-in` | `Box<T, A>::from_raw_in` | PASS | Green |
| `box-from-raw` | `Box<T>::from_raw` | PASS | Green |
| `box-slice-assume-init` | Slice `Box<[MaybeUninit<T>], A>::assume_init` | PASS | Green |

## Sprint Plan

1. Treat the current six passing harnesses as the stable tranche-1 regression baseline.
2. Expand next into outgoing ownership conversions such as `into_non_null`,
   `into_raw_with_allocator`, and `into_non_null_with_allocator`.
3. Add constructor coverage after that: `new_in`, `try_new_in`,
   `try_new_uninit_in`, `try_new_zeroed_in`, and the slice-constructor family.
4. Leave `downcast(_unchecked)` and ThinBox work for a later sprint once the
   ownership and constructor surface is broader.

## Blockers

- There is no blocker on the current tranche; all existing harnesses pass.
- Challenge completion is still incomplete because the README scope extends
  beyond the six implemented harnesses.
- Older notes that referenced a `Layout::new::<u32>` frontier are stale and
  should not be used to prioritize the next sprint.
