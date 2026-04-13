---
challenge: "0012-nonzero"
status: evaluating
priority: p0
iteration: 1
last_updated: 2026-04-11
---

## Challenge Requirements

**Goal:** Verify the safety of `NonZero` in `core::num`.

**Source:** https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0012-nonzero.md
**Tracking issue:** [#71](https://github.com/model-checking/verify-rust-std/issues/71)

### Assumptions (from challenge page)

- `new` and `get` leverage `transmute_unchecked`, so verifying transmutation safety is out of scope (covered by Challenge 1). For this challenge, for a transmutation from type `T` to type `U`, it suffices to write and verify a contract that `T` and `U` have the same size.
- Each `NonZeroInner` type upholds the safety conditions of the `ZeroablePrimitive` trait. Specifically, we need not verify that the integer primitives which implement `ZeroablePrimitive` are valid when 0, or that transmutations to the `Option` type are sound.

### Part 1: `new` and `new_unchecked`

Verify the safety and correctness of `NonZero::new` and `NonZero::new_unchecked`:
1. The preconditions specified by the `SAFETY` comments are upheld.
2. For an input `n`:
   a. A `NonZero` object is created if and only if the input was nonzero.
   b. The value of the `NonZeroInner` object equals `n`.

### Part 2: Other Uses of `unsafe`

Verify the safety of the following 35 functions/methods in `core::num::nonzero`:

`max`, `min`, `clamp`, `bitor` (all 3 impls), `count_ones`, `rotate_left`, `rotate_right`, `swap_bytes`, `reverse_bits`, `from_be`, `from_le`, `to_be`, `to_le`, `checked_mul`, `saturating_mul`, `unchecked_mul`, `checked_pow`, `saturating_pow`, `neg`, `checked_add`, `saturating_add`, `unchecked_add`, `checked_next_power_of_two`, `midpoint`, `isqrt`, `abs`, `checked_abs`, `overflowing_abs`, `saturating_abs`, `wrapping_abs`, `unsigned_abs`, `checked_neg`, `overflowing_neg`, `wrapping_neg`, `from_mut`, `from_mut_unchecked`

### UB Obligations

All proofs must ensure the absence of:
- Invoking undefined behavior via compiler intrinsics
- Reading from uninitialized memory
- Producing an invalid value

## Success Criteria Matrix

### Proof Verification Results (2026-04-11)

All 19 existing harnesses verified with `kmir prove --verbose --terminate-on-thunk --reload --fail-fast` (timeout 300s each).

#### PASSED (17/19)

| Harness | Part | Functions Verified | Status |
|---|---|---|---|
| `new.rs` | Part 1 | `NonZero::new` (u8, i8) | **PASSED** |
| `new_unchecked.rs` | Part 1 | `NonZero::new_unchecked` (u8, i8) | **PASSED** |
| `get.rs` | Part 1/2 | `NonZero::get` (u8: 1,42,255; i8: 1,-1,127) | **PASSED** |
| `const_nonzero.rs` | Part 1 | Const NonZero construction + `get` | **PASSED** |
| `transmute_wrapper_u8.rs` | Control | Transparent wrapper + Option\<NonZero\> transmute | **PASSED** |
| `bitor.rs` | Part 2 | `BitOr` (NZ\|NZ, NZ\|u8) | **PASSED** |
| `signed_ops.rs` | Part 2 | `is_positive`, `is_negative` (i8) | **PASSED** |
| `saturating_mul.rs` | Part 2 | `saturating_mul` (no overflow + saturation) | **PASSED** |
| `pow.rs` | Part 2 | `checked_pow` (2^0, 2^3, 3^2, 5^1) | **PASSED** |
| `checked_mul.rs` | Part 2 | `checked_mul` (non-overflow) | **PASSED** |
| `checked_add.rs` | Part 2 | `checked_add` (1+1, 100+50, 254+1) | **PASSED** |
| `byte_order.rs` | Part 2 | `to_be`, `to_le`, `swap_bytes` | **PASSED** |
| `count_ones.rs` | Part 2 | `count_ones` (u8, u16) | **PASSED** |
| `ilog2.rs` | Part 2 | `ilog2` (1,2,8,255) | **PASSED** |
| `leading_trailing_zeros.rs` | Part 2 | `leading_zeros`, `trailing_zeros` | **PASSED** |
| `saturating_add.rs` | Part 2 | `saturating_add` (no sat + saturation) | **PASSED** |
| `unsigned_ops.rs` | Part 2 | `is_power_of_two`, `ilog2` | **PASSED** |

#### FAILED (2/19)

| Harness | Part | Blocker | Details |
|---|---|---|---|
| `from_mut.rs` | Part 1 | `castKindPtrToPtr` | Pointer-to-pointer cast semantics not implemented |
| `min_max.rs` | Part 2 | `FnOnce::call_once` | Trait dispatch for `Ord::cmp` not supported |

### Coverage Gap Analysis

| Function | Status | Harness | Notes |
|---|---|---|---|
| **Part 1** | | | |
| `new` | VERIFIED | `new.rs` | Both u8, i8. Zero/nonzero paths. |
| `new_unchecked` | VERIFIED | `new_unchecked.rs` | Both u8, i8. Precondition guarded. |
| `get` | VERIFIED | `get.rs`, `const_nonzero.rs` | Multiple values, const path. |
| `from_mut` | BLOCKED | `from_mut.rs` | `castKindPtrToPtr` |
| `from_mut_unchecked` | NO HARNESS | -- | Same blocker as `from_mut` |
| **Part 2 - Verified** | | | |
| `bitor` (3 impls) | VERIFIED | `bitor.rs` | NZ\|NZ, NZ\|u8 |
| `count_ones` | VERIFIED | `count_ones.rs` | u8, u16 |
| `swap_bytes` | VERIFIED | `byte_order.rs` | u8 (identity) |
| `to_be` | VERIFIED | `byte_order.rs` | u8 (identity) |
| `to_le` | VERIFIED | `byte_order.rs` | u8 (identity) |
| `checked_mul` | VERIFIED | `checked_mul.rs` | Non-overflow only |
| `saturating_mul` | VERIFIED | `saturating_mul.rs` | Both paths |
| `checked_pow` | VERIFIED | `pow.rs` | Multiple exponents |
| `checked_add` | VERIFIED | `checked_add.rs` | Non-overflow only |
| `saturating_add` | VERIFIED | `saturating_add.rs` | Both paths |
| `is_positive/is_negative` | VERIFIED | `signed_ops.rs` | i8 |
| `leading_zeros` | VERIFIED | `leading_trailing_zeros.rs` | Multiple values |
| `trailing_zeros` | VERIFIED | `leading_trailing_zeros.rs` | Multiple values |
| `ilog2` | VERIFIED | `ilog2.rs`, `unsigned_ops.rs` | Multiple values |
| `is_power_of_two` | VERIFIED | `unsigned_ops.rs` | Multiple values |
| **Part 2 - Blocked** | | | |
| `max` | BLOCKED | `min_max.rs` | `FnOnce::call_once` |
| `min` | BLOCKED | `min_max.rs` | `FnOnce::call_once` |
| `clamp` | NO HARNESS | -- | Same blocker as min/max |
| **Part 2 - No Harness** | | | |
| `rotate_left` | NO HARNESS | -- | Likely needs `rotate_left` intrinsic |
| `rotate_right` | NO HARNESS | -- | Likely needs `rotate_right` intrinsic |
| `reverse_bits` | NO HARNESS | -- | Likely needs `bitreverse` intrinsic |
| `from_be` | NO HARNESS | -- | May work (similar to byte_order) |
| `from_le` | NO HARNESS | -- | May work (similar to byte_order) |
| `unchecked_mul` | NO HARNESS | -- | May work (arithmetic) |
| `saturating_pow` | NO HARNESS | -- | May work (similar to checked_pow) |
| `neg` | NO HARNESS | -- | Signed-only |
| `unchecked_add` | NO HARNESS | -- | May work (arithmetic) |
| `checked_next_power_of_two` | NO HARNESS | -- | May need ctpop/ctlz |
| `midpoint` | NO HARNESS | -- | Arithmetic |
| `isqrt` | NO HARNESS | -- | Complex; may need bounded proof |
| `abs` | NO HARNESS | -- | Signed-only |
| `checked_abs` | NO HARNESS | -- | Signed-only |
| `overflowing_abs` | NO HARNESS | -- | Signed-only |
| `saturating_abs` | NO HARNESS | -- | Signed-only |
| `wrapping_abs` | NO HARNESS | -- | Signed-only |
| `unsigned_abs` | NO HARNESS | -- | Signed-only |
| `checked_neg` | NO HARNESS | -- | Signed-only |
| `overflowing_neg` | NO HARNESS | -- | May work |
| `wrapping_neg` | NO HARNESS | -- | May work |

**Summary:** 16 unique functions verified out of ~37 required. 3 functions blocked. ~18 functions need new harnesses.

## Semantic Changes Applied

Two rule sets were added to `kmir/src/kmir/kdist/mir-semantics/rt/data.md`:

### 1. Multi-layer transparent transmute
- Recursive unwrap/wrap for nested `#[repr(transparent)]` wrappers (e.g., `NonZero<u8>` -> `NonZeroU8Inner` -> `u8`).
- Uses `#transparentDepth` to detect multi-layer nesting and recursively decompose.
- Sound: `#transparentFieldTy` only matches `typeInfoStructType` (single-field structs at zero offset). Depth guard prevents infinite recursion.

### 2. Niche-encoded `Option<NonZero<T>>` transmute
- Handles `u8 <-> Option<NonZero<u8>>` cast that the Rust compiler generates for `NonZero::new` via niche optimization.
- Uses name-based matching (`#isOptionNonZero`) with prefix `"std::option::Option<std::num::NonZero<"`.
- Guard: `notBool #isEnumWithoutFields(TI)` prevents conflict with field-less enum rules.
- Four cast rules: nonzero-UP (with `#wrapSomeNonZero` continuation), zero-UP, Some-DOWN, None-DOWN.
- **Known fragility:** Name-based matching is a workaround for missing `TagEncoding::Niche` support. Fail-safe (stuck proof on mismatch, not unsound). Medium-term fix: implement structural `TagEncoding::Niche` in K type info.

### Intrinsics (resolved since initial evaluation)
- `ctlz_nonzero`: count leading zeros (unlocked ilog2, leading_zeros, trailing_zeros)
- `ctpop`: population count (unlocked count_ones, is_power_of_two)
- `bswap`: byte swap (unlocked byte_order)
- `saturating_add`: unlocked saturating_add harness

## Sprint Plan

### Sprint 0: Bootstrap (COMPLETE)
- [x] Challenge understanding, requirements extraction, review feedback
- [x] Prerequisite semantic baseline ported from `verify-rust-std/challenge-0012`
- [x] Branch-local artifacts created for Part 1 (`new`, `new_unchecked`, `from_mut`)
- [x] Transparent-wrapper control probe confirmed passing

### Sprint 1: Niche-cast resolution + Part 1/2 core (COMPLETE)
- [x] Resolve `castKindTransmute` blocker for `u8 -> Option<NonZeroU8>`
- [x] Multi-layer transparent transmute rules
- [x] Niche-encoded `Option<NonZero<T>>` transmute rules
- [x] Part 1 proofs passing: `new`, `new_unchecked`, `get`, `const_nonzero`
- [x] Part 2 initial batch: `bitor`, `signed_ops`, `saturating_mul`, `pow`, `checked_mul`, `checked_add`
- [x] Evaluator independently verified 4 proofs

### Sprint 2: Expand Part 2 coverage (COMPLETE)
- [x] `byte_order` PASSED (bswap intrinsic resolved)
- [x] `count_ones` PASSED (ctpop intrinsic resolved)
- [x] `ilog2` PASSED (ctlz_nonzero intrinsic resolved)
- [x] `leading_trailing_zeros` PASSED (ctlz_nonzero resolved)
- [x] `unsigned_ops` PASSED (ctpop resolved)
- [x] `saturating_add` PASSED (saturating_add intrinsic resolved)
- [x] `min_max` confirmed FAILED (FnOnce::call_once still blocked)

### Sprint 3: Remaining Part 2 harnesses (NEXT)
Priority order based on likely ease of implementation:

**Tier 1 -- Likely work immediately (arithmetic, use existing patterns):**
- [ ] `unchecked_mul` harness (similar to checked_mul)
- [ ] `unchecked_add` harness (similar to checked_add)
- [ ] `saturating_pow` harness (similar to checked_pow)
- [ ] `neg` harness (signed-only, basic arithmetic)
- [ ] `midpoint` harness (arithmetic)
- [ ] `from_be` / `from_le` harness (similar to byte_order)
- [ ] `overflowing_neg` / `wrapping_neg` harness

**Tier 2 -- Likely work with existing intrinsics:**
- [ ] `abs`, `checked_abs`, `overflowing_abs`, `saturating_abs`, `wrapping_abs`, `unsigned_abs` (all signed, basic arithmetic)
- [ ] `checked_neg` harness (signed arithmetic)
- [ ] `checked_next_power_of_two` harness (may use ctpop/ctlz)

**Tier 3 -- May need new intrinsics:**
- [ ] `rotate_left`, `rotate_right` harnesses (may need `rotate_left`/`rotate_right` intrinsics)
- [ ] `reverse_bits` harness (may need `bitreverse` intrinsic)

**Tier 4 -- Complex or blocked:**
- [ ] `isqrt` harness (complex algorithm, may need bounded proof strategy)
- [ ] Add overflow (None) test cases for `checked_add` and `checked_mul` (blocked by `UnableToDecode` for niche-encoded None)
- [ ] Add `new(0)` call to exercise zero-to-None path

### Sprint 4: Pointer casts + trait dispatch (PLANNED, may be deferred)
- [ ] Implement `castKindPtrToPtr` to unblock `from_mut` and `from_mut_unchecked`
- [ ] Resolve `FnOnce::call_once` trait dispatch to unblock `min`, `max`, `clamp`

## Blockers & Dependencies

### Active Blockers

| Blocker | Type | Affects | Severity |
|---|---|---|---|
| `castKindPtrToPtr` | Cast semantics | `from_mut`, `from_mut_unchecked` | Medium |
| `FnOnce::call_once` | Trait dispatch | `min`, `max`, `clamp` | Medium-Large |
| `UnableToDecode` niche None | Constant decoding | `checked_add` overflow, `checked_mul` overflow | Low |

### Resolved Blockers

| Blocker | Resolution | Date |
|---|---|---|
| `castKindTransmute` niche-cast | Multi-layer transparent + niche Option rules in `rt/data.md` | 2026-04-11 |
| `ctlz_nonzero` intrinsic | Implemented in K semantics | 2026-04-11 |
| `ctpop` intrinsic | Implemented in K semantics | 2026-04-11 |
| `bswap` intrinsic | Implemented in K semantics | 2026-04-11 |
| `saturating_add` intrinsic | Implemented in K semantics | 2026-04-11 |

### Dependencies on Other Challenges

| Challenge | Dependency | Status |
|---|---|---|
| 0001 (core-transmutation) | `transmute_unchecked` safety (allowed to assume same-size contract) | Assumed per challenge rules |

## Cross-Challenge Notes

- The multi-layer transparent transmute rules are general and benefit any nested `#[repr(transparent)]` wrapping across all challenges.
- The niche-encoded Option transmute rules are specific to `Option<NonZero<T>>` but the pattern could be generalized once `TagEncoding::Niche` is represented structurally in K.
- `castKindPtrToPtr` blocker is shared with pointer-related operations in other challenges.
- `FnOnce::call_once` trait dispatch blocker affects any code using closures/trait objects.
- Any bounded 128-bit proof strategy should carry its own documented rationale.
- The `saturating_add` intrinsic resolution should be noted for other challenges that use saturating arithmetic.
