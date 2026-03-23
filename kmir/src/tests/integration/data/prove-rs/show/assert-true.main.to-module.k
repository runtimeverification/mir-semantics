module ASSERT-TRUE-MAIN-SUMMARY
    
    
    rule [BASIC-BLOCK-1-TO-3]: <kmir>
           <k>
             ( #execTerminator ( terminator ( ... kind: terminatorKindCall ( ... func: operandConstant ( constOperand ( ... span: span ( 0 ) , userTy: noUserTypeAnnotationIndex , const: mirConst ( ... kind: constantKindZeroSized , ty: ty ( -1 ) , id: mirConstId ( 0 ) ) ) ) , args: .Operands , destination: place ( ... local: local ( 0 ) , projection: .ProjectionElems ) , target: noBasicBlockIdx , unwind: unwindActionContinue ) , span: span ( 0 ) ) ) => #EndProgram ~> .K )
           </k>
           <retVal>
             _RETVAL_CELL
           </retVal>
           <currentFunc>
             ( CURRENTFUNC_CELL => ty ( -1 ) )
           </currentFunc>
           <currentFrame>
             <currentBody>
               ( _CURRENTBODY_CELL => ListItem ( basicBlock ( ... statements: .Statements , terminator: terminator ( ... kind: terminatorKindReturn , span: span ( 50 ) ) ) ) )
             </currentBody>
             <caller>
               ( CALLER_CELL => CURRENTFUNC_CELL:Ty )
             </caller>
             <dest>
               ( DEST_CELL => place ( ... local: local ( 0 ) , projection: .ProjectionElems ) )
             </dest>
             <target>
               ( TARGET_CELL => noBasicBlockIdx )
             </target>
             <unwind>
               ( UNWIND_CELL => unwindActionContinue )
             </unwind>
             <locals>
               ListItem ( newLocal ( ty ( ( 0 => 1 ) ) , ( mutabilityNot => mutabilityMut ) ) )
             </locals>
           </currentFrame>
           <stack>
             ( .List => ListItem ( StackFrame ( CALLER_CELL:Ty , DEST_CELL:Place , TARGET_CELL:MaybeBasicBlockIdx , UNWIND_CELL:UnwindAction , ListItem ( newLocal ( ty ( 0 ) , mutabilityNot ) ) ) ) )
           </stack>
         </kmir>
      [priority(20), label(BASIC-BLOCK-1-TO-3)]

endmodule