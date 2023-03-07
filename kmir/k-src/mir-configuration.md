```k
require "mir-syntax.k"
require "mir-types.md"
require "rust-std.md"
```

Mir interpreter configuration
=============================

These modules declares the necessary domain sorts to represent the Mir locals at runtime. The sort declarations are derived from the `rustc` types and are accompanied by permalinks to the respective `rustc` source code locations.

```k
module MIR-CONFIGURATION
  imports MIR-SYNTAX
  imports MIR-LOCALS
  imports MIR-BASIC-BLOCKS

  configuration
    <mir>
      <localDecls/>
      <basicBlocks/>
    </mir>
endmodule
```

Locals
------

```k
module MIR-LOCALS
    imports INT
    imports BOOL
    imports MIR-SYNTAX
```

We declare a runtime configuration to represent the [`LocalDecls`](https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/mod.rs#L72) array and it's item type [`LocalDecl`](https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/mod.rs#L756).

We represent `LocalDecls` as a cell `Map` of multiplicity `"*"`. The fields of `LocalDecl` come directly from the Rust `struct` declaration. We declare custom sorts to represent the filed values as necessary.

```k
  configuration
    <localDecls>
        <localDecl multiplicity="*" type="Map">
            <index> 0:Int </index>
            <mutability>  Not:Mutability </mutability>
            <internal>    false          </internal>
            <ty>          ():Type          </ty>
// It looks like we don't actually care about these fileds:
//            <localInfo>   None:LocalInfo </localInfo>
//            <userTy>      ():Type          </userTy>    // we probably don't need userTy because we won't do typeckecing
//            <isBlockTail> false          </isBlockTail>
//            <sourceInfo>  false          </sourceInfo>
        </localDecl>
    </localDecls>
```

### [Mutability](https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_ast/src/ast.rs#L781)

```k
  syntax Mutability ::= "Not"
                      | "Mut"
```

### [Local kind](https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/mod.rs#LL663C16-L663C20)

```k
  syntax LocalKind ::= "Var"           // User-declared variable binding.
                     | "Temp"          // Compiler-introduced temporary.
                     | "Arg"           // Function argument.
                     | "ReturnPointer" // Location of function's return value.
```

### [LocalInfo](https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/mod.rs#LL887-L905C2)

```k
  syntax DefId ::= Int // TODO: what's that? https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/src/tools/rust-analyzer/crates/hir-ty/src/interner.rs#L63

  syntax LocalInfo ::= "User"                 // User(ClearCrossCrate<BindingForm<'tcx>>)
                     | "StaticRef" DefId Bool // StaticRef { def_id: DefId, is_thread_local: bool }
                     | "ConstRef"  DefId      // ConstRef { def_id: DefId }
                     | "AggregateTemp"
                     | "DerefTemp"
                     | "FakeBorrow"
```

```k
endmodule
```

Basic blocks
------------

```k
module MIR-BASIC-BLOCKS
  imports MIR-SYNTAX
  imports MIR-TYPES
```

```k
  configuration
    <basicBlocks multiplicity="*" type="Map">
        <bbName> "bb0":String </bbName>
        <bbBody> BBBottom:BasicBlockBody </bbBody>
    </basicBlocks>

  syntax BasicBlockBody ::= "BBBottom" [macro]
  // -----------------------------------------
  rule BBBottom => assert(String2SringLiteral("dummy"))
```

```k
endmodule
```


Functions
---------

```k
```

