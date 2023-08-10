```k
requires "mir-statement.md"
requires "mir-rvalue.md"
requires "mir-place.md"
```

```k
module MIR-BASICBLOCK-SYNTAX
  imports MIR-STATEMENT-SYNTAX
  imports MIT-TERMINATOR-SYNTAX

  syntax BasicBlock ::= BBId ":" BasicBlockData
  syntax BBId ::= "bb" Int [token]
  syntax BasicBlockData ::= "{" Statements Terminator ";" "}"

endmodule
```

## [Statements]
[Statements](https://github.com/rust-lang/rust/blob/e3590fccfbdb6284bded9b70eca2e72b0c57e070/compiler/rustc_middle/src/mir/mod.rs#L1450) occur within a basic block. They are executed in sequence and never transfer control anywhere outside their basic block.

```k
module MIR-STATEMENT-SYNTAX
  imports MIR-PLACE
  imports MIT-RVALUE-SYNTAX
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
  syntax RetagKindPretty = "[fn entry]" | "[2phase]" | "[raw]"  //RetagKind: mod.rs#L1461
  syntax VariantIdx = Int // TODO: need to find the definition of VariantIdx
  syntax Variance
  syntax UserTypeProjection
  syntax CoverageKind
  syntax CodeRegion

endmodule
```
## [Terminators](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/enum.TerminatorKind.html) occur at the end of a basic block and always transfer control outside the current block: either to a block within the same function or to a block outside of it.

```k
module MIR-TERMINATOR-SYNTAX
  syntax Terminator ::= Goto
                      | SwitchInt
                      | Resume
                      | Abort
                      | Return
                      | Unreachable
                      | Call
                      | Yield
                      | GeneratorDrop
                      | FalseEdge
                      | InlineAsm

  syntax Goto ::= "goto" "->" BBId
  syntax SwitchInt ::= "switchInt" "(" Operand ")" "->" "[" SwitchTargets "," "otherwise" ":" BB "]"
  syntax Resume ::= "resume"
  syntax Abort ::= "abort"
  syntax Return ::= "return"
  syntax Unreachable ::= "unreachable"

endmodule
```

The `Call` sort intentionally lumps together several constructs that occur in MIR emitted by `compiletest-rs`:
* actual function calls
* panics
* [Drop](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/enum.TerminatorKind.html#variant.Drop)
* [FalseUnwind](See https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/enum.TerminatorKind.html#variant.FalseUnwind)
* TODO: what else?

These constructs need to be disambiguated at runtime. See the `MIR-AMBIGUITIES` module for the disambiguation pass.

```k
  syntax Call ::= Place "=" CallLike "->" TerminatorDestination
                | CallLike "->" TerminatorDestination
                // seems to be needed for panics
                | Place "=" CallLike [avoid]

  syntax Yield
  syntax GeneratorDrop
  syntax FalseEdge
  syntax InlineAsm

  // https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/terminator/struct.SwitchTargets.html
  syntax SwitchTargets ::= List{SwitchTarget, ","}
  syntax SwitchTarget ::= Int ":" BBIndex

  syntax CallLike ::= Callable "(" ArgumentList ")" | AssertCall

  syntax Callable ::= PathExpression
                    | "move" Local

  syntax AssertCall ::= "assert" "(" AssertArgumentList ")"
  syntax AssertArgument ::= Operand | "!" Operand | StringLiteral
  syntax AssertArgumentList ::= NeList{AssertArgument, ","}

  syntax ArgumentList ::= List{Operand, ","}

  syntax TerminatorDestination ::= BBIndex | SwitchIntCases | CallDestination | AssertDestination
  syntax SwitchIntCases ::= "[" IntCaseList "," OtherwiseCase "]"
  syntax IntCaseList ::= NeList{IntCase, ","}
  syntax IntCase ::= Int ":" BBIndex
  syntax OtherwiseCase ::= "otherwise" ":" BBIndex
  syntax CallDestination ::= "[" "return" ":" BBIndex "," "unwind" ":" BBIndex "]"
  syntax AssertDestination ::= "[" "success" ":" BBIndex "," "unwind" ":" BBIndex "]"

endmodule
```