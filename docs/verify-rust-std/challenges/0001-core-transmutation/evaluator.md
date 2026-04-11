# Evaluator Record: Challenge 0001

Ownership:

- Evaluator owns this file and `rubric.md`.
- Evaluator must not implement code, proofs, or harnesses.
- Evaluator must fail closed on missing evidence.

## Inputs

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0001-core-transmutation.md
- Tracking issue: [#19](https://github.com/model-checking/verify-rust-std/issues/19)
- Planner record: `docs/verify-rust-std/challenges/0001-core-transmutation/planner.md`
- Generator record: `docs/verify-rust-std/challenges/0001-core-transmutation/generator.md`
- Branch-local rubric: `docs/verify-rust-std/challenges/0001-core-transmutation/rubric.md`

## Baseline Tasks

- Extend the rubric with challenge-specific criteria.
- Incorporate patterns from resolved challenges, existing solution PRs, and
  review comments.
- Record concrete evidence paths and rerun commands.

## Sprint 1 Evaluation

### 1. Artifact Inventory

19 `.rs` harness files in `kmir/src/tests/integration/data/verify-rust-std/0001-core-transmutation/`:

| File | Target Function(s) | Semantically Meaningful | Correct |
| --- | --- | --- | --- |
| `transmute_roundtrip.rs` | `transmute` | Yes - byte-array <-> u64 roundtrip with endianness check | Yes |
| `transmute_integers.rs` | `transmute` | Yes - u32/i32 MAX=-1 check, multiple widths | Yes |
| `transmute_array_bytes.rs` | `transmute` | Yes - LE byte layout verified | Yes |
| `transmute_multi_width.rs` | `transmute` | Yes - u128/i128, LE layout checks | Yes |
| `transmute_roundtrip_comprehensive.rs` | `transmute` | Yes - all widths, boundary values | Yes |
| `transmute_same_type.rs` | `transmute` | Weak - identity transmute is trivial | Yes |
| `transmute_wrapper_structs.rs` | `transmute` | Yes - T <-> Wrapper(T) field access | Yes |
| `transmute_struct_fields.rs` | `transmute` | Yes - repr(transparent) roundtrips | Yes |
| `transmute_enum.rs` | `transmute` | Yes - discriminant matching u8->enum | Yes |
| `transmute_enum_variants.rs` | `transmute` | Yes - multiple repr types u8/u16/i32 | Yes |
| `transmute_unchecked_integers.rs` | `transmute_unchecked` | Yes - roundtrip across widths | Yes |
| `transmute_unchecked_maybeuninit_int.rs` | `transmute_unchecked` + `MaybeUninit::assume_init` | Yes - T -> MaybeUninit<T> -> T | Yes |
| `transmute_unchecked_struct.rs` | `transmute_unchecked` + `MaybeUninit::assume_init` | Yes - struct -> MaybeUninit<struct> | Yes |
| `maybeuninit_basic.rs` | `MaybeUninit::new` + `assume_init` | Yes - multiple types including bool | Yes |
| `maybeuninit_write_assume_init.rs` | `MaybeUninit::new` + `assume_init` | Yes - nested, boundary values | Yes |
| `maybeuninit_assume_init_ref.rs` | `MaybeUninit::assume_init_ref` | Yes - read by reference | Yes |
| `maybeuninit_assume_init_mut.rs` | `MaybeUninit::assume_init_mut` | Yes - read by mut reference | Yes |
| `maybeuninit_struct.rs` | `MaybeUninit::new` + `assume_init` (structs) | Yes - multi-field structs | Yes |
| `maybeuninit_init_patterns.rs` | `MaybeUninit::new` + `assume_init` (enums/arrays) | Yes - Option, Result, arrays | Yes |

### 2. Function Coverage Assessment

The upstream challenge lists **47 functions**. The 19 harnesses map to the following
**distinct upstream functions**:

| Upstream Function | Covered By | Count |
| --- | --- | --- |
| `transmute` (core::intrinsics) | 10 harness files | 1 |
| `transmute_unchecked` (core::intrinsics) | 3 harness files | 1 |

That is **2 of 47 upstream functions** covered by passing proofs.

The MaybeUninit harnesses (6 files) exercise `MaybeUninit::new` and `assume_init`/
`assume_init_ref`/`assume_init_mut`, but these are **not listed** in the upstream
challenge's 47 functions. The challenge lists:
- `MaybeUninit<T>::array_assume_init` (blocked)
- `MaybeUninit<[T; N]>::transpose` (blocked)
- `<[MaybeUninit<T>; N]>::transpose` (blocked)
- `MaybeUninit<T>::copy_from_slice` (not started)

None of these four specific MaybeUninit methods are exercised by the current harnesses.
The harnesses test `MaybeUninit::new` + `assume_init` which are foundational but are
**not themselves listed in the 47 functions**.

**Critical finding**: The 19 harnesses cover only **2 of 47** upstream-listed functions
(`transmute` and `transmute_unchecked`). The remaining 17 harnesses test useful
properties of the transmute intrinsics and MaybeUninit basics, but they are
**redundant coverage of the same 2 functions**, not coverage of additional upstream
targets.

The success-criteria.md claims "19 harnesses covering functions `transmute`,
`transmute_unchecked`, and `MaybeUninit` methods" which is accurate in a literal sense
but misleading because the MaybeUninit methods exercised are not the ones the challenge
requires.

### 3. Reproducibility Verification

Four proofs were re-run and all passed:

| Harness | Status | Nodes | Depth |
| --- | --- | --- | --- |
| `transmute_integers.rs` | PASSED | 3 | 494 |
| `transmute_unchecked_struct.rs` | PASSED | 3 | 431 |
| `maybeuninit_init_patterns.rs` | PASSED | 3 | 870 |
| `transmute_enum_variants.rs` | PASSED | 3 | 910 |

Command template:
```bash
cd /home/zhaoji/projs/mir-semantics-vrs/challenges/0001-core-transmutation/
timeout 900 uv --project kmir run -- kmir prove \
    kmir/src/tests/integration/data/verify-rust-std/0001-core-transmutation/<file>.rs \
    --verbose --terminate-on-thunk --proof-dir /tmp/kmir-0001-eval-<name> --reload --fail-fast
```

All proofs pass cleanly with 3 nodes (init -> execution -> target subsumption), confirming
the proofs are genuine and reproducible.

### 4. Harness Quality Assessment

**Strengths:**
- Assertions are non-trivial (endianness checks, boundary values, roundtrip verification)
- Good variety of types (u8 through u128, signed/unsigned, structs, enums)
- `transmute_same_type.rs` is the weakest (identity transmute) but still valid
- Enum transmute harnesses correctly check discriminant-matching behavior
- MaybeUninit harnesses correctly exercise the transmute bridge through union types

**Weaknesses:**
- All harnesses use concrete values only; no symbolic/arbitrary inputs
- Harnesses test direct `std::mem::transmute` calls, not the libcore wrapper functions
  that the challenge actually lists (e.g., `from_u32_unchecked`, `str::as_bytes`,
  `Alignment::new`, etc.)
- The MaybeUninit harnesses test `.new()` and `.assume_init()` which are not in the
  challenge list; the listed methods (`array_assume_init`, `transpose`, `copy_from_slice`)
  are all blocked
- No harness tests any Part III or Part IV function from the challenge

### 5. Blocker Classification Assessment

| Blocker Class | Correctly Classified | Could a Simpler Harness Bypass? | Estimated Fix Effort |
| --- | --- | --- | --- |
| `TRANSMUTE_CHAR` (8 functions) | Yes - no `#cast` rule for Integer -> char type | No - fundamental semantic gap | **Medium** - add a K rule for `#cast(Integer(VAL, 32, _), castKindTransmute, _, TY)` where `TY` resolves to `char`, producing a `Char(VAL)` value. Single rule in `rt/data.md`. |
| `TRANSMUTE_USIZE` (3 functions) | Partially - the real issue is transmuting `usize` into `Alignment` which is a newtype wrapping a `NonZero<usize>` wrapping `usize`. The existing wrapper rules may not chain through multiple layers. | Possibly - if `Alignment` is `repr(transparent)`, the existing `#transparentFieldTy` rule might work if the type resolution properly unwraps. Needs investigation. | **Small-Medium** - may need a rule for transmuting through nested newtypes, or a specific `usize -> Alignment` rule. |
| `UNION_EVAL` (2 functions) | Yes - `#evalUnion` has no rule for extracting a value from a `Union` when indexing into an array of `MaybeUninit<T>`. | No - the stuck term is a genuine semantic gap. | **Medium** - need a rule for array indexing that produces a `Union` element, then a rule to unwrap it. |
| `UNION_TRANSMUTE` (2 functions) | Yes - reverse direction (Union -> T) not handled. | No - fundamental gap. | **Medium** - add a `#cast(Union(fieldIdx(1), Aggregate(variantIdx(0), ListItem(VAL))), castKindTransmute, TY_FROM, TY_TO)` rule to unwrap the ManuallyDrop layer. |
| `ARRAY_TRANSMUTE` (2 functions) | Yes - transmuting `[u16; N]` <-> `[u8; 2N]` requires element-wise byte reinterpretation. | No - the existing `#transmuteElems` only handles same-length arrays. | **Large** - need byte-level array reinterpretation rules, handling different element sizes. |
| `STRING_DECODE` (2 functions) | Yes - `#decodeConstant` has no rule for string allocations (commented-out rule at `decoding.md:61`). | Possibly - if the harness avoids string literals and uses byte-constructed strings instead. But `str::as_bytes` inherently needs string handling. | **Large** - requires implementing string constant decoding. |
| `INTRINSIC_CTPOP` (1 function) | Yes - no `ctpop` intrinsic support anywhere in the semantics. `Alignment::new` calls `is_power_of_two()` which uses `count_ones()` which maps to `ctpop`. | No - fundamental intrinsic gap. | **Small** - add a `ctpop` intrinsic rule that computes popcount. Single rule addition in `kmir.md`. |
| `UNKNOWN` (15+ functions) | Acceptable classification at S1 stage but these need investigation in S2. | Varies - some may be reachable with focused harness work. | Unknown until investigated. |

### 6. Priority Ranking for Generator S2

**Highest leverage fixes** (unlock the most functions per effort):

1. **TRANSMUTE_CHAR** (unlocks 8 functions): Add a K rule for transmuting an integer
   to a `char` type. This is a single rule in `rt/data.md` at the `castKindTransmute`
   section (~line 1775). The rule should:
   - Match `#cast(Integer(VAL, 32, _), castKindTransmute, _, TY_TO)` where
     `lookupTy(TY_TO)` is `typeInfoPrimitiveType(primTypeChar)`
   - Produce `Char(VAL)` (or whatever the K representation of char is)
   - Optionally validate that VAL is a valid Unicode scalar value
   **File**: `kmir/src/kmir/kdist/mir-semantics/rt/data.md`

2. **INTRINSIC_CTPOP** (unlocks 1 function directly, but `Alignment::new` is a
   prerequisite for `TRANSMUTE_USIZE` functions too, so effectively unlocks 3-4):
   Add `ctpop` to the intrinsic dispatch. Check how other intrinsics like `black_box`
   are implemented in `kmir.md` and follow the same pattern.
   **File**: `kmir/src/kmir/kdist/mir-semantics/kmir.md` (intrinsic dispatch)

3. **TRANSMUTE_USIZE** (unlocks 3 functions): Investigate whether the existing
   `#transparentFieldTy` wrapper rules can chain through `Alignment -> NonZero<usize> -> usize`.
   If not, add rules for multi-layer newtype unwrapping.
   **File**: `kmir/src/kmir/kdist/mir-semantics/rt/data.md`

4. **UNION_EVAL + UNION_TRANSMUTE** (unlocks 4 functions): Two related gaps. Add rules
   for extracting values from `Union` containers and for reverse-transmuting `Union`
   back to the inner type.
   **File**: `kmir/src/kmir/kdist/mir-semantics/rt/data.md`

5. **UNKNOWN investigation** (15+ functions): Many of the `UNKNOWN` functions may be
   reachable once the above fixes land. Generator S2 should attempt harnesses for
   at least `BorrowedBuf::unfilled`, `align_offset`, `MaybeUninit::copy_from_slice`,
   and the simpler slice/iterator functions to discover which concrete blockers they hit.

**Lower priority** (high effort, few functions):
- `ARRAY_TRANSMUTE` (2 functions): Requires byte-level array reinterpretation
- `STRING_DECODE` (2 functions): Requires string constant infrastructure

### 7. Actionable Critique for Generator S2

1. **Coverage is critically low**: 2/47 upstream functions vs. the 35/47 threshold.
   The 19 harnesses give good **depth** on `transmute` and `transmute_unchecked` but
   near-zero **breadth** across the challenge function list. S2 must prioritize breadth.

2. **MaybeUninit harnesses target wrong methods**: The 6 MaybeUninit harnesses test
   `new`/`assume_init`/`assume_init_ref`/`assume_init_mut` which are building blocks
   but not listed in the 47. S2 should target `array_assume_init`, `transpose`, and
   `copy_from_slice` specifically.

3. **No semantic fixes were attempted**: All blockers are documented but none were
   fixed. S2 must implement at least the `TRANSMUTE_CHAR` and `INTRINSIC_CTPOP`
   rules to make meaningful progress toward the 35/47 threshold.

4. **No spec-book entry exists**: The challenge explicitly requires "a new entry to
   the specification book" explaining transmute verification patterns. This is a
   critical rubric criterion that is completely absent.

5. **Concrete-only testing**: All harnesses use hardcoded values. While this is valid
   for kmir proofs (which symbolically execute), the specific values chosen should be
   documented as representative of the proof obligations (bit-validity, boundary
   conditions, etc.).

6. **The `transmute_same_type.rs` harness is near-trivial**: Identity transmute
   exercises no interesting semantic behavior. It could be replaced with a harness
   for an actual listed function.

7. **Missing fail harnesses**: No `-fail.rs` harnesses test that invalid transmutes
   (e.g., wrong-discriminant enum transmute) are correctly rejected. These would
   strengthen the evidence that the semantics is sound.

## Scorecard

| Criterion | Score | Evidence | Gap |
| --- | --- | --- | --- |
| Spec-book guidance for transmutation exists and is referenced | 0 | No spec-book entry created. | Critical gap - challenge explicitly requires this. |
| Coverage threshold is evidenced for the published target set | 0 | 2/47 functions covered by passing proofs. 19 harnesses exist but map to only 2 upstream functions. | 33 more functions needed to reach 35/47 threshold. |
| In-scope transmutation APIs have faithful contracts | 1 | `transmute` and `transmute_unchecked` are well-exercised with meaningful assertions. Remaining 45 functions have no contracts. | Partial - good depth on 2 functions, zero breadth. |
| Safe wrappers are wrapped with local assumptions and assertions | 0 | No safe wrapper functions (Part IV) have been attempted. | No harnesses for any safe API from the challenge list. |
| Excluded categories stay explicitly excluded | 2 | success-criteria.md correctly identifies excluded categories and does not claim coverage of excluded items. | Acceptable at S1 stage. |
| Evidence bundles are reproducible | 3 | All 4 re-run proofs passed. Command template documented. | None - reproducibility is confirmed. |
| Review feedback patterns are incorporated | 1 | Distinct artifact naming is used. Blockers are disclosed. | Generator record not fully updated with evidence. |
| Residual risk is explicit | 2 | 7 blocker categories documented with affected counts. 15+ functions marked UNKNOWN. | UNKNOWN classification acceptable at S1 but needs resolution in S2. |

## Review Pattern Notes

- Prior solution PR review cue from `runtimeverification/mir-semantics#985`:
  keep test and artifact names distinct across challenge directories, and make
  blockers explicit rather than leaving them to inference.
- Reviewer-facing writeups should separate delivered evidence from blocked
  scope so a reviewer can tell what was proven, what was deferred, and why.
- For this challenge, the reviewer will likely expect a countable artifact map
  rather than a narrative-only summary.

## Likely Reviewer Concerns

- The challenge requires 35/47 coverage. Current state is 2/47 with passing proofs.
  The gap is enormous and cannot be closed by harness writing alone - semantic fixes
  are required.
- The 19 harnesses give an impression of significant progress but map to only 2
  upstream functions. A reviewer will immediately flag this discrepancy.
- No semantic rule changes or intrinsic additions were made. The blockers are
  accurately identified but unaddressed.
- No specification book entry exists.

## Verdict

- Current status: `in progress`
- Current verdict: `in progress - major gaps remain`
- Rationale: 19 harnesses pass reproducibly, confirming the `transmute` and
  `transmute_unchecked` intrinsics are well-handled by the existing K semantics.
  However, only 2/47 upstream functions are covered. The 35/47 threshold requires
  both semantic rule additions (TRANSMUTE_CHAR, INTRINSIC_CTPOP, TRANSMUTE_USIZE,
  UNION_EVAL/TRANSMUTE) and harnesses for the actual listed functions (not just the
  two intrinsics). S2 should prioritize TRANSMUTE_CHAR (8 functions), CTPOP (1+
  transitively 3), and investigation of the 15+ UNKNOWN functions.

## Iteration Log

- Bootstrap record created by orchestrator.
- Challenge-specific rubric and evaluator skeleton added; no evidence collected
  yet.
- **Sprint 1 evaluation (2026-04-11)**:
  - Read all 19 harness files and verified assertion correctness.
  - Re-ran 4 proofs (transmute_integers, transmute_unchecked_struct,
    maybeuninit_init_patterns, transmute_enum_variants) - all PASSED.
  - Mapped harnesses to upstream function list: only 2/47 covered.
  - Assessed 7 blocker categories with fix priorities.
  - Identified TRANSMUTE_CHAR as highest-leverage S2 fix (8 functions).
  - Scored all rubric criteria. Overall verdict: in progress with major gaps.
