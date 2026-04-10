# Challenge 0026 Success Criteria

Branch evidence is recorded against `verify-rust-std/reexec-0026-rc` as of 2026-04-10.
The public `unsafe` APIs below are the auditable success surface derived from
`https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0026-rc.md`.

The challenge page also lists a large set of non-public unsafe functions.
Rather than repeat that long internal list here, this branch summarizes those
functions by invariant cluster in `docs/verify-rust-std/challenges/0026-rc/contract-map.md`
so the audit trail stays compact without losing traceability.

| Function | Location | Status | Specification | Notes |
| --- | --- | --- | --- | --- |
| `Rc<mem::MaybeUninit<T>,A>::assume_init` | `alloc::rc` | Not started | Caller must prove the inner value is fully initialized before converting to `Rc<T>`. | The challenge page explicitly calls out that this may be hard to express in the current type system. |
| `Rc<[mem::MaybeUninit<T>],A>::assume_init` | `alloc::rc` | Not started | Caller must prove every element is fully initialized before converting to `Rc<[T]>`. | Same initialization-transition burden as the scalar `assume_init` variant. |
| `Rc<T:?Sized>::from_raw` | `alloc::rc` | Pending wrapper follow-on | Thin `Global` specialization of `Rc<T:?Sized,A:Allocator>::from_raw_in`. | Wrapper coverage depends on the allocator-general root being discharged first. |
| `Rc<T:?Sized>::increment_strong_count` | `alloc::rc` | Pending wrapper follow-on | Thin `Global` specialization of `Rc<T:?Sized,A:Allocator>::increment_strong_count_in`. | Same wrapper relationship as `from_raw`. |
| `Rc<T:?Sized>::decrement_strong_count` | `alloc::rc` | Pending wrapper follow-on | Thin `Global` specialization of `Rc<T:?Sized,A:Allocator>::decrement_strong_count_in`. | Same wrapper relationship as `from_raw`. |
| `Rc<T:?Sized,A:Allocator>::from_raw_in` | `alloc::rc` | Verification-shaped proof harness added; frontier moved once and is still recorded | Raw pointer must come from `Rc::into_raw`, allocator provenance must match, and ownership must be recovered exactly once. | Symbolic proof harness: `kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-from-raw-in.rs`. Minimal frontier reproducer: `kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-new-in-frontier-fail.rs` (minimized to `let _ = Rc::new_in(7u32, System);`). Broader frontier reproducer: `kmir/src/tests/integration/data/verify-rust-std/0026-rc/rc-from-raw-in-frontier-fail.rs`. A small transmute fix moved the frontier past `CastKind::Transmute`; both proof paths now stop at `#setUpCalleeData(... symbol("malloc"), body: noBody ...)`. |
| `Rc<T:?Sized,A:Allocator>::increment_strong_count_in` | `alloc::rc` | Pending root proof | Pointer must come from `Rc::into_raw` and remain valid with strong count at least 1 for the duration of the call. | Contract-map root after `Rc::from_raw_in` is discharged. |
| `Rc<T:?Sized,A:Allocator>::decrement_strong_count_in` | `alloc::rc` | Pending root proof | Pointer must come from `Rc::into_raw` and remain valid with strong count at least 1 when called. | Contract-map root after `Rc::from_raw_in` is discharged. |
| `Rc<T:?Sized,A:Allocator>::get_mut_unchecked` | `alloc::rc` | Not started | Other aliases must not be dereferenced or actively borrowed during the mutable borrow, and all aliases must have identical inner type identity. | Separate aliasing and lifetime reasoning from the raw-pointer tranche. |
| `Rc<dyn Any,A:Allocator>::downcast_unchecked` | `alloc::rc` | Not started | The stored value must really be of the requested dynamic type. | Separate dynamic-type reasoning from the raw-pointer tranche. |
| `Weak<T:?Sized>::from_raw` | `alloc::rc` | Pending wrapper follow-on | Thin `Global` specialization of `Weak<T:?Sized,A:Allocator>::from_raw_in`. | Wrapper coverage depends on the allocator-general weak root. |
| `Weak<T:?Sized,A:Allocator>::from_raw_in` | `alloc::rc` | Not started | Raw pointer must come from `Weak::into_raw`, retain one weak token, and match allocator provenance. | Strong count may already be zero; this is the weak-token recovery root. |
