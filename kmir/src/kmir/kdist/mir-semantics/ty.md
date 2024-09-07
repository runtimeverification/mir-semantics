```k
module TYPES-SORTS

syntax AdtDef
syntax Align
syntax Allocation
syntax BoundVariableKindList
syntax ClosureDef
syntax CoroutineDef
syntax ExistentialTraitRef
syntax GenericArgs
syntax ImplDef
syntax MirConst
syntax Movability
syntax Region
syntax Span
syntax TraitDef
syntax Ty
syntax TyConst
syntax VariantIdx
syntax MIRInt
syntax MIRBool
syntax MIRString

endmodule

module TYPES
  imports ALLOC-SORTS
  imports BODY-SORTS
  imports LIB-SORTS
  imports MONO-SORTS
  imports TYPES-SORTS
  imports INT
  imports STRING
  imports LIST
```

#### Internal MIR
- [AdtDef]()
- [AliasDef]()
- [BrNamedDef]()
- [ClosureDef]()
- [ConstDef]()
- [CoroutineDef]()
- [CoroutineWitnessDef]()
- [FnDef]()
- [ForeignDef]()
- [ForeignModuleDef]()
- [GenericDef]()
- [ImplDef]()
- [ParamDef]()
- [RegionDef]()
- [TraitDef]()
- [VariantIdx]()
- [DynKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/ty_kind.rs#L19-L32)
- [ForeignModule](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_session/src/cstore.rs#L146-L151)
- [ForeignItemKind]()
- [AdtKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/adt.rs#L203-L208)
- [VariantDef]()
- [FieldDef](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/mod.rs#L1395-L1400)
- [GenericArgKind alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/generic_args.rs#L27) [GenericArgKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/generic_arg.rs#L5-L18)
- [GenericArgs](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/generic_args.rs#L335-L336) [GenericArg](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/generic_args.rs#L30-L42)
- [TermKind alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/generic_args.rs#L28) [TermKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/generic_arg.rs#L20-L32)
- [AliasTyKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/ty_kind.rs#L34-L49)
- [AliasTy alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/sty.rs#L39) [AliasTy](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/ty_kind.rs#L427-L470)
- [Abi](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_target/src/spec/abi/mod.rs#L10-L64)
- [BoundTyKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/sty.rs#L361-L366)
- [BoundRegionKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/region.rs#L365-L380)
- [BoundVariableKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/sty.rs#L253-L259)
- [FnSig alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/sty.rs#L40) [FnSig](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/ty_kind.rs#L958-L973)
- [Binder - BinderForFnSig alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/sty.rs#L41) [Binder - BinderForFnSig](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/binder.rs#L18-L40)
- [PolyFnSig]()
- [Ty](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/mod.rs#L472-L476)
- [Pattern](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/pattern.rs#L7-L9)
- [TyConst from Const](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/consts.rs#L29-L32)
- [TyConstId]()
- [MirConst from Const](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/consts.rs#L29-L32)
- [MirConstId]()
- [TyConstKind from ConstKind alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/consts.rs#L23) [TyConstKind from ConstKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/const_kind.rs#L12-L44)
- [DebruijinIndex]()
- [UniverseIndex]()
- [EarlyParamRegion]()
- [BoundVar]()
- [BoundRegion]()
- [Placeholder - PlaceholderForBoundRegion]()
- [RegionKind alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/region.rs#L15) [RegionKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/region_kind.rs#L33-L190)
- [Region](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/region.rs#L17-L20)
- [Span]()
- [ExistentialTraitRef alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/predicate.rs#L18) [ExistentialTraitRef](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/predicate.rs#L289-L309)
- [ExistentialProjection](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L94-L105)
- [ExistentialPredicate alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/predicate.rs#L17) [ExistentialPredicate](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/predicate.rs#L231-L249)
- [Binder - BinderForExistentialPredicate alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/sty.rs#L41) [Binder - BinderForExistentialPredicate](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/binder.rs#L18-L40)
- [IntTy](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/cast.rs#L9-L17)
- [UintTy ast](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_ast/src/ast.rs#L2001-L2010) [UintTy ir](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/ty_kind.rs#L633-L642)
- [FloatTy ast](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_ast/src/ast.rs#L1937-L1944) [FloatTy ir](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/ty_kind.rs#L691-L698)
- [Movability](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_ast_ir/src/lib.rs#L10-L19)
- [RigidTy -> TyKind alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/sty.rs#L37) [RigidTy -> TyKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/ty_kind.rs#L62-L250)
- [TyKind]()
- [TypeAndMut]()
- [ParamTy](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/sty.rs#L287-L292)
- [BoundTy](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/sty.rs#L344-L349)
- [Promoted]()
- [Align]()
- [ProvenanceMap]()
- [Bytes -> AllocByte and AllocBytes]()
- [Allocation]()
- [ConstantKind]()
- [ParamConst](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/sty.rs#L321-L326)
- [UnevaluatedConst]()
- [TraitSpecializationKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/trait_def.rs#L72-L88)
- [Ident]()
- [TraitDecl -> TraitDef](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/trait_def.rs#L14-L70)
- [TraitRef alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/predicate.rs#L14) [TraitRef ast](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_ast/src/ast.rs#L2838-L2848) [TraitRef ir](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/predicate.rs#L42-L69)
- [GenericParamDefKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/generics.rs#L13-L18)
- [GenericParamDef](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/generics.rs#L52-L64)
- [GenericDefAndIdxPair]()
- [Generics](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/generics.rs#L127-L147)
- [PredicateKindAndSpanPair]()
- [GenericPredicates]()
- [PredicateKind alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/predicate.rs#L22) [PredicateKind ir](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/predicate_kind.rs#L56-L112)
- [ClauseKind alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/predicate.rs#L21) [ClauseKind ir](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/predicate_kind.rs#L8-L39)
- [TraitPredicate alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/predicate.rs#L20) [TraitPredicate](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/predicate.rs#L116-L137)
- [RegionOutlivesPredicate]()
- [TypeOutlivesPredicate]()
- [ProjectionPredicate alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/predicate.rs#L16) [ProjectionPredicate ir](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/predicate.rs#L635-L660)
- [SubtypePredicate alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/predicate.rs#L25) [SubtypePredicate ir](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/predicate.rs#L761-L779)
- [CoercePredicate alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/predicate.rs#L24) [CoercePredicate ir](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/predicate.rs#L781-L796)
- [AliasRelationDirection](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/predicate_kind.rs#L114-L119)
- [ClosureKind hir](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_hir/src/hir.rs#L1014-L1028) [ClosureKind ir](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/lib.rs#L389-L401)
- [ImplPolarity ast](https://github.com/runtimeverification/rust/blob/master/compiler/rustc_ast/src/ast.rs#L2578) [ImplPolarity ir](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/predicate.rs#L176-L188)
- [PredicatePolarity](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/predicate.rs#L200-L210)

#### SMIR (Bridge)
- [AdtDef]()
- [AliasDef]()
- [BrNamedDef]()
- [ClosureDef]()
- [ConstDef]()
- [CoroutineDef]()
- [CoroutineWitnessDef]()
- [FnDef]()
- [ForeignDef]()
- [ForeignModuleDef]()
- [GenericDef]()
- [ImplDef]()
- [ParamDef]()
- [RegionDef]()
- [TraitDef]()
- [VariantIdx]()
- [DynKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L39-L48)
- [ForeignModule](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L923-L932)
- [ForeignItemKind]()
- [AdtKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L133-L143)
- [VariantDef]()
- [FieldDef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L145-L154)
- [GenericArgKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L163-L174)
- [GenericArgs](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L156-L161)
- [TermKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L79-L92)
- [AliasKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L11-L21)
- [AliasTy](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L23-L29)
- [Abi](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L888-L921)
- [BoundTyKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L223-L236)
- [BoundRegionKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L238-L252)
- [BoundVariableKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L254-L270)
- [FnSig](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L209-L221)
- [Binder - BinderForFnSig](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L176-L194)
- [PolyFnSig]()
- [Ty](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L315-L320)
- [Pattern](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L398-L410)
- [TyConst](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L454-L492)
- [TyConstId]()
- [MirConst](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L412-L452)
- [MirConstId]()
- [TyConstKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L458-L482)
- [DebruijinIndex]()
- [UniverseIndex]()
- [EarlyParamRegion]()
- [BoundVar]()
- [BoundRegion]()
- [Placeholder - PlaceholderForBoundRegion]()
- [RegionKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L806-L834)
- [Region](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L798-L804)
- [Span]()
- [ExistentialTraitRef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L67-L77)
- [ExistentialProjection](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L94-L105)
- [ExistentialPredicate](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L50-L65)
- [Binder - BinderForExistentialPredicate](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L176-L194)
- [Binder- BindersForExistentialPredicate](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L176-L194)
- [IntTy](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L272-L285)
- [UintTy](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L287-L300)
- [FloatTy](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L302-L313)
- [Movability](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L877-L886)
- [RigidTy](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L325-L394)
- [TyKind]()
- [TypeAndMut]()
- [ParamTy](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L502-L508)
- [BoundTy](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L510-L516)
- [Promoted]()
- [Align]()
- [ProvenanceMap]()
- [Bytes -> AllocByte and AllocBytes]()
- [Allocation]()
- [ConstantKind]()
- [ParamConst](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L494-L500)
- [UnevaluatedConst]()
- [TraitSpecializationKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L518-L531)
- [Ident]()
- [TraitDecl](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L533-L557)
- [TraitRef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L559-L566)
- [GenericParamDefKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L593-L608)
- [GenericParamDef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L610-L622)
- [GenericDefAndIdxPair]()
- [Generics](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L568-L591)
- [PredicateKindAndSpanPair]()
- [GenericPredicates]()
- [PredicateKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L624-L656)
- [ClauseKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L658-L692)
- [TraitPredicate](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L737-L747)
- [RegionOutlivesPredicate]()
- [TypeOutlivesPredicate]()
- [ProjectionPredicate](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L761-L771)
- [SubtypePredicate](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L707-L714)
- [CoercePredicate](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L716-L723)
- [AliasRelationDirection](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L725-L735)
- [ClosureKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L694-L705)
- [ImplPolarity](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L773-L784)
- [PredicatePolarity](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L786-L796)

#### Stable MIR
- [AdtDef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L801) [crate_def](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/stable_mir/src/crate_def.rs#L55-L69)
- [AliasDef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L939) [crate_def](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/stable_mir/src/crate_def.rs#L55-L69)
- [BrNamedDef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L796) [crate_def](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/stable_mir/src/crate_def.rs#L55-L69)
- [ClosureDef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L781) [crate_def_with_ty](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/crate_def.rs#L126-L142)
- [ConstDef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L961) [crate_def](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/stable_mir/src/crate_def.rs#L55-L69)
- [CoroutineDef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L786) [crate_def](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/stable_mir/src/crate_def.rs#L55-L69)
- [CoroutineWitnessDef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L984) [crate_def](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/stable_mir/src/crate_def.rs#L55-L69)
- [FnDef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L722) [crate_def_with_ty](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/crate_def.rs#L126-L142)
- [ForeignDef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L703) [crate_def_with_ty](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/crate_def.rs#L126-L142)
- [ForeignModuleDef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L680) [crate_def](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/stable_mir/src/crate_def.rs#L55-L69)
- [GenericDef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L956) [crate_def](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/stable_mir/src/crate_def.rs#L55-L69)
- [ImplDef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L967) [crate_def](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/stable_mir/src/crate_def.rs#L55-L69)
- [ParamDef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L791) [crate_def](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/stable_mir/src/crate_def.rs#L55-L69)
- [RegionDef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L979) [crate_def]https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/stable_mir/src/crate_def.rs#L55-L69()
- [TraitDef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L945) [crate_def](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/stable_mir/src/crate_def.rs#L55-L69)
- [VariantIdx](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1575-L1589)
- [DynKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1194-L1198)
- [ForeignModule](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L689-L692)
- [ForeignItemKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L712-L717)
- [AdtKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L804-L809)
- [VariantDef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L857-L872)
- [FieldDef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L887-L897)
- [GenericArgKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1007-L1012)
- [GenericArgs](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L987-L989)
- [TermKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1044-L1048)
- [AliasKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1050-L1056)
- [AliasTy](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1058-L1062)
- [Abi](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1100-L1126)
- [BoundTyKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1181-L1185)
- [BoundRegionKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1187-L1192)
- [BoundVariableKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1174-L1179)
- [FnSig](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1082-L1088)
- [Binder - BinderForFnSig](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1070C22-L1070C35)
- [PolyFnSig](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1070)
- [Ty](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L16-L17)
- [Pattern](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L157-L161)
- [TyConst](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L163-L168)
- [TyConstId](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L202-L203)
- [MirConst](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L205-L214)
- [MirConstId](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L263-L264)
- [TyConstKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L202-L203)
- [DebruijinIndex](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L282)
- [UniverseIndex](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L298)
- [EarlyParamRegion](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L284-L288)
- [BoundVar](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L290)
- [BoundRegion](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L292-L296)
- [Placeholder - PlaceholderForBoundRegion](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L300-L304)
- [RegionKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L273-L280)
- [Region](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L268-L271)
- [Span](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L306-L307)
- [ExistentialTraitRef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1207-L1214)
- [ExistentialProjection](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1228-L1233)
- [ExistentialPredicate](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1200-L1205)
- [Binder - BinderForExistentialPredicate](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1128-L1133)
- [Binder- BindersForExistentialPredicate](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1128-L1133)
- [IntTy](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L618-L626)
- [UintTy](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L641-L649)
- [FloatTy](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L664-L670)
- [Movability](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L672-L676)
- [RigidTy](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L579-L603)
- [TyKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L340-L346)
- [TypeAndMut](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L574-L577)
- [ParamTy](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1235-L1239)
- [BoundTy](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1241-L1245)
- [Promoted](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1256)
- [Align](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1255)
- [ProvenanceMap](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1259-L1265)
- [Bytes -> AllocByte and AllocBytes](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1247)
- [Allocation](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1267-L1273)
- [ConstantKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1343-L1352)
- [ParamConst](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1354-L1358)
- [UnevaluatedConst](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1360-L1365)
- [TraitSpecializationKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1367-L1372)
- [Ident](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L266)
- [TraitDecl](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1374-L1388)
- [TraitRef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1406-L1413)
- [GenericParamDefKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1452-L1457)
- [GenericParamDef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1459-L1466)
- [GenericDefAndIdxPair](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1446C36-L1446C53)
- [Generics](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1441-L1450)
- [PredicateKindAndSpanPair](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1470C25-L1470C46)
- [GenericPredicates](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1468-L1471)
- [PredicateKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1473-L1482)
- [ClauseKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1484-L1493)
- [TraitPredicate](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1520-L1524)
- [RegionOutlivesPredicate](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1529)
- [TypeOutlivesPredicate](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1530)
- [ProjectionPredicate](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1532-L1536)
- [SubtypePredicate](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1502-L1506)
- [CoercePredicate](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1508-L1512)
- [AliasRelationDirection](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1514-L1518)
- [ClosureKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1495-L1500)
- [ImplPolarity](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1538-L1543)
- [PredicatePolarity](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L1545-L1549)

```k
syntax TestSort2 ::= testSort2(MIRInt, MyList)     [group(mir), symbol(testSort2)]
syntax MyList ::= List [group(mir-klist-MIRInt)]

syntax MIRInt ::= mirInt(Int)          [group(mir-int), symbol(MIRInt::Int)]
                | Int
syntax MIRBool ::= mirBool(Bool)       [group(mir-bool), symbol(MIRBool::Bool)]
                 | Bool
syntax MIRString ::= mirString(String) [group(mir-string), symbol(MIRString::String)]
                   | String

syntax LineInfo ::= lineInfo(startLine: MIRInt, startCol: MIRInt, endLine: MIRInt, endCol: MIRInt)
syntax InitMaskMaterialized ::= List {MIRInt, ""}

syntax AdtDef ::= adtDef(Int)             [group(mir-int)] // imported from crate
syntax AliasDef ::= aliasDef(Int) // imported from crate
syntax BrNamedDef ::= brNamedDef(Int) // imported from crate
syntax ClosureDef ::= closureDef(Int) // imported from crate
syntax ConstDef ::= constDef(Int) // imported from crate
syntax CoroutineDef ::= coroutineDef(Int) // imported from crate
syntax CoroutineWitnessDef ::= coroutineWitnessDef(Int) // imported from crate
syntax FnDef ::= fnDef(Int) // imported from crate
syntax ForeignDef ::= foreignDef(Int) // imported from crate
syntax ForeignModuleDef ::= foreignModuleDef(Int) // imported from crate
syntax GenericDef ::= genericDef(Int) // imported from crate
syntax ImplDef ::= implDef(Int) // imported from crate
syntax ParamDef ::= paramDef(Int) // imported from crate
syntax RegionDef ::= regionDef(Int) // imported from crate
syntax TraitDef ::= traitDef(Int) // imported from crate

syntax VariantIdx ::= variantIdx(Int) [group(mir-int)]

syntax DynKind ::= "dynKindDyn"      [group(mir-enum), symbol(DynKind::Dyn)]
                 | "dynKindDynStar"  [group(mir-enum), symbol(DynKind::DynStar)]

syntax ForeignModule ::= foreignModule(defId: ForeignModuleDef, abi: Abi) [group(mir-def-id-abi)]

syntax ForeignItemKind ::= foreignItemKindFn()               [group("mir-enum"), symbol("ForeignItemKind::Fn")]
                         | foreignItemKindStatic(StaticDef)  [group("mir-enum"), symbol("ForeignItemKind::Static")]
                         | foreignItemKindType(Ty)           [group("mir-enum"), symbol("ForeignItemKind::Type")]

syntax AdtKind ::= "adtKindEnum"
                 | "adtKindUnion"
                 | "adtKindStruct"

syntax VariantDef ::= variantDef(idx: VariantIdx, adtDef: AdtDef)

syntax FieldDef ::= fieldDef(def: DefId, name: Symbol)

syntax GenericArgKind ::= genericArgKindLifetime(Region)
                        | genericArgKindType(Ty)
                        | genericArgKindConst(TyConst)
syntax GenericArgs ::= List {GenericArgKind, ""} [group(mir-list), symbol(GenericArgs::append), terminator-symbol(GenericArgs::empty)]

syntax TermKind ::= termKindType(Ty)
                  | termKindConst(TyConst)

syntax AliasKind ::= "aliasKindProjection"
                   | "aliasKindInherent"
                   | "aliasKindOpaque"
                   | "aliasKindWeak"
syntax AliasTy ::= aliasTy(defId:AliasDef, args: GenericArgs)

syntax Abi ::= "abiRust"
             | abiC(unwind: Bool)
             | abiCdecl(unwind: Bool)
             | abiStdcall(unwind: Bool)
             | abiFastcall(unwind: Bool)
             | abiVectorcall(unwind: Bool)
             | abiThiscall(unwind: Bool)
             | abiAapcs(unwind: Bool)
             | abiWin64(unwind: Bool)
             | abiSysV64(unwind: Bool)
             | "abiPtxKernel"
             | "abiMsp430Interrupt"
             | "abiX86Interrupt"
             | "abiEfiApi"
             | "abiAvrInterrupt"
             | "abiAvrNonBlockingInterrupt"
             | "abiCCmseNonSecureCall"
             | "abiWasm"
             | abiSystem(unwind: Bool)
             | "abiRustIntrinsic"
             | "abiRustCall"
             | "abiUnadjusted"
             | "abiRustCold"
             | "abiRiscvInterruptM"
             | "abiRiscvInterruptS"

syntax BoundTyKind ::= "boundTyKindAnon"
                     | boundTyKindParam(ParamDef, MIRString)
syntax BoundRegionKind ::= "boundRegionKindBrAnon"
                         | boundRegionKindBrNamed(BrNamedDef, MIRString)
                         | "boundRegionKindBrEnv"
syntax BoundVariableKind ::= boundVariableKindTy(BoundTyKind)
                           | boundVariableKindRegion(BoundRegionKind)
                           | "boundVariableKindConst"
syntax BoundVariableKindList ::= List {BoundVariableKind, ""}

syntax FnSig ::= fnSig(inputsAndOutput: Tys, cVaradic: MIRBool, unsafety: Safety, abi: Abi)
syntax BinderForFnSig ::= binderForFnSig(value: FnSig, boundVars: BoundVariableKindList)
syntax PolyFnSig ::= BinderForFnSig
// Not needed this way. We could just do PolyFnSig ::= binderForFnSig(value: FnSig, boundVars: BoundVariableKindList).

syntax Ty ::= ty(MIRInt, TyKind) [symbol(ty)]
            | ty(Int)            [group(mir-int)]
syntax Tys ::= List {Ty, ""}

syntax Pattern ::= patternRange(start: MaybeTyConst, end: MaybeTyConst, includeEnd: MIRBool)

syntax TyConst ::= tyConst(kind: TyConstKind, id: TyConstId)
syntax TyConstId ::= tyConstId(Int)
syntax MaybeTyConst ::= someTyConst(TyConst) | "noTyConst"

syntax MirConst ::= mirConst(kind: ConstantKind, ty: Ty, id: MirConstId)
syntax MirConstId ::= mirConstId(Int)

syntax TyConstKind ::= tyConstKindParam(ParamConst)
                     | tyConstKindBound(DebruijinIndex, BoundVar)
                     | tyConstKindUnevaluated(ConstDef, GenericArgs)
                     | tyConstKindValue(Ty, Allocation)
                     | tyConstKindZSTValue(Ty)

syntax DebruijinIndex ::= debruijinIndex(Int)
syntax UniverseIndex ::= universeIndex(Int)
syntax EarlyParamRegion ::= earlyParamRegion(index: MIRInt, name: Symbol)
syntax BoundVar ::= boundVar(Int)
syntax BoundRegion ::= boundRegion(var: BoundVar, kind: BoundRegionKind)
syntax PlaceholderForBoundRegion ::= placeholderForBoundRegion(universe: UniverseIndex, bound: BoundRegion)
syntax RegionKind ::= regionKindReEarlyParam(EarlyParamRegion)
                    | regionKindReBound(DebruijinIndex, BoundRegion)
                    | "regionKindReStatic"
                    | regionKindRePlaceholder(PlaceholderForBoundRegion)
                    | "regionKindReErased"
syntax Region ::= region(kind: RegionKind)

syntax Span ::= span(Int) [group(mir-int)]

syntax ExistentialTraitRef ::= existentialTraitRef(defId: TraitDef, genericArgs: GenericArgs)
syntax ExistentialProjection ::= existentialProjection(defId: TraitDef, genericArgs: GenericArgs, term: TermKind)
syntax ExistentialPredicate ::= existentialPredicateTrait(ExistentialTraitRef)
                              | existentialPredicateProjection(ExistentialProjection)
                              | existentialPredicateAutoTrait(TraitDef)
syntax BinderForExistentialPredicate ::= binderForExistentialPredicate(value: ExistentialPredicate, boundVars: BoundVariableKindList)
syntax BindersForExistentialPredicate ::= List {BinderForExistentialPredicate, ""}

  syntax IntTy ::= "intTyIsize"  [group(mir), symbol(IntTy::Isize)]
                 | "intTyI8"     [group(mir), symbol(IntTy::I8)]
                 | "intTyI16"    [group(mir), symbol(IntTy::I16)]
                 | "intTyI32"    [group(mir), symbol(IntTy::I32)]
                 | "intTyI64"    [group(mir), symbol(IntTy::I64)]
                 | "intTyI128"   [group(mir), symbol(IntTy::I128)]

  syntax UintTy ::= "uintTyUsize" [group(mir), symbol(UintTy::Usize)]
                  | "uintTyU8"    [group(mir), symbol(UintTy::U8)]
                  | "uintTyU16"   [group(mir), symbol(UintTy::U16)]
                  | "uintTyU32"   [group(mir), symbol(UintTy::U32)]
                  | "uintTyU64"   [group(mir), symbol(UintTy::U64)]
                  | "uintTyU128"  [group(mir), symbol(UintTy::U128)]

  syntax FloatTy ::= "floatTyF16"   [group(mir), symbol(FloatTy::F16)]
                   | "floatTyF32"   [group(mir), symbol(FloatTy::F32)]
                   | "floatTyF64"   [group(mir), symbol(FloatTy::F64)]
                   | "floatTyF128"  [group(mir), symbol(FloatTy::F128)]

  syntax Movability ::= "movabilityStatic"
                      | "movabilityMovable"

  syntax RigidTy ::= "rigidTyBool" [group(mir), symbol(RigidTy::Bool)]
                   | "rigidTyChar" [group(mir), symbol(RigidTy::Char)]
                   | rigidTyInt(IntTy)  [group(mir), symbol(RigidTy::Int)]
                   | rigidTyUint(UintTy)  [group(mir), symbol(RigidTy::Uint)]
                   | rigidTyFloat(FloatTy)  [group(mir), symbol(RigidTy::Float)]
                   | rigidTyAdt(AdtDef, GenericArgs)
                   | rigidTyForeign(ForeignDef)
                   | "rigidTyStr" [group(mir), symbol(RigidTy::Str)]
                   | rigidTyArray(Ty, TyConst)
                   | rigidTyPat(Ty, Pattern)
                   | rigidTySlice(Ty)
                   | rigidTyRawPtr(Ty, Mutability)
                   | rigidTyRef(Region, Ty, Mutability)
                   | rigidTyFnDef(FnDef, GenericArgs)
                   | rigidTyFnPtr(PolyFnSig)
                   | rigidTyClosure(ClosureDef, GenericArgs)
                   | rigidTyCoroutine(CoroutineDef, GenericArgs, Movability)
                   | rigidTyDynamic(BindersForExistentialPredicate, Region, DynKind)
                   | "rigidTyNever" [group(mir), symbol(RigidTy::Never)]
                   | rigidTyTuple(Tys)
                   | rigidTyCoroutineWitness(CoroutineWitnessDef, GenericArgs)
                   | "rigidTyUnimplemented" [symbol(rigidTyUnimplemented), deprecated] // TODO: remove

syntax TyKind ::= tyKindRigidTy(RigidTy)          [group(mir), symbol(TyKind::RigidTy)]
                | tyKindAlias(AliasKind, AliasTy) [group(mir), symbol(TyKind::Alias)]
                | tyKindParam(ParamTy)            [group(mir), symbol(TyKind::Param)]
                | tyKindBound(MIRInt, BoundTy)       [group(mir), symbol(TyKind::Bound)]

syntax TypeAndMut ::= typeAndMut(ty: Ty, mutability: Mutability)

syntax ParamTy ::= paramTy(index: MIRInt, name: MIRString)
syntax BoundTy ::= boundTy(var: MIRInt, kind: BoundTyKind)

syntax Promoted ::= promoted(Int)
syntax MaybePromoted ::= somePromoted(Promoted) | "noPromoted"

syntax Align ::= align(Int) [symbol(align)]
syntax ProvenanceMapEntry ::= provenanceMapEntry(provSize: MIRInt, allocId: AllocId) [symbol(provenanceMapEntry)]
syntax ProvenanceMapEntries ::= List {ProvenanceMapEntry, ""} [symbol(provenanceMapEntries), terminator-symbol(.provenanceMapEntries)]
syntax ProvenanceMap ::= provenanceMap(ptrs: ProvenanceMapEntries) [symbol(provenanceMap)]
syntax AllocByte ::= someByte(Int) [symbol(someByte)]
                   | "noByte"      [symbol(noByte)]
syntax AllocBytes ::= List {AllocByte, ""} [symbol(maybeBytes), terminator-symbol(.maybeBytes)]
syntax Allocation ::= allocation(
                        bytes: AllocBytes,
                        provenance: ProvenanceMap,
                        align: Align,
                        mutability: Mutability) [symbol(allocation)]

syntax ConstantKind ::= constantKindTy(TyConst)
                      | constantKindAllocated(Allocation)
                      | constantKindUnevaluated(UnevaluatedConst)
                      | constantKindParam(ParamConst)
                      | "constantKindZeroSized"
                      | "constantKindNoOp" [symbol(constantKindNoOp)]
                      | constantKindFnDef(id: Int) [symbol(constantKindFnDef)]
                      | constantKindIntrinsic(name: Symbol) [symbol(constantKindIntrinsic)]

syntax ParamConst ::= paramConst(index: MIRInt, name: MIRString)

syntax UnevaluatedConst ::= unevaluatedConst(def: ConstDef, args: GenericArgs, promoted: MaybePromoted)

syntax TraitSpecializationKind ::= "traitSpecializationKindNone"
                                 | "traitSpecializationKindMarker"
                                 | "traitSpecializationKindAlwaysApplicable"

syntax Ident ::= ident(Opaque)
syntax Idents ::= List {Ident, ""}
syntax MaybeIdents ::= someIdents(Idents) | "noIdents"
syntax TraitDecl ::= traitDecl(defId: TraitDef, unsafety: Safety, parenSugar: MIRBool, hasAutoImpl: MIRBool, isMarker: MIRBool, isCoinductive: MIRBool, skipArrayDuringMethodDispatch: MIRBool, specializationKind: TraitSpecializationKind, mustImplementOneOf: MaybeIdents, implementViaObject: MIRBool, denyExplicitImpl: MIRBool)

syntax TraitRef ::= traitRef(defId: TraitDef, args: GenericArgs)

syntax GenericParamDefKind ::= "genericParamDefKindLifetime"
                             | genericParamDefKindType(hasDefault: MIRBool, synthetic: MIRBool)
                             | genericParamDefKindConst(hasDefault: Bool)
syntax GenericParamDef ::= genericParamDef(name: Symbol, defId: GenericDef, index: MIRInt, pureWrtDrop: MIRBool, kind: GenericParamDefKind)
syntax MaybeGenericDef ::= someGenericDef(GenericDef) | "noGenericDef"
syntax GenericParamDefs ::= List {GenericParamDef, ""}
syntax GenericDefAndIdxPair ::= genericDefAndIdxPair(GenericDef, MIRInt)
syntax GenericDefAndIdxPairs ::= List {GenericDefAndIdxPair, ""}
syntax MaybeSpan ::= someSpan(Span) | "noSpan"
syntax Generics ::= generics(parent: MaybeGenericDef, parentCount: MIRInt, params: GenericParamDefs, paramDefIdToIndex: GenericDefAndIdxPairs, hasSelf: MIRBool, hasLateBoundRegions: MaybeSpan, hostEffectIndex: MaybeInt)

syntax MaybeTraitDef ::= someTraitDef(TraitDef) | "noTraitDef"
syntax PredicateKindAndSpanPair ::= predicateKindAndSpanPair(predicateKind: PredicateKind, span: Span)
syntax PredicateKindAndSpanPairs ::= List {PredicateKindAndSpanPair, ""}
syntax GenericPredicates ::= genericPredicates(parent: MaybeTraitDef, predicates: PredicateKindAndSpanPairs)

syntax PredicateKind ::= predicateKindClause(ClauseKind)
                       | predicateKindObjectSafe(TraitDef)
                       | predicateKindSubType(SubtypePredicate)
                       | predicateKindCoerce(CoercePredicate)
                       | predicateKindConstEquate(TyConst, TyConst)
                       | "predicateKindAmbiguous"
                       | predicateKindAliasRelate(TermKind, TermKind, AliasRelationDirection)

syntax ClauseKind ::= clauseKindTrait(TraitPredicate)
                    | clauseKindRegionOutlives(RegionOutlivesPredicate)
                    | clauseKindTypeOutlives(TypeOutlivesPredicate)
                    | clauseKindProjection(ProjectionPredicate)
                    | clauseKindConstArgHasType(TyConst, Ty)
                    | clauseKindWellFormed(GenericArgKind)
                    | clauseKindConstEvaluatable(TyConst)

syntax TraitPredicate ::= traitPredicate(traitDef: TraitDef, polarity: PredicatePolarity)
syntax RegionOutlivesPredicate ::= regionOutlivesPredicate(Region, Region)
syntax TypeOutlivesPredicate ::= typeOutlivesPredicate(Ty, Region)
syntax ProjectionPredicate ::= projectionPredicate(projectionTy: AliasTy, term: TermKind)

syntax SubtypePredicate ::= subtypePredicate(a: Ty, b: Ty)
syntax CoercePredicate ::= coercePredicate(a: Ty, b: Ty)
syntax AliasRelationDirection ::= "aliasRelationDirectionEquate"
                                | "aliasRelationDirectionSubtype"

syntax ClosureKind ::= "closureKindFn"
                     | "closureKindFnMut"
                     | "closureKindFnOnce"

syntax ImplPolarity ::= "implPolarityPositive"
                      | "implPolarityNegative"
                      | "implPolarityReservation"
syntax PredicatePolarity ::= "predicatePolarityPositive"
                           | "predicatePolarityNegative"

endmodule
```