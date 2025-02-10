```k
requires "ty.md"
requires "mono.md"

module ALLOC-SORTS

syntax AllocId
syntax GlobalAllocsMap

endmodule

module ALLOC
  imports ALLOC-SORTS
  imports MONO-SORTS
  imports TYPES-SORTS
  imports INT

syntax BinderForExistentialTraitRef ::= binderForExistentialTraitRef(value: ExistentialTraitRef, boundVars: BoundVariableKindList)
                                          [group(mir---value--bound-vars)]

syntax MaybeBinderForExistentialTraitRef ::= someBinderForExistentialTraitRef(BinderForExistentialTraitRef) [group(mir-option)]
                                           | "noBinderForExistentialTraitRef"                               [group(mir-option)]

syntax GlobalAllocKind ::= globalAllocFunction(Instance)
                             [group(mir-enum), symbol(GlobalAllocKind::Function)]
                         | globalAllocVTable(Ty, MaybeBinderForExistentialTraitRef)
                             [group(mir-enum), symbol(GlobalAllocKind::VTable)]
                         | Static(StaticDef)
                             [group(mir-enum), symbol(GlobalAllocKind::Static)]
                         | Memory(Allocation)
                             [group(mir-enum), symbol(GlobalAllocKind::Memory)]

syntax GlobalAlloc ::= globalAllocEntry(MIRInt, GlobalAllocKind)
         [symbol(globalAllocEntry), group(mir)]

syntax GlobalAllocs ::= List {GlobalAlloc, ""}
         [symbol(GlobalAllocs::append), terminator-symbol(GlobalAllocs::empty), group(mir-list)]

syntax AllocId ::= allocId(Int) [group(mir-int), symbol(allocId)]

endmodule
```

### Index

#### Internal MIR
- [AllocId](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_middle/src/mir/interpret/mod.rs#L104-L105)
- [GlobalAlloc](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_middle/src/mir/interpret/mod.rs#L270-L288)

#### SMIR (Bridge)
- [AllocId](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L701-L706)
- [GlobalAlloc](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L708-L725)

#### Stable MIR
- [AllocId](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/alloc.rs#L45-L47)
- [GlobalAlloc](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/alloc.rs#L11-L25)
