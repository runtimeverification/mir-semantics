# Success Criteria Coverage: Challenge 0001

This branch-local coverage map is seeded from the upstream challenge page and
the current harness sweep plan.

Status legend:

- `harness defined` means a branch-local proof-shaped entrypoint exists, but
  the branch has not yet classified the resulting frontier.
- `not started` means there is no branch-local harness/spec yet.
- `frontier reached` means a proof run reached a concrete leaf or thunk for
  the named entrypoint.

| Function | Upstream Location | Harness/Spec File | Start Symbol | Kind | Status | Blocker Class | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `transmute_unchecked` | `core::intrinsics` | `kmir/src/tests/integration/data/prove-rs/transmute_unchecked_maybeuninit.rs` | `into_maybeuninit`, `from_maybeuninit` | proof harness | frontier reached | `HASKELL_BACKEND` | First breadth-first seed for the primitive intrinsic path; proof hits a backend runtime error on `FLOAT.int2float`. |
| `transmute` | `core::intrinsics` | `kmir/src/tests/integration/data/prove-rs/transmute_roundtrip.rs` | `bytes_to_u64`, `u64_to_bytes` | proof harness | passed | `MIR_SEMANTICS` | First direct value-reinterpretation seed using roundtrip assertions; proof and expected output both generated. |
| `MaybeUninit<T>::array_assume_init` | `core::mem` | `kmir/src/tests/integration/data/prove-rs/maybeuninit_array_assume_init.rs` | `array_assume_init_u8`, `array_assume_init_u16` | proof harness | frontier reached | `UNKNOWN` | First array-closure seed for the `MaybeUninit` family; compile gate fixed, proof still fails. |
| `MaybeUninit<[T; N]>::transpose` | `core::mem` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `<[MaybeUninit<T>; N]>::transpose` | `core::mem` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `<[T; N] as IntoIterator>::into_iter` | `core::array::iter` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `BorrowedBuf::unfilled` | `core::io::borrowed_buf` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `BorrowedCursor::reborrow` | `core::io::borrowed_buf` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `str::as_bytes` | `core::str` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `from_u32_unchecked` | `core::char::convert` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | First `from_u32_unchecked` location from the upstream list. |
| `char_try_from_u32` | `core::char::convert` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `Ipv6Addr::new` | `core::net::ip_addr` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `Ipv6Addr::segments` | `core::net::ip_addr` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `align_offset` | `core::ptr` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `Alignment::new_unchecked` | `core::ptr::alignment` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `MaybeUninit<T>::copy_from_slice` | `core::mem` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `str::as_bytes_mut` | `core::str` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `<Filter<I,P> as Iterator>::next_chunk` | `core::iter::adapters` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `<FilterMap<I,F> as Iterator>::next_chunk` | `core::iter::adapters` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `try_from_fn` | `core::array` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `iter_next_chunk` | `core::array` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `from_u32_unchecked` | `core::char` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | Second `from_u32_unchecked` location from the upstream list. |
| `AsciiChar::from_u8_unchecked` | `core::ascii_char` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `memchr_aligned` | `core::slice::memchr` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `<[T]>::align_to_mut` | `core::slice` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `run_utf8_validation` | `core::str::validations` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `<[T]>::align_to` | `core::slice` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `is_aligned_to` | `core::const_ptr` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | Const-pointer variant from the upstream list. |
| `is_aligned_to` | `core::mut_ptr` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | Mut-pointer variant from the upstream list. |
| `Alignment::new` | `core::ptr::alignment` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `Layout::from_size_align` | `core::alloc::layout` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `Layout::from_size_align_unchecked` | `core::alloc::layout` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `make_ascii_lowercase` | `core::str` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `make_ascii_uppercase` | `core::str` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `<char as Step>::forward_checked` | `core::iter::range` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `<Chars as Iterator>::next` | `core::str::iter` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `<Chars as DoubleEndedIterator>::next_back` | `core::str::iter` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `char::encode_utf16_raw` | `core::char` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `<char as Step>::backward_unchecked` | `core::iter::range` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `<char as Step>::forward_unchecked` | `core::iter::range` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `AsciiChar::from_u8` | `core::ascii_char` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `char::as_ascii` | `core::char` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `<[T]>::as_simd_mut` | `core::slice` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `<[T]>::as_simd` | `core::slice` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `memrchr` | `core::slice::memchr` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
| `do_count_chars` | `str::count` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local harness yet. |
