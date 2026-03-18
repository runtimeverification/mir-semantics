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
  imports FLOAT
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

  syntax Bool ::= #isFloatType ( TypeInfo ) [function, total]
  // --------------------------------------------------------
  rule #isFloatType(typeInfoPrimitiveType(primTypeFloat(_))) => true
  rule #isFloatType(_)                                       => false [owise]

  syntax FloatTy ::= #floatTypeOf ( TypeInfo ) [function]
  // ----------------------------------------------------
  rule #floatTypeOf(typeInfoPrimitiveType(primTypeFloat(FLOATTY))) => FLOATTY
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

## Helpers and Constants for Float Operations

Rust supports four fixed-width IEEE 754 float types: `f16`, `f32`, `f64`, and `f128`.
The helpers below extract format parameters for each type. First, an overview of the format.

### IEEE 754 Binary Format

An IEEE 754 binary floating-point word has three fields stored left-to-right:

```
  MSB                                             LSB
  +---------+----------------+----------------------+
  |  sign   |    exponent    |       fraction       |
  | (1 bit) |   (EB bits)    |   (SB - 1 bits)      |
  +---------+----------------+----------------------+
  total bits = 1 + EB + (SB - 1)
```

The **significand** (also called **precision**) is the total number of significant bits
in the represented value, including an implicit leading 1 that is not stored in the
fraction field. For a normal number, the mathematical value is:

    value  =  (-1)^sign  *  2^(exponent - bias)  *  1.fraction

The "1." prefix is the implicit bit, so the significand has `SB` bits of precision
even though only `SB - 1` fraction bits are stored. For example, f64 stores 52 fraction
bits but has 53 bits of significand precision.

K's built-in `FLOAT` module uses this convention: `Int2Float(x, precision, exponentBits)`
takes `precision = SB` (total significand bits including the implicit 1) and `exponentBits = EB`.
See [IEEE 754 on Wikipedia](https://en.wikipedia.org/wiki/IEEE_754) for full details.

The exponent is stored as an unsigned integer in
[excess-M encoding](https://en.wikipedia.org/wiki/Offset_binary) with `bias = 2^(EB-1) - 1`,
so that the actual exponent is `stored - bias`. For f64, bias = 1023: a stored value of 1023
means exponent 0, 1024 means +1, and 1 means -1022. Stored values 0 and `2^EB - 1` are
reserved for zero/subnormals and infinity/NaN respectively.

| Type | Total bits | Sign | Exponent (EB) | Fraction (SB-1) | Significand (SB) | Bias       |
|------|------------|------|---------------|-----------------|------------------|------------|
| f16  | 16         | 1    | 5             | 10              | 11               | 15         |
| f32  | 32         | 1    | 8             | 23              | 24               | 127        |
| f64  | 64         | 1    | 11            | 52              | 53               | 1023       |
| f128 | 128        | 1    | 15            | 112             | 113              | 16383      |

```k
  syntax Int ::= #significandBits ( FloatTy ) [function, total]
  // ----------------------------------------------------------
  rule #significandBits(floatTyF16)  => 11
  rule #significandBits(floatTyF32)  => 24
  rule #significandBits(floatTyF64)  => 53
  rule #significandBits(floatTyF128) => 113

  syntax Int ::= #exponentBits ( FloatTy ) [function, total]
  // -------------------------------------------------------
  rule #exponentBits(floatTyF16)  => 5
  rule #exponentBits(floatTyF32)  => 8
  rule #exponentBits(floatTyF64)  => 11
  rule #exponentBits(floatTyF128) => 15

  syntax Int ::= #bias ( FloatTy ) [function, total]
  // -----------------------------------------------
  rule #bias(FLOATTY) => (1 <<Int (#exponentBits(FLOATTY) -Int 1)) -Int 1
```

### IEEE 754 Special Values

When the exponent field is all 1s (`2^EB - 1`), the value is either infinity
(fraction = 0) or NaN (fraction != 0). K's `FLOAT-SYNTAX` module in
[domains.md](https://github.com/runtimeverification/k/blob/master/k-distribution/include/kframework/builtin/domains.md#ieee-754-floating-point-numbers)
defines float literals with a `p<SB>x<EB>` suffix to specify precision and exponent
bits. See IEEE 754 Binary Format above for values of SB and EB.

For example, `Infinityp53x11` is f64 positive infinity, `NaNp24x8` is f32 NaN.

```k
  syntax Float ::= #posInfFloat ( FloatTy ) [function, total]
  // --------------------------------------------------------
  rule #posInfFloat(floatTyF16)  => Infinityp11x5
  rule #posInfFloat(floatTyF32)  => Infinityp24x8
  rule #posInfFloat(floatTyF64)  => Infinityp53x11
  rule #posInfFloat(floatTyF128) => Infinityp113x15

  syntax Float ::= #nanFloat ( FloatTy ) [function, total]
  // -----------------------------------------------------
  rule #nanFloat(floatTyF16)  => NaNp11x5
  rule #nanFloat(floatTyF32)  => NaNp24x8
  rule #nanFloat(floatTyF64)  => NaNp53x11
  rule #nanFloat(floatTyF128) => NaNp113x15
```

## Decoding Float values from `Bytes` for `OperandConstant`

The `#decodeFloat` function reconstructs a `Float` value from its IEEE 754 byte representation.
The bytes are first converted to a raw integer, then the sign, biased exponent, and stored significand
are extracted. The value is reconstructed using K's `Int2Float` and float arithmetic, with a
high-precision intermediate to avoid overflow when reconstructing subnormals and small normal values.

```k
  syntax Value ::= #decodeFloat ( Bytes, FloatTy ) [function]
  // --------------------------------------------------------
  rule #decodeFloat(BYTES, FLOATTY) => #decodeFloatRaw(Bytes2Int(BYTES, LE, Unsigned), FLOATTY)
    requires lengthBytes(BYTES) ==Int #bitWidth(FLOATTY) /Int 8
    [preserves-definedness]

  syntax Value ::= #decodeFloatRaw ( Int, FloatTy ) [function, total]
  // ----------------------------------------------------------------
  rule #decodeFloatRaw(RAW, FLOATTY)
    => #decodeFloatParts(
         RAW >>Int (#significandBits(FLOATTY) +Int #exponentBits(FLOATTY) -Int 1),
         (RAW >>Int (#significandBits(FLOATTY) -Int 1)) &Int ((1 <<Int #exponentBits(FLOATTY)) -Int 1),
         RAW &Int ((1 <<Int (#significandBits(FLOATTY) -Int 1)) -Int 1),
         FLOATTY
       )

  syntax Value ::= #decodeFloatParts ( sign: Int, biasedExp: Int, storedSig: Int, FloatTy ) [function]
  // -------------------------------------------------------------------------------------------------

  // Zero (positive or negative)
  rule #decodeFloatParts(SIGN, 0, 0, FLOATTY)
    => Float(#applyFloatSign(Int2Float(0, #significandBits(FLOATTY), #exponentBits(FLOATTY)), SIGN), #bitWidth(FLOATTY))
    [preserves-definedness]

  // Subnormal: no implicit leading 1, exponent is 1 - bias
  rule #decodeFloatParts(SIGN, 0, SIG, FLOATTY)
    => Float(
         #applyFloatSign(
           #reconstructFloat(SIG, 2 -Int #bias(FLOATTY) -Int #significandBits(FLOATTY), FLOATTY),
           SIGN
         ),
         #bitWidth(FLOATTY)
       )
    requires SIG =/=Int 0
    [preserves-definedness]

  // Normal: implicit leading 1 in significand
  rule #decodeFloatParts(SIGN, EXP, SIG, FLOATTY)
    => Float(
         #applyFloatSign(
           #reconstructFloat(
             SIG |Int (1 <<Int (#significandBits(FLOATTY) -Int 1)),
             EXP -Int #bias(FLOATTY) -Int #significandBits(FLOATTY) +Int 1,
             FLOATTY
           ),
           SIGN
         ),
         #bitWidth(FLOATTY)
       )
    requires EXP >Int 0 andBool EXP <Int ((1 <<Int #exponentBits(FLOATTY)) -Int 1)
    [preserves-definedness]

  // Infinity
  rule #decodeFloatParts(SIGN, EXP, 0, FLOATTY)
    => Float(#applyFloatSign(#posInfFloat(FLOATTY), SIGN), #bitWidth(FLOATTY))
    requires EXP ==Int ((1 <<Int #exponentBits(FLOATTY)) -Int 1)
    [preserves-definedness]

  // NaN
  rule #decodeFloatParts(_SIGN, EXP, SIG, FLOATTY)
    => Float(#nanFloat(FLOATTY), #bitWidth(FLOATTY))
    requires EXP ==Int ((1 <<Int #exponentBits(FLOATTY)) -Int 1) andBool SIG =/=Int 0
    [preserves-definedness]
```

Reconstruct a float from its integer significand and adjusted exponent.
For positive exponents, shift the significand left and convert.
For negative exponents, use a high-precision intermediate (256-bit significand, 64-bit exponent)
to avoid overflow, then round down to the target precision.

```k
  syntax Float ::= #reconstructFloat ( sig: Int, adjExp: Int, FloatTy ) [function]
  // -------------------------------------------------------------------------------
  rule #reconstructFloat(SIG, AEXP, FLOATTY)
    => Int2Float(SIG <<Int AEXP, #significandBits(FLOATTY), #exponentBits(FLOATTY))
    requires AEXP >=Int 0
    [preserves-definedness]

  rule #reconstructFloat(SIG, AEXP, FLOATTY)
    => roundFloat(
         Int2Float(SIG, 256, 64) /Float Int2Float(1 <<Int (0 -Int AEXP), 256, 64),
         #significandBits(FLOATTY),
         #exponentBits(FLOATTY)
       )
    requires AEXP <Int 0
    [preserves-definedness]

  // Apply the sign bit to a float value
  syntax Float ::= #applyFloatSign ( Float, Int ) [function, total]
  // ---------------------------------------------------------------
  rule #applyFloatSign(F, 0) => F
  rule #applyFloatSign(F, 1) => --Float F
  rule #applyFloatSign(F, _) => F [owise]
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
    [preserves-definedness]

  // widening: nothing to do: VAL does not change (enough bits to represent, no sign change possible)
  rule #intAsType(VAL, WIDTH, INTTYPE:IntTy)
      =>
        Integer(VAL, #bitWidth(INTTYPE), true)
    requires WIDTH <Int #bitWidth(INTTYPE)
    [preserves-definedness]

  // converting to unsigned int types (simple bitmask)
  rule #intAsType(VAL, _, UINTTYPE:UintTy)
      =>
        Integer(
          truncate(VAL, #bitWidth(UINTTYPE), Unsigned),
          #bitWidth(UINTTYPE),
          false
        )
    [preserves-definedness]
```

```k
endmodule
```
