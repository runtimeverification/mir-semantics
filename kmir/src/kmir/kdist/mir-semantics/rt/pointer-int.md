# Pointer/Integer Encoding Helpers

This module defines the reversible encoding used for pointer/int transmutes.
We keep these helpers isolated from `RT-DATA` so GitHub reviews stay focused
on the semantics while still reusing exactly the same encoding/decoding logic.
The encoding works by flattening every pointer component into a single natural
number, using Cantor pairing to store the following pieces in order:

1. Stack depth (`PtrLocal` provenance)
2. Place + projection list (locals, fields, etc.)
3. Mutability flag
4. Metadata triple (`MetadataSize`, pointer offset, original metadata)
5. Logical pointer offset converted into bytes when a pointee `Ty` is known

Decoding simply applies the inverse Cantor functions to rebuild the original
`PtrLocal`, metadata, and projection structure before reinterpreting offsets.

```k
requires "../body.md"
requires "./value.md"
requires "./types.md"
requires "./decoding.md"

module RT-POINTER-INT
  imports BOOL
  imports INT
  imports BODY
  imports RT-VALUE-SYNTAX
  imports RT-TYPES
  imports RT-DECODING

  syntax ProjectionElem ::= PointerOffset( Int , Int )

  syntax Int ::= #intToNat ( Int ) [function, total]
  rule #intToNat(VAL) => 2 *Int VAL
    requires VAL >=Int 0
  rule #intToNat(VAL) => 0 -Int (2 *Int VAL) -Int 1
    requires VAL <Int 0

  syntax Int ::= #natToInt ( Int ) [function, total]
  rule #natToInt(N) => N /Int 2
    requires N >=Int 0
     andBool N modInt 2 ==Int 0
  rule #natToInt(N) => 0 -Int ((N +Int 1) /Int 2)
    requires N >=Int 0
     andBool N modInt 2 ==Int 1

  syntax Int ::= #tri ( Int ) [function, total]
  rule #tri(T) => (T *Int (T +Int 1)) /Int 2

  syntax Int ::= #cantorPair ( Int , Int ) [function, total]
  rule #cantorPair(A, B)
    => ((A +Int B) *Int (A +Int B +Int 1)) /Int 2 +Int B
    requires A >=Int 0
     andBool B >=Int 0

  syntax Int ::= #cantorUnpairLeft ( Int ) [function, total]
  syntax Int ::= #cantorUnpairRight( Int ) [function, total]
  syntax Int ::= #cantorUnpairLeftAux ( Int , Int ) [function, total]
  syntax Int ::= #cantorUnpairRightAux( Int , Int ) [function, total]

  rule #cantorUnpairLeft(Z) => #cantorUnpairLeftAux(Z, 0)
    requires Z >=Int 0
  rule #cantorUnpairLeftAux(Z, T)
    => T -Int (#tri(T) -Int Z)
    requires Z <Int #tri(T)
  rule #cantorUnpairLeftAux(Z, T)
    => #cantorUnpairLeftAux(Z, T +Int 1)
    requires Z >=Int #tri(T)

  rule #cantorUnpairRight(Z) => #cantorUnpairRightAux(Z, 0)
    requires Z >=Int 0
  rule #cantorUnpairRightAux(Z, T)
    => Z -Int #tri(T)
    requires Z <Int #tri(T)
  rule #cantorUnpairRightAux(Z, T)
    => #cantorUnpairRightAux(Z, T +Int 1)
    requires Z >=Int #tri(T)

  syntax Int ::= #encodeBool ( Bool ) [function, total]
  syntax Bool ::= #decodeBool ( Int ) [function, total]
  rule #encodeBool(false) => 0
  rule #encodeBool(true)  => 1
  rule #decodeBool(0) => false
  rule #decodeBool(1) => true
  rule #decodeBool(_) => false [owise]

  syntax Int ::= #encodeMIRBool ( MIRBool ) [function, total]
  syntax MIRBool ::= #decodeMIRBool ( Int ) [function, total]
  rule #encodeMIRBool(mirBool(B)) => #encodeBool(B)
  rule #encodeMIRBool(_) => 0 [owise]
  rule #decodeMIRBool(N) => mirBool(#decodeBool(N))

  syntax Int ::= #encodeMIRInt ( MIRInt ) [function, total]
  syntax MIRInt ::= #decodeMIRInt ( Int ) [function, total]
  rule #encodeMIRInt(mirInt(I)) => #intToNat(I)
  rule #encodeMIRInt(_) => 0 [owise]
  rule #decodeMIRInt(N) => mirInt(#natToInt(N))

  syntax Int ::= #encodeLocal ( Local ) [function, total]
  syntax Local ::= #decodeLocal ( Int ) [function, total]
  rule #encodeLocal(local(I)) => #intToNat(I)
  rule #decodeLocal(N) => local(#natToInt(N))
    requires N >=Int 0

  syntax Int ::= #encodeFieldIdx ( FieldIdx ) [function, total]
  syntax FieldIdx ::= #decodeFieldIdx ( Int ) [function, total]
  rule #encodeFieldIdx(fieldIdx(I)) => #intToNat(I)
  rule #decodeFieldIdx(N) => fieldIdx(#natToInt(N))
    requires N >=Int 0

  syntax Int ::= #encodeVariantIdx ( VariantIdx ) [function, total]
  syntax VariantIdx ::= #decodeVariantIdx ( Int ) [function, total]
  rule #encodeVariantIdx(variantIdx(I)) => #intToNat(I)
  rule #encodeVariantIdx(_) => 0 [owise]
  rule #decodeVariantIdx(N) => variantIdx(#natToInt(N))
    requires N >=Int 0

  syntax Int ::= #encodeTy ( Ty ) [function, total]
  syntax Ty ::= #decodeTy ( Int ) [function, total]
  rule #encodeTy(ty(I)) => #intToNat(I)
  rule #decodeTy(N) => ty(#natToInt(N))
    requires N >=Int 0

  syntax Int ::= #encodeMutability ( Mutability ) [function, total]
  syntax Mutability ::= #decodeMutability ( Int ) [function, total]
  rule #encodeMutability(mutabilityNot) => 0
  rule #encodeMutability(mutabilityMut) => 1
  rule #decodeMutability(0) => mutabilityNot
  rule #decodeMutability(1) => mutabilityMut
  rule #decodeMutability(_) => mutabilityNot [owise]

  syntax Int ::= #encodeMetadataSize ( MetadataSize ) [function, total]
  syntax MetadataSize ::= #decodeMetadataSize ( Int ) [function, total]
  rule #encodeMetadataSize(noMetadataSize) => 0
  rule #encodeMetadataSize(staticSize(SIZE)) => 1 +Int #cantorPair(0, #intToNat(SIZE))
  rule #encodeMetadataSize(dynamicSize(SIZE)) => 1 +Int #cantorPair(1, #intToNat(SIZE))
  rule #decodeMetadataSize(0) => noMetadataSize
  rule #decodeMetadataSize(ENC)
    => staticSize(#natToInt(#cantorUnpairRight(ENC -Int 1)))
    requires ENC >Int 0
     andBool #cantorUnpairLeft(ENC -Int 1) ==Int 0
  rule #decodeMetadataSize(ENC)
    => dynamicSize(#natToInt(#cantorUnpairRight(ENC -Int 1)))
    requires ENC >Int 0
     andBool #cantorUnpairLeft(ENC -Int 1) ==Int 1

  syntax Int ::= #encodeMetadata ( Metadata ) [function, total]
  syntax Metadata ::= #decodeMetadata ( Int ) [function, total]
  rule #encodeMetadata(metadata(SIZE, PTR_OFFSET, ORIGIN))
    => #cantorPair(
         #encodeMetadataSize(SIZE),
         #cantorPair(#intToNat(PTR_OFFSET), #encodeMetadataSize(ORIGIN))
       )
  rule #decodeMetadata(ENC)
    => metadata(
         #decodeMetadataSize(#cantorUnpairLeft(ENC)),
         #natToInt(#cantorUnpairLeft(#cantorUnpairRight(ENC))),
         #decodeMetadataSize(#cantorUnpairRight(#cantorUnpairRight(ENC)))
       )
    requires ENC >=Int 0

  syntax Int ::= #encodeProjectionElem ( ProjectionElem ) [function, total]
  syntax ProjectionElem ::= #decodeProjectionElem ( Int ) [function, total]
  rule #encodeProjectionElem(projectionElemDeref) => 0
  rule #encodeProjectionElem(projectionElemField(FIELD, TY))
    => 1 +Int #cantorPair(0, #cantorPair(#encodeFieldIdx(FIELD), #encodeTy(TY)))
  rule #encodeProjectionElem(projectionElemIndex(LOCAL))
    => 1 +Int #cantorPair(1, #encodeLocal(LOCAL))
  rule #encodeProjectionElem(projectionElemConstantIndex(OFFSET, MIN, FROM_END))
    => 1 +Int #cantorPair(
         2,
         #cantorPair(
           #encodeMIRInt(OFFSET),
           #cantorPair(#encodeMIRInt(MIN), #encodeMIRBool(FROM_END))
         )
       )
  rule #encodeProjectionElem(projectionElemSubslice(FROM, TO, FROM_END))
    => 1 +Int #cantorPair(
         3,
         #cantorPair(
           #encodeMIRInt(FROM),
           #cantorPair(#encodeMIRInt(TO), #encodeMIRBool(FROM_END))
         )
       )
  rule #encodeProjectionElem(projectionElemDowncast(VARIANT))
    => 1 +Int #cantorPair(4, #encodeVariantIdx(VARIANT))
  rule #encodeProjectionElem(projectionElemOpaqueCast(TY))
    => 1 +Int #cantorPair(5, #encodeTy(TY))
  rule #encodeProjectionElem(projectionElemSubtype(TY))
    => 1 +Int #cantorPair(6, #encodeTy(TY))
  rule #encodeProjectionElem(PointerOffset(OFFSET, LEN))
    => 1 +Int #cantorPair(7, #cantorPair(#intToNat(OFFSET), #intToNat(LEN)))

  rule #decodeProjectionElem(0) => projectionElemDeref
  rule #decodeProjectionElem(ENC)
    => projectionElemField(
         #decodeFieldIdx(#cantorUnpairLeft(#cantorUnpairRight(ENC -Int 1))),
         #decodeTy(#cantorUnpairRight(#cantorUnpairRight(ENC -Int 1)))
       )
    requires ENC >Int 0
     andBool #cantorUnpairLeft(ENC -Int 1) ==Int 0
  rule #decodeProjectionElem(ENC)
    => projectionElemIndex(#decodeLocal(#cantorUnpairRight(ENC -Int 1)))
    requires ENC >Int 0
     andBool #cantorUnpairLeft(ENC -Int 1) ==Int 1
  rule #decodeProjectionElem(ENC)
    => projectionElemConstantIndex(
         #decodeMIRInt(#cantorUnpairLeft(#cantorUnpairRight(ENC -Int 1))),
         #decodeMIRInt(#cantorUnpairLeft(#cantorUnpairRight(#cantorUnpairRight(ENC -Int 1)))),
         #decodeMIRBool(#cantorUnpairRight(#cantorUnpairRight(#cantorUnpairRight(ENC -Int 1))))
       )
    requires ENC >Int 0
     andBool #cantorUnpairLeft(ENC -Int 1) ==Int 2
  rule #decodeProjectionElem(ENC)
    => projectionElemSubslice(
         #decodeMIRInt(#cantorUnpairLeft(#cantorUnpairRight(ENC -Int 1))),
         #decodeMIRInt(#cantorUnpairLeft(#cantorUnpairRight(#cantorUnpairRight(ENC -Int 1)))),
         #decodeMIRBool(#cantorUnpairRight(#cantorUnpairRight(#cantorUnpairRight(ENC -Int 1))))
       )
    requires ENC >Int 0
     andBool #cantorUnpairLeft(ENC -Int 1) ==Int 3
  rule #decodeProjectionElem(ENC)
    => projectionElemDowncast(#decodeVariantIdx(#cantorUnpairRight(ENC -Int 1)))
    requires ENC >Int 0
     andBool #cantorUnpairLeft(ENC -Int 1) ==Int 4
  rule #decodeProjectionElem(ENC)
    => projectionElemOpaqueCast(#decodeTy(#cantorUnpairRight(ENC -Int 1)))
    requires ENC >Int 0
     andBool #cantorUnpairLeft(ENC -Int 1) ==Int 5
  rule #decodeProjectionElem(ENC)
    => projectionElemSubtype(#decodeTy(#cantorUnpairRight(ENC -Int 1)))
    requires ENC >Int 0
     andBool #cantorUnpairLeft(ENC -Int 1) ==Int 6
  rule #decodeProjectionElem(ENC)
    => PointerOffset(
         #natToInt(#cantorUnpairLeft(#cantorUnpairRight(ENC -Int 1))),
         #natToInt(#cantorUnpairRight(#cantorUnpairRight(ENC -Int 1)))
       )
    requires ENC >Int 0

  syntax Int ::= #encodeProjectionElems ( ProjectionElems ) [function, total]
  syntax ProjectionElems ::= #decodeProjectionElems ( Int ) [function, total]
  rule #encodeProjectionElems(.ProjectionElems) => 0
  rule #encodeProjectionElems(PROJ PROJS)
    => 1 +Int #cantorPair(#encodeProjectionElem(PROJ), #encodeProjectionElems(PROJS))

  rule #decodeProjectionElems(0) => .ProjectionElems
  rule #decodeProjectionElems(ENC)
    => #decodeProjectionElem(#cantorUnpairLeft(ENC -Int 1))
       #decodeProjectionElems(#cantorUnpairRight(ENC -Int 1))
    requires ENC >Int 0

  syntax Int ::= #encodePlace ( Place ) [function, total]
  syntax Place ::= #decodePlace ( Int ) [function, total]
  rule #encodePlace(place(LOCAL, PROJS))
    => #cantorPair(#encodeLocal(LOCAL), #encodeProjectionElems(PROJS))
  rule #decodePlace(ENC)
    => place(
         #decodeLocal(#cantorUnpairLeft(ENC)),
         #decodeProjectionElems(#cantorUnpairRight(ENC))
       )
    requires ENC >=Int 0

  syntax Int ::= #encodePtrBase ( Value ) [function, total]
  syntax Value ::= #decodePtrBase ( Int ) [function, total]
  rule #encodePtrBase(PtrLocal(STACK, PLACE, MUT, META))
    => #cantorPair(
         #intToNat(STACK),
         #cantorPair(
           #encodePlace(PLACE),
           #cantorPair(#encodeMutability(MUT), #encodeMetadata(META))
         )
       )
  rule #encodePtrBase(_OTHER:Value) => 0 [owise]

  rule #decodePtrBase(ENC)
    => PtrLocal(
         #natToInt(#cantorUnpairLeft(ENC)),
         #decodePlace(#cantorUnpairLeft(#cantorUnpairRight(ENC))),
         #decodeMutability(#cantorUnpairLeft(#cantorUnpairRight(#cantorUnpairRight(ENC)))),
         #decodeMetadata(#cantorUnpairRight(#cantorUnpairRight(ENC)))
       )
    requires ENC >=Int 0

  syntax Int ::= #ptrOffsetBytes ( Int , MaybeTy ) [function, total]
  rule #ptrOffsetBytes(PTR_OFFSET, TyUnknown) => PTR_OFFSET
  rule #ptrOffsetBytes(PTR_OFFSET, TY:Ty) => PTR_OFFSET *Int #elemSize(lookupTy(TY))

  syntax Int ::= #bytesToPtrOffset ( Int , MaybeTy ) [function, total]
  rule #bytesToPtrOffset(BYTES, TyUnknown) => BYTES
  rule #bytesToPtrOffset(BYTES, TY:Ty)
    => BYTES /Int #elemSize(lookupTy(TY))
    requires #elemSize(lookupTy(TY)) >Int 0
     andBool BYTES modInt #elemSize(lookupTy(TY)) ==Int 0

  syntax Int ::= #encodePtrInt ( Value , MaybeTy ) [function, total]
  rule #encodePtrInt(PtrLocal(STACK, PLACE, MUT, metadata(SIZE, PTR_OFFSET, ORIGIN)), TY)
    => #cantorPair(
         #encodePtrBase(PtrLocal(STACK, PLACE, MUT, metadata(SIZE, PTR_OFFSET, ORIGIN))),
         #ptrOffsetBytes(PTR_OFFSET, TY)
       )
  rule #encodePtrInt(_OTHER:Value, _) => 0 [owise]

  // Helper to materialise the Cantor-encoded pointer into either a signed or unsigned Integer.
  syntax Value ::= #ptrIntValue ( Int , NumTy ) [function, total]
  rule #ptrIntValue(ENC, INTTY:IntTy)
    => Integer(ENC, #bitWidth(INTTY), true)
  rule #ptrIntValue(ENC, UINTTY:UintTy)
    => Integer(ENC, #bitWidth(UINTTY), false)
  rule #ptrIntValue(_, FLOATTY:FloatTy)
    => Integer(0, #bitWidth(FLOATTY), false)
  rule #ptrIntValue(_, _) => Integer(0, 0, false) [owise]

  syntax Int ::= #unsignedFromIntValue ( Int , Int , Bool ) [function, total]
  rule #unsignedFromIntValue(VAL, _WIDTH, _SIGNED) => VAL
    requires VAL >=Int 0
  rule #unsignedFromIntValue(VAL, WIDTH, _SIGNED)
    => VAL +Int (1 <<Int WIDTH)
    requires VAL <Int 0

endmodule
```
