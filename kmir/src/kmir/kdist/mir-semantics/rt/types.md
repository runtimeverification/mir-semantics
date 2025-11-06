# Helpers for type metadata (`TypeInfo`)

```k
requires "../ty.md"
requires "../body.md"
requires "numbers.md"
requires "value.md"

module RT-TYPES
  imports BOOL
  imports INT
  imports STRING
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

When two types use the same representation for their values, these
values, and pointers to them, can be converted from one type to the other.
The `#typesCompatible` function determines this compatibility, and is by default `false`.

```k
  syntax Bool ::= #typesCompatible ( TypeInfo , TypeInfo ) [function, total]

  // by default, only identical types are compatible
  rule #typesCompatible (             T            ,           T              ) => true  [priority(60)] 
  rule #typesCompatible (             _            ,           _              ) => false [owise] 
```

Arrays and slices are compatible if their element type is (ignoring length)
```k
  rule #typesCompatible ( typeInfoArrayType(TY1, _), typeInfoArrayType(TY2, _)) => #typesCompatible(lookupTy(TY1), lookupTy(TY2))
```

Pointers are compatible if their pointee types are
```k
  rule #typesCompatible ( typeInfoPtrType(TY1)     , typeInfoPtrType(TY2)     ) => true
    requires #typesCompatible(lookupTy(TY1), lookupTy(TY2))
     [priority(59)]
```

Pointers to arrays/slices are compatible with pointers to the element type
```k
  rule #typesCompatible ( typeInfoPtrType(TY1)     , typeInfoPtrType(TY2)     ) => true
    requires #isArrayOf(lookupTy(TY1), TY2)

  rule #typesCompatible ( typeInfoPtrType(TY1)     , typeInfoPtrType(TY2)     ) => true
    requires #isArrayOf(lookupTy(TY2), TY1)

  syntax Bool ::= #isArrayOf ( TypeInfo , Ty ) [function, total]

  rule #isArrayOf(typeInfoArrayType(TY, _), TY) => true
  rule #isArrayOf(      _                 , _ ) => false [owise]

  rule #typesCompatible(SRC, OTHER) => true
    requires #zeroSizedType(SRC) orBool #zeroSizedType(OTHER)

  syntax Bool ::= #zeroSizedType ( TypeInfo ) [function, total]

  rule #zeroSizedType(typeInfoTupleType(.Tys)) => true
  rule #zeroSizedType(typeInfoStructType(_, _, .Tys, _)) => true
  rule #zeroSizedType(typeInfoVoidType) => true
  // FIXME: Only unit tuples, empty structs, and void are recognized here; other
  // zero-sized types (e.g. single-variant enums, function or closure items,
  // newtype wrappers around ZSTs) still fall through because we do not consult
  // the layout metadata yet. Update once we rely on machineSize(0).
  rule #zeroSizedType(_) => false [owise]

  rule #typesCompatible(typeInfoStructType(_, _, FIELD .Tys, LAYOUT), OTHER)
    => #typesCompatible(lookupTy(FIELD), OTHER)
    requires #zeroFieldOffset(LAYOUT)

  rule #typesCompatible(OTHER, typeInfoStructType(_, _, FIELD .Tys, LAYOUT))
    => #typesCompatible(OTHER, lookupTy(FIELD))
    requires #zeroFieldOffset(LAYOUT)

  syntax Bool ::= #zeroFieldOffset ( MaybeLayoutShape ) [function, total]

  rule #zeroFieldOffset(LAYOUT)
    =>      #structOffsets(LAYOUT) ==K .MachineSizes
     orBool #structOffsets(LAYOUT) ==K machineSize(mirInt(0)) .MachineSizes
     orBool #structOffsets(LAYOUT) ==K machineSize(0) .MachineSizes

  syntax MachineSizes ::= #structOffsets ( MaybeLayoutShape ) [function, total]

  rule #structOffsets(someLayoutShape(layoutShape(fieldsShapeArbitrary(mk(OFFSETS)), _, _, _, _))) => OFFSETS
  rule #structOffsets(_) => .MachineSizes [owise]

  syntax Bool ::= #allowsInteriorMutation(TypeInfo) [function, total]

  rule #allowsInteriorMutation(typeInfoStructType(mirString(NAME), _, _, _))
    => findString(NAME, "UnsafeCell", 0) =/=Int -1
  rule #allowsInteriorMutation(typeInfoStructType(NAME:String, _, _, _))
    => findString(NAME, "UnsafeCell", 0) =/=Int -1
  rule #allowsInteriorMutation(_) => false [owise]

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

  syntax TypeInfo ::= #lookupMaybeTy ( MaybeTy ) [function, total]

  rule #lookupMaybeTy(TY:Ty) => lookupTy(TY)
  rule #lookupMaybeTy(TyUnknown) => typeInfoVoidType

  syntax MaybeTy ::= getTyOf( MaybeTy , ProjectionElems ) [function, total]
  // -----------------------------------------------------------
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

```k
endmodule
```
