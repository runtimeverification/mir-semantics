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
                          span: span ( 79 ) ,
                          userTy: noUserTypeAnnotationIndex ,
                          const: mirConst (... 
                              kind: constantKindZeroSized , 
                              ty: ty ( 32 ) , // <- this is the reference to `unchecked_op`
                              id: mirConstId ( 15 ) 
                          )
                      )
                  ) ,
                  args: 
                      operandCopy ( place (... local: local ( 2 ) , projection: .ProjectionElems ) ),
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
      // _ // if we keep this we need a lemma for list size predicate simplification
      => 
      ListItem ( typedLocal ( Integer ( ?RESULT, 16, true), ty ( 23 ) , ?_ ))
      ?_
    </locals>
  </currentFrame>
  <stack> _ => ?_ </stack>
  <functions>
    (
      ty ( 32 ) |-> monoItemFn (... name: symbol ( "unchecked_op" ) , id: defId ( 10 ) , body: body (... blocks: basicBlock (... statements: .Statements , terminator: terminator (... kind: terminatorKindCall (... func: operandConstant ( constOperand (... span: span ( 88 ) , userTy: noUserTypeAnnotationIndex , const: mirConst (... kind: constantKindZeroSized , ty: ty ( 33 ) , id: mirConstId ( 17 ) ) ) ) , args: operandCopy ( place (... local: local ( 1 ) , projection: .ProjectionElems ) )  .Operands , destination: place (... local: local ( 0 ) , projection: .ProjectionElems ) , target: someBasicBlockIdx ( basicBlockIdx ( 1 ) ) , unwind: unwindActionContinue ) , span: span ( 89 ) ) )  basicBlock (... statements: .Statements , terminator: terminator (... kind: terminatorKindReturn , span: span ( 90 ) ) )  .BasicBlocks , locals: localDecl (... ty: ty ( 23 ) , span: span ( 91 ) , mut: mutabilityMut )  localDecl (... ty: ty ( 23 ) , span: span ( 92 ) , mut: mutabilityNot )  .LocalDecls , argCount: 1 , varDebugInfo: varDebugInfo (... name: symbol ( "a" ) , sourceInfo: sourceInfo (... span: span ( 92 ) , scope: sourceScope ( 0 ) ) , composite: noVarDebugInfoFragment , value: varDebugInfoContentsPlace ( place (... local: local ( 1 ) , projection: .ProjectionElems ) ) , argumentIndex: someInt ( 1 ) )  varDebugInfo (... name: symbol ( "unchecked_res" ) , sourceInfo: sourceInfo (... span: span ( 93 ) , scope: sourceScope ( 1 ) ) , composite: noVarDebugInfoFragment , value: varDebugInfoContentsPlace ( place (... local: local ( 0 ) , projection: .ProjectionElems ) ) , argumentIndex: noInt )  .VarDebugInfos , spreadArg: noLocal , span: span ( 94 ) )  .Bodies )
      ty ( 33 ) |-> monoItemFn (... name: symbol ( "core::num::<impl i16>::unchecked_neg" ) , id: defId ( 4 ) , body: body (... blocks: basicBlock (... statements: statement (... kind: statementKindStorageLive ( local ( 2 ) ) , span: span ( 46 ) )  statement (... kind: statementKindAssign (... place: place (... local: local ( 2 ) , projection: .ProjectionElems ) , rvalue: rvalueNullaryOp ( nullOpUbChecks , ty ( 21 ) ) ) , span: span ( 47 ) )  .Statements , terminator: terminator (... kind: terminatorKindSwitchInt (... discr: operandMove ( place (... local: local ( 2 ) , projection: .ProjectionElems ) ) , targets: switchTargets (... branches: branch ( 0 , basicBlockIdx ( 2 ) )  .Branches , otherwise: basicBlockIdx ( 1 ) ) ) , span: span ( 46 ) ) )  basicBlock (... statements: .Statements , terminator: terminator (... kind: terminatorKindCall (... func: operandConstant ( constOperand (... span: span ( 48 ) , userTy: noUserTypeAnnotationIndex , const: mirConst (... kind: constantKindZeroSized , ty: ty ( 22 ) , id: mirConstId ( 6 ) ) ) ) , args: operandCopy ( place (... local: local ( 1 ) , projection: .ProjectionElems ) )  .Operands , destination: place (... local: local ( 3 ) , projection: .ProjectionElems ) , target: someBasicBlockIdx ( basicBlockIdx ( 2 ) ) , unwind: unwindActionUnreachable ) , span: span ( 49 ) ) )  basicBlock (... statements: statement (... kind: statementKindStorageDead ( local ( 2 ) ) , span: span ( 51 ) )  statement (... kind: statementKindAssign (... place: place (... local: local ( 0 ) , projection: .ProjectionElems ) , rvalue: rvalueBinaryOp ( binOpSubUnchecked , operandConstant ( constOperand (... span: span ( 52 ) , userTy: noUserTypeAnnotationIndex , const: mirConst (... kind: constantKindAllocated ( allocation (... bytes: b"\x00\x00" , provenance: provenanceMap (... ptrs: .ProvenanceMapEntries ) , align: align ( 2 ) , mutability: mutabilityMut ) ) , ty: ty ( 23 ) , id: mirConstId ( 7 ) ) ) ) , operandCopy ( place (... local: local ( 1 ) , projection: .ProjectionElems ) ) ) ) , span: span ( 53 ) )  .Statements , terminator: terminator (... kind: terminatorKindReturn , span: span ( 50 ) ) )  .BasicBlocks , locals: localDecl (... ty: ty ( 23 ) , span: span ( 54 ) , mut: mutabilityMut )  localDecl (... ty: ty ( 23 ) , span: span ( 55 ) , mut: mutabilityNot )  localDecl (... ty: ty ( 21 ) , span: span ( 46 ) , mut: mutabilityMut )  localDecl (... ty: ty ( 1 ) , span: span ( 49 ) , mut: mutabilityNot )  .LocalDecls , argCount: 1 , varDebugInfo: varDebugInfo (... name: symbol ( "self" ) , sourceInfo: sourceInfo (... span: span ( 55 ) , scope: sourceScope ( 0 ) ) , composite: noVarDebugInfoFragment , value: varDebugInfoContentsPlace ( place (... local: local ( 1 ) , projection: .ProjectionElems ) ) , argumentIndex: someInt ( 1 ) )  .VarDebugInfos , spreadArg: noLocal , span: span ( 56 ) )  .Bodies )
      ty ( 22 ) |-> monoItemFn (... name: symbol ( "core::num::<impl i16>::unchecked_neg::precondition_check" ) , id: defId ( 5 ) , body: body (... blocks: basicBlock (... statements: statement (... kind: statementKindStorageLive ( local ( 3 ) ) , span: span ( 58 ) )  statement (... kind: statementKindAssign (... place: place (... local: local ( 3 ) , projection: .ProjectionElems ) , rvalue: rvalueBinaryOp ( binOpEq , operandCopy ( place (... local: local ( 1 ) , projection: .ProjectionElems ) ) , operandConstant ( constOperand (... span: span ( 59 ) , userTy: noUserTypeAnnotationIndex , const: mirConst (... kind: constantKindAllocated ( allocation (... bytes: b"\x00\x80" , provenance: provenanceMap (... ptrs: .ProvenanceMapEntries ) , align: align ( 2 ) , mutability: mutabilityMut ) ) , ty: ty ( 23 ) , id: mirConstId ( 8 ) ) ) ) ) ) , span: span ( 58 ) )  .Statements , terminator: terminator (... kind: terminatorKindSwitchInt (... discr: operandCopy ( place (... local: local ( 3 ) , projection: .ProjectionElems ) ) , targets: switchTargets (... branches: branch ( 0 , basicBlockIdx ( 3 ) )  .Branches , otherwise: basicBlockIdx ( 1 ) ) ) , span: span ( 57 ) ) )  basicBlock (... statements: .Statements , terminator: terminator (... kind: terminatorKindCall (... func: operandConstant ( constOperand (... span: span ( 60 ) , userTy: noUserTypeAnnotationIndex , const: mirConst (... kind: constantKindZeroSized , ty: ty ( 24 ) , id: mirConstId ( 9 ) ) ) ) , args: .Operands , destination: place (... local: local ( 4 ) , projection: .ProjectionElems ) , target: someBasicBlockIdx ( basicBlockIdx ( 2 ) ) , unwind: unwindActionUnreachable ) , span: span ( 61 ) ) )  basicBlock (... statements: statement (... kind: statementKindStorageDead ( local ( 3 ) ) , span: span ( 65 ) )  .Statements , terminator: terminator (... kind: terminatorKindCall (... func: operandConstant ( constOperand (... span: span ( 62 ) , userTy: noUserTypeAnnotationIndex , const: mirConst (... kind: constantKindZeroSized , ty: ty ( 25 ) , id: mirConstId ( 10 ) ) ) ) , args: operandConstant ( constOperand (... span: span ( 63 ) , userTy: noUserTypeAnnotationIndex , const: mirConst (... kind: constantKindAllocated ( allocation (... bytes: b"\x00\x00\x00\x00\x00\x00\x00\x00C\x00\x00\x00\x00\x00\x00\x00" , provenance: provenanceMap (... ptrs: provenanceMapEntry (... provSize: 0 , allocId: allocId ( 0 ) )  .ProvenanceMapEntries ) , align: align ( 8 ) , mutability: mutabilityMut ) ) , ty: ty ( 26 ) , id: mirConstId ( 11 ) ) ) )  .Operands , destination: place (... local: local ( 2 ) , projection: .ProjectionElems ) , target: noBasicBlockIdx , unwind: unwindActionUnreachable ) , span: span ( 64 ) ) )  basicBlock (... statements: statement (... kind: statementKindStorageDead ( local ( 3 ) ) , span: span ( 65 ) )  .Statements , terminator: terminator (... kind: terminatorKindReturn , span: span ( 66 ) ) )  .BasicBlocks , locals: localDecl (... ty: ty ( 1 ) , span: span ( 67 ) , mut: mutabilityMut )  localDecl (... ty: ty ( 23 ) , span: span ( 68 ) , mut: mutabilityNot )  localDecl (... ty: ty ( 27 ) , span: span ( 64 ) , mut: mutabilityNot )  localDecl (... ty: ty ( 21 ) , span: span ( 58 ) , mut: mutabilityMut )  localDecl (... ty: ty ( 1 ) , span: span ( 61 ) , mut: mutabilityNot )  .LocalDecls , argCount: 1 , varDebugInfo: varDebugInfo (... name: symbol ( "lhs" ) , sourceInfo: sourceInfo (... span: span ( 68 ) , scope: sourceScope ( 0 ) ) , composite: noVarDebugInfoFragment , value: varDebugInfoContentsPlace ( place (... local: local ( 1 ) , projection: .ProjectionElems ) ) , argumentIndex: someInt ( 1 ) )  varDebugInfo (... name: symbol ( "self" ) , sourceInfo: sourceInfo (... span: span ( 69 ) , scope: sourceScope ( 1 ) ) , composite: noVarDebugInfoFragment , value: varDebugInfoContentsPlace ( place (... local: local ( 1 ) , projection: .ProjectionElems ) ) , argumentIndex: someInt ( 1 ) )  varDebugInfo (... name: symbol ( "b" ) , sourceInfo: sourceInfo (... span: span ( 70 ) , scope: sourceScope ( 2 ) ) , composite: noVarDebugInfoFragment , value: varDebugInfoContentsPlace ( place (... local: local ( 3 ) , projection: .ProjectionElems ) ) , argumentIndex: someInt ( 1 ) )  .VarDebugInfos , spreadArg: noLocal , span: span ( 71 ) )  .Bodies )
    )
  </functions>
  requires // i16 invariants
             0 -Int (1 <<Int 15) <=Int A
     andBool A <Int (1 <<Int 15)
     andBool 0 -Int (1 <<Int 15) <=Int B
     andBool B <Int (1 <<Int 15)
     // invariant of the `unchecked_sub` operation
     andBool B =!Int -32768
endmodule
