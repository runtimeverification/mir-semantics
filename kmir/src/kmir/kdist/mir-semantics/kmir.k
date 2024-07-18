requires "kmir-ast.k"

module KMIR-SYNTAX
  imports KMIR-AST
  imports MAP

  syntax InitialState ::= #init( Int, Map )

  syntax Statements ::= "emptyBlock" [function]
  rule emptyBlock => .Statements
  syntax GenericArgs ::= "emptyArgs" [function]
  rule emptyArgs => .GenericArgs
  syntax Operands ::= "emptyOperands" [function]
  rule emptyOperands => .Operands
  syntax ProjectionElems ::= "noProjection" [function]
  rule noProjection => .ProjectionElems
endmodule

module KMIR-MEMORY
  imports INT
  imports KMIR-SYNTAX
  imports LIST
  imports MAP

  configuration <memoryConfig>
                  <stack> .List </stack>
                  <globals>  .Map  </globals>
                </memoryConfig>
endmodule

module KMIR-MEMORY-API
  imports KMIR-SYNTAX

  syntax Address
  syntax Value

  // Returning Results
  syntax KItem ::= #value( Value )
                 | #function( Body )

  syntax KItem ::= #loadConst( Int, Map )

  // Value Production
  syntax KItem ::= #evalOp( BinOp, List )
                 | #evalOp( UnOp, List )
                 | #evalNullOp( NullOp, Ty )
                 | #evalCast( CastKind, List )
                 | #evalDisc( List )
                 | #evalLen( List )
                 | #makePtr( Place )
                 | #buildPtr( List )
                 | #makeStruct( Int, List )
                 | #makeArray( List )
                 | #makeTLRef( )

  syntax KItem ::= #setValue( Address, Value ) // non-functional due to state update
                 | #setDisc( Place, Int )
                 | #setPlace( Place, Value )   [function]
                 | #setLocal( Local, Value )   [function]
                 | #deinitPlace( Place )

  syntax KItem ::= #assume( List )
                 | #copy( List )

  // TODO: make this a non-contextual function
  syntax Value ::= #loadValue( Address )       [function]
                 | #loadPlace( Place )         [function]
                 | #loadLocal( Local )         [function]
                 | #loadPtr( Address, Value )  [function]
                 | #makeFnPtr( String, Map )   [function]

  syntax Int ::= #readScalar( Value )          [function]
  syntax Bool ::= #isTrue( Value )             [function]

  syntax Body ::= #loadFnPtr( Value )

  syntax KItem ::= #setupStackFrame( List, Int, LocalDecls, Place, MaybeBasicBlockIdx )
                 | "#return"
endmodule

module KMIR-CONFIGURATION
  imports KMIR-SYNTAX
  imports KMIR-MEMORY

  configuration <kmir>
                  <k> $PGM:InitialState </k>
                  <body> .BasicBlocks </body>
                  <memoryConfig/>
                </kmir>
endmodule

module KMIR-MEMORY-IMPL [private]
  imports KMIR-MEMORY-API
  imports KMIR-CONFIGURATION
  imports BOOL
  imports K-EQUAL
  imports INT

  // Memory Implementation Structures

  // 1. Address to top-level objects
  // 2. Address to top-level or nested objects
  // 3. Value Structure
  // 4. Stack Frame Structure

  syntax AddressBase ::= AddrBase( Int )                 // global index
                       | AddrBase( Int, Int )            // stack frame index, local var index

  syntax Address ::= LocalAddr( Int,                     // stack frame height
                                Place )                  // stack local address
                   | GlobalAddr( Int,                    // global address
                                 ProjectionElems )       // projection out of global address

  syntax MaybeValue ::= Value
                      | "NoValue"

  syntax Value ::= Scalar( Int, Int, Bool )              // value, bit-width, signedness   for bool, un/signed int
                 | Float( Float, Int )                   // value, bit-width               for f16-f128
                 | Ptr( Address, MaybeValue )            // address, metadata              for ref/ptr
                 | Range( List )                         // homogenous values              for array/slice
                 | Struct( Int, List )                   // heterogenous value list        for tuples and structs (standard, tuple, or anonymous)
                 | "Any"                                 // arbitrary value                for transmute/invalid ptr lookup

  syntax StackFrameRecord ::= Frame( Address,            // address of caller function
                                     MaybeBasicBlockIdx, // basic block to return to
                                     Place,              // place to store return value
                                     UnwindAction,       // action to perform if we panic
                                     locals: List )      // stack locals

  syntax MemoryWrite ::= MemWrite( AddressBase,          // address to overwrite
                                   Value )               // value to store at address

  // Memory Implementation Rules

  syntax AddressBase ::= #base( Address )                                        [function] // get address base

  syntax ProjectionElems ::= #getProj( Address )                                 [function] // get projections from Address
                           | #revPrjs( ProjectionElems, ProjectionElems )        [function] // reverse a list of projections
                           | #catPrjs( ProjectionElems, ProjectionElems )        [function] // concatenate two lists of projections

  syntax Value ::= #prj( ProjectionElem, Value )                                 [function] // project point out of Value
                 | #prjs( ProjectionElems, Value )                               [function] // project point out of Value

  syntax MemoryWrite ::= #set( AddressBase, ProjectionElems, Value, Value )      [function] // update Value1 projected via ProjectionElems with Value2 and store at Int address
                       | #setPtr( Address, ProjectionElems, Value  )             [function] // update Value at address, further projected out via ProjectionElems
                       | #inj( AddressBase, ProjectionElem, Value, MemoryWrite ) [function] // perform Write, accumulating any missing context
                       | #inj(              ProjectionElem, Value, MemoryWrite ) [function] // helper function for #inj

  syntax List ::= #update1(List, Int, Value )                                    [function] // updates an index in the list
                | #updateN(List, Int, Int, Bool, Value )                         [function] // updates multiple indices in the list

  syntax KItem ::= #write( MemoryWrite )                                                    // perform memory write

  syntax StackFrameRecord ::= #setStkVar( StackFrameRecord, Int, Value )         [function] // perform stack variable update

  syntax Value ::= #loadField( Int, List )                                       [function]
                 | #loadIndex( Value, List )                                     [function]
                 | #loadIndex( Int, List )                                       [function]
                 | #loadSlice( Int, Int, Bool, List )                            [function]
                 | #loadVar( List, Int, Int )                                    [function]
                 | #loadVar( StackFrameRecord, Int )                             [function]

  syntax Bool ::= #validSlice(List, Int, Int, Bool)                              [macro]
                | #NoOpProjection( ProjectionElem )                              [function]

  syntax Int ::= #sizeSlice(List, Int, Int, Bool)                                [macro]
               | #boolToInt( Bool )                                              [function]

  syntax Address ::= #readAddr( Value )                                          [function]
                   | #delProj( Address )                                         [function]

  // Eval Impl

  rule <k> #deinitPlace( _PLACE ) => .K ... </k> // TODO: flesh out this implementation

  rule #evalOp( binOpAdd,          ListItem(Scalar(N1, WIDTH, SIGN)) ListItem(Scalar(N2, WIDTH, SIGN)) ) => #value(Struct( 0, ListItem(Scalar( N1 +Int N2, WIDTH, SIGN )) ListItem(Scalar( 0, 1, false )) ))
  rule #evalOp( binOpAddUnchecked, ListItem(Scalar(N1, WIDTH, SIGN)) ListItem(Scalar(N2, WIDTH, SIGN)) ) => #value(Scalar( N1 +Int N2, WIDTH, SIGN ))
  rule #evalOp( binOpSub,          ListItem(Scalar(N1, WIDTH, SIGN)) ListItem(Scalar(N2, WIDTH, SIGN)) ) => #value(Struct( 0, ListItem(Scalar( N1 -Int N2, WIDTH, SIGN )) ListItem(Scalar( 0, 1, false )) ))
  rule #evalOp( binOpSubUnchecked, ListItem(Scalar(N1, WIDTH, SIGN)) ListItem(Scalar(N2, WIDTH, SIGN)) ) => #value(Scalar( N1 -Int N2, WIDTH, SIGN ))
  rule #evalOp( binOpMul,          ListItem(Scalar(N1, WIDTH, SIGN)) ListItem(Scalar(N2, WIDTH, SIGN)) ) => #value(Struct( 0, ListItem(Scalar( N1 *Int N2, WIDTH, SIGN )) ListItem(Scalar( 0, 1, false )) ))
  rule #evalOp( binOpMulUnchecked, ListItem(Scalar(N1, WIDTH, SIGN)) ListItem(Scalar(N2, WIDTH, SIGN)) ) => #value(Scalar( N1 *Int N2, WIDTH, SIGN ))
  rule #evalOp( binOpDiv,          ListItem(Scalar(N1, WIDTH, SIGN)) ListItem(Scalar(N2, WIDTH, SIGN)) ) => #value(Scalar( N1 /Int N2, WIDTH, SIGN ))
  rule #evalOp( binOpRem,          ListItem(Scalar(N1, WIDTH, SIGN)) ListItem(Scalar(N2, WIDTH, SIGN)) ) => #value(Scalar( N1 %Int N2, WIDTH, SIGN ))
  rule #evalOp( binOpBitXor,       ListItem(Scalar(N1, WIDTH, SIGN)) ListItem(Scalar(N2, WIDTH, SIGN)) ) => #value(Scalar( N1 xorInt N2, WIDTH, SIGN ))
  rule #evalOp( binOpBitAnd,       ListItem(Scalar(N1, WIDTH, SIGN)) ListItem(Scalar(N2, WIDTH, SIGN)) ) => #value(Scalar( N1 &Int N2, WIDTH, SIGN ))
  rule #evalOp( binOpBitOr,        ListItem(Scalar(N1, WIDTH, SIGN)) ListItem(Scalar(N2, WIDTH, SIGN)) ) => #value(Scalar( N1 |Int N2, WIDTH, SIGN ))
  rule #evalOp( binOpShl,          ListItem(Scalar(N1, WIDTH, SIGN)) ListItem(Scalar(N2, WIDTH, SIGN)) ) => #value(Struct( 0, ListItem(Scalar( N1 <<Int N2, WIDTH, SIGN )) ListItem(Scalar( 0, 1, false )) ))
  rule #evalOp( binOpShlUnchecked, ListItem(Scalar(N1, WIDTH, SIGN)) ListItem(Scalar(N2, WIDTH, SIGN)) ) => #value(Scalar( N1 <<Int N2, WIDTH, SIGN ))
  rule #evalOp( binOpShr,          ListItem(Scalar(N1, WIDTH, SIGN)) ListItem(Scalar(N2, WIDTH, SIGN)) ) => #value(Struct( 0, ListItem(Scalar( N1 >>Int N2, WIDTH, SIGN )) ListItem(Scalar( 0, 1, false )) ))
  rule #evalOp( binOpShrUnchecked, ListItem(Scalar(N1, WIDTH, SIGN)) ListItem(Scalar(N2, WIDTH, SIGN)) ) => #value(Scalar( N1 >>Int N2, WIDTH, SIGN ))
  rule #evalOp( binOpEq,           ListItem(_Arg1) ListItem(_Arg2) ) => #value( Any )
  rule #evalOp( binOpLt,           ListItem(_Arg1) ListItem(_Arg2) ) => #value( Any )
  rule #evalOp( binOpLe,           ListItem(_Arg1) ListItem(_Arg2) ) => #value( Any )
  rule #evalOp( binOpNe,           ListItem(_Arg1) ListItem(_Arg2) ) => #value( Any )
  rule #evalOp( binOpGe,           ListItem(_Arg1) ListItem(_Arg2) ) => #value( Any )
  rule #evalOp( binOpGt,           ListItem(_Arg1) ListItem(_Arg2) ) => #value( Any )
  rule #evalOp( binOpCmp,          ListItem(_Arg1) ListItem(_Arg2) ) => #value( Any )
  rule #evalOp( binOpOffset,       ListItem(_Arg1) ListItem(_Arg2) ) => #value( Any )

  rule #evalOp( unOpNot,           ListItem(Scalar(N, WIDTH, SIGN))) => #value( Scalar( #if WIDTH ==Int 1 andBool SIGN ==Bool false #then #boolToInt(notBool (N =/=Int 0)) #else (~Int N) #fi, WIDTH, SIGN) )
  rule #evalOp( unOpNeg,           ListItem(Scalar(N, WIDTH, true))) => #value( Scalar( N *Int -1, WIDTH, true ) )

  rule #evalNullOp( nullOpSizeOf,            _TY ) => #value( Scalar( 0, 32, false ) )
  rule #evalNullOp( nullOpAlignOf,           _TY ) => #value( Scalar( 0, 32, false ) )
  rule #evalNullOp( nullOpOffsetOf(_VFIdxs), _TY ) => #value( Scalar( 0, 32, false ) )
  rule #evalNullOp( nullOpUbChecks,          _TY ) => #value( Scalar( 0, 1,  false ) )

  rule #boolToInt( true  ) => 1
  rule #boolToInt( false ) => 0

  rule <k> #evalCast( _KIND, ListItem( _:Value ) )       => #value( Any )                            ... </k>
  rule <k> #evalLen( ListItem( Range( Mem ) ) )          => #value( Scalar( size(Mem), 64, false ) ) ... </k>
  rule <k> #evalDisc( ListItem( Struct( Idx, _Args ) ) ) => #value( Scalar( Idx,       8,  false ) ) ... </k>

  // Make Impl

  rule <k> #buildPtr( ListItem( Ptr( Addr:Address, Meta:Value ) )                        ) => #value( Ptr( Addr, Meta ) ) ... </k>
  rule <k> #buildPtr( ListItem( Ptr( Addr:Address, NoValue    ) ) ListItem( Meta:Value ) ) => #value( Ptr( Addr, Meta ) ) ... </k>

  rule <k> #makePtr(PLACE) => #value( Ptr( LocalAddr(size(Stack) -Int 1, PLACE), NoValue ) ) ... </k>
       <stack> Stack </stack>

  rule <k> #makeStruct(VIdx, Args) => #value( Struct( VIdx, Args ) ) ... </k>

  rule <k> #makeArray( Args ) => #value( Range( Args ) ) ... </k>

  rule <k> #makeTLRef() => #value( Any ) ... </k>

  // Set Impl

  rule #setStkVar( Frame( Addr, Target, Dest, Unwind, LocalVars ), LIdx, Val ) => Frame( Addr, Target, Dest, Unwind, LocalVars [ LIdx <- Val ] )

  rule #setLocal( LIdx, Val ) => #setPlace( place(LIdx, .ProjectionElems), Val )

  rule [[ #setPlace( place(LIdx, Prjs), Val ) => #setValue( LocalAddr(size(Stack) -Int 1, place(LIdx, Prjs)), Val ) ]]
       <stack> Stack </stack>
    requires size(Stack) >Int 0

  rule <k> #setValue( Addr, Val ) => #write( #set( #base(Addr), #getProj(Addr), #loadValue( Addr ), Val ) ) ... </k>

  rule <k> #write( MemWrite( AddrBase(Idx, LIdx), Val ) ) => .K ... </k>
       <stack> Stack => Stack [ Idx <- #setStkVar( { Stack }:>StackFrameRecord, LIdx, Val ) ] </stack>
  rule <k> #write( MemWrite( AddrBase(Idx), Val ) ) => .K ... </k>
       <globals> Globals => Globals [ Idx <- Val ] </globals>

  // Load Impl

  rule [[ #loadValue( LocalAddr( Idx, place(local(LIdx), Prjs) ) ) => #prjs( Prjs, #loadVar( Stack,  Idx, LIdx ) ) ]]
       <stack> Stack </stack>

  rule [[ #loadValue( GlobalAddr( Idx, Prjs ) ) => #prjs( Prjs, { Global [ Idx ] }:>Value ) ]]
       <globals> Global </globals>
    requires 0 <=Int Idx andBool Idx <Int size(Global)

  rule [[ #loadPlace( PLACE ) => #loadValue( LocalAddr(size(Stack) -Int 1, PLACE) ) ]]
       <stack> Stack </stack>

  rule [[ #loadLocal( local(LIdx:Int) ) => #loadValue( LocalAddr(size(Stack) -Int 1, place(local(LIdx:Int), .ProjectionElems)) ) ]]
       <stack> Stack </stack>

  rule #loadPtr( Addr, _ ) => #loadValue( Addr )

  rule #loadVar( Stack, Idx, LIdx ) => #loadVar({ Stack [ Idx ] }:>StackFrameRecord, LIdx)
    requires 0 <=Int Idx andBool Idx <Int size(Stack)

  rule #loadVar( StkFrm, LIdx ) => { locals(StkFrm) [ LIdx ] }:>Value
    requires 0 <=Int LIdx andBool LIdx <Int size(locals(StkFrm))

  // Address Manipulation

  rule #base(LocalAddr(Idx:Int,  place(local(LIdx:Int), _:ProjectionElems))) => AddrBase(Idx, LIdx)
  rule #base(GlobalAddr(Idx:Int,                        _:ProjectionElems) ) => AddrBase(Idx)

  rule #getProj(LocalAddr(_, place(_, Prjs))) => Prjs
  rule #getProj(GlobalAddr(_, Prjs))          => Prjs

  rule #delProj(LocalAddr(Idx:Int, place(LIdx:Local, _:ProjectionElems))) => LocalAddr(Idx, place(LIdx, .ProjectionElems))
  rule #delProj(GlobalAddr(Idx:Int,                  _:ProjectionElems) ) => GlobalAddr(Idx, .ProjectionElems)

  // Writing a value

  rule #set( Addr, Prj Prjs, Scrutinee, Val )
    => #if #NoOpProjection(Prj)
         #then #set( Addr, Prjs, Scrutinee, Val )
         #else #if Prj ==K projectionElemDeref
           #then #setPtr( #readAddr( Scrutinee ), Prjs, Val )
           #else #inj( Addr, Prj, Scrutinee, #set( Addr, Prjs, #prj( Prj, Scrutinee ), Val ) )
       #fi #fi

  rule #set( Addr, .ProjectionElems, _Scrutinee, Val ) => MemWrite( Addr, Val )

  rule #setPtr( Addr, Prjs, Val ) => #set( #base( Addr ), #catPrjs( #getProj( Addr ), Prjs ), #loadValue( #delProj( Addr ) ), Val )

  // Projecting out a nested object

  rule #prjs( Prj Prjs,         Val ) => #prjs( Prjs, #prj( Prj, Val ) )
  rule #prjs( .ProjectionElems, Val ) => Val

  // NOTE: an infinite descent of only deref chains cannot exist because:
  //       any self-referntial type has to be mediated by a struct which wraps a pointer
  rule #prj( projectionElemDeref,                    Ptr( Next, Meta ) ) => #loadPtr(Next, Meta)
  rule #prj( projectionElemField(fieldIdx(I), _),    Struct( _, Flds ) ) => #loadField(I, Flds)
  rule #prj( projectionElemIndex(Idx),               Range( Mem )      ) => #loadIndex(#loadLocal(Idx), Mem)
  rule #prj( projectionElemConstantIndex(Off, _, _), Range( Mem )      ) => #loadIndex(Off, Mem)
  rule #prj( projectionElemSubslice(From, To, Dir),  Range( Mem )      ) => #loadSlice(From, To, Dir, Mem)

  rule #loadField( Idx, Fields:List   ) => { Fields [ Idx ] }:>Value requires 0 <=Int Idx andBool Idx <Int size(Fields)
  rule #loadIndex( Idx, Mem:List      ) => { Mem    [ Idx ] }:>Value requires 0 <=Int Idx andBool Idx <Int size(Mem)
  rule #loadIndex( Val, Mem:List      ) => #loadIndex(#readScalar(Val), Mem)
  rule #loadSlice( From, To, Dir, Mem )
    => #if Dir
         #then Range( range( Mem, From, size(Mem) -Int To ) )
         #else Range( range( Mem, From, To                ) )
       #fi
    requires #validSlice(Mem, From, To, Dir)

  rule #NoOpProjection( projectionElemDeref                  ) => false
  rule #NoOpProjection( projectionElemField(_, _)            ) => false
  rule #NoOpProjection( projectionElemIndex(_)               ) => false
  rule #NoOpProjection( projectionElemConstantIndex(_, _, _) ) => false
  rule #NoOpProjection( projectionElemSubslice(_, _, _)      ) => false
  rule #NoOpProjection( projectionElemDowncast(_)            ) => true
  rule #NoOpProjection( projectionElemOpaqueCast(_)          ) => true
  rule #NoOpProjection( projectionElemSubtype(_)             ) => true

  rule #catPrjs( Prjs1,            Prjs2 ) => #revPrjs( #revPrjs( Prjs1, .ProjectionElems ), Prjs2     )
  rule #revPrjs( Prj Prjs1,        Prjs2 ) => #revPrjs( Prjs1,                               Prj Prjs2 )
  rule #revPrjs( .ProjectionElems, Prjs2 ) => Prjs2

  // Injecting an updated value into a nested object

  rule #inj( Orig, Prj, Scrutinee, MemWrite(Addr, Val) )
    => #if Orig =/=K Addr
         #then MemWrite(Addr, Val)
         #else #inj( Prj, Scrutinee, MemWrite(Orig, Val) )
       #fi

  rule #inj( projectionElemField( fieldIdx(I), _ ),    Struct( VIdx, Flds ), MemWrite( Addr, Val ) ) => MemWrite( Addr, Struct( VIdx, #update1( Flds, I, Val ) ) )
  rule #inj( projectionElemIndex( Idx ),               Range( Mem ),         MemWrite( Addr, Val ) ) => MemWrite( Addr, Range( #update1( Mem, #readScalar( #loadLocal( Idx ) ), Val ) ) )
  rule #inj( projectionElemConstantIndex( Off, _, _ ), Range( Mem ),         MemWrite( Addr, Val ) ) => MemWrite( Addr, Range( #update1( Mem, Off, Val ) ) )
  rule #inj( projectionElemSubslice( From, To, Dir ),  Range( Mem ),         MemWrite( Addr, Val ) ) => MemWrite( Addr, Range( #updateN( Mem, From, To, Dir, Val) ) )

  rule #update1( Mem, Idx, Val )
    => #if Idx >=Int size(Mem)
         #then Mem
         #else Mem [ Idx <- Val ]
       #fi
    requires Idx >=Int 0

  rule #updateN( Mem, From, To, Dir, Range(New) )
    => updateList(Mem, From, New)
    requires #validSlice(Mem, From, To, Dir)
     andBool size(New) ==Int #sizeSlice(Mem, From, To, Dir)

  // Access sanity checks

  rule #validSlice(Mem, From, To, Dir) => 0  <=Int From
                                  andBool 0  <=Int To
                                  andBool To <=Int size(Mem)
                                  andBool 0  <=Int #sizeSlice(Mem, From, To, Dir)

  rule #sizeSlice(Mem, From, To, Dir) => #if Dir
                                           #then (size(Mem) -Int To) -Int From
                                           #else To -Int From
                                         #fi

  // Value Interpretation

  rule #readScalar( Scalar( Val, _Width, _Signed ) ) => Val
  rule #readAddr( Ptr( Addr, _ ) )                   => Addr
endmodule

module KMIR
  imports KMIR-SYNTAX
  imports KMIR-MEMORY-IMPL
  imports KMIR-CONFIGURATION
  imports KMIR-MEMORY-API
  imports LIST
  imports STRING
  imports BOOL
  imports BYTES
  imports K-EQUAL

  // Lookup Fn Type

  syntax String ::= #lookupFnType( Int ) [function]

  // Argument Evaluation

  syntax KItem ::= #operands( List )

  syntax K ::= #evalArgs( Rvalue )                [function]
             | #evalArgs( NonDivergingIntrinsic ) [function]
             | #evalArgs( TerminatorKind )        [function]

  rule #evalArgs(rvalueAddressOf(_MUT, _PLACE))                                      => .K
  rule #evalArgs(rvalueAggregate(_KIND, ARGS))                                       => #evalArgs(#argsToList(ARGS, .List), .List)
  rule #evalArgs(rvalueBinaryOp(_OP, ARG1, ARG2))                                    => #evalArgs(ListItem(ARG1) ListItem(ARG2), .List)
  rule #evalArgs(rvalueCast(_KIND, ARG, _TY))                                        => #evalArgs(ListItem(ARG), .List)
  rule #evalArgs(rvalueCheckedBinaryOp(_OP, ARG1, ARG2))                             => #evalArgs(ListItem(ARG1) ListItem(ARG2), .List)
  rule #evalArgs(rvalueCopyForDeref(PLACE))                                          => #evalArgs(ListItem(PLACE), .List)
  rule #evalArgs(rvalueDiscriminant(PLACE))                                          => #evalArgs(ListItem(PLACE), .List)
  rule #evalArgs(rvalueLen(PLACE))                                                   => #evalArgs(ListItem(PLACE), .List)
  rule #evalArgs(rvalueRef(_REG, _BRW_KIND, _PLACE))                                 => .K
  rule #evalArgs(rvalueRepeat(ARG, CONST))                                           => #evalArgs(ListItem(ARG) ListItem(CONST), .List)
  rule #evalArgs(rvalueShallowInitBox(ARG, _TY))                                     => #evalArgs(ListItem(ARG), .List)
  rule #evalArgs(rvalueThreadLocalRef(_CRATE_ITEM))                                  => .K
  rule #evalArgs(rvalueNullaryOp(_OP, _TY))                                          => .K
  rule #evalArgs(rvalueUnaryOp(_OP, ARG))                                            => #evalArgs(ListItem(ARG), .List)
  rule #evalArgs(rvalueUse(ARG))                                                     => #evalArgs(ListItem(ARG), .List)
  rule #evalArgs(nonDivergingIntrinsicAssume(ARG))                                   => #evalArgs(ListItem(ARG), .List)
  rule #evalArgs(nonDivergingIntrinsicCopyNonOverlapping(ARGS))                      => #evalArgs(ListItem(src(ARGS)) ListItem(dst(ARGS)) ListItem(count(ARGS)), .List)
  rule #evalArgs(terminatorKindSwitchInt(ARG, _TARGETS))                             => #evalArgs(ListItem(ARG), .List)
  rule #evalArgs(terminatorKindResume)                                               => .K
  rule #evalArgs(terminatorKindAbort)                                                => .K
  rule #evalArgs(terminatorKindReturn)                                               => .K
  rule #evalArgs(terminatorKindUnreachable)                                          => .K
  rule #evalArgs(terminatorKindDrop(_PLACE, _TARGET, _ACT))                          => .K
  rule #evalArgs(terminatorKindCall(FUNC, ARGS, _DEST, _TARGET, _ACT))               => #evalArgs(#argsToList(FUNC ARGS, .List), .List)
  rule #evalArgs(assert(COND, _EXPECTED, _MSG, _TARGET, _ACT))                       => #evalArgs(ListItem(COND), .List)
  rule #evalArgs(terminatorKindInlineAsm(_TMPL, _ARGS, _OPTS, _SPNS, _TARGET, _ACT)) => .K

  syntax List ::= #argsToList( Operands, List ) [function]
                | #reverse( List, List )        [function]
  rule #argsToList( ARG1 ARGS, REST ) => #argsToList( ARGS, ListItem( ARG1 ) REST )
  rule #argsToList( .Operands, REST ) => #reverse(REST, .List)
  rule #reverse( ListItem(LI) L1:List, L2 ) => #reverse( L1, ListItem(LI) L2 )
  rule #reverse( .List, L2 ) => L2

  syntax KItem ::= #evalArgs( List, List )

  rule <k> #evalArgs( ListItem( operandCopy(PLACE) ) ARGS, EVALED )
        => #evalArgs( ARGS, ListItem( #loadPlace( PLACE ) ) EVALED )
           ...
       </k>

  rule <k> #evalArgs( ListItem( operandMove(PLACE) ) ARGS, EVALED )
        => #deinitPlace( PLACE )
        ~> #evalArgs( ARGS, ListItem( #loadPlace( PLACE ) ) EVALED )
           ...
       </k>

  rule <k> #evalArgs( ListItem( operandConstant(CONST) ) ARGS, EVALED )
        => #evalArgs( ARGS, ListItem( #evalConst(CONST) ) EVALED )
           ...
       </k>

  rule <k> #evalArgs( ListItem( CONST:Constant ) ARGS, EVALED )
        => #evalArgs( ARGS, ListItem( #evalConst(CONST) ) EVALED )
           ...
       </k>

  rule <k> #evalArgs( ListItem( PLACE:Place ) ARGS, EVALED )
        => #evalArgs( ARGS, ListItem( #loadPlace( PLACE ) ) EVALED )
           ...
       </k>

  rule <k> #evalArgs( .List, ARGS ) => #operands( ARGS ) ... </k>

  syntax Value ::= #evalConst( Constant )

  rule <k> #evalConst( constant(_SPAN, _USERTY, const(KIND, ty(TID, _), constId(CID))) )
        => #if KIND ==K constantKindZeroSized
             #then #makeFnPtr( #lookupFnType(TID), .Map )
             #else #loadConst( CID, .Map )
           #fi
           ...
       </k>

  syntax Value ::= #getArg( List )     [function]
                 | #getFstArg( List )  [function]
  syntax List ::= #getRestArgs( List ) [function]

  rule #getArg( ListItem( Val:Value ) )     => Val
  rule #getFstArg( ListItem( Val:Value ) )  => Val
  rule #getRestArgs( ListItem(_) RestArgs ) => RestArgs

  // Expression Evaluation

  syntax KItem ::= #eval(Rvalue)

  rule <k>                    #eval(rvalueAddressOf(_MUT, PLACE))      => #makePtr(PLACE)            ... </k>
  rule <k> #operands(ARGS) ~> #eval(rvalueAggregate(KIND, _))          => #makeAggregate(KIND, ARGS) ... </k>
  rule <k> #operands(ARGS) ~> #eval(rvalueBinaryOp(OP, _, _))          => #evalOp(OP, ARGS)          ... </k>
  rule <k> #operands(ARGS) ~> #eval(rvalueCheckedBinaryOp(OP, _, _))   => #evalOp(OP, ARGS)          ... </k>
  rule <k> #operands(ARGS) ~> #eval(rvalueCast(KIND, _, _TY))          => #evalCast(KIND, ARGS)      ... </k>
  rule <k> #operands(ARGS) ~> #eval(rvalueCopyForDeref(_))             => #value( #getArg(ARGS) )    ... </k>
  rule <k> #operands(ARGS) ~> #eval(rvalueDiscriminant(_))             => #evalDisc(ARGS)            ... </k>
  rule <k> #operands(ARGS) ~> #eval(rvalueLen(_))                      => #evalLen(ARGS)             ... </k>
  rule <k>                    #eval(rvalueRef(_REG, _BRW_KIND, PLACE)) => #makePtr(PLACE)            ... </k>
  rule <k> #operands(ARGS) ~> #eval(rvalueRepeat(_, _))                => #makeArray(ARGS)           ... </k>
  rule <k> #operands(ARGS) ~> #eval(rvalueShallowInitBox(_, _))        => #buildPtr(ARGS)            ... </k>
  rule <k>                    #eval(rvalueThreadLocalRef(_CRATE_ITEM)) => #makeTLRef()               ... </k>
  rule <k>                    #eval(rvalueNullaryOp(OP, TY))           => #evalNullOp(OP, TY)        ... </k>
  rule <k> #operands(ARGS) ~> #eval(rvalueUnaryOp(OP, _))              => #evalOp(OP, ARGS)          ... </k>
  rule <k> #operands(ARGS) ~> #eval(rvalueUse(_))                      => #value( #getArg(ARGS) )    ... </k>

  // Aggregate Builder

  syntax KItem ::= #makeAggregate(AggregateKind, List) [function]
  rule #makeAggregate(aggregateKindArray(_),                                                                         Args ) => #makeArray( Args )
  rule #makeAggregate(aggregateKindTuple,                                                                            Args ) => #makeStruct( 0, Args )
  rule #makeAggregate(aggregateKindAdt(_AdtDef, variantIdx(Idx), _Generics, _UserType, noFieldIdx),                  Args ) => #makeStruct( Idx, Args )
  rule #makeAggregate(aggregateKindAdt(_AdtDef, variantIdx(0),   _Generics, _UserType, someFieldIdx(fieldIdx(Idx))), Args ) => #makeStruct( Idx, Args )
  rule #makeAggregate(aggregateKindClosure(_ClosureDef, _Generics),                                                  Args ) => #makeStruct( 0, Args )
  rule #makeAggregate(aggregateKindCoroutine(_CoroutineDef, _Generics, _Movability),                                 Args ) => #makeStruct( 0, Args )
  rule #makeAggregate(aggregateKindRawPtr(_Ty, _Mutability),                                                         Args ) => #buildPtr( Args )

  // Intrinsic

  syntax KItem ::= #eval(NonDivergingIntrinsic)

  rule <k> #operands(ARGS) ~> #eval(nonDivergingIntrinsicAssume(_))             => #assume( ARGS ) ... </k>
  rule <k> #operands(ARGS) ~> #eval(nonDivergingIntrinsicCopyNonOverlapping(_)) => #copy( ARGS )   ... </k>

  // Statement/Terminator Evaluation

  syntax KItem ::= #exec(StatementKind)
                 | #exec(TerminatorKind)

  rule <k> basicBlock( statement(STMT, _SPAN) STMTS, TERM )     => #exec( STMT ) ~> basicBlock( STMTS, TERM ) ... </k>
  rule <k> basicBlock( .Statements, terminator( TERM, _SPAN ) ) => #evalArgs( TERM ) ~> #exec( TERM )         ... </k>

  // Statements

  syntax KItem ::= #assign(Place)

  rule <k> #exec(statementKindAssign(PLACE, RVAL))                           => #evalArgs(RVAL) ~> #eval(RVAL) ~> #assign(PLACE) ... </k>
  rule <k> #value(VAL) ~> #assign(PLACE)                                     => #setPlace(PLACE, VAL)                            ... </k>
  rule <k> #exec(statementKindIntrinsic(INT))                                => #evalArgs(INT) ~> #eval(INT)                     ... </k>
  rule <k> #exec(statementKindSetDiscriminant(PLACE, variantIdx(IDX)))       => #setDisc(PLACE, IDX)                             ... </k>
  rule <k> #exec(deinit(PLACE))                                              => #deinitPlace(PLACE)                              ... </k>
  rule <k> #exec(statementKindFakeRead(_FakeReadCause, _Place))              => .K                                               ... </k>
  rule <k> #exec(statementKindStorageLive(_Local))                           => .K                                               ... </k>
  rule <k> #exec(statementKindStorageDead(_Local))                           => .K                                               ... </k>
  rule <k> #exec(statementKindRetag(_RetagKind, _Place))                     => .K                                               ... </k>
  rule <k> #exec(statementKindPlaceMention(_Place))                          => .K                                               ... </k>
  rule <k> #exec(statementKindAscribeUserType(_Place, _UserType, _Variance)) => .K                                               ... </k>
  rule <k> #exec(statementKindCoverage(_Coverage))                           => .K                                               ... </k>
  rule <k> #exec(statementKindConstEvalCounter)                              => .K                                               ... </k>
  rule <k> #exec(statementKindNop)                                           => .K                                               ... </k>

  // Terminators

  syntax KItem ::= "#stuck"
                 | #goto( Int )
                 | #goto( BasicBlockIdx )
                 | #goto( MaybeBasicBlockIdx )
                 | #jump( Int, Branches, BasicBlockIdx )
                 | #prepareCall( Value, List, Place, MaybeBasicBlockIdx )
                 | #call( List, Place, MaybeBasicBlockIdx )
                 | #assert( Value )

  rule <k> #exec( terminatorKindGoto( basicBlockIdx( N ) ) ) => #goto( N ) ... </k>

  rule <k> #goto(                    basicBlockIdx( N )   ) => #goto( N )             ... </k>
  rule <k> #goto( someBasicBlockIdx( basicBlockIdx( N ) ) ) => #goto( N )             ... </k>
  rule <k> #goto( N )                                       => #getBlock( N, Blocks ) ... </k>
       <body> Blocks </body>
    requires N <Int #numBlocks(Blocks)

  syntax Int ::= #numBlocks( BasicBlocks ) [function]
  rule #numBlocks( _ BS ) => 1 +Int #numBlocks( BS )
  rule #numBlocks( .BasicBlocks ) => 0

  syntax BasicBlock ::= #getBlock( Int, BasicBlocks ) [function]
  rule #getBlock( I, _Block  Blocks ) => #getBlock( I -Int 1, Blocks ) requires I >Int 0
  rule #getBlock( 0,  Block _Blocks ) => Block

  rule <k> #operands(ARGS) ~> #exec(terminatorKindSwitchInt(_ARG, TARGETS))                             => #jump(#readScalar(#getArg(ARGS)), branches(TARGETS), otherwise(TARGETS)) ... </k>
  rule <k>                    #exec(terminatorKindResume)                                               => .K                                                                       ... </k>
  rule <k>                    #exec(terminatorKindAbort)                                                => .K                                                                       ... </k>
  rule <k>                    #exec(terminatorKindReturn)                                               => #return                                                                  ... </k>
  rule <k>                    #exec(terminatorKindUnreachable)                                          => #stuck                                                                   ... </k>
  rule <k>                    #exec(terminatorKindDrop(PLACE, _TARGET, _ACT))                           => #deinitPlace(PLACE)                                                      ... </k>
  rule <k> #operands(ARGS) ~> #exec(terminatorKindCall(_FUNC, _ARGS, DEST, TARGET, _ACT))               => #prepareCall(#getFstArg(ARGS), #getRestArgs(ARGS), DEST, TARGET)         ... </k>
  rule <k> #operands(ARGS) ~> #exec(assert(_COND, _EXPECTED, _MSG, _TARGET, _ACT))                      => #assert(#getArg(ARGS))                                                   ... </k>
  rule <k>                    #exec(terminatorKindInlineAsm(_TMPL, _ARGS, _OPTS, _SPNS, _TARGET, _ACT)) => #stuck                                                                   ... </k>

  // Jump Terminator

  rule <k> #jump( I, branch(J, BBIdx) TGTS, OWISE) => #if I ==Int J #then #goto(BBIdx) #else #jump(I, TGTS, OWISE) #fi ... </k>
  rule <k> #jump(_I, .Branches,             OWISE) => #goto(OWISE)                                                     ... </k>

  // Assert Terminator

  rule <k> #assert( Val:Value ) => #if #isTrue( Val ) #then .K #else #stuck #fi ... </k>

  // Call Terminator

  rule <k> #prepareCall( Func, Args, Dest, Target ) => #loadFnPtr( Func ) ~> #call( Args, Dest, Target ) ... </k>

  rule <k> #function(body(Blocks, Locals, ArgCount, _DebugInfo, _SpreadArg, _Span))
        ~> #call( Args, Dest, Target )
        => #setupStackFrame( Args, ArgCount, Locals, Dest, Target )
        ~> #goto( 0 )
       </k>
       <body> _PrevBlocks => Blocks </body>
endmodule
