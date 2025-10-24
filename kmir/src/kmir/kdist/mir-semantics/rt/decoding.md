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
The decoder follows a two-step strategy:
- Prefer explicit offsets from the struct's layout to slice each field out of the byte array.
- Fallback to a simple sequential split only when there is no layout and the total length matches the sum of field sizes (i.e., no padding).

When using layout offsets we always return fields in declaration order within the `Aggregate` (variant 0), regardless of the physical order in memory.

```k
// ---------------------------------------------------------------------------
// Struct decoding rules (top level)
// ---------------------------------------------------------------------------
// Case 1 (layout offsets present): use the offsets when they are provided
// and the input length is sufficient. Distinguished purely via `requires`.
rule #decodeValue(BYTES, typeInfoStructType(_, _, TYS, LAYOUT))
      => Aggregate(variantIdx(0), #decodeStructFieldsWithOffsets(BYTES, TYS, #structOffsets(LAYOUT)))
  requires #structOffsets(LAYOUT) =/=K .MachineSizes
   andBool lengthBytes(BYTES) >=Int #neededBytesForOffsets(TYS, #structOffsets(LAYOUT))
  [preserves-definedness]

// Case 2 (no layout): use sequential decoding with no padding allowed.
rule #decodeValue(BYTES, typeInfoStructType(_, _, TYS, noLayoutShape))
      => Aggregate(variantIdx(0), #decodeStructFields(BYTES, TYS))
  requires lengthBytes(BYTES) ==Int #sumElemSizes(TYS)
  [preserves-definedness]

// ---------------------------------------------------------------------------
// Offsets and helpers (used by the rules above)
// ---------------------------------------------------------------------------
// MachineSize is in bits in the ABI; convert to bytes for slicing.
syntax Int ::= #msBytes ( MachineSize ) [function, total]
rule #msBytes(machineSize(mirInt(NBITS))) => NBITS /Int 8 [preserves-definedness]
rule #msBytes(machineSize(NBITS)) => NBITS /Int 8 [owise, preserves-definedness]

// Extract field offsets from the struct layout when available (Arbitrary only).
syntax MachineSizes ::= #structOffsets ( MaybeLayoutShape ) [function, total]
rule #structOffsets(someLayoutShape(layoutShape(fieldsShapeArbitrary(mk(OFFSETS)), _, _, _, _))) => OFFSETS
rule #structOffsets(noLayoutShape) => .MachineSizes
rule #structOffsets(_) => .MachineSizes [owise]

// Minimum number of input bytes required to decode all fields by the chosen offsets.
// Uses builtin maxInt to compute max(offset + size). When offsets are absent
// (empty list), this collapses to the exact sequential size (#sumElemSizes),
// which matches the semantics of our sequential decoding helper.
syntax Int ::= #neededBytesForOffsets ( Tys , MachineSizes ) [function, total]
rule #neededBytesForOffsets(.Tys, .MachineSizes) => 0
rule #neededBytesForOffsets(TY TYS, OFFSET OFFSETS)
  => maxInt(#msBytes(OFFSET) +Int #elemSize(lookupTy(TY)), #neededBytesForOffsets(TYS, OFFSETS))
rule #neededBytesForOffsets(TYS, .MachineSizes) => #sumElemSizes(TYS)
rule #neededBytesForOffsets(.Tys, _OFFSETS) => 0 [owise]

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

// Sequential helper (used when no layout is available and there is no padding).
syntax List ::= #decodeStructFields ( Bytes , Tys ) [function, total]
rule #decodeStructFields(BYTES, .Tys) => .List
  requires lengthBytes(BYTES) ==Int 0
  [preserves-definedness]

rule #decodeStructFields(BYTES, TY TYS)
  => ListItem(
       #decodeValue(
         substrBytes(BYTES, 0, #elemSize(lookupTy(TY))),
         lookupTy(TY)
       )
     )
     #decodeStructFields(substrBytes(BYTES, #elemSize(lookupTy(TY)), lengthBytes(BYTES)), TYS)
  requires lengthBytes(BYTES) >=Int #elemSize(lookupTy(TY))
  [preserves-definedness]

syntax Int  ::= #sumElemSizes      ( Tys )        [function, total]
rule #sumElemSizes(.Tys) => 0
rule #sumElemSizes(TY TYS) => #elemSize(lookupTy(TY)) +Int #sumElemSizes(TYS)
```

### Error marker (becomes thunk) for other (unimplemented) cases

All unimplemented cases will become thunks by way of this default rule:

```k
  rule #decodeValue(BYTES, TYPEINFO) => UnableToDecode(BYTES, TYPEINFO) [owise]
```

## Helper function to determine the expected byte length for a type

```k
  // TODO: this function should go into the rt/types.md module
  syntax Int ::= #elemSize ( TypeInfo ) [function]
```

Known element sizes for common types:

```k
  rule #elemSize(typeInfoPrimitiveType(primTypeBool)) => 1
  rule #elemSize(TYPEINFO) => #bitWidth(#intTypeOf(TYPEINFO)) /Int 8
    requires #isIntType(TYPEINFO)

  rule #elemSize(typeInfoArrayType(ELEM_TY, someTyConst(tyConst(LEN, _))))
    => #elemSize(lookupTy(ELEM_TY)) *Int readTyConstInt(LEN)

  // thin and fat pointers
  rule #elemSize(typeInfoRefType(TY)) => #elemSize(typeInfoPrimitiveType(primTypeUint(uintTyUsize)))
    requires dynamicSize(1) ==K #metadataSize(TY)
  rule #elemSize(typeInfoRefType(_)) => 2 *Int #elemSize(typeInfoPrimitiveType(primTypeUint(uintTyUsize)))
    [owise]
  rule #elemSize(typeInfoPtrType(TY)) => #elemSize(typeInfoPrimitiveType(primTypeUint(uintTyUsize)))
    requires dynamicSize(1) ==K #metadataSize(TY)
  rule #elemSize(typeInfoPtrType(_)) => 2 *Int #elemSize(typeInfoPrimitiveType(primTypeUint(uintTyUsize)))
    [owise]

  rule #elemSize(typeInfoVoidType) => 0

  // FIXME can only use size from layout here. Requires adding layout first.
  // Enum, Struct, Tuple,

  rule 0 <=Int #elemSize(_) => true [simplification, preserves-definedness]
```


### Enum decoding

Enum decoding is for now restricted to enums wihout any fields.

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
