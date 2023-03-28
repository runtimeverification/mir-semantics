(very) loosely based on https://rust-lang.github.io/rfcs/1211-mir.html

```k
require "mir-type-syntax.md"
require "mir-place-syntax.md"
require "mir-rvalue-syntax.md"

module MIR-SYNTAX
  imports BOOL
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

### Statements and Terminators

```k
  // https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/syntax.rs#L242
  // https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/mod.rs#L1432
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

  // https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/syntax.rs#L532
  // https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/terminator.rs#L300
  syntax Terminator ::= "return"
                      | "unreachable"
                      | "resume"
                      | "goto" "->" BB
//                      // TODO: Can this happen for things other than panics?
                      | Place "=" CallLike
                      | Place "=" CallLike "->" TerminatorDestination
                      | CallLike
                      // I only found examples of this for assert and switchInt
                      | CallLike "->" TerminatorDestination

  // https://doc.rust-lang.org/reference/expressions/call-expr.html
  syntax CallLike ::= Callable "(" ArgumentList ")" | AssertCall
  syntax Callable ::= PathExpression
                   | "move" Local
  syntax AssertCall ::= "assert" "(" AssertArgumentList ")"
  syntax AssertArgument ::= Operand | "!" Operand | StringLiteral
  syntax AssertArgumentList ::= NeList{AssertArgument, ","}

  syntax ArgumentList ::= List{Operand, ","}
```

```k
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
  imports K-AMBIGUITIES

  syntax String ::= IdentifierToken2String(IdentifierToken) [function, hook(STRING.token2string)]

  syntax Bool ::= isNullaryOpName(Identifier) [function, total]
  //---------------------------------------------------------------------
  rule isNullaryOpName(OP_NAME)  => true
    requires IdentifierToken2String(OP_NAME) ==String "SizeOf"
      orBool IdentifierToken2String(OP_NAME) ==String "AlignOf"
  rule isNullaryOpName(_)       => false [owise]

  syntax Bool ::= isUnaryOpName(Identifier) [function, total]
  //-------------------------------------------------------------------
  rule isUnaryOpName(OP_NAME)  => true
    requires IdentifierToken2String(OP_NAME) ==String "Not"
      orBool IdentifierToken2String(OP_NAME) ==String "Neg"
  rule isUnaryOpName(_)       => false [owise]

//  syntax Bool ::= isBinaryOp(RValue) [function, total]
//  //--------------------------------------------------
//  rule isBinaryOp(NAME(LHS:Operand, RHS:Operand)) => isBinaryOpName(NAME)
//  rule isBinaryOp(_)                              => false [owise]

  syntax Bool ::= isBinaryOpName(Identifier) [function, total]
  //--------------------------------------------------------------------
  rule isBinaryOpName(OP_NAME)  => true
    requires IdentifierToken2String(OP_NAME) ==String "Add"
      orBool IdentifierToken2String(OP_NAME) ==String "Sub"
      orBool IdentifierToken2String(OP_NAME) ==String "Mul"
      orBool IdentifierToken2String(OP_NAME) ==String "Div"
      orBool IdentifierToken2String(OP_NAME) ==String "Rem"
      orBool IdentifierToken2String(OP_NAME) ==String "BitXor"
      orBool IdentifierToken2String(OP_NAME) ==String "BitAnd"
      orBool IdentifierToken2String(OP_NAME) ==String "BitOr"
      orBool IdentifierToken2String(OP_NAME) ==String "Shl"
      orBool IdentifierToken2String(OP_NAME) ==String "Shr"
      orBool IdentifierToken2String(OP_NAME) ==String "Eq"
      orBool IdentifierToken2String(OP_NAME) ==String "Lt"
      orBool IdentifierToken2String(OP_NAME) ==String "Le"
      orBool IdentifierToken2String(OP_NAME) ==String "Ne"
      orBool IdentifierToken2String(OP_NAME) ==String "Ge"
      orBool IdentifierToken2String(OP_NAME) ==String "Gt"
      orBool IdentifierToken2String(OP_NAME) ==String "Offset"
  rule isBinaryOpName(_)       => false [owise]

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
        amb((NAME:Identifier (AGR_1:Operand, ARG_2:Operand, .OperandList))::EnumConstructor,
            (NAME:Identifier (AGR_1:Operand, ARG_2:Operand))::BinaryOp
          )) =>
         (NAME::Identifier (AGR_1:Operand, ARG_2:Operand))::BinaryOp
    requires isBinaryOpName(NAME)
  rule disambiguateRValue(X) => X [owise]

endmodule
```
