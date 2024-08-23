```k
module ALLOC-SORTS

syntax AllocId
syntax GlobalAllocsMap

endmodule

module ALLOC
  imports ALLOC-SORTS
  imports MONO-SORTS
  imports TYPES-SORTS
  imports INT
```

#### Internal MIR
- [AllocId](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_middle/src/mir/interpret/mod.rs#L104-L105)
- [GlobalAlloc](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_middle/src/mir/interpret/mod.rs#L270-L288)

#### SMIR (Bridge)
- [AllocId](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L701-L706)
- [GlobalAlloc](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L708-L725)

#### Stable MIR
- [AllocId](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/alloc.rs#L45-L47)
- [GlobalAlloc](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/alloc.rs#L11-L25)

```k
syntax BinderForExistentialTraitRef ::= binderForExistentialTraitRef(value: ExistentialTraitRef, boundVars: BoundVariableKindList)
syntax MaybeBinderForExistentialTraitRef ::= someBinderForExistentialTraitRef(BinderForExistentialTraitRef)
                                           | "noBinderForExistentialTraitRef"
syntax GlobalAlloc ::= globalAllocFunction(Instance)
                     | globalAllocVTable(Ty, MaybeBinderForExistentialTraitRef)
                     | globalAllocStatic(StaticDef) [symbol(globalAllocStatic)]
                     | globalAllocMemory(Allocation) [symbol(globalAllocMemory)]

syntax GlobalAllocEntry ::= globalAllocEntry(MIRInt, GlobalAlloc) [symbol(globalAllocEntry)]
syntax GlobalAllocsMap ::= List {GlobalAllocEntry, ""} [symbol(globalAllocsMap), terminator-symbol(.globalAllocsMap)]
syntax AllocId ::= allocId(Int) [symbol(allocId)]

endmodule
```