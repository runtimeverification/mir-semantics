```k
requires "body.md"
requires "ty.md"

module LIB-SORTS

syntax CrateItem
syntax ItemKind
syntax Opaque
syntax Symbol

endmodule

module LIB
  imports BODY-SORTS
  imports LIB-SORTS
  imports TYPES-SORTS
  imports STRING
```

#### Internal MIR
- [Symbol](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_span/src/symbol.rs#L2233-L2243)
- Opaque - not present
- [Loc.file](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_span/src/lib.rs#L2383) - [SourceFile.name](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_span/src/lib.rs#L1583)
- [fn trait_def](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_hir_analysis/src/collect.rs#L1101-L1135)
- [fn impl_trait_def](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/context.rs#L2746-L2758)
- CrateItem - not present, comes from [DefId](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_span/src/def_id.rs#L216-L235)
- [CrateNum](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_span/src/def_id.rs#L17-L21)
- Crate - not entirely sure, there is `Crate` in hir, but I am not certain it is the same as what the `CrateNum` is referring to just yet. Needs a better look
- [DefKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_hir/src/def.rs#L49-L134)
- [CtorKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_hir/src/def.rs#L26-L33)

#### SMIR (Bridge)
- [Symbol](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mod.rs#L73-L79)
- Opaque - not present
- [Filename](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/context.rs#L279-L288)
- [fn trait_decls](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/context.rs#L112-L119)
- [fn trait_impls](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/context.rs#L138-L145)
- [fn crate_item](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_internal/mod.rs#L80-L82)
- [fn smir_crate](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/mod.rs#L91C29-L91C45)
- [Crate](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/mod.rs#L86-L92)
- [ItemKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/mod.rs#L94-L127)
- [CtorKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/mod.rs#L124-L125)

#### Stable MIR
- [Symbol](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/lib.rs#L44)
- [Opaque](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/lib.rs#L215-L217)
- [Filename](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/lib.rs#L116)
- [TraitDecls](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/lib.rs#L72)
- [ImplTraitDecls](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/lib.rs#L75)
- [CrateItem](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/lib.rs#L121) [crate_def_with_ty](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/crate_def.rs#L126-L142)
- [CrateNum](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/lib.rs#L47)
- [Crate](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/lib.rs#L77-L83)
- [ItemKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/lib.rs#L102-L108)
- [CtorKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/lib.rs#L110-L114)

```k
syntax Symbol ::= symbol(String) [group(mir-string)]
syntax Opaque ::= opaque(String) [symbol(opaque)]
syntax Filename ::= filename(String)

syntax TraitDecls ::= List {TraitDef, ""}
syntax ImplTraitDecls ::= List {ImplDef, ""}

syntax CrateItem ::= crateItem(Int) // imported from crate
syntax CrateNum ::= crateNum(Int)
syntax Crate ::= crate(id: CrateNum, name: Symbol, isLocal: MIRBool)

syntax ItemKind ::= "itemKindFn" [symbol(itemKindFn)]
                  | "itemKindStatic" [symbol(itemKindStatic)]
                  | "itemKindConst" [symbol(itemKindConst)]
                  | itemKindCtor(CtorKind)
syntax CtorKind ::= "ctorKindConst"
                  | "ctorKindFn"

endmodule
```
