module ALLOC-SORTS

syntax AllocId
syntax GlobalAllocs

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
                     | globalAllocStatic(StaticDef)
                     | globalAllocMemory(Allocation) [symbol(globalAllocMemory)]
syntax GlobalAllocs ::= List {GlobalAlloc, ""} [symbol(globalAllocs), terminator-symbol(.globalAllocs)]
syntax AllocId ::= allocId(Int) [symbol(allocId)]

endmodule
