```k
require "mir-rvalue.md"
```
## [Statements]
[Statements](https://github.com/rust-lang/rust/blob/e3590fccfbdb6284bded9b70eca2e72b0c57e070/compiler/rustc_middle/src/mir/mod.rs#L1450) occur within a basic block. They are executed in sequence and never transfer control anywhere outside their basic block.

```k
module MIR-STATEMENT-SYNTAX
  imports MIR-PLACE
  imports MIR-RVALUE-SYNTAX

  syntax Statements ::= List {Statement, ";"}

  syntax Statement  ::= Place "=" RValue // StatementKind::Assign
                      | "FakeRead" FakeReadCause "," Place // StatementKind::FakeRead
                      | "Retag" "()" Place //where RetagKindPretty = ""
                      | "Retag" "(" RetagKindPretty ")" Place
                      | "StorageLive" "(" Local ")"
                      | "StorageDead" "(" Local ")"
                      | "discriminant" "(" Place ")" "=" VariantIdx
                      | "Deinit" "(" Place ")"
                      | "PlaceMention" "(" Place ")" 
                      | "AscribeUserType" "(" Place "," Variance "," UserTypeProjection ")" //TODOmod.rs#L1478
                      | "Coverage" "::" CoverageKind "for" CodeRegion //TODO:mod.rs#L1481
                      | "Coverage" "::" CoverageKind //TODO
                      | "{" "intrinsic" "}" //StatemetKind::NonDivergingIntrinsic
                      | "ConstEvalCounter" //StatementKind::ConstEvalCounter
                      | "nop" //StatementKind::NOP

  syntax FakeReadCause
  syntax RetagKindPretty ::= "[fn entry]" | "[2phase]" | "[raw]"  //RetagKind: mod.rs#L1461
  syntax VariantIdx = Int // TODO: need to find the definition of VariantIdx
  syntax Variance
  syntax UserTypeProjection
  syntax CoverageKind
  syntax CodeRegion

endmodule
```
