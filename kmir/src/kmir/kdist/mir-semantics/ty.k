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

endmodule

module TYPES
  imports ALLOC-SORTS
  imports BODY-SORTS
  imports LIB-SORTS
  imports MONO-SORTS
  imports TYPES-SORTS
  imports INT
  imports STRING

syntax LineInfo ::= lineInfo(startLine: Int, startCol: Int, endLine: Int, endCol: Int)
syntax InitMaskMaterialized ::= List {Int, ""}

syntax AdtDef ::= Int // imported from crate
syntax AliasDef ::= Int // imported from crate
syntax BrNamedDef ::= Int // imported from crate
syntax ClosureDef ::= Int // imported from crate
syntax ConstDef ::= Int // imported from crate
syntax CoroutineDef ::= Int // imported from crate
syntax CoroutineWitnessDef ::= Int // imported from crate
syntax FnDef ::= Int // imported from crate
syntax ForeignDef ::= Int // imported from crate
syntax ForeignModuleDef ::= Int // imported from crate
syntax GenericDef ::= Int // imported from crate
syntax ImplDef ::= Int // imported from crate
syntax ParamDef ::= Int // imported from crate
syntax RegionDef ::= Int // imported from crate
syntax TraitDef ::= Int // imported from crate

syntax VariantIdx ::= variantIdx(Int) [symbol(variantIdx)]

syntax DynKind ::= "dynKindDyn" | "dynKindDynStar"

syntax ForeignModule ::= foreignModule(defId: ForeignModuleDef, abi: Abi)
syntax ForeignItemKind ::= foreignItemKindFn()
                         | foreignItemKindStatic(StaticDef)
                         | foreignItemKindType(Ty)

syntax AdtKind ::= "adtKindEnum"
                 | "adtKindUnion"
                 | "adtKindStruct"

syntax VariantDef ::= variantDef(idx: VariantIdx, adtDef: AdtDef)

syntax FieldDef ::= fieldDef(def: DefId, name: Symbol)

syntax GenericArgKind ::= genericArgKindLifetime(Region)
                        | genericArgKindType(Ty)
                        | genericArgKindConst(TyConst)
syntax GenericArgs ::= List {GenericArgKind, ""} [symbol(genericArgs), terminator-symbol(.genericArgs)]

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
                     | boundTyKindParam(ParamDef, String)
syntax BoundRegionKind ::= "boundRegionKindBrAnon"
                         | boundRegionKindBrNamed(BrNamedDef, String)
                         | "boundRegionKindBrEnv"
syntax BoundVariableKind ::= boundVariableKindTy(BoundTyKind)
                           | boundVariableKindRegion(BoundRegionKind)
                           | "boundVariableKindConst"
syntax BoundVariableKindList ::= List {BoundVariableKind, ""}

syntax FnSig ::= fnSig(inputsAndOutput: Tys, cVaradic: Bool, unsafety: Safety, abi: Abi)
syntax BinderForFnSig ::= binderForFnSig(value: FnSig, boundVars: BoundVariableKindList)
syntax PolyFnSig ::= BinderForFnSig
// Not needed this way. We could just do PolyFnSig ::= binderForFnSig(value: FnSig, boundVars: BoundVariableKindList).

syntax Ty ::= ty(Int, TyKind) [symbol(ty)]
syntax Tys ::= List {Ty, ""}

syntax Pattern ::= patternRange(start: MaybeTyConst, end: MaybeTyConst, includeEnd: Bool)

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
syntax EarlyParamRegion ::= earlyParamRegion(index: Int, name: Symbol)
syntax BoundVar ::= boundVar(Int)
syntax BoundRegion ::= boundRegion(var: BoundVar, kind: BoundRegionKind)
syntax PlaceholderForBoundRegion ::= placeholderForBoundRegion(universe: UniverseIndex, bound: BoundRegion)
syntax RegionKind ::= regionKindReEarlyParam(EarlyParamRegion)
                    | regionKindReBound(DebruijinIndex, BoundRegion)
                    | "regionKindReStatic"
                    | regionKindRePlaceholder(PlaceholderForBoundRegion)
                    | "regionKindReErased"
syntax Region ::= region(kind: RegionKind)

syntax Span ::= span(Int)

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
                | tyKindBound(Int, BoundTy)       [group(mir), symbol(TyKind::Bound)]

syntax TypeAndMut ::= typeAndMut(ty: Ty, mutability: Mutability)

syntax ParamTy ::= paramTy(index: Int, name: String)
syntax BoundTy ::= boundTy(var: Int, kind: BoundTyKind)

syntax Promoted ::= promoted(Int)
syntax MaybePromoted ::= somePromoted(Promoted) | "noPromoted"

syntax Align ::= align(Int) [symbol(align)]
syntax ProvenanceMapEntry ::= provenanceMapEntry(size: Int, allocId: AllocId) [symbol(provenanceMapEntry)]
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

syntax ParamConst ::= paramConst(index: Int, name: String)

syntax UnevaluatedConst ::= unevaluatedConst(def: ConstDef, args: GenericArgs, promoted: MaybePromoted)

syntax TraitSpecializationKind ::= "traitSpecializationKindNone"
                                 | "traitSpecializationKindMarker"
                                 | "traitSpecializationKindAlwaysApplicable"

syntax Ident ::= ident(Opaque)
syntax Idents ::= List {Ident, ""}
syntax MaybeIdents ::= someIdents(Idents) | "noIdents"
syntax TraitDecl ::= traitDecl(defId: TraitDef, unsafety: Safety, parenSugar: Bool, hasAutoImpl: Bool, isMarker: Bool, isCoinductive: Bool, skipArrayDuringMethodDispatch: Bool, specializationKind: TraitSpecializationKind, mustImplementOneOf: MaybeIdents, implementViaObject: Bool, denyExplicitImpl: Bool)

syntax TraitRef ::= traitRef(defId: TraitDef, args: GenericArgs)

syntax GenericParamDefKind ::= "genericParamDefKindLifetime"
                             | genericParamDefKindType(hasDefault: Bool, synthetic: Bool)
                             | genericParamDefKindConst(hasDefault: Bool)
syntax GenericParamDef ::= genericParamDef(name: Symbol, defId: GenericDef, index: Int, pureWrtDrop: Bool, kind: GenericParamDefKind)
syntax MaybeGenericDef ::= someGenericDef(GenericDef) | "noGenericDef"
syntax GenericParamDefs ::= List {GenericParamDef, ""}
syntax GenericDefAndIdxPair ::= genericDefAndIdxPair(GenericDef, Int)
syntax GenericDefAndIdxPairs ::= List {GenericDefAndIdxPair, ""}
syntax MaybeSpan ::= someSpan(Span) | "noSpan"
syntax Generics ::= generics(parent: MaybeGenericDef, parentCount: Int, params: GenericParamDefs, paramDefIdToIndex: GenericDefAndIdxPairs, hasSelf: Bool, hasLateBoundRegions: MaybeSpan, hostEffectIndex: MaybeInt)

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
