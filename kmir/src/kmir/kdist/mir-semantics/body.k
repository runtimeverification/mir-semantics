module BODY-SORTS

syntax Body
syntax Bodies
syntax DefId
syntax MaybeInt
syntax Mutability
syntax Safety

endmodule

module BODY
  imports BODY-SORTS
  imports LIB-SORTS
  imports TYPES-SORTS
  imports INT
  imports STRING

syntax DefId ::= defId(Int) [symbol(defId)]
syntax LocalDefId ::= localDefId(Opaque)
syntax Coverage ::= coverage(Opaque)

syntax Mutability ::= "mutabilityNot" | "mutabilityMut"
syntax Safety ::= "safetyUnsafe" | "safetyNormal"

syntax BasicBlockIdx ::= basicBlockIdx(Int)
syntax MaybeBasicBlockIdx ::= someBasicBlockIdx(BasicBlockIdx) | "noBasicBlockIdx"

syntax Operand ::= operandCopy(Place)
                 | operandMove(Place)
                 | operandConstant(ConstOperand)
syntax MaybeOperand ::= someOperand(Operand) | "noOperand"
syntax Operands ::= List {Operand, ""}

syntax Local ::= local(Int)
syntax MaybeLocal ::= someLocal(Local) | "noLocal"

syntax ProjectionElemDeref ::= "projectionElemDeref"
syntax ProjectionElemField ::= projectionElemField(FieldIdx, Ty)
syntax ProjectionElemIndex ::= projectionElemIndex(Local)
syntax ProjectionElemConstantIndex ::= projectionElemConstantIndex(offset: Int, minLength: Int, fromEnd: Bool)
syntax ProjectionElemSubslice ::= projectionElemSubslice(from: Int, to: Int, fromEnd: Bool)
syntax ProjectionElemDowncast ::= projectionElemDowncast(VariantIdx)
syntax ProjectionElemOpaqueCast ::= projectionElemOpaqueCast(Ty)
syntax ProjectionElemSubtype ::= projectionElemSubtype(Ty)
syntax ProjectionElem ::= ProjectionElemDeref
                        | ProjectionElemField
                        | ProjectionElemIndex
                        | ProjectionElemConstantIndex
                        | ProjectionElemSubslice
                        | ProjectionElemDowncast
                        | ProjectionElemOpaqueCast
                        | ProjectionElemSubtype
syntax ProjectionElems ::= List {ProjectionElem, ""}
syntax Place ::= place(local: Local, projection: ProjectionElems)
syntax MaybePlace ::= somePlace(Place) | "noPlace"

syntax Branch ::= branch(Int, BasicBlockIdx)
syntax Branches ::= List {Branch, ""}
syntax SwitchTargets ::= switchTargets(branches: Branches, otherwise: BasicBlockIdx)

syntax UserTypeProjection ::= userTypeProjection(base: UserTypeAnnotationIndex, projection: Opaque)

syntax BinOp ::= "binOpAdd"
               | "binOpAddUnchecked"
               | "binOpSub"
               | "binOpSubUnchecked"
               | "binOpMul"
               | "binOpMulUnchecked"
               | "binOpDiv"
               | "binOpRem"
               | "binOpBitXor"
               | "binOpBitAnd"
               | "binOpBitOr"
               | "binOpShl"
               | "binOpShlUnchecked"
               | "binOpShr"
               | "binOpShrUnchecked"
               | "binOpEq"
               | "binOpLt"
               | "binOpLe"
               | "binOpNe"
               | "binOpGe"
               | "binOpGt"
               | "binOpCmp"
               | "binOpOffset"

syntax UnOp ::= "unOpNot"
              | "unOpNeg"
              | "unOpPtrMetadata"

syntax NullOp ::= "nullOpSizeOf"
                | "nullOpAlignOf"
                | nullOpOffsetOf(VariantAndFieldIndices)
                | "nullOpUbChecks"

syntax CoroutineSource ::= "coroutineSourceBlock"
                         | "coroutineSourceClosure"
                         | "coroutineSourceFn"
syntax CoroutineDesugaring ::= "coroutineDesugaringAsync"
                             | "coroutineDesugaringGen"
                             | "coroutineDesugaringAsyncGen"
syntax CoroutineKind ::= coroutineKindDesugared(CoroutineDesugaring, CoroutineSource)
                       | coroutineKindCoroutine(Movability)

syntax UnwindAction ::= "unwindActionContinue"
                      | "unwindActionUnreachable"
                      | "unwindActionTerminate"
                      | unwindActionCleanup(BasicBlockIdx)

/////// Rvalue
syntax VariantAndFieldIndex ::= vfi(VariantIdx, FieldIdx)
syntax VariantAndFieldIndices ::= List {VariantAndFieldIndex, ""}
syntax PointerCoersion ::= "pointerCoersionReifyFnPointer"
                         | "pointerCoersionUnsafeFnPointer"
                         | pointerCoersionClosureFnPointer(Safety)
                         | "pointerCoersionMutToConstPointer"
                         | "pointerCoersionArrayToPointer"
                         | "pointerCoersionUnsize"
syntax CastKind ::= "castKindPointerExposeAddress"
                  | "castKindPointerWithExposedProvenance"
                  | castKindPointerCoersion(PointerCoersion)
                  | "castKindDynStar"
                  | "castKindIntToInt"
                  | "castKindFloatToInt"
                  | "castKindFloatToFloat"
                  | "castKindIntToFloat"
                  | "castKindPtrToPtr"
                  | "castKindFnPtrToPtr"
                  | "castKindTransmute"
syntax BorrowKind ::= "borrowKindShared"
                    | borrowKindFake(FakeBorrowKind)
                    | borrowKindMut(kind: MutBorrowKind)
syntax MutBorrowKind ::= "mutBorrowKindDefault"
                       | "mutBorrowKindTwoPhaseBorrow"
                       | "mutBorrowKindClosureCapture"
syntax FakeBorrowKind ::= "fakeBorrowKindDeep"
                        | "fakeBorrowKindShallow"
syntax UserTypeAnnotationIndex ::= userTypeAnnotationIndex(Int)
syntax MaybeUserTypeAnnotationIndex ::= someUserTypeAnnotationIndex(UserTypeAnnotationIndex)
                                      | "noUserTypeAnnotationIndex"
syntax FieldIdx ::= fieldIdx(Int)
syntax MaybeFieldIdx ::= someFieldIdx(FieldIdx) | "noFieldIdx"

syntax AggregateKind ::= aggregateKindArray(Ty)
                       | "aggregateKindTuple"
                       | aggregateKindAdt(AdtDef, VariantIdx, GenericArgs, MaybeUserTypeAnnotationIndex, MaybeFieldIdx)
                       | aggregateKindClosure(ClosureDef, GenericArgs)
                       | aggregateKindCoroutine(CoroutineDef, GenericArgs, Movability)
                       | aggregateKindRawPtr(Ty, Mutability)

syntax RvalueAddressOf ::= rvalueAddressOf(Mutability, Place)
syntax RvalueAggregate ::= rvalueAggregate(AggregateKind, Operands)
syntax RvalueBinaryOp ::= rvalueBinaryOp(BinOp, Operand, Operand)
syntax RvalueCast ::= rvalueCast(CastKind, Operand, Operand)
syntax RvalueCheckedBinaryOp ::= rvalueCheckedBinaryOp(BinOp, Operand, Operand)
syntax RvalueCopyForDeref ::= rvalueCopyForDeref(Place)
syntax RvalueDiscriminant ::= rvalueDiscriminant(Place)
syntax RvalueLen ::= rvalueLen(Place)
syntax RvalueRef ::= rvalueRef(Region, BorrowKind, Place)
syntax RvalueRepeat ::= rvalueRepeat(Operand, TyConst)
syntax RvalueShallowInitBox ::= rvalueShallowInitBox(Operand, Ty)
syntax RvalueThreadLocalRef ::= rvalueThreadLocalRef(crate: CrateItem)
syntax RvalueNullaryOp ::= rvalueNullaryOp(NullOp, Ty)
syntax RvalueUnaryOp ::= rvalueUnaryOp(UnOp, Operand)
syntax RvalueUse ::= rvalueUse(Operand)

syntax Rvalue ::= RvalueAddressOf
                | RvalueAggregate
                | RvalueBinaryOp
                | RvalueCast
                | RvalueCheckedBinaryOp
                | RvalueCopyForDeref
                | RvalueDiscriminant
                | RvalueLen
                | RvalueRef
                | RvalueRepeat
                | RvalueShallowInitBox
                | RvalueThreadLocalRef
                | RvalueNullaryOp
                | RvalueUnaryOp
                | RvalueUse

/////// End Rvalue


/////// Statements

syntax StatementKindAssign ::= statementKindAssign(place: Place, rvalue: Rvalue)
syntax StatementKindFakeRead ::= statementKindFakeRead(cause: FakeReadCause, place: Place)
syntax StatementKindSetDiscriminant ::= statementKindSetDiscriminant(place: Place, variantIndex: VariantIdx)
syntax StatementKindDeinit ::= deinit(place: Place)
syntax StatementKindStorageLive ::= statementKindStorageLive(Local)
syntax StatementKindStorageDead ::= statementKindStorageDead(Local)
syntax StatementKindRetag ::= statementKindRetag(kind: RetagKind, place: Place)
syntax StatementKindPlaceMention ::= statementKindPlaceMention(place: Place)
syntax StatementKindAscribeUserType ::= statementKindAscribeUserType(place: Place, projections: UserTypeProjection, variance: Variance)
syntax StatementKindCoverage ::= statementKindCoverage(Coverage)
syntax StatementKindIntrinsic ::= statementKindIntrinsic(NonDivergingIntrinsic)
syntax StatementKindConstEvalCounter ::= "statementKindConstEvalCounter"
syntax StatementKindNop ::= "statementKindNop"

syntax StatementKind ::= StatementKindAssign
                       | StatementKindFakeRead
                       | StatementKindSetDiscriminant
                       | StatementKindDeinit
                       | StatementKindStorageLive
                       | StatementKindStorageDead
                       | StatementKindRetag
                       | StatementKindPlaceMention
                       | StatementKindAscribeUserType
                       | StatementKindCoverage
                       | StatementKindIntrinsic
                       | StatementKindConstEvalCounter
                       | StatementKindNop

syntax Statement ::= statement(kind: StatementKind, span: Span)
syntax Statements ::= List {Statement, ""}
/////// End Statements

/////// Terminators

syntax TerminatorKindGoto ::= terminatorKindGoto(target: BasicBlockIdx)
syntax TerminatorKindSwitchInt ::= terminatorKindSwitchInt(discr: Operand, targets: SwitchTargets)
syntax TerminatorKindResume ::= "terminatorKindResume"
syntax TerminatorKindAbort ::= "terminatorKindAbort"
syntax TerminatorKindReturn ::= "terminatorKindReturn"
syntax TerminatorKindUnreachable ::= "terminatorKindUnreachable"
syntax TerminatorKindDrop ::= terminatorKindDrop(place: Place, target: BasicBlockIdx, unwind: UnwindAction)
syntax TerminatorKindCall ::= terminatorKindCall(
                                func: Operand,
                                args: Operands,
                                destination: Place,
                                target: MaybeBasicBlockIdx,
                                unwind: UnwindAction) [symbol(terminatorKindCall)]

syntax AssertMessageBoundsCheck ::= assertMessageBoundsCheck(len: Operand, index: Operand)
syntax AssertMessageOverflow ::= assertMessageOverflow(BinOp, Operand, Operand)
syntax AssertMessageOverflowNeg ::= assertMessageOverflowNeg(Operand)
syntax AssertMessageDivisionByZero ::= assertMessageDivisionByZero(Operand)
syntax AssertMessageRemainderByZero ::= assertMessageRemainderByZero(Operand)
syntax AssertMessageResumedAfterReturn ::= assertMessageResumedAfterReturn(CoroutineKind)
syntax AssertMessageResumedAfterPanic ::= assertMessageResumedAfterPanic(CoroutineKind)
syntax AssertMessageMisalignedPointerDereference ::= assertMessageMisalignedPointerDereference(required: Operand, found: Operand)
syntax AssertMessage ::= AssertMessageBoundsCheck
                       | AssertMessageOverflow
                       | AssertMessageOverflowNeg
                       | AssertMessageDivisionByZero
                       | AssertMessageRemainderByZero
                       | AssertMessageResumedAfterReturn
                       | AssertMessageResumedAfterPanic
                       | AssertMessageMisalignedPointerDereference
syntax TerminatorKindAssert ::= assert(cond: Operand, expected: Bool, msg: AssertMessage, target: BasicBlockIdx, unwind: UnwindAction)
syntax InlineAsmOperand ::= inlineAsmOperand(inValue: MaybeOperand, outValue: MaybePlace, rawPtr: String)
syntax InlineAsmOperands ::= List {InlineAsmOperand, ""}
syntax TerminatorKindInlineAsm ::= terminatorKindInlineAsm(template: String, operands: InlineAsmOperands, options: String, lineSpans: String, destination: MaybeBasicBlockIdx, unwind: UnwindAction)

syntax TerminatorKind ::= TerminatorKindGoto
                        | TerminatorKindSwitchInt
                        | TerminatorKindResume
                        | TerminatorKindAbort
                        | TerminatorKindReturn
                        | TerminatorKindUnreachable
                        | TerminatorKindDrop
                        | TerminatorKindCall
                        | TerminatorKindAssert
                        | TerminatorKindInlineAsm
syntax Terminator ::= terminator(kind: TerminatorKind, span: Span)

syntax FakeReadCause ::= "fakeReadCauseForMatchGuard"
                       | fakeReadCauseForMatchedPlace(LocalDefId)
                       | "fakeReadCauseForGuardBinding"
                       | fakeReadCauseForLet(LocalDefId)
                       | "fakeReadCauseForIndex"

syntax RetagKind ::= "retagKindFnEntry"
                   | "retagKindTwoPhase"
                   | "retagKindRaw"
                   | "retagKindDefault"

syntax Variance ::= "varianceCovariant"
                  | "varianceInvariant"
                  | "varianceContravariant"
                  | "varianceBivariant"

syntax CopyNonOverlapping ::= copyNonOverlapping(src: Operand, dst: Operand, count: Operand)
syntax NonDivergingIntrinsic ::= nonDivergingIntrinsicAssume(Operand)
                               | nonDivergingIntrinsicCopyNonOverlapping(CopyNonOverlapping)

/////// End terminators

syntax BasicBlock ::= basicBlock(statements: Statements, terminator: Terminator)
syntax BasicBlocks ::= List {BasicBlock, ""}

syntax LocalDecl ::= localDecl(ty: Ty, span: Span, mut: Mutability)
syntax LocalDecls ::= List {LocalDecl, ""}

syntax SourceScope ::= sourceScope(Int)
syntax SourceInfo ::= sourceInfo(span: Span, scope: SourceScope)
syntax VarDebugInfoFragment ::= varDebugInfoFragment(ty: Ty, projection: ProjectionElems)
syntax MaybeVarDebugInfoFragment ::= someVarDebugInfoFragment(VarDebugInfoFragment)
                                   | "noVarDebugInfoFragment"
syntax ConstOperand ::= constOperand(span: Span, userTy: MaybeUserTypeAnnotationIndex, const: MirConst)
syntax VarDebugInfoContents ::= varDebugInfoContentsPlace(Place)
                              | varDebugInfoContentsConst(ConstOperand)
syntax MaybeInt ::= someInt(Int) | "noInt"
syntax VarDebugInfo ::= varDebugInfo(name: Symbol, sourceInfo: SourceInfo, composite: MaybeVarDebugInfoFragment, value: VarDebugInfoContents, argumentIndex: MaybeInt)
syntax VarDebugInfos ::= List {VarDebugInfo, ""}

syntax Body ::= body(blocks: BasicBlocks, locals: LocalDecls, argCount: Int, varDebugInfo: VarDebugInfos, spreadArg: MaybeLocal, span: Span)
syntax Bodies ::= List {Body, ""} [symbol(bodies), terminator-symbol(.bodies)]

endmodule
