requires "kmir-ast.k"

module CONFIG
  imports KMIR-AST
  imports LIST
  imports MAP
  imports STRING
  imports BOOL
  imports BYTES
  imports K-EQUAL

  syntax CallStackItem  ::= CallRecord( FuncAddress, MaybeBasicBlockIdx, Place, UnwindAction, Values)
  syntax FuncAddress    ::= FnAddr( Int )
  syntax Values         ::= List{ Value, "" }
  syntax Value          ::= // MIR Value Types
                            Scalar( Int )
                          | Ref( Int )
                          | Ptr( Int, Value )
                          | Array( Bytes )
                          | Tuple( Values )
                          | Closure( Int, Values )
                          | Adt( Int, Int, Values )
                            // Semantics Specific Types
                          | Uninit()
                          | FnVal( BasicBlocks, Int, Int )

  configuration <kmir>
                  <k> #init($PGM:Int) </k>
                  <callStack> .List </callStack>
                  <funcAddr> FnAddr( -1 ) </funcAddr>
                  <body> .BasicBlocks </body>
                  <locals> Uninit() .Values </locals>
                  <memory> $ENV:Map </memory>
                </kmir>

  // Initialization

  syntax KItem ::= #init( Int )

  rule <k> #init( Addr )
        => #evaluated( Ptr( Addr, Uninit() )  )
        ~> #prepareCall( place( local( 0 ), .ProjectionElems ),
                         someBasicBlockIdx(basicBlockIdx( -1 )),
                         unwindActionTerminate
                       )
       </k>

  // Evaluation

  syntax KItem ::= #evaluating( Operands, Values )
                 | #evaluated( Values )

  rule <k> #evaluating( Opr Oprs,  Vals )         => #evaluate( Opr ) ~> #evaluating( Oprs, Vals ) ... </k>
  rule <k> Val:Value ~> #evaluating( Oprs, Vals ) => #evaluating( Oprs, Val Vals )                 ...  </k>
  rule <k> #evaluating( .Operands, Vals )         => #evaluated( #concatValues(Vals, .Values) )    ... </k>

  syntax Value ::= #evaluate( Operand )

  rule <k> #evaluate( operandConstant(constant(_SPAN, _UTY, const( CK, ty( _TID, TY ), _CID ))) )
        => #evalConst( CK, TY )
           ...
       </k>

  syntax Value ::= #evalConst( ConstantKind, TyKind )

  rule <k> #evalConst( constantKindZeroSized, tyKindRigidTy( rigidTyFnDef( FNDEF, _ )))
        => Ptr( FNDEF, Uninit() )
       </k>

  // Update

  syntax Value ::= #setPlace( Value, ProjectionElems, Value ) [function]

  rule #setPlace( _Val, .ProjectionElems, Val' ) => Val'
  // TODO: finish add update cases

  // Terminators

  syntax KItem ::= #goto( Int )
                 | #goto( MaybeBasicBlockIdx )

  rule <k> basicBlock( .Statements, terminator( terminatorKindGoto( basicBlockIdx( N ) ), _SPAN ))
        => #goto( N )
           ...
       </k>

  rule <k> #goto( someBasicBlockIdx(basicBlockIdx( N ))) => #goto( N ) ... </k>

  rule <k> #goto( N ) => #getBlock(N, Blocks) ... </k>
       <body> Blocks </body>
    requires N <Int #numBlocks(Blocks)

  syntax KItem ::= #prepareCall( Place, MaybeBasicBlockIdx, UnwindAction )
                 | #call( Int, Value, Values, Place, MaybeBasicBlockIdx, UnwindAction )

  rule <k> basicBlock( .Statements, terminator( terminatorKindCall( Callee, Args, Dest, Target, Unwind ), _SPAN ))
        => #evaluating( Callee Args, .Values )
        ~> #prepareCall( Dest, Target, Unwind )
           ...
       </k>

  rule <k> #evaluated( Ptr( Addr, Uninit() ) Args )
        ~> #prepareCall( Dest, Target, Unwind )
        => #call( Addr, { Mem [ Addr ] }:>Value, Args, Dest, Target, Unwind )
           ...
       </k>
       <memory> Mem:Map </memory>
    requires Addr in_keys( Mem )
     andBool FnVal( _, _, _ ) :=K Mem [ Addr ]

  rule <k> #call( CalleeAddr, FnVal( CalleeBody, ArgCount, LocalCount ), Args, Dest, Target, Unwind )
        => #goto( 0 )
           ...
       </k>
       <callStack> Stack => ListItem(CallRecord( FnAddr( CallerAddr ), Target, Dest, Unwind, CallerLocals )) Stack </callStack>
       <body> _CallerBody => CalleeBody </body>
       <locals> CallerLocals => #makeLocals( LocalCount, ArgCount, Args ) </locals>
       <funcAddr> FnAddr( CallerAddr => CalleeAddr ) </funcAddr>

  rule <k> basicBlock( .Statements, terminator( terminatorKindReturn, _SPAN ))
        => #goto( Target:MaybeBasicBlockIdx )
           ...
       </k>
       <callStack> ListItem(CallRecord( FnAddr( CallerAddr ), Target, Dest, _Unwind, CallerLocals )) Stack => Stack </callStack>
       <locals> (RetValue _Locals:Values) => #setValue( CallerLocals, Dest, RetValue ) </locals>
       <body> _CalleeBody => CallerBody </body>
       <memory> ... CallerAddr |-> FnVal( CallerBody, _, _ ) ... </memory>
    requires Target =/=K noBasicBlockIdx

  // Helpers

  syntax Values ::= #makeLocals( Int, Int, Values )           [function]
                  | #setValue( Values, Place, Value )         [function]
                  | #setValue( Values, Values, Place, Value ) [function]
                  | #concatValues( Values, Values )           [function]
                  | #makeValues( Int, Value )                 [function]

  rule #makeLocals( LocalCount, ArgCount, Args )
    => #concatValues( #concatValues( Args, Uninit() ), #makeValues( LocalCount -Int ArgCount, Uninit() ) )

  rule #setValue( Vals, I, Val' ) => #setValue( Vals, .Values, I, Val' )

  rule #setValue( Val RestVals, Vals, place(local(I:Int), Projs), Val' ) => #setValue( RestVals, Val Vals, place(local(I -Int 1), Projs), Val' ) requires I >Int 0
  rule #setValue( Val RestVals, Vals, place(local(0),     Projs), Val' ) => #concatValues( Vals, #setPlace(Val, Projs, Val') RestVals )

  rule #concatValues( Val Vals, Vals2 ) => #concatValues( Vals, Val Vals2 )
  rule #concatValues( .Values,  Vals2 ) => Vals2

  rule #makeValues( N,  Val ) => Val #makeValues( N -Int 1, Val ) requires N >Int  0
  rule #makeValues( N, _Val ) => .Values                          requires N <=Int 0

  syntax Int ::= #numBlocks( BasicBlocks ) [function]
  rule #numBlocks( _ BS ) => 1 +Int #numBlocks( BS )
  rule #numBlocks( .BasicBlocks ) => 0

  syntax BasicBlock ::= #getBlock( Int, BasicBlocks ) [function]
  rule #getBlock( I, _Block  Blocks ) => #getBlock( I -Int 1, Blocks ) requires I >Int 0
  rule #getBlock( 0,  Block _Blocks ) => Block
endmodule
