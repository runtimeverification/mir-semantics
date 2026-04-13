# Evaluation Result: Challenge 0004-btree-node

## Verdict

`blocked` -- the current evaluated set has only `1/5` pass (`btree_probe`),
while `insert_probe`, `get_probe`, `contains_key_probe`, and `len_probe` all
still get stuck on heap allocation. That is enough to establish a reproducible
frontier, but not enough to satisfy the node-local verification goal recorded
in `plan.md`.

## Scorecard

| Criterion | Status | Evidence |
| --- | --- | --- |
| Initial harness baseline | PASS | The challenge is no longer at the `0 existing harnesses` bootstrap state from `plan.md`; five evaluated probes now define a concrete frontier. |
| Current proof health | FAIL | `1/5` harnesses pass and the four behavior-bearing probes all stop at the same heap-allocation class of failure. |
| Alignment with plan scope | PARTIAL | The current probes touch small `BTreeMap` operations, which is directionally consistent with the plan's localized node work. |
| Submission readiness | FAIL | No node-operation proof beyond the smoke probe is green yet. |
| Residual risk | HIGH | The shared allocator frontier prevents progress on node invariants, parent/child relations, and initialized-slot reasoning. |

## Current Coverage Summary

- Passing harnesses: `1/5`
  - `btree_probe`
- Failing harnesses: `4/5`
  - `insert_probe`
  - `get_probe`
  - `contains_key_probe`
  - `len_probe`

## Scope Note

This evaluation follows the current run state, which counts the extra smoke
probe `btree_probe` alongside the four challenge-local behavior probes now
visible in the `0004-btree-node` harness directory. The branch has therefore
moved past bootstrap, but it is still blocked before any meaningful `btree`
node-safety obligation is discharged.

## Next Steps

1. Minimize the shared heap-allocation frontier until one of the four failing
   behavior probes reaches a node-local semantic obligation instead of
   allocator setup.
2. Re-run `insert_probe`, `get_probe`, `contains_key_probe`, and `len_probe`
   immediately after that semantic shift to confirm whether they collapse onto
   one shared fix or split into distinct follow-on blockers.
3. Finish the exact upstream node API inventory promised in `plan.md` once the
   first node-local proof slice is actually reachable.
