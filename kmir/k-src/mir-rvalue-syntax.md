```k
requires "mir-type-syntax.md"
requires "mir-place-syntax.md"
```

```k
module MIR-RVALUE-SYNTAX
  imports BOOL
  imports UNSIGNED-INT-SYNTAX
  imports MIR-TYPE-SYNTAX
  imports MIR-PLACE-SYNTAX
  imports MIR-CONSTANT-SYNTAX
```

```k
  syntax Operand ::= Place
                   | "move" Place
                   | Constant

  syntax RValue ::= Use
                  | Repeat
                  | Ref
//                  | ThreadLocalRef
                  | AddressOf
                  | Len
                  | Cast
                  | NullaryOp
                  | UnaryOp
                  | BinaryOp
                  | Discriminant
                  | Aggregate
                  | ShallowInitBox
                  | CopyForDeref

  syntax Use    ::= Operand

  syntax Repeat ::= "[" Operand ";" Constant "]"
                  | "[" Operand ";" RustExpression "]" [avoid]
  syntax Ref // TODO: define

  // this seems to be responsible for function pointer assignmetn, e.g. `_1 = fn_name`
//  syntax ThreadLocalRef ::= PathExpression

  syntax AddressOf ::= "&" PtrModifiers Place

  syntax Len ::= "Len" "(" Place ")"

  // TODO: this needs additional productions
  syntax Cast ::= Operand "as" Type
                | Operand "as" Type  "(" PointerCastArg ")"
                | PathExpression "as" Type
                | PathExpression "as" Type "(" PointerCastArg ")"

  syntax PointerCastArg ::= "Pointer" "(" PointerCast ")"
  syntax PointerCast ::= "ReifyFnPointer"
                       | "UnsafeFnPointer"
                       | "ClosureFnPointer" "(" Unsafety ")"
                       | "MutToConstPointer"
                       | "ArrayToPointer"
                       | "Unsize"

  syntax Unsafety ::= "Unsafe" | "Normal"

//  syntax MirBuiltInIdentifier ::= Identifier

  syntax NullaryOp ::= Identifier "(" Type ")"

  syntax UnaryOp ::= Identifier "(" Operand ")"

  syntax BinaryOp ::= Identifier "(" Operand "," Operand ")"

  syntax Discriminant ::= "discriminant" "(" Place ")"

  syntax CopyForDeref ::= "deref_copy" NonTerminalPlace

  syntax Aggregate ::= Array
                     | Tuple
                     | Adt
                     | Closure
                     | Generator

  syntax Array ::= "[" "]"
                 | "[" Operand "]"
                 | "[" Operand "," OperandList "]"

  syntax Tuple  ::= "(" ")"
                  | "(" Operand "," OperandList ")"

  syntax Adt ::= StructConstructor
               | EnumConstructor

  syntax StructConstructor ::= Type "{" AdtFieldList "}"

  syntax EnumConstructor ::= Identifier
                           | Identifier "(" OperandList ")"
                           | PathExpression "::" Identifier
                           | PathExpression "::" Identifier "(" OperandList ")"

  syntax AdtField ::= AdtFieldName ":" Operand
  syntax AdtFieldList ::= List{AdtField, ","}

  syntax Closure ::= "[" "closure" "@" FilePosition "]"

  syntax Generator ::= "[" "generator" "@" FilePosition "(" "#" Int ")" "]"
                     | "[" "generator" "@" FilePosition "(" "#" Int ")" "]" "{" AdtFieldList "}"

  syntax ShallowInitBox ::= "ShallowInitBox" "(" Operand "," Type ")"

  syntax OperandList ::= List{Operand, ","}

  syntax PtrModifiers ::= "" | "mut" | "raw" "mut" | "raw" "const"
```

```k
endmodule
```

```k
module MIR-CONSTANT-SYNTAX
  imports MIR-TYPE-SYNTAX

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

### Build-in operations

```k
module MIR-BUILTINS-SYNTAX
  imports BOOL
  imports STRING

  syntax MirBuiltInToken ::= NullaryOpName
                           | UnaryOpName
                           | BinaryOpName
                           | CheckedBinaryOpName

  syntax MirBuiltInToken ::= String2MirBuiltInToken(MirBuiltInToken) [function, hook(STRING.token2string)]

  syntax NullaryOpName ::= "SizeOf"  [token]
                         | "AlignOf" [token]

  syntax UnaryOpName ::= "Not" [token]
                       | "Neg" [token]

  syntax BinaryOpName ::= String2BinaryOpName(String) [function, hook(STRING.string2token)]

  syntax BinaryOpName ::= "Add"    [token]
                        | "Sub"    [token]
                        | "Mul"    [token]
                        | "Div"    [token]
                        | "Rem"    [token]
                        | "BitXor" [token]
                        | "BitAnd" [token]
                        | "BitOr"  [token]
                        | "Shl"    [token]
                        | "Shr"    [token]
                        | "Eq"     [token]
                        | "Lt"     [token]
                        | "Le"     [token]
                        | "Ne"     [token]
                        | "Ge"     [token]
                        | "Gt"     [token]
                        | "Offset" [token]

  syntax Bool ::= isBinOp(String) [function, total]
  //--------------------------------------------------------------------
  rule isBinOp(OP_NAME)  => true
    requires OP_NAME ==String "Add"
      orBool OP_NAME ==String "Sub"
      orBool OP_NAME ==String "Mul"
      orBool OP_NAME ==String "Div"
      orBool OP_NAME ==String "Rem"
      orBool OP_NAME ==String "BitXor"
      orBool OP_NAME ==String "BitAnd"
      orBool OP_NAME ==String "BitOr"
      orBool OP_NAME ==String "Shl"
      orBool OP_NAME ==String "Shr"
      orBool OP_NAME ==String "Eq"
      orBool OP_NAME ==String "Lt"
      orBool OP_NAME ==String "Le"
      orBool OP_NAME ==String "Ne"
      orBool OP_NAME ==String "Ge"
      orBool OP_NAME ==String "Gt"
      orBool OP_NAME ==String "Offset"
  rule isBinOp(_)       => false [owise]

  syntax CheckedBinaryOpName ::= "CheckedAdd"
                               | "CheckedSub"
                               | "CheckedMul"
                               | "CheckedShl"
                               | "CheckedShr"

endmodule
```
