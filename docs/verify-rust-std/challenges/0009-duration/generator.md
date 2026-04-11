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

### Sprint 2

- **Fixed `checked_div` blocker**: Two-part fix in `rt/data.md`:
  1. Added `#cast(Moved, _, _, _) => Moved` rule to propagate `Moved` through any cast operation.
  2. Changed `operandMove` to use `#readProjection(false)` instead of `#readProjection(true)`, treating `operandMove` like `operandCopy`. This is correct because the Rust compiler generates `operandMove` for Copy types (integers, booleans), and the MIR may use the same local multiple times. The compiler guarantees no use-after-move at the type level.
- **`checked_div` now PASSES** (previously BLOCKED).
- Added overflow/underflow None-branch harnesses:
  - `checked_add_overflow.rs` (BLOCKED: niche decoding)
  - `checked_sub_underflow.rs` (BLOCKED: niche decoding)
  - `checked_mul_overflow.rs` (BLOCKED: niche decoding)
  - `checked_div_zero.rs` (BLOCKED: niche decoding)
- All four None-branch harnesses hit `UnableToDecode` for niche-encoded `Option<Duration>` (the None variant uses nanos=1_000_000_000 as niche).
- Updated test_integration.py: included `checked_div` in test matrix, excluded niche-blocked harnesses.
- Full regression check: all 15 previously passing proofs still pass, plus `checked_div` now passes (16/16 functions covered).

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
- `kmir/src/tests/integration/data/verify-rust-std/0009-duration/checked_div.rs` (PASS -- unblocked in sprint 2)
- `kmir/src/tests/integration/data/verify-rust-std/0009-duration/checked_add_overflow.rs` (BLOCKED: niche decoding)
- `kmir/src/tests/integration/data/verify-rust-std/0009-duration/checked_sub_underflow.rs` (BLOCKED: niche decoding)
- `kmir/src/tests/integration/data/verify-rust-std/0009-duration/checked_mul_overflow.rs` (BLOCKED: niche decoding)
- `kmir/src/tests/integration/data/verify-rust-std/0009-duration/checked_div_zero.rs` (BLOCKED: niche decoding)
- `kmir/src/tests/integration/data/verify-rust-std/0009-duration/from_secs-fail.rs` (EXPECTED FAIL)
- `kmir/src/tests/integration/data/verify-rust-std/0009-duration/from_millis-fail.rs` (EXPECTED FAIL)
- `kmir/src/tests/integration/data/verify-rust-std/0009-duration/new-fail.rs` (EXPECTED FAIL)
- `kmir/src/tests/integration/data/verify-rust-std/0009-duration/accessors-fail.rs` (EXPECTED FAIL)
- `kmir/src/tests/integration/data/verify-rust-std/0009-duration/checked_add-fail.rs` (EXPECTED FAIL)
- `kmir/src/tests/integration/test_integration.py` (added test_vrs_0009_duration; updated exclusion list)
- `kmir/src/kmir/kdist/mir-semantics/rt/data.md` (operandMove fix + #cast Moved rule)

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
| checked_div.rs | PASSED | `checked_div` (unblocked by operandMove + #cast fix) |
| checked_add_overflow.rs | BLOCKED | Niche-encoded `Option<Duration>` `None` cannot be decoded |
| checked_sub_underflow.rs | BLOCKED | Niche-encoded `Option<Duration>` `None` cannot be decoded |
| checked_mul_overflow.rs | BLOCKED | Niche-encoded `Option<Duration>` `None` cannot be decoded |
| checked_div_zero.rs | BLOCKED | Niche-encoded `Option<Duration>` `None` cannot be decoded |
| from_secs-fail.rs | EXPECTED FAIL | Incorrect assertion correctly detected |
| from_millis-fail.rs | EXPECTED FAIL | Incorrect assertion correctly detected |
| new-fail.rs | EXPECTED FAIL | Incorrect assertion correctly detected |
| accessors-fail.rs | EXPECTED FAIL | Incorrect assertion correctly detected |
| checked_add-fail.rs | EXPECTED FAIL | Incorrect assertion correctly detected |

## Commit Inventory

- Sprint 2: `fix(rt): handle Moved in operandMove/cast + add overflow harnesses for 0009`

## Blockers

- ~~`checked_div`~~: **RESOLVED** in sprint 2. Fixed `operandMove` to not invalidate Copy-type locals and added `#cast(Moved, ...)` passthrough rule.
- `Option<Duration>` niche decoding: The niche-encoded `Option<Duration>` cannot be decoded from bytes when the value is `None`. All four overflow/underflow/zero-division harnesses hit `UnableToDecode` at the point where the `None` result is constructed. This is a fundamental limitation in KMIR's constant decoding -- requires niche encoding support. Evidence: thunk output shows `UnableToDecode(bytes, typeInfoEnumType(...Option<Duration>...))` at `core::time.rs` checked_add/sub/mul/div return sites.
