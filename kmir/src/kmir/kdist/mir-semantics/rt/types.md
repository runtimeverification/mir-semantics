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

When two types use the same representation for their values, these
values, and pointers to them, can be converted from one type to the other.
The `#typesCompatible` function determines this compatibility, and is by default `false`.

```k
  syntax Bool ::= #typesCompatible ( TypeInfo , TypeInfo , Map ) [function, total]

  // by default, only identical types are compatible
  rule #typesCompatible (             T            ,           T              ,   _    ) => true  [priority(60)] 
  rule #typesCompatible (             _            ,           _              ,   _    ) => false [owise] 
```

Arrays and slices are compatible if their element type is (ignoring length)
```k
  rule #typesCompatible ( typeInfoArrayType(TY1, _), typeInfoArrayType(TY2, _), TYPEMAP) => #typesCompatible({TYPEMAP[TY1]}:>TypeInfo, {TYPEMAP[TY2]}:>TypeInfo, TYPEMAP)
    requires isTypeInfo(TYPEMAP[TY1])
     andBool isTypeInfo(TYPEMAP[TY2])
```

Pointers are compatible if their pointee types are
```k
  rule #typesCompatible ( typeInfoPtrType(TY1)     , typeInfoPtrType(TY2)     , TYPEMAP) => true
    requires isTypeInfo(TYPEMAP[TY1])
     andBool isTypeInfo(TYPEMAP[TY2])
     andBool #typesCompatible({TYPEMAP[TY1]}:>TypeInfo, {TYPEMAP[TY2]}:>TypeInfo, TYPEMAP)
     [priority(59)]
```

Pointers to arrays/slices are compatible with pointers to the element type
```k
  rule #typesCompatible ( typeInfoPtrType(TY1)     , typeInfoPtrType(TY2)     , TYPEMAP) => true
    requires isTypeInfo(TYPEMAP[TY1])
     andBool #isArrayOf({TYPEMAP[TY1]}:>TypeInfo, TY2)

  rule #typesCompatible ( typeInfoPtrType(TY1)     , typeInfoPtrType(TY2)     , TYPEMAP) => true
    requires isTypeInfo(TYPEMAP[TY2])
     andBool #isArrayOf({TYPEMAP[TY2]}:>TypeInfo, TY1)

  syntax Bool ::= #isArrayOf ( TypeInfo , Ty ) [function, total]

  rule #isArrayOf(typeInfoArrayType(TY, _), TY) => true
  rule #isArrayOf(      _                 , _ ) => false [owise]
```

## Determining types of places with projection

A helper function `getTyOf` traverses type metadata (using the type metadata map `Ty -> TypeInfo`) along the applied projections to determine the `Ty` of the projected place.
To make this function total, an optional `MaybeTy` is used.

```k
  syntax MaybeTy ::= Ty
                   | "TyUnknown"

  syntax MaybeTy ::= getTyOf( MaybeTy , ProjectionElems ,  Map ) [function, total]
  // -----------------------------------------------------------
  rule getTyOf(TyUnknown,             _                      ,     _    ) => TyUnknown
  rule getTyOf(TY,                    .ProjectionElems       ,     _    ) => TY

  rule getTyOf(TY, projectionElemDeref                  PROJS, TYPEMAP ) => getTyOf(pointeeTy({TYPEMAP[TY]}:>TypeInfo), PROJS, TYPEMAP)
    requires TY in_keys(TYPEMAP) andBool isTypeInfo(TYPEMAP[TY])
  rule getTyOf( _, projectionElemField(_, TY)           PROJS, TYPEMAP ) => getTyOf(TY, PROJS, TYPEMAP) // could also look it up
  
  rule getTyOf(TY, projectionElemIndex(_)               PROJS, TYPEMAP ) => getTyOf(elemTy({TYPEMAP[TY]}:>TypeInfo), PROJS, TYPEMAP)
    requires TY in_keys(TYPEMAP) andBool isTypeInfo(TYPEMAP[TY])
  rule getTyOf(TY, projectionElemConstantIndex(_, _, _) PROJS, TYPEMAP ) => getTyOf(elemTy({TYPEMAP[TY]}:>TypeInfo), PROJS, TYPEMAP)
    requires TY in_keys(TYPEMAP) andBool isTypeInfo(TYPEMAP[TY])
  rule getTyOf(TY, projectionElemSubslice(_, _, _)      PROJS, TYPEMAP ) => getTyOf(TY, PROJS, TYPEMAP) // TODO assumes TY is already a slice type

  rule getTyOf(TY, projectionElemDowncast(_)            PROJS, TYPEMAP ) => getTyOf(TY, PROJS, TYPEMAP) // unchanged type, just setting variantIdx

  rule getTyOf( _, projectionElemOpaqueCast(TY)         PROJS, TYPEMAP ) => getTyOf(TY, PROJS, TYPEMAP)

  rule getTyOf( _, projectionElemSubtype(TY)            PROJS, TYPEMAP ) => getTyOf(TY, PROJS, TYPEMAP)
  // -----------------------------------------------------------
  rule getTyOf(_, _, _) => TyUnknown [owise]


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
The helper function `#metadata` determines whether or not a given `TypeInfo` requires size information or other metadata (also see `Metadata` sort in `value.md`).
To avoid repeated lookups, static array sizes are also stored as metadata (for `Unsize` casts).

NB that the need for metadata is determined for the _pointee_ type, not the pointer type.

A [similar function exists in `rustc`](https://doc.rust-lang.org/nightly/nightly-rustc/src/rustc_middle/ty/util.rs.html#224-235) to determine whether or not a type needs dynamic metadata.
Slices, `str`s  and dynamic types require it, and any `Ty` that `is_sized` does not.

```k
  syntax Metadata ::= #metadata    ( Ty , ProjectionElems , Map ) [function, total]
                    | #metadata    (  MaybeTy , Map )             [function, total]
                    | #metadataAux ( TypeInfo , Map )             [function, total]
  // ------------------------------------------------------------
  rule #metadata(TY, PROJS, TYPEMAP) => #metadata(getTyOf(TY, PROJS, TYPEMAP), TYPEMAP)

  rule #metadata(TY, TYPEMAP) => #metadataAux({TYPEMAP[TY]}:>TypeInfo, TYPEMAP)
    requires TY in_keys(TYPEMAP) andBool isTypeInfo(TYPEMAP[TY]) [preserves-definedness] // valid map key and sort coercion
  rule #metadata( _,       _) => noMetadata [owise, preserves-definedness]  // if the type is not known, assume no metadata is required

  rule #metadataAux(typeInfoArrayType(_, noTyConst                     ),    _   ) => dynamicSize(1)
  rule #metadataAux(typeInfoArrayType(_, someTyConst(tyConst(CONST, _))), TYPEMAP) => staticSize(readTyConstInt(CONST, TYPEMAP))
  rule #metadataAux(    _OTHER                                          ,    _   ) => noMetadata     [owise]
```


```k
  // reading Int-valued TyConsts from allocated bytes
  syntax Int ::= readTyConstInt ( TyConstKind , Map ) [function]
  // -----------------------------------------------------------
  rule readTyConstInt( tyConstKindValue(TY, allocation(BYTES, _, _, _)), TYPEMAP) => Bytes2Int(BYTES, LE, Unsigned)
    requires isUintTy(#numTypeOf({TYPEMAP[TY]}:>TypeInfo))
     andBool lengthBytes(BYTES) ==Int #bitWidth(#numTypeOf({TYPEMAP[TY]}:>TypeInfo)) /Int 8
    [preserves-definedness]

  rule readTyConstInt( tyConstKindValue(TY, allocation(BYTES, _, _, _)), TYPEMAP) => Bytes2Int(BYTES, LE, Signed  )
    requires isIntTy(#numTypeOf({TYPEMAP[TY]}:>TypeInfo))
     andBool lengthBytes(BYTES) ==Int #bitWidth(#numTypeOf({TYPEMAP[TY]}:>TypeInfo)) /Int 8
    [preserves-definedness]
```

```k
endmodule
```
