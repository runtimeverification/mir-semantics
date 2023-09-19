```k
require "mir-types.md"
require "mir-place.md"
require "mir-basicblock.md"
```

MIR syntax
----------
This module is designed to parse the exported MIR of a rust program from `rustc` into `KItem`s accepted by K framework. It is a decompilation process from [string format MIR to strcutured MIR in K.

```k
module MIR-SYNTAX
  imports INT-SYNTAX
  imports MIR-TYPE-SYNTAX
  imports MIR-PLACE
  //imports MIR-IDENTIFIERS
  imports MIR-BASICBLOCK-SYNTAX
```

```k
  syntax Mir ::= List{Item, ""}

  syntax Item ::= Function
             // | UserTypeAnnotations //TODO:
  
  //syntax UserTypeAnnotations ::= "| UserTypeAnnotations \n" "|" Int ":" "user_ty:" UserType "," "span:" String "," "inderred_ty:" Type "|"

  //We disabled the Promoted while dumping mir using Rustc.
  syntax Function ::= Fn Promoteds             //ty::InstanceDef::Item(def_id)
//                    | Fn Promoteds FnForCTFE   //ConstFnRaw: tcx.def_kind(def_id) = DefKind::Fn | DefKind::AssocFn | DefKind::Ctor(..) | DefKind::Closure && tcx.constness(def_id) == hir::Constness::Const
```
## Function signatures 
They are dependent on the function type. Where in the pretty print, the [implementations](//https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/pretty.rs#L988) matches `(kind:DefKind, body.source.promoted:Option(Promoted) )` to different types.
```k
  syntax Fn ::= FnSig "{" Body "}"
              | FnSig "{" Body "}" Allocations //assume only Fn Body has allocations

  syntax Promoteds ::= List{Promoted, ""}
  syntax Promoted ::= PromotedSig "{" Body "}"

  syntax PromotedSig ::= "promoted" "[" Int "]" DefPath ":" Type "="            //pattern: (_, Some(i)). Here Int is a Promoted Type, a.k.a., index type in rustc_index
  
//  syntax FnForCTFE ::= Fn

  syntax FnSig ::= "const" DefPath ":" Type "="                           //pattern: (DefKind::Const | DefKind::AssocConst, _)
                 | "static" DefPath ":" Type "="                          //pattern: (DefKind::Static(hir::Mutability::Not), _)
                 | "static mut" DefPath ":" Type "="                      //pattern: (DefKind::Static(hir::Mutability::Mut), _)
                 | "fn" DefPath "()" "->" Type                            //pattern: DefKind::Fn | DefKind::AssocFn | DefKind::Ctor(..) | DefKind::Closure
                 | "fn" DefPath "(" Args ")" "->" Type                    //pattern: DefKind::Fn | DefKind::AssocFn | DefKind::Ctor(..) | DefKind::Closure
                //  | "fn" DefPath "(" LocalToken ":" Type ")" "->" Type // FAIL: test-sum-to-n.mir                    //pattern: DefKind::Fn | DefKind::AssocFn | DefKind::Ctor(..) | DefKind::Closure
                //  | "fn" DefPath "(" "_1" ":" Type ")" "->" Type  // PASS: test-sum-to-n.mir                   //pattern: DefKind::Fn | DefKind::AssocFn | DefKind::Ctor(..) | DefKind::Closure
                 | "fn" DefPath "()" "->" Type  "yields" Type             //pattern: DefKind::Generator     //TODO: Do we need `\n`
                 | "fn" DefPath "(" Args ")" "->" Type  "yields" Type     //pattern: DefKind::Generator
                 | DefPath ":" Type "="                                   //pattern: (DefKind::AnonConst | DefKind::InlineConst, _)

  syntax Arg ::= Local ":" Type
  syntax Args ::= List{Arg, ","}

  syntax Allocations
/*   // https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/pretty.rs#L725
  // https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/pretty.rs#L806
  // https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/pretty.rs#L848
  syntax Allocation ::= Identifier "(" MaybeStaticPath "size" ":" Int "," "align" ":" Int ")" "{" DataAllocData "}"
  syntax DataAllocData ::= DataAllocDataShortLine | DataAllocDataLines
  syntax DataAllocElement ::= AllocReferenceToken | DoubleHexDigit | "__"
  syntax DoubleHexDigit ::= Int | DoubleHexDigitNoInt
  syntax DoubleHexDigitNoInt ::= DoubleHexDigitNoIntLetter | DoubleHexDigitNoIntDigit

  syntax MaybeStaticPath ::= "" | "static" ":" FunctionPath ","
  syntax DataAllocDataShortLine ::= List{DataAllocElement, ""}
  syntax DataAllocDataLine ::= HexLiteral "|" DataAllocDataShortLine
  syntax DataAllocDataLines ::= NeList {DataAllocDataLine, ""} */

```

The `Body` sort represents a single MIR function. Based on [`rustc::mir::Body`](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/struct.Body.html).

```k
  syntax Body ::= VarDebugList LocalDecls ScopeTree BasicBlocks

  syntax VarDebugList ::= List{VarDebug, ""} 
  syntax VarDebug ::= "debug" UserVar "=>" Place ";"

  // Temporaries and the return place are always mutable.
  // a binding declared by the user, a temporary inserted by the compiler, a function argument, or the return place
  // a binding declared by the user, a function argument will be recorded as a localdecl, the others will be a map from place to value
  syntax LocalDecls ::= List{LocalDecl, ""}
  syntax LocalDecl ::= "let" Local ":" Type ";"
                   | "let" "mut" Local ":" Type ";"
                   // UserTypeProjecttion
  
/*   syntax Mutability ::= MutPrefixToMutability(MutPrefix) [function]
  rule MutPrefixToMutability("") => Not
  rule MutPrefixToMutability("mut") => Mut */
  
  syntax ScopeTree ::= List{Scope, ""}
  syntax Scope ::= "scope" Int "{" VarDebugList LocalDecls ScopeTree "}" //Body::source_scope

  syntax BasicBlocks ::= List {BasicBlock, ""} //IndexVec
  // syntax BasicBlock`

endmodule
```

```k
module MIR-PARSER-SYNTAX
  imports MIR-SYNTAX

  // Declaring regular expressions of sort `#Layout` infroms the K lexer to drop these tokens.
  syntax #Layout  ::= r"(\\/\\/[^\\n\\r]*)" // single-line comments
                    | r"([\\ \\n\\r\\t])"   // whitespace

endmodule
```
