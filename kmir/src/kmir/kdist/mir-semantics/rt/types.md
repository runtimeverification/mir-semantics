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
```

```{.k .concrete}
  syntax MaybeProjectionElems ::= #typeProjection ( MaybeMap , TypeInfo , TypeInfo )    [function, total]
  rule #typeProjection ( TYPESMAP, typeInfoPtrType(TY1), typeInfoPtrType(TY2) ) => #pointeeProjection(TYPESMAP, lookupTy(TYPESMAP, TY1), lookupTy(TYPESMAP, TY2))
  rule #typeProjection ( _, _, _ ) => NoProjectionElems [owise]
```

```{.k .symbolic}
  syntax MaybeProjectionElems ::= #typeProjection ( MaybeMap , TypeInfo , TypeInfo )    [function, total, no-evaluators]
  rule #typeProjection ( _, typeInfoPtrType(TY1), typeInfoPtrType(TY2) ) => #pointeeProjection(noMap, lookupTyKore(TY1), lookupTyKore(TY2))
  rule #typeProjection ( _, _, _ ) => NoProjectionElems [owise]
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

It uses a **source-first strategy**: always unwrap the source type (struct wrapper or array) before
attempting to unwrap the target type. This eliminates non-deterministic overlap between source-side
and target-side rules, because a type cannot be both a struct and an array simultaneously.
When the source cannot be unwrapped further, target-side unwrapping is handled by `#pointeeProjectionTarget`.

```{.k .concrete}
  syntax MaybeProjectionElems ::= #pointeeProjection ( MaybeMap , TypeInfo , TypeInfo ) [function, total]
```

```{.k .symbolic}
  syntax MaybeProjectionElems ::= #pointeeProjection ( MaybeMap , TypeInfo , TypeInfo ) [function, total, no-evaluators]
```

A short-cut rule for identical types takes preference.
```k
  rule #pointeeProjection(_, T , T) => .ProjectionElems  [priority(40)]
```

Pointers to zero-sized types can be converted from and to. No recursion beyond the ZST.
**TODO** Problem: our ZSTs have different representation: compare empty arrays and empty structs/unit tuples.
```k
  rule #pointeeProjection(_, SRC, OTHER) => projectionElemToZST   .ProjectionElems
    requires #zeroSizedType(OTHER) andBool notBool #zeroSizedType(SRC)
    [priority(45)]
  rule #pointeeProjection(_, SRC, OTHER) => projectionElemFromZST .ProjectionElems
    requires #zeroSizedType(SRC) andBool notBool #zeroSizedType(OTHER)
    [priority(45)]
```

Source-side: unwrap structs and arrays from the source type first.

When source is an array and target is a transparent wrapper whose inner type equals the source,
the source should be wrapped rather than unwrapped (e.g., `*const [u8;2] → *const Wrapper([u8;2])`).
```{.k .concrete}
  rule #pointeeProjection(TYPESMAP, typeInfoStructType(_, _, FIELD .Tys, LAYOUT), OTHER)
    => maybeConcatProj(
          projectionElemField(fieldIdx(0), FIELD),
          #pointeeProjection(TYPESMAP, lookupTy(TYPESMAP, FIELD), OTHER)
        )
    requires #zeroFieldOffset(LAYOUT)

  rule #pointeeProjection(TYPESMAP, SRC:TypeInfo, typeInfoStructType(_NAME, _ADTDEF, FIELD .Tys, LAYOUT))
    => maybeConcatProj(
          projectionElemWrapStruct,
          #pointeeProjection(TYPESMAP, SRC, lookupTy(TYPESMAP, FIELD))
        )
    requires #isArrayType(SRC)
    andBool #zeroFieldOffset(LAYOUT)
    andBool lookupTy(TYPESMAP, FIELD) ==K SRC
    [priority(42)]

  rule #pointeeProjection(TYPESMAP, typeInfoArrayType(TY1, _), TY2)
    => maybeConcatProj(
          projectionElemConstantIndex(0, 0, false),
          #pointeeProjection(TYPESMAP, lookupTy(TYPESMAP, TY1), TY2)
        )
```

```{.k .symbolic}
  rule #pointeeProjection(_, typeInfoStructType(_, _, FIELD .Tys, LAYOUT), OTHER)
    => maybeConcatProj(
          projectionElemField(fieldIdx(0), FIELD),
          #pointeeProjection(noMap, lookupTyKore(FIELD), OTHER)
        )
    requires #zeroFieldOffset(LAYOUT)

  rule #pointeeProjection(_, SRC:TypeInfo, typeInfoStructType(_NAME, _ADTDEF, FIELD .Tys, LAYOUT))
    => maybeConcatProj(
          projectionElemWrapStruct,
          #pointeeProjection(noMap, SRC, lookupTyKore(FIELD))
        )
    requires #isArrayType(SRC)
    andBool #zeroFieldOffset(LAYOUT)
    andBool lookupTyKore(FIELD) ==K SRC
    [priority(42)]

  rule #pointeeProjection(_, typeInfoArrayType(TY1, _), TY2)
    => maybeConcatProj(
          projectionElemConstantIndex(0, 0, false),
          #pointeeProjection(noMap, lookupTyKore(TY1), TY2)
        )
```

Pointers to `MaybeUninit<X>` can be cast to pointers to `X`.
This is actually a 2-step compatibility:
The `MaybeUninit<X>` union contains a `ManuallyDrop<X>` (when filled),
which is a singleton struct (see above).

```k
  rule #pointeeProjection(_, MAYBEUNINIT_TYINFO, ELEM_TYINFO)
    => maybeConcatProj(
          projectionElemField(fieldIdx(1), {getFieldTy(MAYBEUNINIT_TYINFO, 1)}:>Ty),
          maybeConcatProj(
            projectionElemField(fieldIdx(0), {getFieldTy(#lookupMaybeTy(noMap, getFieldTy(MAYBEUNINIT_TYINFO, 1)), 0)}:>Ty), // TODO temporary noMap, convert #pointeeProjection MaybeUninit rule
           .ProjectionElems // TODO recursion?
          )
        )
    requires #typeNameIs(MAYBEUNINIT_TYINFO, "std::mem::MaybeUninit<")
     andBool #lookupMaybeTy(noMap, getFieldTy(#lookupMaybeTy(noMap, getFieldTy(MAYBEUNINIT_TYINFO, 1)), 0)) ==K ELEM_TYINFO
```

Fallback: source is not unwrappable, delegate to target-side.
```k
  rule #pointeeProjection(TYPESMAP, SRC, TGT) => #pointeeProjectionTarget(TYPESMAP, SRC, TGT) [owise]
```

Target-side fallback: only reached when source cannot be unwrapped further.
After one step of target unwrapping, recurse back to `#pointeeProjection` to maintain
the source-first strategy.

```{.k .concrete}
  syntax MaybeProjectionElems ::= #pointeeProjectionTarget ( MaybeMap , TypeInfo , TypeInfo ) [function, total]

  rule #pointeeProjectionTarget(TYPESMAP, TY1, typeInfoArrayType(TY2, _))
    => maybeConcatProj(
          projectionElemSingletonArray,
          #pointeeProjection(TYPESMAP, TY1, lookupTy(TYPESMAP, TY2))
        )

  rule #pointeeProjectionTarget(TYPESMAP, OTHER, typeInfoStructType(_, _, FIELD .Tys, LAYOUT))
    => maybeConcatProj(
          projectionElemWrapStruct,
          #pointeeProjection(TYPESMAP, OTHER, lookupTy(TYPESMAP, FIELD))
        )
    requires #zeroFieldOffset(LAYOUT)

  rule #pointeeProjectionTarget(_, _, _) => NoProjectionElems [owise]
```

```{.k .symbolic}
  syntax MaybeProjectionElems ::= #pointeeProjectionTarget ( MaybeMap , TypeInfo , TypeInfo ) [function, total, no-evaluators]

  rule #pointeeProjectionTarget(_, TY1, typeInfoArrayType(TY2, _))
    => maybeConcatProj(
          projectionElemSingletonArray,
          #pointeeProjection(noMap, TY1, lookupTyKore(TY2))
        )

  rule #pointeeProjectionTarget(_, OTHER, typeInfoStructType(_, _, FIELD .Tys, LAYOUT))
    => maybeConcatProj(
          projectionElemWrapStruct,
          #pointeeProjection(noMap, OTHER, lookupTyKore(FIELD))
        )
    requires #zeroFieldOffset(LAYOUT)

  rule #pointeeProjectionTarget(_, _, _) => NoProjectionElems [owise]
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

```

```{.k .concrete}
  syntax TypeInfo ::= getArrayElemTypeInfo ( MaybeMap , TypeInfo ) [function, total]
  rule getArrayElemTypeInfo(TYPESMAP, typeInfoArrayType(ELEM_TY, _)) => lookupTy(TYPESMAP, ELEM_TY)
  rule getArrayElemTypeInfo(_, _) => typeInfoVoidType [owise]

  syntax TypeInfo ::= #lookupMaybeTy ( MaybeMap , MaybeTy ) [function, total]
  rule #lookupMaybeTy(TYPESMAP, TY:Ty) => lookupTy(TYPESMAP, TY)
  rule #lookupMaybeTy(_, TyUnknown) => typeInfoVoidType
```

```{.k .symbolic}
  syntax TypeInfo ::= getArrayElemTypeInfo ( MaybeMap , TypeInfo ) [function, total, no-evaluators]
  rule getArrayElemTypeInfo(_, typeInfoArrayType(ELEM_TY, _)) => lookupTyKore(ELEM_TY)
  rule getArrayElemTypeInfo(_, _) => typeInfoVoidType [owise]

  syntax TypeInfo ::= #lookupMaybeTy ( MaybeMap , MaybeTy ) [function, total, no-evaluators]
  rule #lookupMaybeTy(_, TY:Ty) => lookupTyKore(TY)
  rule #lookupMaybeTy(_, TyUnknown) => typeInfoVoidType
```

```{.k .concrete}
  syntax MaybeTy ::= getTyOf( MaybeMap , MaybeTy , ProjectionElems ) [function, total]
  // ----------------------------------------------------------------------
  rule getTyOf(_, TyUnknown,             _                      ) => TyUnknown
  rule getTyOf(_, TY,                    .ProjectionElems       ) => TY

  rule getTyOf(TYPESMAP, TY, projectionElemDeref                  PROJS ) => getTyOf(TYPESMAP, pointeeTy(lookupTy(TYPESMAP, TY)), PROJS)
  rule getTyOf(TYPESMAP,  _, projectionElemField(_, TY)           PROJS ) => getTyOf(TYPESMAP, TY, PROJS)

  rule getTyOf(TYPESMAP, TY, projectionElemIndex(_)               PROJS) => getTyOf(TYPESMAP, elemTy(lookupTy(TYPESMAP, TY)), PROJS)
  rule getTyOf(TYPESMAP, TY, projectionElemConstantIndex(_, _, _) PROJS) => getTyOf(TYPESMAP, elemTy(lookupTy(TYPESMAP, TY)), PROJS)
  rule getTyOf(TYPESMAP, TY, projectionElemSubslice(_, _, _)      PROJS) => getTyOf(TYPESMAP, TY, PROJS) // TODO assumes TY is already a slice type

  rule getTyOf(TYPESMAP, TY, projectionElemDowncast(_)            PROJS) => getTyOf(TYPESMAP, TY, PROJS)

  rule getTyOf(TYPESMAP,  _, projectionElemOpaqueCast(TY)         PROJS) => getTyOf(TYPESMAP, TY, PROJS)

  rule getTyOf(TYPESMAP,  _, projectionElemSubtype(TY)            PROJS) => getTyOf(TYPESMAP, TY, PROJS)
  // -----------------------------------------------------------
  rule getTyOf(_, _, _) => TyUnknown [owise]
```

```{.k .symbolic}
  syntax MaybeTy ::= getTyOf( MaybeMap , MaybeTy , ProjectionElems ) [function, total, no-evaluators]
  // ----------------------------------------------------------------------
  rule getTyOf(_, TyUnknown,             _                      ) => TyUnknown
  rule getTyOf(_, TY,                    .ProjectionElems       ) => TY

  rule getTyOf(_, TY, projectionElemDeref                  PROJS ) => getTyOf(noMap, pointeeTy(lookupTyKore(TY)), PROJS)
  rule getTyOf(_,  _, projectionElemField(_, TY)           PROJS ) => getTyOf(noMap, TY, PROJS)

  rule getTyOf(_, TY, projectionElemIndex(_)               PROJS) => getTyOf(noMap, elemTy(lookupTyKore(TY)), PROJS)
  rule getTyOf(_, TY, projectionElemConstantIndex(_, _, _) PROJS) => getTyOf(noMap, elemTy(lookupTyKore(TY)), PROJS)
  rule getTyOf(_, TY, projectionElemSubslice(_, _, _)      PROJS) => getTyOf(noMap, TY, PROJS) // TODO assumes TY is already a slice type

  rule getTyOf(_, TY, projectionElemDowncast(_)            PROJS) => getTyOf(noMap, TY, PROJS)

  rule getTyOf(_,  _, projectionElemOpaqueCast(TY)         PROJS) => getTyOf(noMap, TY, PROJS)

  rule getTyOf(_,  _, projectionElemSubtype(TY)            PROJS) => getTyOf(noMap, TY, PROJS)
  // -----------------------------------------------------------
  rule getTyOf(_, _, _) => TyUnknown [owise]
```

```k


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

```{.k .concrete}
  syntax MetadataSize ::= #metadataSize    ( MaybeMap , Ty , ProjectionElems ) [function, total]
                        | #metadataSize    ( MaybeMap , MaybeTy )              [function, total]
  // --------------------------------------------------------------------------------------
  rule #metadataSize(TYPESMAP, TY, PROJS) => #metadataSize(TYPESMAP, getTyOf(TYPESMAP, TY, PROJS))

  rule #metadataSize(_, TyUnknown) => noMetadataSize
  rule #metadataSize(TYPESMAP, TY) => #metadataSizeAux(TYPESMAP, lookupTy(TYPESMAP, TY))
```

```{.k .symbolic}
  syntax MetadataSize ::= #metadataSize    ( MaybeMap , Ty , ProjectionElems ) [function, total, no-evaluators]
                        | #metadataSize    ( MaybeMap , MaybeTy )              [function, total, no-evaluators]
  // --------------------------------------------------------------------------------------
  rule #metadataSize(_, TY, PROJS) => #metadataSize(noMap, getTyOf(noMap, TY, PROJS))

  rule #metadataSize(_, TyUnknown) => noMetadataSize
  rule #metadataSize(_, TY) => #metadataSizeAux(noMap, lookupTyKore(TY))
```

```{.k .concrete}
  syntax MetadataSize ::= #metadataSizeAux ( MaybeMap , TypeInfo )  [function, total]
  rule #metadataSizeAux(_, typeInfoArrayType(_, noTyConst                     )) => dynamicSize(1)
  rule #metadataSizeAux(TYPESMAP, typeInfoArrayType(_, someTyConst(tyConst(CONST, _)))) => staticSize(readTyConstInt(TYPESMAP, CONST))
  rule #metadataSizeAux(_, _OTHER                                              ) => noMetadataSize     [owise]
```

```{.k .symbolic}
  syntax MetadataSize ::= #metadataSizeAux ( MaybeMap , TypeInfo )  [function, total, no-evaluators]
  rule #metadataSizeAux(_, typeInfoArrayType(_, noTyConst                     )) => dynamicSize(1)
  rule #metadataSizeAux(_, typeInfoArrayType(_, someTyConst(tyConst(CONST, _)))) => staticSize(readTyConstInt(noMap, CONST))
  rule #metadataSizeAux(_, _OTHER                                              ) => noMetadataSize     [owise]
```


```{.k .concrete}
  // reading Int-valued TyConsts from allocated bytes
  syntax Int ::= readTyConstInt ( MaybeMap , TyConstKind ) [function]
  // -----------------------------------------------------------
  rule readTyConstInt( TYPESMAP, tyConstKindValue(TY, allocation(BYTES, _, _, _))) => Bytes2Int(BYTES, LE, Unsigned)
    requires isUintTy(#numTypeOf(lookupTy(TYPESMAP, TY)))
     andBool lengthBytes(BYTES) ==Int #bitWidth(#numTypeOf(lookupTy(TYPESMAP, TY))) /Int 8
    [preserves-definedness]

  rule readTyConstInt( TYPESMAP, tyConstKindValue(TY, allocation(BYTES, _, _, _))) => Bytes2Int(BYTES, LE, Signed  )
    requires isIntTy(#numTypeOf(lookupTy(TYPESMAP, TY)))
     andBool lengthBytes(BYTES) ==Int #bitWidth(#numTypeOf(lookupTy(TYPESMAP, TY))) /Int 8
    [preserves-definedness]
```

```{.k .symbolic}
  syntax Int ::= readTyConstInt ( MaybeMap , TyConstKind ) [function, no-evaluators]

  rule readTyConstInt( _, tyConstKindValue(TY, allocation(BYTES, _, _, _))) => Bytes2Int(BYTES, LE, Unsigned)
    requires isUintTy(#numTypeOf(lookupTyKore(TY)))
     andBool lengthBytes(BYTES) ==Int #bitWidth(#numTypeOf(lookupTyKore(TY))) /Int 8
    [preserves-definedness]

  rule readTyConstInt( _, tyConstKindValue(TY, allocation(BYTES, _, _, _))) => Bytes2Int(BYTES, LE, Signed  )
    requires isIntTy(#numTypeOf(lookupTyKore(TY)))
     andBool lengthBytes(BYTES) ==Int #bitWidth(#numTypeOf(lookupTyKore(TY))) /Int 8
    [preserves-definedness]
```

## Zero-sized types

```k
  syntax Bool ::= #zeroSizedType ( TypeInfo ) [function, total]

  rule #zeroSizedType(typeInfoTupleType(.Tys, _)) => true
  rule #zeroSizedType(typeInfoStructType(_, _, .Tys, _)) => true
  rule #zeroSizedType(typeInfoVoidType) => true
  rule #zeroSizedType(typeInfoFunType(_)) => true
  // FIXME: Only unit tuples, empty structs, void, and function items are
  // recognized here; other zero-sized types (e.g. single-variant enums,
  // newtype wrappers around ZSTs) still fall through because we do not consult
  // the layout metadata yet. Update once we rely on machineSize(0).
  rule #zeroSizedType(_) => false [owise]
```

## Alignment and Size of Types as per `TypeInfo`

The `alignOf` and `sizeOf` nullary operations return the alignment / size in bytes as a `usize`.
This information is either hard-wired for primitive types (numbers, first and foremost), or read from the layout in `TypeInfo`.

```{.k .concrete}
  syntax Int ::= #sizeOf ( MaybeMap , TypeInfo )  [function, total]
               | #alignOf ( MaybeMap , TypeInfo ) [function, total]
```

```{.k .symbolic}
  syntax Int ::= #sizeOf ( MaybeMap , TypeInfo )  [function, total, no-evaluators]
               | #alignOf ( MaybeMap , TypeInfo ) [function, total, no-evaluators]
```

```k

  // primitive int types: use bit width (both for size and alignment)
  rule #sizeOf(_, typeInfoPrimitiveType(primTypeInt(NUMTY))) => #bitWidth(NUMTY) /Int 8 [preserves-definedness]
  rule #alignOf(_, typeInfoPrimitiveType(primTypeInt(NUMTY))) => #bitWidth(NUMTY) /Int 8 [preserves-definedness]
  rule #sizeOf(_, typeInfoPrimitiveType(primTypeUint(NUMTY))) => #bitWidth(NUMTY) /Int 8 [preserves-definedness]
  rule #alignOf(_, typeInfoPrimitiveType(primTypeUint(NUMTY))) => #bitWidth(NUMTY) /Int 8 [preserves-definedness]
  rule #sizeOf(_, typeInfoPrimitiveType(primTypeFloat(NUMTY))) => #bitWidth(NUMTY) /Int 8 [preserves-definedness]
  rule #alignOf(_, typeInfoPrimitiveType(primTypeFloat(NUMTY))) => #bitWidth(NUMTY) /Int 8 [preserves-definedness]
  // bool and char
  rule #sizeOf(_, typeInfoPrimitiveType(primTypeBool))  => 1
  rule #alignOf(_, typeInfoPrimitiveType(primTypeBool)) => 1
  rule #sizeOf(_, typeInfoPrimitiveType(primTypeChar))  => 4
  rule #alignOf(_, typeInfoPrimitiveType(primTypeChar)) => 4
  // The str primitive has alignment of a Char but size 0 (indicating dynamic size)
  rule #sizeOf(_, typeInfoPrimitiveType(primTypeStr))  => 0
  rule #alignOf(_, typeInfoPrimitiveType(primTypeStr)) => 4
  // enums, structs , and tuples provide the values from their layout information
  rule #sizeOf(_, typeInfoEnumType(_, _, _, _, someLayoutShape(layoutShape(_, _, _, _, machineSize(   BITS     ))))) => BITS /Int 8 [preserves-definedness]
  rule #sizeOf(_, typeInfoEnumType(_, _, _, _, someLayoutShape(layoutShape(_, _, _, _, machineSize(mirInt(BITS)))))) => BITS /Int 8 [preserves-definedness]
  rule #sizeOf(_, typeInfoEnumType(_, _, _, _, noLayoutShape)) => 0
  rule #alignOf(_, typeInfoEnumType(_, _, _, _, someLayoutShape(layoutShape(_, _, _, align(BYTES),_)))) => BYTES
  rule #alignOf(_, typeInfoEnumType(_, _, _, _, noLayoutShape)) => 1
  // struct
  rule #sizeOf(_, typeInfoStructType(_, _, _, someLayoutShape(layoutShape(_, _, _, _, machineSize(   BITS     ))))) => BITS /Int 8 [preserves-definedness]
  rule #sizeOf(_, typeInfoStructType(_, _, _, someLayoutShape(layoutShape(_, _, _, _, machineSize(mirInt(BITS)))))) => BITS /Int 8 [preserves-definedness]
  rule #sizeOf(_, typeInfoStructType(_, _, _, noLayoutShape)) => 0
  rule #alignOf(_, typeInfoStructType(_, _, _, someLayoutShape(layoutShape(_, _, _, align(BYTES),_)))) => BYTES
  rule #alignOf(_, typeInfoStructType(_, _, _, noLayoutShape)) => 1
  // tuple
  rule #sizeOf(_, typeInfoTupleType(_, someLayoutShape(layoutShape(_, _, _, _, machineSize(   BITS     ))))) => BITS /Int 8 [preserves-definedness]
  rule #sizeOf(_, typeInfoTupleType(_, someLayoutShape(layoutShape(_, _, _, _, machineSize(mirInt(BITS)))))) => BITS /Int 8 [preserves-definedness]
  rule #sizeOf(_, typeInfoTupleType(_, noLayoutShape)) => 0
  rule #alignOf(_, typeInfoTupleType(_, someLayoutShape(layoutShape(_, _, _, align(BYTES),_)))) => BYTES
  rule #alignOf(_, typeInfoTupleType(_, noLayoutShape)) => 1
  // union
  rule #sizeOf(_, typeInfoUnionType(_, _, _, someLayoutShape(layoutShape(_, _, _, _, machineSize(   BITS     ))))) => BITS /Int 8 [preserves-definedness]
  rule #sizeOf(_, typeInfoUnionType(_, _, _, someLayoutShape(layoutShape(_, _, _, _, machineSize(mirInt(BITS)))))) => BITS /Int 8 [preserves-definedness]
  rule #sizeOf(_, typeInfoUnionType(_, _, _, noLayoutShape)) => 0
  rule #alignOf(_, typeInfoUnionType(_, _, _, someLayoutShape(layoutShape(_, _, _, align(BYTES),_)))) => BYTES
  rule #alignOf(_, typeInfoUnionType(_, _, _, noLayoutShape)) => 1
  // arrays with no known length
  rule #sizeOf(_, typeInfoArrayType(  _    ,    noTyConst                 )) => 0
  // thin ptr and ref types have the size of `usize` and twice that for fat pointers/refs. Alignment is that of `usize`
  rule #sizeOf(TYPESMAP, typeInfoPtrType(POINTEE_TY))
    => #sizeOf(TYPESMAP, typeInfoPrimitiveType(primTypeUint(uintTyUsize)))
          *Int (#if #metadataSize(TYPESMAP, POINTEE_TY) ==K dynamicSize(1) #then 2 #else 1 #fi)
  rule #sizeOf(TYPESMAP, typeInfoRefType(POINTEE_TY))
    => #sizeOf(TYPESMAP, typeInfoPrimitiveType(primTypeUint(uintTyUsize)))
          *Int (#if #metadataSize(TYPESMAP, POINTEE_TY) ==K dynamicSize(1) #then 2 #else 1 #fi)
  rule #alignOf(TYPESMAP, typeInfoPtrType(_)) => #alignOf(TYPESMAP, typeInfoPrimitiveType(primTypeUint(uintTyUsize)))
  rule #alignOf(TYPESMAP, typeInfoRefType(_)) => #alignOf(TYPESMAP, typeInfoPrimitiveType(primTypeUint(uintTyUsize)))
  // other types (fun and void types) have size and alignment 0
  rule #sizeOf(_, _)  => 0 [owise]
  rule #alignOf(_, _) => 0 [owise]
```

Arrays with known length have the alignment of the element type, and a size multiplying element count and element size:

```{.k .concrete}
  rule #sizeOf(TYPESMAP, typeInfoArrayType(ELEM_TY, someTyConst(tyConst(KIND, _)))) => #sizeOf(TYPESMAP, lookupTy(TYPESMAP, ELEM_TY)) *Int readTyConstInt(TYPESMAP, KIND)
  rule #alignOf(TYPESMAP, typeInfoArrayType(ELEM_TY, _)) => #alignOf(TYPESMAP, lookupTy(TYPESMAP, ELEM_TY))
```

```{.k .symbolic}
  rule #sizeOf(_, typeInfoArrayType(ELEM_TY, someTyConst(tyConst(KIND, _)))) => #sizeOf(noMap, lookupTyKore(ELEM_TY)) *Int readTyConstInt(noMap, KIND)
  rule #alignOf(_, typeInfoArrayType(ELEM_TY, _)) => #alignOf(noMap, lookupTyKore(ELEM_TY))
```

```k
endmodule
```
