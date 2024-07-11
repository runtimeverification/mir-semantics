module LIB-SORTS

syntax CrateItem
syntax ItemKind
syntax Opaque
syntax Symbol

endmodule

module LIB
  imports BODY-SORTS
  imports LIB-SORTS
  imports TYPES-SORTS
  imports STRING

syntax Symbol ::= String
syntax Opaque ::= opaque(String) [symbol(opaque)]
syntax Filename ::= String

syntax TraitDecls ::= List {TraitDef, ""}
syntax ImplTraitDecls ::= List {ImplDef, ""}

syntax CrateItem ::= Int // imported from crate
syntax CrateNum ::= crateNum(Int)
syntax Crate ::= crate(id: CrateNum, name: Symbol, isLocal: Bool)

syntax ItemKind ::= "itemKindFn" [symbol(itemKindFn)]
                  | "itemKindStatic" [symbol(itemKindStatic)]
                  | "itemKindConst" [symbol(itemKindConst)]
                  | itemKindCtor(CtorKind)
syntax CtorKind ::= "ctorKindConst"
                  | "ctorKindFn"

endmodule
