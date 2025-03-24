```k
requires "lib.md"
requires "ty.md"

module BODY-SORTS

syntax Body
syntax DefId
syntax MaybeInt
syntax MIRBool
syntax MIRInt
syntax MIRString
syntax Mutability
syntax Safety

endmodule

module BODY
  imports BODY-SORTS
  imports LIB-SORTS
  imports TYPES-SORTS
  imports INT
  imports STRING

syntax DefId ::= defId(Int)              [group(mir-int)]
syntax LocalDefId ::= localDefId(Opaque) [group(mir)]
syntax Coverage ::= coverage(Opaque)     [group(mir)]

syntax Mutability ::= "mutabilityNot" [group(mir-enum), symbol(Mutability::Not)]
                    | "mutabilityMut" [group(mir-enum), symbol(Mutability::Mut)]

syntax Safety ::= "safetyUnsafe" [group(mir-enum), symbol(Safety::Unsafe)]
                | "safetyNormal" [group(mir-enum), symbol(Safety::Normal)]

syntax BasicBlockIdx ::= basicBlockIdx(Int)                    [group(mir-int)]
syntax MaybeBasicBlockIdx ::= someBasicBlockIdx(BasicBlockIdx) [group(mir-option)]
                           | "noBasicBlockIdx"                 [group(mir-option)]

syntax Operand ::= operandCopy(Place)            [group(mir-enum), symbol(Operand::Copy)]
                 | operandMove(Place)            [group(mir-enum), symbol(Operand::Move)]
                 | operandConstant(ConstOperand) [group(mir-enum), symbol(Operand::Constant)]

syntax MaybeOperand ::= someOperand(Operand) [group(mir-option)]
                      | "noOperand"          [group(mir-option)]

syntax Operands ::= List {Operand, ""} [group(mir-list), symbol(Operands::append), terminator-symbol(Operands::empty)]

syntax Local ::= local(Int)            [group(mir-int)]
syntax MaybeLocal ::= someLocal(Local) [group(mir-option)]
                    | "noLocal"        [group(mir-option)]

syntax ProjectionElem ::=  "projectionElemDeref"                                                            [group(mir-enum),                               symbol(ProjectionElem::Deref)]
                        |  projectionElemField(FieldIdx, Ty)                                                [group(mir-enum),                               symbol(ProjectionElem::Field)]
                        |  projectionElemIndex(Local)                                                       [group(mir-enum),                               symbol(ProjectionElem::Index)]
                        |  projectionElemConstantIndex(offset: MIRInt, minLength: MIRInt, fromEnd: MIRBool) [group(mir-enum---offset-min-length--from-end), symbol(ProjectionElem::ConstantIndex)]
                        |  projectionElemSubslice(from: MIRInt, to: MIRInt, fromEnd: MIRBool)               [group(mir-enum),                               symbol(ProjectionElem::Subslice)]
                        |  projectionElemDowncast(VariantIdx)                                               [group(mir-enum),                               symbol(ProjectionElem::Downcast)]
                        |  projectionElemOpaqueCast(Ty)                                                     [group(mir-enum),                               symbol(ProjectionElem::OpaqueCast)]
                        |  projectionElemSubtype(Ty)                                                        [group(mir-enum),                               symbol(ProjectionElem::Subtype)]

syntax ProjectionElems ::= List {ProjectionElem, ""} [group(mir-list), symbol(ProjectionElems::append), terminator-symbol(ProjectionElems::empty)]
syntax Place ::= place(local: Local, projection: ProjectionElems) [group(mir---local--projection)]
syntax MaybePlace ::= somePlace(Place)                            [group(mir-option)]
                    | "noPlace"                                   [group(mir-option)]

syntax Branch ::= branch(MIRInt, BasicBlockIdx) [group(mir)]
syntax Branches ::= List {Branch, ""} [group(mir-list), symbol(Branches::append), terminator-symbol(Branches::empty)]
syntax SwitchTargets ::= switchTargets(branches: Branches, otherwise: BasicBlockIdx) [group(mir---branches--otherwise)]

syntax UserTypeProjection ::= userTypeProjection(base: UserTypeAnnotationIndex, projection: Opaque) [group(mir---base--projection)]

syntax BinOp ::= "binOpAdd"          [group(mir-enum), symbol(BinOp::Add)]
               | "binOpAddUnchecked" [group(mir-enum), symbol(BinOp::AddUnchecked)]
               | "binOpSub"          [group(mir-enum), symbol(BinOp::Sub)]
               | "binOpSubUnchecked" [group(mir-enum), symbol(BinOp::SubUnchecked)]
               | "binOpMul"          [group(mir-enum), symbol(BinOp::Mul)]
               | "binOpMulUnchecked" [group(mir-enum), symbol(BinOp::MulUnchecked)]
               | "binOpDiv"          [group(mir-enum), symbol(BinOp::Div)]
               | "binOpRem"          [group(mir-enum), symbol(BinOp::Rem)]
               | "binOpBitXor"       [group(mir-enum), symbol(BinOp::BitXor)]
               | "binOpBitAnd"       [group(mir-enum), symbol(BinOp::BitAnd)]
               | "binOpBitOr"        [group(mir-enum), symbol(BinOp::BitOr)]
               | "binOpShl"          [group(mir-enum), symbol(BinOp::Shl)]
               | "binOpShlUnchecked" [group(mir-enum), symbol(BinOp::ShlUnchecked)]
               | "binOpShr"          [group(mir-enum), symbol(BinOp::Shr)]
               | "binOpShrUnchecked" [group(mir-enum), symbol(BinOp::ShrUnchecked)]
               | "binOpEq"           [group(mir-enum), symbol(BinOp::Eq)]
               | "binOpLt"           [group(mir-enum), symbol(BinOp::Lt)]
               | "binOpLe"           [group(mir-enum), symbol(BinOp::Le)]
               | "binOpNe"           [group(mir-enum), symbol(BinOp::Ne)]
               | "binOpGe"           [group(mir-enum), symbol(BinOp::Ge)]
               | "binOpGt"           [group(mir-enum), symbol(BinOp::Gt)]
               | "binOpCmp"          [group(mir-enum), symbol(BinOp::Cmp)]
               | "binOpOffset"       [group(mir-enum), symbol(BinOp::Offset)]

syntax UnOp ::= "unOpNot"            [group(mir-enum), symbol(UnOp::Not)]
              | "unOpNeg"            [group(mir-enum), symbol(UnOp::Neg)]
              | "unOpPtrMetadata"    [group(mir-enum), symbol(UnOp::PtrMetadata)]

syntax NullOp ::= "nullOpSizeOf"                         [group(mir-enum), symbol(NullOp::SizeOf)]
                | "nullOpAlignOf"                        [group(mir-enum), symbol(NullOp::AlignOf)]
                | nullOpOffsetOf(VariantAndFieldIndices) [group(mir-enum), symbol(NullOp::OffsetOf)]
                | "nullOpUbChecks"                       [group(mir-enum), symbol(NullOp::UbChecks)]

syntax CoroutineSource ::= "coroutineSourceBlock"   [group(mir-enum), symbol(CoroutineSource::Block)]
                         | "coroutineSourceClosure" [group(mir-enum), symbol(CoroutineSource::Closure)]
                         | "coroutineSourceFn"      [group(mir-enum), symbol(CoroutineSource::Fn)]

syntax CoroutineDesugaring ::= "coroutineDesugaringAsync"    [group(mir-enum), symbol(CoroutineDesguaring::Async)]
                             | "coroutineDesugaringGen"      [group(mir-enum), symbol(CoroutineDesguaring::Gen)]
                             | "coroutineDesugaringAsyncGen" [group(mir-enum), symbol(CoroutineDesguaring::AsyncGen)]

syntax CoroutineKind ::= coroutineKindDesugared(CoroutineDesugaring, CoroutineSource) [group(mir-enum), symbol(CoroutineKind::Desguared)]
                       | coroutineKindCoroutine(Movability)                           [group(mir-enum), symbol(CoroutineKind::Coroutine)]

syntax UnwindAction ::= "unwindActionContinue"              [group(mir-enum), symbol(UnwindAction::Continue)]
                      | "unwindActionUnreachable"           [group(mir-enum), symbol(UnwindAction::Unreachable)]
                      | "unwindActionTerminate"             [group(mir-enum), symbol(UnwindAction::Terminate)]
                      | unwindActionCleanup(BasicBlockIdx)  [group(mir-enum), symbol(UnwindAction::Cleanup)]

/////// Rvalue
syntax VariantAndFieldIndex ::= vfi(VariantIdx, FieldIdx)           [group(mir)]
syntax VariantAndFieldIndices ::= List {VariantAndFieldIndex, ""}   [group(mir-list), symbol(VariantAndFieldIndices::append), terminator-symbol(VariantAndFieldIndices::empty)]
syntax PointerCoercion ::= "pointerCoercionReifyFnPointer"          [group(mir-enum), symbol(PointerCoercion::ReifyFnPointer)]
                         | "pointerCoercionUnsafeFnPointer"         [group(mir-enum), symbol(PointerCoercion::UnsafeFnPointer)]
                         | pointerCoercionClosureFnPointer(Safety)  [group(mir-enum), symbol(PointerCoercion::ClosureFnPointer)]
                         | "pointerCoercionMutToConstPointer"       [group(mir-enum), symbol(PointerCoercion::MutToConstPointer)]
                         | "pointerCoercionArrayToPointer"          [group(mir-enum), symbol(PointerCoercion::CoercionArrayToPointer)]
                         | "pointerCoercionUnsize"                  [group(mir-enum), symbol(PointerCoercion::Unsize)]

syntax CastKind ::= "castKindPointerExposeAddress"                  [group(mir-enum), symbol(CastKind::ExposeAddress)]
                  | "castKindPointerWithExposedProvenance"          [group(mir-enum), symbol(CastKind::PointerWithExposedProvenance)]
                  | castKindPointerCoercion(PointerCoercion)        [group(mir-enum), symbol(CastKind::PointerCoercion)]
                  | "castKindDynStar"                               [group(mir-enum), symbol(CastKind::DynStar)]
                  | "castKindIntToInt"                              [group(mir-enum), symbol(CastKind::IntToInt)]
                  | "castKindFloatToInt"                            [group(mir-enum), symbol(CastKind::FloatToInt)]
                  | "castKindFloatToFloat"                          [group(mir-enum), symbol(CastKind::FloatToFloat)]
                  | "castKindIntToFloat"                            [group(mir-enum), symbol(CastKind::IntToFloat)]
                  | "castKindPtrToPtr"                              [group(mir-enum), symbol(CastKind::PtrToPtr)]
                  | "castKindFnPtrToPtr"                            [group(mir-enum), symbol(CastKind::FnPtrToPtr)]
                  | "castKindTransmute"                             [group(mir-enum), symbol(CastKind::Transmute)]

syntax BorrowKind ::= "borrowKindShared"                  [group(mir-enum),        symbol(BorrowKind::Shared)]
                    | borrowKindFake(FakeBorrowKind)      [group(mir-enum),        symbol(BorrowKind::Fake)]
                    | borrowKindMut(kind: MutBorrowKind)  [group(mir-enum---kind), symbol(BorrowKind::Mut)]

syntax MutBorrowKind ::= "mutBorrowKindDefault"           [group(mir-enum), symbol(MutBorrowKind::Default)]
                       | "mutBorrowKindTwoPhaseBorrow"    [group(mir-enum), symbol(MutBorrowKind::TwoPhaseBorrow)]
                       | "mutBorrowKindClosureCapture"    [group(mir-enum), symbol(MutBorrowKind::ClosureCapture)]

syntax FakeBorrowKind ::= "fakeBorrowKindDeep"            [group(mir-enum), symbol(FakeBorrowKind::Deep)]
                        | "fakeBorrowKindShallow"         [group(mir-enum), symbol(FakeBorrowKind::Shallow)]

syntax UserTypeAnnotationIndex ::= userTypeAnnotationIndex(Int)                              [group(mir-int)]
syntax MaybeUserTypeAnnotationIndex ::= someUserTypeAnnotationIndex(UserTypeAnnotationIndex) [group(mir-option)]
                                      | "noUserTypeAnnotationIndex"                          [group(mir-option)]

syntax FieldIdx ::= fieldIdx(Int)                [group(mir-int)]
syntax MaybeFieldIdx ::= someFieldIdx(FieldIdx)  [group(mir-option)]
                      | "noFieldIdx"             [group(mir-option)]

syntax AggregateKind ::= aggregateKindArray(Ty)                                                                         [group(mir-enum), symbol(AggregateKind::Array)]
                       | "aggregateKindTuple"                                                                           [group(mir-enum), symbol(AggregateKind::Tuple)]
                       | aggregateKindAdt(AdtDef, VariantIdx, GenericArgs, MaybeUserTypeAnnotationIndex, MaybeFieldIdx) [group(mir-enum), symbol(AggregateKind::Adt)]
                       | aggregateKindClosure(ClosureDef, GenericArgs)                                                  [group(mir-enum), symbol(AggregateKind::Closure)]
                       | aggregateKindCoroutine(CoroutineDef, GenericArgs, Movability)                                  [group(mir-enum), symbol(AggregateKind::Coroutine)]
                       | aggregateKindRawPtr(Ty, Mutability)                                                            [group(mir-enum), symbol(AggregateKind::RawPtr)]

syntax Rvalue ::= rvalueAddressOf(Mutability, Place)                     [group(mir-enum), symbol(Rvalue::AddressOf)]
                | rvalueAggregate(AggregateKind, Operands)               [group(mir-enum), symbol(Rvalue::Aggregate)]
                | rvalueBinaryOp(BinOp, Operand, Operand)                [group(mir-enum), symbol(Rvalue::BinaryOp)]
                | rvalueCast(CastKind, Operand, Ty)                      [group(mir-enum), symbol(Rvalue::Cast)]
                | rvalueCheckedBinaryOp(BinOp, Operand, Operand)         [group(mir-enum), symbol(Rvalue::CheckedBinaryOp)]
                | rvalueCopyForDeref(Place)                              [group(mir-enum), symbol(Rvalue::CopyForDeref)]
                | rvalueDiscriminant(Place)                              [group(mir-enum), symbol(Rvalue::Discriminant)]
                | rvalueLen(Place)                                       [group(mir-enum), symbol(Rvalue::Len)]
                | rvalueRef(Region, BorrowKind, Place)                   [group(mir-enum), symbol(Rvalue::Ref)]
                | rvalueRepeat(Operand, TyConst)                         [group(mir-enum), symbol(Rvalue::Repeat)]
                | rvalueShallowInitBox(Operand, Ty)                      [group(mir-enum), symbol(Rvalue::ShallowInitBox)]
                | rvalueThreadLocalRef(crate: CrateItem)                 [group(mir-enum), symbol(Rvalue::ThreadLocalRef)]
                | rvalueNullaryOp(NullOp, Ty)                            [group(mir-enum), symbol(Rvalue::NullaryOp)]
                | rvalueUnaryOp(UnOp, Operand)                           [group(mir-enum), symbol(Rvalue::UnaryOp)]
                | rvalueUse(Operand)                                     [group(mir-enum), symbol(Rvalue::Use)]

/////// End Rvalue


/////// Statements

syntax StatementKind ::= statementKindAssign(place: Place, rvalue: Rvalue)
                         [ group(mir-enum)
                         , symbol(StatementKind::Assign)
                         ]
                       | statementKindFakeRead(cause: FakeReadCause, place: Place)
                         [ group(mir-enum)
                         , symbol(StatementKind::FakeRead)
                         ]
                       | statementKindSetDiscriminant(place: Place, variantIndex: VariantIdx)
                         [ group(mir-enum---place--variant-index)
                         , symbol(StatementKind::SetDiscriminant)
                         ]
                       | statementKindDeinit(place: Place)
                         [ group(mir-enum)
                         , symbol(StatementKind::Deinit)
                         ]
                       | statementKindStorageLive(Local)
                         [ group(mir-enum)
                         , symbol(StatementKind::StorageLive)
                         ]
                       | statementKindStorageDead(Local)
                         [ group(mir-enum)
                         , symbol(StatementKind::StorageDead)
                         ]
                       | statementKindRetag(kind: RetagKind, place: Place)
                         [ group(mir-enum)
                         , symbol(StatementKind::Retag)
                         ]
                       | statementKindPlaceMention(place: Place)
                         [ group(mir-enum)
                         , symbol(StatementKind::PlaceMention)
                         ]
                       | statementKindAscribeUserType(place: Place, projections: UserTypeProjection, variance: Variance) [group(mir-enum---place--projections--variance), symbol(StatementKind::AscribeUserType)]
                       | statementKindCoverage(Coverage)
                         [ group(mir-enum)
                         , symbol(StatementKind::Coverage)
                         ]
                       | statementKindIntrinsic(NonDivergingIntrinsic)
                         [ group(mir-enum)
                         , symbol(StatementKind::Intrinsic)
                         ]
                       | "statementKindConstEvalCounter"
                         [ group(mir-enum)
                         , symbol(StatementKind::ConstEvalCounter)
                         ]
                       | "statementKindNop"
                         [ group(mir-enum)
                         , symbol(StatementKind::Nop)
                         ]

syntax Statement ::= statement(kind: StatementKind, span: Span) [group(mir---kind--span)]
syntax Statements ::= List {Statement, ""} [group(mir-list), symbol(Statements::append), terminator-symbol(Statements::empty)]
/////// End Statements

/////// Terminators

syntax AssertMessage ::= assertMessageBoundsCheck(len: Operand, index: Operand)
                         [group(mir-enum---len--index),      symbol(AssertMessage::BoundsCheck)]
                       | assertMessageOverflow(BinOp, Operand, Operand)
                         [group(mir-enum),                   symbol(AssertMessage::Overflow)]
                       | assertMessageOverflowNeg(Operand)
                         [group(mir-enum),                   symbol(AssertMessage::OverflowNeg)]
                       | assertMessageDivisionByZero(Operand)
                         [group(mir-enum),                   symbol(AssertMessage::DivisionByZero)]
                       | assertMessageRemainderByZero(Operand)
                         [group(mir-enum),                   symbol(AssertMessage::RemainderByZero)]
                       | assertMessageResumedAfterReturn(CoroutineKind)
                         [group(mir-enum),                   symbol(AssertMessage::ResumedAfterReturn)]
                       | assertMessageResumedAfterPanic(CoroutineKind)
                         [group(mir-enum),                   symbol(AssertMessage::ResumedAfterPanic)]
                       | assertMessageMisalignedPointerDereference(required: Operand, found: Operand)
                         [group(mir-enum---required--found), symbol(AssertMessage::MisalignedPointerDereference)]

syntax InlineAsmOperand  ::= inlineAsmOperand(inValue: MaybeOperand, outValue: MaybePlace, rawPtr: MIRString)
                             [group(mir---in-value--out-place--raw-rpr)]
syntax InlineAsmOperands ::= List {InlineAsmOperand, ""}
                             [group(mir-list), symbol(InlineAsmOperands::append), terminator-symbol(InlineAsmOperands::empty)]

syntax TerminatorKind ::= terminatorKindGoto(target: BasicBlockIdx)
                          [ group(mir-enum---target)
                          , symbol(TerminatorKind::Goto)
                          ]
                        | terminatorKindSwitchInt(discr: Operand, targets: SwitchTargets)                                                                                                            [group(mir-enum---discr--targets),                                               symbol(TerminatorKind::SwitchInt)]
                        | "terminatorKindResume"
                          [ group(mir-enum)
                          , symbol(TerminatorKind::Resume)
                          ]
                        | "terminatorKindAbort"
                          [ group(mir-enum)
                          , symbol(TerminatorKind::Abort)
                          ]
                        | "terminatorKindReturn"
                          [ group(mir-enum)
                          , symbol(TerminatorKind::Return)
                          ]
                        | "terminatorKindUnreachable"
                          [ group(mir-enum)
                          , symbol(TerminatorKind::Unreachable)
                          ]
                        | terminatorKindDrop(place: Place, target: BasicBlockIdx, unwind: UnwindAction)
                          [ group(mir-enum---place--target--unwind)
                          , symbol(TerminatorKind::Drop)
                          ]
                        | terminatorKindCall( func: Operand, args: Operands, destination: Place, target: MaybeBasicBlockIdx, unwind: UnwindAction)
                          [ group(mir-enum---func--args--destination--target--unwind)
                          , symbol(TerminatorKind::Call)
                          ]
                        | assert(cond: Operand, expected: MIRBool, msg: AssertMessage, target: BasicBlockIdx, unwind: UnwindAction)
                          [ group(mir-enum---cond--expected--msg--target--unwind)
                          , symbol(TerminatorKind::Assert)
                          ]
                        | terminatorKindInlineAsm(template: MIRString, operands: InlineAsmOperands, options: MIRString, lineSpans: MIRString, destination: MaybeBasicBlockIdx, unwind: UnwindAction)
                          [ group(mir-enum---template--operands--options--line-spans--destination--unwind)
                          , symbol(TerminatorKind::InlineAsm)
                          ]

syntax Terminator ::= terminator(kind: TerminatorKind, span: Span) [group(mir---kind--span)]

syntax FakeReadCause ::= "fakeReadCauseForMatchGuard"             [group(mir-enum), symbol(FakeReadCause::ForMatchGuard)]
                       | fakeReadCauseForMatchedPlace(LocalDefId) [group(mir-enum), symbol(FakeReadCause::ForMatchedPlace)]
                       | "fakeReadCauseForGuardBinding"           [group(mir-enum), symbol(FakeReadCause::ForGuardBinding)]
                       | fakeReadCauseForLet(LocalDefId)          [group(mir-enum), symbol(FakeReadCause::ForLet)]
                       | "fakeReadCauseForIndex"                  [group(mir-enum), symbol(FakeReadCause::ForIndex)]

syntax RetagKind ::= "retagKindFnEntry"  [group(mir-enum), symbol(RetagKind::FnEntry)]
                   | "retagKindTwoPhase" [group(mir-enum), symbol(RetagKind::TwoPhase)]
                   | "retagKindRaw"      [group(mir-enum), symbol(RetagKind::Raw)]
                   | "retagKindDefault"  [group(mir-enum), symbol(RetagKind::Default)]

syntax Variance ::= "varianceCovariant"     [group(mir-enum), symbol(Variance::Covariant)]
                  | "varianceInvariant"     [group(mir-enum), symbol(Variance::Invariant)]
                  | "varianceContravariant" [group(mir-enum), symbol(Variance::Contravariant)]
                  | "varianceBivariant"     [group(mir-enum), symbol(Variance::Bivariant)]

syntax CopyNonOverlapping ::= copyNonOverlapping(src: Operand, dst: Operand, count: Operand)
                              [group(mir---src--dst--count)]
syntax NonDivergingIntrinsic ::= nonDivergingIntrinsicAssume(Operand)
                                 [group(mir-enum), symbol(NonDivergingIntrinsic::Assume)]
                               | nonDivergingIntrinsicCopyNonOverlapping(CopyNonOverlapping)
                                 [group(mir-enum), symbol(NonDivergingIntrinsic::CopyNonOverlapping)]

/////// End terminators

syntax BasicBlock ::= basicBlock(statements: Statements, terminator: Terminator) [group(mir---statements--terminator)]
syntax BasicBlocks ::= List {BasicBlock, ""} [group(mir-list), symbol(BasicBlocks::append), terminator-symbol(BasicBlocks::empty)]

syntax LocalDecl ::= localDecl(ty: Ty, span: Span, mut: Mutability) [group(mir---ty--span--mutability)]
syntax LocalDecls ::= List {LocalDecl, ""} [group(mir-list), symbol(LocalDecls::append), terminator-symbol(LocalDecls::empty)]

syntax SourceScope ::= sourceScope(Int)                          [group(mir-int)]
syntax SourceInfo ::= sourceInfo(span: Span, scope: SourceScope) [group(mir---span--scope)]
syntax VarDebugInfoFragment ::= varDebugInfoFragment(ty: Ty, projection: ProjectionElems) [group(mir---ty--projection)]
syntax MaybeVarDebugInfoFragment ::= someVarDebugInfoFragment(VarDebugInfoFragment) [group(mir-option)]
                                   | "noVarDebugInfoFragment"                       [group(mir-option)]

syntax ConstOperand ::= constOperand(span: Span, userTy: MaybeUserTypeAnnotationIndex, const: MirConst) [group(mir---span--user-ty--const-)]
syntax VarDebugInfoContents ::= varDebugInfoContentsPlace(Place)        [group(mir-enum), symbol(VarDebugInfoContents::Place)]
                              | varDebugInfoContentsConst(ConstOperand) [group(mir-enum), symbol(VarDebugInfoContents::Const)]

syntax MaybeInt ::= someInt(Int) [group(mir-option-int)]
                  | "noInt"      [group(mir-option)]

syntax VarDebugInfo ::= varDebugInfo(name: Symbol, sourceInfo: SourceInfo, composite: MaybeVarDebugInfoFragment, value: VarDebugInfoContents, argumentIndex: MaybeInt)
                        [group(mir---name--source-info--composite--value--argument-index)]
syntax VarDebugInfos ::= List {VarDebugInfo, ""}
                         [group(mir-list), symbol(VarDebugInfos::append), terminator-symbol(VarDebugInfos::empty)]

syntax Body ::= body(blocks: BasicBlocks, locals: LocalDecls, argCount: MIRInt, varDebugInfo: VarDebugInfos, spreadArg: MaybeLocal, span: Span)
                [group(mir---blocks--locals--arg-count--var-debug-info--spread-arg--span)]

endmodule
```

### Index

#### Internal MIR
- [DefId](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_span/src/def_id.rs#L216-L235)
- LocalDefId - not present ?
- Coverage - not present ?
- [Mutability](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_ast_ir/src/lib.rs#L21-L27)
- [Safety](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_hir/src/hir.rs#L3221-L3226)
- BasicBlockIdx - not present
- [Operand](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/syntax.rs#L1155-L1200)
- [Local](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/mod.rs#L901-L909)
- [ProjectionElem](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/syntax.rs#L1065-L1148) [PlaceElem](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/syntax.rs#L1150-L1152)
- [Place](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/syntax.rs#L979-L1063)
- [SwitchTargets](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/syntax.rs#L877-L896)
- [UserTypeProjection](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/mod.rs#L1549-L1584)
- [BinOp](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/syntax.rs#L1446-L1534)
- [UnOp](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/syntax.rs#L1430-L1444)
- [NullOp](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/syntax.rs#L1417-L1428)
- [CoroutineSource](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_hir/src/hir.rs#L1449-L1464)
- [CoroutineDesugaring](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_hir/src/hir.rs#L1477-L1488)
- [CoroutineKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_hir/src/hir.rs#L1410-L1418)
- [UnwindAction](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/syntax.rs#L898-L915)
- VariantAndFieldIndex - not present
- [PointerCoercion](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/adjustment.rs#L8-L37)
- [CastKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/syntax.rs#L1354-L1381)
- [BorrowKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/syntax.rs#L163-L192)
- [MutBorrowKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/syntax.rs#L194-L242)
- [FakeBorrowKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/syntax.rs#L244-L293)
- [UserTypeAnnotationIndex](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/ty/typeck_results.rs#L701-L708)
- [FieldIdx](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_target/src/abi/mod.rs#L24-L50)
- [AggregateKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/syntax.rs#L1383-L1415)
- [Rvalue](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/syntax.rs#L1218-L1352)
- [StatementKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/syntax.rs#L296-L442)
- [Statement](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/statement.rs#L7-L12)
- [AssertMessage](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/syntax.rs#L975-L976) [AssertKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/syntax.rs#L928-L940)
- [InlineAsmOperand](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/syntax.rs#L942-L973)
- [Terminator](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/terminator.rs#L374-L378)
- [FakeReadCause](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/syntax.rs#L516-L570)
- [RetagKind](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/syntax.rs#L502-L514)
- [Variance](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_type_ir/src/lib.rs#L199-L207)
- [CopyNonOverlapping](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/syntax.rs#L572-L579)
- [NonDivergingIntrinsic](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/syntax.rs#L466-L500)
- [BasicBlock](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/mod.rs#L1314-L1346)
- [LocalDecl](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/mod.rs#L1001-L1105)
- [SourceScope](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/mod.rs#L1475-L1482)
- [SourceInfo](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/mod.rs#L876-L889)
- [VarDebugInfoFragment](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/mod.rs#L1269-L1285)
- [ConstOperand](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/syntax.rs#L1202-L1215)
- [VarDebugInfoContents](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/mod.rs#L1253-L1258)
- [VarDebugInfo](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/mod.rs#L1287-L1311)
- [Body](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_middle/src/mir/mod.rs#L326-L446)

#### SMIR (Bridge)
- [DefId](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_internal/mod.rs#L148-L150)
- LocalDefId - not present
- Coverage - not present
- [Mutability](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L221-L230)
- [Safety](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mod.rs#L14-L22)
- BasicBlockIdx - not present
- [Operand](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L318-L328)
- [Local](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L394-L399)
- [ProjectionElem](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L352-L384)
- [Place](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L342-L350)
- [SwitchTargets](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L613-L619)
- [UserTypeProjection](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L386-L392)
- [BinOp](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L487-L520)
- [UnOp](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L522-L532)
- [NullOp](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L267-L280)
- [CoroutineSource](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mod.rs#L31-L41)
- [CoroutineDesugaring](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mod.rs#L48-L68)
- [CoroutineKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mod.rs#L43-L71)
- [UnwindAction](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L414-L425)
- VariantAndFieldIndex - not present
- [PointerCoercion](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L107-L124)
- [CastKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L282-L300)
- [BorrowKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L232-L242)
- [MutBorrowKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L244-L254)
- [FakeBorrowKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L256-L265)
- [UserTypeAnnotationIndex](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L126-L131)
- [FieldIdx](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mod.rs#L24-L29)
- [AggregateKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L534-L572)
- [Rvalue](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L160-L219)
- [StatementKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L102-L158)
- [Statement](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L59-L64)
- [AssertMessage](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L448-L485)
- [InlineAsmOperand](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L574-L593)
- [TerminatorKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L603-L679)
- [Terminator](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L595-L601)
- [FakeReadCause](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L302-L316)
- [RetagKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L401-L412)
- [Variance](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/ty.rs#L865-L875)
- [CopyNonOverlapping](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L437-L443)
- [NonDivergingIntrinsic](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L427-L446)
- [BasicBlock](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L19-L29)
- [LocalDecl](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L30-L37)
- [SourceScope](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L69C71-L69C95)
- [SourceInfo](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L66-L71)
- [VarDebugInfoFragment](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L73-L81)
- [ConstOperand](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L330-L340)
- [VarDebugInfoContents](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L83-L100)
- [VarDebugInfo](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L46-L57)
- [Body](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/mir.rs#L14-L44)

#### Stable MIR
- [DefId](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/crate_def.rs#L8-L10)
- [LocalDefId](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L383)
- [Coverage](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L387)
- [Mutability](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L916-L920)
- [Safety](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L922-L926)
- [BasicBlockIdx](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L38)
- [Operand](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L637-L641)
- [Local](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L811)
- [ProjectionElem](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L725-L802)
- [Place](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L644-L649)
- [SwitchTargets](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L833-L842)
- [UserTypeProjection](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L804-L809)
- [BinOp](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L311-L336)
- [UnOp](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L346-L351)
- [NullOp](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L971-L981)
- [CoroutineSource](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L367-L372)
- [CoroutineDesugaring](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L374-L381)
- [CoroutineKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L361-L365)
- [UnwindAction](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L234-L240)
- [~VariantAndFieldIndex~](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L978C14-L978C41)
- [PointerCoercion](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L928-L953)
- [CastKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L955-L969)
- [BorrowKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L871-L885)
- [MutBorrowKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L898-L903)
- [FakeBorrowKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L905-L914)
- [UserTypeAnnotationIndex](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L831)
- [FieldIdx](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L815-L829)
- [AggregateKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L626-L635)
- [Rvalue](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L452-L562)
- [StatementKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L435-L450)
- [Statement](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L429-L433)
- [AssertMessage](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L242-L252)
- [InlineAsmOperand](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L225-L232)
- [TerminatorKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L135-L175)
- [Terminator](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L121-L125)
- [FakeReadCause](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L389-L397)
- [RetagKind](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L399-L406)
- [Variance](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L408-L414)
- [CopyNonOverlapping](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L416-L421)
- [NonDivergingIntrinsic](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L423-L427)
- [BasicBlock](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L115-L119)
- [LocalDecl](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L108-L113)
- [SourceScope](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L705)
- [SourceInfo](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L707-L711)
- [VarDebugInfoFragment](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L713-L717)
- [ConstOperand](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L657-L662)
- [VarDebugInfoContents](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L719-L723)
- [VarDebugInfo](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L664-L685)
- [Body](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/mir/body.rs#L11-L36)
