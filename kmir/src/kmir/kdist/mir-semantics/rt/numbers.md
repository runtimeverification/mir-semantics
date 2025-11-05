# Implementation of Number Types in MIR Semantics

The code in this file implements functionality for `Integer` and `Float` values in `mir-semantics`.

```k
requires "./value.md"
requires "../ty.md"

module RT-NUMBERS
  imports TYPES
  imports RT-VALUE-SYNTAX

  imports BOOL
  imports BYTES
  imports INT
```

## Helpers and Constants for Integer Operations

```k
  syntax NumTy ::= InTy | FloatTy

  syntax InTy  ::= IntTy | UintTy

  syntax NumTy ::= #numTypeOf( TypeInfo ) [function]
  // ----------------------------------------------
  rule #numTypeOf(typeInfoPrimitiveType(primTypeInt(INTTY))) => INTTY
  rule #numTypeOf(typeInfoPrimitiveType(primTypeUint(UINTTY))) => UINTTY
  rule #numTypeOf(typeInfoPrimitiveType(primTypeFloat(FLOATTY))) => FLOATTY

  syntax InTy ::= #intTypeOf( TypeInfo ) [function]
  // ----------------------------------------------
  rule #intTypeOf(typeInfoPrimitiveType(primTypeInt(INTTY))) => INTTY
  rule #intTypeOf(typeInfoPrimitiveType(primTypeUint(UINTTY))) => UINTTY

  syntax Bool ::= #isIntType ( TypeInfo ) [function, total]
  // -----------------------------------------------------
  rule #isIntType(typeInfoPrimitiveType(primTypeInt(_)))  => true
  rule #isIntType(typeInfoPrimitiveType(primTypeUint(_))) => true
  rule #isIntType(_)                                 => false [owise]
```

Constants used for overflow-checking and truncation are defined here as macros.
The `#bitWidth` is defined as a function so it can be called dynamically.

```k
  syntax Int ::= #bitWidth( NumTy ) [function]
  // ------------------------------
  rule #bitWidth(intTyIsize) => 64 // on 64-bit systems
  rule #bitWidth(intTyI8   ) => 8
  rule #bitWidth(intTyI16  ) => 16
  rule #bitWidth(intTyI32  ) => 32
  rule #bitWidth(intTyI64  ) => 64
  rule #bitWidth(intTyI128 ) => 128
  rule #bitWidth(uintTyUsize) => 64 // on 64-bit systems
  rule #bitWidth(uintTyU8   ) => 8
  rule #bitWidth(uintTyU16  ) => 16
  rule #bitWidth(uintTyU32  ) => 32
  rule #bitWidth(uintTyU64  ) => 64
  rule #bitWidth(uintTyU128 ) => 128
  rule #bitWidth(floatTyF16 ) => 16
  rule #bitWidth(floatTyF32 ) => 32
  rule #bitWidth(floatTyF64 ) => 64
  rule #bitWidth(floatTyF128) => 128
```

This truncation function is instrumental in the implementation of Integer arithmetic and overflow checking.

```k
  // helper function to truncate int values
  syntax Int ::= truncate(Int, Int, Signedness) [function, total, smtlib(smt_truncate)]
  // -------------------------------------------------------------
  rule truncate(_, WIDTH, _) => 0
    requires WIDTH <=Int 0
  // unsigned values can be truncated using a simple bitmask
  // NB if VAL is negative (underflow), the truncation will yield a positive number

  rule truncate(VAL, WIDTH, Unsigned)
      => // mask with relevant bits
        VAL &Int ((1 <<Int WIDTH) -Int 1)
    requires 0 <Int WIDTH
    [preserves-definedness]

  // for signed values we need to preserve/restore the sign
  rule truncate(VAL, WIDTH, Signed)
      => // if truncated value small enough and positive, all is done
          (VAL &Int ((1 <<Int WIDTH) -Int 1))
    requires 0 <Int WIDTH
     andBool VAL &Int ((1 <<Int WIDTH) -Int 1) <Int (1 <<Int (WIDTH -Int 1))
    [preserves-definedness]

  rule truncate(VAL, WIDTH, Signed)
      => // subtract a bias when the truncation result too large
          (VAL &Int ((1 <<Int WIDTH) -Int 1)) -Int (1 <<Int WIDTH)
    requires 0 <Int WIDTH
     andBool VAL &Int ((1 <<Int WIDTH) -Int 1) >=Int (1 <<Int (WIDTH -Int 1))
    [preserves-definedness]
```

## Decoding Integer values from `Bytes` for `OperandConstant`

```k
  syntax Value ::= #decodeInteger ( Bytes , InTy ) [function] // byte length is checked, partial
  // --------------------------------------------------------
  rule #decodeInteger(BYTES, INTTY:IntTy) => Integer(Bytes2Int(BYTES, LE, Signed), #bitWidth(INTTY), true)
    requires lengthBytes(BYTES) ==Int #bitWidth(INTTY) /Int 8
    [preserves-definedness]
  rule #decodeInteger(BYTES, UINTTY:UintTy) => Integer(Bytes2Int(BYTES, LE, Unsigned), #bitWidth(UINTTY), false)
    requires lengthBytes(BYTES) ==Int #bitWidth(UINTTY) /Int 8
    [preserves-definedness]
```

## Type Casts Between Different Numeric Types



```k
  syntax Value ::= #intAsType( Int, Int, NumTy ) [function]
  // ------------------------------------------------------
  // converting to signed int types:
  // narrowing or converting unsigned->signed: use truncation for signed numbers
  rule #intAsType(VAL, WIDTH, INTTYPE:IntTy)
      =>
        Integer(
          truncate(VAL, #bitWidth(INTTYPE), Signed),
          #bitWidth(INTTYPE),
          true
        )
    requires #bitWidth(INTTYPE) <=Int WIDTH

  // widening: nothing to do: VAL does not change (enough bits to represent, no sign change possible)
  rule #intAsType(VAL, WIDTH, INTTYPE:IntTy)
      =>
        Integer(VAL, #bitWidth(INTTYPE), true)
    requires WIDTH <Int #bitWidth(INTTYPE)

  // converting to unsigned int types (simple bitmask)
  rule #intAsType(VAL, _, UINTTYPE:UintTy)
      =>
        Integer(
          truncate(VAL, #bitWidth(UINTTYPE), Unsigned),
          #bitWidth(UINTTYPE),
          false
        )
```

## Alignment of Primitives

```k
// FIXME: Alignment is platform specific
// TODO: Extend #alignOf to be total by handling aggregate layouts (structs, arrays, unions).
syntax Int ::= #alignOf( TypeInfo ) [function]
rule #alignOf( typeInfoPrimitiveType(primTypeBool) )        => 1
rule #alignOf( typeInfoPrimitiveType(primTypeChar) )        => 4
rule #alignOf( typeInfoPrimitiveType(primTypeInt(intTyIsize)) )  => 8 // FIXME: Hard coded since usize not implemented
rule #alignOf( typeInfoPrimitiveType(primTypeInt(intTyI8)) )     => 1
rule #alignOf( typeInfoPrimitiveType(primTypeInt(intTyI16)) )    => 2
rule #alignOf( typeInfoPrimitiveType(primTypeInt(intTyI32)) )    => 4
rule #alignOf( typeInfoPrimitiveType(primTypeInt(intTyI64)) )    => 8
rule #alignOf( typeInfoPrimitiveType(primTypeInt(intTyI128)) )   => 16
rule #alignOf( typeInfoPrimitiveType(primTypeUint(uintTyUsize)) ) => 8 // FIXME: Hard coded since usize not implemented
rule #alignOf( typeInfoPrimitiveType(primTypeUint(uintTyU8)) )    => 1
rule #alignOf( typeInfoPrimitiveType(primTypeUint(uintTyU16)) )   => 2
rule #alignOf( typeInfoPrimitiveType(primTypeUint(uintTyU32)) )   => 4
rule #alignOf( typeInfoPrimitiveType(primTypeUint(uintTyU64)) )   => 8
rule #alignOf( typeInfoPrimitiveType(primTypeUint(uintTyU128)) )  => 16
rule #alignOf( typeInfoPrimitiveType(primTypeFloat(floatTyF16)) )  => 2
rule #alignOf( typeInfoPrimitiveType(primTypeFloat(floatTyF32)) )  => 4
rule #alignOf( typeInfoPrimitiveType(primTypeFloat(floatTyF64)) )  => 8
rule #alignOf( typeInfoPrimitiveType(primTypeFloat(floatTyF128)) ) => 16
rule #alignOf( typeInfoStructType(_,_,_,someLayoutShape(layoutShape(_, _, _, align(ALIGN), _)))) => ALIGN
```

```k
endmodule
```
