module ADD1


    rule [BASIC-BLOCK-8-TO-6]: <generatedTop>
           <kmir>
             <k>
               ( #execTerminator ( terminator ( ... kind: terminatorKindCall ( ... func: operandConstant ( constOperand ( ... span: span ( 0 ) , userTy: noUserTypeAnnotationIndex , const: mirConst ( ... kind: constantKindZeroSized , ty: ty ( 27 ) , id: mirConstId ( 0 ) ) ) ) , args: operandCopy ( place ( ... local: local ( 1 ) , projection: .ProjectionElems ) )  .Operands , destination: place ( ... local: local ( 0 ) , projection: .ProjectionElems ) , target: noBasicBlockIdx , unwind: unwindActionContinue ) , span: span ( 0 ) ) ) => #ProgramError ( AssertError ( assertMessageOverflow ( binOpAdd , operandCopy ( place ( ... local: local ( 1 ) , projection: .ProjectionElems ) ) , operandConstant ( constOperand ( ... span: span ( 50 ) , userTy: noUserTypeAnnotationIndex , const: mirConst ( ... kind: constantKindAllocated ( allocation ( ... bytes: b"\x01\x00\x00\x00" , provenance: provenanceMap ( ... ptrs: .ProvenanceMapEntries ) , align: align ( 4 ) , mutability: mutabilityMut ) ) , ty: ty ( 16 ) , id: mirConstId ( 9 ) ) ) ) ) ) )
               ~> #execBlockIdx ( basicBlockIdx ( 1 ) ) )
             </k>
             <retVal>
               _RETVAL_CELL:RetVal
             </retVal>
             <currentFunc>
               ( CURRENTFUNC_CELL:Ty => ty ( 27 ) )
             </currentFunc>
             <currentFrame>
               <currentBody>
                 ( _CURRENTBODY_CELL => ListItem ( basicBlock ( ... statements: statement ( ... kind: statementKindAssign ( ... place: place ( ... local: local ( 2 ) , projection: .ProjectionElems ) , rvalue: rvalueCheckedBinaryOp ( binOpAdd , operandCopy ( place ( ... local: local ( 1 ) , projection: .ProjectionElems ) ) , operandConstant ( constOperand ( ... span: span ( 50 ) , userTy: noUserTypeAnnotationIndex , const: mirConst ( ... kind: constantKindAllocated ( allocation ( ... bytes: b"\x01\x00\x00\x00" , provenance: provenanceMap ( ... ptrs: .ProvenanceMapEntries ) , align: align ( 4 ) , mutability: mutabilityMut ) ) , ty: ty ( 16 ) , id: mirConstId ( 9 ) ) ) ) ) ) , span: span ( 51 ) )  .Statements , terminator: terminator ( ... kind: assert ( ... cond: operandMove ( place ( ... local: local ( 2 ) , projection: projectionElemField ( fieldIdx ( 1 ) , ty ( 25 ) )  .ProjectionElems ) ) , expected: false , msg: assertMessageOverflow ( binOpAdd , operandCopy ( place ( ... local: local ( 1 ) , projection: .ProjectionElems ) ) , operandConstant ( constOperand ( ... span: span ( 50 ) , userTy: noUserTypeAnnotationIndex , const: mirConst ( ... kind: constantKindAllocated ( allocation ( ... bytes: b"\x01\x00\x00\x00" , provenance: provenanceMap ( ... ptrs: .ProvenanceMapEntries ) , align: align ( 4 ) , mutability: mutabilityMut ) ) , ty: ty ( 16 ) , id: mirConstId ( 9 ) ) ) ) ) , target: basicBlockIdx ( 1 ) , unwind: unwindActionContinue ) , span: span ( 51 ) ) ) ) ListItem ( basicBlock ( ... statements: statement ( ... kind: statementKindAssign ( ... place: place ( ... local: local ( 0 ) , projection: .ProjectionElems ) , rvalue: rvalueUse ( operandMove ( place ( ... local: local ( 2 ) , projection: projectionElemField ( fieldIdx ( 0 ) , ty ( 16 ) )  .ProjectionElems ) ) ) ) , span: span ( 51 ) )  .Statements , terminator: terminator ( ... kind: terminatorKindReturn , span: span ( 52 ) ) ) ) )
               </currentBody>
               <caller>
                 ( CALLER_CELL:Ty => CURRENTFUNC_CELL:Ty )
               </caller>
               <dest>
                 ( DEST_CELL:Place => place ( ... local: local ( 0 ) , projection: .ProjectionElems ) )
               </dest>
               <target>
                 ( TARGET_CELL:MaybeBasicBlockIdx => noBasicBlockIdx )
               </target>
               <unwind>
                 ( UNWIND_CELL:UnwindAction => unwindActionContinue )
               </unwind>
               <locals>
                 ListItem ( newLocal ( ty ( ( 0 => 16 ) ) , ( mutabilityNot => mutabilityMut ) ) ) ( ListItem ( typedValue ( Integer ( ARG_INT1:Int , 32 , true ) , ty ( 16 ) , mutabilityNot ) ) => ListItem ( typedValue ( Integer ( ARG_INT1:Int , 32 , true ) , ty ( 16 ) , mutabilityNot ) ) ListItem ( typedValue ( Aggregate ( variantIdx ( 0 ) , ListItem ( Integer ( truncate ( ARG_INT1:Int +Int 1 , 32 , Signed ) , 32 , true ) ) ListItem ( Moved ) ) , ty ( 26 ) , mutabilityMut ) ) )
               </locals>
             </currentFrame>
             <stack>
               ( .List => ListItem ( StackFrame ( CALLER_CELL:Ty , DEST_CELL:Place , TARGET_CELL:MaybeBasicBlockIdx , UNWIND_CELL:UnwindAction , ListItem ( newLocal ( ty ( 0 ) , mutabilityNot ) ) ListItem ( typedValue ( Integer ( ARG_INT1:Int , 32 , true ) , ty ( 16 ) , mutabilityNot ) ) ) ) )
             </stack>
             <memory>
               _MEMORY_CELL:Map
             </memory>
             <functions>
               ty ( 20 ) |-> IntrinsicFunction ( symbol ( "black_box" ) ) ty ( 27 ) |-> monoItemFn ( ... name: symbol ( "add1" ) , id: defId ( 6 ) , body: someBody ( body ( ... blocks: basicBlock ( ... statements: statement ( ... kind: statementKindAssign ( ... place: place ( ... local: local ( 2 ) , projection: .ProjectionElems ) , rvalue: rvalueCheckedBinaryOp ( binOpAdd , operandCopy ( place ( ... local: local ( 1 ) , projection: .ProjectionElems ) ) , operandConstant ( constOperand ( ... span: span ( 50 ) , userTy: noUserTypeAnnotationIndex , const: mirConst ( ... kind: constantKindAllocated ( allocation ( ... bytes: b"\x01\x00\x00\x00" , provenance: provenanceMap ( ... ptrs: .ProvenanceMapEntries ) , align: align ( 4 ) , mutability: mutabilityMut ) ) , ty: ty ( 16 ) , id: mirConstId ( 9 ) ) ) ) ) ) , span: span ( 51 ) )  .Statements , terminator: terminator ( ... kind: assert ( ... cond: operandMove ( place ( ... local: local ( 2 ) , projection: projectionElemField ( fieldIdx ( 1 ) , ty ( 25 ) )  .ProjectionElems ) ) , expected: false , msg: assertMessageOverflow ( binOpAdd , operandCopy ( place ( ... local: local ( 1 ) , projection: .ProjectionElems ) ) , operandConstant ( constOperand ( ... span: span ( 50 ) , userTy: noUserTypeAnnotationIndex , const: mirConst ( ... kind: constantKindAllocated ( allocation ( ... bytes: b"\x01\x00\x00\x00" , provenance: provenanceMap ( ... ptrs: .ProvenanceMapEntries ) , align: align ( 4 ) , mutability: mutabilityMut ) ) , ty: ty ( 16 ) , id: mirConstId ( 9 ) ) ) ) ) , target: basicBlockIdx ( 1 ) , unwind: unwindActionContinue ) , span: span ( 51 ) ) )  basicBlock ( ... statements: statement ( ... kind: statementKindAssign ( ... place: place ( ... local: local ( 0 ) , projection: .ProjectionElems ) , rvalue: rvalueUse ( operandMove ( place ( ... local: local ( 2 ) , projection: projectionElemField ( fieldIdx ( 0 ) , ty ( 16 ) )  .ProjectionElems ) ) ) ) , span: span ( 51 ) )  .Statements , terminator: terminator ( ... kind: terminatorKindReturn , span: span ( 52 ) ) )  .BasicBlocks , locals: localDecl ( ... ty: ty ( 16 ) , span: span ( 53 ) , mut: mutabilityMut )  localDecl ( ... ty: ty ( 16 ) , span: span ( 54 ) , mut: mutabilityNot )  localDecl ( ... ty: ty ( 26 ) , span: span ( 51 ) , mut: mutabilityMut )  .LocalDecls , argCount: 1 , varDebugInfo: varDebugInfo ( ... name: symbol ( "x" ) , sourceInfo: sourceInfo ( ... span: span ( 54 ) , scope: sourceScope ( 0 ) ) , composite: noVarDebugInfoFragment , value: varDebugInfoContentsPlace ( place ( ... local: local ( 1 ) , projection: .ProjectionElems ) ) , argumentIndex: someInt ( 1 ) )  .VarDebugInfos , spreadArg: noLocal , span: span ( 55 ) ) ) )
             </functions>
             <types>
               ty ( 1 ) |-> typeInfoTupleType ( .Tys ) ty ( 10 ) |-> typeInfoEnumType ( "std::result::Result<isize, !>" , adtDef ( 19 ) , Discriminant ( 0 )  Discriminant ( 1 )  .Discriminants ) ty ( 11 ) |-> typeInfoRefType ( ty ( 12 ) ) ty ( 15 ) |-> typeInfoStructType ( "std::sys::pal::unix::process::process_common::ExitCode" , adtDef ( 11 ) , ty ( 9 )  .Tys ) ty ( 16 ) |-> typeInfoPrimitiveType ( primTypeInt ( intTyI32 ) ) ty ( 17 ) |-> typeInfoStructType ( "std::process::ExitCode" , adtDef ( 9 ) , ty ( 15 )  .Tys ) ty ( 18 ) |-> typeInfoRefType ( ty ( 15 ) ) ty ( 22 ) |-> typeInfoPtrType ( ty ( 12 ) ) ty ( 24 ) |-> typeInfoRefType ( ty ( 12 ) ) ty ( 25 ) |-> typeInfoPrimitiveType ( primTypeBool ) ty ( 26 ) |-> typeInfoTupleType ( ty ( 16 )  ty ( 25 )  .Tys ) ty ( 29 ) |-> typeInfoRefType ( ty ( 34 ) ) ty ( 30 ) |-> typeInfoVoidType ty ( 32 ) |-> typeInfoPtrType ( ty ( 9 ) ) ty ( 33 ) |-> typeInfoRefType ( ty ( 35 ) ) ty ( 34 ) |-> typeInfoPrimitiveType ( primTypeStr ) ty ( 35 ) |-> typeInfoStructType ( "std::panic::Location<'_>" , adtDef ( 23 ) , ty ( 29 )  ty ( 36 )  ty ( 36 )  .Tys ) ty ( 36 ) |-> typeInfoPrimitiveType ( primTypeUint ( uintTyU32 ) ) ty ( 5 ) |-> typeInfoRefType ( ty ( 31 ) ) ty ( 6 ) |-> typeInfoPrimitiveType ( primTypeInt ( intTyIsize ) ) ty ( 8 ) |-> typeInfoPtrType ( ty ( 32 ) ) ty ( 9 ) |-> typeInfoPrimitiveType ( primTypeUint ( uintTyU8 ) )
             </types>
             <adt-to-ty>
               adtDef ( 11 ) |-> ty ( 15 ) adtDef ( 19 ) |-> ty ( 10 ) adtDef ( 23 ) |-> ty ( 35 ) adtDef ( 9 ) |-> ty ( 17 )
             </adt-to-ty>
           </kmir>
           <generatedCounter>
             _GENERATEDCOUNTER_CELL:Int
           </generatedCounter>
         </generatedTop>
      requires ( ARG_INT1:Int <=Int 2147483647
       andBool ( -2147483648 <=Int ARG_INT1:Int
       andBool ( notBool truncate ( ARG_INT1:Int +Int 1 , 32 , Signed ) =/=Int ARG_INT1:Int +Int 1 ==Bool false
               )))
      [priority(20), label(BASIC-BLOCK-8-TO-6)]

    rule [BASIC-BLOCK-9-TO-7]: <generatedTop>
           <kmir>
             <k>
               ( #execTerminator ( terminator ( ... kind: terminatorKindCall ( ... func: operandConstant ( constOperand ( ... span: span ( 0 ) , userTy: noUserTypeAnnotationIndex , const: mirConst ( ... kind: constantKindZeroSized , ty: ty ( 27 ) , id: mirConstId ( 0 ) ) ) ) , args: operandCopy ( place ( ... local: local ( 1 ) , projection: .ProjectionElems ) )  .Operands , destination: place ( ... local: local ( 0 ) , projection: .ProjectionElems ) , target: noBasicBlockIdx , unwind: unwindActionContinue ) , span: span ( 0 ) ) ) => #EndProgram ~> .K )
             </k>
             <retVal>
               ( _RETVAL_CELL:RetVal => return ( Integer ( truncate ( ARG_INT1:Int +Int 1 , 32 , Signed ) , 32 , true ) ) )
             </retVal>
             <currentFunc>
               ( CURRENTFUNC_CELL:Ty => ty ( 27 ) )
             </currentFunc>
             <currentFrame>
               <currentBody>
                 ( _CURRENTBODY_CELL => ListItem ( basicBlock ( ... statements: statement ( ... kind: statementKindAssign ( ... place: place ( ... local: local ( 2 ) , projection: .ProjectionElems ) , rvalue: rvalueCheckedBinaryOp ( binOpAdd , operandCopy ( place ( ... local: local ( 1 ) , projection: .ProjectionElems ) ) , operandConstant ( constOperand ( ... span: span ( 50 ) , userTy: noUserTypeAnnotationIndex , const: mirConst ( ... kind: constantKindAllocated ( allocation ( ... bytes: b"\x01\x00\x00\x00" , provenance: provenanceMap ( ... ptrs: .ProvenanceMapEntries ) , align: align ( 4 ) , mutability: mutabilityMut ) ) , ty: ty ( 16 ) , id: mirConstId ( 9 ) ) ) ) ) ) , span: span ( 51 ) )  .Statements , terminator: terminator ( ... kind: assert ( ... cond: operandMove ( place ( ... local: local ( 2 ) , projection: projectionElemField ( fieldIdx ( 1 ) , ty ( 25 ) )  .ProjectionElems ) ) , expected: false , msg: assertMessageOverflow ( binOpAdd , operandCopy ( place ( ... local: local ( 1 ) , projection: .ProjectionElems ) ) , operandConstant ( constOperand ( ... span: span ( 50 ) , userTy: noUserTypeAnnotationIndex , const: mirConst ( ... kind: constantKindAllocated ( allocation ( ... bytes: b"\x01\x00\x00\x00" , provenance: provenanceMap ( ... ptrs: .ProvenanceMapEntries ) , align: align ( 4 ) , mutability: mutabilityMut ) ) , ty: ty ( 16 ) , id: mirConstId ( 9 ) ) ) ) ) , target: basicBlockIdx ( 1 ) , unwind: unwindActionContinue ) , span: span ( 51 ) ) ) ) ListItem ( basicBlock ( ... statements: statement ( ... kind: statementKindAssign ( ... place: place ( ... local: local ( 0 ) , projection: .ProjectionElems ) , rvalue: rvalueUse ( operandMove ( place ( ... local: local ( 2 ) , projection: projectionElemField ( fieldIdx ( 0 ) , ty ( 16 ) )  .ProjectionElems ) ) ) ) , span: span ( 51 ) )  .Statements , terminator: terminator ( ... kind: terminatorKindReturn , span: span ( 52 ) ) ) ) )
               </currentBody>
               <caller>
                 ( CALLER_CELL:Ty => CURRENTFUNC_CELL:Ty )
               </caller>
               <dest>
                 ( DEST_CELL:Place => place ( ... local: local ( 0 ) , projection: .ProjectionElems ) )
               </dest>
               <target>
                 ( TARGET_CELL:MaybeBasicBlockIdx => noBasicBlockIdx )
               </target>
               <unwind>
                 ( UNWIND_CELL:UnwindAction => unwindActionContinue )
               </unwind>
               <locals>
                 ListItem ( ( newLocal ( ty ( 0 ) , mutabilityNot ) => typedValue ( Integer ( truncate ( ARG_INT1:Int +Int 1 , 32 , Signed ) , 32 , true ) , ty ( 16 ) , mutabilityMut ) ) ) ( ListItem ( typedValue ( Integer ( ARG_INT1:Int , 32 , true ) , ty ( 16 ) , mutabilityNot ) ) => ListItem ( typedValue ( Integer ( ARG_INT1:Int , 32 , true ) , ty ( 16 ) , mutabilityNot ) ) ListItem ( typedValue ( Aggregate ( variantIdx ( 0 ) , ListItem ( Moved ) ListItem ( Moved ) ) , ty ( 26 ) , mutabilityMut ) ) )
               </locals>
             </currentFrame>
             <stack>
               ( .List => ListItem ( StackFrame ( CALLER_CELL:Ty , DEST_CELL:Place , TARGET_CELL:MaybeBasicBlockIdx , UNWIND_CELL:UnwindAction , ListItem ( newLocal ( ty ( 0 ) , mutabilityNot ) ) ListItem ( typedValue ( Integer ( ARG_INT1:Int , 32 , true ) , ty ( 16 ) , mutabilityNot ) ) ) ) )
             </stack>
             <memory>
               _MEMORY_CELL:Map
             </memory>
             <functions>
               ty ( 20 ) |-> IntrinsicFunction ( symbol ( "black_box" ) ) ty ( 27 ) |-> monoItemFn ( ... name: symbol ( "add1" ) , id: defId ( 6 ) , body: someBody ( body ( ... blocks: basicBlock ( ... statements: statement ( ... kind: statementKindAssign ( ... place: place ( ... local: local ( 2 ) , projection: .ProjectionElems ) , rvalue: rvalueCheckedBinaryOp ( binOpAdd , operandCopy ( place ( ... local: local ( 1 ) , projection: .ProjectionElems ) ) , operandConstant ( constOperand ( ... span: span ( 50 ) , userTy: noUserTypeAnnotationIndex , const: mirConst ( ... kind: constantKindAllocated ( allocation ( ... bytes: b"\x01\x00\x00\x00" , provenance: provenanceMap ( ... ptrs: .ProvenanceMapEntries ) , align: align ( 4 ) , mutability: mutabilityMut ) ) , ty: ty ( 16 ) , id: mirConstId ( 9 ) ) ) ) ) ) , span: span ( 51 ) )  .Statements , terminator: terminator ( ... kind: assert ( ... cond: operandMove ( place ( ... local: local ( 2 ) , projection: projectionElemField ( fieldIdx ( 1 ) , ty ( 25 ) )  .ProjectionElems ) ) , expected: false , msg: assertMessageOverflow ( binOpAdd , operandCopy ( place ( ... local: local ( 1 ) , projection: .ProjectionElems ) ) , operandConstant ( constOperand ( ... span: span ( 50 ) , userTy: noUserTypeAnnotationIndex , const: mirConst ( ... kind: constantKindAllocated ( allocation ( ... bytes: b"\x01\x00\x00\x00" , provenance: provenanceMap ( ... ptrs: .ProvenanceMapEntries ) , align: align ( 4 ) , mutability: mutabilityMut ) ) , ty: ty ( 16 ) , id: mirConstId ( 9 ) ) ) ) ) , target: basicBlockIdx ( 1 ) , unwind: unwindActionContinue ) , span: span ( 51 ) ) )  basicBlock ( ... statements: statement ( ... kind: statementKindAssign ( ... place: place ( ... local: local ( 0 ) , projection: .ProjectionElems ) , rvalue: rvalueUse ( operandMove ( place ( ... local: local ( 2 ) , projection: projectionElemField ( fieldIdx ( 0 ) , ty ( 16 ) )  .ProjectionElems ) ) ) ) , span: span ( 51 ) )  .Statements , terminator: terminator ( ... kind: terminatorKindReturn , span: span ( 52 ) ) )  .BasicBlocks , locals: localDecl ( ... ty: ty ( 16 ) , span: span ( 53 ) , mut: mutabilityMut )  localDecl ( ... ty: ty ( 16 ) , span: span ( 54 ) , mut: mutabilityNot )  localDecl ( ... ty: ty ( 26 ) , span: span ( 51 ) , mut: mutabilityMut )  .LocalDecls , argCount: 1 , varDebugInfo: varDebugInfo ( ... name: symbol ( "x" ) , sourceInfo: sourceInfo ( ... span: span ( 54 ) , scope: sourceScope ( 0 ) ) , composite: noVarDebugInfoFragment , value: varDebugInfoContentsPlace ( place ( ... local: local ( 1 ) , projection: .ProjectionElems ) ) , argumentIndex: someInt ( 1 ) )  .VarDebugInfos , spreadArg: noLocal , span: span ( 55 ) ) ) )
             </functions>
             <types>
               ty ( 1 ) |-> typeInfoTupleType ( .Tys ) ty ( 10 ) |-> typeInfoEnumType ( "std::result::Result<isize, !>" , adtDef ( 19 ) , Discriminant ( 0 )  Discriminant ( 1 )  .Discriminants ) ty ( 11 ) |-> typeInfoRefType ( ty ( 12 ) ) ty ( 15 ) |-> typeInfoStructType ( "std::sys::pal::unix::process::process_common::ExitCode" , adtDef ( 11 ) , ty ( 9 )  .Tys ) ty ( 16 ) |-> typeInfoPrimitiveType ( primTypeInt ( intTyI32 ) ) ty ( 17 ) |-> typeInfoStructType ( "std::process::ExitCode" , adtDef ( 9 ) , ty ( 15 )  .Tys ) ty ( 18 ) |-> typeInfoRefType ( ty ( 15 ) ) ty ( 22 ) |-> typeInfoPtrType ( ty ( 12 ) ) ty ( 24 ) |-> typeInfoRefType ( ty ( 12 ) ) ty ( 25 ) |-> typeInfoPrimitiveType ( primTypeBool ) ty ( 26 ) |-> typeInfoTupleType ( ty ( 16 )  ty ( 25 )  .Tys ) ty ( 29 ) |-> typeInfoRefType ( ty ( 34 ) ) ty ( 30 ) |-> typeInfoVoidType ty ( 32 ) |-> typeInfoPtrType ( ty ( 9 ) ) ty ( 33 ) |-> typeInfoRefType ( ty ( 35 ) ) ty ( 34 ) |-> typeInfoPrimitiveType ( primTypeStr ) ty ( 35 ) |-> typeInfoStructType ( "std::panic::Location<'_>" , adtDef ( 23 ) , ty ( 29 )  ty ( 36 )  ty ( 36 )  .Tys ) ty ( 36 ) |-> typeInfoPrimitiveType ( primTypeUint ( uintTyU32 ) ) ty ( 5 ) |-> typeInfoRefType ( ty ( 31 ) ) ty ( 6 ) |-> typeInfoPrimitiveType ( primTypeInt ( intTyIsize ) ) ty ( 8 ) |-> typeInfoPtrType ( ty ( 32 ) ) ty ( 9 ) |-> typeInfoPrimitiveType ( primTypeUint ( uintTyU8 ) )
             </types>
             <adt-to-ty>
               adtDef ( 11 ) |-> ty ( 15 ) adtDef ( 19 ) |-> ty ( 10 ) adtDef ( 23 ) |-> ty ( 35 ) adtDef ( 9 ) |-> ty ( 17 )
             </adt-to-ty>
           </kmir>
           <generatedCounter>
             _GENERATEDCOUNTER_CELL:Int
           </generatedCounter>
         </generatedTop>
      requires ( ARG_INT1:Int <=Int 2147483647
       andBool ( -2147483648 <=Int ARG_INT1:Int
       andBool ( truncate ( ARG_INT1:Int +Int 1 , 32 , Signed ) =/=Int ARG_INT1:Int +Int 1 ==Bool false
               )))
      [priority(20), label(BASIC-BLOCK-9-TO-7)]

endmodule
