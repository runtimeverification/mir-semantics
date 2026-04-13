# Evaluation Result: Challenge 0009-duration

## Verdict

`submission_ready` -- all `16/16` required `Duration` methods have passing proofs. The remaining blocked overflow/underflow harnesses are valuable follow-up coverage, but they do not prevent meeting the stated required-method target.

## Scorecard

| Criterion | Status | Evidence |
| --- | --- | --- |
| Required method coverage | PASS | All `16/16` required constructors, accessors, and arithmetic methods pass on the supported path. |
| Harness health for required scope | PASS | Every required-method harness is green, including `checked_add`, `checked_sub`, `checked_mul`, and `checked_div`. |
| Negative-path overflow/underflow coverage | BLOCKED | `4` harnesses for `None`/error paths fail because KMIR cannot yet decode niche-encoded `Option<Duration>`. |
| Soundness checks | PASS | `5` expected-fail harnesses fail as intended, confirming the proofs are not vacuous. |
| Reproducibility | PASS | The suite is fully runnable with direct `kmir prove` commands over the challenge-local harness directory. |

## Current Coverage Summary

- Required methods passing: `16/16`
- Blocked extra harnesses: `4`
  - `checked_add_overflow.rs`
  - `checked_sub_underflow.rs`
  - `checked_mul_overflow.rs`
  - `checked_div_zero.rs`
- Expected-fail harnesses behaving correctly: `5/5`

## Reproducibility Evidence Commands

```bash
cd /home/zhaoji/projs/mir-semantics-vrs/challenges/0009-duration

# Reproduce representative passing proofs
uv --project kmir run -- kmir prove \
  kmir/src/tests/integration/data/verify-rust-std/0009-duration/new.rs \
  --verbose --terminate-on-thunk \
  --proof-dir /tmp/kmir-0009-new --reload --fail-fast

uv --project kmir run -- kmir prove \
  kmir/src/tests/integration/data/verify-rust-std/0009-duration/checked_div.rs \
  --verbose --terminate-on-thunk \
  --proof-dir /tmp/kmir-0009-checked-div --reload --fail-fast

# Reproduce the current niche-decoding blocker
uv --project kmir run -- kmir prove \
  kmir/src/tests/integration/data/verify-rust-std/0009-duration/checked_add_overflow.rs \
  --verbose --terminate-on-thunk \
  --proof-dir /tmp/kmir-0009-checked-add-overflow --reload --fail-fast

# Reproduce an expected-fail soundness check
uv --project kmir run -- kmir prove \
  kmir/src/tests/integration/data/verify-rust-std/0009-duration/new-fail.rs \
  --verbose --terminate-on-thunk \
  --proof-dir /tmp/kmir-0009-new-fail --reload --fail-fast

# Sweep the full challenge harness directory
for f in kmir/src/tests/integration/data/verify-rust-std/0009-duration/*.rs; do
  name=$(basename "$f" .rs)
  uv --project kmir run -- kmir prove "$f" \
    --verbose --terminate-on-thunk \
    --proof-dir "/tmp/kmir-0009-$name" --reload --fail-fast
done
```

## Actionable Next Steps

1. Submit the challenge based on the current `16/16` required-method result set.
2. Track the `Option<Duration>` niche-decoding issue as a separate KMIR semantic gap; it affects `None`-path verification rather than the already-satisfied required-method bar.
3. Keep the `operandMove` fix isolated and reviewable so this challenge can cherry-pick cleanly if the semantic change is split into its own PR.
4. Once niche decoding exists, rerun the four blocked overflow/underflow harnesses to upgrade the challenge from submission-ready to stronger total-path coverage.
