# Planner Record: Challenge 0009

Ownership:

- Planner owns this file.
- Planner must not implement code, proofs, or evaluation.
- Planner may update challenge-local checklists only if the change is purely
  organizational and clearly documented here.

## Inputs

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0009-duration.md
- Tracking issue: [#72](https://github.com/model-checking/verify-rust-std/issues/72)
- Challenge artifact directory: `kmir/src/tests/integration/data/verify-rust-std/0009-duration`
- Generator record: `docs/verify-rust-std/challenges/0009-duration/generator.md`
- Evaluator record: `docs/verify-rust-std/challenges/0009-duration/evaluator.md`

## Requirements Extraction

- Published goal: Verify safety of `core::time::Duration` public API
- Published success criteria:
  - 5 constructors: `new`, `from_secs`, `from_millis`, `from_micros`, `from_nanos`
  - 7 accessors: `as_secs`, `as_millis`, `as_micros`, `as_nanos`, `subsec_millis`, `subsec_micros`, `subsec_nanos`
  - 4 arithmetic: `checked_add`, `checked_sub`, `checked_mul`, `checked_div`
  - UB: no compiler-intrinsic UB, no uninitialized reads, no invalid values
- Challenge-specific UB obligations: No undefined behavior in any of the listed methods
- Additional safety conditions from source docs or SAFETY comments: Duration nanos field must be < 1_000_000_000

## Scope Contract

- In scope for current branch: All 16 Duration methods listed in challenge requirements
- Out of scope unless later justified: `checked_div` blocked by missing `#cast(IntToInt)` in KMIR semantics
- Exceptional dependency escalation policy: Semantic fix for `#cast(IntToInt)` would unblock `checked_div`

## Sprint Contracts

| Sprint | Intended slice | Acceptance check | Status |
| --- | --- | --- | --- |
| 0 | Bootstrap challenge understanding | Requirements and blockers recorded | done |
| 1 | Constructors + accessors | 11 proofs pass | done |
| 2 | Arithmetic (add/sub/mul) | 3 proofs pass | done |
| 3 | Arithmetic (div) | Blocked by #cast(IntToInt) | blocked |

## Dependencies And Blockers

- `checked_div`: Blocked by unsupported `#cast(Moved, castKindIntToInt, ty(27), ty(25))` in KMIR semantics at `/rust/library/core/src/time.rs:822`
- `Option<Duration>` niche encoding: `UnableToDecode` for niche-encoded `Option<Duration>` when the result is `None` (overflow/underflow tests). Workaround: use `.unwrap()` for Some cases, `.is_none()` for None cases separately.

## Cross-Challenge Notes

- No reuse candidates recorded yet.

## History

- Bootstrap record created by orchestrator.
