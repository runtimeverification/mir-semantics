## Summary

`test_process_close_account_multisig` reaches a stuck leaf while closing an account through
`delete_account -> AccountInfo::assign -> std::ptr::write_volatile`.

The observed stuck family writes a `[u8; 32]` payload through a cast from `*const Pubkey` to
`*mut [u8; 32]`. This is the shape used by `solana_account_info::AccountInfo::assign`.

## Source Proof

- proof target: `test_process_close_account_multisig`
- source run: `proof-unknown-ae54c481`
- source node: `132`
- known out-of-scope case: issue #181 uninitialized multisig OOB is not this blocker

## Minimal Reproducer

- file: `kmir/src/tests/integration/data/prove-rs/write_volatile_pubkey_array.rs`
- start symbol: `repro`
- failing baseline: `FAILED`, `nodes=3`, `pending=0`, `failing=1`, `stuck=1`
- current regression status: `PASSED`, `nodes=3`, `pending=0`, `failing=0`, `stuck=0`, `terminal=2`

## Leaf Shape

The failing leaf is both `failing` and `stuck` at node `132`.

The head of the stuck state is:

```text
#traverseProjection(... projectionElemSingletonArray projectionElemField(fieldIdx(0), ...)
 projectionElemConstantIndex(...))
~> #derefTruncate(staticSize(32), .ProjectionElems)
~> #writeProjection(Range(ListItem(Integer(0, 8, false)) ...))
```

This suggests the semantics gets as far as a projected writeback into a wrapped `[u8; 32]`
representation, but cannot normalize or complete the final projection/write step.

The standalone reproducer reached the same projection family before the fix:

```text
#traverseProjection(
  ...,
  Aggregate(variantIdx(0), ListItem(Range(...))),
  projectionElemSingletonArray projectionElemField(fieldIdx(0), ty(64))
  projectionElemConstantIndex(... offset: 0, minLength: 0, fromEnd: false),
  .Contexts
)
~> #derefTruncate(staticSize(32), .ProjectionElems)
~> #writeProjection(Range(...))
```

## Rust Behavior

`solana_account_info::AccountInfo::assign` uses:

```rust
std::ptr::write_volatile(
    self.owner as *const Pubkey as *mut [u8; 32],
    new_owner.to_bytes(),
)
```

`Pubkey` is represented as a tuple struct over `[u8; 32]`, so the write path naturally introduces
field and singleton-array projections around the byte array payload.

## Hypothesis

The blocker is in `mir-semantics` projection normalization or projected writeback for
`write_volatile(*mut [u8; 32], ...)`, not in the multisig spec itself.

## Plan

1. Add a minimal `prove-rs` reproducer that performs the same `AccountInfo::assign`-style cast and
   `write_volatile`.
2. Confirm it fails in the same stuck family.
3. Repair the relevant projection/writeback semantics.
4. Re-run the scoped reproducer and then the full `test_process_close_account_multisig` proof.
