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

  syntax NumTy ::= #numTypeOf( RigidTy ) [function]
  // ----------------------------------------------
  rule #numTypeOf(rigidTyInt(INTTY)) => INTTY
  rule #numTypeOf(rigidTyUint(UINTTY)) => UINTTY
  rule #numTypeOf(rigidTyFloat(FLOATTY)) => FLOATTY

  syntax InTy ::= #intTypeOf( RigidTy ) [function]
  // ----------------------------------------------
  rule #intTypeOf(rigidTyInt(INTTY)) => INTTY
  rule #intTypeOf(rigidTyUint(UINTTY)) => UINTTY

  syntax Bool ::= #isIntType ( RigidTy ) [function, total]
  // -----------------------------------------------------
  rule #isIntType(rigidTyInt(_))  => true
  rule #isIntType(rigidTyUint(_)) => true
  rule #isIntType(_)              => false [owise]
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

  syntax Int ::= #maxIntValue( InTy ) [macro]
               | #minIntValue( InTy ) [macro]
  // ---------------------------------------------------
  rule #maxIntValue( INT:IntTy  ) => (1 <<Int (#bitWidth( INT) -Int 1)) -Int 1 [preserves-definedness]
  rule #maxIntValue(UINT:UintTy ) => (1 <<Int  #bitWidth(UINT)        ) -Int 1 [preserves-definedness]

  rule #minIntValue(INT:IntTy ) => 0 -Int (1 <<Int (#bitWidth(INT) -Int 1)) [preserves-definedness]
  rule #minIntValue(  _:UintTy) => 0


// use macros for bitWidth, max/min values, bit masking, and range
```

This truncation function is instrumental in the implementation of Integer arithmetic and overflow checking.

```k
  // helper function to truncate int values
  syntax Int ::= truncate(Int, Int, Signedness) [function, total]
  // -------------------------------------------------------------
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

## Type Casts Between Different Integer Types

```k
// all castIntToInt rules, maybe under its own rewrite symbol
```

```k
endmodule
```