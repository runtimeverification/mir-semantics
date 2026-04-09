# Contract Map: Challenge 0026 `alloc::rc`

## Basis

- Challenge page checked on 2026-04-09: `verify-rust-std` challenge 0026 requires contracts for 12 public `unsafe` APIs in `alloc::rc`.
- Local source basis: `nightly-2024-11-29` toolchain from `rust-toolchain.toml`.
- Source file audited: `/home/zhaoji/.rustup/toolchains/nightly-2024-11-29-x86_64-unknown-linux-gnu/lib/rustlib/src/rust/library/alloc/src/rc.rs`

## Contract Surface

| API | Source anchor | Source safety summary | Likely proof entrypoint | Cluster | First tranche |
| --- | --- | --- | --- | --- | --- |
| `Rc<MaybeUninit<T>, A>::assume_init` | `alloc/src/rc.rs:1164-1197` | Caller must guarantee the inner value is fully initialized before converting to `Rc<T>`. | Prove this body directly. | initialization transition | no |
| `Rc<[MaybeUninit<T>], A>::assume_init` | `alloc/src/rc.rs:1201-1237` | Caller must guarantee every element is fully initialized before converting to `Rc<[T]>`. | Prove this body directly. | initialization transition | no |
| `Rc::from_raw` | `alloc/src/rc.rs:1241-1306` | Raw pointer must come from `Rc::into_raw`, preserve layout compatibility, come from the global allocator, and be turned back into an owning `Rc` only once. | Root proof on `Rc::from_raw_in`; wrapper proof is allocator specialization to `Global`. | raw pointer recovery | wrapper |
| `Rc::increment_strong_count` | `alloc/src/rc.rs:1309-1339` | Pointer must come from `Rc::into_raw`; associated allocation must stay valid with strong count at least 1 for the duration; memory must come from the global allocator. | Root proof on `Rc::increment_strong_count_in`; wrapper proof is allocator specialization to `Global`. | refcount transition | wrapper |
| `Rc::decrement_strong_count` | `alloc/src/rc.rs:1342-1373` | Pointer must come from `Rc::into_raw`; allocation must be valid with strong count at least 1 when called; call may release the final `Rc` but must not run after final release; memory must come from the global allocator. | Root proof on `Rc::decrement_strong_count_in`; wrapper proof is allocator specialization to `Global`. | refcount transition | wrapper |
| `Rc::from_raw_in` | `alloc/src/rc.rs:1468-1542` | Raw pointer must come from `Rc::into_raw`, preserve layout compatibility, come from allocator `A`, and reconstitute ownership exactly once. | Prove this body directly; this is the raw-recovery root for both `Rc::from_raw*` variants. | raw pointer recovery | yes |
| `Rc::increment_strong_count_in` | `alloc/src/rc.rs:1605-1644` | Pointer must come from `Rc::into_raw`; allocation must stay valid with strong count at least 1 for the whole call; memory must come from allocator `A`. | Prove this body directly after `Rc::from_raw_in`, since the implementation rehydrates an `Rc` with `ManuallyDrop` and clones it. | refcount transition | yes |
| `Rc::decrement_strong_count_in` | `alloc/src/rc.rs:1647-1681` | Pointer must come from `Rc::into_raw`; allocation must be valid with strong count at least 1 when called; call may release the final `Rc`; memory must come from allocator `A`. | Prove this body directly after `Rc::from_raw_in`, since the implementation is `drop(Rc::from_raw_in(...))`. | refcount transition | yes |
| `Rc::get_mut_unchecked` | `alloc/src/rc.rs:1721-1786` | Other `Rc` or `Weak` aliases must not be dereferenced or actively borrowed during the returned mutable borrow, and all aliases must have exactly the same inner type, including lifetimes. | Prove this body directly. | aliasing and type identity | no |
| `Rc::downcast_unchecked` | `alloc/src/rc.rs:1988-2019` | Contained value must really be of type `T`; wrong-type downcast is UB. | Prove this body directly. | dynamic type recovery | no |
| `Weak::from_raw` | `alloc/src/rc.rs:3049-3095` | Raw pointer must come from `Weak::into_raw`, still own the represented weak token, and refer to memory from the global allocator; strong count may already be 0. | Root proof on `Weak::from_raw_in`; wrapper proof is allocator specialization to `Global`. | weak raw recovery | wrapper |
| `Weak::from_raw_in` | `alloc/src/rc.rs:3222-3278` | Raw pointer must come from `Weak::into_raw`, still own one weak token, and refer to memory from allocator `A`; strong count may already be 0. | Prove this body directly; this is the weak raw-recovery root for both `Weak::from_raw*` variants. | weak raw recovery | yes |

## Invariant Clusters

1. Raw pointer recovery and refcount transition
   - `Rc::from_raw`, `Rc::from_raw_in`, `Rc::increment_strong_count`, `Rc::increment_strong_count_in`, `Rc::decrement_strong_count`, `Rc::decrement_strong_count_in`, `Weak::from_raw`, `Weak::from_raw_in`
   - Shared invariants:
     - Pointer/token originates from the matching `into_raw` family.
     - Allocator used for recovery matches the allocation provenance.
     - Recovered ownership token is consumed exactly once.
     - `Rc` strong-count APIs require a live strong owner; `Weak::from_raw*` explicitly permits `strong_count == 0`.
2. Initialization transition
   - The two `assume_init` variants.
   - Distinct invariant: all bytes of the stored `MaybeUninit` payload must already be initialized.
3. Aliasing and type identity
   - `Rc::get_mut_unchecked`
   - Distinct invariant: no conflicting alias dereference or borrow, and all aliases have the exact same type/lifetime.
4. Dynamic type recovery
   - `Rc::downcast_unchecked`
   - Distinct invariant: runtime dynamic type matches the requested `T`.

## Selected First Tranche

### Proof roots

- `Rc::from_raw_in`
- `Rc::increment_strong_count_in`
- `Rc::decrement_strong_count_in`
- `Weak::from_raw_in`

### Immediate wrapper follow-ons

- `Rc::from_raw`
- `Rc::increment_strong_count`
- `Rc::decrement_strong_count`
- `Weak::from_raw`

### Why this is the smallest useful tranche

- It stays inside the planner-selected raw-pointer/refcount family.
- Four proof roots cover eight of the twelve public `unsafe` APIs because the stable `Global` variants are thin wrappers over the allocator-general `_in` bodies.
- `Rc::increment_strong_count_in` and `Rc::decrement_strong_count_in` both reduce to `Rc::from_raw_in` plus clone/drop behavior, so the tranche has one clear dependency spine instead of four disconnected proofs.
- `Weak::from_raw_in` reuses the same pointer-recovery shape but adds the one distinct weak-token rule that `strong_count` may already be zero.
- The remaining four APIs (`assume_init` x2, `get_mut_unchecked`, `downcast_unchecked`) require separate initialization, aliasing, or dynamic-typing invariants and would widen the slice immediately.

## Recommended Proof Order Inside The Tranche

1. `Rc::from_raw_in`
2. `Rc::increment_strong_count_in`
3. `Rc::decrement_strong_count_in`
4. `Weak::from_raw_in`
5. Thin-wrapper specialization checks for the four stable `Global` entrypoints

## Soft Risks Outside The Tranche

- The challenge page explicitly notes that `assume_init` may be hard to express with the current type system, so keeping both `assume_init` APIs out of tranche 1 avoids an avoidable blocker.
- `Rc::get_mut_unchecked` will likely need stronger alias/lifetime modeling than the raw-pointer tranche.
