# Workpad: 0001-core-transmutation

Date: 2026-04-11
Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0001-core-transmutation`

## Summary

- Reproduced both existing failed proofs and inspected their failing frontiers.
- Added four new harnesses for uncovered upstream functions.
- Fixed the existing `borrowed_buf_unfilled.rs` harness compile bug (`BorrowedBuf::unfilled` needed a mutable receiver).
- Proof results from this round:
  - Existing failures still failing: `is_aligned_to_const.rs`, `layout_from_size_align.rs`
  - Existing compile error now passing: `borrowed_buf_unfilled.rs`
  - New harnesses passing: `borrowed_cursor_reborrow.rs`
  - New harnesses failing: `maybeuninit_copy_from_slice.rs`, `try_from_fn.rs`, `align_offset.rs`

## Coverage Snapshot After This Round

- Harness count: `38` total
- Passing harnesses: `33`
- Failing harnesses: `5`
- Compile errors: `0`
- Upstream passing coverage: `16/47`

Coverage movement:

- Started at `14/47`
- `BorrowedBuf::unfilled` now passes after the harness fix: `15/47`
- `BorrowedCursor::reborrow` now has a passing harness: `16/47`

## Phase 1: Existing Failed Proofs

### 1. `is_aligned_to_const.rs`

Repro command:

```bash
timeout 180 uv --project kmir run -- kmir prove \
  kmir/src/tests/integration/data/verify-rust-std/0001-core-transmutation/is_aligned_to_const.rs \
  --verbose --terminate-on-thunk \
  --proof-dir /tmp/kmir-0001-gen-aligned --reload --fail-fast
```

Observed result:

- `ProofStatus.FAILED`
- `failing: 1`
- no stuck nodes

Frontier:

- Leaf is inside `std::ptr::const_ptr::<impl *const u64>::is_aligned`
- Source span reported by KMIR: `core/src/ptr/const_ptr.rs:1466`
- The leaf is a thunked cast:

```text
thunk ( #cast ( PtrLocal(...) , castKindTransmute , ty(35) , ty(27) ) )
```

Interpretation:

- This proof dies on the pointer-address conversion performed by `is_aligned` / `is_aligned_to`.
- That matches the known pointer-to-`usize` transmute gap more than a harness bug.
- The second assertion (`ptr.is_aligned_to(1)`) is not reached; the first `ptr.is_aligned()` already hits the blocker.

Likely blocker class:

- Pointer address cast / `TRANSMUTE_USIZE`-adjacent support

### 2. `layout_from_size_align.rs`

Repro command:

```bash
timeout 180 uv --project kmir run -- kmir prove \
  kmir/src/tests/integration/data/verify-rust-std/0001-core-transmutation/layout_from_size_align.rs \
  --verbose --terminate-on-thunk \
  --proof-dir /tmp/kmir-0001-gen-layout --reload --fail-fast
```

Observed result:

- `ProofStatus.FAILED`
- `failing: 1`
- `stuck: 1`

Frontier:

- Leaf is a stuck call setup:

```text
#setUpCalleeData ( monoItemFn(... Layout::is_size_align_valid ..., body: noBody) ...)
```

- Source span reported by KMIR: `core/src/alloc/layout.rs:70`

Interpretation:

- The proof does not fail because of the `mem::transmute(align)` itself.
- It gets stuck earlier because the helper `Layout::is_size_align_valid` is referenced with `body: noBody`.
- This looks like a missing-body / SMIR exposure issue, not a postcondition mismatch in the harness.

Likely blocker class:

- Missing callee body for const helper `Layout::is_size_align_valid`

## Phase 2: New Harnesses Added

Files added:

- `kmir/src/tests/integration/data/verify-rust-std/0001-core-transmutation/borrowed_cursor_reborrow.rs`
- `kmir/src/tests/integration/data/verify-rust-std/0001-core-transmutation/maybeuninit_copy_from_slice.rs`
- `kmir/src/tests/integration/data/verify-rust-std/0001-core-transmutation/try_from_fn.rs`
- `kmir/src/tests/integration/data/verify-rust-std/0001-core-transmutation/align_offset.rs`

Existing file fixed:

- `kmir/src/tests/integration/data/verify-rust-std/0001-core-transmutation/borrowed_buf_unfilled.rs`

## Phase 3: Proof Results For New Harnesses

### PASS: `borrowed_cursor_reborrow.rs`

- Result: `ProofStatus.PASSED`
- Function covered: `BorrowedCursor::reborrow`

Notes:

- This path is reachable with current semantics.
- The harness only reborrows and checks `capacity()` / `written()`, which is enough to hit the transmute-based lifetime shrinking inside `BorrowedCursor::reborrow`.

### FAIL: `maybeuninit_copy_from_slice.rs`

- Result: `ProofStatus.FAILED`
- Function targeted: `MaybeUninit<T>::copy_from_slice`

Frontier:

- Leaf is inside `std::mem::MaybeUninit::<u16>::copy_from_slice`
- Source span reported by KMIR: `core/src/mem/maybe_uninit.rs:1073`
- The failing leaf is a thunked reference cast:

```text
thunk ( #cast ( Reference(...) , castKindTransmute , ty(44) , ty(40) ) )
```

Interpretation:

- This matches the std implementation pattern where `&[T]` is transmuted into `&[MaybeUninit<T>]` before copying.
- That cast is the immediate blocker, not the element copy itself.

Likely blocker class:

- Slice-reference transmute support for `&[T] -> &[MaybeUninit<T>]`

### FAIL: `try_from_fn.rs`

- Result: `ProofStatus.FAILED`
- Function targeted: `try_from_fn`

Harness iterations tried:

1. Inline closure
2. Explicit `fn` pointer (`let cb: fn(usize) -> Option<u8> = build_value;`)

Frontiers:

- Closure version failed on a thunked zero-sized callback constant before entering the array machinery.
- Function-pointer version still failed, but the leaf moved to:

```text
thunk ( #cast ( FunPtr(...) , castKindPointerCoercion(pointerCoercionReifyFnPointer), ... ) )
```

- Source span reported by KMIR after the second attempt: local harness `try_from_fn.rs:13`

Interpretation:

- This is not yet blocked on `MaybeUninit::array_assume_init`.
- The proof dies earlier on function-item / function-pointer reification.
- Changing closure shape does not avoid the current runtime gap.

Likely blocker class:

- Function pointer reification / pointer coercion support

### FAIL: `align_offset.rs`

- Result: `ProofStatus.FAILED`
- Function targeted: `align_offset`

Frontier:

- Leaf is inside `std::ptr::align_offset::<u32>`
- Source span reported by KMIR: `core/src/ptr/mod.rs:1917`
- The failing leaf is a thunked cast:

```text
thunk ( #cast ( PtrLocal(...) , castKindTransmute , ty(30) , ty(22) ) )
```

Interpretation:

- This aligns with the implementation line `let addr: usize = p.addr();`.
- So this is another pointer-to-address cast blocker, closely related to the `is_aligned_to_const` failure.

Likely blocker class:

- Pointer address cast / `TRANSMUTE_USIZE`-adjacent support

## Existing Harness Fix: `borrowed_buf_unfilled.rs`

Change made:

- `let bb = BorrowedBuf::from(...)` -> `let mut bb = BorrowedBuf::from(...)`

Result:

- Now compiles and proves successfully
- Function covered: `BorrowedBuf::unfilled`

Interpretation:

- This was a harness bug, not a semantic blocker.

## Consolidated Blockers Identified This Round

1. Pointer-to-`usize` / address-cast support
   - `is_aligned_to_const.rs`
   - `align_offset.rs`

2. Missing callee body in SMIR / call setup
   - `layout_from_size_align.rs`

3. Slice-reference transmute support
   - `maybeuninit_copy_from_slice.rs`

4. Function-item / function-pointer reification support
   - `try_from_fn.rs`

## Suggested Next Steps

1. Prioritize the pointer-address cast blocker.
   - It should unlock at least `is_aligned_to_const` and `align_offset`.

2. Investigate why `Layout::is_size_align_valid` appears as `noBody`.
   - If this is a SMIR/toolchain visibility issue, fixing it may unlock `Layout::from_size_align` without semantic changes.

3. Add support for the slice transmute used by `MaybeUninit::write_copy_of_slice`.
   - That should help `MaybeUninit<T>::copy_from_slice` and related APIs.

4. Investigate function-pointer reification in MIR/KMIR.
   - `try_from_fn` is blocked before the array initialization logic runs.
