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
requires "../alloc.md"

module RT-DECODING
  imports BOOL
  imports MAP

  imports TYPES
  imports ALLOC
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
  syntax Evaluation ::= #decodeValue ( Bytes , TypeInfo , Map ) [function, total]
                      | UnableToDecode( Bytes , TypeInfo )

  // Boolean: should be one byte with value one or zero
  rule #decodeValue(BYTES, typeInfoPrimitiveType(primTypeBool), _TYPEMAP) => BoolVal(false)
    requires 0 ==Int Bytes2Int(BYTES, LE, Unsigned) andBool lengthBytes(BYTES) ==Int 1

  rule #decodeValue(BYTES, typeInfoPrimitiveType(primTypeBool), _TYPEMAP) => BoolVal(true)
    requires 1 ==Int Bytes2Int(BYTES, LE, Unsigned) andBool lengthBytes(BYTES) ==Int 1

  // Integer: handled in separate module for numeric operation_s
  rule #decodeValue(BYTES, TYPEINFO, _TYPEMAP) => #decodeInteger(BYTES, #intTypeOf(TYPEINFO))
    requires #isIntType(TYPEINFO) andBool lengthBytes(BYTES) ==Int #elemSize(TYPEINFO)
     [preserves-definedness]

  // TODO Char type
  // rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), typeInfoPrimitiveType(primTypeChar)) => typedValue(Str(...), TY, mutabilityNot)

  // TODO Float decoding: not supported natively in K
```


### Array decoding

Arrays are decoded iteratively, using a known (expected) length or the length of the byte array.

```k
rule #decodeValue(BYTES, typeInfoArrayType(ELEMTY, someTyConst(tyConst(LEN, _))), TYPEMAP)
      => #decodeArrayAllocation(BYTES, {TYPEMAP[ELEMTY]}:>TypeInfo, readTyConstInt(LEN, TYPEMAP))
  requires ELEMTY in_keys(TYPEMAP)
   andBool isTypeInfo(TYPEMAP[ELEMTY])
   andBool isInt(readTyConstInt(LEN, TYPEMAP))
  [preserves-definedness]

rule #decodeValue(BYTES, typeInfoArrayType(ELEMTY, noTyConst), TYPEMAP)
      => #decodeSliceAllocation(BYTES, {TYPEMAP[ELEMTY]}:>TypeInfo)
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
  syntax Int ::= #elemSize ( TypeInfo ) [function]
```

Known element sizes for common types:

```k
  rule #elemSize(typeInfoPrimitiveType(primTypeBool)) => 1
  rule #elemSize(TYPEINFO) => #bitWidth(#intTypeOf(TYPEINFO)) /Int 8
    requires #isIntType(TYPEINFO)

  rule 0 <=Int #elemSize(_) => true [simplification, preserves-definedness]
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
                   // bytes, element type info, array length

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
           ELEMTYPEINFO,
           .Map // HACK
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
    => Range(#decodeArrayElements(BYTES, ELEMTYPEINFO,
                                   lengthBytes(BYTES) /Int #elemSize(ELEMTYPEINFO), .List))
    requires lengthBytes(BYTES) %Int #elemSize(ELEMTYPEINFO) ==Int 0  // element size divides cleanly
     andBool 0 <Int #elemSize(ELEMTYPEINFO)
    [preserves-definedness]
```

# Decoding the allocated constants into a memory map

When the program starts, all allocated constants are stored in the `<memory>` cell in the configuration,
as a mapping of `AllocId -> Value`, decoding the allocations to values using the above functions.

Besides actual byte allocations, we often find allocations with provenance,
as slim or fat pointers pointing to other static allocations.
One example of this is allocated error strings, whose length is stored in a fat pointer that is itself an allocated constant.


The basic decoding function is very similar to `#decodeConstant` but returns its result as a singleton `Map` instead of a mere value.

```k
  syntax Map ::= #decodeAlloc ( AllocId , Ty , Allocation , Map ) [function] // returns AllocId |-> Value
  // ----------------------------------------------------------
  rule #decodeAlloc(ID, TY, allocation(BYTES, provenanceMap(.ProvenanceMapEntries), _ALIGN, _MUT), TYPEMAP)
      => ID |-> #decodeValue(BYTES, {TYPEMAP[TY]}:>TypeInfo, TYPEMAP)
    requires TY in_keys(TYPEMAP)
     andBool isTypeInfo(TYPEMAP[TY])

  rule #decodeAlloc(
          ID,
          _TY,
          allocation(_BYTES, provenanceMap(provenanceMapEntry(_OFFSET, REF_ID) ), _ALIGN, _MUT),
          _TYPEMAP 
          // FIXME this is only correct for special cases of a single provenance map entry
          // FIXME more general cases must consider the BYTES and insert AllocRef data where needed according to the provenance map (also considering layout of the target type)
        )
      => ID |-> AllocRef(REF_ID, dynamicSize(0))
        // FIXME: if length(BYTES) ==Int 16 decode 2nd half as size.
        // Otherwise query type information for static size and insert it.
```

The entire set of `GlobalAllocs` is decoded by iterating over the list.
It is assumed that the given `Ty -> TypeInfo` map contains all types required.

```k
  syntax Map ::= #decodeAllocs ( GlobalAllocs , Map )       [function, total, symbol("decodeAllocs")] // AllocId |-> Thing
               | #decodeAllocs ( Map , GlobalAllocs , Map ) [function, total] // accumulating version
  // -----------------------------------------------------------------------------------------------
  rule #decodeAllocs(ALLOCS, TYPEMAP) => #decodeAllocs(.Map, ALLOCS, TYPEMAP)

  rule #decodeAllocs(ACCUM, .GlobalAllocs, _TYPEMAP) => ACCUM
  rule #decodeAllocs(ACCUM, globalAllocEntry(ID, TY, Memory(ALLOC)) ALLOCS, TYPEMAP)
      => #decodeAllocs(ACCUM #decodeAlloc(ID, TY, ALLOC, TYPEMAP), ALLOCS, TYPEMAP)
    requires TY in_keys(TYPEMAP)
    [preserves-definedness]
```

Non-`Memory` allocs are simply stored as raw data as they cannot be handled at the moment.
This ensures that the function is total (anyway lookups require constraining the sort).

```k
  syntax AllocData ::= Value | AllocData ( Ty , GlobalAllocKind )

  rule #decodeAllocs(ACCUM, globalAllocEntry(ID, TY, OTHER) ALLOCS, TYPEMAP)
      => #decodeAllocs(ACCUM ID |-> AllocData(TY, OTHER), ALLOCS, TYPEMAP)
    [owise]
```

```k
endmodule
```
