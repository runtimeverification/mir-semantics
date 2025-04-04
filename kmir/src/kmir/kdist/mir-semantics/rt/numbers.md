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
  rule #numTypeOf(typeInfoBasetype(baseTypeInt(INTTY))) => INTTY
  rule #numTypeOf(typeInfoBasetype(baseTypeUint(UINTTY))) => UINTTY
  rule #numTypeOf(typeInfoBasetype(baseTypeFloat(FLOATTY))) => FLOATTY

  syntax InTy ::= #intTypeOf( TypeInfo ) [function]
  // ----------------------------------------------
  rule #intTypeOf(typeInfoBasetype(baseTypeInt(INTTY))) => INTTY
  rule #intTypeOf(typeInfoBasetype(baseTypeUint(UINTTY))) => UINTTY

  syntax Bool ::= #isIntType ( TypeInfo ) [function, total]
  // -----------------------------------------------------
  rule #isIntType(typeInfoBasetype(baseTypeInt(_)))  => true
  rule #isIntType(typeInfoBasetype(baseTypeUint(_))) => true
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
  syntax Int ::= truncate(Int, Int, Signedness) [function, total]
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
  rule truncate(VAL, WIDTH, Unsigned)
      => VAL // shortcut when there is nothing to do
    requires 0 <Int WIDTH andBool VAL <Int 1 <<Int WIDTH
    [simplification, preserves-definedness]

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
    [preserves-definedness] // positive shift, divisor non-zero

  // widening: nothing to do: VAL does not change (enough bits to represent, no sign change possible)
  rule #intAsType(VAL, WIDTH, INTTYPE:IntTy)
      =>
        Integer(VAL, #bitWidth(INTTYPE), true)
    requires WIDTH <Int #bitWidth(INTTYPE)

  // converting to unsigned int types
  // truncate (if necessary), then add bias to make non-negative, then truncate again
  rule #intAsType(VAL, _, UINTTYPE:UintTy)
      =>
        Integer(
          (VAL %Int (1 <<Int #bitWidth(UINTTYPE) )
            +Int (1 <<Int #bitWidth(UINTTYPE)))
          %Int (1 <<Int #bitWidth(UINTTYPE) )
          ,
          #bitWidth(UINTTYPE),
          false
        )
    [preserves-definedness] // positive shift, divisor non-zero
```

```k
endmodule
```