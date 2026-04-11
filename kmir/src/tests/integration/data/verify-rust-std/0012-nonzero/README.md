# Challenge 0012: Challenge 12: Safety of `NonZero`

Reference inputs:

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0012-nonzero.md
- Tracking issue: [#71](https://github.com/model-checking/verify-rust-std/issues/71)
- Tracking issue state at bootstrap: `OPEN`

Execution context:

- Branch: `verify-rust-std/reexec-0012-nonzero`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0012-nonzero`
- Planner record: `docs/verify-rust-std/challenges/0012-nonzero/planner.md`
- Generator record: `docs/verify-rust-std/challenges/0012-nonzero/generator.md`
- Evaluator record: `docs/verify-rust-std/challenges/0012-nonzero/evaluator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0012-nonzero/rubric.md`

Challenge-local artifact contract:

- Place harnesses, tests, expected output, and supporting files in this
  directory.
- Keep changes organized so proof or semantic commits can be cherry-picked
  cleanly later.
- Record any exceptional dependency change in the generator and evaluator logs
  before landing it.
- Keep the proof coverage map in
  `docs/verify-rust-std/challenges/0012-nonzero/success-criteria.md`.

## Semantic changes

### Multi-layer transparent transmute (rt/data.md)

Added rules to handle `castKindTransmute` for types with nested transparent
wrappers (e.g. `NonZero<u8>` = `NonZero<u8>` -> `NonZeroU8Inner` -> `u8`).
Uses `#transparentDepth` to detect multi-layer wrapping and recursively
unwrap/wrap each layer.

### Niche-encoded `Option<NonZero<T>>` transmute (rt/data.md)

Added rules to handle the niche-encoded transmute between an integer type and
`Option<NonZero<T>>`. Uses name-based matching (`#isOptionNonZero`) since
`TagEncoding::Niche` data is not yet represented in K. Handles:
- UP: nonzero integer -> Some(NonZero<T>) via continuation `#wrapSomeNonZero`
- UP: zero -> None
- DOWN: Some(NonZero<T>) -> integer (recursive unwrap)
- DOWN: None -> 0

## Proof harness status

### PASSING (10 harnesses)

| Harness | Part | Operations verified |
|---------|------|-------------------|
| `new.rs` | Part 1 | `NonZero::new` (u8, i8) |
| `new_unchecked.rs` | Part 1 | `NonZero::new_unchecked` (u8, i8) |
| `const_nonzero.rs` | Part 1 | const NonZero construction + `get` |
| `get.rs` | Part 1/2 | `NonZero::get` (u8, i8, multiple values) |
| `transmute_wrapper_u8.rs` | Control | transparent wrapper + Option<NonZero> transmute |
| `bitor.rs` | Part 2 | `BitOr` (NonZero|NonZero, NonZero|u8) |
| `signed_ops.rs` | Part 2 | `is_positive`, `is_negative` (i8) |
| `saturating_mul.rs` | Part 2 | `saturating_mul` (no overflow, overflow) |
| `pow.rs` | Part 2 | `checked_pow` (various exponents) |
| `checked_mul.rs` | Part 2 | `checked_mul` (non-overflow case) |
| `checked_add.rs` | Part 2 | `checked_add` (non-overflow cases) |

### FAILING (separate blockers, not niche-cast)

| Harness | Blocker | Details |
|---------|---------|---------|
| `from_mut.rs` | `castKindPtrToPtr` | Pointer-to-pointer cast not supported |
| `leading_trailing_zeros.rs` | `ctlz_nonzero` intrinsic | Count leading zeros intrinsic not implemented |
| `ilog2.rs` | `ctlz_nonzero` intrinsic | ilog2 delegates to ctlz_nonzero |
| `unsigned_ops.rs` | `ctpop` intrinsic | is_power_of_two delegates to ctpop |
| `count_ones.rs` | `ctpop` intrinsic | count_ones delegates to ctpop |
| `min_max.rs` | `FnOnce::call_once` | Trait dispatch for Ord::cmp |
| `byte_order.rs` | `bswap` intrinsic | Byte swap intrinsic not implemented |
| `saturating_add.rs` | `saturating_add` intrinsic | Not implemented |

## Key findings

1. The primary niche-cast blocker (`castKindTransmute` for `u8 -> Option<NonZeroU8>`)
   is RESOLVED by the semantic changes in this branch.
2. Part 1 (`new`, `new_unchecked`, `get`) is fully verified.
3. Part 2 coverage includes: bitor, signed ops, saturating_mul, checked_pow,
   checked_mul, checked_add.
4. Remaining Part 2 gaps are due to missing intrinsics (`ctlz_nonzero`, `ctpop`,
   `bswap`, `saturating_add`) and trait dispatch limitations, not the niche-cast.
