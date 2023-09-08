```k
require "mir-types.md"
require "mir-rvalue.md"
```


[Terminators](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/enum.TerminatorKind.html) occur at the end of a basic block and always transfer control outside the current block: either to a block within the same function or to a block outside of it.

```k
module MIR-TERMINATOR-SYNTAX
  import MIR-TYPE-SYNTAX
  import MIR-RVALUE-SYNTAX

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


  syntax Goto ::= "goto" "->" BB
  syntax SwitchInt ::= "switchInt" "(" Operand ")" "->" "[" SwitchTargets "," "otherwise" ":" BB "]"
  syntax Resume ::= "resume"
  syntax Abort ::= "abort"
  syntax Return ::= "return"
  syntax Unreachable ::= "unreachable"
  
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
  syntax SwitchTarget ::= Int ":" BB

  syntax CallLike ::= Callable "(" ArgumentList ")" | AssertCall

  syntax Callable ::= PathExpression
                    | "move" Local

  syntax AssertCall ::= "assert" "(" AssertArgumentList ")"
  syntax AssertArgument ::= Operand | "!" Operand | StringLiteral
  syntax AssertArgumentList ::= NeList{AssertArgument, ","}

  syntax ArgumentList ::= List{Operand, ","}

  syntax TerminatorDestination ::= BB | SwitchIntCases | CallDestination | AssertDestination
  syntax SwitchIntCases ::= "[" IntCaseList "," OtherwiseCase "]"
  syntax IntCaseList ::= NeList{IntCase, ","}
  syntax IntCase ::= Int ":" BB
  syntax OtherwiseCase ::= "otherwise" ":" BB
  syntax CallDestination ::= "[" "return" ":" BB "," "unwind" ":" BB "]"
  syntax AssertDestination ::= "[" "success" ":" BB "," "unwind" ":" BB "]"
endmodule
```