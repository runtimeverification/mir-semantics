```k
requires "mir-statement.md"
requires "mir-terminator.md"
requires "mir-identifiers.md"
```

```k
module MIR-BASICBLOCK-SYNTAX
  imports MIR-IDENTIFIERS
  imports MIR-STATEMENT-SYNTAX
  imports MIR-TERMINATOR-SYNTAX

  syntax BasicBlock ::= BBId ":" BasicBlockData

  syntax BasicBlockData ::= "{" Statements Terminator ";" "}"

endmodule
```
