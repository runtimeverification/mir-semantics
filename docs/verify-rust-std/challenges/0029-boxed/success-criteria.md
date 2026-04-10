# Challenge 0029 Success Criteria

Branch evidence is recorded against `verify-rust-std/reexec-0029-boxed` as of 2026-04-10.
The rows below are the auditable success surface extracted from
`https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0029-boxed.md`.

Statuses used in this branch:

- `not started`: no challenge-local harness or reproducer yet
- `harness defined`: verification-shaped entrypoint added but no proof evidence recorded yet
- `frontier reached`: proof run executed and stopped at a concrete frontier
- `passed`: proof run closed for the current primitive instance

| Function | Upstream Location | Harness/Spec File | Start Symbol | Kind | Status | Blocker Class | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `Box<mem::MaybeUninit<T>, A>::assume_init` | `alloc::boxed` | `kmir/src/tests/integration/data/verify-rust-std/0029-boxed/box-assume-init.rs` | `verify_box_assume_init_u32` | proof harness | harness defined | UNKNOWN | Primitive instantiation uses `u32` and constructs `Box<MaybeUninit<u32>>` from raw allocation to hit `assume_init` directly. |
| `Box<[mem::MaybeUninit<T>], A>::assume_init` | `alloc::boxed` | `kmir/src/tests/integration/data/verify-rust-std/0029-boxed/box-slice-assume-init.rs` | `verify_box_slice_assume_init_u32_pair` | proof harness | harness defined | UNKNOWN | First slice proof fixes the length at `2` and uses `u32` elements. |
| `Box<T>::from_raw` | `alloc::boxed` | `kmir/src/tests/integration/data/verify-rust-std/0029-boxed/box-from-raw.rs` | `verify_box_from_raw` | proof harness | frontier reached | MIR_SEMANTICS | Narrow proof run reaches the same leaf as `from_raw_in`: `thunk(#cast(Integer(4,64,false), castKindTransmute, ...))` in `std::alloc::Layout::new::<u32>` before the recovered box is observed. |
| `Box<T>::from_non_null` | `alloc::boxed` | `kmir/src/tests/integration/data/verify-rust-std/0029-boxed/box-from-non-null.rs` | `verify_box_from_non_null` | proof harness | harness defined | UNKNOWN | First tranche uses the global allocator plus an explicit `NonNull<u32>` witness. |
| `Box<T, A>::from_raw_in` | `alloc::boxed` | `kmir/src/tests/integration/data/verify-rust-std/0029-boxed/box-from-raw-in.rs` | `verify_box_from_raw_in` | proof harness | frontier reached | MIR_SEMANTICS | First proof run on the allocator-general root fails at `thunk(#cast(Integer(4,64,false), castKindTransmute, ...))` in `std::alloc::Layout::new::<u32>`, before the recovered box value is observed. |
| `Box<T, A>::from_non_null_in` | `alloc::boxed` | `kmir/src/tests/integration/data/verify-rust-std/0029-boxed/box-from-non-null-in.rs` | `verify_box_from_non_null_in` | proof harness | harness defined | UNKNOWN | Allocator-general `NonNull` root paired with the `from_raw_in` tranche. |
| `<dyn Error>::downcast_unchecked` | `alloc::boxed::convert` |  |  | contract row | not started | UNKNOWN | Dynamic-type proof tranche is separate from the raw ownership tranche. |
| `<dyn Error + Send>::downcast_unchecked` | `alloc::boxed::convert` |  |  | contract row | not started | UNKNOWN | Same dynamic-type tranche as `<dyn Error>::downcast_unchecked`. |
| `<dyn Error + Send + Sync>::downcast_unchecked` | `alloc::boxed::convert` |  |  | contract row | not started | UNKNOWN | Same dynamic-type tranche as the other `downcast_unchecked` rows. |
| `Box<T, A>::new_in` | `alloc::boxed` |  |  | contract row | not started | UNKNOWN | Root allocation-constructor tranche; likely shares allocator frontier with `from_raw_in`. |
| `Box<T, A>::try_new_in` | `alloc::boxed` |  |  | contract row | not started | UNKNOWN | Same allocation-constructor tranche as `new_in`. |
| `Box<T, A>::try_new_uninit_in` | `alloc::boxed` |  |  | contract row | not started | UNKNOWN | Constructor tranche feeding `assume_init`. |
| `Box<T, A>::try_new_zeroed_in` | `alloc::boxed` |  |  | contract row | not started | UNKNOWN | Constructor tranche feeding `assume_init`. |
| `Box<T, A>::into_boxed_slice` | `alloc::boxed` |  |  | contract row | not started | UNKNOWN | Conversion tranche after raw ownership roots. |
| `Box<[T]>::new_uninit_slice` | `alloc::boxed` |  |  | contract row | not started | UNKNOWN | Slice-constructor tranche; current direct root is the corresponding `assume_init` row. |
| `Box<[T]>::new_zeroed_slice` | `alloc::boxed` |  |  | contract row | not started | UNKNOWN | Same slice-constructor tranche. |
| `Box<[T]>::try_new_uninit_slice` | `alloc::boxed` |  |  | contract row | not started | UNKNOWN | Same slice-constructor tranche. |
| `Box<[T]>::try_new_zeroed_slice` | `alloc::boxed` |  |  | contract row | not started | UNKNOWN | Same slice-constructor tranche. |
| `Box<[T]>::into_array` | `alloc::boxed` |  |  | contract row | not started | UNKNOWN | Conversion tranche for boxed slices and arrays. |
| `Box<T, A>::new_uninit_slice_in` | `alloc::boxed` |  |  | contract row | not started | UNKNOWN | Allocator-general slice-constructor tranche. |
| `Box<T, A>::new_zeroed_slice_in` | `alloc::boxed` |  |  | contract row | not started | UNKNOWN | Allocator-general slice-constructor tranche. |
| `Box<T, A>::try_new_uninit_slice_in` | `alloc::boxed` |  |  | contract row | not started | UNKNOWN | Allocator-general slice-constructor tranche. |
| `Box<T, A>::try_new_zeroed_slice_in` | `alloc::boxed` |  |  | contract row | not started | UNKNOWN | Allocator-general slice-constructor tranche. |
| `Box<mem::MaybeUninit<T>, A>::write` | `alloc::boxed` |  |  | contract row | not started | UNKNOWN | Follows the same initialization-conversion tranche as scalar `assume_init`. |
| `Box<T>::into_non_null` | `alloc::boxed` |  |  | contract row | not started | UNKNOWN | Outgoing raw ownership tranche; pairs with `from_non_null`. |
| `Box<T, A>::into_raw_with_allocator` | `alloc::boxed` |  |  | contract row | not started | UNKNOWN | Allocator-general outgoing raw ownership root. |
| `Box<T, A>::into_non_null_with_allocator` | `alloc::boxed` |  |  | contract row | not started | UNKNOWN | Allocator-general outgoing `NonNull` root. |
| `Box<T, A>::into_unique` | `alloc::boxed` |  |  | contract row | not started | UNKNOWN | Unique-pointer conversion tranche. |
| `Box<T, A>::leak` | `alloc::boxed` |  |  | contract row | not started | UNKNOWN | Borrow/lifetime tranche. |
| `Box<T, A>::into_pin` | `alloc::boxed` |  |  | contract row | not started | UNKNOWN | Pinning conversion tranche. |
| `<Box<T, A> as Drop>::drop` | `alloc::boxed` |  |  | contract row | not started | UNKNOWN | Destructor tranche; depends on allocation and ownership roots. |
| `<Box<T> as Default>::default` | `alloc::boxed` |  |  | contract row | not started | UNKNOWN | Constructor tranche. |
| `<Box<str> as Default>::default` | `alloc::boxed` |  |  | contract row | not started | UNKNOWN | String conversion / constructor tranche. |
| `<Box<T, A> as Clone>::clone` | `alloc::boxed` |  |  | contract row | not started | UNKNOWN | Clone / allocation tranche. |
| `<Box<str> as Clone>::clone` | `alloc::boxed` |  |  | contract row | not started | UNKNOWN | String clone tranche. |
| `<Box<[T]> as BoxFromSlice<T>>::from_slice` | `alloc::boxed::convert` |  |  | contract row | not started | UNKNOWN | Slice conversion tranche in `boxed::convert`. |
| `<Box<str> as From<&str>>::from` | `alloc::boxed::convert` |  |  | contract row | not started | UNKNOWN | String conversion tranche in `boxed::convert`. |
| `<Box<[u8], A> as From<Box<str, A>>>::from` | `alloc::boxed::convert` |  |  | contract row | not started | UNKNOWN | In-place representation change tranche. |
| `<Box<[T; N]> as TryFrom<Box<[T]>>>::try_from` | `alloc::boxed::convert` |  |  | contract row | not started | UNKNOWN | Slice-to-array conversion tranche. |
| `<Box<[T; N]> as TryFrom<Box<T>>>::try_from` | `alloc::boxed::convert` |  |  | contract row | not started | UNKNOWN | Box-to-array conversion tranche. |
| `Box<dyn Any, A>::downcast` | `alloc::boxed::convert` |  |  | contract row | not started | UNKNOWN | Dynamic-type proof tranche. |
| `Box<dyn Any + Send, A>::downcast` | `alloc::boxed::convert` |  |  | contract row | not started | UNKNOWN | Dynamic-type proof tranche. |
| `Box<dyn Any + Send + Sync, A>::downcast` | `alloc::boxed::convert` |  |  | contract row | not started | UNKNOWN | Dynamic-type proof tranche. |
| `<dyn Error>::downcast` | `alloc::boxed::convert` |  |  | contract row | not started | UNKNOWN | Dynamic-type proof tranche. |
| `<dyn Error + Send>::downcast` | `alloc::boxed::convert` |  |  | contract row | not started | UNKNOWN | Dynamic-type proof tranche. |
| `<dyn Error + Send + Sync>::downcast` | `alloc::boxed::convert` |  |  | contract row | not started | UNKNOWN | Dynamic-type proof tranche. |
| `<ThinBox<T> as Deref>::deref` | `alloc::boxed::thin` |  |  | contract row | not started | UNKNOWN | ThinBox tranche is separate and likely requires metadata/header reasoning. |
| `<ThinBox<T> as DerefMut>::deref_mut` | `alloc::boxed::thin` |  |  | contract row | not started | UNKNOWN | ThinBox metadata/header tranche. |
| `<ThinBox<T> as Drop>::drop` | `alloc::boxed::thin` |  |  | contract row | not started | UNKNOWN | ThinBox drop tranche. |
| `ThinBox<T>::meta` | `alloc::boxed::thin` |  |  | contract row | not started | UNKNOWN | ThinBox metadata tranche. |
| `ThinBox<T>::with_header` | `alloc::boxed::thin` |  |  | contract row | not started | UNKNOWN | ThinBox header-access tranche. |
| `WithHeader<H>::new` | `alloc::boxed::thin` |  |  | contract row | not started | UNKNOWN | ThinBox allocation/layout tranche. |
| `WithHeader<H>::try_new` | `alloc::boxed::thin` |  |  | contract row | not started | UNKNOWN | ThinBox allocation/layout tranche. |
| `WithHeader<H>::new_unsize_zst` | `alloc::boxed::thin` |  |  | contract row | not started | UNKNOWN | ThinBox unsizing/ZST tranche. |
| `WithHeader<H>::header` | `alloc::boxed::thin` |  |  | contract row | not started | UNKNOWN | ThinBox header-access tranche. |
