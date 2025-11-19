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

  rule 0 <=Int size(_LIST:List) => true [simplification]
```

The hooked `range` function selects a segment from a list, by removing elements from front and back.
If nothing is removed, the list remains the same. If all elements are removed, nothing remains.

```k
  rule range(L:List, 0, 0) => L [simplification]

  rule range(L:List, size(L), 0) => .List [simplification]

  rule range(L:List, 0, size(L)) => .List [simplification]

  rule size(range(L, A, B)) => size(L) -Int A -Int B
    requires A +Int B <=Int size(L) [simplification, preserves-definedness]

  rule #Ceil(range(L, A, B)) => #Ceil(L) #And #Ceil(A) #And #Ceil(B) #And {true #Equals A +Int B <=Int size(L)} [simplification]
```

The `#mapOffset` function maps `#adjustRef` over a lists of `Value`s, leaving the list length unchanged.
Definedness of the list and list elements is also guaranteed.

```k
  rule size(#mapOffset(L, _)) => size(L) [simplification, preserves-definedness]

  rule #Ceil(#mapOffset(L, _)[I]) => #Ceil(L) #And {true #Equals 0 <=Int I} #And {true #Equals I <Int size(L)} [simplification]

  rule #Ceil(#mapOffset(L, _)) => #Ceil(L) [simplification]

  rule #adjustRef(VAL:Value, 0) => VAL [simplification]

  rule #adjustRef(#adjustRef(VAL, OFFSET1), OFFSET2)
    => #adjustRef(VAL, OFFSET1 +Int OFFSET2)
    [simplification]

  rule #mapOffset(L, 0) => L [simplification]

  rule #mapOffset(#mapOffset(L, OFFSET1), OFFSET2)
    => #mapOffset(L, OFFSET1 +Int OFFSET2)
    [simplification]
```

## Simplifications for `enum` Discriminants and Variant Indexes

For symbolic enum values, the variant index remains unevaluated but the original (symbolic) discriminant can be restored:

```k
  rule #lookupDiscriminant(typeInfoEnumType(_, _, _, _, _), #findVariantIdxAux(DISCR, DISCRS, _IDX)) => DISCR
    requires isOneOf(DISCR, DISCRS)
    [simplification, preserves-definedness, symbolic(DISCR)]

  syntax Bool ::= isOneOf ( Int , Discriminants ) [function, total]
  // --------------------------------------------------------------
  rule isOneOf( _,                       .Discriminants                      ) => false
  rule isOneOf( I, discriminant(D)                     .Discriminants        ) => I ==Int D
  rule isOneOf( I, discriminant(mirInt(D))             .Discriminants        ) => I ==Int D
  rule isOneOf( I, discriminant(D)         ((discriminant(_) _MORE) #as REST)) => I ==Int D orBool isOneOf(I, REST)
  rule isOneOf( I, discriminant(mirInt(D)) ((discriminant(_) _MORE) #as REST)) => I ==Int D orBool isOneOf(I, REST)
```

## Simplifications for Int

These are trivial simplifications driven by syntactic equality, which should be present upstream.

```k
  rule A <=Int A => true [simplification]

  rule A ==Int A => true [simplification]

  rule A -Int A => 0 [simplification]
```

## Simplifications related to the `truncate` function

The `truncate` function is used in various overflow checks in integer arithmetic.
Therefore, its value range should be simplified for symbolic input asserted to be in range.

```k
  rule truncate(VAL, WIDTH, Unsigned) => VAL
    requires 0 <Int WIDTH
     andBool VAL <Int (1 <<Int WIDTH)
     andBool 0 <=Int VAL
     [simplification, preserves-definedness] // , smt-lemma], but `Unsigned` needs to be smtlib

  rule truncate(VAL, WIDTH, Signed) => VAL
    requires 0 <Int WIDTH
     andBool VAL <Int (1 <<Int (WIDTH -Int 1))
     andBool 0 -Int (1 <<Int (WIDTH -Int 1)) <=Int VAL
     [simplification, preserves-definedness] // , smt-lemma], but `Signed` needs to be smtlib
```

However, `truncate` gets evaluated and is therefore not present any more for this simplification.
The following simplification rules operate on the expression created by evaluating `truncate` when
`WIDTH` is 8, 16, 32, 64, or 128 and the mode is `Unsigned`. The simplification would hold for any
power of two but the semantics will always operate with these particular ones.

```k
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

  rule VAL &Int bitmask8   => VAL requires 0 <=Int VAL andBool VAL <=Int bitmask8   [simplification, preserves-definedness, smt-lemma]
  rule VAL &Int bitmask16  => VAL requires 0 <=Int VAL andBool VAL <=Int bitmask16  [simplification, preserves-definedness, smt-lemma]
  rule VAL &Int bitmask32  => VAL requires 0 <=Int VAL andBool VAL <=Int bitmask32  [simplification, preserves-definedness, smt-lemma]
  rule VAL &Int bitmask64  => VAL requires 0 <=Int VAL andBool VAL <=Int bitmask64  [simplification, preserves-definedness, smt-lemma]
  rule VAL &Int bitmask128 => VAL requires 0 <=Int VAL andBool VAL <=Int bitmask128 [simplification, preserves-definedness, smt-lemma]
```

Repeated bit-masking can be simplified in an even more general way:

```k
     rule (X &Int MASK1 &Int MASK2) => X &Int MASK2
       requires 0 <Int MASK1
        andBool 0 <Int MASK2
        andBool MASK2 <=Int MASK1
       [simplification, concrete(MASK1, MASK2), smt-lemma]
     rule (X &Int MASK2 &Int MASK1) => X &Int MASK2
       requires 0 <Int MASK1
        andBool 0 <Int MASK2
        andBool MASK2 <Int MASK1 // not <=Int; uses rule above when MASK1 == MASK2
       [simplification, concrete(MASK1, MASK2), smt-lemma]
```

Support for `transmute` between byte arrays and numbers (and vice-versa) uses computations involving bit masks with 255 and 8-bit shifts.
To support simplifying round-trip conversion, the following simplifications are essential.

```k
  rule (VAL +Int 256 *Int REST) &Int 255 => VAL
  requires 0 <=Int VAL
    andBool VAL <=Int 255
    andBool 0 <=Int REST
  [simplification, preserves-definedness]

  rule (VAL +Int 256 *Int REST) >>Int 8 => REST
  requires 0 <=Int VAL
    andBool VAL <=Int 255
    andBool 0 <=Int REST
  [simplification, preserves-definedness]

  rule (_ &Int 255) <=Int 255 => true
    [simplification, preserves-definedness]
  rule 0 <=Int (_ &Int 255) => true
    [simplification, preserves-definedness]

  rule [simplify-u64-bytes-u64]:
      (VAL                                                                         &Int 255) +Int (256 *Int (
        ((VAL >>Int 8)                                                             &Int 255) +Int (256 *Int (
          ((VAL >>Int 8 >>Int 8)                                                   &Int 255) +Int (256 *Int (
            ((VAL >>Int 8 >>Int 8 >>Int 8)                                         &Int 255) +Int (256 *Int (
              ((VAL >>Int 8 >>Int 8 >>Int 8 >>Int 8)                               &Int 255) +Int (256 *Int (
                ((VAL >>Int 8 >>Int 8 >>Int 8 >>Int 8 >>Int 8)                     &Int 255) +Int (256 *Int (
                  ((VAL >>Int 8 >>Int 8 >>Int 8 >>Int 8 >>Int 8 >>Int 8)           &Int 255) +Int (256 *Int (
                    ((VAL >>Int 8 >>Int 8 >>Int 8 >>Int 8 >>Int 8 >>Int 8 >>Int 8) &Int 255)))))))))))))))
      => VAL
    requires 0 <=Int VAL andBool VAL <=Int bitmask64
    [simplification, preserves-definedness, symbolic(VAL)]
```

More generally, a value which is composed of sliced bytes can generally be assumed to be in range of a suitable bitmask for the byte length.
This avoids building up large expressions related to overflow checks and vacuous branches leading to overflow errors.

```k
  rule ((( _X0 )                                                                     &Int 255) +Int 256 *Int (
         (( _X1 >>Int 8)                                                              &Int 255) +Int 256 *Int (
           (( _X2 >>Int 8 >>Int 8)                                                    &Int 255) +Int 256 *Int (
              (( _X3 >>Int 8 >>Int 8 >>Int 8)                                         &Int 255) +Int 256 *Int (
                (( _X4 >>Int 8 >>Int 8 >>Int 8 >>Int 8)                               &Int 255) +Int 256 *Int (
                  (( _X5 >>Int 8 >>Int 8 >>Int 8 >>Int 8 >>Int 8)                     &Int 255) +Int 256 *Int (
                    (( _X6 >>Int 8 >>Int 8 >>Int 8 >>Int 8 >>Int 8 >>Int 8)           &Int 255) +Int 256 *Int (
                      (( _X7 >>Int 8 >>Int 8 >>Int 8 >>Int 8 >>Int 8 >>Int 8 >>Int 8) &Int 255)))))))))
          <=Int bitmask64
        => true
    [simplification, preserves-definedness, symbolic]
```


For the case where the (symbolic) byte values are first converted to a number, the round-trip simplification requires different matching.
First, the bit-masking with `&Int 255` eliminates `Bytes2Int(Int2Bytes(1, ..) +Bytes ..)` enclosing a byte-valued variable:

```k
  rule Bytes2Int(Int2Bytes(1, X, LE) +Bytes _, LE, Unsigned) &Int 255 => X
    requires 0 <=Int X andBool X <=Int 255
    [simplification]
  rule Bytes2Int(Int2Bytes(1, X, LE), LE, Unsigned) &Int 255 => X
    requires 0 <=Int X andBool X <=Int 255
    [simplification]
```

Conversely, bit shifts by 8 interact with nests of `Bytes2Int(Int2Bytes(..) +Bytes Rest)` by eliminating the first byte:
```k
  rule Bytes2Int(Int2Bytes(1, _:Int, _) +Bytes REST, LE, SIGNEDNESS) >>Int 8 => Bytes2Int(REST, LE, SIGNEDNESS)
    [simplification, preserves-definedness] // bit-shift by positive number
```

Finally, the magnitude of a value converted from bytes is known to be within the limit for the byte count:
```k
  rule [u64-bytes-within-limit]:
    BYTE0 +Int (256 *Int (
      BYTE1 +Int (256 *Int (
        BYTE2 +Int (256 *Int (
          BYTE3 +Int (256 *Int (
            BYTE4 +Int (256 *Int (
              BYTE5 +Int (256 *Int (
                BYTE6 +Int (256 *Int (
                  BYTE7)))))))))))))) <=Int bitmask64 => true
    requires 0 <=Int BYTE0 andBool BYTE0 <=Int 255
     andBool 0 <=Int BYTE1 andBool BYTE1 <=Int 255
     andBool 0 <=Int BYTE2 andBool BYTE2 <=Int 255
     andBool 0 <=Int BYTE3 andBool BYTE3 <=Int 255
     andBool 0 <=Int BYTE4 andBool BYTE4 <=Int 255
     andBool 0 <=Int BYTE5 andBool BYTE5 <=Int 255
     andBool 0 <=Int BYTE6 andBool BYTE6 <=Int 255
     andBool 0 <=Int BYTE7 andBool BYTE7 <=Int 255
    [simplification]
```


```k
endmodule
```
