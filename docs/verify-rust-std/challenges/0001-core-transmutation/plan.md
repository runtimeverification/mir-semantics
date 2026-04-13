---
challenge: "0001-core-transmutation"
status: generating
priority: p0
iteration: 2
last_updated: 2026-04-11
---

## Challenge Requirements

**Source:** https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0001-core-transmutation.md
**Tracking Issue:** [#19](https://github.com/model-checking/verify-rust-std/issues/19) (CLOSED)

### Goal

Verify the safety of `core` transmuting methods. The challenge covers `transmute`, `transmute_unchecked`, and all standard library functions that use these intrinsics internally.

### Threshold

35 out of 47 listed functions must have passing proofs for submission.

### UB Obligations

- No access through dangling or misaligned pointers
- No reads from uninitialized memory
- No mutation of immutable bytes
- No production of invalid values
- All SAFETY comments in source must be respected

### Additional Requirement

A new entry to the specification book documenting transmute verification patterns.

## Success Criteria Matrix

### Proof Run Summary (2026-04-11, iteration 2)

**34 harnesses total: 31 PASSED, 2 FAILED, 1 COMPILE ERROR**

#### PASSED (31 harnesses)

| Harness | Target Function | Upstream Listed | Timeout Notes |
|---|---|---|---|
| `transmute_roundtrip.rs` | `transmute` | Yes (1/47) | <120s |
| `transmute_integers.rs` | `transmute` | Yes | <120s |
| `transmute_array_bytes.rs` | `transmute` | Yes | <120s |
| `transmute_multi_width.rs` | `transmute` | Yes | <120s |
| `transmute_roundtrip_comprehensive.rs` | `transmute` | Yes | <120s |
| `transmute_same_type.rs` | `transmute` | Yes | <120s |
| `transmute_wrapper_structs.rs` | `transmute` | Yes | <120s |
| `transmute_struct_fields.rs` | `transmute` | Yes | <120s |
| `transmute_enum.rs` | `transmute` | Yes | <120s |
| `transmute_enum_variants.rs` | `transmute` | Yes | <120s |
| `transmute_unchecked_integers.rs` | `transmute_unchecked` | Yes (2/47) | <120s |
| `transmute_unchecked_maybeuninit_int.rs` | `transmute_unchecked` | Yes | <120s |
| `transmute_unchecked_struct.rs` | `transmute_unchecked` | Yes | <120s |
| `maybeuninit_basic.rs` | `MaybeUninit::new`/`assume_init` | No (building blocks) | <120s |
| `maybeuninit_write_assume_init.rs` | `MaybeUninit::new`/`assume_init` | No | <120s |
| `maybeuninit_assume_init_ref.rs` | `MaybeUninit::assume_init_ref` | No | <120s |
| `maybeuninit_assume_init_mut.rs` | `MaybeUninit::assume_init_mut` | No | 120-180s |
| `maybeuninit_struct.rs` | `MaybeUninit` (structs) | No | <120s |
| `maybeuninit_init_patterns.rs` | `MaybeUninit` (enums/arrays) | No | <120s |
| `from_u32_unchecked.rs` | `char::from_u32_unchecked` | Yes (3/47) | <120s |
| `char_try_from_u32.rs` | `char::try_from(u32)` | Yes (4/47) | <120s |
| `ascii_char_from_u8.rs` | `AsciiChar::from_u8` | Yes (5/47) | <120s |
| `ascii_char_from_u8_unchecked.rs` | `AsciiChar::from_u8_unchecked` | Yes (6/47) | <120s |
| `char_as_ascii.rs` | `char::as_ascii` | Yes (7/47) | <120s |
| `char_step_forward_checked.rs` | `<char as Step>::forward_checked` | Yes (8/47) | <120s |
| `char_step_forward_unchecked.rs` | `<char as Step>::forward_unchecked` | Yes (9/47) | 120-180s |
| `char_step_backward_unchecked.rs` | `<char as Step>::backward_unchecked` | Yes (10/47) | <120s |
| `char_encode_utf16_raw.rs` | `char::encode_utf16_raw` | Yes (11/47) | <120s |
| `alignment_new.rs` | `Alignment::new` | Yes (12/47) | 120-180s |
| `alignment_new_unchecked.rs` | `Alignment::new_unchecked` | Yes (13/47) | <120s |
| `layout_from_size_align_unchecked.rs` | `Layout::from_size_align_unchecked` | Yes (14/47) | 120-180s |

#### FAILED (2 harnesses)

| Harness | Target Function | Failure Mode | Upstream Listed |
|---|---|---|---|
| `is_aligned_to_const.rs` | `is_aligned_to` | ProofStatus.FAILED (failing: 1) | Yes (15/47) |
| `layout_from_size_align.rs` | `Layout::from_size_align` | ProofStatus.FAILED (failing: 1, stuck: 1) | Yes (16/47) |

#### COMPILE ERROR (1 harness)

| Harness | Target Function | Error |
|---|---|---|
| `borrowed_buf_unfilled.rs` | `BorrowedBuf::unfilled` | stable-mir-json compilation failure (exit 101) |

### Upstream Function Coverage

**Current: 14/47 upstream functions with PASSING proofs** (previously the evaluator assessed 2/47, but 12 new harnesses now pass for char, alignment, and layout functions).

The 2 FAILED proofs target 2 additional upstream functions (`is_aligned_to`, `Layout::from_size_align`) that are reachable but need harness/semantic fixes.

The 6 MaybeUninit harnesses exercise building-block methods (`new`, `assume_init`, `assume_init_ref`, `assume_init_mut`) that are not in the upstream 47 function list but demonstrate the semantic support foundation.

### Gap to Threshold

**35 - 14 = 21 more upstream functions needed.**

## Semantic Changes Applied

This branch includes the following changes vs the portfolio baseline:

1. **`intrinsics.md`** -- priority annotation
2. **`rt/data.md`** -- operandMove fix (shared with 0009-duration) + MaybeUninit transmute relaxation + TRANSMUTE_CHAR rule (u32->char cast, enabling 9 char-related functions) + TRANSMUTE_USIZE/Alignment rules
3. **`rt/decoding.md`** -- minor change

**Cross-challenge cherry-picks available from 0012-nonzero:**
- `ctpop` (popcount), `ctlz`/`ctlz_nonzero` (leading zeros), `bswap` (byte swap), `saturating_add` intrinsics
- Niche-encoded `Option<NonZero<T>>` transmute rules
- Multi-layer transparent wrapper transmute rules

## Sprint Plan

| Sprint | Scope | Status | Functions Unlocked |
|---|---|---|---|
| S0 | Bootstrap, requirements extraction | Done | -- |
| S1 | transmute + transmute_unchecked harnesses (19 harnesses) | Done | 2/47 |
| S1b | Harnesses for blocked char/alignment/layout functions (15 harnesses) | Done | +12 = 14/47 |
| S2 | Fix `is_aligned_to_const` and `layout_from_size_align` proofs | Pending | +2 = 16/47 |
| S3 | Fix `borrowed_buf_unfilled` compile error | Pending | +1 = 17/47 |
| S4 | Write harnesses for remaining reachable functions (see NOT STARTED list) | Pending | target +10-15 |
| S5 | Implement UNION_EVAL/UNION_TRANSMUTE rules (array_assume_init, transpose) | Pending | +4 |
| S6 | Investigate UNKNOWN-category functions, pick low-hanging fruit | Pending | varies |
| S7 | Write specification book entry | Pending | -- |

### Functions NOT STARTED (no harness exists)

**Likely reachable with current semantics (investigate first):**
- `BorrowedCursor::reborrow`
- `MaybeUninit<T>::copy_from_slice`
- `try_from_fn` (core::array)
- `iter_next_chunk` (core::array)
- `align_offset` (core::ptr)
- `<[T]>::align_to`, `<[T]>::align_to_mut`

**Blocked by known semantic gaps:**
- `MaybeUninit<T>::array_assume_init` (UNION_EVAL)
- `MaybeUninit<[T; N]>::transpose` (UNION_TRANSMUTE)
- `<[MaybeUninit<T>; N]>::transpose` (UNION_TRANSMUTE)
- `<[T; N] as IntoIterator>::into_iter` (UNION_EVAL)
- `str::as_bytes`, `str::as_bytes_mut` (STRING_DECODE)
- `Ipv6Addr::new`, `Ipv6Addr::segments` (ARRAY_TRANSMUTE)

**Likely high-effort / deep semantic gaps:**
- `run_utf8_validation`, `memchr_aligned`, `memrchr`, `do_count_chars`
- `make_ascii_lowercase`, `make_ascii_uppercase`
- `<Chars>::next`, `<Chars>::next_back`
- `<Filter>::next_chunk`, `<FilterMap>::next_chunk`
- `<[T]>::as_simd`, `<[T]>::as_simd_mut`

## Blockers & Dependencies

### Blocker Classification

| Blocker | Functions Affected | Fix Effort | Fix Location | Status |
|---|---|---|---|---|
| TRANSMUTE_CHAR | 9 | Medium | rt/data.md | **RESOLVED** (all 9 now pass) |
| INTRINSIC_CTPOP | 1 + transitively 3-4 | Small | intrinsics.md | **RESOLVED** (Alignment::new passes) |
| TRANSMUTE_USIZE | 3 | Small-Medium | rt/data.md | **PARTIALLY RESOLVED** (2/3 pass, layout_from_size_align fails) |
| UNION_EVAL | 2 | Medium | rt/data.md | Open |
| UNION_TRANSMUTE | 2 | Medium | rt/data.md | Open |
| ARRAY_TRANSMUTE | 2 | Large | rt/data.md | Open |
| STRING_DECODE | 2 | Large | decoding.md | Open |
| UNKNOWN | 15+ | Varies | Investigation needed | Open |

### Proof Failures Requiring Investigation

1. **`is_aligned_to_const`**: ProofStatus.FAILED with `failing: 1`. Needs frontier inspection to determine if this is a harness issue or a semantic gap.
2. **`layout_from_size_align`**: ProofStatus.FAILED with `failing: 1, stuck: 1`. The stuck node indicates a semantic gap (likely a missing rule hit during execution).
3. **`borrowed_buf_unfilled`**: Compilation failure in stable-mir-json. The harness may use unstable features not supported by the current toolchain.

### Cross-Challenge Semantic Reuse Opportunities

- The `ctpop`/`ctlz`/`bswap`/`saturating_add` intrinsics from 0012-nonzero appear to already be cherry-picked into this branch (Alignment::new passes).
- The TRANSMUTE_CHAR rule benefits any challenge involving char operations.
- The operandMove fix is shared with 0009-duration.
- UNION_EVAL/UNION_TRANSMUTE fixes would benefit any challenge using MaybeUninit arrays.

## Cross-Challenge Notes

- Challenge 0011 (floats-ints) artifact layout is a useful template for organizing proof evidence.
- Challenge 0002 contract framing for unsafe intrinsics is a style reference for caller obligations.
- Simplification lemmas in `kmir-lemmas.md` may be needed for byte-mask identities in transmute arithmetic.
- Spec-book entry should document: (a) transmute safety model, (b) concrete proof patterns used, (c) blocker taxonomy for future challenges.

## Reproducibility

```bash
cd /home/zhaoji/projs/mir-semantics-vrs/challenges/0001-core-transmutation

# Run a single proof (use 180s timeout for alignment_new, char_step_forward_unchecked,
# layout_from_size_align_unchecked, maybeuninit_assume_init_mut)
timeout 180 uv --project kmir run -- kmir prove \
  kmir/src/tests/integration/data/verify-rust-std/0001-core-transmutation/<file>.rs \
  --verbose --terminate-on-thunk \
  --proof-dir /tmp/kmir-0001-<name> --reload --fail-fast

# Run all proofs in batch (120s timeout per proof)
for f in kmir/src/tests/integration/data/verify-rust-std/0001-core-transmutation/*.rs; do
  name=$(basename "$f" .rs)
  echo "=== $name ==="
  timeout 120 uv --project kmir run -- kmir prove "$f" \
    --verbose --terminate-on-thunk \
    --proof-dir "/tmp/kmir-0001-$name" --reload --fail-fast 2>&1 | tail -3
  echo "---"
done
```
