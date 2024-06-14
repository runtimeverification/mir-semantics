module LIB-SORTS

syntax CrateItem
syntax Opaque
syntax Symbol

endmodule

module LIB
  imports LIB-SORTS
  imports TYPES-SORTS
  imports STRING

syntax Symbol ::= String
syntax Opaque ::= opaque(String)
syntax Filename ::= String

syntax TraitDecls ::= List {TraitDef, ""}
syntax ImplTraitDecls ::= List {ImplDef, ""}

syntax CrateItem ::= Int // imported from crate
syntax CrateItems ::= List {CrateItem, ""}
syntax CrateNum ::= crateNum(Int)
syntax Crate ::= crate(id: CrateNum, name: Symbol, isLocal: Bool)

syntax ItemKind ::= "itemKindFn"
                   | "itemKindStatic"
                   | "itemKindConst"
                   | itemKindCtor(CtorKind)
syntax CtorKind ::= "ctorKindConst"
                  | "ctorKindFn"

endmodule
