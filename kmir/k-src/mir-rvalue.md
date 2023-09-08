```k
require "mir-syntax.md"
require "mir-configuration.md"
require "mir-operand.md"
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

Evaluation of rvalues
---------------------

```k
module MIR-RVALUE
  imports MIR-RVALUE-SYNTAX
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
  rule evalUnaryOp(FN_KEY, NAME:UnaryOpName (X:Operand)) =>
       evalUnaryOpImpl(FN_KEY, NAME, X)

  syntax MIRValue ::= evalUnaryOpImpl(FunctionLikeKey, UnaryOpName, Operand) [function]
  //-----------------------------------------------------------------------------------
  rule evalUnaryOpImpl(FN_KEY, Not, X)    => notBool {evalOperand(FN_KEY, X)}:>Bool
  rule evalUnaryOpImpl(FN_KEY, Neg, X)    => 0 -Int {evalOperand(FN_KEY, X)}:>Int
```

### `BinaryOp` evaluation

```k
  syntax MIRValue ::= evalBinaryOp(FunctionLikeKey, BinaryOp) [function]
  //--------------------------------------------------------------------
  rule evalBinaryOp(FN_KEY, NAME:BinaryOpName (X:Operand, Y:Operand)) =>
       evalBinaryOpImpl(FN_KEY, NAME, X, Y)

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
  // rule evalBinaryOpImpl(FN_KEY, _, X, Y) => "not supported" [owise]
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
