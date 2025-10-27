## Cheatcodes

### Assume

- Purpose: prune paths by assuming a boolean condition.
- Hook: NonDivergingIntrinsic::Assume.
- Semantics: add a path constraint via ensures (post-condition); false makes the path infeasible; true is a no-op.

```k
module KMIR-CHEATCODES
  imports BOOL
  imports KMIR-CONTROL-FLOW

  // Driver
  syntax KItem ::= #assume ( Evaluation ) [strict(1), symbol(cheatcode_assume)]

  // Hook: intrinsic → cheatcode
  rule <k> #execStmt(statement(statementKindIntrinsic(nonDivergingIntrinsicAssume(OP)), _SPAN))
         => #assume(OP)
       ...
       </k>

  // Post-condition
  rule <k> #assume(BoolVal(B)) => .K ... </k>
    ensures B

endmodule
```
