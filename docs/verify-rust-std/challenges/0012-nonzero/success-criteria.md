# Success Criteria Coverage: Challenge 0012

This table is the branch-local coverage map for the published `NonZero`
requirements. It is seeded from the challenge page, planner/evaluator notes,
and the currently recorded branch evidence.

Status legend:

- `proof harness` means there is a branch-local proof/spec entrypoint for the
  function or family.
- `control reproducer` means the file exists only to separate a semantic
  frontier from a generic control shape.
- `not started` means no branch-local harness/spec has been added yet.
- `frontier reached` means a proof attempt has reached a concrete leaf or
  thunk frontier but has not closed.

| Function | Upstream Location | Harness/Spec File | Start Symbol | Kind | Status | Blocker Class | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `NonZeroU8::new` | `library/core/src/num/nonzero.rs` | `kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/new.rs` | `part1_new_u8` | proof harness | frontier reached | `MIR_SEMANTICS` | Exact `u8 -> Option<NonZeroU8>` niche-cast leaf still stops at `castKindTransmute`. |
| `NonZeroI8::new` | `library/core/src/num/nonzero.rs` | `kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/new.rs` | `part1_new_i8` | proof harness | frontier reached | `MIR_SEMANTICS` | Same harness as `NonZeroU8::new`; branch evidence keeps the narrowed cast frontier. |
| `NonZeroU8::new_unchecked` | `library/core/src/num/nonzero.rs` | `kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/new_unchecked.rs` | `part1_new_unchecked_u8` | proof harness | frontier reached | `MIR_SEMANTICS` | Checked by the same branch-local Part 1 slice; still not fully closed. |
| `NonZeroI8::new_unchecked` | `library/core/src/num/nonzero.rs` | `kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/new_unchecked.rs` | `part1_new_unchecked_i8` | proof harness | frontier reached | `MIR_SEMANTICS` | Part 1 slice uses an `i8` mirror to keep the proof shape symmetric. |
| `NonZeroU8::from_mut` | `library/core/src/num/nonzero.rs` | `kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/from_mut.rs` | `part1_from_mut_u8` | proof harness | frontier reached | `MIR_SEMANTICS` | Independent frontier at `castKindPtrToPtr`. |
| `NonZeroI8::from_mut` | `library/core/src/num/nonzero.rs` | `kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/from_mut.rs` | `part1_from_mut_i8` | proof harness | frontier reached | `MIR_SEMANTICS` | Mirrors the `u8` slice and keeps the pointer-cast blocker visible. |
| `NonZeroU8::count_ones` | `library/core/src/num/nonzero.rs` | `kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/count_ones.rs` | `part2_count_ones_u8` | proof harness | frontier reached | `MIR_SEMANTICS` | Part 2 seed; checks returned `NonZero` semantics via `.get()`. |
| `NonZeroU16::count_ones` | `library/core/src/num/nonzero.rs` | `kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/count_ones.rs` | `part2_count_ones_u16` | proof harness | frontier reached | `MIR_SEMANTICS` | Same seed as above on a wider integer. |
| `NonZero::<T>::from_mut_unchecked` | `library/core/src/num/nonzero.rs` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | Published Part 2 API listed in planner; no branch-local harness yet. |
| `NonZero::<T>::max` | `library/core/src/num/nonzero.rs` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | Part 2 API family, still waiting on a dedicated proof slice. |
| `NonZero::<T>::min` | `library/core/src/num/nonzero.rs` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | Part 2 API family, still waiting on a dedicated proof slice. |
| `NonZero::<T>::clamp` | `library/core/src/num/nonzero.rs` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | Part 2 API family, still waiting on a dedicated proof slice. |
| `NonZero::<T>::bitor` impls | `library/core/src/num/nonzero.rs` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | Planner calls out all 3 impls; no branch-local coverage yet. |
| `NonZero::<T>` bit operations family | `library/core/src/num/nonzero.rs` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | Includes the published bit-op family beyond the current seeds. |
| `NonZero::<T>` byte-order conversions family | `library/core/src/num/nonzero.rs` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local proof slice yet. |
| `NonZero::<T>` arithmetic family | `library/core/src/num/nonzero.rs` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local proof slice yet. |
| `NonZero::<T>` power family | `library/core/src/num/nonzero.rs` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | Includes the review-sensitive `isqrt` / 128-bit power discussion. |
| `NonZero::<T>` signed-only ops family | `library/core/src/num/nonzero.rs` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local proof slice yet. |
| `NonZero::<T>` unsigned-only ops family | `library/core/src/num/nonzero.rs` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | No branch-local proof slice yet. |
| `NonZero::<T>::isqrt` | `library/core/src/num/nonzero.rs` | `n/a` | `n/a` | proof harness | not started | `UNKNOWN` | Explicitly tracked because the evaluator expects a wide-type / bounded-case decision. |
| `u8 -> #[repr(transparent)] WrapU8` control | `n/a` | `kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/transmute_wrapper_u8.rs` | `part1_transmute_wrapper_u8` | control reproducer | passed | `none` | This is a control, not a published `NonZero` target; it separates generic same-size transmute support from the `NonZero::new` niche-cast frontier. |
| `u8 -> Option<NonZeroU8>` exact niche-cast control | `library/core/src/num/nonzero.rs` | `kmir/src/tests/integration/data/verify-rust-std/0012-nonzero/transmute_wrapper_u8.rs` | `part1_transmute_option_nonzero_u8` | control reproducer | frontier reached | `MIR_SEMANTICS` | Reproducer used to isolate the exact `NonZero::new` transmute shape. |

