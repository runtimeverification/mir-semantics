module ALLOC-SORTS

syntax AllocId

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
                     | globalAllocMemory(Allocation)
syntax AllocId ::= allocId(Int) [symbol(allocId)]

endmodule
