module MONO-SORTS

syntax Instance
syntax StaticDef

endmodule

module MONO
  imports LIB-SORTS
  imports MONO-SORTS
  imports INT

syntax StaticDef ::= Int // imported from crate

syntax MonoItem ::= monoItemFn(Instance)
                  | monoItemStatic(StaticDef)
                  | monoItemGlobalAsm(Opaque)

syntax Instance ::= instance(kind: InstanceKind, def: InstanceDef)
syntax InstanceKind ::= "instanceKindItem"
                      | "instanceKindIntrinsic"
                      | instanceKindVirtual(idx: Int)
                      | "instanceKindShim"
syntax InstanceDef ::= inatanceDef(Int)

endmodule
