# CSE Support

Helper constructs for Compositional Symbolic Execution summary rules.

```k
module KMIR-CSE-SUPPORT
  imports KMIR-CONTROL-FLOW
  imports RT-DATA

  // Helper for value-returning CSE summaries: evaluates the operand first via seqstrict,
  // then sets the local to the computed return value.
  syntax KItem ::= "#cseReturn" "(" Place "," Evaluation ")" [seqstrict(2), symbol(cseReturn)]

  rule <k> #cseReturn(DEST, VAL:Value) => #setLocalValue(DEST, VAL) ... </k>
endmodule
```
