```k
require "mir-types.md"
require "mir-place-syntax.md"
require "mir-rvalue.md"
```

MIR syntax
----------
This module is designed to parse the exported MIR of a rust program from `rustc` into `KItem`s accepted by K framework. It is a decompilation process from [string format MIR to strcutured MIR in K.

```k
module MIR-SYNTAX
  imports UNSIGNED-INT-SYNTAX
  imports MIR-TYPE-SYNTAX
  imports MIR-PLACE-SYNTAX
  imports MIR-RVALUE-SYNTAX
```

```k
  syntax Mir ::= List{CrateItem, ""}
  syntax CrateItem ::= Function
                        | FunctionForData
                        | FunctionForPromoted
                        | DataAlloc
                        | FunctionAlloc
```

```k
  syntax Function ::= FnSig "{" FunctionBody "}"
  syntax FnSig ::= "fn" FunctionPath "(" ParameterList ")" "->" Type
  syntax Parameter ::= Local ":" Type
  syntax ParameterList ::= List{Parameter, ","}
```

The `FunctionBody` sort represents a single MIR function. Based on [`rustc::mir::Body`](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/struct.Body.html).

```k
  syntax FunctionBody ::= DebugList LocalDecls ScopeList BasicBlocks
  syntax Binding ::= "let" MutPrefix Local ":" Type
  // Temporaries and the return place are always mutable.
  // a binding declared by the user, a temporary inserted by the compiler, a function argument, or the return place
  // a binding declared by the user, a function argument will be recorded as a localdecl, the others will be a map from place to value
  syntax LocalDecls ::= List{Binding, ";"}

  syntax Scope ::= "scope" Int "{" DebugList BindingList ScopeList "}"
  syntax ScopeList ::= List{Scope, ""}

  syntax Debug ::= "debug" UserVar "=>" Place ";"
  syntax DebugList ::= List{Debug, ""}

  syntax BasicBlock ::= BBIndex ":" BasicBlockData
  syntax BBIndex ::= "bb" Int
  syntax BasicBlockData ::= "{" Statements Terminator ";" "}"
  syntax BasicBlocks ::= List {BasicBlock, ""} //IndexVec
```

The `FunctionForData` and `FunctionForPromoted` sorts are currently unfinished.

```k
  syntax FunctionForData ::= FunctionForDataSignature "{" FunctionBody "}"
  syntax FunctionForDataSignature ::= MaybeStaticConstMut PathFunctionData ":" Type "="
  syntax MaybeStaticConstMut ::= "" | "static" | "const" | "static" "mut"
  // MIR-only, most likely, inspired from PathExpression, FunctionPath and similar.
  syntax PathFunctionData ::= NeList{FunctionPathComponent, "::"}
```

```k
  syntax FunctionForPromoted ::= FunctionForPromotedSignature "{" FunctionBody "}"
  syntax FunctionForPromotedSignature ::= "promoted" "[" Int "]" "in" FunctionPath ":" Type "="
```

### [Statements](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/enum.StatementKind.html) and [Terminators](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/enum.TerminatorKind.html)

[Statements](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/enum.StatementKind.html) occur within a basic block. They are executed in sequence and never transfer control anywhere outside their basic block.

```k
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
  syntax Statement ::= StatementKind
  syntax Statements ::= List {Statement, ";"}
```

[Terminators](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/enum.TerminatorKind.html) occur at the end of a basic block and always transfer control outside the current block: either to a block within the same function or to a block outside of it.

```k
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


  syntax Goto ::= "goto" "->" BBIndex
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
```

```k
endmodule
```

```k
module MIR-PARSER-SYNTAX
  imports MIR-SYNTAX

  // Declaring regular expressions of sort `#Layout` infroms the K lexer to drop these tokens.
  syntax #Layout  ::= r"(\\/\\/[^\\n\\r]*)" // single-line comments
                    | r"([\\ \\n\\r\\t])"   // whitespace

endmodule
```
