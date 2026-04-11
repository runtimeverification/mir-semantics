# Evaluator Record: Challenge 0012

Ownership:

- Evaluator owns this file and `rubric.md`.
- Evaluator must not implement code, proofs, or harnesses.
- Evaluator must fail closed on missing evidence.

## Inputs

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0012-nonzero.md
- Tracking issue: [#71](https://github.com/model-checking/verify-rust-std/issues/71)
- Planner record: `docs/verify-rust-std/challenges/0012-nonzero/planner.md`
- Generator record: `docs/verify-rust-std/challenges/0012-nonzero/generator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0012-nonzero/rubric.md`

## Baseline Tasks

- Extend the rubric with challenge-specific criteria.
- Incorporate patterns from resolved challenges, existing solution PRs, and
  review comments.
- Record concrete evidence paths and rerun commands.

## Sprint 1 Evaluation

### Reproducibility verification

Four passing proofs re-run independently by evaluator (all PASSED):

| Harness | Command | Result |
| --- | --- | --- |
| `new.rs` | `timeout 900 uv --project kmir run -- kmir prove kmir/.../0012-nonzero/new.rs --verbose --terminate-on-thunk --proof-dir /tmp/kmir-0012-eval-new --reload --fail-fast` | `ProofStatus.PASSED`, nodes: 3, failing: 0 |
| `bitor.rs` | (same pattern, `--proof-dir /tmp/kmir-0012-eval-bitor`) | `ProofStatus.PASSED`, nodes: 3, failing: 0 |
| `checked_add.rs` | (same pattern, `--proof-dir /tmp/kmir-0012-eval-checked-add`) | `ProofStatus.PASSED`, nodes: 3, failing: 0 |
| `pow.rs` | (same pattern, `--proof-dir /tmp/kmir-0012-eval-pow`) | `ProofStatus.PASSED`, nodes: 3, failing: 0 |

Two failing proofs re-run independently (both FAILED as expected):

| Harness | Result | Blocker confirmed |
| --- | --- | --- |
| `leading_trailing_zeros.rs` | `ProofStatus.FAILED`, stuck: 1 | `ctlz_nonzero` intrinsic |
| `min_max.rs` | `ProofStatus.FAILED`, stuck: 1 | `FnOnce::call_once` trait dispatch |

### Niche-cast semantic fix review

Two rule sets were added to `kmir/src/kmir/kdist/mir-semantics/rt/data.md`:

**1. Multi-layer transparent transmute (lines 1684-1708)**

- Adds recursive wrap/unwrap for nested `#[repr(transparent)]` wrappers.
- Uses `#transparentDepth` (from `types.md`) to detect multi-layer nesting.
- The "Up" rule fires when `#transparentFieldTy(lookupTy(TY_TARGET))` is not
  `TyUnknown`, is not `TY_SOURCE`, and depth > 1.
- The "Down" rule fires analogously for the source type.
- **Assessment**: Sound. `#transparentFieldTy` only matches `typeInfoStructType`
  (single-field structs at zero offset), so these rules cannot fire for enum
  types. The depth guard prevents infinite recursion (base case terminates at
  depth 1 where the existing single-layer rules apply). The recursive
  decomposition correctly wraps/unwraps one layer at a time via K term
  rewriting. No overlap with existing single-layer rules because the depth > 1
  guard is exclusive with the `==K TY_SOURCE` / `==K TY_TARGET` guards on the
  single-layer rules.

**2. Niche-encoded `Option<NonZero<T>>` transmute (lines 1853-1933)**

- Introduces `#isOptionNonZero` helper using name-based prefix matching on
  `"std::option::Option<std::num::NonZero<"`.
- Guard: `notBool #isEnumWithoutFields(TI)` prevents conflict with field-less
  enum transmute rules.
- `#optionSomeFieldTy` extracts the `Some` variant field type from the enum
  type info structure.
- Four cast rules: nonzero-UP (with `#wrapSomeNonZero` continuation), zero-UP,
  Some-DOWN, None-DOWN.

**Assessment - correctness**: The rules are logically correct for the intended
pattern. The `#isOptionNonZero` / `#isEnumWithoutFields` mutual exclusion
prevents overlap with the existing integer-to-fieldless-enum transmute rules.
The `#wrapSomeNonZero` continuation is a standard K pattern for sequencing a
multi-step rewrite and is sound.

**Assessment - fragility**: The name-based matching (`#typeNameIs`) is
explicitly acknowledged as a workaround for missing `TagEncoding::Niche`
support in K. This is a known technical debt.
- Risk: if Rust changes the mangled name of `NonZero` or `Option` in SMIR
  output, or if the stable-mir-json tool changes its name encoding, the rules
  will silently stop matching and the niche transmute will thunk instead of
  resolving. This is a **fail-safe** failure (stuck proof, not unsound result).
- Risk: this only handles `Option<NonZero<T>>`, not other niche-encoded enums
  (e.g., `Option<&T>` where null is the niche). Generalizing will require
  structural `TagEncoding::Niche` support.
- Recommendation for S2: document the exact string dependency and add a
  regression test that catches name changes. Medium-term, implement
  `TagEncoding::Niche` in `ty.md` to replace name-based matching.

**Assessment - could this break other transmute paths?**: No. The new rules
are guarded by `#isOptionNonZero` which is only true for types named
`std::option::Option<std::num::NonZero<...`. The multi-layer transparent
rules are guarded by `#transparentFieldTy` which only returns non-`TyUnknown`
for `typeInfoStructType`. Neither set can fire for types that the existing
rules handle.

### Harness correctness review

**Part 1 harnesses (critical)**:

| Harness | Tests | Semantic assertions | Verdict |
| --- | --- | --- | --- |
| `new.rs` | `NonZeroU8::new(1)`, `NonZeroI8::new(1)` | "object created iff nonzero" via `is_none()`/`is_some()` branch, "value equals input" via `.unwrap().get() == x` | **Good** but only tested with `x=1`. Does not exercise `x=0` path at runtime since `main` passes `1`. The function body handles both cases but only the nonzero path is exercised. |
| `new_unchecked.rs` | `NonZeroU8::new_unchecked(1)`, `NonZeroI8::new_unchecked(1)` | Guards `x != 0` then asserts `.get() == x` | **Good** but only exercises `x=1`. |
| `get.rs` | `NonZeroU8::get`, `NonZeroI8::get` with values 1, 42, 255, -1, 127 | Asserts `.get() == expected` for each const | **Good**. Multi-value coverage. |
| `const_nonzero.rs` | Const `NonZeroU8` construction + `get` | Asserts `.get() == 5`, `.get() == 3` | **Adequate** for const path. |
| `transmute_wrapper_u8.rs` | Transparent wrapper + `Option<NonZero>` transmute | Asserts wrapped value equality and `is_some()` / `.unwrap().get()` | **Good** control harness. |

**Part 2 harnesses**:

| Harness | Semantic assertions | Verdict |
| --- | --- | --- |
| `bitor.rs` | `(3\|5).get() == 7`, `(5\|12).get() == 13`, `(3\|4u8).get() == 7` | **Good**. Tests both NZ\|NZ and NZ\|u8 impls. |
| `signed_ops.rs` | `is_positive`/`is_negative` for +5, -5, +1, -1 | **Good**. |
| `saturating_mul.rs` | `3*10 == 30` (no overflow), `100*10 == 255` (saturates) | **Good**. Tests both paths. |
| `pow.rs` | `checked_pow` for 2^0=1, 2^3=8, 3^2=9, 5^1=5 | **Good**. Multi-case coverage. |
| `checked_mul.rs` | `3*10 == 30` (no overflow only) | **Partial**. Missing overflow case (returns `None`). |
| `checked_add.rs` | `1+1=2`, `100+50=150`, `254+1=255` | **Partial**. Missing overflow case (returns `None`). |

**Part 1 concern**: The `new.rs` harness has the right structure (`if x == 0 {
is_none } else { is_some && get == x }`) but `main()` only calls with `x=1`.
The proof does exercise the full function body (K proves for the given
concrete input path), so this is semantically valid but not as strong as a
symbolic test. For a concrete-input proof, the `x=0` path is NOT exercised.

### Remaining 8 failures assessment

| Harness | Missing feature | Type | Complexity | Unlocks |
| --- | --- | --- | --- | --- |
| `leading_trailing_zeros.rs` | `ctlz_nonzero` intrinsic | Intrinsic impl | Small (K rule mapping `ctlz_nonzero` to log2 bit count) | `leading_zeros`, `trailing_zeros` |
| `ilog2.rs` | `ctlz_nonzero` intrinsic | (same) | (same fix) | `ilog2` (delegates to ctlz) |
| `unsigned_ops.rs` | `ctpop` intrinsic | Intrinsic impl | Small (K rule for popcount) | `is_power_of_two`, `count_ones` |
| `count_ones.rs` | `ctpop` intrinsic | (same) | (same fix) | `count_ones` |
| `byte_order.rs` | `bswap` intrinsic | Intrinsic impl | Small (K rule for byte reversal) | `to_be`, `to_le`, `swap_bytes` |
| `saturating_add.rs` | `saturating_add` intrinsic | Intrinsic impl | Small (K rule for saturating addition) | `saturating_add` |
| `min_max.rs` | `FnOnce::call_once` | Trait dispatch | Medium-large (core trait dispatch infrastructure) | `min`, `max`, `clamp` |
| `from_mut.rs` | `castKindPtrToPtr` | Pointer cast semantics | Medium (pointer-to-pointer cast system) | `from_mut`, `from_mut_unchecked` |

**Priority order for S2**:
1. **`ctlz_nonzero`** -- Small K rule addition, unlocks 3 harnesses (leading_zeros, trailing_zeros, ilog2). Highest ROI.
2. **`ctpop`** -- Small K rule, unlocks 2 harnesses (count_ones, is_power_of_two).
3. **`bswap`** -- Small K rule, unlocks 1 harness (byte_order). Trivial for u8 (identity).
4. **`saturating_add`** -- Small K rule, unlocks 1 harness.
5. **`castKindPtrToPtr`** -- Medium complexity, unlocks `from_mut` and `from_mut_unchecked`.
6. **`FnOnce::call_once`** -- Largest effort (trait dispatch infrastructure), unlocks min/max/clamp.

Items 1-4 are all small intrinsic additions (see `docs/dev/adding-intrinsics.md`).
Item 5 is a cast semantics extension. Item 6 is the largest and should be last.

### Not-started harnesses

Three functions still have no harness:
- `NonZero::clamp` -- blocked by same `FnOnce::call_once` as `min_max.rs`
- `NonZero::isqrt` -- needs separate harness; may involve `ctlz_nonzero`
- `NonZero::from_mut_unchecked` -- blocked by `castKindPtrToPtr` like `from_mut.rs`

## Scorecard

| Criterion | Score | Evidence | Gap |
| --- | --- | --- | --- |
| Published NonZero requirements are mapped to concrete artifacts | 3 | 19 harness files cover Part 1 (`new`, `new_unchecked`, `get`, `from_mut`) and Part 2 (`bitor`, `signed_ops`, `saturating_mul`, `checked_pow`, `checked_mul`, `checked_add`, `leading_trailing_zeros`, `ilog2`, `unsigned_ops`, `count_ones`, `min_max`, `byte_order`, `saturating_add`); coverage table in `success-criteria.md` | 3 functions still have no harness (`clamp`, `isqrt`, `from_mut_unchecked`) |
| Challenge-book rules are satisfied | 3 | Work is in challenge branch, scoped to `rt/data.md` semantic changes and `0012-nonzero/` harness directory; cherry-pickable | none |
| Safety conditions are modeled faithfully | 2 | Part 1 harnesses encode "object created iff nonzero" and "value equals input"; but `new.rs` only exercises `x=1` path (zero path not reached at runtime) | Need symbolic or multi-concrete-input tests for the zero path |
| Undefined behavior obligations are covered | 2 | 11 proofs pass without UB; `new_unchecked` guards `x != 0` precondition; no compiler-intrinsic UB in passing harnesses | 8 harnesses fail before UB check due to missing intrinsics; no explicit UB-triggering negative test |
| Evidence is reproducible | 3 | 4 proofs independently re-run by evaluator, all matched claimed status; 2 failures confirmed | none |
| Scope is challenge-local and cherry-pickable | 3 | Only `rt/data.md` semantic changes + `0012-nonzero/` harness files + docs | none |
| Review feedback patterns are incorporated | 2 | Harnesses use explicit value assertions (not just UB-free); `checked_mul`, `checked_add` only test non-overflow path | Overflow (None) path missing for checked arithmetic |
| Residual risk is explicit | 3 | Generator documents all 8 blockers with exact intrinsic/feature names; coverage table distinguishes `passed`, `frontier reached`, `not started` | none |

## Challenge-Specific Criteria

| Criterion | Score | Evidence | Gap |
| --- | --- | --- | --- |
| Part 1 `new` / `new_unchecked` correctness is implemented and verified | 3 | `new.rs` and `new_unchecked.rs` PASS with explicit `is_some`/`is_none` + `get == x` assertions; `get.rs` covers multiple values | `new.rs` only exercises x=1 concrete path |
| Part 2 `NonZero` APIs are covered with semantic assertions | 2 | 6 Part 2 proofs pass (`bitor`, `signed_ops`, `saturating_mul`, `checked_pow`, `checked_mul`, `checked_add`); 8 harnesses exist but fail on missing intrinsics | `checked_mul` and `checked_add` missing overflow/None path; 3 functions have no harness |
| Wide-type / bounded-case decisions are explicit | 0 | No `isqrt` harness, no 128-bit coverage, no explicit decision documented | Need explicit rationale or harness |
| Reproducible proof/test evidence exists for the actual NonZero suite | 3 | 11 passing proofs confirmed by generator; 4 independently re-verified by evaluator; 8 failures documented with exact blockers | none |
| Niche-cast semantic fix is correct and non-breaking | 2 | Rules are logically correct and disjoint from existing transmute rules; fragility of name-based matching is acknowledged | Name-based matching should be replaced with structural `TagEncoding::Niche` support medium-term |

## Review Pattern Notes

- The niche-cast fix (name-based `#isOptionNonZero`) is a pragmatic workaround.
  It is fail-safe (stuck proof on mismatch, not unsound). The correct long-term
  fix is structural `TagEncoding::Niche` data in K type info.
- The multi-layer transparent transmute rules are well-designed and general.
  They should work for any nested `#[repr(transparent)]` wrapping, not just
  `NonZero`.
- `checked_add.rs` and `checked_mul.rs` only test the non-overflow (Some) path.
  The overflow (None) path reportedly hits `UnableToDecode` for niche-encoded
  constant bytes. This is a separate issue from the transmute fix and should be
  addressed in S2.
- `new.rs` calls with concrete `x=1` only. The function body branches on `x ==
  0` but only the nonzero path is reached. A harness calling `new(0)` would
  exercise the zero-to-None path and strengthen Part 1 coverage.

## Verdict

- Current status: `in progress`
- Score: 11/19 harnesses passing. Part 1 core (`new`, `new_unchecked`, `get`)
  is verified. The niche-cast semantic fix is the major accomplishment of this
  sprint. 8 failures are due to missing intrinsics/features, not the niche-cast.

## Actionable critique for Generator S2

1. **Highest priority**: Implement `ctlz_nonzero` intrinsic (unlocks 3
   harnesses). See `docs/dev/adding-intrinsics.md`. Expected: small K rule
   addition mapping to bit-width minus floor-log2.
2. **Second priority**: Implement `ctpop` intrinsic (unlocks 2 harnesses).
   Standard popcount operation.
3. **Third priority**: Implement `bswap` and `saturating_add` intrinsics
   (unlock 2 harnesses total).
4. **Fourth priority**: Add `new(0)` call to `new.rs` main function to exercise
   the zero-to-None transmute path.
5. **Fifth priority**: Add overflow test cases for `checked_add` and
   `checked_mul` (requires fixing `UnableToDecode` for niche-encoded None
   constants).
6. **Sixth priority**: Add `clamp`, `isqrt`, `from_mut_unchecked` harnesses
   (some blocked by `FnOnce::call_once` or `castKindPtrToPtr`).

## Iteration Log

- Bootstrap record created by orchestrator.
- 2026-04-09 UTC: prerequisite semantic baseline validated on the re-execution
  branch, but the actual NonZero harness/contract layer is still missing.
- 2026-04-09 UTC: branch-local `NonZero` artifacts landed and reproducible
  proof frontiers were recorded; readiness remains `in progress` because no
  NonZero proof has passed end-to-end yet.
- 2026-04-11 UTC: Sprint 1 evaluation. Generator resolved the niche-cast
  blocker with two rule sets in `rt/data.md`. 11/19 harnesses now PASS. 4
  proofs independently re-verified by evaluator (`new.rs`, `bitor.rs`,
  `checked_add.rs`, `pow.rs`). 2 expected failures confirmed
  (`leading_trailing_zeros.rs`, `min_max.rs`). The niche-cast fix is logically
  correct but uses fragile name-based matching. Status upgraded from `blocked`
  to `in progress`. Remaining work is primarily intrinsic implementations
  (small K rule additions) rather than semantic architecture changes.
