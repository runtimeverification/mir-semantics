# Integer Implementation

The code in this file implements functionality for `Integer` values in `mir-semantics`.

```k
requires "./value.md"

module RT-INTEGER
  imports RT-VALUE-SYNTAX // syntax only
```

## Helpers and Constants for Integer Operations

```k
// use macros for bitWidth, max/min values, bit masking, and range
```

## Decoding Integer values from `Bytes` for `OperandConstant`

```k
// decode rules for int, as its own function
// what about errors? Can there be any?
```

## Type Casts Between Different Integer Types

```k
// all castIntToInt rules, maybe under its own rewrite symbol
```

```k
endmodule
```