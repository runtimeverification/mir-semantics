# Evaluation Result: Challenge 0027-arc

Status: `IN PROGRESS`

Harness probes: `1/2` passing

## Verdict

- `in_progress`
- The current harness set has one passing proof root and one expected-fail
  diagnostic harness.
- This challenge remains active rather than blocked because `arc-from-raw-in`
  is green, giving the branch a real regression baseline while the remaining
  frontier is investigated.

## Current Probe Status

- `arc-from-raw-in`: passing
- `arc-from-raw-in-frontier-fail`: expected-fail

## Blocking Frontier

- The remaining diagnostic harness still stops at the current allocator/setup
  frontier.
- That blocker is real, but it does not erase the existing green baseline for
  `Arc::from_raw_in`.

## Next Action

- Preserve `arc-from-raw-in` as the regression baseline and use the expected
  fail harness to continue shrinking or classifying the allocator/setup
  frontier before widening coverage to more `Arc`/`Weak` entry points.

## Evidence Base

- `docs/verify-rust-std/challenges/0027-arc/plan.md`
- `docs/verify-rust-std/challenges/0027-arc/success_criteria.md`
- `docs/verify-rust-std/challenges/0027-arc/workpad.md`
