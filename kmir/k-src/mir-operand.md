```k
require "mir-types.md"
require "mir-place.md"
```
[`Operand`](https://github.com/rust-lang/rust/blob/e3590fccfbdb6284bded9b70eca2e72b0c57e070/compiler/rustc_middle/src/mir/mod.rs#L1889)

Operands are leafs, i.e. the "basic components" of rvalues: either a loading of a place, or a constant.

```k
module MIR-OPERAND-SYNTAX
  imports MIR-PLACE
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

### [`Constant`](https://github.com/rust-lang/rust/blob/e3590fccfbdb6284bded9b70eca2e72b0c57e070/compiler/rustc_middle/src/mir/mod.rs#L2219)
There are three types of constants- 
- constant value from the type system
- constant that are unevaluated, thus not part of the type system
- constant that doesnot go back to type system like pointers.

Literals and const generic parameters are eagerly converted to a constant, everything else becomes `Unevaluated`.

```k
  syntax Constant ::= "const " ConstantValue   //ConstantKind::Ty(ty::Const<'tcx>)
                    | "const " "_"             //ConstantKind::Unevaluated(UnevaluatedConst<'tcx>, Ty<'tcx>)
                    |                  //ConstantKind::Val(interpret::ConstValue<'tcx>, Ty<'tcx>)
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