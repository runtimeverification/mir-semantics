```k
require "mir-syntax.k"

module PANICS
  imports MIR-SYNTAX

  syntax InternalPanic ::= "DuplicateBinding"
                         | "DuplicateFunction"
                         | "DuplicateBasicBlock"
                         | "MissingBasicBlock"
                         | "NotImplemented"
                         | "RValueEvalError"
                         | "TypeError"

  syntax Panic ::= "AssertionViolation"

endmodule
```
