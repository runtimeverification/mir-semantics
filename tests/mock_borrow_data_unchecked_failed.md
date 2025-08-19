
┌─ 1 (root, init)
│     <generatedTop>
│       <kmir>
│         <k>
│           #execTerminator ( terminator ( ... kind: terminatorKindCall ( ... func: operandConstant ( constOperand ( ... span: span ( 0 ) , userTy: noUserTypeAnnotationIndex , const: mirConst ( ... kind: constantKindZeroSized , ty: ty ( -1 ) , id: mirConstId ( 0 ) ) ) ) , args: .Operands , destination: place ( ... local: local ( 0 ) , projection: .ProjectionElems ) , target: noBasicBlockIdx , unwind: unwindActionContinue ) , span: span ( 0 ) ) )
│         </k>
│         <currentFrame>
│           <locals>
│             ListItem (newLocal ( ty ( 0 ) , mutabilityNot ))
│           </locals>
│           ...
│         </currentFrame>
│         <stack>
│           .List
│         </stack>
│         ...
│       </kmir>
│       ...
│     </generatedTop>
│   #execTerminator ( terminator ( ... kind: terminatorKindCall ( ... func: operandC
│   span: library/core/src/slice/iter.rs:130
│
│  (10 steps)
├─ 3
│     <generatedTop>
│       <kmir>
│         <k>
│           operandConstant ( constOperand ( ... span: span ( 869 ) , userTy: noUserTypeAnnotationIndex , const: mirConst ( ... kind: constantKindAllocated ( allocation ( ... bytes: b"\x00" , provenance: provenanceMap ( ... ptrs: .ProvenanceMapEntries ) , align: align ( 1 ) , mutability: mutabilityMut ) ) , ty: ty ( 16 ) , id: mirConstId ( 93 ) ) ) )
│           ~> #freezer#setLocalValue(_,_)_RT-DATA_KItem_Place_Evaluation1_ ( place ( ... local: local ( 1 ) , projection: .ProjectionElems ) ~> .K )
│           ~> #setArgsFromStack ( 2 , operandConstant ( constOperand ( ... span: span ( 870 ) , userTy: noUserTypeAnnotationIndex , const: mirConst ( ... kind: constantKindAllocated ( allocation ( ... bytes: b"d\x00\x00\x00\x00\x00\x00\x00" , provenance: provenanceMap ( ... ptrs: .ProvenanceMapEntries ) , align: align ( 8 ) , mutability: mutabilityMut ) ) , ty: ty ( 52 ) , id: mirConstId ( 46 ) ) ) )  .Operands )
│           ~> #execBlock ( basicBlock ( ... statements: .Statements , terminator: terminator ( ... kind: terminatorKindCall ( ... func: operandConstant ( constOperand ( ... span: span ( 594 ) , userTy: someUserTypeAnnotationIndex ( userTypeAnnotationIndex ( 0 ) ) , const: mirConst ( ... kind: constantKindZeroSized , ty: ty ( 125 ) , id: mirConstId ( 69 ) ) ) ) , args: operandMove ( place ( ... local: local ( 1 ) , projection: .ProjectionElems ) )  operandMove ( place ( ... local: local ( 2 ) , projection: .ProjectionElems ) )  operandConstant ( constOperand ( ... span: span ( 48 ) , userTy: noUserTypeAnnotationIndex , const: mirConst ( ... kind: constantKindZeroSized , ty: ty ( 115 ) , id: mirConstId ( 64 ) ) ) )  .Operands , destination: place ( ... local: local ( 0 ) , projection: .ProjectionElems ) , target: someBasicBlockIdx ( basicBlockIdx ( 1 ) ) , unwind: unwindActionContinue ) , span: span ( 595 ) ) ) )
│         </k>
│         <currentFunc>
│           ty ( 155 )
│         </currentFunc>
│         <currentFrame>
│           <caller>
│             ty ( -1 )
│           </caller>
│           <dest>
│             place ( ... local: local ( 1 ) , projection: .ProjectionElems )
│           </dest>
│           <target>
│             someBasicBlockIdx ( basicBlockIdx ( 1 ) )
│           </target>
│           <unwind>
│             unwindActionContinue
│           </unwind>
│           <locals>
│             ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 16 ) , mutabilityNot ))
│
│             ListItem (newLocal ( ty ( 52 ) , mutabilityNot ))
│           </locals>
│           ...
│         </currentFrame>
│         <stack>
│           ListItem (StackFrame ( CURRENTFUNC_CELL:Ty , place ( ... local: local ( 0 ) , projection: .ProjectionElems ) , noBasicBlockIdx , unwindActionContinue , ListItem (newLocal ( ty ( 2 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 80 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 80 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 80 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 163 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 81 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 82 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 124 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 163 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 81 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 82 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 124 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 163 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 81 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 82 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 124 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 164 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 161 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 148 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 47 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 161 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 148 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 47 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 161 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 148 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 47 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 146 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 52 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 52 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 43 ) , mutabilityMut ))
│              ))
│
│           ListItem (StackFrame ( CALLER_CELL:Ty , DEST_CELL:Place , TARGET_CELL:MaybeBasicBlockIdx , UNWIND_CELL:UnwindAction , ListItem (newLocal ( ty ( 0 ) , mutabilityNot ))
│              ))
│         </stack>
│         ...
│       </kmir>
│       ...
│     </generatedTop>
│   operandConstant ( constOperand ( ... span: span ( 869 ) , userTy: noUserTypeAnno
│   function: std::vec::from_elem::<u8>
│   span: s/mir-semantics/tests/deref.rs:44
│
│  (10 steps)
├─ 4
│     <generatedTop>
│       <kmir>
│         <k>
│           #setLocalValue ( place ( ... local: local ( 2 ) , projection: .ProjectionElems ) , Integer ( 100 , 64 , false ) )
│           ~> #setArgsFromStack ( 3 , .Operands )
│           ~> #execBlock ( basicBlock ( ... statements: .Statements , terminator: terminator ( ... kind: terminatorKindCall ( ... func: operandConstant ( constOperand ( ... span: span ( 594 ) , userTy: someUserTypeAnnotationIndex ( userTypeAnnotationIndex ( 0 ) ) , const: mirConst ( ... kind: constantKindZeroSized , ty: ty ( 125 ) , id: mirConstId ( 69 ) ) ) ) , args: operandMove ( place ( ... local: local ( 1 ) , projection: .ProjectionElems ) )  operandMove ( place ( ... local: local ( 2 ) , projection: .ProjectionElems ) )  operandConstant ( constOperand ( ... span: span ( 48 ) , userTy: noUserTypeAnnotationIndex , const: mirConst ( ... kind: constantKindZeroSized , ty: ty ( 115 ) , id: mirConstId ( 64 ) ) ) )  .Operands , destination: place ( ... local: local ( 0 ) , projection: .ProjectionElems ) , target: someBasicBlockIdx ( basicBlockIdx ( 1 ) ) , unwind: unwindActionContinue ) , span: span ( 595 ) ) ) )
│         </k>
│         <currentFunc>
│           ty ( 155 )
│         </currentFunc>
│         <currentFrame>
│           <caller>
│             ty ( -1 )
│           </caller>
│           <dest>
│             place ( ... local: local ( 1 ) , projection: .ProjectionElems )
│           </dest>
│           <target>
│             someBasicBlockIdx ( basicBlockIdx ( 1 ) )
│           </target>
│           <unwind>
│             unwindActionContinue
│           </unwind>
│           <locals>
│             ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│
│             ListItem (typedValue ( Integer ( 0 , 8 , false ) , ty ( 16 ) , mutabilityNot ))
│
│             ListItem (newLocal ( ty ( 52 ) , mutabilityNot ))
│           </locals>
│           ...
│         </currentFrame>
│         <stack>
│           ListItem (StackFrame ( CURRENTFUNC_CELL:Ty , place ( ... local: local ( 0 ) , projection: .ProjectionElems ) , noBasicBlockIdx , unwindActionContinue , ListItem (newLocal ( ty ( 2 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 80 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 80 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 80 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 163 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 81 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 82 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 124 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 163 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 81 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 82 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 124 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 163 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 81 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 82 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 124 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 164 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 161 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 148 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 47 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 161 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 148 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 47 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 161 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 148 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 47 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 146 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 52 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 52 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 43 ) , mutabilityMut ))
│              ))
│
│           ListItem (StackFrame ( CALLER_CELL:Ty , DEST_CELL:Place , TARGET_CELL:MaybeBasicBlockIdx , UNWIND_CELL:UnwindAction , ListItem (newLocal ( ty ( 0 ) , mutabilityNot ))
│              ))
│         </stack>
│         ...
│       </kmir>
│       ...
│     </generatedTop>
│   #setLocalValue ( place ( ... local: local ( 2 ) , projection: .ProjectionElems )
│   function: std::vec::from_elem::<u8>
│   span: t/library/alloc/src/vec/mod.rs:3175
│
│  (10 steps)
├─ 5
│     <generatedTop>
│       <kmir>
│         <k>
│           #setArgFromStack ( 2 , operandMove ( place ( ... local: local ( 2 ) , projection: .ProjectionElems ) ) )
│           ~> #setArgsFromStack ( 3 , operandConstant ( constOperand ( ... span: span ( 48 ) , userTy: noUserTypeAnnotationIndex , const: mirConst ( ... kind: constantKindZeroSized , ty: ty ( 115 ) , id: mirConstId ( 64 ) ) ) )  .Operands )
│           ~> #execBlock ( basicBlock ( ... statements: .Statements , terminator: terminator ( ... kind: terminatorKindSwitchInt ( ... discr: operandCopy ( place ( ... local: local ( 1 ) , projection: .ProjectionElems ) ) , targets: switchTargets ( ... branches: branch ( 0 , basicBlockIdx ( 1 ) )  .Branches , otherwise: basicBlockIdx ( 2 ) ) ) , span: span ( 659 ) ) ) )
│         </k>
│         <currentFunc>
│           ty ( 125 )
│         </currentFunc>
│         <currentFrame>
│           <caller>
│             ty ( 155 )
│           </caller>
│           <dest>
│             place ( ... local: local ( 0 ) , projection: .ProjectionElems )
│           </dest>
│           <target>
│             someBasicBlockIdx ( basicBlockIdx ( 1 ) )
│           </target>
│           <unwind>
│             unwindActionContinue
│           </unwind>
│           <locals>
│             ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│
│             ListItem (typedValue ( Integer ( 0 , 8 , false ) , ty ( 16 ) , mutabilityNot ))
│
│             ListItem (newLocal ( ty ( 52 ) , mutabilityNot ))
│
│             ListItem (newLocal ( ty ( 115 ) , mutabilityNot ))
│
│             ListItem (newLocal ( ty ( 90 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│
│             ListItem (newLocal ( ty ( 47 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 118 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 132 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 13 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 129 ) , mutabilityNot ))
│
│             ListItem (newLocal ( ty ( 65 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 90 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 118 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 119 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 120 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 53 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 45 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 53 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 43 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│
│             ListItem (newLocal ( ty ( 64 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 43 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 119 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 120 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 52 ) , mutabilityMut ))
│           </locals>
│           ...
│         </currentFrame>
│         <stack>
│           ListItem (StackFrame ( ty ( -1 ) , place ( ... local: local ( 1 ) , projection: .ProjectionElems ) , someBasicBlockIdx ( basicBlockIdx ( 1 ) ) , unwindActionContinue , ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│              ListItem (typedValue ( Moved , ty ( 16 ) , mutabilityMut ))
│              ListItem (typedValue ( Integer ( 100 , 64 , false ) , ty ( 52 ) , mutabilityNot ))
│              ))
│
│           ListItem (StackFrame ( CURRENTFUNC_CELL:Ty , place ( ... local: local ( 0 ) , projection: .ProjectionElems ) , noBasicBlockIdx , unwindActionContinue , ListItem (newLocal ( ty ( 2 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 80 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 80 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 80 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 163 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 81 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 82 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 124 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 163 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 81 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 82 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 124 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 163 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 81 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 82 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 124 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 164 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 161 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 148 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 47 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 161 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 148 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 47 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 161 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 148 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 47 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 146 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 52 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 52 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 43 ) , mutabilityMut ))
│              ))
│
│           ListItem (StackFrame ( CALLER_CELL:Ty , DEST_CELL:Place , TARGET_CELL:MaybeBasicBlockIdx , UNWIND_CELL:UnwindAction , ListItem (newLocal ( ty ( 0 ) , mutabilityNot ))
│              ))
│         </stack>
│         ...
│       </kmir>
│       ...
│     </generatedTop>
│   #setArgFromStack ( 2 , operandMove ( place ( ... local: local ( 2 ) , projection
│   function: <u8 as std::vec::spec_from_elem::SpecFromElem>::from_elem::<std::alloc::Global>
│   span: no-location:0
│
│  (10 steps)
├─ 6
│     <generatedTop>
│       <kmir>
│         <k>
│           #execBlock ( basicBlock ( ... statements: .Statements , terminator: terminator ( ... kind: terminatorKindSwitchInt ( ... discr: operandCopy ( place ( ... local: local ( 1 ) , projection: .ProjectionElems ) ) , targets: switchTargets ( ... branches: branch ( 0 , basicBlockIdx ( 1 ) )  .Branches , otherwise: basicBlockIdx ( 2 ) ) ) , span: span ( 659 ) ) ) ) ~> .K
│         </k>
│         <currentFunc>
│           ty ( 125 )
│         </currentFunc>
│         <currentFrame>
│           <caller>
│             ty ( 155 )
│           </caller>
│           <dest>
│             place ( ... local: local ( 0 ) , projection: .ProjectionElems )
│           </dest>
│           <target>
│             someBasicBlockIdx ( basicBlockIdx ( 1 ) )
│           </target>
│           <unwind>
│             unwindActionContinue
│           </unwind>
│           <locals>
│             ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│
│             ListItem (typedValue ( Integer ( 0 , 8 , false ) , ty ( 16 ) , mutabilityNot ))
│
│             ListItem (typedValue ( Integer ( 100 , 64 , false ) , ty ( 52 ) , mutabilityNot ))
│
│             ListItem (typedValue ( Aggregate ( variantIdx ( 0 ) , .List ) , ty ( 115 ) , mutabilityNot ))
│
│             ListItem (newLocal ( ty ( 90 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│
│             ListItem (newLocal ( ty ( 47 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 118 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 132 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 13 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 129 ) , mutabilityNot ))
│
│             ListItem (newLocal ( ty ( 65 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 90 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 118 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 119 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 120 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 53 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 45 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 53 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 43 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│
│             ListItem (newLocal ( ty ( 64 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 43 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 119 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 120 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 52 ) , mutabilityMut ))
│           </locals>
│           ...
│         </currentFrame>
│         <stack>
│           ListItem (StackFrame ( ty ( -1 ) , place ( ... local: local ( 1 ) , projection: .ProjectionElems ) , someBasicBlockIdx ( basicBlockIdx ( 1 ) ) , unwindActionContinue , ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│              ListItem (typedValue ( Moved , ty ( 16 ) , mutabilityMut ))
│              ListItem (typedValue ( Moved , ty ( 52 ) , mutabilityMut ))
│              ))
│
│           ListItem (StackFrame ( CURRENTFUNC_CELL:Ty , place ( ... local: local ( 0 ) , projection: .ProjectionElems ) , noBasicBlockIdx , unwindActionContinue , ListItem (newLocal ( ty ( 2 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 80 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 80 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 80 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 163 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 81 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 82 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 124 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 163 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 81 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 82 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 124 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 163 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 81 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 82 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 124 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 164 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 161 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 148 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 47 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 161 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 148 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 47 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 161 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 148 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 47 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 146 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 52 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 52 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 43 ) , mutabilityMut ))
│              ))
│
│           ListItem (StackFrame ( CALLER_CELL:Ty , DEST_CELL:Place , TARGET_CELL:MaybeBasicBlockIdx , UNWIND_CELL:UnwindAction , ListItem (newLocal ( ty ( 0 ) , mutabilityNot ))
│              ))
│         </stack>
│         ...
│       </kmir>
│       ...
│     </generatedTop>
│   #execBlock ( basicBlock ( ... statements: .Statements , terminator: terminator (
│   function: <u8 as std::vec::spec_from_elem::SpecFromElem>::from_elem::<std::alloc::Global>
│   span: lloc/src/vec/spec_from_elem.rs:54
│
│  (10 steps)
├─ 7
│     <generatedTop>
│       <kmir>
│         <k>
│           #execStmts ( statement ( ... kind: statementKindStorageLive ( local ( 4 ) ) , span: span ( 662 ) )  statement ( ... kind: statementKindStorageLive ( local ( 10 ) ) , span: span ( 663 ) )  statement ( ... kind: statementKindStorageLive ( local ( 12 ) ) , span: span ( 663 ) )  statement ( ... kind: statementKindStorageLive ( local ( 13 ) ) , span: span ( 663 ) )  statement ( ... kind: statementKindStorageLive ( local ( 11 ) ) , span: span ( 661 ) )  .Statements )
│           ~> #execTerminator ( terminator ( ... kind: terminatorKindCall ( ... func: operandConstant ( constOperand ( ... span: span ( 660 ) , userTy: someUserTypeAnnotationIndex ( userTypeAnnotationIndex ( 0 ) ) , const: mirConst ( ... kind: constantKindZeroSized , ty: ty ( 126 ) , id: mirConstId ( 70 ) ) ) ) , args: operandCopy ( place ( ... local: local ( 2 ) , projection: .ProjectionElems ) )  operandConstant ( constOperand ( ... span: span ( 48 ) , userTy: noUserTypeAnnotationIndex , const: mirConst ( ... kind: constantKindAllocated ( allocation ( ... bytes: b"\x01" , provenance: provenanceMap ( ... ptrs: .ProvenanceMapEntries ) , align: align ( 1 ) , mutability: mutabilityMut ) ) , ty: ty ( 127 ) , id: mirConstId ( 74 ) ) ) )  operandMove ( place ( ... local: local ( 3 ) , projection: .ProjectionElems ) )  operandConstant ( constOperand ( ... span: span ( 48 ) , userTy: noUserTypeAnnotationIndex , const: mirConst ( ... kind: constantKindAllocated ( allocation ( ... bytes: b"\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00" , provenance: provenanceMap ( ... ptrs: .ProvenanceMapEntries ) , align: align ( 8 ) , mutability: mutabilityNot ) ) , ty: ty ( 131 ) , id: mirConstId ( 75 ) ) ) )  .Operands , destination: place ( ... local: local ( 11 ) , projection: .ProjectionElems ) , target: someBasicBlockIdx ( basicBlockIdx ( 4 ) ) , unwind: unwindActionContinue ) , span: span ( 661 ) ) )
│         </k>
│         <currentFunc>
│           ty ( 125 )
│         </currentFunc>
│         <currentFrame>
│           <caller>
│             ty ( 155 )
│           </caller>
│           <dest>
│             place ( ... local: local ( 0 ) , projection: .ProjectionElems )
│           </dest>
│           <target>
│             someBasicBlockIdx ( basicBlockIdx ( 1 ) )
│           </target>
│           <unwind>
│             unwindActionContinue
│           </unwind>
│           <locals>
│             ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│
│             ListItem (typedValue ( Integer ( 0 , 8 , false ) , ty ( 16 ) , mutabilityNot ))
│
│             ListItem (typedValue ( Integer ( 100 , 64 , false ) , ty ( 52 ) , mutabilityNot ))
│
│             ListItem (typedValue ( Aggregate ( variantIdx ( 0 ) , .List ) , ty ( 115 ) , mutabilityNot ))
│
│             ListItem (newLocal ( ty ( 90 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│
│             ListItem (newLocal ( ty ( 47 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 118 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 132 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 13 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 129 ) , mutabilityNot ))
│
│             ListItem (newLocal ( ty ( 65 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 90 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 118 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 119 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 120 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 53 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 45 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 53 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 43 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│
│             ListItem (newLocal ( ty ( 64 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 43 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 119 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 120 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 52 ) , mutabilityMut ))
│           </locals>
│           ...
│         </currentFrame>
│         <stack>
│           ListItem (StackFrame ( ty ( -1 ) , place ( ... local: local ( 1 ) , projection: .ProjectionElems ) , someBasicBlockIdx ( basicBlockIdx ( 1 ) ) , unwindActionContinue , ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│              ListItem (typedValue ( Moved , ty ( 16 ) , mutabilityMut ))
│              ListItem (typedValue ( Moved , ty ( 52 ) , mutabilityMut ))
│              ))
│
│           ListItem (StackFrame ( CURRENTFUNC_CELL:Ty , place ( ... local: local ( 0 ) , projection: .ProjectionElems ) , noBasicBlockIdx , unwindActionContinue , ListItem (newLocal ( ty ( 2 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 80 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 80 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 80 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 163 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 81 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 82 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 124 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 163 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 81 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 82 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 124 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 163 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 81 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 82 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 124 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 164 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 161 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 148 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 47 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 161 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 148 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 47 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 161 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 148 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 47 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 146 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 52 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 52 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 43 ) , mutabilityMut ))
│              ))
│
│           ListItem (StackFrame ( CALLER_CELL:Ty , DEST_CELL:Place , TARGET_CELL:MaybeBasicBlockIdx , UNWIND_CELL:UnwindAction , ListItem (newLocal ( ty ( 0 ) , mutabilityNot ))
│              ))
│         </stack>
│         ...
│       </kmir>
│       ...
│     </generatedTop>
│   #execStmts ( statement ( ... kind: statementKindStorageLive ( local ( 4 ) ) , sp
│   function: <u8 as std::vec::spec_from_elem::SpecFromElem>::from_elem::<std::alloc::Global>
│   span: lloc/src/vec/spec_from_elem.rs:55
│
│  (10 steps)
├─ 8
│     <generatedTop>
│       <kmir>
│         <k>
│           #execStmts ( .Statements )
│           ~> #execTerminator ( terminator ( ... kind: terminatorKindCall ( ... func: operandConstant ( constOperand ( ... span: span ( 660 ) , userTy: someUserTypeAnnotationIndex ( userTypeAnnotationIndex ( 0 ) ) , const: mirConst ( ... kind: constantKindZeroSized , ty: ty ( 126 ) , id: mirConstId ( 70 ) ) ) ) , args: operandCopy ( place ( ... local: local ( 2 ) , projection: .ProjectionElems ) )  operandConstant ( constOperand ( ... span: span ( 48 ) , userTy: noUserTypeAnnotationIndex , const: mirConst ( ... kind: constantKindAllocated ( allocation ( ... bytes: b"\x01" , provenance: provenanceMap ( ... ptrs: .ProvenanceMapEntries ) , align: align ( 1 ) , mutability: mutabilityMut ) ) , ty: ty ( 127 ) , id: mirConstId ( 74 ) ) ) )  operandMove ( place ( ... local: local ( 3 ) , projection: .ProjectionElems ) )  operandConstant ( constOperand ( ... span: span ( 48 ) , userTy: noUserTypeAnnotationIndex , const: mirConst ( ... kind: constantKindAllocated ( allocation ( ... bytes: b"\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00" , provenance: provenanceMap ( ... ptrs: .ProvenanceMapEntries ) , align: align ( 8 ) , mutability: mutabilityNot ) ) , ty: ty ( 131 ) , id: mirConstId ( 75 ) ) ) )  .Operands , destination: place ( ... local: local ( 11 ) , projection: .ProjectionElems ) , target: someBasicBlockIdx ( basicBlockIdx ( 4 ) ) , unwind: unwindActionContinue ) , span: span ( 661 ) ) )
│         </k>
│         <currentFunc>
│           ty ( 125 )
│         </currentFunc>
│         <currentFrame>
│           <caller>
│             ty ( 155 )
│           </caller>
│           <dest>
│             place ( ... local: local ( 0 ) , projection: .ProjectionElems )
│           </dest>
│           <target>
│             someBasicBlockIdx ( basicBlockIdx ( 1 ) )
│           </target>
│           <unwind>
│             unwindActionContinue
│           </unwind>
│           <locals>
│             ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│
│             ListItem (typedValue ( Integer ( 0 , 8 , false ) , ty ( 16 ) , mutabilityNot ))
│
│             ListItem (typedValue ( Integer ( 100 , 64 , false ) , ty ( 52 ) , mutabilityNot ))
│
│             ListItem (typedValue ( Aggregate ( variantIdx ( 0 ) , .List ) , ty ( 115 ) , mutabilityNot ))
│
│             ListItem (newLocal ( ty ( 90 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│
│             ListItem (newLocal ( ty ( 47 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 118 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 132 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 13 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 129 ) , mutabilityNot ))
│
│             ListItem (newLocal ( ty ( 65 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 90 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 118 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 119 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 120 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 53 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 45 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 53 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 43 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│
│             ListItem (newLocal ( ty ( 64 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 43 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 119 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 120 ) , mutabilityMut ))
│
│             ListItem (newLocal ( ty ( 52 ) , mutabilityMut ))
│           </locals>
│           ...
│         </currentFrame>
│         <stack>
│           ListItem (StackFrame ( ty ( -1 ) , place ( ... local: local ( 1 ) , projection: .ProjectionElems ) , someBasicBlockIdx ( basicBlockIdx ( 1 ) ) , unwindActionContinue , ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│              ListItem (typedValue ( Moved , ty ( 16 ) , mutabilityMut ))
│              ListItem (typedValue ( Moved , ty ( 52 ) , mutabilityMut ))
│              ))
│
│           ListItem (StackFrame ( CURRENTFUNC_CELL:Ty , place ( ... local: local ( 0 ) , projection: .ProjectionElems ) , noBasicBlockIdx , unwindActionContinue , ListItem (newLocal ( ty ( 2 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 80 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 80 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 80 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 163 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 81 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 82 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 124 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 163 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 81 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 82 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 124 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 163 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 81 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 82 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 5 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 124 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 164 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 161 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 148 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 47 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 161 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 148 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 47 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 161 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 148 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 47 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 146 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 52 ) , mutabilityNot ))
│              ListItem (newLocal ( ty ( 52 ) , mutabilityMut ))
│              ListItem (newLocal ( ty ( 43 ) , mutabilityMut ))
│              ))
│
│           ListItem (StackFrame ( CALLER_CELL:Ty , DEST_CELL:Place , TARGET_CELL:MaybeBasicBlockIdx , UNWIND_CELL:UnwindAction , ListItem (newLocal ( ty ( 0 ) , mutabilityNot ))
│              ))
│         </stack>
│         ...
│       </kmir>
│       ...
│     </generatedTop>
│   #execStmts ( .Statements )
~> #execTerminator ( terminator ( ... kind: terminato
│   function: <u8 as std::vec::spec_from_elem::SpecFromElem>::from_elem::<std::alloc::Global>
│   span: t/library/alloc/src/raw_vec.rs:448
│
│  (1 step)
└─ 9 (stuck, leaf)
      <generatedTop>
        <kmir>
          <k>
            #execTerminator ( terminator ( ... kind: terminatorKindCall ( ... func: operandConstant ( constOperand ( ... span: span ( 660 ) , userTy: someUserTypeAnnotationIndex ( userTypeAnnotationIndex ( 0 ) ) , const: mirConst ( ... kind: constantKindZeroSized , ty: ty ( 126 ) , id: mirConstId ( 70 ) ) ) ) , args: operandCopy ( place ( ... local: local ( 2 ) , projection: .ProjectionElems ) )  operandConstant ( constOperand ( ... span: span ( 48 ) , userTy: noUserTypeAnnotationIndex , const: mirConst ( ... kind: constantKindAllocated ( allocation ( ... bytes: b"\x01" , provenance: provenanceMap ( ... ptrs: .ProvenanceMapEntries ) , align: align ( 1 ) , mutability: mutabilityMut ) ) , ty: ty ( 127 ) , id: mirConstId ( 74 ) ) ) )  operandMove ( place ( ... local: local ( 3 ) , projection: .ProjectionElems ) )  operandConstant ( constOperand ( ... span: span ( 48 ) , userTy: noUserTypeAnnotationIndex , const: mirConst ( ... kind: constantKindAllocated ( allocation ( ... bytes: b"\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00" , provenance: provenanceMap ( ... ptrs: .ProvenanceMapEntries ) , align: align ( 8 ) , mutability: mutabilityNot ) ) , ty: ty ( 131 ) , id: mirConstId ( 75 ) ) ) )  .Operands , destination: place ( ... local: local ( 11 ) , projection: .ProjectionElems ) , target: someBasicBlockIdx ( basicBlockIdx ( 4 ) ) , unwind: unwindActionContinue ) , span: span ( 661 ) ) ) ~> .K
          </k>
          <currentFunc>
            ty ( 125 )
          </currentFunc>
          <currentFrame>
            <caller>
              ty ( 155 )
            </caller>
            <dest>
              place ( ... local: local ( 0 ) , projection: .ProjectionElems )
            </dest>
            <target>
              someBasicBlockIdx ( basicBlockIdx ( 1 ) )
            </target>
            <unwind>
              unwindActionContinue
            </unwind>
            <locals>
              ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))

              ListItem (typedValue ( Integer ( 0 , 8 , false ) , ty ( 16 ) , mutabilityNot ))

              ListItem (typedValue ( Integer ( 100 , 64 , false ) , ty ( 52 ) , mutabilityNot ))

              ListItem (typedValue ( Aggregate ( variantIdx ( 0 ) , .List ) , ty ( 115 ) , mutabilityNot ))

              ListItem (newLocal ( ty ( 90 ) , mutabilityMut ))

              ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))

              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))

              ListItem (newLocal ( ty ( 47 ) , mutabilityMut ))

              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))

              ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))

              ListItem (newLocal ( ty ( 118 ) , mutabilityMut ))

              ListItem (newLocal ( ty ( 132 ) , mutabilityMut ))

              ListItem (newLocal ( ty ( 13 ) , mutabilityMut ))

              ListItem (newLocal ( ty ( 129 ) , mutabilityNot ))

              ListItem (newLocal ( ty ( 65 ) , mutabilityMut ))

              ListItem (newLocal ( ty ( 90 ) , mutabilityMut ))

              ListItem (newLocal ( ty ( 118 ) , mutabilityMut ))

              ListItem (newLocal ( ty ( 119 ) , mutabilityMut ))

              ListItem (newLocal ( ty ( 120 ) , mutabilityMut ))

              ListItem (newLocal ( ty ( 53 ) , mutabilityMut ))

              ListItem (newLocal ( ty ( 45 ) , mutabilityMut ))

              ListItem (newLocal ( ty ( 53 ) , mutabilityMut ))

              ListItem (newLocal ( ty ( 43 ) , mutabilityMut ))

              ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))

              ListItem (newLocal ( ty ( 64 ) , mutabilityMut ))

              ListItem (newLocal ( ty ( 43 ) , mutabilityMut ))

              ListItem (newLocal ( ty ( 119 ) , mutabilityMut ))

              ListItem (newLocal ( ty ( 120 ) , mutabilityMut ))

              ListItem (newLocal ( ty ( 52 ) , mutabilityMut ))
            </locals>
            ...
          </currentFrame>
          <stack>
            ListItem (StackFrame ( ty ( -1 ) , place ( ... local: local ( 1 ) , projection: .ProjectionElems ) , someBasicBlockIdx ( basicBlockIdx ( 1 ) ) , unwindActionContinue , ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
               ListItem (typedValue ( Moved , ty ( 16 ) , mutabilityMut ))
               ListItem (typedValue ( Moved , ty ( 52 ) , mutabilityMut ))
               ))

            ListItem (StackFrame ( CURRENTFUNC_CELL:Ty , place ( ... local: local ( 0 ) , projection: .ProjectionElems ) , noBasicBlockIdx , unwindActionContinue , ListItem (newLocal ( ty ( 2 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 117 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 117 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 117 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 80 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 80 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 80 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 5 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 163 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 81 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 82 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 5 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 124 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 5 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 163 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 81 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 82 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 5 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 124 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 117 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 5 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 163 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 81 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 82 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 5 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 124 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 164 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 161 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 148 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 47 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 161 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 148 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 47 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 161 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 148 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 47 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 3 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 2 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 146 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 52 ) , mutabilityNot ))
               ListItem (newLocal ( ty ( 52 ) , mutabilityMut ))
               ListItem (newLocal ( ty ( 43 ) , mutabilityMut ))
               ))

            ListItem (StackFrame ( CALLER_CELL:Ty , DEST_CELL:Place , TARGET_CELL:MaybeBasicBlockIdx , UNWIND_CELL:UnwindAction , ListItem (newLocal ( ty ( 0 ) , mutabilityNot ))
               ))
          </stack>
          ...
        </kmir>
        ...
      </generatedTop>
    #execTerminator ( terminator ( ... kind: terminatorKindCall ( ... func: operandC
    function: <u8 as std::vec::spec_from_elem::SpecFromElem>::from_elem::<std::alloc::Global>
    span: t/library/alloc/src/raw_vec.rs:448


┌─ 2 (root, leaf, target, terminal)
│     <generatedTop>
│       <kmir>
│         <k>
│           #EndProgram ~> .K
│         </k>
│         ...
│       </kmir>
│       ...
│     </generatedTop>
│   #EndProgram ~> .K



