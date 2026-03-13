# Challenge 0011: Safety of Methods for Numeric Primitive Types

Tests for [verify-rust-std challenge 0011](https://model-checking.github.io/verify-rust-std/challenges/0011-floats-ints.html), which verifies the safety of public unsafe methods for floats and integers in `core::num`.

## Part 1: Unsafe Integer Methods

All types: i8, i16, i32, i64, i128, u8, u16, u32, u64, u128

- [x] `unchecked_add`
- [x] `unchecked_sub`
- [x] `unchecked_mul`
- [x] `unchecked_shl`
- [x] `unchecked_shr`

Signed only: i8, i16, i32, i64, i128

- [x] `unchecked_neg`

## Part 2: Safe API Verification

All types: i8, i16, i32, i64, i128, u8, u16, u32, u64, u128

- [x] `wrapping_shl`
- [x] `wrapping_shr`

Unsigned only: u8, u16, u32, u64

- [x] `widening_mul`
- [x] `carrying_mul`

## Part 3: Float to Integer Conversion

TODO: Currently floats are unsupported. However there the required harnesses are
added to `to_int_unchecked-fail.txt` which should be changed to `.rs` when floats
will not cause thunks and branching

Types: f16, f32, f64, f128

- [ ] `to_int_unchecked`
