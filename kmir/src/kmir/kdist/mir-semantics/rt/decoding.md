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
  syntax Evaluation ::= #decodeValue ( Bytes , TypeInfo ) [function, total, symbol(decodeValue)]
                      | UnableToDecode( Bytes , TypeInfo )
                      | UnableToDecode( Bytes , Ty , ProvenanceMapEntries )

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
    requires dynamicSize(1) ==K #metadata(TY)
  rule #elemSize(typeInfoRefType(_)) => 2 *Int #elemSize(typeInfoPrimitiveType(primTypeUint(uintTyUsize)))
    [owise]
  rule #elemSize(typeInfoPtrType(TY)) => #elemSize(typeInfoPrimitiveType(primTypeUint(uintTyUsize)))
    requires dynamicSize(1) ==K #metadata(TY)
  rule #elemSize(typeInfoPtrType(_)) => 2 *Int #elemSize(typeInfoPrimitiveType(primTypeUint(uintTyUsize)))
    [owise]

  rule #elemSize(typeInfoVoidType) => 0

  // FIXME can only use size from layout here. Requires adding layout first.
  // Enum, Struct, Tuple,

  rule 0 <=Int #elemSize(_) => true [simplification, preserves-definedness]
```


### Enum decoding

Enum decoding is performed by `#evalDecodeEnum(DecodeEnum)`.
If the decoding is for some reason unsuccessful, the result is `unableToDecodeEnum(DECODE_ENUM:DecodeEnum)`
where `DECODE_ENUM` is a data structure representing the step in the decoding process where the failure occured.

```k
  syntax Evaluation ::= #evalDecodeEnum ( DecodeEnum ) [function, total]
                      | unableToDecodeEnum ( DecodeEnum )

  syntax DecodeEnum ::= deMatchLayout(
                          bytes: Bytes
                        , discriminants: Discriminants
                        , fieldTypess: Tyss
                        , layout: MaybeLayoutShape // -> layoutFields layoutVariants layoutSize
                        )

                      | deMatchLayoutFields(
                          bytes: Bytes
                        , discriminants: Discriminants
                        , fieldTypess: Tyss
                        , layoutFields: FieldsShape // -> layoutFieldOffsets
                        , layoutVariants: VariantsShape
                        , layoutSize: MachineSize
                        )

                      | deMatchLayoutVariants(
                          bytes: Bytes
                        , discriminants: Discriminants
                        , fieldTypess: Tyss
                        , layoutFieldOffsets: MachineSizes
                        , layoutVariants: VariantsShape // -> variantIndex | variantTag variantTagEncoding variantTagField variantLayouts
                        , layoutSize: MachineSize
                        )

                      | deSingle(
                          bytes: Bytes
                        , discriminants: Discriminants
                        , fieldTypess: Tyss
                        , layoutFieldOffsets: MachineSizes
                        , variantIndex: Int
                        , layoutSize: MachineSize
                        )

                      | deMultipleMatchTagType(
                          bytes: Bytes
                        , discriminants: Discriminants
                        , fieldTypess: Tyss
                        , layoutFieldOffsets: MachineSizes
                        , variantTag: Scalar // -> tagType
                        , variantTagEncoding: TagEncoding
                        , variantTagField: Int
                        , variantLayouts: LayoutShapes
                        , layoutSize: MachineSize
                        )

                      | deMultipleMatchTagType(
                          bytes: Bytes
                        , discriminants: Discriminants
                        , fieldTypess: Tyss
                        , layoutFieldOffsets: MachineSizes
                        , variantTag: Scalar // -> tagType
                        , variantTagEncoding: TagEncoding
                        , variantTagField: Int
                        , variantLayouts: LayoutShapes
                        , layoutSize: MachineSize
                        )

                      | deMultipleMatchTagOffset(
                          bytes: Bytes
                        , discriminants: Discriminants
                        , fieldTypess: Tyss
                        , layoutFieldOffsets: MachineSizes // -> tagOffset
                        , tagType: TypeInfo
                        , variantTagEncoding: TagEncoding
                        , variantTagField: Int  // -> .
                        , variantLayouts: LayoutShapes
                        , layoutSize: MachineSize
                        )

                      | deMultipleDecodeTag(
                          bytes: Bytes
                        , discriminants: Discriminants
                        , fieldTypess: Tyss
                        , tagOffset: MachineSize
                        , tagType: TypeInfo
                        , variantTagEncoding: TagEncoding // -> .
                        , variantLayouts: LayoutShapes
                        , layoutSize: MachineSize
                        )

                      | deMultipleDecodeTagDirect(
                          bytes: Bytes
                        , discriminants: Discriminants
                        , fieldTypess: Tyss
                        , tagOffset: MachineSize
                        , tagType: TypeInfo
                        , variantLayouts: LayoutShapes
                        , layoutSize: MachineSize
                        )

                      | deMultipleMatchTag(
                          bytes: Bytes
                        , discriminants: Discriminants
                        , fieldTypess: Tyss
                        , tagValue: Evaluation
                        , variantLayouts: LayoutShapes
                        , layoutSize: MachineSize
                        )

                      | deMultipleFindVariantIdx(
                          bytes: Bytes
                        , discriminants: Discriminants
                        , fieldTypess: Tyss
                        , tag: Int
                        , variantLayouts: LayoutShapes
                        , layoutSize: MachineSize
                        )

                      | deMultipleMatchFindVariantIdxResult(
                          bytes: Bytes
                        , fieldTypess: Tyss
                        , findVariantIdxResult: FindVariantIdxResult
                        , variantLayouts: LayoutShapes
                        , layoutSize: MachineSize
                        )

                      | deMultipleSelectVariant(
                          bytes: Bytes
                        , fieldTypess: Tyss
                        , variantIndex: Int
                        , variantLayouts: LayoutShapes
                        , layoutSize: MachineSize
                        )

                      | deMultipleMatchSelectVariantResult(
                          bytes: Bytes
                        , selectVariantFieldTypesResult: SelectVariantFieldTypesResult
                        , variantIndex: Int
                        , selectVariantLayoutResult: SelectVariantLayoutResult
                        , layoutSize: MachineSize
                        )

                      | deMultiple(
                          bytes: Bytes
                        , fieldTypes: Tys
                        , variantIndex: Int
                        , variantLayout: LayoutShape
                        , layoutSize: MachineSize
                        )

  rule #decodeValue(
         BYTES
       , typeInfoEnumType(...
           name: _
         , adtDef: _
         , discriminants: DISCRIMINANTS
         , fields: FIELD_TYPESS
         , layout: LAYOUT
         )
       )
    => #evalDecodeEnum(
         deMatchLayout(...
           bytes: BYTES
         , discriminants: DISCRIMINANTS
         , fieldTypess: FIELD_TYPESS
         , layout: LAYOUT
         )
       )

  rule #evalDecodeEnum(DECODE_ENUM) => unableToDecodeEnum(DECODE_ENUM) [owise]

  rule #evalDecodeEnum(
         deMatchLayout(...
           bytes: BYTES
         , discriminants: DISCRIMINANTS
         , fieldTypess: FIELD_TYPESS
         , layout: someLayoutShape(
             layoutShape(...
               fields: LAYOUT_FIELDS
             , variants: LAYOUT_VARIANTS
             , abi: _
             , abiAlign: _
             , size: LAYOUT_SIZE
             )
           )
         )
       )
    => #evalDecodeEnum(
         deMatchLayoutFields(...
           bytes: BYTES
         , discriminants: DISCRIMINANTS
         , fieldTypess: FIELD_TYPESS
         , layoutFields: LAYOUT_FIELDS
         , layoutVariants: LAYOUT_VARIANTS
         , layoutSize: LAYOUT_SIZE
         )
       )

  rule #evalDecodeEnum(
         deMatchLayoutFields(...
           bytes: BYTES
         , discriminants: DISCRIMINANTS
         , fieldTypess: FIELD_TYPESS
         , layoutFields: fieldsShapeArbitrary(mk(... offsets: LAYOUT_FIELD_OFFSETS))
         , layoutVariants: LAYOUT_VARIANTS
         , layoutSize: LAYOUT_SIZE
         )
       )
    => #evalDecodeEnum(
         deMatchLayoutVariants(...
           bytes: BYTES
         , discriminants: DISCRIMINANTS
         , fieldTypess: FIELD_TYPESS
         , layoutFieldOffsets: LAYOUT_FIELD_OFFSETS
         , layoutVariants: LAYOUT_VARIANTS
         , layoutSize: LAYOUT_SIZE
         )
       )

  rule #evalDecodeEnum(
         deMatchLayoutVariants(...
           bytes: BYTES
         , discriminants: DISCRIMINANTS
         , fieldTypess: FIELD_TYPESS
         , layoutFieldOffsets: LAYOUT_FIELD_OFFSETS
         , layoutVariants: variantsShapeSingle(mk(... index: variantIdx(VARIANT_INDEX)))
         , layoutSize: LAYOUT_SIZE
         )
       )
    => #evalDecodeEnum(
         deSingle(...
           bytes: BYTES
         , discriminants: DISCRIMINANTS
         , fieldTypess: FIELD_TYPESS
         , layoutFieldOffsets: LAYOUT_FIELD_OFFSETS
         , variantIndex: VARIANT_INDEX
         , layoutSize: LAYOUT_SIZE
         )
       )

  rule #evalDecodeEnum(
         deMatchLayoutVariants(...
           bytes: BYTES
         , discriminants: DISCRIMINANTS
         , fieldTypess: FIELD_TYPESS
         , layoutFieldOffsets: LAYOUT_FIELD_OFFSETS
         , layoutVariants: variantsShapeMultiple(
             mk(...
               tag: VARIANT_TAG
             , tagEncoding: VARIANT_TAG_ENCODING
             , tagField: VARIANT_TAG_FIELD
             , variants: VARIANT_LAYOUTS
             )
           )
         , layoutSize: LAYOUT_SIZE
         )
       )
    => #evalDecodeEnum(
         deMultipleMatchTagType(...
           bytes: BYTES
         , discriminants: DISCRIMINANTS
         , fieldTypess: FIELD_TYPESS
         , layoutFieldOffsets: LAYOUT_FIELD_OFFSETS
         , variantTag: VARIANT_TAG
         , variantTagEncoding: VARIANT_TAG_ENCODING
         , variantTagField: VARIANT_TAG_FIELD
         , variantLayouts: VARIANT_LAYOUTS
         , layoutSize: LAYOUT_SIZE
         )
       )

  rule #evalDecodeEnum(
         deMultipleMatchTagType(...
           bytes: BYTES
         , discriminants: DISCRIMINANTS
         , fieldTypess: FIELD_TYPESS
         , layoutFieldOffsets: LAYOUT_FIELD_OFFSETS
         , variantTag: scalarInitialized(mk(... value: primitiveInt(PRIMITIVE_INT_TAG)))
         , variantTagEncoding: VARIANT_TAG_ENCODING
         , variantTagField: VARIANT_TAG_FIELD
         , variantLayouts: VARIANT_LAYOUTS
         , layoutSize: LAYOUT_SIZE
         )
       )
    => #evalDecodeEnum(
         deMultipleMatchTagOffset(...
           bytes: BYTES
         , discriminants: DISCRIMINANTS
         , fieldTypess: FIELD_TYPESS
         , layoutFieldOffsets: LAYOUT_FIELD_OFFSETS
         , tagType: #primitiveIntToTypeInfo(PRIMITIVE_INT_TAG)
         , variantTagEncoding: VARIANT_TAG_ENCODING
         , variantTagField: VARIANT_TAG_FIELD
         , variantLayouts: VARIANT_LAYOUTS
         , layoutSize: LAYOUT_SIZE
         )
       )

  rule #evalDecodeEnum(
         deMultipleMatchTagOffset(...
           bytes: BYTES
         , discriminants: DISCRIMINANTS
         , fieldTypess: FIELD_TYPESS
         , layoutFieldOffsets: TAG_OFFSET .MachineSizes
         , tagType: TAG_TYPE
         , variantTagEncoding: VARIANT_TAG_ENCODING
         , variantTagField: 0
         , variantLayouts: VARIANT_LAYOUTS
         , layoutSize: LAYOUT_SIZE
         )
       )
    => #evalDecodeEnum(
         deMultipleDecodeTag(...
           bytes: BYTES
         , discriminants: DISCRIMINANTS
         , fieldTypess: FIELD_TYPESS
         , tagOffset: TAG_OFFSET
         , tagType: TAG_TYPE
         , variantTagEncoding: VARIANT_TAG_ENCODING
         , variantLayouts: VARIANT_LAYOUTS
         , layoutSize: LAYOUT_SIZE
         )
       )

  rule #evalDecodeEnum(
         deMultipleDecodeTag(...
           bytes: BYTES
         , discriminants: DISCRIMINANTS
         , fieldTypess: FIELD_TYPESS
         , tagOffset: TAG_OFFSET
         , tagType: TAG_TYPE
         , variantTagEncoding: tagEncodingDirect
         , variantLayouts: VARIANT_LAYOUTS
         , layoutSize: LAYOUT_SIZE
         )
       )
    => #evalDecodeEnum(
         deMultipleDecodeTagDirect(...
           bytes: BYTES
         , discriminants: DISCRIMINANTS
         , fieldTypess: FIELD_TYPESS
         , tagOffset: TAG_OFFSET
         , tagType: TAG_TYPE
         , variantLayouts: VARIANT_LAYOUTS
         , layoutSize: LAYOUT_SIZE
         )
       )

  rule #evalDecodeEnum(
         deMultipleDecodeTagDirect(...
           bytes: BYTES
         , discriminants: DISCRIMINANTS
         , fieldTypess: FIELD_TYPESS
         , tagOffset: machineSize(... numBits: TAG_OFFSET_NUM_BITS)
         , tagType: TAG_TYPE
         , variantLayouts: VARIANT_LAYOUTS
         , layoutSize: LAYOUT_SIZE
         )
       )
    => #evalDecodeEnum(
         deMultipleMatchTag(...
           bytes: BYTES
         , discriminants: DISCRIMINANTS
         , fieldTypess: FIELD_TYPESS
         , tagValue: #decodeValue(
             substrBytes(
               BYTES
             , TAG_OFFSET_NUM_BITS /Int 8
             , (TAG_OFFSET_NUM_BITS /Int 8) +Int #elemSize(TAG_TYPE)
             )
           , TAG_TYPE
           )
         , variantLayouts: VARIANT_LAYOUTS
         , layoutSize: LAYOUT_SIZE
         )
       )
    requires TAG_OFFSET_NUM_BITS >=Int 0
     andBool #elemSize(TAG_TYPE) >Int 0
     andBool lengthBytes(BYTES) >=Int (TAG_OFFSET_NUM_BITS /Int 8) +Int #elemSize(TAG_TYPE)
     andBool #isIntType (TAG_TYPE)
    [preserves-definedness]

  rule #evalDecodeEnum(
         deMultipleMatchTag(...
           bytes: BYTES
         , discriminants: DISCRIMINANTS
         , fieldTypess: FIELD_TYPESS
         , tagValue: Integer(TAG, _BIT_WIDTH, _SIGNED)
         , variantLayouts: VARIANT_LAYOUTS
         , layoutSize: LAYOUT_SIZE
         )
       )
    => #evalDecodeEnum(
         deMultipleFindVariantIdx(...
           bytes: BYTES
         , discriminants: DISCRIMINANTS
         , fieldTypess: FIELD_TYPESS
         , tag: TAG
         , variantLayouts: VARIANT_LAYOUTS
         , layoutSize: LAYOUT_SIZE
         )
       )

  rule #evalDecodeEnum(
         deMultipleFindVariantIdx(...
           bytes: BYTES
         , discriminants: DISCRIMINANTS
         , fieldTypess: FIELD_TYPESS
         , tag: TAG
         , variantLayouts: VARIANT_LAYOUTS
         , layoutSize: LAYOUT_SIZE
         )
       )
    => #evalDecodeEnum(
         deMultipleMatchFindVariantIdxResult(...
           bytes: BYTES
         , fieldTypess: FIELD_TYPESS
         , findVariantIdxResult: #findVariantIdx(... tag: TAG, discriminants: DISCRIMINANTS)
         , variantLayouts: VARIANT_LAYOUTS
         , layoutSize: LAYOUT_SIZE
         )
       )

  rule #evalDecodeEnum(
         deMultipleMatchFindVariantIdxResult(...
           bytes: BYTES
         , fieldTypess: FIELD_TYPESS
         , findVariantIdxResult: ok(VARIANT_INDEX)
         , variantLayouts: VARIANT_LAYOUTS
         , layoutSize: LAYOUT_SIZE
         )
       )
    => #evalDecodeEnum(
         deMultipleSelectVariant(...
           bytes: BYTES
         , fieldTypess: FIELD_TYPESS
         , variantIndex: VARIANT_INDEX
         , variantLayouts: VARIANT_LAYOUTS
         , layoutSize: LAYOUT_SIZE
         )
       )

  rule #evalDecodeEnum(
         deMultipleSelectVariant(...
           bytes: BYTES
         , fieldTypess: FIELD_TYPESS
         , variantIndex: VARIANT_INDEX
         , variantLayouts: VARIANT_LAYOUTS
         , layoutSize: LAYOUT_SIZE
         )
       )
    => #evalDecodeEnum(
         deMultipleMatchSelectVariantResult(...
           bytes: BYTES
         , selectVariantFieldTypesResult: #selectVariantFieldTypes(...
             fieldTypess: FIELD_TYPESS
           , index: VARIANT_INDEX
           )
         , variantIndex: VARIANT_INDEX
         , selectVariantLayoutResult: #selectVariantLayout(...
             layouts: VARIANT_LAYOUTS
           , index: VARIANT_INDEX
           )
         , layoutSize: LAYOUT_SIZE
         )
       )

  rule #evalDecodeEnum(
         deMultipleMatchSelectVariantResult(...
           bytes: BYTES
         , selectVariantFieldTypesResult: ok(FIELD_TYPES)
         , variantIndex: VARIANT_INDEX
         , selectVariantLayoutResult: ok(VARIANT_LAYOUT)
         , layoutSize: MACHINE_SIZE
         )
       )
    => #evalDecodeEnum(
         deMultiple(...
           bytes: BYTES
         , fieldTypes: FIELD_TYPES
         , variantIndex: VARIANT_INDEX
         , variantLayout: VARIANT_LAYOUT
         , layoutSize: MACHINE_SIZE
         )
       )

  rule #evalDecodeEnum(
         deMultiple(...
           bytes: _BYTES
         , fieldTypes: .Tys
         , variantIndex: VARIANT_INDEX
         , variantLayout: _VARIANT_LAYOUT
         , layoutSize: _MACHINE_SIZE
         )
       )
       => Aggregate(variantIdx(VARIANT_INDEX), .List)
```

Helper functions used during the decoding process are defined below.

```k
  syntax TypeInfo ::= #primitiveIntToTypeInfo(PrimitiveInt) [function, total]
  rule #primitiveIntToTypeInfo(mk(... length: integerLengthI8   , signed: false)) => typeInfoPrimitiveType(primTypeUint(uintTyU8  ))
  rule #primitiveIntToTypeInfo(mk(... length: integerLengthI16  , signed: false)) => typeInfoPrimitiveType(primTypeUint(uintTyU16 ))
  rule #primitiveIntToTypeInfo(mk(... length: integerLengthI32  , signed: false)) => typeInfoPrimitiveType(primTypeUint(uintTyU32 ))
  rule #primitiveIntToTypeInfo(mk(... length: integerLengthI64  , signed: false)) => typeInfoPrimitiveType(primTypeUint(uintTyU64 ))
  rule #primitiveIntToTypeInfo(mk(... length: integerLengthI128 , signed: false)) => typeInfoPrimitiveType(primTypeUint(uintTyU128))
  rule #primitiveIntToTypeInfo(mk(... length: integerLengthI8   , signed: true )) => typeInfoPrimitiveType(primTypeInt ( intTyI8  ))
  rule #primitiveIntToTypeInfo(mk(... length: integerLengthI16  , signed: true )) => typeInfoPrimitiveType(primTypeInt ( intTyI16 ))
  rule #primitiveIntToTypeInfo(mk(... length: integerLengthI32  , signed: true )) => typeInfoPrimitiveType(primTypeInt ( intTyI32 ))
  rule #primitiveIntToTypeInfo(mk(... length: integerLengthI64  , signed: true )) => typeInfoPrimitiveType(primTypeInt ( intTyI64 ))
  rule #primitiveIntToTypeInfo(mk(... length: integerLengthI128 , signed: true )) => typeInfoPrimitiveType(primTypeInt ( intTyI128))
  rule #primitiveIntToTypeInfo(mk(... length: integerLengthI8   , signed: mirBool(false))) => typeInfoPrimitiveType(primTypeUint(uintTyU8  ))
  rule #primitiveIntToTypeInfo(mk(... length: integerLengthI16  , signed: mirBool(false))) => typeInfoPrimitiveType(primTypeUint(uintTyU16 ))
  rule #primitiveIntToTypeInfo(mk(... length: integerLengthI32  , signed: mirBool(false))) => typeInfoPrimitiveType(primTypeUint(uintTyU32 ))
  rule #primitiveIntToTypeInfo(mk(... length: integerLengthI64  , signed: mirBool(false))) => typeInfoPrimitiveType(primTypeUint(uintTyU64 ))
  rule #primitiveIntToTypeInfo(mk(... length: integerLengthI128 , signed: mirBool(false))) => typeInfoPrimitiveType(primTypeUint(uintTyU128))
  rule #primitiveIntToTypeInfo(mk(... length: integerLengthI8   , signed: mirBool(true ))) => typeInfoPrimitiveType(primTypeInt ( intTyI8  ))
  rule #primitiveIntToTypeInfo(mk(... length: integerLengthI16  , signed: mirBool(true ))) => typeInfoPrimitiveType(primTypeInt ( intTyI16 ))
  rule #primitiveIntToTypeInfo(mk(... length: integerLengthI32  , signed: mirBool(true ))) => typeInfoPrimitiveType(primTypeInt ( intTyI32 ))
  rule #primitiveIntToTypeInfo(mk(... length: integerLengthI64  , signed: mirBool(true ))) => typeInfoPrimitiveType(primTypeInt ( intTyI64 ))
  rule #primitiveIntToTypeInfo(mk(... length: integerLengthI128 , signed: mirBool(true ))) => typeInfoPrimitiveType(primTypeInt ( intTyI128))

  syntax FindVariantIdxResult ::= ok(Int)
                                | err(String)
                                | #findVariantIdx    ( tag: Int , discriminants: Discriminants )            [function, total, symbol(findVariantIdx)]
                                | #findVariantIdxAux ( tag: Int , discriminants: Discriminants , idx: Int ) [function, total, symbol(findVariantIdxAux)]

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
    => ok(IDX)
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
    => ok(IDX)
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

  syntax SelectVariantFieldTypesResult ::= ok(Tys)
                                         | err(String)
                                         | #selectVariantFieldTypes(fieldTypess: Tyss, index: Int) [function, total, symbol(selectVariantFieldTypes)]

  rule #selectVariantFieldTypes(...
         fieldTypess: .Tyss
       , index: _
       )
    => err("Variant field types not found")

  rule #selectVariantFieldTypes(...
         fieldTypess: _
       , index: INDEX
       )
    => err("Negative index not allowed")
    requires INDEX <Int 0

  rule #selectVariantFieldTypes(...
         fieldTypess: FIELD_TYPES : _REST
       , index: INDEX
       )
    => ok(FIELD_TYPES)
    requires INDEX ==Int 0

  rule #selectVariantFieldTypes(...
         fieldTypess: _FIELD_TYPES : REST
       , index: INDEX
       )
    => #selectVariantFieldTypes(...
         fieldTypess: REST
       , index: INDEX -Int 1
       )
    requires INDEX >Int 0

  syntax SelectVariantLayoutResult ::= ok(LayoutShape)
                                     | err(String)
                                     | #selectVariantLayout(layouts: LayoutShapes, index: Int) [function, total, symbol(selectVariantLayoutResult)]

  rule #selectVariantLayout(...
         layouts: .LayoutShapes
       , index: _
       )
    => err("Variant layout not found")

  rule #selectVariantLayout(...
         layouts: _
       , index: INDEX
       )
    => err("Negative index not allowed")
    requires INDEX <Int 0

  rule #selectVariantLayout(...
         layouts: LAYOUT _REST
       , index: INDEX
       )
    => ok(LAYOUT)
    requires INDEX ==Int 0

  rule #selectVariantLayout(...
         layouts: _LAYOUT REST
       , index: INDEX
       )
    => #selectVariantLayout(...
         layouts: REST
       , index: INDEX -Int 1
       )
    requires INDEX >Int 0
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

# Decoding the allocated constants into a memory map

When the program starts, all allocated constants are stored in the `<memory>` cell in the configuration,
as a mapping of `AllocId -> Value`, decoding the allocations to values using the above functions.

Besides actual byte allocations, we often find allocations with provenance,
as slim or fat pointers pointing to other static allocations.
One example of this is allocated error strings, whose length is stored in a fat pointer that is itself an allocated constant.


The basic decoding function is very similar to `#decodeConstant` but returns its result as a singleton `Map` instead of a mere value.

```k
  syntax Evaluation ::= #decodeAlloc ( AllocId , Ty , Allocation ) [function]
  // ----------------------------------------------------------
  rule #decodeAlloc(_ID, TY, allocation(BYTES, provenanceMap(.ProvenanceMapEntries), _ALIGN, _MUT))
      => #decodeValue(BYTES, lookupTy(TY))
```

If there are entries in the provenance map, then the decoder must create references to other allocations.
Each entry replaces a pointer starting at a certain offset in the bytes.
The pointee of the respective pointer is determined by type _layout_ of the type to decode.

Simple cases of offset 0 and reference types can be implemented here without consideration of layout.
The reference metadata is either determined statically by type, or filled in from the bytes for fat pointers.

```k
  // if length(BYTES) ==Int 16 decode BYTES[9..16] as dynamic size.
  rule #decodeAlloc(
          _ID,
          TY,
          allocation(BYTES, provenanceMap(provenanceMapEntry(0, REF_ID) ), _ALIGN, _MUT)
        )
      => AllocRef(REF_ID, .ProjectionElems, dynamicSize(Bytes2Int(substrBytes(BYTES, 8, 16), LE, Unsigned)))
    requires isTy(pointeeTy(lookupTy(TY))) // ensures this is a reference type
     andBool lengthBytes(BYTES) ==Int 16 // sufficient data to decode dynamic size (assumes usize == u64)
     andBool dynamicSize(1) ==K #metadata(pointeeTy(lookupTy(TY))) // expect fat pointer
    [preserves-definedness] // valid type lookup ensured

  // Otherwise query type information for static size and insert it.
  rule #decodeAlloc(
          _ID,
          TY,
          allocation(BYTES, provenanceMap(provenanceMapEntry(0, REF_ID) ), _ALIGN, _MUT)
        )
      => AllocRef(REF_ID, .ProjectionElems, #metadata(pointeeTy(lookupTy(TY))))
    requires isTy(pointeeTy(lookupTy(TY))) // ensures this is a reference type
     andBool lengthBytes(BYTES) ==Int 8 // single slim pointer (assumes usize == u64)
    [priority(60), preserves-definedness] // valid type lookup ensured
```

Allocations with more than one provenance map entry or witn non-reference types remain undecoded.

```k
  rule #decodeAlloc(_ID, TY, allocation(BYTES, provenanceMap(ENTRIES), _ALIGN, _MUT))
      => UnableToDecode(BYTES, TY, ENTRIES)
    [owise]
```

The entire set of `GlobalAllocs` is decoded by iterating over the list.
It is assumed that the given `Ty -> TypeInfo` map contains all types required.

This code is disabled

```
  syntax Map ::= #decodeAllocs ( GlobalAllocs )       [function, total, symbol("decodeAllocs")] // AllocId |-> Thing
               | #decodeAllocs ( Map , GlobalAllocs ) [function, total] // accumulating version
  // -----------------------------------------------------------------------------------------------
  rule #decodeAllocs(ALLOCS, TYPEMAP) => #decodeAllocs(.Map, ALLOCS, TYPEMAP)

  rule #decodeAllocs(ACCUM, .GlobalAllocs, _TYPEMAP) => ACCUM
  rule #decodeAllocs(ACCUM, globalAllocEntry(ID, TY, Memory(ALLOC)) ALLOCS, TYPEMAP)
      => #decodeAllocs(ACCUM #decodeAlloc(ID, TY, ALLOC, TYPEMAP), ALLOCS, TYPEMAP)
    requires TY in_keys(TYPEMAP)
    [preserves-definedness]
```

If the type of an alloc cannot be found, or for non-`Memory` allocs, the raw data is stored in a super-sort of `Value`.
This ensures that the function is total (anyway lookups require constraining the sort).

```
  syntax AllocData ::= Value | AllocData ( Ty , GlobalAllocKind )

  rule #decodeAllocs(ACCUM, globalAllocEntry(ID, TY, OTHER) ALLOCS, TYPEMAP)
      => #decodeAllocs(ACCUM ID |-> AllocData(TY, OTHER), ALLOCS, TYPEMAP)
    [owise]
```

```k
endmodule
```
