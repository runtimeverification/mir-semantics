# Contract Map: Challenge 0027 `alloc::sync`

## Basis

- Challenge page checked on 2026-04-10: `verify-rust-std` challenge 27
  requires contracts for the public `unsafe` APIs in `alloc::sync`, plus
  safety coverage for the large set of non-public unsafe helpers.
- Local source basis:
  `nightly-2024-11-29-x86_64-unknown-linux-gnu/lib/rustlib/src/rust/library/alloc/src/sync.rs`
- Reuse lessons:
  - `0026-rc` showed that a concrete witness file is useful as a reproducer but
    not sufficient as verification evidence.
  - The `0026-rc` verification-shape split is the preferred pattern here:
    contract-first proof harness plus separate frontier reproducer.
- Arc-specific extra obligation:
  - the proof must also cover the absence of data races.

## Contract Surface

| API | Source anchor | Source safety summary | Likely proof entrypoint | Cluster | First tranche |
| --- | --- | --- | --- | --- | --- |
| `Arc<MaybeUninit<T>, A>::assume_init` | `alloc/src/sync.rs:1164-1199` | Caller must guarantee the inner value is fully initialized before converting to `Arc<T>`. | Prove this body directly. | initialization transition | no |
| `Arc<[MaybeUninit<T>], A>::assume_init` | `alloc/src/sync.rs:1203-1239` | Caller must guarantee every element is fully initialized before converting to `Arc<[T]>`. | Prove this body directly. | initialization transition | no |
| `Arc::from_raw` | `alloc/src/sync.rs:1426-1458` | Raw pointer must come from `Arc::into_raw`, preserve layout compatibility, come from the global allocator, and be turned back into an owning `Arc` only once. | Root proof on `Arc::from_raw_in`; wrapper proof is allocator specialization to `Global`. | raw pointer recovery | wrapper |
| `Arc::increment_strong_count` | `alloc/src/sync.rs:1460-1494` | Pointer must come from `Arc::into_raw`; associated allocation must stay valid with strong count at least 1 for the duration; memory must come from the global allocator. | Root proof on `Arc::increment_strong_count_in`; wrapper proof is allocator specialization to `Global`. | refcount transition | wrapper |
| `Arc::decrement_strong_count` | `alloc/src/sync.rs:1496-1528` | Pointer must come from `Arc::into_raw`; allocation must be valid with strong count at least 1 when called; memory must come from the global allocator. | Root proof on `Arc::decrement_strong_count_in`; wrapper proof is allocator specialization to `Global`. | refcount transition | wrapper |
| `Arc::from_raw_in` | `alloc/src/sync.rs:1662-1809` | Raw pointer must come from `Arc::into_raw`, preserve layout compatibility, come from allocator `A`, and reconstitute ownership exactly once. | Prove this body directly; this is the raw-recovery root for both `Arc::from_raw*` variants. | raw pointer recovery | yes |
| `Arc::increment_strong_count_in` | `alloc/src/sync.rs:1815-1859` | Pointer must come from `Arc::into_raw`; allocation must stay valid with strong count at least 1 for the whole call; memory must come from allocator `A`. | Prove this body directly after `Arc::from_raw_in`, since the implementation rehydrates an `Arc` and clones it. | refcount transition | yes |
| `Arc::decrement_strong_count_in` | `alloc/src/sync.rs:1861-1893` | Pointer must come from `Arc::into_raw`; allocation must be valid with strong count at least 1 when called; memory must come from allocator `A`. | Prove this body directly after `Arc::from_raw_in`, since the implementation is `drop(Arc::from_raw_in(...))`. | refcount transition | yes |
| `Arc::get_mut_unchecked` | `alloc/src/sync.rs:2465-2503` | Other `Arc` or `Weak` aliases must not be dereferenced or actively borrowed during the returned mutable borrow, and all aliases must have identical inner type identity. | Prove this body directly. | aliasing and type identity | no |
| `Arc::downcast_unchecked` | `alloc/src/sync.rs:2643-2674` | Contained value must really be of type `T`; wrong-type downcast is UB. | Prove this body directly. | dynamic type recovery | no |
| `Weak::from_raw` | `alloc/src/sync.rs:2763-2797` | Raw pointer must come from `Weak::into_raw`, still own the represented weak token, and refer to memory from the global allocator; strong count may already be 0. | Root proof on `Weak::from_raw_in`; wrapper proof is allocator specialization to `Global`. | weak raw recovery | wrapper |
| `Weak::from_raw_in` | `alloc/src/sync.rs:2934-2978` | Raw pointer must come from `Weak::into_raw`, still own one weak token, and refer to memory from allocator `A`; strong count may already be 0. | Prove this body directly; this is the weak raw-recovery root for both `Weak::from_raw*` variants. | weak raw recovery | yes |

## Invariant Clusters

1. Raw pointer recovery and refcount transition
   - `Arc::from_raw`, `Arc::from_raw_in`, `Arc::increment_strong_count`,
     `Arc::increment_strong_count_in`, `Arc::decrement_strong_count`,
     `Arc::decrement_strong_count_in`, `Weak::from_raw`, `Weak::from_raw_in`
   - Shared invariants:
     - Pointer/token originates from the matching `into_raw` family.
     - Allocator used for recovery matches the allocation provenance.
     - Recovered ownership token is consumed exactly once.
     - Atomic refcount updates must not introduce a data race.
     - `Arc` strong-count APIs require a live strong owner; `Weak::from_raw*`
       explicitly permits `strong_count == 0`.
2. Initialization transition
   - The two `assume_init` variants.
   - Distinct invariant: all bytes of the stored `MaybeUninit` payload must
     already be initialized.
3. Aliasing and type identity
   - `Arc::get_mut_unchecked`
   - Distinct invariant: no conflicting alias dereference or borrow, and all
     aliases have the exact same type/lifetime.
4. Dynamic type recovery
   - `Arc::downcast_unchecked`
   - Distinct invariant: runtime dynamic type matches the requested `T`.

## Selected First Tranche

### Proof roots

- `Arc::from_raw_in`
- `Arc::increment_strong_count_in`
- `Arc::decrement_strong_count_in`
- `Weak::from_raw_in`

### Immediate wrapper follow-ons

- `Arc::from_raw`
- `Arc::increment_strong_count`
- `Arc::decrement_strong_count`
- `Weak::from_raw`

### Why this is the smallest useful tranche

- It stays inside the raw-pointer/refcount family that reuses the `Rc`
  lessons without copying them blindly.
- Four proof roots cover eight of the twelve public `unsafe` APIs because the
  stable `Global` variants are thin wrappers over the allocator-general `_in`
  bodies.
- `Arc::increment_strong_count_in` and `Arc::decrement_strong_count_in` both
  reduce to `Arc::from_raw_in` plus clone/drop behavior, so the tranche has
  one clear dependency spine instead of four disconnected proofs.
- `Weak::from_raw_in` reuses the same pointer-recovery shape but adds the one
  distinct weak-token rule that `strong_count` may already be zero.
- The remaining four APIs (`assume_init` x2, `get_mut_unchecked`,
  `downcast_unchecked`) require separate initialization, aliasing, or dynamic
  typing invariants and would widen the slice immediately.

## Recommended Proof Order Inside The Tranche

1. `Arc::from_raw_in`
2. `Arc::increment_strong_count_in`
3. `Arc::decrement_strong_count_in`
4. `Weak::from_raw_in`
5. Thin-wrapper specialization checks for the four stable `Global` entrypoints

## Minimal Reproducer Policy

- If a semantic frontier appears, first isolate the smallest challenge-local
  reproducer that still reaches the stuck leaf.
- Keep the verification harness contract-shaped and symbolic over the primitive
  payload value; keep the reproducer separate and concrete.
- Do not widen into `assume_init`, `get_mut_unchecked`, or `downcast_unchecked`
  until the raw-recovery root is either proven or blocked with a precise leaf.

