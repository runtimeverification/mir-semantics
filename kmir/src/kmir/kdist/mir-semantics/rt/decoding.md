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
```

## Element Decoding Interface to turn bytes into a `Value`

This recursive decoder function checks byte length and decodes the bytes to a `Value` of the given type.

This is currently only defined for `PrimitiveType`s (primitive types in MIR).
and arrays (where layout is trivial).

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
  syntax Value ::= #decodeArrayAllocation ( Bytes, Ty, TypeInfo, Int ) [function]
                   // bytes, element type, element type info, array length

  rule #decodeArrayAllocation(BYTES, ELEMTY, ELEMTYPEINFO, LEN)
    => Range(#decodeArrayElements(BYTES, ELEMTY, ELEMTYPEINFO, LEN, .List))

  syntax List ::= #decodeArrayElements ( Bytes, Ty, TypeInfo, Int, List ) [function]
                  // bytes, elem type, elem type info, remaining length, accumulated list

  rule #decodeArrayElements(BYTES, _ELEMTY, _ELEMTYPEINFO, LEN, ACC)
    => ACC
    requires LEN <=Int 0
     andBool lengthBytes(BYTES) ==Int 0  // exact match - no surplus bytes
    [preserves-definedness]

  rule #decodeArrayElements(BYTES, ELEMTY, ELEMTYPEINFO, LEN, ACC) 
    => #decodeArrayElements(
         substrBytes(BYTES, #elemSize(ELEMTYPEINFO), lengthBytes(BYTES)), 
         ELEMTY, 
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
  syntax Value ::= #decodeSliceAllocation ( Bytes, Ty, TypeInfo ) [function]
                   // bytes, element type, element type info

  rule #decodeSliceAllocation(BYTES, ELEMTY, ELEMTYPEINFO)
    => Range(#decodeArrayElements(BYTES, ELEMTY, ELEMTYPEINFO, 
                                   lengthBytes(BYTES) /Int #elemSize(ELEMTYPEINFO), .List))
    requires lengthBytes(BYTES) %Int #elemSize(ELEMTYPEINFO) ==Int 0  // element size divides cleanly
     andBool #elemSize(ELEMTYPEINFO) >Int 0  // positive element size
    [preserves-definedness]
```

## Integration with Existing Decoding

This array decoding functionality would integrate with the existing `#decodeConstant` function by 
adding a new rule for array types:

```k
// Example integration (not included in this module):
// rule <k> #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), TY, typeInfoArrayType(ELEMTY, LEN))
//       => #decodeArrayAllocation(BYTES, ELEMTY, {TYPEMAP[ELEMTY]}:>TypeInfo, LEN) 
//      ... </k>
//      <types> TYPEMAP </types>
//   requires ELEMTY in_keys(TYPEMAP)
//    andBool isTypeInfo(TYPEMAP[ELEMTY])
```

Note: While this `#decodeConstant` integration is technically correct, we don't expect such 
decoding to actually occur during normal execution.

```k
endmodule
```