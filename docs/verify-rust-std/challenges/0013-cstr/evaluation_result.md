# Evaluation Result: Challenge 0013-cstr

## Verdict

`blocked` -- the current branch is `0/3` pass. All three evaluated harnesses
(`clone_to_uninit`, `from_bytes_with_nul_unchecked`, and `from_ptr`) still
fail, so there is no green `CStr` baseline yet.

## Scorecard

| Criterion | Status | Evidence |
| --- | --- | --- |
| Initial harness baseline | PASS | The challenge has three concrete harnesses under evaluation instead of a pure bootstrap state. |
| Current proof health | FAIL | `0/3` harnesses pass. |
| Alignment with plan scope | PARTIAL | The current harness set at least starts with the unsafe roots and branch-local slices called out in the challenge docs. |
| Submission readiness | FAIL | No current `CStr` proof root is green. |
| Residual risk | HIGH | The branch-local docs already point to a shared constructor/body frontier, and the broader safe-method plus `strlen` scope is still untouched. |

## Current Coverage Summary

- Passing harnesses: `0/3`
- Failing harnesses: `3/3`
  - `clone_to_uninit`
  - `from_bytes_with_nul_unchecked`
  - `from_ptr`

## Scope Note

The current `plan.md` and challenge README already indicate that the
`clone_to_uninit` path is blocked on a shared `CStr::from_bytes_with_nul`
constructor/body frontier, and the other two harnesses are not green either.
That means the challenge is still blocked before it can expand into the
remaining safe methods, `strlen`, or the other invariant slices listed in the
branch-local docs.

## Next Steps

1. Unblock the shared constructor/body frontier first, since it is the only
   blocker already identified as common across the current tranche.
2. Re-run `clone_to_uninit` and `from_bytes_with_nul_unchecked` immediately
   after that shift to determine whether they now share a downstream frontier
   or split apart.
3. Reclassify `from_ptr` only after the shared constructor path moves, then
   decide whether the next tranche should target `strlen` or another unsafe
   root.
