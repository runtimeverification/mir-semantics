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
