```k
require "mir-syntax.md"
require "mir-configuration.md"

module PANICS
  imports MIR-SYNTAX
  imports MIR-CONFIGURATION

  syntax InternalPanic ::= "DuplicateBinding"
                         | "DuplicateFunction"
                         | "DuplicateBasicBlock"
                         | "MissingBasicBlock"
                         | "NotImplemented"
                         | "RValueEvalError"
                         | "TypeError"

  syntax Panic ::= "AssertionViolation"

  syntax KItem ::= #internalPanic(FunctionLikeKey, InternalPanic, KItem)

  syntax KItem ::= #panic(FunctionLikeKey, Panic, KItem)
endmodule
```
