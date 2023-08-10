```k
require "mir-types.md"
require "mir-place.md"
require "mir-basicblock.md"
```

MIR syntax
----------
This module is designed to parse the exported MIR of a rust program from `rustc` into `KItem`s accepted by K framework. It is a decompilation process from [string format MIR to strcutured MIR in K.

```k
module MIR-SYNTAX
  imports UNSIGNED-INT-SYNTAX
  imports MIR-TYPE-SYNTAX
  imports MIR-PLACE
  imports MIR-BASICBLOCK-SYNTAX
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
