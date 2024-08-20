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
syntax MaybeBinderForExistentialTraitRef ::= someBinderForExistentialTraitRef(BinderForExistentialTraitRef)
                                           | "noBinderForExistentialTraitRef"
syntax GlobalAlloc ::= globalAllocFunction(Instance)
                         [group(mir-enum)]
                     | globalAllocVTable(Ty, MaybeBinderForExistentialTraitRef)
                         [group(mir-enum)]
                     | Static(StaticDef)
                         [symbol(globalAllocStatic), group(mir-enum)]
                     | Memory(Allocation)
                         [symbol(globalAllocMemory), group(mir-enum)]

syntax GlobalAllocEntry ::= globalAllocEntry(MIRInt, GlobalAlloc)
         [symbol(globalAllocEntry), group(mir)]
syntax GlobalAllocsMap ::= List {GlobalAllocEntry, ""}
         [symbol(globalAllocsMap), terminator-symbol(.globalAllocsMap), group(mir-list)]

////////////////////////////// unused for parsing?

syntax AllocId ::= allocId(Int) [symbol(allocId)]

endmodule
