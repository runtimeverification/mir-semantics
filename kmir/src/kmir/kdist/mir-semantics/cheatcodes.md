// Symbolic cheatcode semantics: assume

```k
module KMIR-CHEATCODES
  imports BOOL

  // Bring in execution driver and MIR AST so we can pattern-match on statements
  imports KMIR-CONTROL-FLOW

  // Non-diverging intrinsic: assume(cond)
  // Encodes the cheatcode semantics by adding a path condition via `ensures`.
  // We evaluate the operand to a BoolVal and then conjoin the boolean to the path.
  syntax KItem ::= #assume ( Evaluation ) [strict(1), symbol(cheatcode_assume)]

  // Hook up MIR intrinsic to the cheatcode
  rule <k> #execStmt(statement(statementKindIntrinsic(nonDivergingIntrinsicAssume(OP)), _SPAN))
         => #assume(OP)
       ...
       </k>

  // Insert condition as a post-condition on the transition.
  // If B simplifies to true, this is a no-op; otherwise it is recorded as a
  // path constraint by the backend. Infeasible paths are eliminated by solver.
  rule <k> #assume(BoolVal(B)) => .K ... </k>
    ensures B

endmodule
```
