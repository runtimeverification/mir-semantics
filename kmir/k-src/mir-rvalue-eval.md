```k
require "mir-syntax.md"
require "mir-configuration.md"
require "mir-types.md"
```

```k
module MIR-RVALUE-EVAL
  imports MIR-SYNTAX
  imports MIR-TYPES
  imports MIR-CONFIGURATION
```

`RValue` evaluation
-------------------

Evaluate a syntactic `RValue` into a semantics `RValueResult`. Inspired by [eval_rvalue_into_place](https://github.com/rust-lang/rust/blob/bd43458d4c2a01af55f7032f7c47d7c8fecfe560/compiler/rustc_const_eval/src/interpret/step.rs#L148).

```k
  syntax InterpResult ::= evalRValue(RValue) [function]
  //---------------------------------------------------
  rule evalRValue(VALUE:Operand)           => evalOperand(VALUE)
  rule evalRValue(OP_NAME:Identifier (LHS:Operand, RHS:Operand):BinaryOp) => {evalOperand(LHS)}:>Int >Int {evalOperand(RHS)}:>Int
  rule evalRValue(RVALUE)                  => Unsupported(RVALUE) [owise]
```

```k
  syntax MIRValue ::= evalOperand(Operand) [function]
  //---------------------------------------------------------
  rule evalOperand(VALUE:Local)               => evalLocal(VALUE)
  rule evalOperand(const VALUE:ConstantValue) => evalConstantValue(VALUE)
//  rule evalOperand(VALUE:NonTerminalPlace)    => "Error: evalOperand --- NonTerminalPlace is not implemented"
//  rule evalOperand(move PLACE:Place)          => "Error: evalOperand --- move Place is not implemented"

  syntax MIRValue ::= evalOperandList(OperandList) [function]
                    | evalOperandListImpl(OperandList, MIRValueNeList) [function]
  //-----------------------------------------------------------------------------
  rule evalOperandList(.OperandList) => "Error: evalOperandList --- RValueList must not be empty"
  rule evalOperandList(VALUE:Operand , REST:OperandList) => evalOperandListImpl(REST, evalOperand(VALUE))
  rule evalOperandListImpl(.OperandList, RESULT) => RESULT
  rule evalOperandListImpl((VALUE:Operand , REST:OperandList):OperandList, RESULT) =>
       evalOperandListImpl(REST:OperandList:OperandList, evalOperand(VALUE) RESULT)
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
//  rule evalConstantValue(_VALUE)                => "Error: evalConstantValue --- unsupported RValue" [owise]
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
