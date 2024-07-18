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

syntax StaticDef ::= Int // imported from crate

syntax MaybeItemKind ::= someItemKind(ItemKind) [symbol(someItemKind)]
                       | "noItemKind" [symbol(noItemKind)]
syntax MaybeBody ::= someBody(Body) [symbol(someBody)]
                   | "noBody" [symbol(noBody)]
syntax MaybeAllocation ::= someAllocation(Allocation) | "noAllocation"
syntax MonoItem ::= monoItemFn(Instance)
                  | monoItemStatic(StaticDef)
                  | monoItemFn(name: Symbol, defId: DefId, instanceKind: InstanceKind, itemKind: MaybeItemKind, body: MaybeBody, promoted: Bodies) [symbol(monoItemFn)]
                  | monoItemStatic(name: Symbol, defId: DefId, allocation: MaybeAllocation)
                  | monoItemGlobalAsm(Opaque)
syntax MonoItemWrapper ::= monoItemWrapper(symbolName: Symbol, monoItemKind: MonoItem) [symbol(monoItemWrapper)]
syntax MonoItems ::= List {MonoItemWrapper, ""} [symbol(monoItems), terminator-symbol(.monoItems)]

syntax Instance ::= instance(kind: InstanceKind, def: InstanceDef)
syntax InstanceKind ::= "instanceKindItem" [symbol(instanceKindItem)]
                      | "instanceKindIntrinsic"
                      | instanceKindVirtual(idx: Int)
                      | "instanceKindShim"
syntax InstanceDef ::= instanceDef(Int)

syntax FunctionMapEntry ::= functionMapEntry(Int, Symbol) [symbol(functionMapEntry)]
syntax FunctionsMap ::= List {FunctionMapEntry, ""} [symbol(functionsMap), terminator-symbol(.functionsMap)]

endmodule
