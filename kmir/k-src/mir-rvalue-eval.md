```k
require "mir-syntax.k"
require "mir-configuration.md"
require "mir-types.md"
```

```k
module MIR-RVALUE-EVAL
  imports MIR-SYNTAX
  imports MIR-TYPES
```

`RValue` evaluation
-------------------

Evaluate a syntactic `RValue` into a semantics `RValueResult`. Inspired by [eval_rvalue_into_place](https://github.com/rust-lang/rust/blob/bd43458d4c2a01af55f7032f7c47d7c8fecfe560/compiler/rustc_const_eval/src/interpret/step.rs#L148).

```k
  syntax InterpResult ::= evalRValue(RValue) [function]
  //---------------------------------------------------
  rule evalRValue(VALUE:BasicRValueNoVariable) => evalBasicRValue(VALUE)
  rule evalRValue([ RVALUES:BasicRValueList ]) => evalBasicRValueList(RVALUES)
  rule evalRValue(RVALUE)                      => Unsupported(RVALUE) [owise]
```

```k
  syntax MIRValue ::= evalBasicRValue(BasicRValue) [function]
  //---------------------------------------------------------
  rule evalBasicRValue(VALUE:Local)               => "Error: evalBasicRValue --- Local is not implemented"
  rule evalBasicRValue(VALUE:NonTerminalPlace)    => "Error: evalBasicRValue --- NonTerminalPlace is not implemented"
  rule evalBasicRValue(move PLACE:Place)          => "Error: evalBasicRValue --- move Place is not implemented"
  rule evalBasicRValue(const VALUE:ConstantValue) => evalConstantValue(VALUE)

  syntax MIRValue ::= evalBasicRValueList(BasicRValueList) [function]
                    | evalBasicRValueListImpl(BasicRValueList, MIRValueNeList) [function]
  //-------------------------------------------------------------------------------------
  rule evalBasicRValueList(.BasicRValueList) => "Error: evalBasicRValueList --- RValueList must not be empty"
  rule evalBasicRValueList(VALUE:BasicRValue , REST:BasicRValueList) => evalBasicRValueListImpl(REST, evalBasicRValue(VALUE))
  rule evalBasicRValueListImpl(.BasicRValueList, RESULT) => RESULT
  rule evalBasicRValueListImpl((VALUE:BasicRValue , REST:BasicRValueList):BasicRValueList, RESULT) =>
       evalBasicRValueListImpl(REST:BasicRValueList:BasicRValueList, evalBasicRValue(VALUE) RESULT)
```

Constant evaluation.
//TODO: implement other cases.

```k
  syntax MIRValue ::= evalConstantValue(ConstantValue) [function]
  //-------------------------------------------------------------
  rule evalConstantValue(VALUE:UnsignedLiteral) => UnsignedLiteral2Int(VALUE)
  rule evalConstantValue(VALUE:SignedLiteral)   => SignedLiteral2Int(VALUE)
  rule evalConstantValue(VALUE:StringLiteral)   => StringLitertal2String(VALUE)
  rule evalConstantValue(_VALUE)                => "Error: evalConstantValue --- unsupported RValue" [owise]
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

  syntax KItem ::= #finished(InterpResult)

  configuration
    <k> $PGM:RValue </k>
    <returncode exit=""> 4 </returncode> // the evaluator exit code

  rule <k> RVALUE:RValue => evalRValue(RVALUE) ... </k>

  rule <k> X:RValueResult => #finished(X:RValueResult) ... </k>
       <returncode> _ => 0 </returncode>
  rule <k> E:InterpError => #finished(E:InterpError) ... </k>
       <returncode> _ => 1 </returncode>


endmodule
```
