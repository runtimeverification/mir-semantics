requires "ty.k"
requires "mono.k"

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
         [symbol(globalAllocsMap), terminator-symbol(.globalAllocsMap), group(mir-list)]

////////////////////////////// unused for parsing?

syntax AllocId ::= allocId(Int) [symbol(allocId)]

endmodule
