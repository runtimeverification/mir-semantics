```k
module MIR-IDENTIFIERS
```

This module defined the necessary `token` productions.

```k
  syntax Identifier ::= r"[_a-zA-Z][_a-zA-Z0-9]*" [token]

  syntax LocalToken ::= "_" Int  [token] //replace regular expression with UnsignedInt
  syntax Local ::= LocalToken
    
  syntax BBId       ::= "bb" Int [token] //It is the BasicBlock type in rustc
  syntax UserVar    ::= Identifier
  syntax AdtFieldName ::= Identifier //TODO: figure out the exact definition

  // syntax String ::= IdentifierToken2String(IdentifierToken) [function, hook(STRING.token2string)]
  // syntax IdentifierToken ::= StringIdentifierToken(String) [function, hook(STRING.string2token)]

  syntax DefId ::= Int
  syntax Symbol ::= Int  
```

Primitive types (in literal format) used in MIR. 

```k
//TODO： locate the code defines the primitive types in MIR.
//Do we need to redefine regular expression? Maybe move to Type File
  //syntax UnsignedLiteral    ::= r"[0-9]+_(usize|u8|u16|u32|u64|u128)" [token]
  //syntax SignedLiteral      ::= r"[-]?[0-9]+_(isize|i8|i16|i32|i64|i128)" [token]
  //syntax FloatLiteral       ::= r"-?[0-9]+(.[0-9]+)?((E|e)(\\+|-)?[0-9]+)?(f32|f64)" [token]
  syntax HexLiteral         ::= r"0x[0-9a-fA-F]+"  [token]
  syntax StringLiteral      ::= r"[\\\"]([^\\\"\\\\\\n]|\\\\[\\\"'nrt0\\\\]|\\\\x[0-7][0-9a-fA-F]|\\\\u\\{[0-9a-fA-F]+\\}|\\\\u[0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F][0-9a-fA-F]?)?)?)?)?|\\\\\\n)*[\\\"]"  [token]
  syntax CharLiteral        ::= r"[']([^\\\"\\\\\\n\\r\\t]|\\\\[\\\"'nrt0\\\\]|\\\\x[0-7][0-9a-fA-F]|\\\\u\\{[0-9a-fA-F]+\\}|\\\\u[0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F][0-9a-fA-F]?)?)?)?)?|\\\\\\n)[']"  [token]
  // TODO: Unicode escapes should probably not be a part of ByteLiteral.
  syntax ByteLiteral        ::= r"b[']([^\\\"\\\\\\n\\r\\t]|\\\\[\\\"'nrt0\\\\]|\\\\x[0-7][0-9a-fA-F]|\\\\u[0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F][0-9a-fA-F]?)?)?)?)?|\\\\\\n)[']"  [token]
  syntax ByteStringLiteral  ::= r"b[\\\"]([^\\\"\\\\\\n\\r\\t]|\\\\[\\\"'nrt0\\\\]|\\\\x[0-9a-fA-F][0-9a-fA-F]|\\\\\\n)*[\\\"]"  [token]
```

## Variances

Types such as structs, tuples and unions, which has fields (indexed by `VariantIdx`).

- [`VariantIdx`](https://github.com/rust-lang/rust/blob/ffaa32b7b646c208f20c827655bb98ff9868852e/compiler/rustc_abi/src/lib.rs#L1493) used in abi is an index of type u32, so the index must not exceed u32::MAX. You can also customize things like the Debug impl, what traits are derived, and so forth via the macro.
- [`FieldIdx`](https://github.com/rust-lang/rust/blob/d7e751006cb3691d1384b74196a9cb45447acfa8/compiler/rustc_abi/src/lib.rs#L1119) is the index of a field in a Variant
```k

  syntax VariantIdx ::= Int //u32
  syntax FieldIdx ::= Int   //u32
```

```k
  syntax FilePosition ::= FileName ":" CodePosition ":" CodePosition //Format FileName:StartLine:StartColumn:EndLine:EndColumn. similar as code region in Coverage. Considered duplicate. 
  syntax FileName ::= r"[^@ ]+"
  syntax CodePosition ::= r"[0-9]+:[0-9]+:"  [token]
```

```k
  syntax AllocReferenceToken ::= r"#\\(-*alloc[0-9]+(?:\\+0x[0-9a-fA-F]+)?-*\\)#"  [token]
  syntax DoubleHexDigitNoIntLetter ::= r"[a-fA-F][0-9a-fA-F]" [token(2)]
  syntax DoubleHexDigitNoIntDigit ::= r"[0-9][a-fA-F]" [token]
```

```k
endmodule
```
