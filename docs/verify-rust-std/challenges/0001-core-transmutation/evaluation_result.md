# Evaluation Result: Challenge 0001-core-transmutation

## Verdict

`in_progress` -- the branch has strong harness health (`31/34` PASS) but is still far below the submission bar (`14/47` upstream functions covered vs `35/47` required).

## Scorecard

| Criterion | Status | Evidence |
| --- | --- | --- |
| Submission threshold | FAIL | `14/47` upstream-listed functions have passing proofs; `21` more are needed for submission. |
| Harness health | PARTIAL | `31/34` harnesses PASS, with `2` proof failures and `1` compile error. |
| Failure triage quality | PASS | The remaining red items are localized: `is_aligned_to_const.rs`, `layout_from_size_align.rs`, and `borrowed_buf_unfilled.rs`. |
| Reproducibility | PASS | The challenge already records concrete `kmir prove` commands and timeout guidance in `plan.md`. |
| Residual risk | HIGH | The current passing set is dominated by `transmute`, `char`, `Alignment`, and `MaybeUninit` building blocks; many upstream functions still have no verified harness. |

## Current Coverage Summary

- Passing harnesses: `31/34`
- Upstream passing function coverage: `14/47`
- Failed harnesses:
  - `is_aligned_to_const.rs` -> `is_aligned_to` fails on the ptr-to-int transmute path
  - `layout_from_size_align.rs` -> `Layout::from_size_align` has one failing node and one stuck node
- Compile error:
  - `borrowed_buf_unfilled.rs` -> stable-mir-json compilation failure

## Reproducibility Evidence Commands

```bash
cd /home/zhaoji/projs/mir-semantics-vrs/challenges/0001-core-transmutation

# Reproduce a representative passing proof
timeout 180 uv --project kmir run -- kmir prove \
  kmir/src/tests/integration/data/verify-rust-std/0001-core-transmutation/alignment_new.rs \
  --verbose --terminate-on-thunk \
  --proof-dir /tmp/kmir-0001-alignment_new --reload --fail-fast

# Reproduce the two current proof failures
timeout 180 uv --project kmir run -- kmir prove \
  kmir/src/tests/integration/data/verify-rust-std/0001-core-transmutation/is_aligned_to_const.rs \
  --verbose --terminate-on-thunk \
  --proof-dir /tmp/kmir-0001-is-aligned --reload --fail-fast

timeout 180 uv --project kmir run -- kmir prove \
  kmir/src/tests/integration/data/verify-rust-std/0001-core-transmutation/layout_from_size_align.rs \
  --verbose --terminate-on-thunk \
  --proof-dir /tmp/kmir-0001-layout-from-size-align --reload --fail-fast

# Reproduce the compile error
timeout 180 uv --project kmir run -- kmir prove \
  kmir/src/tests/integration/data/verify-rust-std/0001-core-transmutation/borrowed_buf_unfilled.rs \
  --verbose --terminate-on-thunk \
  --proof-dir /tmp/kmir-0001-borrowed-buf --reload --fail-fast

# Sweep the full challenge harness directory
for f in kmir/src/tests/integration/data/verify-rust-std/0001-core-transmutation/*.rs; do
  name=$(basename "$f" .rs)
  timeout 180 uv --project kmir run -- kmir prove "$f" \
    --verbose --terminate-on-thunk \
    --proof-dir "/tmp/kmir-0001-$name" --reload --fail-fast
done
```

## Actionable Next Steps

1. Fix `is_aligned_to_const.rs` by resolving the ptr-to-int transmute frontier; this is the cleanest route to converting one known upstream failure into coverage.
2. Split `layout_from_size_align.rs` into its two current problems: close the failing branch first, then inspect the stuck node for the missing semantic rule on the size/align validation path.
3. Unblock `borrowed_buf_unfilled.rs` at the stable-mir-json/toolchain layer so it stops consuming one of the three red slots without giving semantic signal.
4. After the three existing red items are green, target the already-present but not yet counted harnesses for reachable functions such as `align_offset`, `try_from_fn`, `borrowed_cursor_reborrow`, and `maybeuninit_copy_from_slice`.
5. Treat union-related and array/string decoding gaps (`array_assume_init`, `transpose`, `str::as_bytes`, `Ipv6Addr`) as second-wave work only after the reachable low-effort functions have been harvested toward `35/47`.
