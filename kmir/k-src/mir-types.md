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
  syntax RigidTy ::= "bool"                                            //TypeKind::Bool
                   |  "char"                                           //TypeKind::Char
                   | IntTy                                             //TypeKind::Int(IntTy)
                   | UintTy                                            //TypeKind::Uint(UintTy)
                   | FloatTy                                           //TypeKind::Float(FloatTy)
                   | "adt" "(" AdtDef "," GenericArgs ")"              //TypeKind::Adt(AdtDef, GenericArgs), AdtDef= DefId
                   | "Foreign" "(" DefId ")"                           //TypeKind::Foreign(ForeignDef), ForeignDef = DefId
                   | "str"                                             //TypeKind::Str
                   | "[" Type ";" Int "]"                              //TypeKind::Array(t:Ty, c:Const)
                   | "[" Type "]"                                      //TypeKind::Slice(t:ty) 
                   | "*" TypeMut Type                                  //TypeKind::RawPtr(Ty, Mutability)
                   | "&" Region " " RefMut " " Type                    //TypeKind::Ref(r:Region, t:Type, m:Mutability)
                   | "FnDef" "(" DefId "," GenericArgs ")"             //TypeKind::FnDef(d:FnDef, s:GenericArgs). FnDef = DefId
                   | "[" PolyFnSig "]"                                 //TypeKind::FnPtr(s:PolyFnSig) should have a signature like "fn() -> i32"
                   | DynStr ListBinderExistentialPredicate "+" Region  //TypeKind::Dynamic(Vec<Binder<ExistentialPredicate>>, Region, DynKind)
                   | "Closure" "(" DefId "," GenericArgs ")"           //TypeKind::Closure(ClosureDef, GenericArgs), ClosureDef = DefId
                   | "Generator" "(" DefId "," GenericArgs "," Movbl  ")" //TypeKind::Generator(GeneratorDef, GenericArgs, Movability)
                   | "!"                                               //TypeKind::Never
                   | TupleTy                                           //TypeKind::(Vec<Ty>), TODO: Oversimplied, needs to check the other possibilities

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

  syntax AdtDef ::= DefPath

  syntax GenericArgs ::= List{GenericArg, ""}
  syntax GenericArg  ::= Region // GenericArgKind::Lifetime(lt)
                       | Type   //GenericArgKind::Type(ty)
                       | Const  //GenericArgKind::Const

  syntax Const

  syntax TypeMut ::= "mut"   //TypeAndMut.Mutability = Mut
                   | "const" //TypeAndMut.Mutability = Not

  //https://github.com/rust-lang/rust/blob/c40cfcf0494ff7506e753e750adb00eeea839f9c/compiler/rustc_type_ir/src/sty.rs#L1374
  syntax Region ::= "ReEarlyBound" "(" DefId "," Int "," Symbol ")"                        //RegionKind::ReEarlyBound(EarlyBoundRegion, EarlyBoundRegion {DefId, u32,Symbol} where symbil is an index type
                  | "ReLateBound" "(" "DebruijnIndex" "(" Int ")" "," BoundRegionKind ")"  //RegionKind::ReLateBound(binder_id:DebruijinIndex, bound_region:BoundRegionKind)
                  | "Refree" "(" DefId "," BoundRegionKind ")"                             //RegionKind::ReFree(fr:FreeRegion)
                  | "Restatic"                                                             //RegionKind::ReStatic
                 // | "ReplaceHolder"                                                      //RegionKind::RePlaceGolder
                  | "ReErased"                                                             //RegionKind::ReErased
                 // | "ReError"                                                            //RegionKind::ReError

  //https://github.com/rust-lang/rust/blob/c5833f1956bea474034ffec5ab2c75f343548038/compiler/rustc_middle/src/ty/structural_impls.rs#L70
  syntax BoundRegionKind ::= "BrAnon" "(" String ")"            //ty::BrAnon(Span)
                           | "BrNamed" "(" Symbol ")"           // ty::BrNamed(did:DefId, Symbol) && did.is_crate_root()
                           | "BrNamed" "(" DefId "," Symbol ")" // ty::BrNamed(did:DefId, Symbol) && !did.is_crate_root()
                           | "BrEnv"                            //ty::BrEnv

  syntax RefMut ::= "mut" //Mutability = Mut
                  | ""    //Mutability = Not

  //PolyFnSig = Binder{value: FnSig, bound_vars: &'tcx List{BoundVariableKind}}
  syntax PolyFnSig ::= "Binder" "(" Value "," Bind ")"
  syntax Value ::= UnsafetyPrefix Abi "fn" "(...)" OutputType                  // inputs.len() = 0 && *c_variadic
                 | UnsafetyPrefix Abi "fn" "()" OutputType                     // inputs.len() = 0 && !*c_variadic
                 | UnsafetyPrefix Abi "fn" "(" InputTypes "..." ")" OutputType // inputs.len() != 0 && *c_variadic
                 | UnsafetyPrefix Abi "fn" "(" InputTypes ")" OutputType       // inputs.len() != 0 && !*c_variadic

  syntax UnsafetyPrefix ::= "" | "unsafe"

  syntax InputTypes ::= List{Type, ","}

  syntax OutputType ::= ""           //output().kind matcheds ty::Tuple(list) if list.is_empty()
                      | "->" Type    //otherwise

  // https://github.com/rust-lang/rust/blob/c5833f1956bea474034ffec5ab2c75f343548038/compiler/rustc_middle/src/ty/structural_impls.rs#L97
  syntax Abi ::= ""               // rustc_target::spec::abi::Abi::Rust
               | "extern C"       // rustc_target::spec::abi::Abi::C  
              // | "extern abi"   // https://github.com/rust-lang/rust/blob/master/compiler/rustc_target/src/spec/abi.rs

  syntax DynStr ::= "dyn"   //DynKind::Dyn 
                  | "dyn*"  //DynKind::DynStar
                
  syntax ListBinderExistentialPredicate //TODO： List<Binder<'tcx, ExistentialPredicate<'tcx>>>

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
  // https://github.com/rust-lang/rust/blob/c40cfcf0494ff7506e753e750adb00eeea839f9c/compiler/rustc_type_ir/src/sty.rs#L572
  syntax Alias //::=  "Alias" "(" AliasKind "," AliasTy ")"         //TypeKind::Alias(i:AliasKind, a:AliasTy)

// // https://github.com/rust-lang/rust/blob/c5833f1956bea474034ffec5ab2c75f343548038/compiler/rustc_middle/src/ty/sty.rs#L1220
// // https://github.com/rust-lang/rust/blob/c5833f1956bea474034ffec5ab2c75f343548038/compiler/rustc_middle/src/ty/print/pretty.rs#L741
// // https://github.com/rust-lang/rust/blob/c5833f1956bea474034ffec5ab2c75f343548038/compiler/rustc_middle/src/ty/print/pretty.rs#L757
//   syntax AliasKind ::= Projection                          //DefKind::AssocTy who's parent is a DefKind::Impl=> AliasKind::Projection, something to do with DefKind: https://github.com/rust-lang/rust/blob/master/compiler/rustc_hir/src/def.rs
//                      | Inherent                          //DefKind::AssocTy if let DefKind::Impl { of_trait: false } = tcx.def_kind(tcx.parent(self.def_id)) => AliasKind::Inherent
//                      | Opaque                              //DefKind::OpaqueTy => AliasKind::Opaque
//                      | Weak                               //DefKind::TyAlias { .. } => ty::Weak,

//   syntax AliasTy ::= "AliasTy" "{" "args:" GenericArgs "def_id:" DefId "}" //https://github.com/rust-lang/rust/blob/c5833f1956bea474034ffec5ab2c75f343548038/compiler/rustc_middle/src/ty/structural_impls.rs#L240

//   syntax Opaque ::= "Opaque" "(" DefId "," GenericArgs ")" //ty::Alias(ty::Opaque, ty::AliasTy { def_id, args, .. })
```

# The [Param](https://github.com/rust-lang/rust/blob/f3b4c6746aa0e278797ae52e2c16fdef04136e3a/compiler/rustc_smir/src/stable_mir/ty.rs#L31) Type
It represents the type parameter. In stable MIR, its implementation is bridged to [`TypeKind::Param(I::ParamTy)`](https://github.com/rust-lang/rust/blob/c5833f1956bea474034ffec5ab2c75f343548038/compiler/rustc_type_ir/src/sty.rs#L209) in of the `rustc_type_ir`.
```k
  syntax Param ::= String "/#" Int    //ParamTy {index: u32, name: Symbol}
```

## The [Bound](https://github.com/rust-lang/rust/blob/f3b4c6746aa0e278797ae52e2c16fdef04136e3a/compiler/rustc_smir/src/stable_mir/ty.rs#L32) Type
It is used to represent the `'a` in `for<'a> fn(&'a ())`

```k
  syntax Bound ::= "^" Identifier         //ty::BoundTyKind::Anon and debruijn == INNERMOST, a.k.a., 0
                 | "^" Int "_" Identifier //ty::BoundTyKind::Anon and debruijn != INNERMOST
                 | String                 // ty::BoundTyKind::Param(_, sym: Symbol)
```
## Definition Path

```k
  //TODO:https://github.com/rust-lang/rust/blob/a1e1dba9cc40a90409bccb8b19e359c4bdf573e5/compiler/rustc_middle/src/mir/pretty.rs#L1020
  syntax DefPath ::= List{DefPathKind, "::"}

  syntax DefPathKind  ::= DefName
                        | ImplPath
                        | PathClosure
                        | PathConstant
                        | PathOpaque
                        | Int     //CrateNum or Disambiguate
  syntax DefName ::= Identifier //function name
  
  syntax ImplPath ::= "<" "impl" "at" FilePosition ">"
  syntax PathClosure ::= "{" "closure" "#" Int "}"
  syntax PathConstant ::= "{" "constant" "#" Int "}"
  syntax PathOpaque ::= "{" "opaque" "#" Int "}"
  
endmodule
```