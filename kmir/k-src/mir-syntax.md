```k
require "mir-types.md"
require "mir-place-syntax.md"
require "mir-rvalue.md"
```

Mir syntax
----------

These modules defined the syntax of Mir programs. See "mir-types.md" for the syntax of types.

```k
module MIR-SYNTAX
  imports UNSIGNED-INT-SYNTAX
  imports MIR-TYPE-SYNTAX
  imports MIR-PLACE-SYNTAX
  imports MIR-RVALUE-SYNTAX
```

```k
  syntax Mir ::= List{MirComponent, ""}
  syntax MirComponent ::= Function
                        | FunctionForData
                        | FunctionForPromoted
                        | DataAlloc
                        | FunctionAlloc
```

```k
  syntax Function ::= FunctionSignature "{" FunctionBody "}"
  syntax FunctionSignature ::= "fn" FunctionPath "(" ParameterList ")" "->" Type
  syntax Parameter ::= Local ":" Type
  syntax ParameterList ::= List{Parameter, ","}
```

The `FunctionBody` sort represents a single Mir function. Based on [`rustc::mir::Body`](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/struct.Body.html).

```k
  syntax FunctionBody ::= DebugList BindingList ScopeList BasicBlockList
  syntax Binding ::= "let" OptMut Local ":" Type ";"
  syntax BindingList ::= List{Binding, ""}
  syntax OptMut ::= "mut" | ""

  syntax Scope ::= "scope" Int "{" DebugList BindingList ScopeList "}"
  syntax ScopeList ::= List{Scope, ""}

  syntax Debug ::= "debug" UserVariableName "=>" Place ";"
  syntax DebugList ::= List{Debug, ""}

  syntax BasicBlock ::= BB ":" BasicBlockBody
  syntax BasicBlockBody ::= "{" StatementList Terminator ";" "}"
  syntax BasicBlockList ::= List {BasicBlock, ""}
```

The `FunctionForData` and `FunctionForPromoted` sorts are currently unfinished.

```k
  syntax FunctionForData ::= FunctionForDataSignature "{" FunctionBody "}"
  syntax FunctionForDataSignature ::= MaybeStaticConstMut PathFunctionData ":" Type "="
  syntax MaybeStaticConstMut ::= "" | "static" | "const" | "static" "mut"
  // Mir-only, most likely, inspired from PathExpression, FunctionPath and similar.
  syntax PathFunctionData ::= NeList{FunctionPathComponent, "::"}
```

```k
  syntax FunctionForPromoted ::= FunctionForPromotedSignature "{" FunctionBody "}"
  syntax FunctionForPromotedSignature ::= "promoted" "[" Int "]" "in" FunctionPath ":" Type "="
```

### [Statements](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/enum.StatementKind.html) and [Terminators](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/enum.TerminatorKind.html)

[Statements](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/enum.StatementKind.html) occur within a basic block. They are executed in sequence and never transfer control anywhere outside their basic block.

```k
  syntax Statement  ::= Assign
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
  syntax TerminatedStatement ::= Statement ";"
  syntax StatementList ::= List {TerminatedStatement, ""}
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


  syntax Goto ::= "goto" "->" BB
  syntax SwitchInt ::= "switchInt" "(" Operand ")" "->" "[" SwitchTargets "," "otherwise" ":" BB "]"
  syntax Resume ::= "resume"
  syntax Abort ::= "abort"
  syntax Return ::= "return"
  syntax Unreachable ::= "unreachable"
```

The `Call` sort intentionally lumps together several constructs that occur in Mir emitted by `compiletest-rs`:
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

Mir syntax disambiguation
-------------------------

Some of Mir constructs are ambiguous as parsing time. The `MIR-AMBIGUITIES` module contains rewrite rules that disambiguate these constructs.
These rules are applied at `Initialization` phase, see the `MIR` module in "mir.md" for more information on when these rules are used.

```k
module MIR-AMBIGUITIES
  imports MIR-SYNTAX
  imports MIR-LEXER-SYNTAX
  imports MIR-BUILTINS-SYNTAX
  imports K-AMBIGUITIES
```

```k
  syntax BasicBlockBody ::= disambiguateBasicBlockBody(BasicBlockBody) [function]
  //-----------------------------------------------------------------------------
  rule disambiguateBasicBlockBody({ STATEMENTS:StatementList TERMINATOR:Terminator ; }:BasicBlockBody) =>
       ({ disambiguateStatementList(STATEMENTS) disambiguateTerminator(TERMINATOR) ; })

  syntax StatementList ::= disambiguateStatementList(StatementList) [function]
  //--------------------------------------------------------------------------
  rule disambiguateStatementList(.StatementList) => .StatementList
  rule disambiguateStatementList(X ; XS) => disambiguateStatement(X) ; disambiguateStatementList(XS)

  syntax Statement ::= disambiguateStatement(Statement) [function]
  //--------------------------------------------------------------
  rule disambiguateStatement((PLACE:Place = VALUE:RValue):Assign) => (PLACE:Place = disambiguateRValue(VALUE:RValue)):Assign
  rule disambiguateStatement(S) => S [owise]

  syntax Terminator ::= disambiguateTerminator(Terminator) [function]
  //-----------------------------------------------------------------
  rule disambiguateTerminator(T) => T
```

The actual disambiguation starts here: we need to distinguish certain rvalues:
* enum constructors
* primitive unary and binary operations

```k
  syntax RValue ::= disambiguateRValue(RValue) [function]
  //-----------------------------------------------------
  rule disambiguateRValue(
        amb((NAME:IdentifierToken (AGR_1:Operand, ARG_2:Operand, .OperandList))::EnumConstructor,
            (NAME:IdentifierToken (AGR_1:Operand, ARG_2:Operand))::BinaryOp
          )) =>
         (NAME::IdentifierToken (AGR_1:Operand, ARG_2:Operand))::BinaryOp
    requires isBinOp(IdentifierToken2String(NAME))
  rule disambiguateRValue(
        amb((NAME:IdentifierToken (AGR_1:Operand, .OperandList))::EnumConstructor,
            (NAME:IdentifierToken (AGR_1:Operand))::UnaryOp
          )) =>
         (NAME::IdentifierToken (AGR_1:Operand))::UnaryOp
    requires isUnOp(IdentifierToken2String(NAME))
  rule disambiguateRValue(X) => X [owise]
```

```k
endmodule
```
