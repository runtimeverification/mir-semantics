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

  syntax BoundsCheck ::= "\"index out of bounds: the length is {} but the index is {}\"" "," Operand "," Operand
  syntax OverflowNeg ::= "\"attempt to negate" Operand ", which would overflow\""
  syntax DivisionByZero ::= "\"attempt to divide `{}` by zero\"" "," Operand
  syntax RemainderByZero ::= "\"attempt to calculate the remainder of" Operand "with a divisor of zero\""
  syntax Overflow ::= "\"attempt to calculate the remainder of `{}` with a divisor of zero\"" "," Operand
                    | "\"attempt to compute `{} + {}`, which would overflow\"" "," Operand "," Operand
                    | "\"attempt to compute `{} - {}`, which would overflow\"" "," Operand "," Operand
                    | "\"attempt to compute `{} * {}`, which would overflow\"" "," Operand "," Operand
                    | "\"attempt to compute `{} / {}`, which would overflow\"" "," Operand "," Operand
                    | "\"attempt to compute the remainder of `{} % {}`, which would overflow\"" "," Operand "," Operand
                    | "\"attempt to shift right by `{}`, which would overflow\"" "," Operand
                    | "\"attempt to shift left by `{}`, which would overflow\""  "," Operand

  syntax MisalignedPointerDereference ::= "\"misaligned pointer dereference: address must be a multiple of" Operand "but is " Operand "\""
  syntax ResumedAfterReturn ::= "\"generator resumed after completion\""
                              | "\"`async fn` resumed after completion\""
  syntax ResumedAfterPanic ::= "\"generator resumed after panicking\""
                             | "\"`async fn` resumed after panicking\""

endmodule
```