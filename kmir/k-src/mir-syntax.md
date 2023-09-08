```k
require "mir-types.md"
require "mir-place-syntax.md"
require "mir-rvalue.md"
require "mir-terminator.md"
```

MIR syntax
----------

These modules defined the syntax of MIR programs. See "mir-types.md" for the syntax of types.

```k
module MIR-SYNTAX
  imports UNSIGNED-INT-SYNTAX
  imports MIR-TYPE-SYNTAX
  imports MIR-PLACE-SYNTAX
  imports MIR-RVALUE-SYNTAX
  imports MIR-TERMINATOR-SYNTAX
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

The `FunctionBody` sort represents a single MIR function. Based on [`rustc::mir::Body`](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/struct.Body.html).

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
  syntax BasicBlockBody ::= "{" Statements Terminator ";" "}"
  syntax BasicBlockList ::= List {BasicBlock, ""}
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
  syntax Statement ::= StatementKind ";"
  syntax Statements ::= List {Statement, ""}
```


```k
endmodule
```