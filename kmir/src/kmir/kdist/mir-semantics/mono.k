requires "body.k"
requires "lib.k"
requires "ty.k"

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

syntax MonoItemKind ::= monoItemFn(name: Symbol, id: DefId, body: Bodies)
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
                      [symbol(monoItems), terminator-symbol(.monoItems), group(mir-list)]

////////////////////////////////////////// unused for parsing?

syntax Instance ::= instance(kind: InstanceKind, def: InstanceDef)
syntax InstanceKind ::= "instanceKindItem" [symbol(instanceKindItem)]
                      | "instanceKindIntrinsic"
                      | instanceKindVirtual(idx: Int)
                      | "instanceKindShim"
syntax InstanceDef ::= instanceDef(Int)

endmodule
