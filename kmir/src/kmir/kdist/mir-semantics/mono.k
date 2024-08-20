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

syntax MaybeAllocation ::= someAllocation(Allocation) | "noAllocation"
syntax MonoItem ::= monoItemFn(Instance) // do not use - parser uses the key to generate the other production
                  | monoItemStatic(StaticDef) // do not use - parser uses the key to generate the other production
                  | monoItemFn(name: Symbol, id: DefId, body: Bodies)
                      [symbol(MonoItemFn), group(mir-enum)]
                  | monoItemStatic(name: Symbol, id: DefId, allocation: MaybeAllocation)
                      [group(mir-enum)]
                  | monoItemGlobalAsm(Opaque)
                      [group(mir-enum)]
syntax MonoItemWrapper ::= monoItemWrapper(symbolName: Symbol, monoItemKind: MonoItem)
         [symbol(monoItemWrapper), group(mir)]
syntax MonoItems ::= List {MonoItemWrapper, ""}
         [symbol(monoItems), terminator-symbol(.monoItems), group(mir-list)]

////////////////////////////////////////// unused for parsing?

syntax Instance ::= instance(kind: InstanceKind, def: InstanceDef)
syntax InstanceKind ::= "instanceKindItem" [symbol(instanceKindItem)]
                      | "instanceKindIntrinsic"
                      | instanceKindVirtual(idx: Int)
                      | "instanceKindShim"
syntax InstanceDef ::= instanceDef(Int)

endmodule
