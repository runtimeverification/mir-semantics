# Helpers for type metadata (`TypeInfo`)

```k
requires "../ty.md"
requires "../body.md"
requires "numbers.md"
requires "value.md"

module RT-TYPES
  imports BOOL
  imports MAP
  imports K-EQUAL

  imports TYPES
  imports BODY
  imports RT-NUMBERS
  imports RT-VALUE-SYNTAX
```

Type metadata from Stable MIR JSON is present in a type lookup table `Ty -> TypeInfo` at runtime. 

This module contains helper functions to operate on this type information.

## Compatibility of types (high-level representation)

When two types use the same (low-level) representation for their values, pointers to them can be converted from one type to the other.

For compatible pointer types, the `#typeProjection` function computes a projection that can be appended to the pointer's projection
to return the correct type when the pointer is cast to a different pointee type.
Most notably, casting between arrays and single elements as well as casting to and from transparent wrappers.
This projection computation happens _recursively_, for instance casting from `*const [[T]]` to `*const T`.

The interface function is meant for pointer casts to compute pointee projections and returns nothing for other types.

```k
  syntax MaybeProjectionElems ::= ProjectionElems
                                | "NoProjectionElems"

  syntax MaybeProjectionElems ::= #typeProjection ( TypeInfo , TypeInfo )    [function, total]
  // ---------------------------------------------------------------------------------------
  rule #typeProjection ( typeInfoPtrType(TY1)     , typeInfoPtrType(TY2)     ) => #pointeeProjection(lookupTy(TY1), lookupTy(TY2))
  rule #typeProjection ( _, _ ) => NoProjectionElems [owise]
```

Note that certain projections can cancel each other, such as casting from one transparent wrapper to another.
In case of casting an element pointer to an array pointer, we rely on this cancellation to recover the array length
(NB ultimately there needs to be an underlying array if there is more than one element in the original allocation).

This can be done in an extended `append` function for projections, and already in the special cons function here. **TODO**

The `#maybeConsProj` function is a "cons" for projection lists with a short-cut case for when the second argument is not a projection list.
It also implements cancellation of inverse projections (such as casting from one transparent wrapper to another, or between arrays).

```k
  syntax ProjectionElem ::= "projectionElemSingletonArray" // elem -> array. Incomplete information! (relies on cancellation, or caller must consider metadata)
                          | "projectionElemWrapStruct"     // transparent wrapper (singleton struct)
                          | "projectionElemToZST"          // cast to ZST (immaterial data)
                          | "projectionElemFromZST"        // ...and back from ZST to something material (the two cancel out in sequence)

  syntax MaybeProjectionElems ::= maybeConcatProj ( ProjectionElem, MaybeProjectionElems ) [function, total]

  rule maybeConcatProj(PROJ, REST:ProjectionElems) => PROJ REST
  rule maybeConcatProj(  _ , NoProjectionElems   ) => NoProjectionElems

  // special cancellation rules with higher priority
  rule maybeConcatProj(projectionElemSingletonArray, projectionElemConstantIndex(0, 0, false) REST:ProjectionElems) => REST [priority(40)]
  rule maybeConcatProj(projectionElemConstantIndex(0, 0, false), projectionElemSingletonArray REST:ProjectionElems) => REST [priority(40)]

  rule maybeConcatProj(projectionElemWrapStruct, projectionElemField(fieldIdx(0), _) REST:ProjectionElems) => REST [priority(40)]
  // this rule would not be valid if the original pointee had more than one field. In the calling context, this won't occur, though.
  rule maybeConcatProj(projectionElemField(fieldIdx(0), _), projectionElemWrapStruct REST:ProjectionElems) => REST [priority(40)]

  rule maybeConcatProj(projectionElemToZST, projectionElemFromZST REST:ProjectionElems) => REST [priority(40)]
  rule maybeConcatProj(projectionElemFromZST, projectionElemToZST REST:ProjectionElems) => REST [priority(40)]
```

The `#pointeeProjection` function computes, for compatible pointee types, how to project from one pointee to the other.

```k
  syntax MaybeProjectionElems ::= #pointeeProjection ( TypeInfo , TypeInfo ) [function, total]
```

A short-cut rule for identical types takes preference.
As a default, no projection elements are returned for incompatible types.
```k
  rule #pointeeProjection(T , T) => .ProjectionElems  [priority(40)]
  rule #pointeeProjection(_ , _) => NoProjectionElems [owise]
```

Pointers to arrays/slices are compatible with pointers to the element type
```k
  rule #pointeeProjection(typeInfoArrayType(TY1, _), TY2)
    => maybeConcatProj(
          projectionElemConstantIndex(0, 0, false),
          #pointeeProjection(lookupTy(TY1), TY2)
        )
  rule #pointeeProjection(TY1, typeInfoArrayType(TY2, _))
    => maybeConcatProj(
          projectionElemSingletonArray,
          #pointeeProjection(TY1, lookupTy(TY2))
        )
```

Pointers to zero-sized types can be converted from and to. No recursion beyond the ZST.
**TODO** Problem: our ZSTs have different representation: compare empty arrays and empty structs/unit tuples.
```k
  rule #pointeeProjection(SRC, OTHER) => projectionElemToZST   .ProjectionElems
    requires #zeroSizedType(OTHER) andBool notBool #zeroSizedType(SRC)
    [priority(45)]
  rule #pointeeProjection(SRC, OTHER) => projectionElemFromZST .ProjectionElems
    requires #zeroSizedType(SRC) andBool notBool #zeroSizedType(OTHER)
    [priority(45)]
```

Pointers to structs with a single zero-offset field are compatible with pointers to that field's type
```k

  rule #pointeeProjection(typeInfoStructType(_, _, FIELD .Tys, LAYOUT), OTHER)
    => maybeConcatProj(
          projectionElemField(fieldIdx(0), FIELD),
          #pointeeProjection(lookupTy(FIELD), OTHER)
        )
    requires #zeroFieldOffset(LAYOUT)

  rule #pointeeProjection(OTHER, typeInfoStructType(_, _, FIELD .Tys, LAYOUT))
    => maybeConcatProj(
          projectionElemWrapStruct,
          #pointeeProjection(OTHER, lookupTy(FIELD))
        )
    requires #zeroFieldOffset(LAYOUT)
```

Pointers to `MaybeUninit<X>` can be cast to pointers to `X`.
This is actually a 2-step compatibility:
The `MaybeUninit<X>` union contains a `ManuallyDrop<X>` (when filled),
which is a singleton struct (see above).

```k
  rule #pointeeProjection(MAYBEUNINIT_TYINFO, ELEM_TYINFO)
    => maybeConcatProj(
          projectionElemField(fieldIdx(1), {getFieldTy(MAYBEUNINIT_TYINFO, 1)}:>Ty),
          maybeConcatProj(
            projectionElemField(fieldIdx(0), {getFieldTy(#lookupMaybeTy(getFieldTy(MAYBEUNINIT_TYINFO, 1)), 0)}:>Ty),
           .ProjectionElems // TODO recursion?
          )
        )
    requires #typeNameIs(MAYBEUNINIT_TYINFO, "std::mem::MaybeUninit<")
     andBool #lookupMaybeTy(getFieldTy(#lookupMaybeTy(getFieldTy(MAYBEUNINIT_TYINFO, 1)), 0)) ==K ELEM_TYINFO
```

```k
  syntax Bool ::= #zeroFieldOffset ( MaybeLayoutShape ) [function, total]
  // --------------------------------------------------------------------
  rule #zeroFieldOffset(LAYOUT)
    =>      #layoutOffsets(LAYOUT) ==K machineSize(mirInt(0)) .MachineSizes
     orBool #layoutOffsets(LAYOUT) ==K machineSize(0) .MachineSizes

  // Extract field offsets from the struct layout when available (Arbitrary only).
  syntax MachineSizes ::= #layoutOffsets ( MaybeLayoutShape ) [function, total]
  // --------------------------------------------------------------------------
  rule #layoutOffsets(someLayoutShape(layoutShape(fieldsShapeArbitrary(mk(OFFSETS)), _, _, _, _))) => OFFSETS
  rule #layoutOffsets(noLayoutShape) => .MachineSizes
  rule #layoutOffsets(_) => .MachineSizes [owise]
```

--------------------------------------------------

Helper function to identify an `union` type, this is needed so `#setLocalValue`
will not create an `Aggregate` instead of a `Union` `Value`.
```k
  syntax Bool ::= #isUnionType ( TypeInfo ) [function, total]
  // --------------------------------------------------------
  rule #isUnionType(typeInfoUnionType(_NAME, _ADTDEF, _FIELDS, _LAYOUT) ) => true
  rule #isUnionType(_)                                                    => false [owise]
```

## Determining types of places with projection

A helper function `getTyOf` traverses type metadata (using the type metadata map `Ty -> TypeInfo`) along the applied projections to determine the `Ty` of the projected place.
To make this function total, an optional `MaybeTy` is used.

```k
  syntax MaybeTy ::= Ty
                   | "TyUnknown"

  syntax MaybeTy ::= #transparentFieldTy ( TypeInfo ) [function, total]

  rule #transparentFieldTy(typeInfoStructType(_, _, FIELD .Tys, LAYOUT)) => FIELD
    requires #zeroFieldOffset(LAYOUT)
  rule #transparentFieldTy(_) => TyUnknown [owise]

  syntax Int ::= #transparentDepth ( TypeInfo ) [function, total]

  rule #transparentDepth(typeInfoStructType(_, _, FIELD .Tys, LAYOUT))
    => 1 +Int #transparentDepth(lookupTy(FIELD))
    requires #zeroFieldOffset(LAYOUT)
  rule #transparentDepth(_) => 0 [owise]

  syntax String ::= #typeName ( TypeInfo ) [function, total]
  // -------------------------------------------------------
  rule #typeName(typeInfoUnionType(NAME, _, _, _)) => NAME
  rule #typeName(typeInfoStructType(NAME, _, _, _)) => NAME
  rule #typeName(typeInfoEnumType(NAME, _, _, _, _)) => NAME
  rule #typeName(_) => "" [owise]

  syntax Bool ::= #typeNameIs( TypeInfo, String ) [function, total]
  // --------------------------------------------------------------
  rule #typeNameIs( TY_TO, STRING) => findString(#typeName(TY_TO), STRING, 0) ==Int 0

  syntax MaybeTy ::= getFieldTy ( TypeInfo , Int ) [function, total]
  // ---------------------------------------------------------------
  rule getFieldTy(typeInfoStructType(_, _, FIELDS, _) , IDX) => getFieldTyFromList(FIELDS, IDX)
  rule getFieldTy(typeInfoUnionType(_, _, FIELDS, _)  , IDX) => getFieldTyFromList(FIELDS, IDX)
  rule getFieldTy(_, _) => TyUnknown [owise]

  syntax MaybeTy ::= getFieldTyFromList ( Tys , Int ) [function, total]
  // ------------------------------------------------------------------
  rule getFieldTyFromList(FIELD _REST, 0) => FIELD
  rule getFieldTyFromList(_ REST, IDX) => getFieldTyFromList(REST, IDX -Int 1) requires IDX >Int 0
  rule getFieldTyFromList(_, _) => TyUnknown [owise]

  syntax Bool ::= #isArrayType ( TypeInfo ) [function, total]
  // --------------------------------------------------------
  rule #isArrayType(typeInfoArrayType(_, _)) => true
  rule #isArrayType(_) => false [owise]

  syntax Ty ::= getArrayElemTy ( TypeInfo ) [function, total]
  // --------------------------------------------------------
  rule getArrayElemTy(typeInfoArrayType(ELEM_TY, _)) => ELEM_TY
  rule getArrayElemTy(_) => ty(-1) [owise]

  syntax TypeInfo ::= getArrayElemTypeInfo ( TypeInfo ) [function, total]
  // --------------------------------------------------------------------
  rule getArrayElemTypeInfo(typeInfoArrayType(ELEM_TY, _)) => lookupTy(ELEM_TY)
  rule getArrayElemTypeInfo(_) => typeInfoVoidType [owise]

  syntax TypeInfo ::= #lookupMaybeTy ( MaybeTy ) [function, total]
  // -------------------------------------------------------------
  rule #lookupMaybeTy(TY:Ty) => lookupTy(TY)
  rule #lookupMaybeTy(TyUnknown) => typeInfoVoidType

  syntax MaybeTy ::= getTyOf( MaybeTy , ProjectionElems ) [function, total]
  // ----------------------------------------------------------------------
  rule getTyOf(TyUnknown,             _                      ) => TyUnknown
  rule getTyOf(TY,                    .ProjectionElems       ) => TY

  rule getTyOf(TY, projectionElemDeref                  PROJS ) => getTyOf(pointeeTy(lookupTy(TY)), PROJS)
  rule getTyOf( _, projectionElemField(_, TY)           PROJS ) => getTyOf(TY, PROJS) // could also look it up
  
  rule getTyOf(TY, projectionElemIndex(_)               PROJS) => getTyOf(elemTy(lookupTy(TY)), PROJS)
  rule getTyOf(TY, projectionElemConstantIndex(_, _, _) PROJS) => getTyOf(elemTy(lookupTy(TY)), PROJS)
  rule getTyOf(TY, projectionElemSubslice(_, _, _)      PROJS) => getTyOf(TY, PROJS) // TODO assumes TY is already a slice type

  rule getTyOf(TY, projectionElemDowncast(_)            PROJS) => getTyOf(TY, PROJS) // unchanged type, just setting variantIdx

  rule getTyOf( _, projectionElemOpaqueCast(TY)         PROJS) => getTyOf(TY, PROJS)

  rule getTyOf( _, projectionElemSubtype(TY)            PROJS) => getTyOf(TY, PROJS)
  // -----------------------------------------------------------
  rule getTyOf(_, _) => TyUnknown [owise]


  syntax MaybeTy ::= pointeeTy ( TypeInfo ) [function, total]
                   | elemTy ( TypeInfo )    [function, total]
  // ------------------------------------------------------
  rule pointeeTy(typeInfoPtrType(TY)) => TY
  rule pointeeTy(typeInfoRefType(TY)) => TY
  rule pointeeTy(     _             ) => TyUnknown [owise]
  rule elemTy(typeInfoArrayType(TY, _)) => TY
  rule elemTy(     _                  ) => TyUnknown [owise]
```

## Static and Dynamic Metadata for Types

References to data on the heap or stack may require metadata, most commonly the size of slices, which is not statically known.
The helper function `#metadataSize` determines whether or not a given `TypeInfo` requires size information or other metadata (also see `MetadataSize` sort in `value.md`).
To avoid repeated lookups, static array sizes are also stored as metadata (for `Unsize` casts).

NB that the need for metadata is determined for the _pointee_ type, not the pointer type.

A [similar function exists in `rustc`](https://doc.rust-lang.org/nightly/nightly-rustc/src/rustc_middle/ty/util.rs.html#224-235) to determine whether or not a type needs dynamic metadata.
Slices, `str`s  and dynamic types require it, and any `Ty` that `is_sized` does not.

```k
  syntax MetadataSize ::= #metadataSize    ( Ty , ProjectionElems ) [function, total]
                        | #metadataSize    (  MaybeTy )             [function, total]
                        | #metadataSizeAux ( TypeInfo )             [function, total]
  // --------------------------------------------------------------------------------------
  rule #metadataSize(TY, PROJS) => #metadataSize(getTyOf(TY, PROJS))

  rule #metadataSize(TyUnknown) => noMetadataSize
  rule #metadataSize(TY) => #metadataSizeAux(lookupTy(TY))

  rule #metadataSizeAux(typeInfoArrayType(_, noTyConst                     )) => dynamicSize(1)
  rule #metadataSizeAux(typeInfoArrayType(_, someTyConst(tyConst(CONST, _)))) => staticSize(readTyConstInt(CONST))
  rule #metadataSizeAux(    _OTHER                                          ) => noMetadataSize     [owise]
```


```k
  // reading Int-valued TyConsts from allocated bytes
  syntax Int ::= readTyConstInt ( TyConstKind ) [function]
  // -----------------------------------------------------------
  rule readTyConstInt( tyConstKindValue(TY, allocation(BYTES, _, _, _))) => Bytes2Int(BYTES, LE, Unsigned)
    requires isUintTy(#numTypeOf(lookupTy(TY)))
     andBool lengthBytes(BYTES) ==Int #bitWidth(#numTypeOf(lookupTy(TY))) /Int 8
    [preserves-definedness]

  rule readTyConstInt( tyConstKindValue(TY, allocation(BYTES, _, _, _))) => Bytes2Int(BYTES, LE, Signed  )
    requires isIntTy(#numTypeOf(lookupTy(TY)))
     andBool lengthBytes(BYTES) ==Int #bitWidth(#numTypeOf(lookupTy(TY))) /Int 8
    [preserves-definedness]
```

## Zero-sized types

```k
  syntax Bool ::= #zeroSizedType ( TypeInfo ) [function, total]

  rule #zeroSizedType(typeInfoTupleType(.Tys, _)) => true
  rule #zeroSizedType(typeInfoStructType(_, _, .Tys, _)) => true
  rule #zeroSizedType(typeInfoVoidType) => true
  // FIXME: Only unit tuples, empty structs, and void are recognized here; other
  // zero-sized types (e.g. single-variant enums, function or closure items,
  // newtype wrappers around ZSTs) still fall through because we do not consult
  // the layout metadata yet. Update once we rely on machineSize(0).
  rule #zeroSizedType(_) => false [owise]
```

## Alignment and Size of Types as per `TypeInfo`

The `alignOf` and `sizeOf` nullary operations return the alignment / size in bytes as a `usize`.
This information is either hard-wired for primitive types (numbers, first and foremost), or read from the layout in `TypeInfo`.

```k
  syntax Int ::= #sizeOf ( TypeInfo )  [function, total]
               | #alignOf ( TypeInfo ) [function, total]

  // primitive int types: use bit width (both for size and alignment)
  rule #sizeOf(typeInfoPrimitiveType(primTypeInt(NUMTY))) => #bitWidth(NUMTY) /Int 8 [preserves-definedness]
  rule #alignOf(typeInfoPrimitiveType(primTypeInt(NUMTY))) => #bitWidth(NUMTY) /Int 8 [preserves-definedness]
  rule #sizeOf(typeInfoPrimitiveType(primTypeUint(NUMTY))) => #bitWidth(NUMTY) /Int 8 [preserves-definedness]
  rule #alignOf(typeInfoPrimitiveType(primTypeUint(NUMTY))) => #bitWidth(NUMTY) /Int 8 [preserves-definedness]
  rule #sizeOf(typeInfoPrimitiveType(primTypeFloat(NUMTY))) => #bitWidth(NUMTY) /Int 8 [preserves-definedness]
  rule #alignOf(typeInfoPrimitiveType(primTypeFloat(NUMTY))) => #bitWidth(NUMTY) /Int 8 [preserves-definedness]
  // bool and char
  rule #sizeOf(typeInfoPrimitiveType(primTypeBool))  => 1
  rule #alignOf(typeInfoPrimitiveType(primTypeBool)) => 1
  rule #sizeOf(typeInfoPrimitiveType(primTypeChar))  => 4
  rule #alignOf(typeInfoPrimitiveType(primTypeChar)) => 4
  // The str primitive has alignment of a Char but size 0 (indicating dynamic size)
  rule #sizeOf(typeInfoPrimitiveType(primTypeStr))  => 0
  rule #alignOf(typeInfoPrimitiveType(primTypeStr)) => 4
  // enums, structs , and tuples provide the values from their layout information
  rule #sizeOf(typeInfoEnumType(_, _, _, _, someLayoutShape(layoutShape(_, _, _, _, machineSize(   BITS     ))))) => BITS /Int 8 [preserves-definedness]
  rule #sizeOf(typeInfoEnumType(_, _, _, _, someLayoutShape(layoutShape(_, _, _, _, machineSize(mirInt(BITS)))))) => BITS /Int 8 [preserves-definedness]
  rule #sizeOf(typeInfoEnumType(_, _, _, _, noLayoutShape)) => 0
  rule #alignOf(typeInfoEnumType(_, _, _, _, someLayoutShape(layoutShape(_, _, _, align(BYTES),_)))) => BYTES
  rule #alignOf(typeInfoEnumType(_, _, _, _, noLayoutShape)) => 1
  // struct
  rule #sizeOf(typeInfoStructType(_, _, _, someLayoutShape(layoutShape(_, _, _, _, machineSize(   BITS     ))))) => BITS /Int 8 [preserves-definedness]
  rule #sizeOf(typeInfoStructType(_, _, _, someLayoutShape(layoutShape(_, _, _, _, machineSize(mirInt(BITS)))))) => BITS /Int 8 [preserves-definedness]
  rule #sizeOf(typeInfoStructType(_, _, _, noLayoutShape)) => 0
  rule #alignOf(typeInfoStructType(_, _, _, someLayoutShape(layoutShape(_, _, _, align(BYTES),_)))) => BYTES
  rule #alignOf(typeInfoStructType(_, _, _, noLayoutShape)) => 1
  // tuple
  rule #sizeOf(typeInfoTupleType(_, someLayoutShape(layoutShape(_, _, _, _, machineSize(   BITS     ))))) => BITS /Int 8 [preserves-definedness]
  rule #sizeOf(typeInfoTupleType(_, someLayoutShape(layoutShape(_, _, _, _, machineSize(mirInt(BITS)))))) => BITS /Int 8 [preserves-definedness]
  rule #sizeOf(typeInfoTupleType(_, noLayoutShape)) => 0
  rule #alignOf(typeInfoTupleType(_, someLayoutShape(layoutShape(_, _, _, align(BYTES),_)))) => BYTES
  rule #alignOf(typeInfoTupleType(_, noLayoutShape)) => 1
  // union
  rule #sizeOf(typeInfoUnionType(_, _, _, someLayoutShape(layoutShape(_, _, _, _, machineSize(   BITS     ))))) => BITS /Int 8 [preserves-definedness]
  rule #sizeOf(typeInfoUnionType(_, _, _, someLayoutShape(layoutShape(_, _, _, _, machineSize(mirInt(BITS)))))) => BITS /Int 8 [preserves-definedness]
  rule #sizeOf(typeInfoUnionType(_, _, _, noLayoutShape)) => 0
  rule #alignOf(typeInfoUnionType(_, _, _, someLayoutShape(layoutShape(_, _, _, align(BYTES),_)))) => BYTES
  rule #alignOf(typeInfoUnionType(_, _, _, noLayoutShape)) => 1
  // arrays with known length have the alignment of the element type, and a size multiplying element count and element size
  rule #sizeOf(typeInfoArrayType(ELEM_TY, someTyConst(tyConst(KIND, _)))) => #sizeOf(lookupTy(ELEM_TY)) *Int readTyConstInt(KIND)
  rule #sizeOf(typeInfoArrayType(  _    ,    noTyConst                 )) => 0
  rule #alignOf(typeInfoArrayType(ELEM_TY, _)) => #alignOf(lookupTy(ELEM_TY))
  // thin ptr and ref types have the size of `usize` and twice that for fat pointers/refs. Alignment is that of `usize`
  rule #sizeOf(typeInfoPtrType(POINTEE_TY))
    => #sizeOf(typeInfoPrimitiveType(primTypeUint(uintTyUsize)))
          *Int (#if #metadataSize(POINTEE_TY) ==K dynamicSize(1) #then 2 #else 1 #fi)
  rule #sizeOf(typeInfoRefType(POINTEE_TY))
    => #sizeOf(typeInfoPrimitiveType(primTypeUint(uintTyUsize)))
          *Int (#if #metadataSize(POINTEE_TY) ==K dynamicSize(1) #then 2 #else 1 #fi)
  rule #alignOf(typeInfoPtrType(_)) => #alignOf(typeInfoPrimitiveType(primTypeUint(uintTyUsize)))
  rule #alignOf(typeInfoRefType(_)) => #alignOf(typeInfoPrimitiveType(primTypeUint(uintTyUsize)))
  // other types (fun and void types) have size and alignment 0
  rule #sizeOf(_)  => 0 [owise]
  rule #alignOf(_) => 0 [owise]
```

```k
endmodule
```
