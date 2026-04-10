# Success Criteria Map: Challenge 0011

This table maps the published Challenge 11 requirements from
`verify-rust-std/doc/src/challenges/0011-floats-ints.md` to the current
branch-local artifacts and evidence.

Locations below are relative to
`kmir/src/tests/integration/data/verify-rust-std/0011-floats-ints/`.

Status vocabulary:

- `Partial`: at least one branch-local passing slice exists, but the published
  type matrix is still incomplete.
- `Frontier only`: the branch has harnesses and expected-output artifacts, but
  no passing proof slice for the family yet.
- `Blocked`: the branch has a direct blocker with concrete frontier evidence,
  not a passing verification slice.

| Function | Location | Status | Specification | Notes |
| --- | --- | --- | --- | --- |
| `unchecked_add` | `unchecked_add.rs`; `unchecked_add-fail.rs`; `show/unchecked_add-fail.*.expected` | Partial | Part 1: `i8`, `i16`, `i32`, `i64`, `i128`, `u8`, `u16`, `u32`, `u64`, `u128` | Branch-local pass: `unchecked_add_u8`. Remaining widths are still uncovered by passing proofs. |
| `unchecked_sub` | `unchecked_sub.rs`; `unchecked_sub-fail.rs`; `show/unchecked_sub-fail.*.expected` | Partial | Part 1: `i8`, `i16`, `i32`, `i64`, `i128`, `u8`, `u16`, `u32`, `u64`, `u128` | Branch-local pass: `unchecked_sub_u8`. Remaining widths are still uncovered by passing proofs. |
| `unchecked_mul` | `unchecked_mul.rs`; `unchecked_mul-fail.rs`; `show/unchecked_mul-fail.*.expected` | Partial | Part 1: `i8`, `i16`, `i32`, `i64`, `i128`, `u8`, `u16`, `u32`, `u64`, `u128` | Branch-local passes: `unchecked_mul_u8`, `unchecked_mul_u16`, `unchecked_mul_u32`, `unchecked_mul_u64`. Signed widths and `u128` remain uncovered. |
| `unchecked_shl` | `unchecked_shl.rs`; `unchecked_shl-fail.rs`; `show/unchecked_shl-fail.*.expected` | Partial | Part 1: `i8`, `i16`, `i32`, `i64`, `i128`, `u8`, `u16`, `u32`, `u64`, `u128` | Branch-local passes: `unchecked_shl_u8`, `unchecked_shl_u16`, `unchecked_shl_u32`, `unchecked_shl_u64`, and `unchecked_shl_u128`. The unsigned half now has a passing slice at every published width; the next technical step is `unchecked_shl_i8`. |
| `unchecked_shr` | `unchecked_shr.rs`; `unchecked_shr-fail.rs`; `show/unchecked_shr-fail.*.expected` | Frontier only | Part 1: `i8`, `i16`, `i32`, `i64`, `i128`, `u8`, `u16`, `u32`, `u64`, `u128` | No branch-local passing slice yet. The smallest direct target is `unchecked_shr_u8`, and the fail artifacts collapse to the shared `binOpShrUnchecked` frontier. |
| `unchecked_neg` | `unchecked_neg.rs`; `unchecked_neg-fail.rs`; `show/unchecked_neg-fail.*.expected` | Partial | Part 1: `i8`, `i16`, `i32`, `i64`, `i128` | Branch-local pass: `unchecked_neg_i8`. Remaining signed widths are still uncovered by passing proofs. |
| `wrapping_shl` | `wrapping_shl.rs` | Partial | Part 2: `i8`, `i16`, `i32`, `i64`, `i128`, `u8`, `u16`, `u32`, `u64`, `u128` | Branch-local pass: `wrapping_shl_u8`. Remaining widths are still uncovered by passing proofs. |
| `wrapping_shr` | `wrapping_shr.rs` | Partial | Part 2: `i8`, `i16`, `i32`, `i64`, `i128`, `u8`, `u16`, `u32`, `u64`, `u128` | Branch-local pass: `wrapping_shr_u8`. Remaining widths are still uncovered by passing proofs. |
| `widening_mul` | `widening_mul.rs` | Partial | Part 2: `u8`, `u16`, `u32`, `u64` | Branch-local pass: `widening_mul_u8`. Remaining widths are still uncovered by passing proofs. |
| `carrying_mul` | `carrying_mul.rs` | Partial | Part 2: `u8`, `u16`, `u32`, `u64` | Branch-local pass: `carrying_mul_u8`. Remaining widths are still uncovered by passing proofs. |
| `to_int_unchecked` | `to_int_unchecked-fail.rs`; `show/to_int_unchecked-fail.*.expected` | Blocked | Part 3: `f16`, `f32`, `f64`, `f128` | `to_int_unchecked-fail.rs` is the current minimal reproducer/frontier harness. `f32/i32` and `f64/i64` stop at stuck `fabsf32` / `fabsf64` intrinsics; `f16/i8` and `f128/i128` fail artifacts exist, but Part 3 is not yet a passing verification harness. |
