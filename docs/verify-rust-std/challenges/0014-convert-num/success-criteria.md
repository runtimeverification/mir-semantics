# Success Criteria Coverage: Challenge 0014

This table is the branch-local coverage map for the published Challenge 14
requirements. It is seeded from the challenge page, planner/evaluator notes,
and the currently recorded branch evidence.

Status legend:

- `not started`: no branch-local harness/spec has been added yet
- `harness defined`: a branch-local verification entrypoint exists, but no
  targeted validation has been recorded yet
- `frontier reached`: a proof attempt has reached a concrete frontier or stuck
  leaf
- `blocked`: a precise blocker prevents further proof progress
- `passed`: the entrypoint has been discharged on this branch

| Function | Upstream Location | Harness/Spec File | Start Symbol | Kind | Status | Blocker Class | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `Invariant` for `core::num::NonZero` | `library/core/src/convert/num.rs` and `library/core/src/num/nonzero.rs` | `kmir/src/tests/integration/data/verify-rust-std/0014-convert-num/nonzero_from.rs` | `verify_nonzero_from_u8_to_u16`, `verify_nonzero_from_i8_to_i16` | proof harness | `harness defined` | `UNKNOWN` | First sweep covers widening NonZero conversions only; invariant/spec work is not yet encoded separately. |
| `impl_nonzero_int_from_nonzero_int!(u8 => u16)` | `library/core/src/convert/num.rs` | `kmir/src/tests/integration/data/verify-rust-std/0014-convert-num/nonzero_from.rs` | `verify_nonzero_from_u8_to_u16` | proof harness | `harness defined` | `UNKNOWN` | Representative widening case for the unsigned family. |
| `impl_nonzero_int_from_nonzero_int!(i8 => i16)` | `library/core/src/convert/num.rs` | `kmir/src/tests/integration/data/verify-rust-std/0014-convert-num/nonzero_from.rs` | `verify_nonzero_from_i8_to_i16` | proof harness | `harness defined` | `UNKNOWN` | Representative widening case for the signed family. |
| `impl_nonzero_int_try_from_nonzero_int!(u16 => u8)` | `library/core/src/convert/num.rs` | `kmir/src/tests/integration/data/verify-rust-std/0014-convert-num/nonzero_try_from.rs` | `verify_nonzero_try_from_u16_to_u8` | proof harness | `harness defined` | `UNKNOWN` | First fallible narrowing witness; branch-local proof shape distinguishes success and panic paths. |
| `impl_nonzero_int_try_from_nonzero_int!(i16 => i8)` | `library/core/src/convert/num.rs` | `kmir/src/tests/integration/data/verify-rust-std/0014-convert-num/nonzero_try_from.rs` | `verify_nonzero_try_from_i16_to_i8` | proof harness | `harness defined` | `UNKNOWN` | Signed narrowing witness for the fallible NonZero family. |
| `impl_nonzero_int_try_from_nonzero_int!(u8 => i8)` | `library/core/src/convert/num.rs` | `kmir/src/tests/integration/data/verify-rust-std/0014-convert-num/nonzero_try_from.rs` | `verify_nonzero_try_from_u8_to_i8` | proof harness | `harness defined` | `UNKNOWN` | Cross-sign narrowing witness; exact branch-local frontier still unknown. |
| `impl_nonzero_int_try_from_nonzero_int!(i8 => u8)` | `library/core/src/convert/num.rs` | `kmir/src/tests/integration/data/verify-rust-std/0014-convert-num/nonzero_try_from.rs` | `verify_nonzero_try_from_i8_to_u8` | proof harness | `harness defined` | `UNKNOWN` | Cross-sign narrowing witness; exact branch-local frontier still unknown. |
| `impl_float_to_int!(f16 => i8)` | `library/core/src/convert/num.rs` | `kmir/src/tests/integration/data/verify-rust-std/0014-convert-num/to_int_unchecked.rs` | `verify_to_int_unchecked_f16_i8` | proof harness | `harness defined` | `UNKNOWN` | First float-to-int entrypoint, modeled with the documented finite/in-range guard. |
| `impl_float_to_int!(f32 => i32)` | `library/core/src/convert/num.rs` | `kmir/src/tests/integration/data/verify-rust-std/0014-convert-num/to_int_unchecked.rs` | `verify_to_int_unchecked_f32_i32` | proof harness | `harness defined` | `UNKNOWN` | Representative f32 path. |
| `impl_float_to_int!(f64 => i64)` | `library/core/src/convert/num.rs` | `kmir/src/tests/integration/data/verify-rust-std/0014-convert-num/to_int_unchecked.rs` | `verify_to_int_unchecked_f64_i64` | proof harness | `harness defined` | `UNKNOWN` | Representative f64 path. |
| `impl_float_to_int!(f128 => i128)` | `library/core/src/convert/num.rs` | `kmir/src/tests/integration/data/verify-rust-std/0014-convert-num/to_int_unchecked.rs` | `verify_to_int_unchecked_f128_i128` | proof harness | `harness defined` | `UNKNOWN` | Representative f128 path. |

