# Evaluation Result: Challenge 0002-intrinsics-memory

## Verdict

`in_progress` -- as of `2026-04-12`, the challenge stands at `9/16` passing harnesses. The baseline is materially broader than the previous snapshot, but the remaining value-dependent and raw-memory frontier is still open.

## Scorecard

| Criterion | Status | Evidence |
| --- | --- | --- |
| Implemented proof baseline | PASS | `16` counted harnesses now have recorded outcomes. |
| Current proof health | PARTIAL | `9/16` counted harnesses pass. |
| Remaining frontier | PARTIAL | `7/16` counted harnesses still fail. |
| Submission readiness | FAIL | The challenge is still missing closure on several memory/layout operations. |
| Residual risk | HIGH | The active frontier still includes value-dependent layout queries, raw-memory writes/copies, and unstable newer probes. |

## Current Coverage Summary

- Passing harnesses: `9/16`
  - `size_of_probe`
  - `likely_unlikely`
  - `min_align_of`
  - `forget`
  - `black_box`
  - `replace`
  - `align_of`
  - `discriminant_value`
  - `assume`
- Counted failing harnesses: `7/16`
  - `min_align_of_val`
  - `needs_drop`
  - `size_of_val`
  - `write_bytes`
  - `copy`
  - `transmute_copy`
  - `swap` (`typed_swap`)
- Additional non-passing frontier noted in the latest sweep
  - `zeroed`
  - `type_id`
  - `offset_of` (crash)
  - `variant_count`

## Next Steps

1. Close the value-dependent layout frontier: `min_align_of_val`, `needs_drop`, and `size_of_val`.
2. Triage the remaining raw-memory operations: `write_bytes`, `copy`, `transmute_copy`, and `swap`.
3. Stabilize the additional non-passing probes: `zeroed`, `type_id`, `offset_of`, and `variant_count`.
