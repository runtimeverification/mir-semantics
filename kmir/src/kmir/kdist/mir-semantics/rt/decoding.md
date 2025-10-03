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
  syntax Evaluation ::= #decodeValue ( Bytes , TypeInfo , Map ) [function, total, symbol(decodeValue)]
                      | UnableToDecode  ( Bytes , TypeInfo )    [symbol(Evaluation::UnableToDecode)]
                      | UnableToDecodePy ( msg: String )        [symbol(Evaluation::UnableToDecodePy)]

  // Boolean: should be one byte with value one or zero
  rule #decodeValue(BYTES, typeInfoPrimitiveType(primTypeBool), _TYPEMAP) => BoolVal(false)
    requires 0 ==Int Bytes2Int(BYTES, LE, Unsigned) andBool lengthBytes(BYTES) ==Int 1

  rule #decodeValue(BYTES, typeInfoPrimitiveType(primTypeBool), _TYPEMAP) => BoolVal(true)
    requires 1 ==Int Bytes2Int(BYTES, LE, Unsigned) andBool lengthBytes(BYTES) ==Int 1

  // Integer: handled in separate module for numeric operation_s
  rule #decodeValue(BYTES, TYPEINFO, TYPEMAP) => #decodeInteger(BYTES, #intTypeOf(TYPEINFO))
    requires #isIntType(TYPEINFO) andBool lengthBytes(BYTES) ==Int #elemSize(TYPEINFO, TYPEMAP)
     [preserves-definedness]

  // TODO Char type
  // rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), typeInfoPrimitiveType(primTypeChar)) => typedValue(Str(...), TY, mutabilityNot)

  // TODO Float decoding: not supported natively in K
```


### Array decoding

Arrays are decoded iteratively, using a known (expected) length or the length of the byte array.

```k
rule #decodeValue(BYTES, typeInfoArrayType(ELEMTY, someTyConst(tyConst(LEN, _))), TYPEMAP)
      => #decodeArrayAllocation(BYTES, {TYPEMAP[ELEMTY]}:>TypeInfo, readTyConstInt(LEN, TYPEMAP), TYPEMAP)
  requires ELEMTY in_keys(TYPEMAP)
   andBool isTypeInfo(TYPEMAP[ELEMTY])
   andBool isInt(readTyConstInt(LEN, TYPEMAP))
  [preserves-definedness]

rule #decodeValue(BYTES, typeInfoArrayType(ELEMTY, noTyConst), TYPEMAP)
      => #decodeSliceAllocation(BYTES, {TYPEMAP[ELEMTY]}:>TypeInfo, TYPEMAP)
  requires ELEMTY in_keys(TYPEMAP)
   andBool isTypeInfo(TYPEMAP[ELEMTY])
```

### Error marker (becomes thunk) for other (unimplemented) cases

All unimplemented cases will become thunks by way of this default rule:

```k
  rule #decodeValue(BYTES, TYPEINFO, _TYPEMAP) => UnableToDecode(BYTES, TYPEINFO) [owise]
```

## Helper function to determine the expected byte length for a type

```k
  // TODO: this function should go into the rt/types.md module
  syntax Int ::= #elemSize ( TypeInfo , Map ) [function]
```

Known element sizes for common types:

```k
  rule #elemSize(typeInfoPrimitiveType(primTypeBool), _) => 1
  rule #elemSize(TYPEINFO, _) => #bitWidth(#intTypeOf(TYPEINFO)) /Int 8
    requires #isIntType(TYPEINFO)

  rule #elemSize(typeInfoArrayType(ELEM_TY, someTyConst(tyConst(LEN, _))), TYPEMAP)
    => #elemSize({TYPEMAP[ELEM_TY]}:>TypeInfo, TYPEMAP) *Int readTyConstInt(LEN, TYPEMAP)
    requires ELEM_TY in_keys(TYPEMAP)

  // thin and fat pointers
  rule #elemSize(typeInfoRefType(TY), TYPEMAP) => #elemSize(typeInfoPrimitiveType(primTypeUint(uintTyUsize)), .Map)
    requires dynamicSize(1) ==K #metadata(TY, TYPEMAP)
  rule #elemSize(typeInfoRefType(_), _TYPEMAP) => 2 *Int #elemSize(typeInfoPrimitiveType(primTypeUint(uintTyUsize)), .Map)
    [owise]
  rule #elemSize(typeInfoPtrType(TY), TYPEMAP) => #elemSize(typeInfoPrimitiveType(primTypeUint(uintTyUsize)), .Map)
    requires dynamicSize(1) ==K #metadata(TY, TYPEMAP)
  rule #elemSize(typeInfoPtrType(_), _TYPEMAP) => 2 *Int #elemSize(typeInfoPrimitiveType(primTypeUint(uintTyUsize)), .Map)
    [owise]

  rule #elemSize(typeInfoVoidType, _) => 0

  // FIXME can only use size from layout here. Requires adding layout first.
  // Enum, Struct, Tuple,

  rule 0 <=Int #elemSize(_, _) => true [simplification, preserves-definedness]
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
       , _TYPES
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
  syntax Value ::= #decodeArrayAllocation ( Bytes, TypeInfo, Int , Map ) [function]
                   // bytes, element type info, array length, type map (for recursion)

  rule #decodeArrayAllocation(BYTES, ELEMTYPEINFO, LEN, TYPEMAP)
    => Range(#decodeArrayElements(BYTES, ELEMTYPEINFO, LEN, TYPEMAP, .List))
    requires notBool #isIntType(ELEMTYPEINFO)

  rule #decodeArrayAllocation(BYTES, ELEMTYPEINFO, LEN, TYPEMAP)
    => RangeInteger(LEN, #bitWidth(#intTypeOf(ELEMTYPEINFO)), false, #decodeUints(BYTES, 0, LEN, #elemSize(ELEMTYPEINFO, TYPEMAP)))
    requires #isIntType(ELEMTYPEINFO)
     andBool isUintTy(#intTypeOf(ELEMTYPEINFO))
     andBool lengthBytes(BYTES) %Int #elemSize(ELEMTYPEINFO, TYPEMAP) ==Int 0

  syntax ListInt ::= #decodeUints ( Bytes , Int , Int , Int ) [function]
  rule #decodeUints(_, _, _, _) => .Ints [owise]
  rule #decodeUints(BYTES:Bytes, N, LEN, WIDTH)
    => Bytes2Int(substrBytes(BYTES, N *Int WIDTH, (N +Int 1) *Int WIDTH), LE, Signed)
       #decodeUints(BYTES, N +Int 1, LEN, WIDTH)
    requires 0 <=Int N andBool 0 <Int WIDTH andBool (N +Int 1) *Int WIDTH <=Int lengthBytes(BYTES)
    [preserves-definedness]

  syntax List ::= #decodeArrayElements ( Bytes, TypeInfo, Int, Map, List ) [function]
                  // bytes, elem type info, remaining length, accumulated list

  rule #decodeArrayElements(BYTES, _ELEMTYPEINFO, LEN, _TYPEMAP, ACC)
    => ACC
    requires LEN <=Int 0
     andBool lengthBytes(BYTES) ==Int 0  // exact match - no surplus bytes
    [preserves-definedness]

  rule #decodeArrayElements(BYTES, ELEMTYPEINFO, LEN, TYPEMAP, ACC)
    => #decodeArrayElements(
         substrBytes(BYTES, #elemSize(ELEMTYPEINFO, TYPEMAP), lengthBytes(BYTES)),
         ELEMTYPEINFO,
         LEN -Int 1,
         TYPEMAP,
         ACC ListItem(#decodeValue(
           substrBytes(BYTES, 0, #elemSize(ELEMTYPEINFO, TYPEMAP)),
           ELEMTYPEINFO,
           TYPEMAP
         ))
       )
    requires LEN >Int 0
     andBool lengthBytes(BYTES) >=Int #elemSize(ELEMTYPEINFO, TYPEMAP)  // enough bytes remaining
    [preserves-definedness]
```

## Slice Allocations

Slices are arrays with dynamic length.
The `#decodeSliceAllocation` function computes the array length by dividing the total byte length
by the element size, then uses the same element-by-element decoding approach as arrays.

```k
  syntax Value ::= #decodeSliceAllocation ( Bytes, TypeInfo , Map ) [function]
  // -------------------------------------------------------------------
  rule #decodeSliceAllocation(BYTES, ELEMTYPEINFO, TYPEMAP)
    => Range(#decodeArrayElements(
                BYTES,
                ELEMTYPEINFO,
                lengthBytes(BYTES) /Int #elemSize(ELEMTYPEINFO, TYPEMAP),
                TYPEMAP,
                .List
             )
      )
    requires lengthBytes(BYTES) %Int #elemSize(ELEMTYPEINFO, TYPEMAP) ==Int 0  // element size divides cleanly
     andBool 0 <Int #elemSize(ELEMTYPEINFO, TYPEMAP)
    [preserves-definedness]
```

```k
endmodule
```
