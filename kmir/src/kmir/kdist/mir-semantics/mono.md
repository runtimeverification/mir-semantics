```k
requires "body.md"
requires "lib.md"
requires "ty.md"

module MONO-SORTS

syntax Instance
syntax StaticDef

endmodule

module MONO
  imports BODY-SORTS
  imports LIB-SORTS
  imports MONO-SORTS
  imports TYPES-SORTS
  imports INT

syntax StaticDef ::= staticDef(Int) [group(mir-int)] // imported from crate

syntax MaybeAllocation ::= someAllocation(Allocation) [group(mir-option)]
                         | "noAllocation"             [group(mir-option)]

syntax MonoItemKind ::= monoItemFn(name: Symbol, id: DefId, body: Body)
                          [ group(mir-enum---name--id--body)
                          , symbol(MonoItemKind::MonoItemFn)
                          ]
                      | monoItemStatic(name: Symbol, id: DefId, allocation: MaybeAllocation)
                          [ group(mir-enum---name--id--allocation)
                          , symbol(MonoItemKind::MonoItemStatic)
                          ]
                      | monoItemGlobalAsm(Opaque)
                          [ group(mir-enum)
                          , symbol(MonoItemKind::MonoItemGlobalAsm)
                          ]
syntax MonoItem ::= monoItem(symbolName: Symbol, monoItemKind: MonoItemKind)
                      [symbol(monoItemWrapper), group(mir---symbol-name--mono-item-kind)]
syntax MonoItems ::= List {MonoItem, ""}
                      [symbol(MonoItems::append), terminator-symbol(MonoItems::empty), group(mir-list)]

////////////////////////////////////////// unused for parsing?

syntax Instance ::= instance(kind: InstanceKind, def: InstanceDef)
syntax InstanceKind ::= "instanceKindItem" [symbol(instanceKindItem)]
                      | "instanceKindIntrinsic"
                      | instanceKindVirtual(idx: Int)
                      | "instanceKindShim"
syntax InstanceDef ::= instanceDef(Int)

endmodule
```

### Index

#### Internal MIR
- StaticDef - not present, comes from [DefId](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_span/src/def_id.rs#L216-L235)
- [MonoItem](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/mono.rs#L48-L53)
- [Instance](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/instance.rs#L22-L35)
- [InstanceKind -> InstanceDef](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/instance.rs#L59-L180)
- InstanceDef (stable_mir) - not present ?

#### SMIR (Bridge)
- [fn static_def](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_internal/mod.rs#L167-L169)
- [MonoItem](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L771-L782)
- [Instance](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L836-L863)
- [InstanceKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L841-L860)
- InstanceDef - not present

#### Stable MIR
- [StaticDef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/mono.rs#L254-L256) [crate_def](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/stable_mir/src/crate_def.rs#L55-L69)
- [MonoItem](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/mono.rs#L10-L15)
- [Instance](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/mono.rs#L17-L24)
- [InstanceKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/mono.rs#L26-L37)
- [InstanceDef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/mono.rs#L244-L245)
