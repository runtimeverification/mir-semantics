# Success Criteria Coverage: Challenge 0001

This branch-local coverage map is seeded from the upstream challenge page and
the current harness sweep plan.

Status legend:

- `passed` means the proof ran to completion and was verified by the backend.
- `harness defined` means a branch-local proof-shaped entrypoint exists, but
  the branch has not yet classified the resulting frontier.
- `not started` means there is no branch-local harness/spec yet.
- `frontier reached` means a proof run reached a concrete leaf or thunk for
  the named entrypoint.
- `blocked` means the function depends on unsupported semantic features.

## Summary

**Passed**: 19 harnesses covering functions `transmute`, `transmute_unchecked`,
and `MaybeUninit` methods.

**Blocked**: Functions requiring char transmute (u32->char), missing intrinsics
(ctpop, write_bytes), complex pointer operations, or string/iterator handling.

## Coverage Table

| Function | Upstream Location | Harness/Spec File | Kind | Status | Blocker Class | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `transmute` | `core::intrinsics` | `verify-rust-std/0001-core-transmutation/transmute_roundtrip.rs` | proof harness | passed | - | Byte-array <-> u64 roundtrip. |
| `transmute` | `core::intrinsics` | `verify-rust-std/0001-core-transmutation/transmute_integers.rs` | proof harness | passed | - | Integer roundtrips: u32/i32, u16/i16, u64/i64, u8/i8, usize/isize. |
| `transmute` | `core::intrinsics` | `verify-rust-std/0001-core-transmutation/transmute_array_bytes.rs` | proof harness | passed | - | Byte array <-> u32/u16 conversions with endianness checks. |
| `transmute` | `core::intrinsics` | `verify-rust-std/0001-core-transmutation/transmute_multi_width.rs` | proof harness | passed | - | u128/i128, i32/i64 byte roundtrips. |
| `transmute` | `core::intrinsics` | `verify-rust-std/0001-core-transmutation/transmute_roundtrip_comprehensive.rs` | proof harness | passed | - | All integer widths byte roundtrips. |
| `transmute` | `core::intrinsics` | `verify-rust-std/0001-core-transmutation/transmute_same_type.rs` | proof harness | passed | - | Identity transmute (same type). |
| `transmute` | `core::intrinsics` | `verify-rust-std/0001-core-transmutation/transmute_wrapper_structs.rs` | proof harness | passed | - | T <-> single-field wrapper struct. |
| `transmute` | `core::intrinsics` | `verify-rust-std/0001-core-transmutation/transmute_struct_fields.rs` | proof harness | passed | - | repr(transparent) struct roundtrips. |
| `transmute` | `core::intrinsics` | `verify-rust-std/0001-core-transmutation/transmute_enum.rs` | proof harness | passed | - | u8 -> fieldless enum (Color, Status). |
| `transmute` | `core::intrinsics` | `verify-rust-std/0001-core-transmutation/transmute_enum_variants.rs` | proof harness | passed | - | Extended enum transmute (Direction, Opcode, Bool). |
| `transmute_unchecked` | `core::intrinsics` | `verify-rust-std/0001-core-transmutation/transmute_unchecked_integers.rs` | proof harness | passed | - | transmute_unchecked integer roundtrips: u32/i32, u64/i64, u8/i8, u16/i16. |
| `transmute_unchecked` | `core::intrinsics` | `verify-rust-std/0001-core-transmutation/transmute_unchecked_maybeuninit_int.rs` | proof harness | passed | - | transmute_unchecked T -> MaybeUninit<T> with assume_init extraction. |
| `transmute_unchecked` | `core::intrinsics` | `verify-rust-std/0001-core-transmutation/transmute_unchecked_struct.rs` | proof harness | passed | - | transmute_unchecked struct -> MaybeUninit<struct>. |
| `MaybeUninit::new` / `assume_init` | `core::mem` | `verify-rust-std/0001-core-transmutation/maybeuninit_basic.rs` | proof harness | passed | - | new + assume_init for u32, i64, u8, bool, usize. |
| `MaybeUninit::new` / `assume_init` | `core::mem` | `verify-rust-std/0001-core-transmutation/maybeuninit_write_assume_init.rs` | proof harness | passed | - | Nested new/assume_init, i8, i16, i32, u128. |
| `MaybeUninit::assume_init_ref` | `core::mem` | `verify-rust-std/0001-core-transmutation/maybeuninit_assume_init_ref.rs` | proof harness | passed | - | Reading via assume_init_ref for u32, i64, u8. |
| `MaybeUninit::assume_init_mut` | `core::mem` | `verify-rust-std/0001-core-transmutation/maybeuninit_assume_init_mut.rs` | proof harness | passed | - | Reading via assume_init_mut for u32, i64. |
| `MaybeUninit::new` (structs) | `core::mem` | `verify-rust-std/0001-core-transmutation/maybeuninit_struct.rs` | proof harness | passed | - | MaybeUninit with Point, Triple, Wrapper structs. |
| `MaybeUninit::new` (enums) | `core::mem` | `verify-rust-std/0001-core-transmutation/maybeuninit_init_patterns.rs` | proof harness | passed | - | MaybeUninit with Option, Result, arrays. |
| `from_u32_unchecked` | `core::char::convert` | n/a | proof harness | blocked | `TRANSMUTE_CHAR` | Requires u32->char transmute rule (not in semantics). |
| `from_u32_unchecked` | `core::char` | n/a | proof harness | blocked | `TRANSMUTE_CHAR` | Same blocker as above. |
| `char_try_from_u32` | `core::char::convert` | n/a | proof harness | blocked | `TRANSMUTE_CHAR` | Internally calls from_u32_unchecked. |
| `MaybeUninit<T>::array_assume_init` | `core::mem` | `prove-rs/maybeuninit_array_assume_init.rs` | proof harness | frontier reached | `UNION_EVAL` | Array indexing of MaybeUninit union blocked by #evalUnion. |
| `MaybeUninit<[T; N]>::transpose` | `core::mem` | n/a | proof harness | blocked | `UNION_TRANSMUTE` | Reverse transmute from Union to array blocked. |
| `<[MaybeUninit<T>; N]>::transpose` | `core::mem` | n/a | proof harness | blocked | `UNION_TRANSMUTE` | Same as above. |
| `<[T; N] as IntoIterator>::into_iter` | `core::array::iter` | n/a | proof harness | blocked | `UNION_EVAL` | Array-to-MaybeUninit transmute works but indexing blocked. |
| `BorrowedBuf::unfilled` | `core::io::borrowed_buf` | n/a | proof harness | not started | `UNKNOWN` | Complex buffer management. |
| `BorrowedCursor::reborrow` | `core::io::borrowed_buf` | n/a | proof harness | not started | `UNKNOWN` | Complex buffer management. |
| `str::as_bytes` | `core::str` | n/a | proof harness | blocked | `STRING_DECODE` | Stuck on #decodeConstant for string allocations. |
| `Ipv6Addr::new` | `core::net::ip_addr` | n/a | proof harness | blocked | `ARRAY_TRANSMUTE` | Requires [u16;N] <-> [u8;N] array transmute. |
| `Ipv6Addr::segments` | `core::net::ip_addr` | n/a | proof harness | blocked | `ARRAY_TRANSMUTE` | Same blocker. |
| `align_offset` | `core::ptr` | n/a | proof harness | not started | `UNKNOWN` | Complex pointer alignment. |
| `Alignment::new_unchecked` | `core::ptr::alignment` | n/a | proof harness | blocked | `TRANSMUTE_USIZE` | usize->Alignment transmute not handled. |
| `Alignment::new` | `core::ptr::alignment` | n/a | proof harness | blocked | `INTRINSIC_CTPOP` | Requires ctpop intrinsic (is_power_of_two). |
| `MaybeUninit<T>::copy_from_slice` | `core::mem` | n/a | proof harness | not started | `UNKNOWN` | Slice operations likely complex. |
| `str::as_bytes_mut` | `core::str` | n/a | proof harness | blocked | `STRING_DECODE` | Same as str::as_bytes. |
| `<Filter<I,P> as Iterator>::next_chunk` | `core::iter::adapters` | n/a | proof harness | not started | `UNKNOWN` | Complex iterator adaptor. |
| `<FilterMap<I,F> as Iterator>::next_chunk` | `core::iter::adapters` | n/a | proof harness | not started | `UNKNOWN` | Complex iterator adaptor. |
| `try_from_fn` | `core::array` | n/a | proof harness | not started | `UNKNOWN` | Array construction from closure. |
| `iter_next_chunk` | `core::array` | n/a | proof harness | not started | `UNKNOWN` | Iterator to array. |
| `AsciiChar::from_u8_unchecked` | `core::ascii_char` | n/a | proof harness | blocked | `TRANSMUTE_CHAR` | Likely uses char/ascii transmute. |
| `AsciiChar::from_u8` | `core::ascii_char` | n/a | proof harness | blocked | `TRANSMUTE_CHAR` | Same blocker. |
| `char::as_ascii` | `core::char` | n/a | proof harness | blocked | `TRANSMUTE_CHAR` | Same blocker. |
| `memchr_aligned` | `core::slice::memchr` | n/a | proof harness | not started | `UNKNOWN` | Complex memory search. |
| `<[T]>::align_to_mut` | `core::slice` | n/a | proof harness | not started | `UNKNOWN` | Slice alignment operations. |
| `run_utf8_validation` | `core::str::validations` | n/a | proof harness | not started | `UNKNOWN` | UTF-8 validation loop. |
| `<[T]>::align_to` | `core::slice` | n/a | proof harness | not started | `UNKNOWN` | Slice alignment operations. |
| `is_aligned_to` | `core::const_ptr` | n/a | proof harness | not started | `UNKNOWN` | Pointer alignment check. |
| `is_aligned_to` | `core::mut_ptr` | n/a | proof harness | not started | `UNKNOWN` | Pointer alignment check. |
| `Layout::from_size_align` | `core::alloc::layout` | n/a | proof harness | blocked | `TRANSMUTE_USIZE` | from_size_align_unchecked uses usize->Alignment transmute. |
| `Layout::from_size_align_unchecked` | `core::alloc::layout` | n/a | proof harness | blocked | `TRANSMUTE_USIZE` | usize->Alignment transmute not handled. |
| `make_ascii_lowercase` | `core::str` | n/a | proof harness | not started | `UNKNOWN` | String mutation. |
| `make_ascii_uppercase` | `core::str` | n/a | proof harness | not started | `UNKNOWN` | String mutation. |
| `<char as Step>::forward_checked` | `core::iter::range` | n/a | proof harness | blocked | `TRANSMUTE_CHAR` | Char iteration requires u32->char. |
| `<Chars as Iterator>::next` | `core::str::iter` | n/a | proof harness | not started | `UNKNOWN` | String iterator. |
| `<Chars as DoubleEndedIterator>::next_back` | `core::str::iter` | n/a | proof harness | not started | `UNKNOWN` | String iterator. |
| `char::encode_utf16_raw` | `core::char` | n/a | proof harness | not started | `UNKNOWN` | Char encoding. |
| `<char as Step>::backward_unchecked` | `core::iter::range` | n/a | proof harness | blocked | `TRANSMUTE_CHAR` | Char iteration requires u32->char. |
| `<char as Step>::forward_unchecked` | `core::iter::range` | n/a | proof harness | blocked | `TRANSMUTE_CHAR` | Char iteration requires u32->char. |
| `<[T]>::as_simd_mut` | `core::slice` | n/a | proof harness | not started | `UNKNOWN` | SIMD operations. |
| `<[T]>::as_simd` | `core::slice` | n/a | proof harness | not started | `UNKNOWN` | SIMD operations. |
| `memrchr` | `core::slice::memchr` | n/a | proof harness | not started | `UNKNOWN` | Memory search. |
| `do_count_chars` | `str::count` | n/a | proof harness | not started | `UNKNOWN` | String counting. |

## Blocker Categories

| Blocker Class | Description | Affected Count |
| --- | --- | --- |
| `TRANSMUTE_CHAR` | Missing transmute rule for u32 -> char | 8 |
| `TRANSMUTE_USIZE` | Missing transmute rule for usize -> Alignment (or similar newtype) | 3 |
| `UNION_EVAL` | #evalUnion stuck when accessing MaybeUninit array elements | 2 |
| `UNION_TRANSMUTE` | Reverse transmute from Union representation to target type | 2 |
| `ARRAY_TRANSMUTE` | Transmute between arrays of different-width integers | 2 |
| `STRING_DECODE` | #decodeConstant stuck on string literal allocations | 2 |
| `INTRINSIC_CTPOP` | Missing ctpop intrinsic | 1 |
| `UNKNOWN` | Not yet attempted or requires investigation | 15+ |
