```k
require "mir-types.md"
```

```k
module MIR-PLACE-SYNTAX
  imports BOOL
  imports UNSIGNED-INT-SYNTAX
  imports MIR-TYPE-SYNTAX
```

### [Place](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/syntax/struct.Place.html)

A `Place` is either a `Local`, i.e. a "variable" or a non-terminal place, which represents a projection of some sort:

```k
  syntax Place  ::= Local
                  | NonTerminalPlace
```

```k
  syntax Local ::= LocalToken
```

```k
  syntax NonTerminalPlace ::= Deref
                            | Field
                            | Index
                            | ConstantIndex
                            | Subslice
                            | Downcast
                            | OpaqueCast

```

#### [ProjectionElem](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/syntax/enum.ProjectionElem.html)

The `NonTerminalPlace` represents `ProjectionElem`

```k
  syntax Deref ::= "(" "*" Place ")"
  syntax Field ::= "(" Place "." Int ":" Type ")"
  syntax Index ::= Place "[" Local "]"
  syntax ConstantIndex ::= Place "[" Int "of" Int "]"     // ConstantIndex { from_end: false }
                         | Place "[" "-" Int "of" Int "]" // ConstantIndex { from_end: true }
  syntax Subslice ::= Place "[" Int ":" "]"           // Subslice{to: 0, from_end: true}
                    | Place "[" ":" "-" Int "]"       // Subslice{from: 0, from_end: true}
                    | Place "[" Int ":" "-" Int "]"   // Subslice{from_end: true}
                    | Place "[" Int ".." Int "]"      // Subslice{from_end: false}
  syntax Downcast ::= "(" Place "as" Type ")"
                    | "(" Place "as" "variant" "#" Int ")"
  syntax OpaqueCast ::= "(" Place "as" Type ")"

```

```k
endmodule
```
