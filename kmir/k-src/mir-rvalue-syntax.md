```k
requires "mir-operand.md"
```

Syntax of rvalues
-----------------

Rvalues are expression that appear on a right-hand-side of an assignment statement.

```k
module MIR-RVALUE-SYNTAX
  imports BOOL
  imports UNSIGNED-INT-SYNTAX
  imports MIR-TYPE-SYNTAX
  imports MIR-OPERAND-SYNTAX
```

### [`RValue`](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/enum.Rvalue.html)

The various kinds of rvalues that can appear in MIR.

```k
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
  syntax Cast ::= Operand "as" Type [prefer]
                | Operand "as" Type  "(" PointerCastArg ")" [prefer]
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

  syntax NullaryOp ::= NullaryOpName "(" Type ")"
  syntax NullaryOpName ::= "SizeOf"  [token]
                         | "AlignOf" [token]  

  syntax UnaryOp ::= UnaryOpName "(" Operand ")"
  syntax UnaryOpName ::= "Not" [token]
                       | "Neg" [token]

  syntax BinaryOp ::= BinaryOpName "(" Operand "," Operand ")"
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
                            //  | TypePath "(" OperandList ")" // compiletest-rs/ui/traits/copy-requires-self-wf.mir LINE 17

  // `AssertKind` `Eq`, `Ne` conflict with BinaryOp names https://github.com/rust-lang/rust/blob/f562931178ff103f23b9e9a10dc0deb38e0d064f/library/core/src/panicking.rs#L259-L263
  syntax EnumConstructor ::= Identifier
                           | Identifier "(" OperandList ")"
                           | PathExpression "::" Identifier [avoid]
                           | PathExpression "::" "Eq"
                           | PathExpression "::" "Ne"
                          //  | PathExpression "::" "Match" // Match isn't conflicting at the moment but might later
                           | PathExpression "::" Identifier "(" OperandList ")"

  syntax AdtField ::= AdtFieldName ":" Operand
  syntax AdtFieldList ::= List{AdtField, ","}

  syntax Closure ::= "[" "closure" "@" FilePosition "]"

  syntax Generator ::= "[" "generator" "@" FilePosition "(" "#" Int ")" "]"
                     | "[" "generator" "@" FilePosition "(" "#" Int ")" "]" "{" AdtFieldList "}"

  syntax ShallowInitBox ::= "ShallowInitBox" "(" Operand "," Type ")"

  syntax OperandList ::= List{Operand, ","}

  syntax PtrModifiers ::= "" | "mut" | "raw" "mut" | "raw" "const"

  syntax RValue ::= #unwrap(Operand)
```

```k
endmodule
```

