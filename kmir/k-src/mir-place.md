```k
require "mir-types.md"
require "mir-identifiers.md"
```

```k
module MIR-PLACE
  imports STRING-SYNTAX
  imports INT-SYNTAX
  imports MIR-IDENTIFIERS
  imports MIR-TYPE-SYNTAX
```
//syntax Mutability ::= Not | Mut

### [Place](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/syntax/struct.Place.html)
Quote from RustDoc: "Places roughly correspond to a “location in memory.” Places in MIR are the same mathematical object as places in Rust. This of course means that what exactly they are is undecided and part of the Rust memory model."

```k
  syntax Place  ::= Local
                  | Projection // &'tcx List<PlaceElem<'tcx>>, projection out of a place (access a field, deref a pointer, etc)

  syntax Projection ::= ProjectionElem
  syntax Projection ::= ProjectionElem Projection //pub type PlaceElem<'tcx> = ProjectionElem<Local, Ty<'tcx>>;
```

```k
  syntax ProjectionElem ::= Deref
                          | Field
                          | Index
                          | ConstantIndex
                          | Subslice
                          | Downcast
                          | OpaqueCast

```

#### [ProjectionElem](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/syntax/enum.ProjectionElem.html)

```k
  syntax Deref ::= "(" "*" Local ")"                       // ProjectionElem::Deref

  syntax Field ::= "(" Local "." FieldIdx ":" Type ")"     // ProjectionElem::Field(field, ty)

  syntax Index ::= Local "[" Local "]"                     // ProjectionElem::Index(ref index)

  syntax ConstantIndex ::= Local "[" Int "of" Int "]"      // ProjectionElem::ConstantIndex { offset:u64, min_length:u64, from_end: false }
                         | Local "[" "-" Int "of" Int "]"  // ProjectionElem::ConstantIndex { offset:u64, min_length:u64, from_end: true }

  syntax Subslice ::= Local "[" Int ":" "]"                // ProjectionElem::Subslice { from, 0, from_end: true } 
                    | Local "[" ":" "-" Int "]"            // ProjectionElem::Subslice { 0, to, from_end: true } 
                    | Local "[" Int ":" "-" Int "]"        // ProjectionElem::Subslice { from:u64, to:u64, from_end: true }
                    | Local "[" Int ".." Int "]"           // ProjectionElem::Subslice { from, to, from_end: false }

  syntax Downcast ::= "(" Local "as" String ")"            // ProjectionElem::Downcast(Some(name:Symbol), _index: VarantIdx)
                    | "(" Local "as" "variant" "#" VariantIdx ")" // ProjectionElem::Downcast(None, index: VariantIdx)

  syntax OpaqueCast ::= "(" Local "as" Type ")"            // ProjectionElem::OpaqueCast(ty)
```

```k
endmodule
```
