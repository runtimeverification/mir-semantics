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
  syntax InterpResult ::= evalRValue(RValue) [function]
  //---------------------------------------------------
  rule evalRValue(VALUE:Operand)   => evalOperand(VALUE)
  rule evalRValue(BIN_OP:BinaryOp) => evalBinaryOp(BIN_OP)
  rule evalRValue(RVALUE)          => Unsupported(RVALUE) [owise]
```

### `Operand` evaluation

```k
  syntax MIRValue ::= evalOperand(Operand) [function]
  //-------------------------------------------------
  rule evalOperand(const VALUE:ConstantValue)     => evalConstantValue(VALUE)
  rule evalOperand(LOCAL:Local)                   => evalLocal(LOCAL)
  rule evalOperand(move LOCAL:Local)              => evalLocal(LOCAL)
//  rule evalOperand(VALUE:NonTerminalPlace)      => "Error: evalOperand --- NonTerminalPlace is not implemented"
//  rule evalOperand(move VALUE:NonTerminalPlace) => "Error: evalOperand --- NonTerminalPlace is not implemented"
```

### `BinaryOp` evaluation

```k
  syntax MIRValue ::= evalBinaryOp(BinaryOp) [function]
  //---------------------------------------------------
  rule evalBinaryOp(NAME:IdentifierToken (X:Operand, Y:Operand)) =>
       evalBinaryOpImpl(String2BinaryOpName(IdentifierToken2String(NAME)), X, Y)

  syntax MIRValue ::= evalBinaryOpImpl(BinaryOpName, Operand, Operand) [function]
  //-----------------------------------------------------------------------
  rule evalBinaryOpImpl(Add, X, Y)    => {evalOperand(X)}:>Int +Int {evalOperand(Y)}:>Int
  rule evalBinaryOpImpl(Sub, X, Y)    => {evalOperand(X)}:>Int -Int {evalOperand(Y)}:>Int
  rule evalBinaryOpImpl(Mul, X, Y)    => {evalOperand(X)}:>Int *Int {evalOperand(Y)}:>Int
  rule evalBinaryOpImpl(Div, X, Y)    => {evalOperand(X)}:>Int /Int {evalOperand(Y)}:>Int
  rule evalBinaryOpImpl(Rem, X, Y)    => {evalOperand(X)}:>Int %Int {evalOperand(Y)}:>Int
  rule evalBinaryOpImpl(BitXor, X, Y) => {evalOperand(X)}:>Int xorInt {evalOperand(Y)}:>Int
  rule evalBinaryOpImpl(BitOr, X, Y)  => {evalOperand(X)}:>Int |Int {evalOperand(Y)}:>Int
  rule evalBinaryOpImpl(BitAnd, X, Y) => {evalOperand(X)}:>Int &Int {evalOperand(Y)}:>Int
  rule evalBinaryOpImpl(Shl, X, Y)    => {evalOperand(X)}:>Int <<Int {evalOperand(Y)}:>Int
  rule evalBinaryOpImpl(Shr, X, Y)    => {evalOperand(X)}:>Int >>Int {evalOperand(Y)}:>Int
  rule evalBinaryOpImpl(Eq, X, Y)     => {evalOperand(X)}:>Int ==Int {evalOperand(Y)}:>Int
  rule evalBinaryOpImpl(Lt, X, Y)     => {evalOperand(X)}:>Int <Int {evalOperand(Y)}:>Int
  rule evalBinaryOpImpl(Le, X, Y)     => {evalOperand(X)}:>Int <=Int {evalOperand(Y)}:>Int
  rule evalBinaryOpImpl(Ne, X, Y)     => {evalOperand(X)}:>Int =/=Int {evalOperand(Y)}:>Int
  rule evalBinaryOpImpl(Ge, X, Y)     => {evalOperand(X)}:>Int >=Int {evalOperand(Y)}:>Int
  rule evalBinaryOpImpl(Gt, X, Y)     => {evalOperand(X)}:>Int >Int {evalOperand(Y)}:>Int
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

Locals only makes sense withing a function-like, hence we evaluate them as a contextual function that grabs the current function from the global configuration:

```k
  syntax MIRValue ::= evalLocal(Local) [function]
  //---------------------------------------------
  rule [[ evalLocal(LOCAL) => VALUE ]]
    <currentFnKey> FN_KEY </currentFnKey>
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
           <currentFnKey>
             Fn(String2IdentifierToken("dummy"):FunctionPath)
           </currentFnKey>
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
