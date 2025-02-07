```k
requires "alloc.md"
requires "body.md"
requires "lib.md"
requires "mono.md"

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
  imports BYTES
  imports LIST

syntax TestSort2 ::= testSort2(MIRInt, MyList)     [group(mir), symbol(testSort2)]
syntax MyList ::= List [group(mir-klist-MIRInt)]

syntax MIRInt ::= mirInt(Int)          [group(mir-int), symbol(MIRInt::Int)]
                | Int
syntax MIRBool ::= mirBool(Bool)       [group(mir-bool), symbol(MIRBool::Bool)]
                 | Bool
syntax MIRString ::= mirString(String) [group(mir-string), symbol(MIRString::String)]
                   | String
syntax MIRBytes ::= mirBytes(Bytes)    [group(mir-bytes), symbol(MIRBytes::Bytes)]
                  | Bytes

syntax LineInfo ::= lineInfo(startLine: MIRInt, startCol: MIRInt, endLine: MIRInt, endCol: MIRInt)
syntax InitMaskMaterialized ::= List {MIRInt, ""}

syntax AdtDef ::= adtDef(Int)                           [group(mir-int)] // imported from crate
syntax AliasDef ::= aliasDef(Int)                       [group(mir-int)] // imported from crate
syntax BrNamedDef ::= brNamedDef(Int)                   [group(mir-int)] // imported from crate
syntax ClosureDef ::= closureDef(Int)                   [group(mir-int)] // imported from crate
syntax ConstDef ::= constDef(Int)                       [group(mir-int)] // imported from crate
syntax CoroutineDef ::= coroutineDef(Int)               [group(mir-int)] // imported from crate
syntax CoroutineWitnessDef ::= coroutineWitnessDef(Int) [group(mir-int)] // imported from crate
syntax FnDef ::= fnDef(Int)                             [group(mir-int)] // imported from crate
syntax ForeignDef ::= foreignDef(Int)                   [group(mir-int)] // imported from crate
syntax ForeignModuleDef ::= foreignModuleDef(Int)       [group(mir-int)] // imported from crate
syntax GenericDef ::= genericDef(Int)                   [group(mir-int)] // imported from crate
syntax ImplDef ::= implDef(Int)                         [group(mir-int)] // imported from crate
syntax ParamDef ::= paramDef(Int)                       [group(mir-int)] // imported from crate
syntax RegionDef ::= regionDef(Int)                     [group(mir-int)] // imported from crate
syntax TraitDef ::= traitDef(Int)                       [group(mir-int)] // imported from crate

syntax VariantIdx ::= variantIdx(Int) [group(mir-int)]

syntax DynKind ::= "dynKindDyn"      [group(mir-enum), symbol(DynKind::Dyn)]
                 | "dynKindDynStar"  [group(mir-enum), symbol(DynKind::DynStar)]

syntax ForeignModule ::= foreignModule(defId: ForeignModuleDef, abi: Abi) [group(mir---def-id--abi)]

syntax ForeignItemKind ::= foreignItemKindFn()               [group(mir-enum), symbol(ForeignItemKind::Fn)]
                         | foreignItemKindStatic(StaticDef)  [group(mir-enum), symbol(ForeignItemKind::Static)]
                         | foreignItemKindType(Ty)           [group(mir-enum), symbol(ForeignItemKind::Type)]

syntax AdtKind ::= "adtKindEnum"   [group(mir-enum), symbol(AdtKind::Enum)]
                 | "adtKindUnion"  [group(mir-enum), symbol(AdtKind::Union)]
                 | "adtKindStruct" [group(mir-enum), symbol(AdtKind::Struct)]

syntax VariantDef ::= variantDef(idx: VariantIdx, adtDef: AdtDef) [group(mir---idx--adtDef)]

syntax FieldDef ::= fieldDef(def: DefId, name: Symbol) [group(mir---def--name)]

syntax GenericArg ::= genericArgKindLifetime(Region) [group(mir-enum), symbol(GenericArg::Lifetime)]
                    | genericArgKindType(Ty)         [group(mir-enum), symbol(GenericArg::Type)]
                    | genericArgKindConst(TyConst)   [group(mir-enum), symbol(GenericArg::Const)]

syntax GenericArgs ::= List {GenericArg, ""} [group(mir-list), symbol(GenericArgs::append), terminator-symbol(GenericArgs::empty)]

syntax TermKind ::= termKindType(Ty)       [group(mir-enum), symbol(TermKind::Type)]
                  | termKindConst(TyConst) [group(mir-enum), symbol(TermKind::Const)]

syntax AliasKind ::= "aliasKindProjection" [group(mir-enum), symbol(AliasKind::Projection)]
                   | "aliasKindInherent"   [group(mir-enum), symbol(AliasKind::Inherent)]
                   | "aliasKindOpaque"     [group(mir-enum), symbol(AliasKind::Opaque)]
                   | "aliasKindWeak"       [group(mir-enum), symbol(AliasKind::Weak)]

syntax AliasTy ::= aliasTy(defId:AliasDef, args: GenericArgs) [group(mir---defId--args)]

syntax Abi ::= "abiRust"                       [group(mir-enum), symbol(Abi::Rust)]
             | abiC(unwind: MIRBool)           [group(mir-enum), symbol(Abi::C)]
             | abiCdecl(unwind: MIRBool)       [group(mir-enum), symbol(Abi::Cdecl)]
             | abiStdcall(unwind: MIRBool)     [group(mir-enum), symbol(Abi::Stdcall)]
             | abiFastcall(unwind: MIRBool)    [group(mir-enum), symbol(Abi::Fastcall)]
             | abiVectorcall(unwind: MIRBool)  [group(mir-enum), symbol(Abi::Vectorcall)]
             | abiThiscall(unwind: MIRBool)    [group(mir-enum), symbol(Abi::Thiscall)]
             | abiAapcs(unwind: MIRBool)       [group(mir-enum), symbol(Abi::Aapcs)]
             | abiWin64(unwind: MIRBool)       [group(mir-enum), symbol(Abi::Win64)]
             | abiSysV64(unwind: MIRBool)      [group(mir-enum), symbol(Abi::SysV64)]
             | "abiPtxKernel"                  [group(mir-enum), symbol(Abi::PtxKernel)]
             | "abiMsp430Interrupt"            [group(mir-enum), symbol(Abi::Msp430Interrupt)]
             | "abiX86Interrupt"               [group(mir-enum), symbol(Abi::X86Interrupt)]
             | "abiEfiApi"                     [group(mir-enum), symbol(Abi::EfiApi)]
             | "abiAvrInterrupt"               [group(mir-enum), symbol(Abi::AvrInterrupt)]
             | "abiAvrNonBlockingInterrupt"    [group(mir-enum), symbol(Abi::AvrNonBlockingInterrupt)]
             | "abiCCmseNonSecureCall"         [group(mir-enum), symbol(Abi::CCmseNonSecureCall)]
             | "abiWasm"                       [group(mir-enum), symbol(Abi::Wasm)]
             | abiSystem(unwind: MIRBool)      [group(mir-enum), symbol(Abi::System)]
             | "abiRustIntrinsic"              [group(mir-enum), symbol(Abi::RustIntrinsic)]
             | "abiRustCall"                   [group(mir-enum), symbol(Abi::RustCall)]
             | "abiUnadjusted"                 [group(mir-enum), symbol(Abi::Unadjusted)]
             | "abiRustCold"                   [group(mir-enum), symbol(Abi::RustCold)]
             | "abiRiscvInterruptM"            [group(mir-enum), symbol(Abi::RiscvInterruptM)]
             | "abiRiscvInterruptS"            [group(mir-enum), symbol(Abi::RiscvInterruptS)]

syntax BoundTyKind ::= "boundTyKindAnon"                     [group(mir-enum), symbol(BoundTyKind::Anon)]
                     | boundTyKindParam(ParamDef, MIRString) [group(mir-enum), symbol(BoundTyKind::Param)]
syntax BoundRegionKind ::= "boundRegionKindBrAnon"                       [group(mir-enum), symbol(BoundRegionKind::BrAnon)]
                         | boundRegionKindBrNamed(BrNamedDef, MIRString) [group(mir-enum), symbol(BoundRegionKind::BrNamed)]
                         | "boundRegionKindBrEnv"                        [group(mir-enum), symbol(BoundRegionKind::BrEnv)]
syntax BoundVariableKind ::= boundVariableKindTy(BoundTyKind)            [group(mir-enum), symbol(BoundVariableKind::Ty)]
                           | boundVariableKindRegion(BoundRegionKind)    [group(mir-enum), symbol(BoundVariableKind::Region)]
                           | "boundVariableKindConst"                    [group(mir-enum), symbol(BoundVariableKind::Const)]
syntax BoundVariableKindList ::= List {BoundVariableKind, ""}
                                 [group(mir-list), symbol(BoundVariableKindList::append), terminator-symbol(BoundVariableKindList::empty)]

syntax FnSig ::= fnSig(inputsAndOutput: Tys, cVaradic: MIRBool, unsafety: Safety, abi: Abi) [group(mir---inputsAndOutput--cVariadic--unsafety--abi)]
syntax BinderForFnSig ::= binderForFnSig(value: FnSig, boundVars: BoundVariableKindList)    [group(mir---value--boundVars)]
syntax PolyFnSig ::= BinderForFnSig                                                         [group(mir)]
// Not needed this way. We could just do PolyFnSig ::= binderForFnSig(value: FnSig, boundVars: BoundVariableKindList).

syntax Ty ::= ty(Int)            [group(mir-int)]

syntax Tys ::= List {Ty, ""}     [group(mir-list), symbol(Tys::append), terminator-symbol(Tys::empty)]

syntax Pattern ::= patternRange(start: MaybeTyConst, end: MaybeTyConst, includeEnd: MIRBool) [group(mir---start--end--includeEnd)]

syntax TyConst ::= tyConst(kind: TyConstKind, id: TyConstId)  [group(mir---kind--id)]
syntax TyConstId ::= tyConstId(Int)                           [group(mir-int)]
syntax MaybeTyConst ::= someTyConst(TyConst)  [group(mir-option)]
                      | "noTyConst"           [group(mir-option)]

syntax MirConst ::= mirConst(kind: ConstantKind, ty: Ty, id: MirConstId) [group(mir---kind--ty--id)]
syntax MirConstId ::= mirConstId(Int) [group(mir-int)]

syntax TyConstKind ::= tyConstKindParam(ParamConst)                   [group(mir-enum), symbol(TyConstKind::Param)]
                     | tyConstKindBound(DebruijinIndex, BoundVar)     [group(mir-enum), symbol(TyConstKind::Bound)]
                     | tyConstKindUnevaluated(ConstDef, GenericArgs)  [group(mir-enum), symbol(TyConstKind::Unevaluated)]
                     | tyConstKindValue(Ty, Allocation)               [group(mir-enum), symbol(TyConstKind::Value)]
                     | tyConstKindZSTValue(Ty)                        [group(mir-enum), symbol(TyConstKind::ZSTValue)]

syntax DebruijinIndex ::= debruijinIndex(Int)  [group(mir-int)]
syntax UniverseIndex ::= universeIndex(Int)    [group(mir-int)]
syntax BoundVar ::= boundVar(Int)              [group(mir-int)]
syntax EarlyParamRegion ::= earlyParamRegion(index: MIRInt, name: Symbol) [group(mir---index--name)]
syntax BoundRegion ::= boundRegion(var: BoundVar, kind: BoundRegionKind)  [group(mir---var--kind)]
syntax PlaceholderForBoundRegion ::= placeholderForBoundRegion(universe: UniverseIndex, bound: BoundRegion) [group(mir---universe--bound)]

syntax RegionKind ::= regionKindReEarlyParam(EarlyParamRegion)           [group(mir-enum), symbol(RegionKind::ReEarlyParam)]
                    | regionKindReBound(DebruijinIndex, BoundRegion)     [group(mir-enum), symbol(RegionKind::ReBound)]
                    | "regionKindReStatic"                               [group(mir-enum), symbol(RegionKind::ReStatic)]
                    | regionKindRePlaceholder(PlaceholderForBoundRegion) [group(mir-enum), symbol(RegionKind::RePlaceholder)]
                    | "regionKindReErased"                               [group(mir-enum), symbol(RegionKind::ReErased)]
syntax Region ::= region(kind: RegionKind) [group(mir---kind)]

syntax Span ::= span(Int) [group(mir-int)]

syntax ExistentialTraitRef ::= existentialTraitRef(defId: TraitDef, genericArgs: GenericArgs)                     [group(mir---defId--genericArgs)]

syntax ExistentialProjection ::= existentialProjection(defId: TraitDef, genericArgs: GenericArgs, term: TermKind) [group(mir---defId--genericArgs--term)]

syntax ExistentialPredicate ::= existentialPredicateTrait(ExistentialTraitRef)        [group(mir-enum), symbol(ExistentialPredicate::Trait)]
                              | existentialPredicateProjection(ExistentialProjection) [group(mir-enum), symbol(ExistentialPredicate::Projection)]
                              | existentialPredicateAutoTrait(TraitDef)               [group(mir-enum), symbol(ExistentialPredicate::AutoTrait)]

syntax ExistentialPredicateBinder ::= existentialPredicateBinder(value: ExistentialPredicate, boundVars: BoundVariableKindList)
                                         [group(mir---value--boundVars)]
syntax ExistentialPredicateBinders ::= List {ExistentialPredicateBinder, ""}
                                       [group(mir-list), symbol(ExistentialPredicateBinders::append), terminator-symbol(ExistentialPredicateBinders::empty)]

  syntax IntTy ::= "intTyIsize"  [group(mir-enum), symbol(IntTy::Isize)]
                 | "intTyI8"     [group(mir-enum), symbol(IntTy::I8)]
                 | "intTyI16"    [group(mir-enum), symbol(IntTy::I16)]
                 | "intTyI32"    [group(mir-enum), symbol(IntTy::I32)]
                 | "intTyI64"    [group(mir-enum), symbol(IntTy::I64)]
                 | "intTyI128"   [group(mir-enum), symbol(IntTy::I128)]

  syntax UintTy ::= "uintTyUsize" [group(mir-enum), symbol(UintTy::Usize)]
                  | "uintTyU8"    [group(mir-enum), symbol(UintTy::U8)]
                  | "uintTyU16"   [group(mir-enum), symbol(UintTy::U16)]
                  | "uintTyU32"   [group(mir-enum), symbol(UintTy::U32)]
                  | "uintTyU64"   [group(mir-enum), symbol(UintTy::U64)]
                  | "uintTyU128"  [group(mir-enum), symbol(UintTy::U128)]

  syntax FloatTy ::= "floatTyF16"   [group(mir-enum), symbol(FloatTy::F16)]
                   | "floatTyF32"   [group(mir-enum), symbol(FloatTy::F32)]
                   | "floatTyF64"   [group(mir-enum), symbol(FloatTy::F64)]
                   | "floatTyF128"  [group(mir-enum), symbol(FloatTy::F128)]

  syntax Movability ::= "movabilityStatic"  [group(mir-enum), symbol(Movability::Static)]
                      | "movabilityMovable" [group(mir-enum), symbol(Movability::Movable)]

  syntax RigidTy ::= "rigidTyBool"                                                [group(mir-enum), symbol(RigidTy::Bool)]
                   | "rigidTyChar"                                                [group(mir-enum), symbol(RigidTy::Char)]
                   | rigidTyInt(IntTy)                                            [group(mir-enum), symbol(RigidTy::Int)]
                   | rigidTyUint(UintTy)                                          [group(mir-enum), symbol(RigidTy::Uint)]
                   | rigidTyFloat(FloatTy)                                        [group(mir-enum), symbol(RigidTy::Float)]
                   | rigidTyAdt(AdtDef, GenericArgs)                              [group(mir-enum), symbol(RigidTy::Adt)]
                   | rigidTyForeign(ForeignDef)                                   [group(mir-enum), symbol(RigidTy::Foreign)]
                   | "rigidTyStr"                                                 [group(mir-enum), symbol(RigidTy::Str)]
                   | rigidTyArray(Ty, TyConst)                                    [group(mir-enum), symbol(RigidTy::Array)]
                   | rigidTyPat(Ty, Pattern)                                      [group(mir-enum), symbol(RigidTy::Pat)]
                   | rigidTySlice(Ty)                                             [group(mir-enum), symbol(RigidTy::Slice)]
                   | rigidTyRawPtr(Ty, Mutability)                                [group(mir-enum), symbol(RigidTy::RawPtr)]
                   | rigidTyRef(Region, Ty, Mutability)                           [group(mir-enum), symbol(RigidTy::Ref)]
                   | rigidTyFnDef(FnDef, GenericArgs)                             [group(mir-enum), symbol(RigidTy::FnDef)]
                   | rigidTyFnPtr(PolyFnSig)                                      [group(mir-enum), symbol(RigidTy::FnPtr)]
                   | rigidTyClosure(ClosureDef, GenericArgs)                      [group(mir-enum), symbol(RigidTy::Closure)]
                   | rigidTyCoroutine(CoroutineDef, GenericArgs, Movability)      [group(mir-enum), symbol(RigidTy::Coroutine)]
                   | rigidTyDynamic(ExistentialPredicateBinders, Region, DynKind) [group(mir-enum), symbol(RigidTy::Dynamic)]
                   | "rigidTyNever"                                               [group(mir-enum), symbol(RigidTy::Never)]
                   | rigidTyTuple(Tys)                                            [group(mir-enum), symbol(RigidTy::Tuple)]
                   | rigidTyCoroutineWitness(CoroutineWitnessDef, GenericArgs)    [group(mir-enum), symbol(RigidTy::CoroutineWitness)]
                   | "rigidTyUnimplemented"                                       [group(mir-enum), symbol(RigidTy::Unimplemented), deprecated] // TODO: remove

syntax TyKind ::= tyKindRigidTy(RigidTy)          [group(mir-enum), symbol(TyKind::RigidTy)]
                | tyKindAlias(AliasKind, AliasTy) [group(mir-enum), symbol(TyKind::Alias)]
                | tyKindParam(ParamTy)            [group(mir-enum), symbol(TyKind::Param)]
                | tyKindBound(MIRInt, BoundTy)    [group(mir-enum), symbol(TyKind::Bound)]

syntax TypeAndMut ::= typeAndMut(ty: Ty, mutability: Mutability) [group(mir---ty--mutability)]

syntax ParamTy ::= paramTy(index: MIRInt, name: MIRString) [group(mir---index--name)]
syntax BoundTy ::= boundTy(var: MIRInt, kind: BoundTyKind) [group(mir---var--kind)]

// syntax Promoted ::= promoted(Int) [group(mir-int)]
syntax MaybePromoted ::= promoted(Int) [group(mir-option-int)]
                       | "notPromoted" [group(mir-option)]

syntax Align ::= align(Int) [group(mir-int), symbol(align)]

// FIXME provSize and allocId are in a _list_ in json
syntax ProvenanceMapEntry ::= // provenanceMapEntry(provSize: MIRInt, allocId: AllocId) [group(mir), symbol(provenanceMapEntry)]
                              List [group(mir-klist-MIRInt)]

syntax ProvenanceMapEntries ::= List {ProvenanceMapEntry, ""}
                                [group(mir-list), symbol(ProvenanceMapEntries::append), terminator-symbol(ProvenanceMapEntries::empty)]

syntax ProvenanceMap ::= provenanceMap(ptrs: ProvenanceMapEntries) [group(mir---ptrs), symbol(provenanceMap)]

syntax Allocation ::= allocation(
                        bytes: MIRBytes,
                        provenance: ProvenanceMap,
                        align: Align,
                        mutability: Mutability)
                      [group(mir---bytes--provenance--align--mutability), symbol(allocation)]

syntax ConstantKind ::= constantKindTy(TyConst)                   [group(mir-enum), symbol(ConstantKind::Ty)]
                      | constantKindAllocated(Allocation)         [group(mir-enum), symbol(ConstantKind::Allocated)]
                      | constantKindUnevaluated(UnevaluatedConst) [group(mir-enum), symbol(ConstantKind::Unevaluated)]
                      | constantKindParam(ParamConst)             [group(mir-enum), symbol(ConstantKind::Param)]
                      | "constantKindZeroSized"                   [group(mir-enum), symbol(ConstantKind::ZeroSized)]

syntax ParamConst ::= paramConst(index: MIRInt, name: MIRString)  [group(mir---index--name)]

syntax UnevaluatedConst ::= unevaluatedConst(def: ConstDef, args: GenericArgs, promoted: MaybePromoted)
                            [group(mir---def--args--promoted)]

syntax TraitSpecializationKind ::= "traitSpecializationKindNone"             [group(mir-enum), symbol(TraitSpecializationKind::None)]
                                 | "traitSpecializationKindMarker"           [group(mir-enum), symbol(TraitSpecializationKind::Marker)]
                                 | "traitSpecializationKindAlwaysApplicable" [group(mir-enum), symbol(TraitSpecializationKind::AlwaysApplicable)]

syntax Ident ::= ident(Opaque)     [group(mir)]
syntax Idents ::= List {Ident, ""} [group(mir-list), symbol(Idents::append), terminator-symbol(Idents::empty)]
syntax MaybeIdents ::= someIdents(Idents) [group(mir-option)]
                     | "noIdents"         [group(mir-option)]
syntax TraitDecl ::= traitDecl(
                       defId: TraitDef
                     , unsafety: Safety
                     , parenSugar: MIRBool
                     , hasAutoImpl: MIRBool
                     , isMarker: MIRBool
                     , isCoinductive: MIRBool
                     , skipArrayDuringMethodDispatch: MIRBool
                     , specializationKind: TraitSpecializationKind
                     , mustImplementOneOf: MaybeIdents
                     , implementViaObject: MIRBool
                     , denyExplicitImpl: MIRBool)
                     [group(mir---defId--unsafety--parenSugar--hasAutoImpl--isMarker--isCoinductive--skipArrayDuringMethodDispatch--specializationKind--mustImplementOneOf--implementViaObject--denyExplicitImpl)]

syntax TraitRef ::= traitRef(defId: TraitDef, args: GenericArgs) [group(mir---defId--args)]

syntax GenericParamDefKind ::= "genericParamDefKindLifetime"                                    [group(mir-enum), symbol(GenericParamDefKind::Lifetime)]
                             | genericParamDefKindType(hasDefault: MIRBool, synthetic: MIRBool) [group(mir-enum), symbol(GenericParamDefKind::Type)]
                             | genericParamDefKindConst(hasDefault: Bool)                       [group(mir-enum), symbol(GenericParamDefKind::Const)]
syntax GenericParamDef ::= genericParamDef(name: Symbol, defId: GenericDef, index: MIRInt, pureWrtDrop: MIRBool, kind: GenericParamDefKind)
                           [group(mir---name--defId--index--purtWrtDrop--kind)]
syntax MaybeGenericDef ::= someGenericDef(GenericDef)  [group(mir-option)]
                         | "noGenericDef"              [group(mir-option)]
syntax GenericParamDefs ::= List {GenericParamDef, ""} [group(mir-list), symbol(GenericParamDefs::append), terminator-symbol(GenericParamDefs::empty)]

syntax GenericDefAndIdxPair ::= genericDefAndIdxPair(GenericDef, MIRInt) [group(mir)]
syntax GenericDefAndIdxPairs ::= List {GenericDefAndIdxPair, ""}
                                 [group(mir-list), symbol(GenericDefAndIdxPairs::append), terminator-symbol(GenericDefAndIdxPairs::empty)]

syntax MaybeSpan ::= someSpan(Span) [group(mir-option)]
                   | "noSpan"       [group(mir-option)]
syntax Generics ::= generics(
                      parent: MaybeGenericDef
                    , parentCount: MIRInt
                    , params: GenericParamDefs
                    , paramDefIdToIndex: GenericDefAndIdxPairs
                    , hasSelf: MIRBool
                    , hasLateBoundRegions: MaybeSpan
                    , hostEffectIndex: MaybeInt)
                    [group(mir---parent--parentCount--params--paramDefIdToIndex--hasSelf--hasLateBoundRegions--hostEffectIndex)]

syntax MaybeTraitDef ::= someTraitDef(TraitDef) [group(mir-option)]
                       | "noTraitDef"           [group(mir-option)]

syntax PredicateKindAndSpanPair ::= predicateKindAndSpanPair(predicateKind: PredicateKind, span: Span)
                                                                         [group(mir---predicateKind--span)]
syntax PredicateKindAndSpanPairs ::= List {PredicateKindAndSpanPair, ""}
                                     [group(mir-list), symbol(PredicateKindAndSpanPairs::append), terminator-symbol(PredicateKindAndSpanPairs::empty)]

syntax GenericPredicates ::= genericPredicates(parent: MaybeTraitDef, predicates: PredicateKindAndSpanPairs)
                             [group(mir---parent--predicates)]

syntax PredicateKind ::= predicateKindClause(ClauseKind)                                      [group(mir-enum), symbol(PredicateKind::Clause)]
                       | predicateKindObjectSafe(TraitDef)                                    [group(mir-enum), symbol(PredicateKind::ObjectSafe)]
                       | predicateKindSubType(SubtypePredicate)                               [group(mir-enum), symbol(PredicateKind::SubType)]
                       | predicateKindCoerce(CoercePredicate)                                 [group(mir-enum), symbol(PredicateKind::Coerce)]
                       | predicateKindConstEquate(TyConst, TyConst)                           [group(mir-enum), symbol(PredicateKind::ConstEquate)]
                       | "predicateKindAmbiguous"                                             [group(mir-enum), symbol(PredicateKind::Ambiguous)]
                       | predicateKindAliasRelate(TermKind, TermKind, AliasRelationDirection) [group(mir-enum), symbol(PredicateKind::AliasRelate)]

syntax ClauseKind ::= clauseKindTrait(TraitPredicate)                   [group(mir-enum), symbol(ClauseKind::Trait)]
                    | clauseKindRegionOutlives(RegionOutlivesPredicate) [group(mir-enum), symbol(ClauseKind::RegionOutlives)]
                    | clauseKindTypeOutlives(TypeOutlivesPredicate)     [group(mir-enum), symbol(ClauseKind::TypeOutlives)]
                    | clauseKindProjection(ProjectionPredicate)         [group(mir-enum), symbol(ClauseKind::Projection)]
                    | clauseKindConstArgHasType(TyConst, Ty)            [group(mir-enum), symbol(ClauseKind::ConstArgHasType)]
                    | clauseKindWellFormed(GenericArg)                  [group(mir-enum), symbol(ClauseKind::WellFormed)]
                    | clauseKindConstEvaluatable(TyConst)               [group(mir-enum), symbol(ClauseKind::ConstEvaluatable)]

syntax TraitPredicate ::= traitPredicate(traitDef: TraitDef, polarity: PredicatePolarity) [group(mir---traitDef--polarity)]
syntax RegionOutlivesPredicate ::= regionOutlivesPredicate(Region, Region)                [group(mir)] // FIXME field names??
syntax TypeOutlivesPredicate ::= typeOutlivesPredicate(Ty, Region)                        [group(mir)] // FIXME field names??
syntax ProjectionPredicate ::= projectionPredicate(projectionTy: AliasTy, term: TermKind) [group(mir---projectionTy--term)]

syntax SubtypePredicate ::= subtypePredicate(a: Ty, b: Ty) [group(mir---a--b)]
syntax CoercePredicate ::= coercePredicate(a: Ty, b: Ty)   [group(mir---a--b)]
syntax AliasRelationDirection ::= "aliasRelationDirectionEquate"  [group(mir-enum), symbol(AliasRelationDirection::Equate)]
                                | "aliasRelationDirectionSubtype" [group(mir-enum), symbol(AliasRelationDirection::Subtype)]

syntax ClosureKind ::= "closureKindFn"     [group(mir-enum), symbol(ClosureKind::Fn)]
                     | "closureKindFnMut"  [group(mir-enum), symbol(ClosureKind::FnMut)]
                     | "closureKindFnOnce" [group(mir-enum), symbol(ClosureKind::FnOnce)]

syntax ImplPolarity ::= "implPolarityPositive"    [group(mir-enum), symbol(ImplPolarity::Positive)]
                      | "implPolarityNegative"    [group(mir-enum), symbol(ImplPolarity::Negative)]
                      | "implPolarityReservation" [group(mir-enum), symbol(ImplPolarity::Reservation)]
syntax PredicatePolarity ::= "predicatePolarityPositive" [group(mir-enum), symbol(PredicatePolarity::Positive)]
                           | "predicatePolarityNegative" [group(mir-enum), symbol(PredicatePolarity::Negative)]

endmodule
```

### Index

#### Internal MIR
- [AdtDef](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/adt.rs#L172-L174)
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
- [TraitDef](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/trait_def.rs#L14-L70)
- [VariantIdx]()
- [DynKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/ty_kind.rs#L19-L32)
- [ForeignModule](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_session/src/cstore.rs#L146-L151)
- [DefKind -> ForeignItemKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_hir/src/def.rs#L52)
- [AdtKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/adt.rs#L203-L208)
- [VariantDef](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/mod.rs#L1206-L1223)
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
- [PolyFnSig](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/sty.rs#L284)
- [Ty](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/mod.rs#L472-L476)
- [Pattern](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/pattern.rs#L7-L9)
- [TyConst from Const](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/consts.rs#L29-L32)
- TyConstId - Not present
- [MirConst from Const](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/consts.rs#L29-L32)
- MirConstId - Not present
- [TyConstKind from ConstKind alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/consts.rs#L23) [TyConstKind from ConstKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/const_kind.rs#L12-L44)
- [DebruijinIndex](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_type_ir/src/lib.rs#L80-L128)
- [UniverseIndex](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_type_ir/src/lib.rs#L287-L329)
- [EarlyParamRegion](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/region.rs#L331-L336)
- [BoundVar](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_type_ir/src/lib.rs#L377-L384)
- [BoundRegion](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_middle/src/ty/region.rs#L382-L387)
- [Placeholder](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_middle/src/ty/mod.rs#L857-L866) [PlaceholderRegion alias - PlaceholderForBoundRegion](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_middle/src/ty/mod.rs#L892)
- [RegionKind alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/region.rs#L15) [RegionKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/region_kind.rs#L33-L190)
- [Region](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/region.rs#L17-L20)
- [Span](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_span/src/span_encoding.rs#L12-L88)
- [ExistentialTraitRef alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/predicate.rs#L18) [ExistentialTraitRef](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/predicate.rs#L289-L309)
- [ExistentialProjection](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L94-L105)
- [ExistentialPredicate alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/predicate.rs#L17) [ExistentialPredicate](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/predicate.rs#L231-L249)
- [Binder - BinderForExistentialPredicate alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/sty.rs#L41) [Binder - BinderForExistentialPredicate](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/binder.rs#L18-L40)
- [IntTy](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/cast.rs#L9-L17)
- [UintTy ast](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_ast/src/ast.rs#L2001-L2010) [UintTy ir](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/ty_kind.rs#L633-L642)
- [FloatTy ast](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_ast/src/ast.rs#L1937-L1944) [FloatTy ir](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/ty_kind.rs#L691-L698)
- [Movability](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_ast_ir/src/lib.rs#L10-L19)
- [RigidTy -> TyKind alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/sty.rs#L37) [RigidTy -> TyKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/ty_kind.rs#L62-L250)
- [TyKind alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/sty.rs#L37) [TyKind ir](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/ty_kind.rs#L62-L250)
- [TypeAndMut alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/sty.rs#L38) [TypeAndMut ir](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/ty_kind.rs#L942-L956)
- [ParamTy](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/sty.rs#L287-L292)
- [BoundTy](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/sty.rs#L344-L349)
- [Promoted](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/mod.rs#L1702-L1708)
- [Align](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_abi/src/lib.rs#L645-L650)
- [ProvenanceMap](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/interpret/allocation/provenance_map.rs#L13-L24)
- [Bytes -> AllocByte and AllocBytes](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/interpret/allocation.rs#L76C70-L76C86)
- [Allocation](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/interpret/allocation.rs#L67-L96)
- [ConstKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/const_kind.rs#L12-L44)
- [ParamConst](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/sty.rs#L321-L326)
- [UnevaluatedConst ty alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/consts.rs#L24) [UnevaluatedConst ty ir](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/const_kind.rs#L90-L104) [UnevaluatedConst mir](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/consts.rs#L488-L495)
- [TraitSpecializationKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/trait_def.rs#L72-L88)
- Ident - not present
- [TraitDecl -> TraitDef](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/trait_def.rs#L14-L70)
- [TraitRef alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/predicate.rs#L14) [TraitRef ast](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_ast/src/ast.rs#L2838-L2848) [TraitRef ir](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/predicate.rs#L42-L69)
- [GenericParamDefKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/generics.rs#L13-L18)
- [GenericParamDef](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/generics.rs#L52-L64)
- GenericDefAndIdxPair - not present
- [Generics](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/generics.rs#L127-L147)
- PredicateKindAndSpanPair - not present
- [GenericPredicates](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/generics.rs#L377-L382)
- [PredicateKind alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/predicate.rs#L22) [PredicateKind ir](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/predicate_kind.rs#L56-L112)
- [ClauseKind alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/predicate.rs#L21) [ClauseKind ir](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/predicate_kind.rs#L8-L39)
- [TraitPredicate alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/predicate.rs#L20) [TraitPredicate](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/predicate.rs#L116-L137)
- [RegionOutlivesPredicate -> OutlivesPredicate](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/predicate.rs#L27) [OutlivesPredicate](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/predicate.rs#L14-L26)
- [TypeOutlivesPredicate -> OutlivesPredicate alias](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/predicate.rs#L28) [OutlivesPredicate](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/predicate.rs#L14-L26)
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
- [ForeignItemKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/context.rs#L306-L319)
- [AdtKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L133-L143)
- [VariantDef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_internal/internal.rs#L244-L250)
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
- [PolyFnSig](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L355C23-L355C34)
- [Ty](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L315-L320)
- [Pattern](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L398-L410)
- [TyConst](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L454-L492)
- [TyConstId](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L489) [IndexMap<ty::Const<'tcx>, TyConstId>](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/mod.rs#L37)
- [MirConst](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L412-L452)
- [MirConstId](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L450) [IndexMap<mir::Const<'tcx>, MirConstId>](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/mod.rs#L38)
- [TyConstKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L458-L482)
- [DebruijinIndex](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L385C31-L385C54)
- [UniverseIndex](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L823)
- [EarlyParamRegion](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L812-L815)
- [BoundVar](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L825)
- [BoundRegion](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L816-L829)
- [RePlaceholder - Placeholder - PlaceholderForBoundRegion](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L821-L829)
- [RegionKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L806-L834)
- [Region](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L798-L804)
- [Span](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mod.rs#L81-L87)
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
- [TyKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L323-L397)
- TypeAndMut - not present
- [ParamTy](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L502-L508)
- [BoundTy](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L510-L516)
- [Promoted](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L737)
- [Align](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_smir/src/rustc_smir/alloc.rs#L12C25-L12C56)
- [ProvenanceMap](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_smir/src/rustc_smir/alloc.rs#L124-L135)
- [Bytes -> AllocByte and AllocBytes](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_smir/src/rustc_smir/alloc.rs#L108)
- [fn new_allocation -> Allocation](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_smir/src/rustc_smir/alloc.rs#L21-L100)
- [ConstantKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L418-L446)
- [ParamConst](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L494-L500)
- [UnevaluatedConst ty](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L440-L446) [UnevaluatedConst mir](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L738-L747)
- [TraitSpecializationKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L518-L531)
- Ident - not present
- [TraitDecl](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L533-L557)
- [TraitRef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L559-L566)
- [GenericParamDefKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L593-L608)
- [GenericParamDef](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L610-L622)
- GenericDefAndIdxPair - not present
- [Generics](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L568-L591)
- PredicateKindAndSpanPair - not present
- [GenericPredicates -> fn predicates_of](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/context.rs#L161-L178)
- [PredicateKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L624-L656)
- [ClauseKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L658-L692)
- [TraitPredicate](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L737-L747)
- [RegionOutlivesPredicate -> OutlivesPredicate](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L749-L759)
- [OutlivesPredicate](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L670-L676)
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
- [Placeholder](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L278) [PlaceholderForBoundRegion](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/ty.rs#L300-L304)
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
