# Success Criteria Map: Challenge 0027

This table maps the published Challenge 27 requirements from
`verify-rust-std/doc/src/challenges/0027-arc.md` to branch-local planning
artifacts and the eventual proof evidence they should point to.

The public success surface is the auditable minimum for this branch. The
larger set of non-public unsafe helpers is summarized separately in
`contract-map.md` so the audit trail stays readable.

Status vocabulary:

- `Planned first target`: selected as the first proof root for the branch.
- `Pending root proof`: depends on `Arc::from_raw_in` landing first.
- `Pending wrapper follow-on`: thin specialization that should come after the
  allocator-general root proof.
- `Not started`: no branch-local proof target selected yet.

| Function | Location | Status | Specification | Notes |
| --- | --- | --- | --- | --- |
| `Arc<mem::MaybeUninit<T>,A>::assume_init` | `alloc::sync` | Not started | Caller must prove the inner value is fully initialized before converting to `Arc<T>`. | Initialization-transition root; keep out of the first raw-pointer tranche unless it becomes the only blocker-free follow-on. |
| `Arc<[mem::MaybeUninit<T>],A>::assume_init` | `alloc::sync` | Not started | Caller must prove every element is fully initialized before converting to `Arc<[T]>`. | Same initialization-transition burden as the scalar `assume_init` variant. |
| `Arc<T:?Sized>::from_raw` | `alloc::sync` | Pending wrapper follow-on | Thin `Global` specialization of `Arc<T:?Sized,A:Allocator>::from_raw_in`. | Wrapper coverage depends on the allocator-general root being discharged first. |
| `Arc<T:?Sized>::increment_strong_count` | `alloc::sync` | Pending wrapper follow-on | Thin `Global` specialization of `Arc<T:?Sized,A:Allocator>::increment_strong_count_in`. | Same wrapper relationship as `from_raw`. |
| `Arc<T:?Sized>::decrement_strong_count` | `alloc::sync` | Pending wrapper follow-on | Thin `Global` specialization of `Arc<T:?Sized,A:Allocator>::decrement_strong_count_in`. | Same wrapper relationship as `from_raw`. |
| `Arc<T:?Sized,A:Allocator>::from_raw_in` | `alloc::sync` | Planned first target | Raw pointer must come from `Arc::into_raw`, preserve layout compatibility, come from allocator `A`, and reconstitute ownership exactly once. | Highest-leverage root proof target; it unlocks the three refcount follow-ons and the `Global` wrapper layer. |
| `Arc<T:?Sized,A:Allocator>::increment_strong_count_in` | `alloc::sync` | Pending root proof | Pointer must come from `Arc::into_raw`; allocation must stay valid with strong count at least 1 for the duration; memory must come from allocator `A`. | Reuses the raw-recovery spine after `Arc::from_raw_in`. |
| `Arc<T:?Sized,A:Allocator>::decrement_strong_count_in` | `alloc::sync` | Pending root proof | Pointer must come from `Arc::into_raw`; allocation must be valid with strong count at least 1 when called; memory must come from allocator `A`. | Reuses the raw-recovery spine after `Arc::from_raw_in`. |
| `Arc<T:?Sized>::get_mut_unchecked` | `alloc::sync` | Not started | Other `Arc` or `Weak` aliases must not be dereferenced or actively borrowed during the returned mutable borrow, and all aliases must have exactly the same inner type. | Separate aliasing and type-identity reasoning from the raw-pointer tranche. |
| `Arc<dyn Any,A:Allocator>::downcast_unchecked` | `alloc::sync` | Not started | The stored value must really be of the requested dynamic type. | Separate dynamic-type reasoning from the raw-pointer tranche. |
| `Weak<T:?Sized>::from_raw` | `alloc::sync` | Pending wrapper follow-on | Thin `Global` specialization of `Weak<T:?Sized,A:Allocator>::from_raw_in`. | Wrapper coverage depends on the allocator-general weak root. |
| `Weak<T:?Sized,A:Allocator>::from_raw_in` | `alloc::sync` | Planned partner target | Raw pointer must come from `Weak::into_raw`, retain one weak token, and match allocator provenance. | Pair this with `Arc::from_raw_in` after the raw-recovery root is stable. |

