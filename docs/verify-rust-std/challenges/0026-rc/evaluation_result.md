# Evaluation Result: Challenge 0026-rc

## Verdict

`in_progress` -- the current tranche has a real green baseline, with `1/3`
evaluated harnesses passing (`rc-from-raw-in`) and two diagnostic harnesses
remaining `expected-fail` (`rc-from-raw-in-frontier-fail`,
`rc-new-in-frontier-fail`). That keeps the challenge active rather than
blocked, but allocator/setup behavior still prevents broader raw-pointer
coverage.

## Scorecard

| Criterion | Status | Evidence |
| --- | --- | --- |
| Initial harness baseline | PASS | The branch has one passing symbolic proof root plus two explicit frontier reproducers. |
| Current proof health | PARTIAL | `1/3` harnesses are green; the two diagnostic harnesses remain intentionally red. |
| Alignment with plan scope | PARTIAL | The current work matches the plan's tranche-1 focus on `Rc::from_raw_in` and allocator-aware raw ownership. |
| Submission readiness | FAIL | A single green root is not enough to cover the broader `Rc`/`Weak` surface tracked in the plan and README. |
| Residual risk | HIGH | Both expected-fail harnesses still point at unresolved allocator/setup behavior. |

## Current Coverage Summary

- Passing harnesses: `1/3`
  - `rc-from-raw-in`
- Expected-fail diagnostic harnesses: `2/3`
  - `rc-from-raw-in-frontier-fail`
  - `rc-new-in-frontier-fail`

## Scope Note

The current branch-local plan already treats the two red harnesses as frontier
diagnostics rather than regressions to hide. That distinction matters: the
challenge is not blocked because it has a stable green proof root, but it is
still far from complete because the allocator/setup frontier has not moved far
enough to unlock the wrapper and sibling unsafe APIs.

## Next Steps

1. Preserve `rc-from-raw-in` as the green regression baseline while working on
   the shared allocator/setup blocker.
2. Re-run both expected-fail harnesses after each semantic change and either
   refresh them to the new frontier or retire one if it stops adding distinct
   diagnostic value.
3. Once the allocator frontier moves, expand immediately into the planned next
   tranche: `Rc::from_raw`, `Rc::increment_strong_count(_in)`,
   `Rc::decrement_strong_count(_in)`, and `Weak::from_raw(_in)`.
