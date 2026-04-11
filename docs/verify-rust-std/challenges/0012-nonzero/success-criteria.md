# Success Criteria Coverage: Challenge 0012

This table is the branch-local coverage map for the published `NonZero`
requirements. It is seeded from the challenge page, planner/evaluator notes,
and the currently recorded branch evidence.

Status legend:

- `passed` means the proof harness runs to completion without errors.
- `frontier reached` means a proof attempt has reached a concrete leaf or
  thunk frontier but has not closed.
- `not started` means no branch-local harness/spec has been added yet.
- `control reproducer` means the file exists only to separate a semantic
  frontier from a generic control shape.

## Semantic changes

Two semantic rules were added to `rt/data.md` to unblock this challenge:

1. **Multi-layer transparent transmute**: recursive unwrap/wrap for nested
   `#[repr(transparent)]` wrappers (e.g. `NonZero<u8>` -> `NonZeroU8Inner` -> `u8`).
2. **Niche-encoded `Option<NonZero<T>>` transmute**: handles the `u8 <-> Option<NonZero<u8>>`
   cast that the Rust compiler generates for `NonZero::new_unchecked` via niche optimization.

## Coverage table

| Function | Harness/Spec File | Status | Blocker | Notes |
| --- | --- | --- | --- | --- |
| `NonZero::new` (u8, i8) | `new.rs` | **passed** | -- | Part 1. Niche-cast blocker resolved. |
| `NonZero::new_unchecked` (u8, i8) | `new_unchecked.rs` | **passed** | -- | Part 1. Niche-cast blocker resolved. |
| `NonZero::get` (u8, i8) | `get.rs` | **passed** | -- | Part 1/2. Multi-layer Down transmute. |
| `NonZero::get` (const) | `const_nonzero.rs` | **passed** | -- | Part 1. Const construction bypass. |
| `NonZero BitOr` (NZ|NZ, NZ|u8) | `bitor.rs` | **passed** | -- | Part 2 bitor. |
| `NonZero::is_positive/is_negative` | `signed_ops.rs` | **passed** | -- | Part 2 signed-only ops. |
| `NonZero::saturating_mul` | `saturating_mul.rs` | **passed** | -- | Part 2 arithmetic. |
| `NonZero::checked_pow` | `pow.rs` | **passed** | -- | Part 2 powers. |
| `NonZero::checked_mul` | `checked_mul.rs` | **passed** | -- | Part 2 arithmetic. |
| `NonZero::checked_add` (no overflow) | `checked_add.rs` | **passed** | -- | Part 2 arithmetic. |
| transmute control | `transmute_wrapper_u8.rs` | **passed** | -- | Control reproducer including Option<NonZero> path. |
| `NonZero::from_mut` | `from_mut.rs` | frontier reached | `castKindPtrToPtr` | Part 1 blocker: pointer-to-pointer cast. |
| `NonZero::leading_zeros` | `leading_trailing_zeros.rs` | frontier reached | `ctlz_nonzero` intrinsic | Part 2 blocker: missing intrinsic. |
| `NonZero::trailing_zeros` | `leading_trailing_zeros.rs` | frontier reached | `ctlz_nonzero` intrinsic | Part 2 blocker: missing intrinsic. |
| `NonZero::ilog2` | `ilog2.rs` | frontier reached | `ctlz_nonzero` intrinsic | Part 2 blocker: delegates to ctlz_nonzero. |
| `NonZero::is_power_of_two` | `unsigned_ops.rs` | frontier reached | `ctpop` intrinsic | Part 2 blocker: missing intrinsic. |
| `NonZero::count_ones` | `count_ones.rs` | frontier reached | `ctpop` intrinsic | Part 2 blocker: missing intrinsic. |
| `NonZero::min/max` | `min_max.rs` | frontier reached | `FnOnce::call_once` | Part 2 blocker: trait dispatch for Ord::cmp. |
| `NonZero` byte-order | `byte_order.rs` | frontier reached | `bswap` intrinsic | Part 2 blocker: missing intrinsic. |
| `NonZero::saturating_add` | `saturating_add.rs` | frontier reached | `saturating_add` intrinsic | Part 2 blocker: missing intrinsic. |
| `NonZero::from_mut_unchecked` | n/a | not started | -- | |
| `NonZero::clamp` | n/a | not started | -- | |
| `NonZero::isqrt` | n/a | not started | -- | |
