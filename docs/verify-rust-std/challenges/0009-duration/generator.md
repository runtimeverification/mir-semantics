# Generator Record: Challenge 0009

Ownership:

- Generator owns this file and the implementation work for this challenge.
- Generator must not edit `evaluator.md` or `rubric.md`.
- Generator should treat planner and evaluator edits as authoritative inputs,
  not as files to rewrite.

## Inputs

- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0009-duration`
- Planner record: `docs/verify-rust-std/challenges/0009-duration/planner.md`
- Evaluator record: `docs/verify-rust-std/challenges/0009-duration/evaluator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0009-duration/rubric.md`

## Scope Boundary

- Authorized code area: this challenge branch only.
- Default repository scope: `runtimeverification/mir-semantics`
- Allowed secondary scope: `runtimeverification/stable-mir-json` when required
- Exceptional scope: `runtimeverification/haskell-backend` only with explicit
  justification logged here and in the evaluator record

## Work Log

- Bootstrap record created by orchestrator.
- Created 10 proof harnesses covering all 5 constructors, 7 accessors, and 3/4 arithmetic operations.
- Created 5 fail variants (from_secs-fail, from_millis-fail, new-fail, accessors-fail, checked_add-fail).
- checked_div blocked by unsupported `#cast(IntToInt)` in KMIR semantics.
- Wired tests into test_integration.py as `test_vrs_0009_duration`.

## Files Touched

- `kmir/src/tests/integration/data/verify-rust-std/0009-duration/from_secs.rs` (PASS)
- `kmir/src/tests/integration/data/verify-rust-std/0009-duration/from_millis.rs` (PASS)
- `kmir/src/tests/integration/data/verify-rust-std/0009-duration/from_micros.rs` (PASS)
- `kmir/src/tests/integration/data/verify-rust-std/0009-duration/from_nanos.rs` (PASS)
- `kmir/src/tests/integration/data/verify-rust-std/0009-duration/new.rs` (PASS)
- `kmir/src/tests/integration/data/verify-rust-std/0009-duration/accessors.rs` (PASS)
- `kmir/src/tests/integration/data/verify-rust-std/0009-duration/checked_add.rs` (PASS)
- `kmir/src/tests/integration/data/verify-rust-std/0009-duration/checked_sub.rs` (PASS)
- `kmir/src/tests/integration/data/verify-rust-std/0009-duration/checked_mul.rs` (PASS)
- `kmir/src/tests/integration/data/verify-rust-std/0009-duration/checked_div.rs` (BLOCKED: #cast IntToInt)
- `kmir/src/tests/integration/data/verify-rust-std/0009-duration/from_secs-fail.rs` (EXPECTED FAIL)
- `kmir/src/tests/integration/data/verify-rust-std/0009-duration/from_millis-fail.rs` (EXPECTED FAIL)
- `kmir/src/tests/integration/data/verify-rust-std/0009-duration/new-fail.rs` (EXPECTED FAIL)
- `kmir/src/tests/integration/data/verify-rust-std/0009-duration/accessors-fail.rs` (EXPECTED FAIL)
- `kmir/src/tests/integration/data/verify-rust-std/0009-duration/checked_add-fail.rs` (EXPECTED FAIL)
- `kmir/src/tests/integration/test_integration.py` (added test_vrs_0009_duration)

## Validation Evidence

All proofs run with: `uv --project kmir run -- kmir prove <file> --verbose --terminate-on-thunk --proof-dir <dir> --reload --fail-fast`

| Harness | Status | Methods Covered |
|---------|--------|----------------|
| from_secs.rs | PASSED | `from_secs`, `as_secs`, `subsec_nanos` |
| from_millis.rs | PASSED | `from_millis`, `as_secs`, `subsec_millis` |
| from_micros.rs | PASSED | `from_micros`, `as_secs`, `subsec_micros` |
| from_nanos.rs | PASSED | `from_nanos`, `as_secs`, `subsec_nanos` |
| new.rs | PASSED | `new`, `as_secs`, `subsec_nanos` |
| accessors.rs | PASSED | `as_millis`, `as_micros`, `as_nanos`, `subsec_millis`, `subsec_micros`, `subsec_nanos` |
| checked_add.rs | PASSED | `checked_add`, unwrap, value verification |
| checked_sub.rs | PASSED | `checked_sub`, unwrap, value verification |
| checked_mul.rs | PASSED | `checked_mul`, unwrap, value verification |
| checked_div.rs | BLOCKED | `checked_div` stuck on `#cast(IntToInt)` at time.rs:822 |
| from_secs-fail.rs | EXPECTED FAIL | Incorrect assertion correctly detected |
| from_millis-fail.rs | EXPECTED FAIL | Incorrect assertion correctly detected |
| new-fail.rs | EXPECTED FAIL | Incorrect assertion correctly detected |
| accessors-fail.rs | EXPECTED FAIL | Incorrect assertion correctly detected |
| checked_add-fail.rs | EXPECTED FAIL | Incorrect assertion correctly detected |

## Commit Inventory

- None yet.

## Blockers

- `checked_div`: KMIR semantics lacks support for `#cast(Moved, castKindIntToInt, ty(27), ty(25))` used in `Duration::checked_div` at `/rust/library/core/src/time.rs:822`. Requires semantic fix.
- `Option<Duration>` niche decoding: The niche-encoded `Option<Duration>` cannot be decoded from bytes when the value is `None`. Workaround: test `Some` cases via `.unwrap()` and `None` cases via `.is_none()` in separate harnesses.
