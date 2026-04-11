# Challenge 0001: Challenge 1: Verify `core` transmuting methods

Reference inputs:

- Challenge page: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0001-core-transmutation.md
- Tracking issue: [#19](https://github.com/model-checking/verify-rust-std/issues/19)
- Tracking issue state at bootstrap: `CLOSED`

Execution context:

- Branch: `verify-rust-std/reexec-0001-core-transmutation`
- Worktree: `/home/zhaoji/projs/mir-semantics-vrs/challenges/0001-core-transmutation`
- Branch-local coverage map: `docs/verify-rust-std/challenges/0001-core-transmutation/success-criteria.md`

## Proof Harnesses (all PASSED)

### transmute (core::intrinsics)

- `transmute_roundtrip.rs` - Byte-array <-> u64 roundtrip with endianness checks
- `transmute_integers.rs` - Integer roundtrips: u32/i32, u16/i16, u64/i64, u8/i8, usize/isize
- `transmute_array_bytes.rs` - Byte array <-> u32/u16 conversions with endianness checks
- `transmute_multi_width.rs` - u128/i128, i32/i64 byte roundtrips
- `transmute_roundtrip_comprehensive.rs` - All integer widths byte roundtrips
- `transmute_same_type.rs` - Identity transmute (same type)
- `transmute_wrapper_structs.rs` - T <-> single-field wrapper struct
- `transmute_struct_fields.rs` - repr(transparent) struct roundtrips
- `transmute_enum.rs` - u8 -> fieldless enum (Color, Status)
- `transmute_enum_variants.rs` - Extended enum transmute (Direction, Opcode, Bool)

### transmute_unchecked (core::intrinsics)

- `transmute_unchecked_integers.rs` - Integer roundtrips via transmute_unchecked
- `transmute_unchecked_maybeuninit_int.rs` - T -> MaybeUninit<T> via transmute_unchecked
- `transmute_unchecked_struct.rs` - struct -> MaybeUninit<struct> via transmute_unchecked

### MaybeUninit methods (core::mem)

- `maybeuninit_basic.rs` - new + assume_init for u32, i64, u8, bool, usize
- `maybeuninit_write_assume_init.rs` - Nested new/assume_init, i8, i16, i32, u128
- `maybeuninit_assume_init_ref.rs` - Reading via assume_init_ref
- `maybeuninit_assume_init_mut.rs` - Reading via assume_init_mut
- `maybeuninit_struct.rs` - MaybeUninit with Point, Triple, Wrapper structs
- `maybeuninit_init_patterns.rs` - MaybeUninit with Option, Result, arrays

## Running Proofs

```bash
cd /home/zhaoji/projs/mir-semantics-vrs/challenges/0001-core-transmutation/
# Run a single proof
uv --directory kmir run -- kmir prove \
    kmir/src/tests/integration/data/verify-rust-std/0001-core-transmutation/<file>.rs \
    --verbose --terminate-on-thunk --proof-dir /tmp/kmir-0001-<name> --reload --fail-fast
```

## Known Blockers

- **TRANSMUTE_CHAR**: No rule for transmute u32 -> char (blocks from_u32_unchecked, AsciiChar)
- **TRANSMUTE_USIZE**: No rule for transmute usize -> Alignment newtype (blocks Layout)
- **UNION_EVAL**: #evalUnion stuck when accessing MaybeUninit array elements
- **INTRINSIC_CTPOP**: Missing ctpop intrinsic (blocks Alignment::new)
- **STRING_DECODE**: #decodeConstant stuck on string allocations (blocks str::as_bytes)
