module UNCHECKED-OP-SPEC
  imports KMIR

 claim [unchecked-op-spec]:
  <k>
    ( // LHS, start state
      #execTerminator ( 
          terminator (... 
              kind: terminatorKindCall (... 
                  func: operandConstant (
                      constOperand (... 
                          span: span ( 71 ) ,
                          userTy: noUserTypeAnnotationIndex ,
                          const: mirConst (... 
                              kind: constantKindZeroSized , 
                              ty: ty ( 32 ) , // <- this is the reference to `unchecked_op`
                              id: mirConstId ( 13 ) 
                          )
                      )
                  ) ,
                  args: 
                      operandCopy ( place (... local: local ( 2 ) , projection: .ProjectionElems ) )
                      operandCopy ( place (... local: local ( 3 ) , projection: .ProjectionElems ) ),
                  destination: DEST,
                  target: noBasicBlockIdx,
                    // forcing the proof to stop because there is no caller to return to
                  unwind: _
              ),
              span: _
          )
      ) 
    => 
      // RHS: target
      // #execTerminator ( terminator (... kind: terminatorKindReturn , span: ?_ ) )
      #EndProgram
    )
    ~> .K
  </k>
  <retVal> _ </retVal>
  <currentFunc> _ => ty ( 32 ) </currentFunc>
  <currentFrame>
    <currentBody> _ => ?_ </currentBody>
    <caller> _ => ?_ </caller>
    <dest> _ => DEST </dest>
    <target> _ => noBasicBlockIdx </target>
    <unwind> _ => ?_ </unwind>
    <locals>
      ListItem ( _ )
      ListItem ( _ )
      ListItem ( typedLocal ( Integer ( A , 16 , true ) , ty ( 23 ) , _ ) )
      ListItem ( typedLocal ( Integer ( B , 32 , false ) , ty ( 24 ) , _ ) )
      // _ // if we keep this we need a lemma for list size predicate simplification
      => 
      ListItem ( typedLocal ( Integer ( ?RESULT, 16, true), ty ( 23 ) , ?_ ))
      ?_
    </locals>
  </currentFrame>
  <stack> _ => ?_ </stack>
  <functions>
    (
      ty ( 32 ) |-> monoItemFn (... name: symbol ( "unchecked_op" ) , id: defId ( 9 ) , body: body (... blocks: basicBlock (... statements: .Statements , terminator: terminator (... kind: terminatorKindCall (... func: operandConstant ( constOperand (... span: span ( 83 ) , userTy: noUserTypeAnnotationIndex , const: mirConst (... kind: constantKindZeroSized , ty: ty ( 33 ) , id: mirConstId ( 16 ) ) ) ) , args: operandCopy ( place (... local: local ( 1 ) , projection: .ProjectionElems ) )  operandCopy ( place (... local: local ( 2 ) , projection: .ProjectionElems ) )  .Operands , destination: place (... local: local ( 0 ) , projection: .ProjectionElems ) , target: someBasicBlockIdx ( basicBlockIdx ( 1 ) ) , unwind: unwindActionContinue ) , span: span ( 84 ) ) )  basicBlock (... statements: .Statements , terminator: terminator (... kind: terminatorKindReturn , span: span ( 85 ) ) )  .BasicBlocks , locals: localDecl (... ty: ty ( 23 ) , span: span ( 86 ) , mut: mutabilityMut )  localDecl (... ty: ty ( 23 ) , span: span ( 87 ) , mut: mutabilityNot )  localDecl (... ty: ty ( 24 ) , span: span ( 88 ) , mut: mutabilityNot )  .LocalDecls , argCount: 2 , varDebugInfo: varDebugInfo (... name: symbol ( "a" ) , sourceInfo: sourceInfo (... span: span ( 87 ) , scope: sourceScope ( 0 ) ) , composite: noVarDebugInfoFragment , value: varDebugInfoContentsPlace ( place (... local: local ( 1 ) , projection: .ProjectionElems ) ) , argumentIndex: someInt ( 1 ) )  varDebugInfo (... name: symbol ( "b" ) , sourceInfo: sourceInfo (... span: span ( 88 ) , scope: sourceScope ( 0 ) ) , composite: noVarDebugInfoFragment , value: varDebugInfoContentsPlace ( place (... local: local ( 2 ) , projection: .ProjectionElems ) ) , argumentIndex: someInt ( 2 ) )  varDebugInfo (... name: symbol ( "unchecked_res" ) , sourceInfo: sourceInfo (... span: span ( 89 ) , scope: sourceScope ( 1 ) ) , composite: noVarDebugInfoFragment , value: varDebugInfoContentsPlace ( place (... local: local ( 0 ) , projection: .ProjectionElems ) ) , argumentIndex: noInt )  .VarDebugInfos , spreadArg: noLocal , span: span ( 90 ) )  .Bodies )
      ty ( 33 ) |-> monoItemFn (... name: symbol ( "core::num::<impl i16>::unchecked_shl" ) , id: defId ( 3 ) , body: body (... blocks: basicBlock (... statements: statement (... kind: statementKindStorageLive ( local ( 3 ) ) , span: span ( 43 ) )  statement (... kind: statementKindAssign (... place: place (... local: local ( 3 ) , projection: .ProjectionElems ) , rvalue: rvalueNullaryOp ( nullOpUbChecks , ty ( 21 ) ) ) , span: span ( 44 ) )  .Statements , terminator: terminator (... kind: terminatorKindSwitchInt (... discr: operandMove ( place (... local: local ( 3 ) , projection: .ProjectionElems ) ) , targets: switchTargets (... branches: branch ( 0 , basicBlockIdx ( 2 ) )  .Branches , otherwise: basicBlockIdx ( 1 ) ) ) , span: span ( 43 ) ) )  basicBlock (... statements: .Statements , terminator: terminator (... kind: terminatorKindCall (... func: operandConstant ( constOperand (... span: span ( 45 ) , userTy: noUserTypeAnnotationIndex , const: mirConst (... kind: constantKindZeroSized , ty: ty ( 22 ) , id: mirConstId ( 6 ) ) ) ) , args: operandCopy ( place (... local: local ( 2 ) , projection: .ProjectionElems ) )  .Operands , destination: place (... local: local ( 4 ) , projection: .ProjectionElems ) , target: someBasicBlockIdx ( basicBlockIdx ( 2 ) ) , unwind: unwindActionUnreachable ) , span: span ( 46 ) ) )  basicBlock (... statements: statement (... kind: statementKindStorageDead ( local ( 3 ) ) , span: span ( 48 ) )  statement (... kind: statementKindAssign (... place: place (... local: local ( 0 ) , projection: .ProjectionElems ) , rvalue: rvalueBinaryOp ( binOpShlUnchecked , operandCopy ( place (... local: local ( 1 ) , projection: .ProjectionElems ) ) , operandCopy ( place (... local: local ( 2 ) , projection: .ProjectionElems ) ) ) ) , span: span ( 49 ) )  .Statements , terminator: terminator (... kind: terminatorKindReturn , span: span ( 47 ) ) )  .BasicBlocks , locals: localDecl (... ty: ty ( 23 ) , span: span ( 50 ) , mut: mutabilityMut )  localDecl (... ty: ty ( 23 ) , span: span ( 51 ) , mut: mutabilityNot )  localDecl (... ty: ty ( 24 ) , span: span ( 52 ) , mut: mutabilityNot )  localDecl (... ty: ty ( 21 ) , span: span ( 43 ) , mut: mutabilityMut )  localDecl (... ty: ty ( 1 ) , span: span ( 46 ) , mut: mutabilityNot )  .LocalDecls , argCount: 2 , varDebugInfo: varDebugInfo (... name: symbol ( "self" ) , sourceInfo: sourceInfo (... span: span ( 51 ) , scope: sourceScope ( 0 ) ) , composite: noVarDebugInfoFragment , value: varDebugInfoContentsPlace ( place (... local: local ( 1 ) , projection: .ProjectionElems ) ) , argumentIndex: someInt ( 1 ) )  varDebugInfo (... name: symbol ( "rhs" ) , sourceInfo: sourceInfo (... span: span ( 52 ) , scope: sourceScope ( 0 ) ) , composite: noVarDebugInfoFragment , value: varDebugInfoContentsPlace ( place (... local: local ( 2 ) , projection: .ProjectionElems ) ) , argumentIndex: someInt ( 2 ) )  .VarDebugInfos , spreadArg: noLocal , span: span ( 53 ) )  .Bodies )
      ty ( 22 ) |-> monoItemFn (... name: symbol ( "core::num::<impl i16>::unchecked_shl::precondition_check" ) , id: defId ( 4 ) , body: body (... blocks: basicBlock (... statements: statement (... kind: statementKindStorageLive ( local ( 2 ) ) , span: span ( 54 ) )  statement (... kind: statementKindAssign (... place: place (... local: local ( 2 ) , projection: .ProjectionElems ) , rvalue: rvalueBinaryOp ( binOpLt , operandCopy ( place (... local: local ( 1 ) , projection: .ProjectionElems ) ) , operandConstant ( constOperand (... span: span ( 55 ) , userTy: noUserTypeAnnotationIndex , const: mirConst (... kind: constantKindAllocated ( allocation (... bytes: b"\x10\x00\x00\x00" , provenance: provenanceMap (... ptrs: .ProvenanceMapEntries ) , align: align ( 4 ) , mutability: mutabilityMut ) ) , ty: ty ( 24 ) , id: mirConstId ( 7 ) ) ) ) ) ) , span: span ( 54 ) )  .Statements , terminator: terminator (... kind: terminatorKindSwitchInt (... discr: operandMove ( place (... local: local ( 2 ) , projection: .ProjectionElems ) ) , targets: switchTargets (... branches: branch ( 0 , basicBlockIdx ( 2 ) )  .Branches , otherwise: basicBlockIdx ( 1 ) ) ) , span: span ( 54 ) ) )  basicBlock (... statements: statement (... kind: statementKindStorageDead ( local ( 2 ) ) , span: span ( 57 ) )  .Statements , terminator: terminator (... kind: terminatorKindReturn , span: span ( 56 ) ) )  basicBlock (... statements: .Statements , terminator: terminator (... kind: terminatorKindCall (... func: operandConstant ( constOperand (... span: span ( 58 ) , userTy: noUserTypeAnnotationIndex , const: mirConst (... kind: constantKindZeroSized , ty: ty ( 25 ) , id: mirConstId ( 8 ) ) ) ) , args: operandConstant ( constOperand (... span: span ( 59 ) , userTy: noUserTypeAnnotationIndex , const: mirConst (... kind: constantKindAllocated ( allocation (... bytes: b"\x00\x00\x00\x00\x00\x00\x00\x00C\x00\x00\x00\x00\x00\x00\x00" , provenance: provenanceMap (... ptrs: provenanceMapEntry (... provSize: 0 , allocId: allocId ( 0 ) )  .ProvenanceMapEntries ) , align: align ( 8 ) , mutability: mutabilityMut ) ) , ty: ty ( 26 ) , id: mirConstId ( 9 ) ) ) )  .Operands , destination: place (... local: local ( 3 ) , projection: .ProjectionElems ) , target: noBasicBlockIdx , unwind: unwindActionUnreachable ) , span: span ( 60 ) ) )  .BasicBlocks , locals: localDecl (... ty: ty ( 1 ) , span: span ( 61 ) , mut: mutabilityMut )  localDecl (... ty: ty ( 24 ) , span: span ( 62 ) , mut: mutabilityNot )  localDecl (... ty: ty ( 21 ) , span: span ( 54 ) , mut: mutabilityMut )  localDecl (... ty: ty ( 27 ) , span: span ( 60 ) , mut: mutabilityNot )  .LocalDecls , argCount: 1 , varDebugInfo: varDebugInfo (... name: symbol ( "rhs" ) , sourceInfo: sourceInfo (... span: span ( 62 ) , scope: sourceScope ( 0 ) ) , composite: noVarDebugInfoFragment , value: varDebugInfoContentsPlace ( place (... local: local ( 1 ) , projection: .ProjectionElems ) ) , argumentIndex: someInt ( 1 ) )  .VarDebugInfos , spreadArg: noLocal , span: span ( 63 ) )  .Bodies )
    )
  </functions>
  requires // i16 invariants
             0 -Int (1 <<Int 15) <=Int A
     andBool A <Int (1 <<Int 15)
     andBool 0 -Int (1 <<Int 15) <=Int B
     andBool A <Int (1 <<Int 15)
     // invariant of the `unchecked_sub` operation
     ensures 
            B <Int 16
endmodule
