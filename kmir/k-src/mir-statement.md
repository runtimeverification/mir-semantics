```k
require "mir-rvalue.md"
require "mir-place.md"
```
### [Statements](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/enum.StatementKind.html) and [Terminators](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/enum.TerminatorKind.html)

[Statements](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/enum.StatementKind.html) occur within a basic block. They are executed in sequence and never transfer control anywhere outside their basic block.

```k
module MIR-STATEMENT-SYNTAX
  imports MIR-RVALUE-SYNTAX
  imports MIR-PLACE-SYNTAX

  syntax StatementKind  ::= Assign
                      // FakeRead does not seem to be used
                      | "discriminant" "(" Place ")" "=" Int
                      | "Deinit" "(" Place ")"
                      | "StorageLive" "(" Local ")"
                      | "StorageDead" "(" Local ")"
                      // Retag does not seem to be used
                      // AscribeUserType does not seem to be used
                      // Coverage does not seem to be used
                      | NonDivergingIntrinsic
                      | "ConstEvalCounter"
                      // Nop does not seem to be used
  syntax Assign ::= Place "=" RValue
  syntax NonDivergingIntrinsic  ::= "assume" "(" Place ")"
                                  | "copy_nonoverlapping" "(" "dst" "=" RValue "," "src" "=" RValue "," "count" "=" RValue ")"
  syntax Statement ::= StatementKind ";"
  syntax Statements ::= List {Statement, ""}
```

#### Resolved statements are MIR statements where the Places and Locals have been resolved to their indices in the LocalDecls
```k
  syntax ResolvedStatementKind ::= Int "=" RValue
endmodule
```