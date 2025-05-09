# Lemmas for MIR symbolic execution

This file contains basic lemmas required for symbolic execution of MIR programs using `kmir`.

Lemmas are simpliciations of symbolic function application that aims to confirm conditions for rewrite rules to avoid spurious branching on symbolic program parts.

Some of the lemmas relate to the control flow implementation in `kmir.md` and will be needed in various proofs (for instance the simplification of list size for partially-symbolic lists of locals or stack frames).  
Others are related to helper functions used for integer arithmetic.

```k
requires "../rt/data.md"
requires "../kmir.md"

module KMIR-LEMMAS
  imports LIST
  imports INT-SYMBOLIC
  imports BOOL

  imports RT-DATA
```
## Simplifications for lists to avoid spurious branching on error cases in control flow

Rewrite rules that look up locals or stack frames require that an index into the respective `List`s in the configuration be within the bounds of the locals list/stack. Therefore, the `size` function on lists needs to be computed. The following simplifications allow for locals and stacks to have concrete values in the beginning but a symbolic rest (of unknown size).  
The lists used in the semantics are cons-lists, so only rules with a head element match are required.

```k
  rule N <Int size(_LIST:List) => true
    requires N <Int 0
    [simplification, symbolic(_LIST)]

  rule N <Int size(ListItem(_) REST:List) => N -Int 1 <Int size(REST)
    requires 0 <Int N
    [simplification, symbolic(REST)]
```

## Simplifications related to the `truncate` function

The `truncate` function is used in various overflow checks in integer arithmetic.
Therefore, its value range should be simplified for symbolic input asserted to be in range.

```k
  rule truncate(VAL, WIDTH, Unsigned) => VAL
    requires VAL <Int (1 <<Int WIDTH)
     andBool 0 <=Int VAL
     [simplification]

  rule truncate(VAL, WIDTH, Signed) => VAL
    requires VAL <Int (1 <<Int (WIDTH -Int 1))
     andBool 0 -Int (1 <<Int (WIDTH -Int 1)) <=Int VAL
     [simplification]
```

However, `truncate` gets evaluated and is therefore not present any more for this simplification.
The following simplification rules operate on the expression created by evaluating `truncate` when
`WIDTH` is 8, 16, 32, 64, or 128 and the mode is `Unsigned`. The simplification would hold for any
power of two but the semantics will always operate with these particular ones.

```k
  rule VAL &Int MASK => VAL 
    requires 0   <=Int VAL 
     andBool VAL <=Int MASK
     andBool ( MASK ==Int bitmask8
        orBool MASK ==Int bitmask16
        orBool MASK ==Int bitmask32
        orBool MASK ==Int bitmask64
        orBool MASK ==Int bitmask128
     )
    [simplification, preserves-definedness]

  syntax Int ::= "bitmask8"    [macro]
               | "bitmask16"   [macro]
               | "bitmask32"   [macro]
               | "bitmask64"   [macro]
               | "bitmask128"  [macro]

  rule bitmask8   => ( 1 <<Int 8  ) -Int 1
  rule bitmask16  => ( 1 <<Int 16 ) -Int 1
  rule bitmask32  => ( 1 <<Int 32 ) -Int 1
  rule bitmask64  => ( 1 <<Int 64 ) -Int 1
  rule bitmask128 => ( 1 <<Int 128) -Int 1

```


```k
endmodule
```