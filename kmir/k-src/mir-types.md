```k
require "mir-identifiers.md"
```

Syntax of MIR types
-------------------
# [Stable MIR Types](https://github.com/rust-lang/rust/blob/master/compiler/rustc_smir/src/stable_mir/ty.rs)

```k
module MIR-TYPE-SYNTAX
  imports MIR-IDENTIFIERS

  syntax Type ::= RigidTy       //stable_mir::Ty::TyKind::RigidTy(RigidTy)
                | Alias         //stable_mir::Ty::TyKind::Alias(AliasKind, AliasTy)
                | Param         //stable_mir::Ty::TyKind::Param(ParamTy)
                | Bound         //stable_mir::Ty::TyKind::Bound(usize, BoundTy)

```
The following `TyKind` are defined in `rust_type_ir` but not used in [Stable mir TyKind](https://github.com/rust-lang/rust/blob/f3b4c6746aa0e278797ae52e2c16fdef04136e3a/compiler/rustc_smir/src/rustc_smir/mod.rs#L1097).
- TypeKind::GeneratorWitness(g:BinderLIstTy), printed as "GeneratorWitness" "(" BinderListTy ")" 
- TypeKind::GeneratorWitnessMIR(d:DefId, s:GenericArgsRef) printed as "GeneratorWitnessMIR" "(" DefId "," GenericArgsRef")" 
- TyKind::Placeholder(PlaceholderType)
- TyKind::Infer(InferTy)
- TyKind::Error(ErrorGaranteed)

```k
  syntax RigidTy ::= "bool"     //TypeKind::Bool
                   |  "char"    //TypeKind::Char
                   | IntTy      //TypeKind::Int(IntTy)
                   | UintTy     //TypeKind::Uint(UintTy)
                   | FloatTy    //TypeKind::Float(FloatTy)
                   | "adt" "(" AdtDef "," GenericArgs ")"  //TypeKind::Adt(AdtDef, GenericArgs), AdtDef= DefId
                   | "Foreign" "(" DefId ")" //TypeKind::Foreign(ForeignDef), ForeignDef = DefId
                   | "str"      //TypeKind::Str
                   | "[" Type ";" Int "]" //TypeKind::Array(t:Ty, c:Const)
                   | "[" Type "]"//TypeKind::Slice(t:ty) 
                   | "*" TypeMut Type //TypeKind::RawPtr(Ty, Mutability)
                   | "&" Region " " RefMut " " Type // TypeKind::Ref(r:Region, t:Type, m:Mutability)
                   | "FnDef" "(" DefId "," GenericArgsRef ")" // TypeKind::FnDef(d:FnDef, s:GenericArgs). FnDef = DefId
                   | "["  "]" // TypeKind::FnPtr(s:PolyFnSig) should have a signature like "fn() -> i32"
                   | DynStr ListBinderExistentialPredicate "+" Region //TypeKind::Dynamic(Vec<Binder<ExistentialPredicate>>, Region, DynKind)
                   | "Closure" "(" DefId "," GenericArgsRef ")" //TypeKind::Closure(ClosureDef, GenericArgs), ClosureDef = DefId
                   | "Generator" "(" DefId "," GenericArgsRef "," Movbl  ")" //TypeKind::Generator(GeneratorDef, GenericArgs, Movability)
                   | "!" //TypeKind::Never
                   | TupleTy //TypeKind::(Vec<Ty>), TODO: Oversimplied, needs to check the other possibilities

    syntax IntTy ::= "isize"
                   | "i8"
                   | "i16" 
                   | "i32"
                   | "i64"
                   | "i128"

  syntax UintTy ::= "usize"  
                  | "u8"
                  | "u16"
                  | "u32"
                  | "u64"
                  | "u128"

  syntax FloatTy ::= "f32"
                   | "f64"

  syntax AdtDef //TODO:

  syntax GenericArgs //TODO:

  syntax TypeMut ::= "mut"   //TypeAndMut.Mutability = Mut
                   | "const" //TypeAndMut.Mutability = Not

  syntax Region //TODO

  syntax RefMut ::= "mut" //Mutability = Mut
                  | ""    //Mutability = Not

  syntax DynStr ::= "dyn"   //DynKind::Dyn 
                | "dyn*"  //DynKind::DynStar
                
  syntax ListBinderExistentialPredicate //TODO

  //Used the pretty print from ast::Movability, https://github.com/rust-lang/rust/blob/b531630f4255216fce1400c45976e04f1ab35a84/compiler/rustc_ast_pretty/src/pprust/state/expr.rs#L667
  syntax Movbl ::= "static" //Movability = Static, May contain self reference
                 | ""       //Movability = Movable, must not contain self reference

  syntax TupleTy ::= "(" ")"
                   | "(" Type ",)"
                   | "(" Type "," Type ")"//TODO: Not sure why the implementation should have  "(" Type "," Type ")" TypeList ")" 
```

# The [`Alias`](https://github.com/rust-lang/rust/blob/c5833f1956bea474034ffec5ab2c75f343548038/compiler/rustc_smir/src/stable_mir/ty.rs#L30) Type 
It represents a projection of an associated type. In stable MIR, its implementation is bridged to [`TypeKind::Alias(AliasKind, I::AliasTy)`](https://github.com/rust-lang/rust/blob/c5833f1956bea474034ffec5ab2c75f343548038/compiler/rustc_type_ir/src/sty.rs#L203) of the `rustc_type_ir`.


```k
  syntax Alias ::=  "Alias" "(" AliasKind "," AliasTy ")"         //TypeKind::Alias(i:AliasKind, a:AliasTy)
// https://github.com/rust-lang/rust/blob/c5833f1956bea474034ffec5ab2c75f343548038/compiler/rustc_middle/src/ty/sty.rs#L1220
  syntax AliasKind ::= AssocTyDescr                          //DefKind::AssocTy who's parent is a DefKind::Impl=> AliasKind::Projection, something to do with DefKind: https://github.com/rust-lang/rust/blob/master/compiler/rustc_hir/src/def.rs
                     | AssocTyDescr                          //DefKind::AssocTy if let DefKind::Impl { of_trait: false } = tcx.def_kind(tcx.parent(self.def_id)) => AliasKind::Inherent
                     | OpaqueTyDescr                              //DefKind::OpaqueTy => AliasKind::Opaque
                     | TyAliasDescr                               //DefKind::TyAlias { .. } => ty::Weak,
                     | "unexpected DefKind in AliasTy:" DefKind   //Other DefKinds

  syntax AliasTy ::= "AliasTy" "{" "args:" GenericArgs "def_id:" DefId "}" //https://github.com/rust-lang/rust/blob/c5833f1956bea474034ffec5ab2c75f343548038/compiler/rustc_middle/src/ty/structural_impls.rs#L240
```

# The [Param](https://github.com/rust-lang/rust/blob/f3b4c6746aa0e278797ae52e2c16fdef04136e3a/compiler/rustc_smir/src/stable_mir/ty.rs#L31) Type
It represents the type parameter. In stable MIR, its implementation is bridged to [`TypeKind::Param(I::ParamTy)`](https://github.com/rust-lang/rust/blob/c5833f1956bea474034ffec5ab2c75f343548038/compiler/rustc_type_ir/src/sty.rs#L209) in of the `rustc_type_ir`.
```k
  syntax Param
```

## The [Bound](https://github.com/rust-lang/rust/blob/f3b4c6746aa0e278797ae52e2c16fdef04136e3a/compiler/rustc_smir/src/stable_mir/ty.rs#L32) Type
It is used to represent the `'a` in `for<'a> fn(&'a ())`

```k
  syntax Bound
```

```k
  syntax TypeNoBounds ::= ImplTraitTypeOneBound
                        // In the Rust syntax, ImplTraitTypeReduced is a direct
                        // child of type. For some reason, MIR allows `&impl A+B`
                        // so it needs to be a child of TypeNoBounds
                        | ImplTraitTypeReduced
                        | TraitObjectTypeOneBound
                        | TypePath
                        | QualifiedPathInType
                        // Probably not used im MIR: MacroInvocation
                        | MirOnlyTyp

  // https://doc.rust-lang.org/reference/types/impl-trait.html
  syntax ImplTraitTypeOneBound ::= "impl" TraitBound

  // https://doc.rust-lang.org/reference/types/trait-object.html
  syntax TraitObjectTypeOneBound ::= "dyn" TraitBound

  // https://doc.rust-lang.org/reference/paths.html#paths-in-types
  syntax TypePath ::= "::" TypePathList "::" TypePathEndSegment
                    | TypePathList "::" TypePathEndSegment
                    | "::" TypePathEndSegment
                    | TypePathEndSegment

  syntax TypePathList ::= NeList{TypePathSegment, "::"}

  syntax TypePathSegment  ::= PathIdentSegment PathIdentSegmentSuffix
                            | PathIdentSegment "::" PathIdentSegmentSuffix
                            | PathOpaque

  syntax TypePathEndSegment ::= PathIdentSegment PathIdentSegmentEndSuffix
                              | PathIdentSegment "::" PathIdentSegmentEndSuffix
                              | PathOpaque

  // In the Rust documentation, TypePathFn is included in PathIdentSegmentSuffix.
  // However, that generates a parse ambiguity:
  // a::b() -> c::d
  // can be parsed either as a path with three elements:
  // a::(b() -> c)::d
  // or as a path with two elements:
  // a::(b() -> (c::d))
  // TODO: Figure out if this needs disambiguation at runtime, or
  // if having the TypePathFn part at the end is good enough.
  syntax PathIdentSegmentSuffix ::= ""
                                  | GenericArgs
  syntax PathIdentSegmentEndSuffix  ::= PathIdentSegmentSuffix
                                      | TypePathFn

  syntax PathIdentSegment ::= Identifier | "$crate"
  syntax GenericArgs ::= "<" GenericArgsList ">"
  syntax GenericArgsList ::= List{GenericArg, ","}
  syntax GenericArg ::= Lifetime
                      | Type
                      | GenericArgsConst
                      | GenericArgsBinding
                      | PathExpression "+" PathExpression
  syntax GenericArgsConst ::= LiteralExpression
                            | "-" LiteralExpression
                            //| BlockExpression
                            // SimplePathSegmentReduced is not actually needed, it's covered by Type
  syntax GenericArgsBinding ::= Identifier "=" Type
  syntax TypePathFn ::= "(" TypeList ")" MaybeResultType
  syntax MaybeResultType ::= "" | "->" Type

  // https://doc.rust-lang.org/reference/types/pointer.html#shared-references-
  syntax ReferenceType  ::= "&" TypeNoBounds
                          | "&" Lifetime TypeNoBounds
                          | "&" "mut" TypeNoBounds
                          | "&" Lifetime "mut" TypeNoBounds
  syntax DoubleReferenceType  ::= "&&" TypeNoBounds
                                | "&&" Lifetime TypeNoBounds
                                | "&&" "mut" TypeNoBounds
                                | "&&" Lifetime "mut" TypeNoBounds

  // https://doc.rust-lang.org/reference/trait-bounds.html
  // TODO: Make this a token.
  // TODO: There are various lifetime-related tokens that I combined into a
  // single one. Consider actually using multiple token types.
  syntax Lifetime ::= "'" Identifier | "'static"
  syntax LifetimeBounds ::= List{Lifetime, "+"}
  // https://doc.rust-lang.org/reference/paths.html#qualified-paths
  syntax QualifiedPathInType ::= QualifiedPathType
  syntax QualifiedPathInType ::= QualifiedPathInType "::" TypePathSegment
  syntax QualifiedPathType  ::= "<" Type ">"
                              | "<" Type "as" TypePath ">"
  // https://doc.rust-lang.org/reference/types/function-pointer.html
  syntax BareFunctionType ::= MaybeForLifetimes FunctionTypeQualifiers
                              "fn" "(" FunctionParametersMaybeNamedVariadic ")"
                              MaybeBareFunctionReturnType
                              MaybeCurlyBraceTypeAnnotation
  syntax FunctionTypeQualifiers ::= "" | "unsafe" | "extern" Abi | "unsafe" "extern" Abi
  syntax FunctionParametersMaybeNamedVariadic ::= MaybeNamedFunctionParameters
                                                // Not seen in MIR: MaybeNamedFunctionParametersVariadic
                                                // TODO: Try to generate this
  syntax MaybeNamedFunctionParameters ::= List {MaybeNamedParam, ","}
  syntax BareFunctionReturnType ::= "->" TypeNoBounds
  syntax MaybeBareFunctionReturnType ::= "" | BareFunctionReturnType
  // See
  // kmir/src/tests/integration/test-data/compiletest-rs/ui/closures/old-closure-fn-coerce.cs
  // for some rust code that produces this.
  syntax MaybeCurlyBraceTypeAnnotation ::= "" | "{" PathExpression "}"
  // https://doc.rust-lang.org/reference/trait-bounds.html#higher-ranked-trait-bounds
  syntax ForLifetimes ::= "for" GenericParams
  syntax MaybeForLifetimes ::= "" | ForLifetimes

  // https://doc.rust-lang.org/reference/items/generics.html
  syntax GenericParams ::= "<" GenericParamList ">"
  syntax GenericParamList ::= List{GenericParam, ","}

  // https://doc.rust-lang.org/reference/types/impl-trait.html
  // There is a parse conflict between
  // Type -> TypeNoBounds -> ImplTraitTypeOneBound -> impl TraitBound
  // and Type -> TypeParamBounds -> impl TypeParamBound -> impl TraitBound
  // This is an attempt to solve this issue.
  syntax ImplTraitType ::= ImplTraitTypeOneBound | ImplTraitTypeReduced
  syntax ImplTraitTypeReduced ::= "impl" TypeParamBoundsReduced
  // https://doc.rust-lang.org/reference/types/trait-object.html
  // TraitObjectType has a similar conflict as ImplTraitType, solved in the
  // same way.
  syntax TraitObjectType::= TraitObjectTypeOneBound | TraitObjectTypeReduced
  syntax TraitObjectTypeReduced ::= "dyn" TypeParamBoundsReduced
  // https://doc.rust-lang.org/reference/trait-bounds.html
  syntax TypeParamBounds ::= ImplTraitTypeOneBound | TypeParamBoundsReduced
  syntax TypeParamBoundsReduced ::= Lifetime
                                  | TypeParamBound "+" TypeParamBoundsList
  syntax TypeParamBoundsReduced2  ::= ImplTraitTypeOneBound
                                    | TypeParamBound "+" TypeParamBoundsList
  syntax TypeParamBoundsList ::= NeList{TypeParamBound, "+"}
  syntax TypeParamBound ::= Lifetime | TraitBound
  syntax TraitBound ::= TraitBoundInner
                      | "(" TraitBoundInner ")"
  syntax TraitBoundInner  ::= "?" MaybeForLifetimes TypePath
                            | MaybeForLifetimes TypePath

  // https://doc.rust-lang.org/reference/items/generics.html
  // OuterAttributes are likely not used for GenericParam in MIR.
  syntax GenericParam ::= LifetimeParam
                        | TypeParam
                        // ConstParam is likely not used in MIR.
  syntax LifetimeParam  ::= Lifetime
                          | Lifetime ":" LifetimeBounds
  syntax TypeParam  ::= Identifier MaybeColonTypeParamBounds MaybeEqualsType
  syntax MaybeColonTypeParamBounds ::= "" | ":" | ":" TypeParamBounds
  syntax MaybeEqualsType ::= "" | "=" Type

  // It is likely that MIR does not use the full syntax for MaybeNamedParam
  syntax MaybeNamedParam ::= Type

  syntax Abi ::= StringLiteral

  

  syntax Literal  ::= UnsignedLiteral
                    | SignedLiteral
                    | FloatLiteral
                    | HexLiteral
                    | StringLiteral
                    | CharLiteral
                    | ByteLiteral
                    | ByteStringLiteral

  // https://doc.rust-lang.org/reference/expressions/literal-expr.html
  syntax LiteralExpression  ::= Literal
                              | Int
                              | Bool

  // https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/pretty.rs#L725
  // https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/pretty.rs#L806
  // https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/pretty.rs#L848
  syntax DataAlloc ::= Identifier "(" MaybeStaticPath "size" ":" Int "," "align" ":" Int ")" "{" DataAllocData "}"
  syntax DataAllocData ::= DataAllocDataShortLine | DataAllocDataLines
  syntax DataAllocElement ::= AllocReferenceToken | DoubleHexDigit | "__"
  syntax DoubleHexDigit ::= Int | DoubleHexDigitNoInt
  syntax DoubleHexDigitNoInt ::= DoubleHexDigitNoIntLetter | DoubleHexDigitNoIntDigit

  syntax MaybeStaticPath ::= "" | "static" ":" FunctionPath ","
  syntax DataAllocDataShortLine ::= List{DataAllocElement, ""}
  syntax DataAllocDataLine ::= HexLiteral "|" DataAllocDataShortLine
  syntax DataAllocDataLines ::= NeList {DataAllocDataLine, ""}

  syntax FunctionAlloc ::= Identifier "(" "fn" ":" PathExpression "-" "shim" ")" 

  //syntax BB ::= BBName MaybeBBCleanup
  //syntax MaybeBBCleanup ::= "" | "(" "cleanup" ")"

  syntax MirOnlyType  ::= "[" "closure" "@" FilePosition "]"
                        | "[" "async" "fn" "body" "@" FilePosition "]"
                        | "[" "async" "block" "@" FilePosition "]"
                        | "[" MaybeStatic "generator" "@" FilePosition "]"
  syntax MaybeStatic ::= "" | "static"

  // https://doc.rust-lang.org/reference/expressions/path-expr.html
  syntax PathExpression ::= PathInExpression
                          | QualifiedPathInExpression
  // https://doc.rust-lang.org/reference/paths.html#paths-in-expressions
  syntax PathInExpression ::= "::" ExpressionPathList
                            | ExpressionPathList
  syntax ExpressionPathList ::= NeList{PathExprSegment, "::"}
  syntax PathExprSegment  ::= PathIdentSegment
                            | PathIdentSegment "::" GenericArgs
                            | PathLocation  // MIR-only thing.
                            | TypeImplSegment  // MIR-only thing.
  // https://doc.rust-lang.org/reference/paths.html#qualified-paths
  syntax QualifiedPathInExpression  ::= QualifiedPathType "::" ExpressionPathList

  syntax TypeImplSegment  ::= "<" "impl" NonPathImplementableType ">"


  // TODO: This grammar needs a preprocessing step that removes comments and
  // the textual representation at the end of memory dump lines, e.g. the
  // │ ........ part here:
  // alloc1 (static: RAND_SOURCE, size: 8, align: 8) {
  //   00 00 00 00 00 00 00 00                         │ ........
  // }
  // It should also replace │ by |.
  // For clarity, here are the (VSC) regular expressions for cleaning memory dumps:
  // Replace ^(\s*(?: [0-9a-fA-F][0-9a-fA-F])+)\s+│.*$ with $1
  // Replace ^(\s+0x[0-9a-fA-F]+\s+)│(\s*(?: [0-9a-fA-F][0-9a-fA-F])+)\s+│.*$ with $1|$2



```

```k
endmodule
```

Semantics of MIR types
----------------------

```k
module MIR-TYPES
  imports MIR-HOOKS
  imports MIR-VALUE
endmodule
```

Runtime `MIRValue` types
========================

```k
module MIR-VALUE
  imports INT
  imports STRING
  imports BYTES
  imports MIR-TYPE-SYNTAX
  imports MIR-LEXER-SYNTAX

  syntax KItem ::= RValueResult
```

Result of interpretation (inspired by [InterpResult](https://github.com/rust-lang/rust/blob/bd43458d4c2a01af55f7032f7c47d7c8fecfe560/compiler/rustc_middle/src/mir/interpret/error.rs#L496)), either a `RValueResult` or an `InterpError`:

```k
  syntax InterpResult ::= RValueResult
                        | InterpError

  syntax RValueResult ::= fromInterpResult(InterpResult) [function]
  //---------------------------------------------------------------
  rule fromInterpResult(VALUE:RValueResult) => VALUE
  rule fromInterpResult(_ERROR:InterpError) => "Error: fromInterpResult --- InterpError encoutered" [owise]
```

The values of `RValueResult` sort represent the evaluation result of the syntactic `RValue`:
TODO: add more domain sorts

```k
  syntax RValueResult ::= MIRValue
                        | MIRValueNeList

  syntax MIRValueNeList ::= MIRValue | MIRValue MIRValueNeList
```

The `InteprError` sort represent the errors that may occur while interpreting an `RValue` into `RValueResult` (inspired by [InterpError](https://github.com/rust-lang/rust/blob/bd43458d4c2a01af55f7032f7c47d7c8fecfe560/compiler/rustc_middle/src/mir/interpret/error.rs#L480)):

```k
  syntax InterpError ::= Unsupported(KItem)
```

A best-effort default value inference function, for locals initialization.
**ATTENTION** this function will return `UNIMPLEMENTED` for types that are not handled.

```k
  syntax MIRValue ::= defaultMIRValue(Type) [function]
  //--------------------------------------------------
  rule defaultMIRValue(( ):TupleType) => Unit
  rule defaultMIRValue(USIZE_TYPE)    => 0     requires IdentifierToken2String(USIZE_TYPE) ==String "usize"
  rule defaultMIRValue(BOOL_TYPE)     => false requires IdentifierToken2String(BOOL_TYPE)  ==String "bool"
  rule defaultMIRValue(!)             => Never
  rule defaultMIRValue(_:Type)        => UNIMPLEMENTED [owise]
```

```k
endmodule
```
