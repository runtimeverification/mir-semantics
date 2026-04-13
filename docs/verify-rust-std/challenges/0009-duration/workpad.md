---
challenge: "0009-duration"
status: investigating-blocker
last_updated: 2026-04-11
---

## Niche-Encoded Option<Duration> Blocker Investigation

### Problem Statement

4 overflow/underflow harnesses are BLOCKED because KMIR cannot decode constant bytes into
`Option<Duration>` when the encoding uses niche optimization (`TagEncoding::Niche`).

Affected harnesses:
- `checked_add_overflow.rs`
- `checked_sub_underflow.rs`
- `checked_mul_overflow.rs`
- `checked_div_zero.rs`

### Exact Error

The proof terminates at depth 233 with a thunk wrapping:

```
thunk(Evaluation::UnableToDecode(
  b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\xca\x9a;\x00\x00\x00\x00",
  TypeInfo::EnumType("std::option::Option<std::time::Duration>", ...)
))
```

The 16 bytes decode as:
- Bytes 0-7: `u64 secs = 0`
- Bytes 8-11: `u32 nanos = 1_000_000_000` (0x3B9ACA00) -- the niche value
- Bytes 12-15: padding = 0

This represents `Option<Duration>::None`. The niche is in the `nanos` field:
valid `Duration.nanos` values are `[0, 999_999_999]`, so `nanos == 1_000_000_000`
signals the `None` variant.

### Layout Analysis

The layout from SMIR includes full niche encoding info:

```
VariantsShape::Multiple(
  mk(
    tag: Scalar::Initialized(
      mk(
        value: Primitive::Int(mk(I32, unsigned)),
        validRange: wrappingRange(0, 1000000000)
      )
    ),
    tagEncoding: TagEncoding::Niche,
    tagField: 0,
    variants: [
      layoutShape(Arbitrary(offsets: []), Single(variantIdx(0)), ...),  // None
      layoutShape(Arbitrary(offsets: [...]), Single(variantIdx(1)), ...) // Some
    ]
  )
)
```

Key observations:
- `TagEncoding::Niche` (not `tagEncodingDirect`)
- `tagField: 0` -- the niche is in field 0 of the enclosing struct (the `nanos` field of Duration)
- `validRange: wrappingRange(0, 1_000_000_000)` -- values outside this range indicate `None`
- Variant 0 = `None` (no fields), variant 1 = `Some(Duration)` (has fields)

### Diff: 0009-duration vs 0012-nonzero rt/data.md

The 0012-nonzero branch adds niche-encoded `Option<NonZero<T>>` handling in `rt/data.md`.
Key additions:

1. **Transmute cast rules** (not decoding rules) for `Option<NonZero<T>>`:
   - `Integer -> Option<NonZero<T>>`: zero maps to `None`, nonzero maps to `Some(NonZero(v))`
   - `Option<NonZero<T>> -> Integer`: `Some(v)` unwraps, `None` maps to 0
   - Uses name-based matching: `#isOptionNonZero` checks for `"std::option::Option<std::num::NonZero<"`

2. **Multi-layer transparent wrapper cast rules**: recursive unwrap/wrap for nested newtypes

3. **Union field read reinterpretation**: `#unionFieldRead` for cross-field type casts

4. **Other 0012 changes**: operandMove semantics differ (0012 writes `Moved` back; 0009 does not),
   ConstantIndex projection on Aggregate/Range, removed `#cast(Moved)` propagation rule,
   relaxed MaybeUninit transmute guard.

**Crucially, all niche-encoding rules in 0012 operate on `#cast` (transmute), not on `#decodeValue`.
The decoding.md files are identical between branches.**

### Assessment: Can the 0012-nonzero Rules Be Adapted for Option<Duration>?

**No, not directly.** The blockers are fundamentally different:

| Aspect | Option<NonZero<T>> (0012) | Option<Duration> (0009) |
|--------|---------------------------|--------------------------|
| Where stuck | `#cast` (transmute at runtime) | `#decodeValue` (constant byte decoding) |
| Niche value | 0 (zero is the niche) | 1_000_000_000 (out-of-range nanos) |
| Layout | Same size as T (single integer) | Compound struct (u64 + u32 + padding = 16 bytes) |
| Tag field | The entire value IS the tag | Tag is embedded in field 0 of a sub-struct |
| Valid range | wrappingRange(1, 0) meaning "all nonzero" | wrappingRange(0, 1000000000) meaning "0..=999999999" |
| Name pattern | `std::option::Option<std::num::NonZero<` | `std::option::Option<std::time::Duration>` |

### What Would Fix This

The fix needs a **new `#decodeValue` rule** in `decoding.md` (or inlined in `data.md`) that handles
`tagEncodingNiche` enum layouts. The rule must:

1. Match on `typeInfoEnumType` with `TagEncoding::Niche` layout
2. Read the niche field bytes at the `tagField` offset
3. Compare against the `validRange` to determine the variant:
   - If the niche field value is outside `validRange`, this is the `None` variant (variant 0)
   - If inside `validRange`, this is the `Some` variant (variant 1) -- decode all fields
4. For the `None` case: return `Aggregate(variantIdx(0), .List)`
5. For the `Some` case: decode using variant 1's field offsets from `VARIANT_LAYOUTS`

A sketch of the K rule:

```k
  // Niche-encoded enum decoding (e.g., Option<Duration>)
  rule #decodeValue(
         BYTES
       , typeInfoEnumType(...
           name: _
         , adtDef: _
         , discriminants: _DISCRIMINANTS
         , fields: FIELD_TYPESS
         , layout:
            someLayoutShape(layoutShape(...
                fields: _FIELDS
              , variants:
                  variantsShapeMultiple(
                    mk(...
                        tag: scalarInitialized(
                          mk(...
                              value: primitiveInt(mk(... length: TAG_WIDTH, signed: _))
                            , validRange: wrappingRange(RANGE_START, RANGE_END)
                          )
                        )
                      , tagEncoding: tagEncodingNiche()
                      , tagField: TAG_FIELD_IDX
                      , variants: VARIANT_LAYOUTS
                      )
                    )
              , abi: _ABI
              , abiAlign: _ABI_ALIGN
              , size: _SIZE
            ))
         ) #as ENUM_TYPE
       )
    => #decodeEnumNicheFields(
         BYTES,
         TAG_VALUE,                    // extracted niche field value
         RANGE_START, RANGE_END,
         FIELD_TYPESS,
         VARIANT_LAYOUTS,
         ENUM_TYPE
       )
    requires notBool #noFields(FIELD_TYPESS)
     andBool ...  // TAG_VALUE = read niche field from BYTES
```

### Complexity Assessment

- **Moderate difficulty.** The layout data is already fully available from SMIR (unlike what the 0012 comment says about "TagEncoding::Niche data not yet fully represented in K").
- The tricky part is correctly computing which variant the niche value maps to. For the common 2-variant case (`Option<T>`), it is straightforward: niche outside range -> variant 0 (None), inside range -> variant 1 (Some).
- For the general N-variant case, the niche value encodes the "unrepresented" variant index, which requires more complex discriminant math. But for this challenge, the 2-variant Option case suffices.
- Estimated effort: 1-2 hours of K rule implementation + testing.
- This is a new `#decodeValue` rule, completely orthogonal to the 0012-nonzero transmute rules.

### Recommendation

1. Implement a niche-encoded enum decoding rule in `decoding.md` for the 2-variant `Option<T>` case.
2. This is independent of the 0012-nonzero work and should be a separate PR.
3. The 0012-nonzero transmute rules (for `Option<NonZero<T>>`) are NOT needed for this fix and should not be ported.
4. Once implemented, all 4 blocked harnesses should pass, completing the 0009-duration challenge.
