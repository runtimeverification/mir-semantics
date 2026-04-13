---
challenge: "0026-rc"
status: "in_progress"
priority: "high"
iteration: 1
last_updated: 2026-04-11
---

## Challenge Requirements

- Verify the `Rc` raw-pointer surface selected by the README's current tranche.
- Keep `Rc::from_raw_in` as the root proof baseline for allocator-aware raw
  ownership.
- Use the two `*-frontier-fail` harnesses as frontier diagnostics until they
  are either resolved or replaced.
- Expand next into the wrapper and sibling unsafe APIs gated on the same raw
  ownership machinery: `Rc::from_raw`, `Rc::increment_strong_count(_in)`,
  `Rc::decrement_strong_count(_in)`, and `Weak::from_raw(_in)`.

## Success Criteria Matrix

| Harness | Requirement slice | Result | Notes |
| --- | --- | --- | --- |
| `rc-from-raw-in` | Symbolic proof for `Rc::from_raw_in` | PASS | Root harness is green and can serve as the tranche baseline |
| `rc-from-raw-in-frontier-fail` | Broader diagnostic reproducer for the same raw-ownership machinery | EXPECTED-FAIL | Still frontiering; keep as a negative repro until the allocator gap moves |
| `rc-new-in-frontier-fail` | Minimized allocator setup reproducer via `Rc::new_in` | EXPECTED-FAIL | Still frontiering; isolates the remaining allocation/setup path |

## Sprint Plan

1. Preserve `rc-from-raw-in` as the green regression target and avoid regressing the passing root proof while frontier work continues.
2. Use the two expected-fail harnesses to characterize the remaining allocator/setup gap and confirm whether they still stop at the same frontier.
3. If the expected-fail cases move, either refresh them to the new frontier or retire them once they stop adding unique diagnostic value.
4. Start the next public unsafe tranche on top of the passing baseline: `Rc::from_raw`, `Rc::increment_strong_count(_in)`, `Rc::decrement_strong_count(_in)`, and `Weak::from_raw(_in)`.

## Blockers

- The tranche has only one passing verification-shaped harness, so coverage is
  still narrow relative to the README scope.
- Both expected-fail harnesses remain red, indicating unresolved allocator or
  setup behavior beyond the root `Rc::from_raw_in` proof.
- Internal-unsafe coverage remains deferred until the public raw-pointer
  surface is broader than the current single green root.
