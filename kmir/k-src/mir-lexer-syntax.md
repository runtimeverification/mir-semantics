```k
module MIR-LEXER-SYNTAX
```

This module defined the necessary `token` productions.

```k
  syntax Identifier ::= IdentifierToken
                      | LocalToken
                      | BBToken
                      | DoubleHexDigitNoIntLetter
                      | OtherTokens
```

```k
  syntax IdentifierToken ::= r"[_a-zA-Z][_a-zA-Z0-9]*" [token]
  syntax LocalToken      ::= r"_[0-9]+"  [token(2)]
  syntax BBToken         ::= r"bb[0-9]+" [token(2)]
```

Simplified forms of the [Rust literals](https://doc.rust-lang.org/reference/tokens.html#literals), since MIR does not seem to use the full range:

```k
  syntax UnsignedLiteral ::= r"[0-9]+_(usize|u8|u16|u32|u64|u128)" [token]
  syntax SignedLiteral ::= r"[-]?[0-9]+_(isize|i8|i16|i32|i64|i128)" [token]
  syntax FloatLiteral ::= r"-?[0-9]+(.[0-9]+)?((E|e)(\\+|-)?[0-9]+)?(f32|f64)" [token]
  syntax HexLiteral ::= r"0x[0-9a-fA-F]+"  [token]
  syntax StringLiteral ::= r"[\\\"]([^\\\"\\\\\\n]|\\\\[\\\"'nrt0\\\\]|\\\\x[0-7][0-9a-fA-F]|\\\\u\\{[0-9a-fA-F]+\\}|\\\\u[0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F][0-9a-fA-F]?)?)?)?)?|\\\\\\n)*[\\\"]"  [token]
  syntax CharLiteral ::= r"[']([^\\\"\\\\\\n\\r\\t]|\\\\[\\\"'nrt0\\\\]|\\\\x[0-7][0-9a-fA-F]|\\\\u\\{[0-9a-fA-F]+\\}|\\\\u[0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F][0-9a-fA-F]?)?)?)?)?|\\\\\\n)[']"  [token]
  // TODO: Unicode escapes should probably not be a part of ByteLiteral.
  syntax ByteLiteral ::= r"b[']([^\\\"\\\\\\n\\r\\t]|\\\\[\\\"'nrt0\\\\]|\\\\x[0-7][0-9a-fA-F]|\\\\u[0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F][0-9a-fA-F]?)?)?)?)?|\\\\\\n)[']"  [token]
  syntax ByteStringLiteral ::= r"b[\\\"]([^\\\"\\\\\\n\\r\\t]|\\\\[\\\"'nrt0\\\\]|\\\\x[0-9a-fA-F][0-9a-fA-F]|\\\\\\n)*[\\\"]"  [token]
```

```k
  syntax FilePosition ::= FileLineColumnStartLiteral LineColumnEndLiteral
  syntax FileLineColumnStartLiteral ::= r"[^@ ]+:[0-9]+:[0-9]+:"  [token]
  syntax LineColumnEndLiteral ::= r"[0-9]+:[0-9]+"  [token]
```

```k
  syntax AllocReferenceToken ::= r"#\\(-*alloc[0-9]+(?:\\+0x[0-9a-fA-F]+)?-*\\)#"  [token]
  syntax DoubleHexDigitNoIntLetter ::= r"[a-fA-F][0-9a-fA-F]" [token(2)]
  syntax DoubleHexDigitNoIntDigit ::= r"[0-9][a-fA-F]" [token]
```

```k
  // TODO: Allow assert and assume as normal identifiers.
  syntax OtherTokens  ::= "align" | "assume"
                        | "body"
                        | "cleanup" | "closure" | "constant"
                        | "copy_nonoverlapping" | "count"
                        | "debug" | "deref_copy" | "discriminant" | "dst"
                        | "generator" | "goto"
                        | "opaque" | "otherwise"
                        | "promoted"
                        | "resume"
                        | "StorageLive" | "StorageDead"
                        | "scope" | "size" | "src" | "success"
                        | "unreachable" | "unwind"
                        | "transmute"
                        | "variant"
                        | "__"
                        // TODO: These tokens seem to be needed when running
                        // on github. I'm not sure why, looks like a K issue:
                        | "keys" | "values"
```

```k
endmodule
```
