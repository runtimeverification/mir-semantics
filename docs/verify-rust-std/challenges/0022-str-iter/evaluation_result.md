# Evaluation Result: Challenge 0022

Status: `BLOCKED`

Harness probes: `0/1` passing

## Verdict

- `blocked`
- The current harness set has `0/1` passing probes.
- This challenge is blocked by a fundamental semantic gap in string decoding, so the active failure is still below the challenge-local string-iterator obligations.

## Blocking Frontier

- String decode support needed by the `str` iterator harness is missing or insufficient.

## Next Action

- Repair the string-decoding semantics, then rerun the existing probe before widening iterator coverage.

## Evidence Base

- `docs/verify-rust-std/challenges/0022-str-iter/plan.md`
