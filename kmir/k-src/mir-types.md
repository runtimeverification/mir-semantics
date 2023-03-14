```k
require "mir-syntax.k"
```

```k
module MIR-TYPES
  imports MIR-HOOKS
  imports MIR-RVALUE
endmodule
```

Runtime `RValue` types
-------------------

```k
module MIR-RVALUE
  imports INT
  imports STRING
  imports BYTES

  syntax KItem ::= RValueResult
```

Result of interpretation (inspired by [InterpResult](https://github.com/rust-lang/rust/blob/bd43458d4c2a01af55f7032f7c47d7c8fecfe560/compiler/rustc_middle/src/mir/interpret/error.rs#L496), either a `RValueResult` or an `InterpError`:

```k
  syntax InterpResult ::= RValueResult
                        | InterpError
```

The values of `RValueResult` sort represent the evaluation result of the syntactic `RValue`:
TODO: add more domain sorts

```k
  syntax RValueResult ::= Int
                        | String
```

The `InteprError` sort represent the errors that may occur while interpreting an `RValue` into `RValueResult` (inspired by [InterpError](https://github.com/rust-lang/rust/blob/bd43458d4c2a01af55f7032f7c47d7c8fecfe560/compiler/rustc_middle/src/mir/interpret/error.rs#L480)):

```k
  syntax InterpError ::= Unsupported(KItem)
```


```k
endmodule
```

Hooked functions
----------------

```k
module MIR-HOOKS
  imports STRING
  imports MIR-SYNTAX
```

We use several hooks which convert between token and string representations:

```k
  syntax String ::= StringLiteral2Sring(StringLiteral) [function, total, hook(STRING.token2string)]
  syntax StringLiteral ::= String2SringLiteral(String) [function, total, hook(STRING.string2token)]

  syntax String ::= LocalToken2String(LocalToken) [function, total, hook(STRING.token2string)]
  syntax LocalToken ::= String2LocalToken(String) [function, total, hook(STRING.string2token)]

  syntax String ::= BBToken2String(BBToken) [function, total, hook(STRING.token2string)]

  syntax IdentifierToken ::= String2IdentifierToken(String) [function, total, hook(STRING.string2token)]

  syntax String ::= SignedLitertal2String(SignedLiteral) [function, total, hook(STRING.token2string)]
  syntax String ::= UnsignedLitertal2String(UnsignedLiteral) [function, total, hook(STRING.token2string)]
  syntax String ::= StringLitertal2String(StringLiteral) [function, total, hook(STRING.token2string)]
```

Additionally, we need functions that convert between syntactic and semantics representations of several types:

### Locals

```k
  syntax Int ::= Local2Int(Local) [function, total]
  //-----------------------------------------------
  rule Local2Int(LOCAL) => #let STR = LocalToken2String({LOCAL}:>LocalToken) #in String2Int(substrString(STR, 1, lengthString(STR)))

  syntax Int ::= BBName2Int(BBName) [function, total]
  //-------------------------------------------------
  rule BBName2Int(NAME) => #let STR = BBToken2String(NAME) #in String2Int(substrString(STR, 2, lengthString(STR)))
```

### Literals

* Unsigned integer literals

```k
  syntax Int ::= UnsignedLiteral2Int(UnsignedLiteral) [function]
  //------------------------------------------------------------
  rule UnsignedLiteral2Int(LITERAL) =>
    #let     STR = UnsignedLitertal2String(LITERAL)
    #in #let UNDERSCORE_POSITION = findChar(STR, "_", 0)
    #in String2Int(substrString(STR, 0, UNDERSCORE_POSITION))
```

* Signed integer literals

```k
  syntax Int ::= SignedLiteral2Int(SignedLiteral) [function]
  //--------------------------------------------------------
  rule SignedLiteral2Int(LITERAL) =>
    #let     STR = SignedLitertal2String(LITERAL)
    #in #let UNDERSCORE_POSITION = findChar(STR, "_", 0)
    #in String2Int(substrString(STR, 0, UNDERSCORE_POSITION))
```

```k
endmodule
```
