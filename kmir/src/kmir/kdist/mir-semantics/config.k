requires "kmir-ast.k"

module KMIR-CONFIGURATION
  imports KMIR-AST
  imports LIST
  imports MAP

  syntax K ::= #call( Operand, Operands, Place, Target, Unwind )
             | #call( FunctionGlobal, Operands, Place, Target, Unwind )
             | #goto( Int )

  rule <k> #call( operandConstant(constant(_SPAN, _, const( constantKindZeroSized, ty( _ID, tyKindRigidTy(rigidTyFnDef( FNDEF, _ ))), _ID ))),
                  Args,
                  Dest,
                  Target,
                  Unwind )
        => #call( Mem [ FNDEF ], Args, Dest, Target, Unwind )
           ...
       </k>
       <memory> Mem </memory>
    requires funcName in_keys( Mem )
     andBool Function( _, _ ) :=K Mem [ funcName ]

  rule <k> #call( Function( CalleeBody, ArgCount, LocalCount ), Args, Dest, Target, Unwind )
        => basicBlock( .List, terminator( terminatorKindGoto( basicBlockIdx( 0 ) ), span( 0 )))
           ...
       </k>
       <callStack> Stack => ListItem(CallRecord( FnAddr( CallerAddr ), Target, Dest, Unwind, CallerLocals )) </callStack>
       <body> CallerBody => CalleeBody </body>
       <locals> CallerLocals => (ListItem(operandUninit()) Args) makeList( LocalCount - ArgCount, operandUnint() ) </locals>
       <funcAddr> CallerAddr </funcAddr>

  // Terminators

  syntax K ::= #goto ( 

  rule <k> basicBlock( .List, terminator( terminatorKindGoto( basicBlockIdx( N ) ), _SPAN ))
        => #goto( N )
       </k>

  rule <k> basicBlock( .List, terminator( terminatorKindCall( FuncOp, Args, Dest, Target, Unwind ), _SPAN ))
        => #call( FuncOp, Args, Dest, Target, Unwind )
       </k>

  rule <k> #goto( N ) => Blocks [ N ] </k>
       <body> Blocks </body>
    requires N < size(Blocks)

  syntax Operand        ::= operandUnint()
  syntax Global         ::= FunctionGlobal
  syntax FunctionGlobal ::= Function( funcBody: BasicBlocks, argCount: Int, localCount: Int )
  syntax CallStackItem  ::= CallRecord( FuncAddress, MaybeBasicBlockIdx, Place, UnwindAction, List)
  syntax FuncAddress    ::= FnAddr( Int )

  configuration <kmir>
                  <k> #call($PGM:String, 0) </k>
                  <callStack> .List <callStack>
                  <funcAddr> FnAddr( "" ) </funcAddr>
                  <body> .List </body>
                  <locals> ListItem(0) </locals>
                  <terminator> termiantorUnreachable </terminator>
                  <memory> $ENV:Map </memory>
                </kmir>
endmodule
