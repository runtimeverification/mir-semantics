# Allocation Decoding in MIR-Semantics

This module provides functions for decoding byte representations of various allocations into
high-level `Value` representations used by the MIR semantics.

When Rust code contains constants (arrays, structs, enums, etc.), the compiler stores these as
byte sequences in the SMIR JSON output.
The semantics needs to decode these bytes back into structured values that can be operated on at
runtime.
This module contains the decoding functions for different allocation types, handling the conversion
from raw bytes to typed `Value` objects according to Rust's memory layout rules.

```k
requires "../ty.md"
requires "value.md"
requires "numbers.md"

module RT-DECODING
  imports INT
  imports BOOL
  imports MAP

  imports TYPES
  imports RT-VALUE-SYNTAX
  imports RT-NUMBERS
  imports RT-TYPES
```

## Element Decoding Interface to turn bytes into a `Value`

This recursive decoder function checks byte length and decodes the bytes to a `Value` of the given type.

This is currently only defined for `PrimitiveType`s (primitive types in MIR).
and arrays (where layout is trivial).

### Decoding `PrimitiveType`s

```k
  syntax Evaluation ::= #decodeValue ( Bytes , TypeInfo ) [function, total, symbol(decodeValue)]
                      | UnableToDecode  ( Bytes , TypeInfo )    [symbol(Evaluation::UnableToDecode)]
                      | UnableToDecodePy ( msg: String )        [symbol(Evaluation::UnableToDecodePy)]

  // Boolean: should be one byte with value one or zero
  rule #decodeValue(BYTES, typeInfoPrimitiveType(primTypeBool)) => BoolVal(false)
    requires 0 ==Int Bytes2Int(BYTES, LE, Unsigned) andBool lengthBytes(BYTES) ==Int 1

  rule #decodeValue(BYTES, typeInfoPrimitiveType(primTypeBool)) => BoolVal(true)
    requires 1 ==Int Bytes2Int(BYTES, LE, Unsigned) andBool lengthBytes(BYTES) ==Int 1

  // Integer: handled in separate module for numeric operation_s
  rule #decodeValue(BYTES, TYPEINFO) => #decodeInteger(BYTES, #intTypeOf(TYPEINFO))
    requires #isIntType(TYPEINFO) andBool lengthBytes(BYTES) ==Int #elemSize(TYPEINFO)
     [preserves-definedness]

  // TODO Char type
  // rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), typeInfoPrimitiveType(primTypeChar)) => typedValue(Str(...), TY, mutabilityNot)

  // TODO Float decoding: not supported natively in K
```


### Array decoding

Arrays are decoded iteratively, using a known (expected) length or the length of the byte array.

```k
rule #decodeValue(BYTES, typeInfoArrayType(ELEMTY, someTyConst(tyConst(LEN, _))))
      => #decodeArrayAllocation(BYTES, lookupTy(ELEMTY), readTyConstInt(LEN))
  requires isInt(readTyConstInt(LEN))
  [preserves-definedness]

rule #decodeValue(BYTES, typeInfoArrayType(ELEMTY, noTyConst))
      => #decodeSliceAllocation(BYTES, lookupTy(ELEMTY))
```

### Struct decoding

Structs can have non-trivial layouts: field offsets may not match declaration order, and there may be padding.
Decoding is only performed when explicit layout offsets are available; otherwise we leave the term as `UnableToDecode` via the default rule. This avoids incorrectly decoding data when field reordering or padding is present.

When using layout offsets we always return fields in declaration order within the `Aggregate` (variant 0), regardless of the physical order in memory.

```k
// ---------------------------------------------------------------------------
// Struct decoding rules (top level)
// ---------------------------------------------------------------------------
// Use the offsets when they are provided and the input length is sufficient.
rule #decodeValue(BYTES, typeInfoStructType(_, _, TYS, LAYOUT))
      => Aggregate(variantIdx(0), #decodeStructFieldsWithOffsets(BYTES, TYS, #structOffsets(LAYOUT)))
  requires #structOffsets(LAYOUT) =/=K .MachineSizes
   andBool 0 <=Int #neededBytesForOffsets(TYS, #structOffsets(LAYOUT))
   andBool lengthBytes(BYTES) >=Int #neededBytesForOffsets(TYS, #structOffsets(LAYOUT))
  [preserves-definedness]

// ---------------------------------------------------------------------------
// Offsets and helpers (used by the rules above)
// ---------------------------------------------------------------------------
// MachineSize is in bits in the ABI; convert to bytes for slicing.
syntax Int ::= #msBytes ( MachineSize ) [function, total]
rule #msBytes(machineSize(mirInt(NBITS))) => NBITS /Int 8 [preserves-definedness]
rule #msBytes(machineSize(NBITS)) => NBITS /Int 8 [owise, preserves-definedness]

// Minimum number of input bytes required to decode all fields by the chosen offsets.
// Uses builtin maxInt to compute max(offset + size). The lists of types and
// offsets must have the same length; if not, this function returns -1 to signal
// an invalid layout for decoding.
syntax Int ::= #neededBytesForOffsets ( Tys , MachineSizes ) [function, total]
rule #neededBytesForOffsets(.Tys, .MachineSizes) => 0
rule #neededBytesForOffsets(TY TYS, OFFSET OFFSETS)
  => maxInt(#msBytes(OFFSET) +Int #elemSize(lookupTy(TY)), #neededBytesForOffsets(TYS, OFFSETS))
// Any remaining pattern indicates a length mismatch between types and offsets.
rule #neededBytesForOffsets(_, _) => -1 [owise]

// Decode each field at its byte offset and return values in declaration order.
syntax List ::= #decodeStructFieldsWithOffsets ( Bytes , Tys , MachineSizes ) [function, total]
rule #decodeStructFieldsWithOffsets(_, .Tys, _OFFSETS) => .List
rule #decodeStructFieldsWithOffsets(_, _TYS, .MachineSizes) => .List [owise]
rule #decodeStructFieldsWithOffsets(BYTES, TY TYS, OFFSET OFFSETS)
  => ListItem(
       #decodeValue(
         substrBytes(BYTES, #msBytes(OFFSET), #msBytes(OFFSET) +Int #elemSize(lookupTy(TY))),
         lookupTy(TY)
       )
     )
     #decodeStructFieldsWithOffsets(BYTES, TYS, OFFSETS)
  requires lengthBytes(BYTES) >=Int (#msBytes(OFFSET) +Int #elemSize(lookupTy(TY)))
  [preserves-definedness]
```

### Error marker (becomes thunk) for other (unimplemented) cases

All unimplemented cases will become thunks by way of this default rule:

```k
  rule #decodeValue(BYTES, TYPEINFO) => UnableToDecode(BYTES, TYPEINFO) [owise]
```

## Helper function to determine the expected byte length for a type

```k
  // TODO: this function should go into the rt/types.md module
  syntax Int ::= #elemSize ( TypeInfo ) [function, total]
```

Known element sizes for common types:

```k
  // ---- Primitive types ----
  rule #elemSize(typeInfoPrimitiveType(primTypeBool)) => 1
  // Rust `char` is a 32-bit Unicode scalar value
  rule #elemSize(typeInfoPrimitiveType(primTypeChar)) => 4
  rule #elemSize(TYPEINFO) => #bitWidth(#intTypeOf(TYPEINFO)) /Int 8
    requires #isIntType(TYPEINFO)
  // Floating-point sizes
  rule #elemSize(typeInfoPrimitiveType(primTypeFloat(floatTyF16)))  => 2
  rule #elemSize(typeInfoPrimitiveType(primTypeFloat(floatTyF32)))  => 4
  rule #elemSize(typeInfoPrimitiveType(primTypeFloat(floatTyF64)))  => 8
  rule #elemSize(typeInfoPrimitiveType(primTypeFloat(floatTyF128))) => 16
  // `str` is unsized; size only known with metadata (e.g., in fat pointers)
  rule #elemSize(typeInfoPrimitiveType(primTypeStr)) => 0

  // ---- Arrays and slices ----
  rule #elemSize(typeInfoArrayType(ELEM_TY, someTyConst(tyConst(LEN, _))))
    => #elemSize(lookupTy(ELEM_TY)) *Int readTyConstInt(LEN)
  // Slice `[T]` has dynamic size; plain value is unsized
  rule #elemSize(typeInfoArrayType(_ELEM_TY, noTyConst)) => 0

  // ---- thin and fat pointers ----
  rule #elemSize(typeInfoRefType(TY)) => #elemSize(typeInfoPrimitiveType(primTypeUint(uintTyUsize)))
    requires dynamicSize(1) ==K #metadataSize(TY)
  rule #elemSize(typeInfoRefType(_)) => 2 *Int #elemSize(typeInfoPrimitiveType(primTypeUint(uintTyUsize)))
    [owise]
  rule #elemSize(typeInfoPtrType(TY)) => #elemSize(typeInfoPrimitiveType(primTypeUint(uintTyUsize)))
    requires dynamicSize(1) ==K #metadataSize(TY)
  rule #elemSize(typeInfoPtrType(_)) => 2 *Int #elemSize(typeInfoPrimitiveType(primTypeUint(uintTyUsize)))
    [owise]

  // ---- Tuples ----
  // Without layout, approximate as sum of element sizes (ignores padding).
  rule #elemSize(typeInfoTupleType(.Tys)) => 0
  rule #elemSize(typeInfoTupleType(TY TYS))
    => #elemSize(lookupTy(TY)) +Int #elemSize(typeInfoTupleType(TYS))

  // ---- Structs and Enums with layout ----
  rule #elemSize(typeInfoStructType(_, _, _, someLayoutShape(layoutShape(_, _, _, _, SIZE)))) => #msBytes(SIZE)
  rule #elemSize(typeInfoEnumType(_, _, _, _, someLayoutShape(layoutShape(_, _, _, _, SIZE))))   => #msBytes(SIZE)

  // ---- Function item types ----
  // Function items are zero-sized; function pointers are handled by PtrType
  rule #elemSize(typeInfoFunType(_)) => 0

  rule #elemSize(typeInfoVoidType) => 0

  // Fallback to keep the function total for any remaining cases
  rule #elemSize(_) => 0 [owise]

  rule 0 <=Int #elemSize(_) => true [simplification, preserves-definedness]
```


### Enum decoding

Enum decoding is for now restricted to a few special cases.

#### Enums without any fields
If there are no fields, the enum can be decoded by using their data as the discriminant.

```k
  rule #decodeValue(
         BYTES
       , typeInfoEnumType(...
           name: _
         , adtDef: _
         , discriminants: DISCRIMINANTS
         , fields: FIELD_TYPESS
         , layout: _LAYOUT
         )
       )
    => Aggregate(#findVariantIdx(Bytes2Int(BYTES, LE, Unsigned), DISCRIMINANTS), .List)
    requires #noFields(FIELD_TYPESS)

  syntax Bool ::= #noFields(Tyss) [function, total, symbol(noFields)]
  rule #noFields(.Tyss) => true
  rule #noFields(.Tys : REST) => #noFields(REST)
  rule #noFields(_TY _REST_TYS : _REST_TYSS) => false

  syntax VariantIdx ::= #findVariantIdx    ( tag: Int , discriminants: Discriminants )            [function, total, symbol(findVariantIdx)]
                      | #findVariantIdxAux ( tag: Int , discriminants: Discriminants , idx: Int ) [function, total, symbol(findVariantIdxAux)]
                      | err(String)

  rule #findVariantIdx(...
         tag: TAG
       , discriminants: DISCRIMINANTS
       )
    => #findVariantIdxAux(...
         tag: TAG
       , discriminants: DISCRIMINANTS
       , idx: 0
       )

  rule #findVariantIdxAux(...
         tag: _
       , discriminants: .Discriminants
       , idx: _
       )
    => err("Variant index not found")

  rule #findVariantIdxAux(...
         tag: TAG
       , discriminants: discriminant(DISCRIMINANT) _REST
       , idx: IDX
       )
    => variantIdx(IDX)
    requires TAG ==Int DISCRIMINANT

  rule #findVariantIdxAux(...
        tag: TAG
      , discriminants: discriminant(DISCRIMINANT) REST
      , idx: IDX
      )
   => #findVariantIdxAux(...
        tag: TAG
      , discriminants: REST
      , idx: IDX +Int 1
      )
   requires TAG =/=Int DISCRIMINANT

  rule #findVariantIdxAux(...
         tag: TAG
       , discriminants: discriminant(mirInt(DISCRIMINANT)) _REST
       , idx: IDX
       )
    => variantIdx(IDX)
    requires TAG ==Int DISCRIMINANT

  rule #findVariantIdxAux(...
        tag: TAG
      , discriminants: discriminant(mirInt(DISCRIMINANT)) REST
      , idx: IDX
      )
   => #findVariantIdxAux(...
        tag: TAG
      , discriminants: REST
      , idx: IDX +Int 1
      )
   requires TAG =/=Int DISCRIMINANT
```

#### Enums with two variants

Having two variants with possibly zero or one field each is a very common case,
it includes a number of standard library types such as `Option` and `Result`.

The following rules are specialised to the case of encoding an `Option`.
An important distinction here is whether or not the tag is niche-encoded.
If the option holds data that has all-zero as a possible value, a separate tag is used, usually as the first field.
In both cases we expect the tag to be in the single shared field, and the discriminant to be just 0 and 1.

```k
  rule #decodeValue(
         BYTES
       , typeInfoEnumType(...
           name: _
         , adtDef: _
         , discriminants: discriminant(0) discriminant(1) .Discriminants
         , fields: (.Tys : (FIELD_TYPE .Tys) : .Tyss)
         , layout:
            someLayoutShape(layoutShape(...
                fields: fieldsShapeArbitrary(mk(... offsets: machineSize(0) .MachineSizes))
              , variants:
                  variantsShapeMultiple(
                    mk(...
                        tag: scalarInitialized(
                          mk(...
                              value: primitiveInt(mk(... length: TAG_WIDTH, signed: _))
                            , validRange: _RANGE
                          )
                        )
                      , tagEncoding: tagEncodingDirect
                      , tagField: 0
                      , variants: _VARIANTS
                      )
                    )
              , abi: _ABI
              , abiAlign: _ABI_ALIGN
              , size: _SIZE
            ))
         ) #as ENUM_TYPE
       )
    => #decodeOptionTag01(BYTES, TAG_WIDTH, FIELD_TYPE, ENUM_TYPE)

  syntax Evaluation ::= #decodeOptionTag01 ( Bytes , IntegerLength , Ty , TypeInfo ) [function, total]
  // --------------------------------------------------------------------------------------
  rule #decodeOptionTag01(BYTES, _LEN, _TY, _ENUM_TYPE)
    => Aggregate(variantIdx(0), .List)
    requires 0 ==Int BYTES[0] // expect only 0 or 1 as tags, so higher bytes do not matter
    [preserves-definedness]
  rule #decodeOptionTag01(BYTES,  LEN,  TY, _ENUM_TYPE)
    => Aggregate(variantIdx(1), ListItem(#decodeValue(substrBytes(BYTES, #byteLength(LEN), lengthBytes(BYTES)), lookupTy(TY))))
    requires 1 ==Int BYTES[0] // expect only 0 or 1 as tags, so higher bytes do not matter
    [preserves-definedness]
  rule #decodeOptionTag01(BYTES, _LEN, _TY,  ENUM_TYPE)
    => UnableToDecode(BYTES, ENUM_TYPE)
    [owise]

  syntax Int ::= #byteLength ( IntegerLength ) [function, total]
  // -----------------------------------------------------------
  rule #byteLength(integerLengthI8  ) => 1
  rule #byteLength(integerLengthI16 ) => 2
  rule #byteLength(integerLengthI32 ) => 4
  rule #byteLength(integerLengthI64 ) => 8
  rule #byteLength(integerLengthI128) => 16

```

If the option holds a reference or pointer, no extra tag field is required.
The tag is niche-encoded with an all-zero value representing `None`.
However, in this case only a `None` can actually be decoded.
Any pointer or reference would have a very different encoding in KMIR, not a non-zero address.

```k
  rule #decodeValue(
         BYTES
       , typeInfoEnumType(...
           name: _
         , adtDef: _
         , discriminants: discriminant(0) discriminant(1) .Discriminants
         , fields: (.Tys : (_FIELD_TYPE .Tys) : .Tyss)
         , layout:
            someLayoutShape(layoutShape(...
                fields: fieldsShapeArbitrary(mk(... offsets: machineSize(0) .MachineSizes))
              , variants:
                  variantsShapeMultiple(
                    mk(...
                        tag: scalarInitialized(
                          mk(...
                              value: primitivePointer(_ADDR_SPACE)
                            , validRange: wrappingRange(1, 0)
                          )
                        )
                      , tagEncoding: tagEncodingNiche() // FIXME incomplete data model in the AST
                      , tagField: 0
                      , variants: _VARIANTS
                      )
                    )
              , abi: _ABI
              , abiAlign: _ABI_ALIGN
              , size: _SIZE
            ))
         )
       )
    => Aggregate(variantIdx(0), .List)
    requires 0 ==Int Bytes2Int(BYTES, LE, Unsigned)
```

## Array Allocations

Array allocations contain homogeneous elements stored contiguously in memory.
The main function `#decodeArrayAllocation` takes the raw bytes of an array allocation along with
type information and converts it into a `Range` value containing the decoded elements.

The decoding process:
1. Takes the byte array, element type information, and array length
2. Iteratively consumes elements from the front of the byte array
3. Decodes each element according to its type using `#decodeElement`
4. Accumulates the decoded elements into a list
5. Returns a `Range` value containing all elements

The byte consumption approach allows for validation - if there are surplus bytes or insufficient
bytes for the declared array length, the function will get stuck rather than produce incorrect
results.

```k
  syntax Value ::= #decodeArrayAllocation ( Bytes, TypeInfo, Int ) [function]
                   // bytes, element type info, array length, type map (for recursion)

  rule #decodeArrayAllocation(BYTES, ELEMTYPEINFO, LEN)
    => Range(#decodeArrayElements(BYTES, ELEMTYPEINFO, LEN, .List))

  syntax List ::= #decodeArrayElements ( Bytes, TypeInfo, Int, List ) [function]
                  // bytes, elem type info, remaining length, accumulated list

  rule #decodeArrayElements(BYTES, _ELEMTYPEINFO, LEN, ACC)
    => ACC
    requires LEN <=Int 0
     andBool lengthBytes(BYTES) ==Int 0  // exact match - no surplus bytes
    [preserves-definedness]

  rule #decodeArrayElements(BYTES, ELEMTYPEINFO, LEN, ACC)
    => #decodeArrayElements(
         substrBytes(BYTES, #elemSize(ELEMTYPEINFO), lengthBytes(BYTES)),
         ELEMTYPEINFO,
         LEN -Int 1,
         ACC ListItem(#decodeValue(
           substrBytes(BYTES, 0, #elemSize(ELEMTYPEINFO)),
           ELEMTYPEINFO
         ))
       )
    requires LEN >Int 0
     andBool lengthBytes(BYTES) >=Int #elemSize(ELEMTYPEINFO)  // enough bytes remaining
    [preserves-definedness]
```

## Slice Allocations

Slices are arrays with dynamic length.
The `#decodeSliceAllocation` function computes the array length by dividing the total byte length
by the element size, then uses the same element-by-element decoding approach as arrays.

```k
  syntax Value ::= #decodeSliceAllocation ( Bytes, TypeInfo ) [function]
  // -------------------------------------------------------------------
  rule #decodeSliceAllocation(BYTES, ELEMTYPEINFO)
    => Range(#decodeArrayElements(
                BYTES,
                ELEMTYPEINFO,
                lengthBytes(BYTES) /Int #elemSize(ELEMTYPEINFO),
                .List
             )
      )
    requires lengthBytes(BYTES) %Int #elemSize(ELEMTYPEINFO) ==Int 0  // element size divides cleanly
     andBool 0 <Int #elemSize(ELEMTYPEINFO)
    [preserves-definedness]
```

```k
endmodule
```
