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

```k
  rule (VAL +Int 256 *Int _) %Int 256 => VAL
  requires 0 <=Int VAL
    andBool VAL <=Int 255
  [simplification, preserves-definedness]

  rule (VAL +Int 256 *Int REST) /Int 256 => REST
  requires 0 <=Int VAL
    andBool VAL <=Int 255
    andBool 0 <=Int REST
  [simplification, preserves-definedness]
```


```k
endmodule
```