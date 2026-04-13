# 0012-nonzero Workpad

Date: 2026-04-11

## Goal

Record the current verification status for the `verify-rust-std/0012-nonzero` challenge after the intrinsic fixes for `rotate_left`, `rotate_right`, and `bitreverse`.

## Plan

- [x] Record the pre-fix baseline (28 pass / 5 fail).
- [x] Capture the newly passing harnesses unlocked by the intrinsic fixes.
- [x] Recompute the overall harness totals for the challenge.
- [x] Record the remaining blockers and their scope.
- [x] Update the evaluation artifacts with the revised readiness assessment.

## Validation Evidence

| Category | Count | Harnesses / Evidence |
| --- | ---: | --- |
| Previously passing | 28 | `new`, `new_unchecked`, `get`, `const_nonzero`, `transmute_wrapper_u8`, `abs`, `bitor`, `byte_order`, `checked_add`, `checked_mul`, `checked_neg`, `checked_next_power_of_two`, `count_ones`, `from_be`, `from_le`, `ilog2`, `isqrt`, `leading_trailing_zeros`, `midpoint`, `neg`, `pow`, `saturating_add`, `saturating_mul`, `saturating_pow`, `signed_ops`, `unchecked_add`, `unchecked_mul`, `unsigned_ops` |
| Previously failing | 5 | `from_mut` (`castKindPtrToPtr`), `min_max` (`FnOnce::call_once`), `rotate_left` (missing intrinsic), `rotate_right` (missing intrinsic), `reverse_bits` (missing `bitreverse`) |
| New passing after intrinsic fixes | 3 | `rotate_left`, `rotate_right`, `reverse_bits` |
| Current total | 33 | 31 `PASS`, 2 `FAIL` |

## Notes

- The challenge currently covers 33 harnesses in total.
- 31 harnesses are passing.
- 2 harnesses remain failing:
  - `from_mut`: blocked on `castKindPtrToPtr`
  - `min_max`: blocked on `FnOnce::call_once`
- The latest improvement is the promotion of 3 harnesses from failing to passing:
  - `rotate_left`
  - `rotate_right`
  - `reverse_bits`
- Coverage is now roughly `31 / 37` Part 2 function-level targets, depending on whether grouped impls are counted separately.
- Readiness assessment: this is close enough to a `submission_ready` handoff because the remaining delta is concentrated in two upstream semantic infrastructure gaps rather than missing challenge-local harness or intrinsic work.
