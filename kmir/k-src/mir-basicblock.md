```k
requires "mir-statement.md"
requires "mir-terminator.md"
```

```k
module MIR-BASICBLOCK-SYNTAX
  imports MIR-STATEMENT-SYNTAX
  imports MIR-TERMINATOR-SYNTAX


  syntax BasicBlock ::= BB ":" BasicBlockBody
  syntax BasicBlockBody ::= "{" Statements Terminator ";" "}"
  syntax BasicBlockList ::= List {BasicBlock, ""}
endmodule
```