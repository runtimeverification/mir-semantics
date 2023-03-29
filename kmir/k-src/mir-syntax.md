(very) loosely based on https://rust-lang.github.io/rfcs/1211-mir.html

```k
require "mir-type-syntax.md"
require "mir-place-syntax.md"
require "mir-rvalue-syntax.md"

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

### Statements and Terminators

Statements occur within a basic block. They are executed in sequence and never transfer control anywhere outside their basic block.

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

Terminators occur at the end of a basic block and always transfer control outside the current block: either to a block within the same function or to a block outside of it.

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

```k
module MIR-AMBIGUITIES
  imports MIR-SYNTAX
  imports MIR-LEXER-SYNTAX
  imports MIR-BUILTINS-SYNTAX
  imports K-AMBIGUITIES

//  syntax Bool ::= isNullaryOpName(Identifier) [function, total]
//  //---------------------------------------------------------------------
//  rule isNullaryOpName(OP_NAME)  => true
//    requires IdentifierToken2String(OP_NAME) ==String "SizeOf"
//      orBool IdentifierToken2String(OP_NAME) ==String "AlignOf"
//  rule isNullaryOpName(_)       => false [owise]

//  syntax Bool ::= isUnaryOpName(Identifier) [function, total]
//  //-------------------------------------------------------------------
//  rule isUnaryOpName(OP_NAME)  => true
//    requires IdentifierToken2String(OP_NAME) ==String "Not"
//      orBool IdentifierToken2String(OP_NAME) ==String "Neg"
//  rule isUnaryOpName(_)       => false [owise]

//  syntax Bool ::= isBinaryOp(RValue) [function, total]
//  //--------------------------------------------------
//  rule isBinaryOp(NAME(LHS:Operand, RHS:Operand)) => isBinaryOpName(NAME)
//  rule isBinaryOp(_)                              => false [owise]

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

  syntax RValue ::= disambiguateRValue(RValue) [function]
  //-----------------------------------------------------
  rule disambiguateRValue(
        amb((NAME:IdentifierToken (AGR_1:Operand, ARG_2:Operand, .OperandList))::EnumConstructor,
            (NAME:IdentifierToken (AGR_1:Operand, ARG_2:Operand))::BinaryOp
          )) =>
         (NAME::IdentifierToken (AGR_1:Operand, ARG_2:Operand))::BinaryOp
    requires isBinOp(IdentifierToken2String(NAME))
  rule disambiguateRValue(X) => X [owise]

endmodule
```
