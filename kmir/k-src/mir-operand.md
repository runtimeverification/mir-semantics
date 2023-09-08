```k
require "mir-place.md"
```

### [`Operand`](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/enum.Operand.html)

Operands are leafs, i.e. the "basic components" of rvalues: either a loading of a place, or a constant.

```k
module MIR-OPERAND-SYNTAX
  imports MIR-PLACE-SYNTAX
  imports MIR-CONSTANT-SYNTAX
  syntax Operand ::= Place
                   | "move" Place
                   | Constant

endmodule
```

```k
module MIR-CONSTANT-SYNTAX
  imports MIR-TYPE-SYNTAX
```

### [`Constant`](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/struct.Constant.html)

TODO: these sorts may need refactoring to closer match the `rustc` implementation.

```k
  syntax Constant ::= "const" ConstantValue
  syntax ConstantValue  ::= UnsignedLiteral
                          | SignedLiteral
                          | FloatLiteral
                          | CharLiteral
                          | StringLiteral
                          | ByteLiteral
                          | ByteStringLiteral
                          | Bool
                          | ConstEnumConstructor
                          | TupleConstant
                          | AdtConstant
                          | AllocConstant
                          | TransmuteConstant
                          | LiteralAsConstant
  syntax ConstantValueList ::= List{ConstantValue, ","}

  syntax ConstEnumConstructor ::= Identifier
                                | Identifier "(" ConstantValueList ")"
                                | PathExpression "::" Identifier
                                | PathExpression "::" Identifier "(" ConstantValueList ")"

  syntax AllocConstant ::= "{" Identifier ":" Type "}"
  syntax TransmuteConstant ::= "{" "transmute" "(" HexLiteral ")" ":" Type "}"

  syntax TupleConstant  ::= "(" ")"
                          | "(" ConstantValue "," ConstantValueList ")"

  syntax AdtConstant ::= Type "{" "{" AdtFieldConstantList "}" "}"
                       | Type "{" AdtFieldConstantList "}"
  syntax AdtFieldConstant ::= AdtFieldName ":" ConstantValue
  syntax AdtFieldConstantList ::= List{AdtFieldConstant, ","}

  syntax LiteralAsConstant ::= "{" Literal "as" Type "}"
endmodule
```
