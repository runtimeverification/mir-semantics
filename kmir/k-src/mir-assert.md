```k
require "mir-operand.md"
```

```k
module MIR-ASSERT-SYNTAX 
  import MIR-OPERAND-SYNTAX

  syntax AssertKind ::= BoundsCheck
                      | Overflow
                      | OverflowNeg
                      | DivisionByZero
                      | RemainderByZero
                      | ResumedAfterReturn
                      | ResumedAfterPanic
                      | MisalignedPointerDereference

  syntax BoundsCheck ::= "index out of bounds: the length is " Operand " but the index is " Operand //Should this Oprand always uSize
                       | "\"index out of bounds: the length is {} but the index is {}\"" "," Operand "," Operand //Should this Oprand always uSize
  syntax OverflowNeg ::= "attempt to negate " Operand ", which would overflow"
  syntax DivisionByZero ::= "attempt to divide " Operand " by zero"
  syntax RemainderByZero ::= "attempt to calculate the remainder of " Operand " with a divisor of zero"
  syntax Overflow ::= "attempt to compute " Operand " + " Operand ", which would overflow"
                    | "attempt to compute " Operand " - " Operand ", which would overflow"
                    | "attempt to compute " Operand " * " Operand ", which would overflow"
                    | "attempt to compute " Operand " / " Operand ", which would overflow"
                    | "attempt to compute " Operand " % " Operand ", which would overflow"
                    | "attempt to shift right by " Operand ", which would overflow"
                    | "attempt to shift left by " Operand ", which would overflow"
  syntax MisalignedPointerDereference ::= "misaligned pointer dereference: address must be a multiple of " Operand " but is " Operand
  syntax ResumedAfterReturn ::= "generator resumed after completion"
                              | "`async fn` resumed after completion"
  syntax ResumedAfterPanic ::= "generator resumed after panicking"
                             | "`async fn` resumed after panicking"

endmodule
```