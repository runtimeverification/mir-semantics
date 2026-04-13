# Evaluation Result: Challenge 0017-slice

## Verdict

`in_progress` -- as of `2026-04-12`, the challenge stands at `13/26` passing harnesses. The slice surface now has a real mid-coverage baseline, but half of the evaluated APIs are still failing.

## Scorecard

| Criterion | Status | Evidence |
| --- | --- | --- |
| Implemented proof baseline | PASS | `26` evaluated harnesses now have recorded outcomes. |
| Current proof health | PARTIAL | `13/26` evaluated harnesses pass. |
| Remaining proof frontier | PARTIAL | `13/26` evaluated harnesses still fail. |
| Submission readiness | FAIL | With half of the evaluated slice surface still red, the challenge remains in active frontier-closing mode. |
| Residual risk | HIGH | The failing half of the suite still covers a large slice of slice API behavior. |

## Current Coverage Summary

- Passing harnesses: `13/26`
  - `index`
  - `first`
  - `get`
  - `contains`
  - `len`
  - `is_empty`
  - `split_at`
  - `iter_count`
  - `fill`
  - `split_first`
  - `iter_position`
  - `iter_enumerate`
  - `as_ptr`
- Failing harnesses: `13/26`
  - The remaining evaluated slice probes are still failing.

## Next Steps

1. Cluster the remaining failures by family so shared slice/subslice gaps can be fixed once instead of probe-by-probe.
2. Recheck mutation-heavy and iterator-adjacent slice probes after each semantic fix, since those are likely to share the next blocker.
3. Refresh the challenge inventory after the next pass so the `13/26` split stays aligned with the live suite.
