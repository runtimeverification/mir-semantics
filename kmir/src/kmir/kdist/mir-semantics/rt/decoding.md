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
  imports TYPES
  imports RT-VALUE-SYNTAX
  imports RT-NUMBERS
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
         ACC ListItem(#decodeElement(
           substrBytes(BYTES, 0, #elemSize(ELEMTYPEINFO)), 
           ELEMTY,
           ELEMTYPEINFO
         ))
       )
    requires LEN >Int 0
     andBool lengthBytes(BYTES) >=Int #elemSize(ELEMTYPEINFO)  // enough bytes remaining
    [preserves-definedness]
```

## Element Decoding Interface

The `#decodeElement` function handles decoding individual array elements from their byte 
representation. 
This function should be implemented to dispatch to appropriate decoders based on the element's 
`TypeInfo` (e.g., `#decodeInteger` for integer types).

```k
  syntax Value ::= #decodeElement ( Bytes, Ty, TypeInfo ) [function]
                   // decode a single element from its bytes

  syntax Int ::= #elemSize ( TypeInfo ) [function]
                 // size in bytes of an element of this type
                 // TODO: this function should go into the rt/types.md module
```

Known element sizes for common types:

```k
  // Examples (to be moved to rt/types.md):
  // rule #elemSize(typeInfoPrimitiveType(primTypeBool)) => 1
  // rule #elemSize(TYPEINFO) => #bitWidth(#intTypeOf(TYPEINFO)) /Int 8
  //   requires #isIntType(TYPEINFO)
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