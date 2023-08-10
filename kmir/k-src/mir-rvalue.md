```k
require "mir-syntax.md"
require "mir-configuration.md"
require "mir-operand.md"
require "mir-types.md"
```

Syntax of rvalues
-----------------

Rvalues are expression that appear on a right-hand-side of an assignment statement.

```k
module MIR-RVALUE-SYNTAX
//  imports BOOL
//  imports UNSIGNED-INT-SYNTAX
  imports MIR-TYPE-SYNTAX
  imports MIR-OPERAND-SYNTAX
  imports MIR-CONSTANT-SYNTAX
```

### [`RValue`](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/enum.Rvalue.html)

```k
  syntax RValue ::= Use
                  | Repeat
                  | Ref
//                  | ThreadLocalRef 
                  | AddressOf
                  | Len
                  | Cast
                  | BinaryOp
                  | CheckedBinaryOp
                  | NullaryOp
                  | UnaryOp
                  | Discriminant
                  | Aggregate
                  | ShallowInitBox
                  | CopyForDeref

  syntax Use    ::= Operand

  syntax Repeat ::= "[" Operand ";" Constant "]"
  //                | "[" Operand ";" RustExpression "]" [avoid]
  
  syntax Ref ::= "&" Region Place
               | "&" Region BorrowKind Place
  syntax Region //TODO: to be defined: https://github.com/rust-lang/rust/blob/e3590fccfbdb6284bded9b70eca2e72b0c57e070/compiler/rustc_middle/src/mir/mod.rs#L2081

  syntax BorrowKind ::= "shallow" | "mut"

  // this seems to be responsible for function pointer assignmetn, e.g. `_1 = fn_name`
//  syntax ThreadLocalRef ::= PathExpression

  syntax AddressOf ::= "&raw" Mutability Place
  syntax Mutability ::= "mut" | "const" 
  //TODO:in rustc_ast, Not < Mut, why there is an order

  syntax Len ::= "Len" "(" Place ")"

  syntax Cast ::= Operand "as" Type "(" CastKind ")"
  syntax CastKind ::= "PointerExposeAddress" //TODO: figure out the syntax here.
                    | "PointerFromExposeAddress"
                    | "Pointer" "(" PointerCast ")"
                    | "DynStar"
                    | "IntToInt" 
                    | "FloatToInt"
                    | "FloatToFloat"
                    | "IntToFloat"
                    | "PtrToPtr"
                    | "FnPtrToPtr"
                    | "Transmute" // MIR is well-formed if the input and output types have different sizes, but running a transmute between differently-sized types is UB.

//TODO: Need locate the exact definition, starting point CastKind: https://github.com/rust-lang/rust/blob/f88a8b71cebb730cbd5058c45ebcae1d4d9be377/compiler/rustc_middle/src/mir/syntax.rs#L1231
  syntax PointerCast ::= "ReifyFnPointer"
                       | "UnsafeFnPointer"
                       | "ClosureFnPointer" "(" Unsafety ")"
                       | "MutToConstPointer"
                       | "ArrayToPointer"
                       | "Unsize"

  syntax Unsafety ::= "Unsafe" | "Normal"

  syntax BinaryOp ::= BinOp "(" Operand "," Operand ")"
  syntax BinOp ::= "Add"          [token]
                 | "AddUnchecked" [token]
                 | "Sub"          [token]
                 | "SubUnchecked" [token]
                 | "Mul"          [token]
                 | "MulUnchecked" [token]
                 | "Div"          [token]
                 | "Rem"          [token]
                 | "BitXor"       [token]
                 | "BitAnd"       [token]
                 | "BitOr"        [token]
                 | "Shl"          [token]
                 | "ShlUnchecked" [token]
                 | "Shr"          [token]
                 | "ShrUnchecked" [token]
                 | "Eq"           [token]
                 | "Lt"           [token]
                 | "Le"           [token]
                 | "Ne"           [token]
                 | "Ge"           [token]
                 | "Gt"           [token]
                 | "Offset"       [token]

// CheckedBinaryOp is the same as BinaryOp except additional overflow checking. https://github.com/rust-lang/rust/blob/f88a8b71cebb730cbd5058c45ebcae1d4d9be377/compiler/rustc_middle/src/mir/syntax.rs#L1178
  syntax CheckedBinaryOp ::= "Checked" BinOp "(" Operand "," Operand ")"
                              
  syntax NullaryOp ::= NullOp "(" Type ")"
                     | NullOpOffset "(" Type ")" Fields
  syntax NullOp ::= "SizeOf"   [token]
                  | "AlignOf"  [token]  
  syntax NullOpOffset ::= "OffsetOf" [token]

  syntax FieldIdx
  syntax Fields ::= List{FieldIdx, ","} //TODO: define the Feilds


  syntax UnaryOp ::= UnOp "(" Operand ")"
  syntax UnOp ::= "Not" [token]
                | "Neg" [token]
                        
  syntax Discriminant ::= "discriminant" "(" Place ")"

  syntax CopyForDeref ::= "deref_copy" Place// NonTerminalPlace "deref_copy {place:#?}"

//TODO: Need further refactoring
  syntax Aggregate ::= AggregateKind
  syntax AggregateKind ::= Array
                     | Tuple
                     | Adt
                     | Closure
                     | Generator

  syntax OperandList ::= List{Operand, ","}

//Array is defined: IndexVec<FieldIdx, Operand>, hook to K-Array?
  syntax Array ::= "[" "]"
                 | "[" Operand "]"
                 | "[" Operand "," OperandList "]"

  syntax Tuple  ::= "(" ")"
                  | "(" Operand "," OperandList ")" //TODO:(Operand, Operand)?

  syntax Adt ::= StructConstructor
               | EnumConstructor

  syntax StructConstructor ::= Type "{" AdtFieldList "}"

  syntax EnumConstructor ::= Identifier
                           | Identifier "(" OperandList ")"
                           | PathExpression "::" Identifier
                           | PathExpression "::" Identifier "(" OperandList ")"

  syntax AdtField ::= AdtFieldName ":" Operand
  syntax AdtFieldList ::= List{AdtField, ","}

  syntax Closure ::= "[" "closure" "@" FilePosition "]" //FilePosition should be function path or defid

  syntax Generator ::= "[" "generator" "@" FilePosition "(" "#" Int ")" "]"
                     | "[" "generator" "@" FilePosition "(" "#" Int ")" "]" "{" AdtFieldList "}"

  syntax ShallowInitBox ::= "ShallowInitBox" "(" Operand "," Type ")"
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
  //TODO: checkedBinOp should be implemented with AssertKind
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
  rule evalUnaryOp(FN_KEY, NAME:UnOp (X:Operand)) =>
       evalUnaryOpImpl(FN_KEY, NAME, X)

  syntax MIRValue ::= evalUnaryOpImpl(FunctionLikeKey, UnOp, Operand) [function]
  //-----------------------------------------------------------------------------------
  rule evalUnaryOpImpl(FN_KEY, Not, X)    => notBool {evalOperand(FN_KEY, X)}:>Bool
  rule evalUnaryOpImpl(FN_KEY, Neg, X)    => 0 -Int {evalOperand(FN_KEY, X)}:>Int
```

### `BinaryOp` evaluation

```k
  syntax MIRValue ::= evalBinaryOp(FunctionLikeKey, BinaryOp) [function]
  //--------------------------------------------------------------------
  rule evalBinaryOp(FN_KEY, NAME:BinOp (X:Operand, Y:Operand)) =>
       evalBinaryOpImpl(FN_KEY, NAME, X, Y)

  syntax MIRValue ::= evalBinaryOpImpl(FunctionLikeKey, BinOp, Operand, Operand) [function]
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
