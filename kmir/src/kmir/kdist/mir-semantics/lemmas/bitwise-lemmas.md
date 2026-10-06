# Bitwise lemmas for MIR symbolic execution

This file contains lemmas that rewrite bitwise operations on integers into arithmetic, and that bound the results of
bitwise operations. They are imported into the `KMIR` module alongside the lemmas in `kmir-lemmas.md`.

```k
module KMIR-BITWISE-LEMMAS
  imports INT
  imports INT-SYMBOLIC
  imports BOOL
```

The SMT solver treats `&Int`, `|Int`, `>>Int` and `<<Int` as uninterpreted functions, but `modInt` and `divInt` map to
SMT `mod` and `div` (Euclidean division), and `/Int` to truncating division. For a positive power-of-two divisor,
Euclidean division computes exactly what shifts and low masks do, so the following simplifications rewrite bitwise
operations by a constant into arithmetic the solver can reason about. All of them hold for every integer, as K
integers are two's complement of infinite width.

The rules only apply to a concrete mask or shift amount, so that a shift by a symbolic amount does not turn into
nonlinear arithmetic. They have a lower priority than the default, so that the more specific simplifications in
`kmir-lemmas.md` (e.g. for round trips through bytes) apply first to a term that both match.

A low mask `2^k - 1` keeps the low `k` bits, i.e. the remainder modulo `2^k` (also for negative `X`).
`M &Int (M +Int 1) ==Int 0` holds iff `M + 1` is a power of two.

```k
  rule [bitwise-low-mask]:
    X &Int M => X modInt (M +Int 1)
    requires 0 <=Int M andBool M &Int (M +Int 1) ==Int 0
    [simplification(60), preserves-definedness, concrete(M)]

  rule [bitwise-low-mask-comm]:
    M &Int X => X modInt (M +Int 1)
    requires 0 <=Int M andBool M &Int (M +Int 1) ==Int 0
    [simplification(60), preserves-definedness, concrete(M)]
```

An arithmetic right shift is floor division by `2^N`, which for `X >= 0` is truncating division (`/Int`). For negative
`X` it equals Euclidean division (`divInt`) instead, but the rule is restricted to nonnegative values for simplicity.

```k
  rule [bitwise-shr]:
    X >>Int N => X /Int (2 ^Int N)
    requires 0 <=Int N andBool 0 <=Int X
    [simplification(60), preserves-definedness, concrete(N)]
```

Repeated shifts give nested divisions, each of which the solver sees as a nested if-then-else; they are collapsed into
one. Truncating division by a positive `A`, then by a positive `B`, equals truncating division by `A * B`, for either
sign of `X`.

```k
  rule [bitwise-div-div]:
    (X /Int A) /Int B => X /Int (A *Int B)
    requires 0 <Int A andBool 0 <Int B andBool 0 <=Int X
    [simplification, preserves-definedness, concrete(A, B)]
```

A left shift is a multiplication by `2^N`. The rule is restricted to nonnegative values for simplicity, but would also
hold for negative ones.

```k
  rule [bitwise-shl]:
    X <<Int N => X *Int (2 ^Int N)
    requires 0 <=Int N andBool 0 <=Int X
    [simplification(60), preserves-definedness, concrete(N)]
```

With the rules above, the bytes of a nonnegative number `X` become `(X /Int 256^k) modInt 256` instead of
`(X >>Int 8 ... >>Int 8) &Int 255`, so the round-trip simplifications in `kmir-lemmas.md` no longer apply when the bytes are
put back together. The following simplifications put them back together instead, from the most significant byte.
Note that the second rule follows directly from the definition of integer division, and is equivalent to the first rule with
`A ==Int 1`.

```k
  rule [bitwise-digits]:
    (X /Int A) modInt N +Int N *Int (X /Int B) => X /Int A
    requires 0 <=Int X andBool 0 <Int A andBool 0 <Int N andBool B ==Int A *Int N
    [simplification, preserves-definedness, concrete(A, B, N)]

  rule [bitwise-digits-low]:
    X modInt N +Int N *Int (X /Int N) => X
    requires 0 <=Int X andBool 0 <Int N
    [simplification, preserves-definedness, concrete(N)]
```

For any other constant mask `0 < C < 2^k`, `X &Int C` only has bits of `C`, so it equals `(X &Int C) modInt 2^k`, and
the solver knows that the remainder modulo `2^k` lies in `[0, 2^k)`. This bounds masks like `0xAAAAAAAA` below `2^32`.
The rewrite puts the constant on the left, where this rule (with the constant on the right) does not match again.

```k
  rule [bitwise-mask-bound]:
    X &Int C => (C &Int X) modInt (2 ^Int (log2Int(C) +Int 1))
    requires 0 <Int C andBool C &Int (C +Int 1) =/=Int 0
    [simplification(60), preserves-definedness, concrete(C), symbolic(X)]
```

Finally, comparisons that bound bitwise operations on nonnegative values. The bitwise and with a nonnegative value lies
between zero and that value. The bitwise or of two values below `2^k` is below `2^k`, which bounds it by any constant
`C` from the largest power of two not above `C` (or `C + 1` for `<=Int`).
These only simplify comparisons of the given forms, for instance in the side conditions of the simplifications of
masks and truncation in `kmir-lemmas.md`.

```k
  rule [bitwise-and-lower]:
    0 <=Int X &Int _Y => true
    requires 0 <=Int X
    [simplification]

  rule [bitwise-and-lower-ge]:
    X &Int _Y >=Int 0 => true
    requires 0 <=Int X
    [simplification]

  rule [bitwise-and-upper]:
    X &Int _Y <=Int X => true
    requires 0 <=Int X
    [simplification]

  rule [bitwise-and-upper-ge]:
    X >=Int X &Int _Y => true
    requires 0 <=Int X
    [simplification]

  rule [bitwise-or-lower]:
    0 <=Int X |Int Y => true
    requires 0 <=Int X andBool 0 <=Int Y
    [simplification]

  rule [bitwise-or-upper]:
    X |Int Y <Int C => true
    requires 0 <Int C
     andBool 0 <=Int X andBool X <Int 2 ^Int log2Int(C)
     andBool 0 <=Int Y andBool Y <Int 2 ^Int log2Int(C)
    [simplification, concrete(C)]

  rule [bitwise-or-upper-le]:
    X |Int Y <=Int C => true
    requires 0 <=Int C
     andBool 0 <=Int X andBool X <Int 2 ^Int log2Int(C +Int 1)
     andBool 0 <=Int Y andBool Y <Int 2 ^Int log2Int(C +Int 1)
    [simplification, concrete(C)]
```

```k
endmodule
```
