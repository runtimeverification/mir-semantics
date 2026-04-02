module ASSERT-TRUE-MAIN-SUMMARY
    
    
    rule [BASIC-BLOCK-1-TO-3]: <kmir>
           <k>
             ( #execTerminator ( terminator ( ... kind: terminatorKindCall ( ... func: operandConstant ( constOperand ( ... span: span ( 0 ) , userTy: noUserTypeAnnotationIndex , const: mirConst ( ... kind: constantKindZeroSized , ty: ty ( -1 ) , id: mirConstId ( 0 ) ) ) ) , args: .Operands , destination: place ( ... local: local ( 0 ) , projection: .ProjectionElems ) , target: noBasicBlockIdx , unwind: unwindActionContinue ) , span: span ( 0 ) ) ) => #EndProgram ~> .K )
           </k>
           <retVal>
             noReturn
           </retVal>
           <currentFunc>
             ty ( -1 )
           </currentFunc>
           <currentFrame>
             <frameId>
               ( 0 => 1 )
             </frameId>
             <currentBody>
               ( .List => ListItem ( basicBlock ( ... statements: .Statements , terminator: terminator ( ... kind: terminatorKindReturn , span: span ( 50 ) ) ) ) )
             </currentBody>
             <caller>
               ty ( -1 )
             </caller>
             <dest>
               place ( ... local: local ( ( -1 => 0 ) ) , projection: .ProjectionElems )
             </dest>
             <target>
               noBasicBlockIdx
             </target>
             <unwind>
               ( unwindActionUnreachable => unwindActionContinue )
             </unwind>
             <locals>
               ListItem ( newLocal ( ty ( ( 0 => 1 ) ) , ( mutabilityNot => mutabilityMut ) ) )
             </locals>
           </currentFrame>
           <stack>
             ( .List => ListItem ( StackFrame ( 0 , ty ( -1 ) , place ( ... local: local ( -1 ) , projection: .ProjectionElems ) , noBasicBlockIdx , unwindActionUnreachable , ListItem ( newLocal ( ty ( 0 ) , mutabilityNot ) ) ) ) )
           </stack>
           <nextFrameId>
             ( 1 => 2 )
           </nextFrameId>
           <addressMap>
             .Map
           </addressMap>
           <nextAddress>
             4096
           </nextAddress>
           <exposedSet>
             .Set
           </exposedSet>
         </kmir>
      [priority(20), label(BASIC-BLOCK-1-TO-3)]

endmodule