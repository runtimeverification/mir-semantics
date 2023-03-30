```k
require "mir-syntax.md"
require "mir-rvalue-syntax.md"
require "mir-configuration.md"
require "mir-types.md"
```

```k
module MIR-RVALUE-EVAL
  imports MIR-SYNTAX
  imports MIR-BUILTINS-SYNTAX
  imports MIR-TYPES
  imports MIR-CONFIGURATION
```

`RValue` evaluation
-------------------

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
//  rule evalOperand(VALUE:NonTerminalPlace)      => "Error: evalOperand --- NonTerminalPlace is not implemented"
//  rule evalOperand(move VALUE:NonTerminalPlace) => "Error: evalOperand --- NonTerminalPlace is not implemented"
```

### `UnaryOp` evaluation

```k
  syntax MIRValue ::= evalUnaryOp(FunctionLikeKey, UnaryOp) [function]
  //---------------------------------------------------
  rule evalUnaryOp(FN_KEY, NAME:IdentifierToken (X:Operand)) =>
       evalUnaryOpImpl(FN_KEY, String2UnaryOpName(IdentifierToken2String(NAME)), X)

  syntax MIRValue ::= evalUnaryOpImpl(FunctionLikeKey, UnaryOpName, Operand) [function]
  //------------------------------------------------------------------
  rule evalUnaryOpImpl(FN_KEY, Not, X)    => notBool {evalOperand(FN_KEY, X)}:>Bool
  rule evalUnaryOpImpl(FN_KEY, Neg, X)    => 0 -Int {evalOperand(FN_KEY, X)}:>Int
```

### `BinaryOp` evaluation

```k
  syntax MIRValue ::= evalBinaryOp(FunctionLikeKey, BinaryOp) [function]
  //---------------------------------------------------
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

Locals only makes sense withing a function-like, hence we evaluate them as a contextual function that grabs the necessary values from the function-like's environment:

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



Standalone expression interpreter
---------------------------------

The following module implements a standalone K semantics for interpreting MIR expressions.
This module *MUST NOT* be imported by any other module. Import `MIR-RVALUE-EVAL` instead.

```k
module KMIR-CONSTEVAL
  imports MIR-RVALUE-EVAL
  imports MIR-CONFIGURATION

  syntax KItem ::= #finished(InterpResult)

  configuration
    <k> #initDefaultMir() ~> $PGM:RValue </k>
    <returncode exit=""> 4 </returncode> // the evaluator exit code
    <mir/>

  rule <k> RVALUE:RValue => evalRValue(RVALUE) ... </k>

  rule <k> X:RValueResult => #finished(X:RValueResult) ... </k>
       <returncode> _ => 0 </returncode>
  rule <k> E:InterpError => #finished(E:InterpError) ... </k>
       <returncode> _ => 1 </returncode>
```

```k
  syntax KItem ::= #initDefaultMir()
  //--------------------------------
  rule <k> #initDefaultMir() => .K ... </k>
       <mir> _ =>
         <env>
           <callStack>
             ListItem(Fn(String2IdentifierToken("dummy"):FunctionPath))
           </callStack>
           <currentBasicBlock>
             0
           </currentBasicBlock>
         </env>
         <functions>
           <function>
             <fnKey> Fn(String2IdentifierToken("dummy"):FunctionPath)  </fnKey>
             <localDecls>
               <localDecl>
                   <index> 0:Int </index>
                   <value>       0:MIRValue     </value>
                   ...
               </localDecl>
               <localDecl>
                   <index> 1:Int </index>
                   <value>       1:MIRValue     </value> ...
               </localDecl>
             </localDecls>
             <basicBlocks> .Bag </basicBlocks>
           </function>
         </functions>
       </mir>


```

```k
endmodule
```
