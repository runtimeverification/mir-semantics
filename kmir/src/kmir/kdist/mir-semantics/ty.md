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
  imports LIST

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

// FIXME why are the bytes optional? What does it mean???
syntax AllocByte ::= someByte(Int) [group(mir-option-int), symbol(someByte)]
                   | "noByte"      [group(mir-option), symbol(noByte)]
syntax AllocBytes ::= List {AllocByte, ""} [group(mir-list), symbol(AllocBytes::append), terminator-symbol(AllocBytes::empty)]
syntax Allocation ::= allocation(
                        bytes: AllocBytes,
                        provenance: ProvenanceMap,
                        align: Align,
                        mutability: Mutability)
                      [group(mir---bytes--provenance--align--mutability), symbol(allocation)]

syntax ConstantKind ::= constantKindTy(TyConst)                   [group(mir-enum), symbol(ConstantKind::Ty)]
                      | constantKindAllocated(Allocation)         [group(mir-enum), symbol(ConstantKind::Allocated)]
                      | constantKindUnevaluated(UnevaluatedConst) [group(mir-enum), symbol(ConstantKind::Unevaluated)]
                      | constantKindParam(ParamConst)             [group(mir-enum), symbol(ConstantKind::Param)]
                      | "constantKindZeroSized"                   [group(mir-enum), symbol(ConstantKind::ZeroSized)]
                      | "constantKindNoOp"                        [group(mir-enum), symbol(ConstantKind::NoOp)]
                      | constantKindFnDef(id: Int)                [group(mir-enum), symbol(ConstantKind::FnDef)]
                      | constantKindIntrinsic(name: Symbol)       [group(mir-enum), symbol(ConstantKind::Intrinsic)]

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
