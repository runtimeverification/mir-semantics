```k
require "mir-syntax.md"
require "mir-configuration.md"
require "mir-types.md"
```

Syntax of rvalues
-----------------

Rvalues are expression that appear on a right-hand-side of an assignment statement.

```k
module MIR-RVALUE-SYNTAX
  imports BOOL
  imports UNSIGNED-INT-SYNTAX
  imports MIR-TYPE-SYNTAX
  imports MIR-PLACE-SYNTAX
  imports MIR-CONSTANT-SYNTAX
```

### [`Operand`](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/enum.Operand.html)

Operands are leafs, i.e. the "basic components" of rvalues: either a loading of a place, or a constant.

```k
  syntax Operand ::= Place
                   | "move" Place
                   | Constant
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

  syntax UnaryOpName ::= String2UnaryOpName(String) [function, hook(STRING.string2token)]

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

  syntax Bool ::= isUnOp(String) [function, total]
  //----------------------------------------------
  rule isUnOp(OP_NAME)  => true
    requires OP_NAME ==String "Not"
      orBool OP_NAME ==String "Neg"
  rule isUnOp(_)       => false [owise]

  syntax Bool ::= isBinOp(String) [function, total]
  //-----------------------------------------------
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

Evaluation of rvalues
---------------------

```k
module MIR-RVALUE
  imports MIR-RVALUE-SYNTAX
  imports MIR-BUILTINS-SYNTAX
  imports MIR-TYPES
  imports MIR-CONFIGURATION
```

Evaluate a syntactic `RValue` into a semantics `RValueResult`. Inspired by [eval_rvalue_into_place](https://github.com/rust-lang/rust/blob/bd43458d4c2a01af55f7032f7c47d7c8fecfe560/compiler/rustc_const_eval/src/interpret/step.rs#L148).

```k
  syntax InterpResult ::= evalRValue(FunctionLikeKey, RValue) [function]
  //--------------------------------------------------------------------
  rule evalRValue(FN_KEY, VALUE:Operand)   => evalOperand(FN_KEY, VALUE)
  rule evalRValue(FN_KEY, UN_OP:UnaryOp)   => evalUnaryOp(FN_KEY, UN_OP)
  rule evalRValue(FN_KEY, BIN_OP:BinaryOp) => evalBinaryOp(FN_KEY, BIN_OP)
  rule evalRValue(_FN_KEY, RVALUE)         => Unsupported(RVALUE) [owise]
```

### `Operand` evaluation

```k
  syntax MIRValue ::= evalOperand(FunctionLikeKey, Operand) [function]
  //------------------------------------------------------------------
  rule evalOperand(_, const VALUE:ConstantValue)     => evalConstantValue(VALUE)
  rule evalOperand(FN_KEY, LOCAL:Local)                   => evalLocal(FN_KEY, LOCAL)
  rule evalOperand(FN_KEY, move LOCAL:Local)              => evalLocal(FN_KEY, LOCAL)
```

### `UnaryOp` evaluation

```k
  syntax MIRValue ::= evalUnaryOp(FunctionLikeKey, UnaryOp) [function]
  //------------------------------------------------------------------
  rule evalUnaryOp(FN_KEY, NAME:IdentifierToken (X:Operand)) =>
       evalUnaryOpImpl(FN_KEY, String2UnaryOpName(IdentifierToken2String(NAME)), X)

  syntax MIRValue ::= evalUnaryOpImpl(FunctionLikeKey, UnaryOpName, Operand) [function]
  //-----------------------------------------------------------------------------------
  rule evalUnaryOpImpl(FN_KEY, Not, X)    => notBool {evalOperand(FN_KEY, X)}:>Bool
  rule evalUnaryOpImpl(FN_KEY, Neg, X)    => 0 -Int {evalOperand(FN_KEY, X)}:>Int
```

### `BinaryOp` evaluation

```k
  syntax MIRValue ::= evalBinaryOp(FunctionLikeKey, BinaryOp) [function]
  //--------------------------------------------------------------------
  rule evalBinaryOp(FN_KEY, NAME:IdentifierToken (X:Operand, Y:Operand)) =>
       evalBinaryOpImpl(FN_KEY, String2BinaryOpName(IdentifierToken2String(NAME)), X, Y)

  syntax MIRValue ::= evalBinaryOpImpl(FunctionLikeKey, BinaryOpName, Operand, Operand) [function]
  //-----------------------------------------------------------------------
  rule evalBinaryOpImpl(FN_KEY, Add, X, Y)    => {evalOperand(FN_KEY, X)}:>Int +Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, Sub, X, Y)    => {evalOperand(FN_KEY, X)}:>Int -Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, Mul, X, Y)    => {evalOperand(FN_KEY, X)}:>Int *Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, Div, X, Y)    => {evalOperand(FN_KEY, X)}:>Int /Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, Rem, X, Y)    => {evalOperand(FN_KEY, X)}:>Int %Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, BitXor, X, Y) => {evalOperand(FN_KEY, X)}:>Int xorInt {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, BitOr, X, Y)  => {evalOperand(FN_KEY, X)}:>Int |Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, BitAnd, X, Y) => {evalOperand(FN_KEY, X)}:>Int &Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, Shl, X, Y)    => {evalOperand(FN_KEY, X)}:>Int <<Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, Shr, X, Y)    => {evalOperand(FN_KEY, X)}:>Int >>Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, Eq, X, Y)     => {evalOperand(FN_KEY, X)}:>Int ==Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, Lt, X, Y)     => {evalOperand(FN_KEY, X)}:>Int <Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, Le, X, Y)     => {evalOperand(FN_KEY, X)}:>Int <=Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, Ne, X, Y)     => {evalOperand(FN_KEY, X)}:>Int =/=Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, Ge, X, Y)     => {evalOperand(FN_KEY, X)}:>Int >=Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, Gt, X, Y)     => {evalOperand(FN_KEY, X)}:>Int >Int {evalOperand(FN_KEY, Y)}:>Int
  // rule evalBinaryOpImpl("Offset", X, Y) => "not implemented"
```

### Constant evaluation.
//TODO: implement other cases.

```k
  syntax MIRValue ::= evalConstantValue(ConstantValue) [function]
  //-------------------------------------------------------------
  rule evalConstantValue(VALUE:UnsignedLiteral) => UnsignedLiteral2Int(VALUE)
  rule evalConstantValue(VALUE:SignedLiteral)   => SignedLiteral2Int(VALUE)
  rule evalConstantValue(VALUE:StringLiteral)   => StringLitertal2String(VALUE)
  rule evalConstantValue(( ))                   => Unit
  rule evalConstantValue(VALUE:Bool)            => VALUE
//  rule evalConstantValue(_VALUE)              => "Error: evalConstantValue --- unsupported ConstantValue" [owise]
```

### `Local` evaluation

Locals only makes sense withing a function-like, hence we evaluate them as a contextual function that grabs the value from the function-like's environment:

```k
  syntax MIRValue ::= evalLocal(FunctionLikeKey, Local) [function]
  //--------------------------------------------------------------
  rule [[ evalLocal(FN_KEY, LOCAL) => VALUE ]]
    <function>
      <fnKey> FN_KEY </fnKey>
      <localDecl>
        <index> INDEX </index>
        <value> VALUE </value>
        ...
      </localDecl>
      ...
    </function>
    requires  INDEX ==Int Local2Int(LOCAL)
```


```k
endmodule
```
