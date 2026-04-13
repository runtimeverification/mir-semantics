# Evaluation Result: Challenge 0020

Status: `BLOCKED`

Harness probes: `0/1` passing

## Verdict

- `blocked`
- The current harness set has `0/1` passing probes.
- This challenge is blocked by a fundamental semantic gap in string decoding, so the active failure is still below the challenge-local string-pattern obligations.

## Blocking Frontier

- String decode support needed by the `str` pattern harness is missing or insufficient.

## Next Action

- Repair the string-decoding semantics, then rerun the existing probe before widening pattern coverage.

## Evidence Base

- `docs/verify-rust-std/challenges/0020-str-pattern-pt1/plan.md`
