```k
requires "body.md"
requires "ty.md"

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

syntax Symbol ::= symbol(String) [group(mir-string)]
syntax Opaque ::= opaque(String) [symbol(opaque)]
syntax Filename ::= filename(String)

syntax TraitDecls ::= List {TraitDef, ""}
syntax ImplTraitDecls ::= List {ImplDef, ""}

syntax CrateItem ::= crateItem(Int) // imported from crate
syntax CrateNum ::= crateNum(Int)
syntax Crate ::= crate(id: CrateNum, name: Symbol, isLocal: MIRBool)

syntax ItemKind ::= "itemKindFn" [symbol(itemKindFn)]
                  | "itemKindStatic" [symbol(itemKindStatic)]
                  | "itemKindConst" [symbol(itemKindConst)]
                  | itemKindCtor(CtorKind)
syntax CtorKind ::= "ctorKindConst"
                  | "ctorKindFn"

endmodule
```
