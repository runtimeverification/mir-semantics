
┌─ 1 (root, init)
│   #execTerminator ( terminator ( ... kind: terminatorKindCall ( ... func: operandC
│   span: src/rust/library/std/src/rt.rs:194
│
│  (10 steps)
├─ 3
│   operandConstant ( constOperand ( ... span: span ( 91 ) , userTy: noUserTypeAnnot
│   function: main
│   span: perties/mir-semantics/deref.rs:3
│
│  (10 steps)
├─ 4
│   rvalueRef ( region ( ... kind: regionKindReErased ) , borrowKindShared , place (
│   function: main
│   span: perties/mir-semantics/deref.rs:10
│
│  (10 steps)
├─ 5
│   #traverseProjection ( toLocal ( 2 ) , Reference ( 0 , place ( ... local: local (
│   function: main
│   span: library/core/src/macros/mod.rs:44
│
│  (10 steps)
├─ 6
│   #traverseProjection ( toLocal ( 3 ) , Integer ( 42 , 32 , true ) , .ProjectionEl
│   function: main
│   span: library/core/src/macros/mod.rs:44
│
│  (10 steps)
├─ 7
│   thunk ( #decodeConstant ( constantKindAllocated ( allocation ( ... bytes: b"\x00
│   function: main
│   span: library/core/src/macros/mod.rs:44
│
│  (10 steps)
├─ 8
│   #traverseProjection ( toLocal ( 5 ) , Reference ( 0 , place ( ... local: local (
│   function: main
│   span: library/core/src/macros/mod.rs:45
│
│  (10 steps)
├─ 9
│   ListItem (Reference ( 0 , place ( ... local: local ( 3 ) , projection: .Projecti
│   function: main
│   span: library/core/src/macros/mod.rs:45
│
│  (10 steps)
├─ 10
│   Reference ( 0 , place ( ... local: local ( 3 ) , projection: .ProjectionElems )
│   function: main
│   span: library/core/src/macros/mod.rs:45
│
│  (10 steps)
├─ 11
│   #setLocalValue ( place ( ... local: local ( 8 ) , projection: .ProjectionElems )
│   function: main
│   span: library/core/src/macros/mod.rs:46
│
│  (10 steps)
├─ 12
│   #setLocalValue ( place ( ... local: local ( 10 ) , projection: .ProjectionElems
│   function: main
│   span: library/core/src/macros/mod.rs:46
│
│  (6 steps)
└─ 13 (stuck, leaf)
    #traverseProjection ( toLocal ( 8 ) , thunk ( #decodeConstant ( constantKindAllo
    function: main
    span: library/core/src/macros/mod.rs:46


┌─ 2 (root, leaf, target, terminal)
│   #EndProgram ~> .K


Node 11:

<generatedTop>
  <kmir>
    <k>
      #setLocalValue ( place ( ... local: local ( 8 ) , projection: .ProjectionElems ) , thunk ( #decodeConstant ( constantKindAllocated ( allocation ( ... bytes: b"\x00\x00\x00\x00\x00\x00\x00\x00" , provenance: provenanceMap ( ... ptrs: provenanceMapEntry ( ... provSize: 0 , allocId: allocId ( 0 ) )  .ProvenanceMapEntries ) , align: align ( 8 ) , mutability: mutabilityMut ) ) , ty ( 25 ) , typeInfoRefType ( ty ( 16 ) ) ) ) )
      ~> #execStmts ( statement ( ... kind: statementKindAssign ( ... place: place ( ... local: local ( 10 ) , projection: .ProjectionElems ) , rvalue: rvalueUse ( operandCopy ( place ( ... local: local ( 7 ) , projection: projectionElemDeref  .ProjectionElems ) ) ) ) , span: span ( 100 ) )  statement ( ... kind: statementKindAssign ( ... place: place ( ... local: local ( 11 ) , projection: .ProjectionElems ) , rvalue: rvalueUse ( operandCopy ( place ( ... local: local ( 8 ) , projection: projectionElemDeref  .ProjectionElems ) ) ) ) , span: span ( 101 ) )  statement ( ... kind: statementKindAssign ( ... place: place ( ... local: local ( 9 ) , projection: .ProjectionElems ) , rvalue: rvalueBinaryOp ( binOpEq , operandMove ( place ( ... local: local ( 10 ) , projection: .ProjectionElems ) ) , operandMove ( place ( ... local: local ( 11 ) , projection: .ProjectionElems ) ) ) ) , span: span ( 90 ) )  .Statements )
      ~> #execTerminator ( terminator ( ... kind: terminatorKindSwitchInt ( ... discr: operandMove ( place ( ... local: local ( 9 ) , projection: .ProjectionElems ) ) , targets: switchTargets ( ... branches: branch ( 0 , basicBlockIdx ( 2 ) )  .Branches , otherwise: basicBlockIdx ( 1 ) ) ) , span: span ( 90 ) ) )
    </k>
    <currentFunc>
      ty ( -1 )
    </currentFunc>
    <currentFrame>
      <dest>
        place ( ... local: local ( 0 ) , projection: .ProjectionElems )
      </dest>
      <target>
        noBasicBlockIdx
      </target>
      <unwind>
        unwindActionContinue
      </unwind>
      <locals>
        ListItem (newLocal ( ty ( 1 ) , mutabilityMut ))
         ListItem (typedValue ( Aggregate ( variantIdx ( 0 ) , ListItem (Integer ( 42 , 32 , true ))
           ) , ty ( 42 ) , mutabilityNot ))
         ListItem (typedValue ( Reference ( 0 , place ( ... local: local ( 1 ) , projection: .ProjectionElems ) , mutabilityNot , noMetadata ) , ty ( 43 ) , mutabilityNot ))
         ListItem (typedValue ( Integer ( 42 , 32 , true ) , ty ( 16 ) , mutabilityNot ))
         ListItem (typedValue ( Aggregate ( variantIdx ( 0 ) , ListItem (Reference ( 0 , place ( ... local: local ( 3 ) , projection: .ProjectionElems ) , mutabilityNot , noMetadata ))
           ListItem (thunk ( #decodeConstant ( constantKindAllocated ( allocation ( ... bytes: b"\x00\x00\x00\x00\x00\x00\x00\x00" , provenance: provenanceMap ( ... ptrs: provenanceMapEntry ( ... provSize: 0 , allocId: allocId ( 0 ) )  .ProvenanceMapEntries ) , align: align ( 8 ) , mutability: mutabilityMut ) ) , ty ( 25 ) , typeInfoRefType ( ty ( 16 ) ) ) ))
           ) , ty ( 44 ) , mutabilityMut ))
         ListItem (typedValue ( Moved , ty ( 25 ) , mutabilityMut ))
         ListItem (typedValue ( Moved , ty ( 25 ) , mutabilityMut ))
         ListItem (typedValue ( Reference ( 0 , place ( ... local: local ( 3 ) , projection: .ProjectionElems ) , mutabilityNot , noMetadata ) , ty ( 25 ) , mutabilityNot ))
         ListItem (newLocal ( ty ( 25 ) , mutabilityNot ))
         ListItem (newLocal ( ty ( 45 ) , mutabilityMut ))
         ListItem (newLocal ( ty ( 16 ) , mutabilityMut ))
         ListItem (newLocal ( ty ( 16 ) , mutabilityMut ))
         ListItem (newLocal ( ty ( 38 ) , mutabilityNot ))
         ListItem (newLocal ( ty ( 37 ) , mutabilityNot ))
         ListItem (newLocal ( ty ( 39 ) , mutabilityMut ))
      </locals>
      ...
    </currentFrame>
    <stack>
      ListItem (StackFrame ( CALLER_CELL:Ty , DEST_CELL:Place , TARGET_CELL:MaybeBasicBlockIdx , UNWIND_CELL:UnwindAction , ListItem (newLocal ( ty ( 0 ) , mutabilityNot ))
         ))
    </stack>
    ...
  </kmir>
  ...
</generatedTop>



Node 12:

<generatedTop>
  <kmir>
    <k>
      #setLocalValue ( place ( ... local: local ( 10 ) , projection: .ProjectionElems ) , Integer ( 42 , 32 , true ) )
      ~> #execStmts ( statement ( ... kind: statementKindAssign ( ... place: place ( ... local: local ( 11 ) , projection: .ProjectionElems ) , rvalue: rvalueUse ( operandCopy ( place ( ... local: local ( 8 ) , projection: projectionElemDeref  .ProjectionElems ) ) ) ) , span: span ( 101 ) )  statement ( ... kind: statementKindAssign ( ... place: place ( ... local: local ( 9 ) , projection: .ProjectionElems ) , rvalue: rvalueBinaryOp ( binOpEq , operandMove ( place ( ... local: local ( 10 ) , projection: .ProjectionElems ) ) , operandMove ( place ( ... local: local ( 11 ) , projection: .ProjectionElems ) ) ) ) , span: span ( 90 ) )  .Statements )
      ~> #execTerminator ( terminator ( ... kind: terminatorKindSwitchInt ( ... discr: operandMove ( place ( ... local: local ( 9 ) , projection: .ProjectionElems ) ) , targets: switchTargets ( ... branches: branch ( 0 , basicBlockIdx ( 2 ) )  .Branches , otherwise: basicBlockIdx ( 1 ) ) ) , span: span ( 90 ) ) )
    </k>
    <currentFunc>
      ty ( -1 )
    </currentFunc>
    <currentFrame>
      <dest>
        place ( ... local: local ( 0 ) , projection: .ProjectionElems )
      </dest>
      <target>
        noBasicBlockIdx
      </target>
      <unwind>
        unwindActionContinue
      </unwind>
      <locals>
        ListItem (newLocal ( ty ( 1 ) , mutabilityMut ))
         ListItem (typedValue ( Aggregate ( variantIdx ( 0 ) , ListItem (Integer ( 42 , 32 , true ))
           ) , ty ( 42 ) , mutabilityNot ))
         ListItem (typedValue ( Reference ( 0 , place ( ... local: local ( 1 ) , projection: .ProjectionElems ) , mutabilityNot , noMetadata ) , ty ( 43 ) , mutabilityNot ))
         ListItem (typedValue ( Integer ( 42 , 32 , true ) , ty ( 16 ) , mutabilityNot ))
         ListItem (typedValue ( Aggregate ( variantIdx ( 0 ) , ListItem (Reference ( 0 , place ( ... local: local ( 3 ) , projection: .ProjectionElems ) , mutabilityNot , noMetadata ))
           ListItem (thunk ( #decodeConstant ( constantKindAllocated ( allocation ( ... bytes: b"\x00\x00\x00\x00\x00\x00\x00\x00" , provenance: provenanceMap ( ... ptrs: provenanceMapEntry ( ... provSize: 0 , allocId: allocId ( 0 ) )  .ProvenanceMapEntries ) , align: align ( 8 ) , mutability: mutabilityMut ) ) , ty ( 25 ) , typeInfoRefType ( ty ( 16 ) ) ) ))
           ) , ty ( 44 ) , mutabilityMut ))
         ListItem (typedValue ( Moved , ty ( 25 ) , mutabilityMut ))
         ListItem (typedValue ( Moved , ty ( 25 ) , mutabilityMut ))
         ListItem (typedValue ( Reference ( 0 , place ( ... local: local ( 3 ) , projection: .ProjectionElems ) , mutabilityNot , noMetadata ) , ty ( 25 ) , mutabilityNot ))
         ListItem (typedValue ( thunk ( #decodeConstant ( constantKindAllocated ( allocation ( ... bytes: b"\x00\x00\x00\x00\x00\x00\x00\x00" , provenance: provenanceMap ( ... ptrs: provenanceMapEntry ( ... provSize: 0 , allocId: allocId ( 0 ) )  .ProvenanceMapEntries ) , align: align ( 8 ) , mutability: mutabilityMut ) ) , ty ( 25 ) , typeInfoRefType ( ty ( 16 ) ) ) ) , ty ( 25 ) , mutabilityNot ))
         ListItem (newLocal ( ty ( 45 ) , mutabilityMut ))
         ListItem (newLocal ( ty ( 16 ) , mutabilityMut ))
         ListItem (newLocal ( ty ( 16 ) , mutabilityMut ))
         ListItem (newLocal ( ty ( 38 ) , mutabilityNot ))
         ListItem (newLocal ( ty ( 37 ) , mutabilityNot ))
         ListItem (newLocal ( ty ( 39 ) , mutabilityMut ))
      </locals>
      ...
    </currentFrame>
    <stack>
      ListItem (StackFrame ( CALLER_CELL:Ty , DEST_CELL:Place , TARGET_CELL:MaybeBasicBlockIdx , UNWIND_CELL:UnwindAction , ListItem (newLocal ( ty ( 0 ) , mutabilityNot ))
         ))
    </stack>
    ...
  </kmir>
  ...
</generatedTop>



Node 13:

<generatedTop>
  <kmir>
    <k>
      #traverseProjection ( toLocal ( 8 ) , thunk ( #decodeConstant ( constantKindAllocated ( allocation ( ... bytes: b"\x00\x00\x00\x00\x00\x00\x00\x00" , provenance: provenanceMap ( ... ptrs: provenanceMapEntry ( ... provSize: 0 , allocId: allocId ( 0 ) )  .ProvenanceMapEntries ) , align: align ( 8 ) , mutability: mutabilityMut ) ) , ty ( 25 ) , typeInfoRefType ( ty ( 16 ) ) ) ) , projectionElemDeref  .ProjectionElems , .Contexts )
      ~> #readProjection ( false )
      ~> #freezer#setLocalValue(_,_)_RT-DATA_KItem_Place_Evaluation1_ ( place ( ... local: local ( 11 ) , projection: .ProjectionElems ) ~> .K )
      ~> #execStmts ( statement ( ... kind: statementKindAssign ( ... place: place ( ... local: local ( 9 ) , projection: .ProjectionElems ) , rvalue: rvalueBinaryOp ( binOpEq , operandMove ( place ( ... local: local ( 10 ) , projection: .ProjectionElems ) ) , operandMove ( place ( ... local: local ( 11 ) , projection: .ProjectionElems ) ) ) ) , span: span ( 90 ) )  .Statements )
      ~> #execTerminator ( terminator ( ... kind: terminatorKindSwitchInt ( ... discr: operandMove ( place ( ... local: local ( 9 ) , projection: .ProjectionElems ) ) , targets: switchTargets ( ... branches: branch ( 0 , basicBlockIdx ( 2 ) )  .Branches , otherwise: basicBlockIdx ( 1 ) ) ) , span: span ( 90 ) ) )
    </k>
    <currentFunc>
      ty ( -1 )
    </currentFunc>
    <currentFrame>
      <dest>
        place ( ... local: local ( 0 ) , projection: .ProjectionElems )
      </dest>
      <target>
        noBasicBlockIdx
      </target>
      <unwind>
        unwindActionContinue
      </unwind>
      <locals>
        ListItem (newLocal ( ty ( 1 ) , mutabilityMut ))
         ListItem (typedValue ( Aggregate ( variantIdx ( 0 ) , ListItem (Integer ( 42 , 32 , true ))
           ) , ty ( 42 ) , mutabilityNot ))
         ListItem (typedValue ( Reference ( 0 , place ( ... local: local ( 1 ) , projection: .ProjectionElems ) , mutabilityNot , noMetadata ) , ty ( 43 ) , mutabilityNot ))
         ListItem (typedValue ( Integer ( 42 , 32 , true ) , ty ( 16 ) , mutabilityNot ))
         ListItem (typedValue ( Aggregate ( variantIdx ( 0 ) , ListItem (Reference ( 0 , place ( ... local: local ( 3 ) , projection: .ProjectionElems ) , mutabilityNot , noMetadata ))
           ListItem (thunk ( #decodeConstant ( constantKindAllocated ( allocation ( ... bytes: b"\x00\x00\x00\x00\x00\x00\x00\x00" , provenance: provenanceMap ( ... ptrs: provenanceMapEntry ( ... provSize: 0 , allocId: allocId ( 0 ) )  .ProvenanceMapEntries ) , align: align ( 8 ) , mutability: mutabilityMut ) ) , ty ( 25 ) , typeInfoRefType ( ty ( 16 ) ) ) ))
           ) , ty ( 44 ) , mutabilityMut ))
         ListItem (typedValue ( Moved , ty ( 25 ) , mutabilityMut ))
         ListItem (typedValue ( Moved , ty ( 25 ) , mutabilityMut ))
         ListItem (typedValue ( Reference ( 0 , place ( ... local: local ( 3 ) , projection: .ProjectionElems ) , mutabilityNot , noMetadata ) , ty ( 25 ) , mutabilityNot ))
         ListItem (typedValue ( thunk ( #decodeConstant ( constantKindAllocated ( allocation ( ... bytes: b"\x00\x00\x00\x00\x00\x00\x00\x00" , provenance: provenanceMap ( ... ptrs: provenanceMapEntry ( ... provSize: 0 , allocId: allocId ( 0 ) )  .ProvenanceMapEntries ) , align: align ( 8 ) , mutability: mutabilityMut ) ) , ty ( 25 ) , typeInfoRefType ( ty ( 16 ) ) ) ) , ty ( 25 ) , mutabilityNot ))
         ListItem (newLocal ( ty ( 45 ) , mutabilityMut ))
         ListItem (typedValue ( Integer ( 42 , 32 , true ) , ty ( 16 ) , mutabilityMut ))
         ListItem (newLocal ( ty ( 16 ) , mutabilityMut ))
         ListItem (newLocal ( ty ( 38 ) , mutabilityNot ))
         ListItem (newLocal ( ty ( 37 ) , mutabilityNot ))
         ListItem (newLocal ( ty ( 39 ) , mutabilityMut ))
      </locals>
      ...
    </currentFrame>
    <stack>
      ListItem (StackFrame ( CALLER_CELL:Ty , DEST_CELL:Place , TARGET_CELL:MaybeBasicBlockIdx , UNWIND_CELL:UnwindAction , ListItem (newLocal ( ty ( 0 ) , mutabilityNot ))
         ))
    </stack>
    ...
  </kmir>
  ...
</generatedTop>



