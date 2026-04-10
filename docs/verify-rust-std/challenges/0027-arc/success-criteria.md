# Challenge 0027 Success Criteria

Branch evidence is recorded against `verify-rust-std/reexec-0027-arc` as of
2026-04-10.

The public `unsafe` APIs below are the first auditable success surface derived
from `https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0027-arc.md`.

The challenge page also lists a large set of non-public unsafe functions.
That list is expected to be summarized later in a contract map, but the
initial workspace is intentionally narrowed to the public surface and the
first proof/reproducer split.

| Function | Location | Status | Specification | Notes |
| --- | --- | --- | --- | --- |
| `Arc<T, A>::assume_init` | `alloc::sync` | Not started | Caller must prove the inner value is fully initialized before converting to `Arc<T>`. | The challenge page explicitly warns this may be difficult to express with the current type system. |
| `Arc<[MaybeUninit<T>], A>::assume_init` | `alloc::sync` | Not started | Caller must prove every element is fully initialized before converting to `Arc<[T]>`. | Same initialization-transition burden as the scalar `assume_init` variant. |
| `Arc<T>::from_raw` | `alloc::sync` | Pending wrapper follow-on | Thin `Global` specialization of `Arc<T, A>::from_raw_in`. | Wrapper coverage depends on the allocator-general root being discharged first. |
| `Arc<T>::increment_strong_count` | `alloc::sync` | Pending wrapper follow-on | Thin `Global` specialization of `Arc<T, A>::increment_strong_count_in`. | Same wrapper relationship as `from_raw`. |
| `Arc<T>::decrement_strong_count` | `alloc::sync` | Pending wrapper follow-on | Thin `Global` specialization of `Arc<T, A>::decrement_strong_count_in`. | Same wrapper relationship as `from_raw`. |
| `Arc<T, A>::from_raw_in` | `alloc::sync` | Proof harness added; frontier reproducer split recorded | Raw pointer must come from `Arc::into_raw`, allocator provenance must match, and ownership must be recovered exactly once. | Symbolic proof harness: `kmir/src/tests/integration/data/verify-rust-std/0027-arc/arc-from-raw-in.rs`. Concrete frontier reproducer: `kmir/src/tests/integration/data/verify-rust-std/0027-arc/arc-from-raw-in-frontier-fail.rs` (smaller and more concrete than the symbolic harness because it fixes the payload and uses `main`). The latest validation moved both proof paths to leaf `3`, where `#setUpCalleeData(monoItemFn(... name: symbol("malloc"), body: noBody), ...)` replaces the old `castKindTransmute` frontier. |
| `Arc<T, A>::increment_strong_count_in` | `alloc::sync` | Pending root proof | Pointer must come from `Arc::into_raw` and remain valid with strong count at least 1 for the duration of the call. | Wrapper follow-on after `Arc::from_raw_in`. |
| `Arc<T, A>::decrement_strong_count_in` | `alloc::sync` | Pending root proof | Pointer must come from `Arc::into_raw` and remain valid with strong count at least 1 when called. | Wrapper follow-on after `Arc::from_raw_in`. |
| `Arc<T>::get_mut_unchecked` | `alloc::sync` | Not started | Other aliases must not be dereferenced or actively borrowed during the mutable borrow, and all aliases must have identical inner type identity. | Separate aliasing and lifetime reasoning from the raw-pointer tranche. |
| `Arc<dyn Any>::downcast_unchecked` | `alloc::sync` | Not started | The stored value must really be of the requested dynamic type. | Separate dynamic-type reasoning from the raw-pointer tranche. |
| `Weak<T>::from_raw` | `alloc::sync` | Pending wrapper follow-on | Thin `Global` specialization of `Weak<T, A>::from_raw_in`. | Wrapper coverage depends on the allocator-general weak root. |
| `Weak<T, A>::from_raw_in` | `alloc::sync` | Not started | Raw pointer must come from `Weak::into_raw`, retain one weak token, and match allocator provenance. | Strong count may already be zero; this is the weak-token recovery root. |

## Tranche Note

- The first execution tranche is intentionally centered on
  `Arc<T, A>::from_raw_in` and the refcount recovery spine it enables.
- The `assume_init` and dynamic-type rows stay out of the first tranche unless
  the proof frontier forces a narrow dependency update later.
