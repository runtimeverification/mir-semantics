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

syntax MaybeItemKind ::= someItemKind(ItemKind) | "noItemKind"
syntax MaybeBody ::= someBody(Body) | "noBody"
syntax MaybeAllocation ::= someAllocation(Allocation) | "noAllocation"
syntax MonoItem ::= monoItemFn(Instance)
                  | monoItemStatic(StaticDef)
                  | monoItemFn(name: Symbol, defId: DefId, instanceKind: InstanceKind, itemKind: MaybeItemKind, body: MaybeBody, promoted: Bodies)
                  | monoItemStatic(name: Symbol, defId: DefId, allocation: MaybeAllocation)
                  | monoItemGlobalAsm(Opaque)
syntax MonoItemWrapper ::= monoItemWrapper(symbolName: Symbol, monoItemKind: MonoItem)
syntax MonoItems ::= List {MonoItemWrapper, ""} [symbol(monoItems), terminator-symbol(.monoItems)]

syntax Instance ::= instance(kind: InstanceKind, def: InstanceDef)
syntax InstanceKind ::= "instanceKindItem"
                      | "instanceKindIntrinsic"
                      | instanceKindVirtual(idx: Int)
                      | "instanceKindShim"
syntax InstanceDef ::= instanceDef(Int)

endmodule
