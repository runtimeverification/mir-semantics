# Evaluation Result: Challenge 0003-pointer-arithmentic

## Verdict

`in_progress` -- as of `2026-04-12`, `5/12` evaluated harnesses are passing (`offset_probe`, `ptr_read`, `ptr_write`, `ptr_eq`, `ptr_is_null`) and `7/12` are still failing. The challenge now has a broader working baseline, but most of the pointer-arithmetic frontier remains red.

## Scorecard

| Criterion | Status | Evidence |
| --- | --- | --- |
| Harness baseline exists | PASS | Twelve challenge-local harnesses now have recorded outcomes. |
| Current proof health | PARTIAL | `5/12` evaluated harnesses pass. |
| Pointer arithmetic frontier closure | FAIL | `7/12` evaluated harnesses remain red. |
| Submission readiness | FAIL | The challenge is still in progress with a majority of the evaluated surface failing. |
| Residual risk | HIGH | The remaining frontier still spans arithmetic, wrapping behavior, null handling, and pointer memory operations. |

## Current Coverage Summary

- Passing harnesses: `5/12`
  - `offset_probe`
  - `ptr_read`
  - `ptr_write`
  - `ptr_eq`
  - `ptr_is_null`
- Failing harnesses: `7/12`
  - `ptr_add`
  - `ptr_offset`
  - `ptr_sub`
  - `ptr_wrapping_add`
  - `ptr_copy_nonoverlapping`
  - `ptr_swap`
  - `ptr_null`

## Next Steps

1. Triage the plain arithmetic frontier first: `ptr_add`, `ptr_offset`, and `ptr_sub`.
2. Separate arithmetic/provenance work from memory-operation fixes in `ptr_copy_nonoverlapping` and `ptr_swap`.
3. Re-run the full challenge sweep after the next semantic change and refresh the `5/12` split.
