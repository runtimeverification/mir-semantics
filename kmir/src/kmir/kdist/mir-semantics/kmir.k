requires "kmir-ast.k"

module KMIR-SYNTAX
  imports KMIR-AST
  imports MAP
  imports LIST

  syntax InitialState ::= #init( Int, Map, Map )

  syntax Statements ::= "emptyBlock" [function]
  rule emptyBlock => .Statements
  syntax GenericArgs ::= "emptyArgs" [function]
  rule emptyArgs => .GenericArgs
  syntax Operands ::= "emptyOperands" [function]
  rule emptyOperands => .Operands
  syntax ProjectionElems ::= "noProjection" [function]
  rule noProjection => .ProjectionElems
  syntax Map ::= "emptyMap" [function]
  rule emptyMap => .Map
  syntax VarDebugInfos ::= "noVarDebug" [function]
  rule noVarDebug => .VarDebugInfos
endmodule

module KMIR-MEMORY
  imports INT
  imports KMIR-SYNTAX
  imports LIST
  imports MAP

  syntax Value

  configuration <memoryConfig>
                  <body> .BasicBlocks </body>
                  <stack> .List </stack>
                  <globals>  .Map  </globals>
                  <allocs> .Map </allocs>
                  <currentFunc> -1 </currentFunc>
                </memoryConfig>
endmodule

// TODO: try to rewrite most contextual functions to not be contextual
//
// 1. setPlace
// 2. loadPlace
// 3. loadValue
// 4. loadLocal
//
// TODO: parameterize #makeStruct by two values:
// 1. the variant index (we currently have this)
// 2. the struct kind index (we currently lack this)
// In particular, the concrete memory model will need BOTH indices to look up the type layout
//
// TODO: implement missing functions
// 1. #loadAllocation
// 2. #loadUnevalConst
// 3. #deinitPlace
// 4. #setDisc
// 5. #assume
// 6. #copy
//
// TODO: fixup incorrect function implementations
// 1. #evalOp
// 2. #evalCast
// 3. #makeTLRef

module KMIR-MEMORY-API
  imports KMIR-SYNTAX

  // information transfers between the frontend and backend via these three types
  // 1. Addresses are abstract representations of memory locations
  // 2. Values are abstract representations of results of operations which may be stored to/read from addresses
  // 3. Results capture responses from the backend to the frontend that are more structured than mere Values/Addresses
  syntax Address
  syntax Value
  syntax Result ::= #value( Value )
                  | #function( Body )
                  | #goto( MaybeBasicBlockIdx )

  // UN-EFFECTFUL OPERATIONS
  // =======================

  // Un-effectul operations that produce a Value wrapped in a Result
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

  // Un-effectful operations that produce a Body wrapped in a Result
  syntax KItem ::= #loadFnPtr( Value )

  // Un-effectful operations that directly return values
  syntax Value ::= #loadValue( Address )                      [function]
                 | #loadPlace( Place )                        [function]
                 | #loadLocal( Local )                        [function]
                 | #loadPtr( Address, Value )                 [function]
                 | #loadAllocation( Ty, Allocation )          [function]
                 | #loadUnevalConst( Ty, Int, MaybePromoted ) [function]
                 | #makeFnPtrValue( Int )                     [function]
                 | #makeStructValue( Int, List )              [function]
                 | #getNoOpFnAddr()                           [function]
                 | #getIntrinsicAddr( String )                [function]

  // Un-effectful operations that decode values into K built-in sorts
  syntax Int  ::= #readScalar( Value ) [function]
  syntax Bool ::= #isTrue( Value )     [function]

  // EFFECTFUL OPERATIONS
  // ====================

  // NOTE: Any effectful operation which is a function must desugar into a non-functional effectful operation

  // Effectful operations that update memory (on stack or otherwise) with no Result
  syntax KItem ::= #setValue( Address, Value )
                 | #setDisc( Place, Int )
                 | #deinitPlace( Place )
                 | #copy( List )
                 | #setPlace( Place, Value )   [function]
                 | #setLocal( Local, Value )   [function]

  // Effectful operations that modify the stack with no Result
  syntax KItem ::= #setupStackFrame( Value, BasicBlocks, List, Int, LocalDecls, Int, Place, MaybeBasicBlockIdx, UnwindAction )
                 | #setupFakeStackFrame()
                 | "#saveRetVal"
                 | "#setProcRetVal"
                 | "#return"

  // Effectful operations that modify control flow with no Result
  syntax KItem ::= #assume( List )
endmodule

module KMIR-CONFIGURATION
  imports KMIR-SYNTAX
  imports KMIR-MEMORY

  syntax RetVal ::= "NoRetVal"
                  | Value

  configuration <kmir>
                  <k> $PGM:InitialState </k>
                  <retVal> NoRetVal </retVal>
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

  // 1. AddressBase: represents addresses at the level of K maps; these are the only truly "writable" addresses
  // 2. Address: represents an address that may refer to the interior of a structured value
  // 3. Value: represents byte structures abstractly
  // 4. StackFrameRecord: represents stack frames abstractly
  // 5. MemoryWrite: represents a possible write to memory

  syntax AddressBase ::= AddrBase( Int )                 // global index
                       | AddrBase( Int, Int )            // stack frame height, local var index

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

  syntax StackFrameRecord ::= Frame( Int,                // address of caller function
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
                 | #prjs( ProjectionElems, Value )                               [function] // project point out of Value at arbitrary depth

  syntax MemoryWrite ::= #set( AddressBase, ProjectionElems, Value, Value )      [function] // update Value1 projected via ProjectionElems with Value2 and store at AddressBase
                       | #setPtr( Address, ProjectionElems, Value  )             [function] // update Value at address, further projected out via ProjectionElems
                       | #inj( AddressBase, ProjectionElem, Value, MemoryWrite ) [function] // perform Write, accumulating any missing context
                       | #inj(              ProjectionElem, Value, MemoryWrite ) [function] // helper function for #inj

  syntax List ::= #update1(List, Int, Value )                                    [function] // updates an index in the list
                | #updateN(List, Int, Int, Bool, Value )                         [function] // updates multiple indices in the list

  syntax KItem ::= #write( MemoryWrite )                                                    // perform memory write

  syntax StackFrameRecord ::= #setStkVar( StackFrameRecord, Int, Value )         [function] // perform stack variable update

  syntax Value ::= #loadField( Int, List )                                       [function] // these are helper functions for implementing loads
                 | #loadIndex( Value, List )                                     [function]
                 | #loadIndex( Int, List )                                       [function]
                 | #loadSlice( Int, Int, Bool, List )                            [function]
                 | #loadVar( List, Int, Int )                                    [function]
                 | #loadVar( StackFrameRecord, Int )                             [function]

  syntax Bool ::= #NoOpProjection( ProjectionElem )                              [function] // this is a helper function for implementing loads
                | #validSlice(List, Int, Int, Bool)                              [macro]    // this is a helper function for implementing loads/stores

  syntax Int ::= #sizeSlice(List, Int, Int, Bool)                                [macro]    // this is a helper function for implementing loads/stores
               | #boolToInt( Bool )                                              [function] // miscellaneous helper function
               | #readAddrAsInt( Value )                                         [function] // miscellaneous helper function

  syntax Address ::= #readAddr( Value )                                          [function] // miscellaneous helper function
                   | #delProj( Address )                                         [function] // miscellaneous helper function

  // Call Impl

  rule <k> #setupStackFrame( CalleeFun, Blocks, Args, ArgCount, _Locals, LocalCount, Dest, Target, Act ) => .K ... </k>
       <stack> Frames => ListItem(Frame( CurrFun, Target, Dest, Act, Args makeList( LocalCount -Int ArgCount, Any ) )) Frames </stack>
       <currentFunc> CurrFun => #readAddrAsInt(CalleeFun) </currentFunc>
       <body> _PrevBlocks => Blocks </body>

  rule <k> #setupFakeStackFrame() => .K ... </k>
       <stack> .List => ListItem(Frame( -1, noBasicBlockIdx, place(local(-1), .ProjectionElems), unwindActionTerminate, ListItem(Any))) </stack>

  rule <k> #saveRetVal => #setValue( LocalAddr( size(Frames) -Int 1, Dest ), { Locals [ 0 ] }:>Value ) ... </k>
       <stack> ListItem(Frame( _, _, Dest, _, Locals )) Frames </stack>
    requires size(Frames) >=Int 1

  rule <k> #setProcRetVal => .K ... </k>
       <stack> ListItem(Frame( _, _, _, _, ListItem( V:Value ) )) => .List </stack>
       <retVal> NoRetVal => V </retVal>

  rule <k> #return => #if size(Frames) =/=Int 1 #then #goto(Target) #else .K #fi ... </k>
       <stack> ListItem(Frame(Addr, Target, _, _, _)) Frames => Frames </stack>
       <body> _PrevBlocks => #if size(Frames) =/=Int 1 #then blocks( { { Mem [ Addr ] }:>List [0] }:>Body ) #else .BasicBlocks #fi </body>
       <globals> Mem </globals>

  // Eval Impl

  rule <k> #deinitPlace( _PLACE ) => .K ... </k>

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
       <stack> Stack => #updateStk( Stack, Idx, LIdx, Val ) </stack>

  rule <k> #write( MemWrite( AddrBase(Idx), Val ) ) => .K ... </k>
       <globals> Globals => Globals [ Idx <- Val ] </globals>

  syntax List ::= #updateStk( List, Int, Int, Value ) [function]
  rule #updateStk( Stack, Idx, LIdx, Val )
    => Stack [ size(Stack) -Int (Idx +Int 1) <- #setStkVar( { Stack [ size(Stack) -Int (Idx +Int 1)] }:>StackFrameRecord, LIdx, Val ) ]

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

  rule <k> #loadFnPtr( Ptr( GlobalAddr( Addr, .ProjectionElems ), NoValue ) )
        => #function( { { Mem [ Addr ] }:>List [0] }:>Body )
           ...
       </k>
       <globals> Mem </globals>
       requires isList(Mem [ Addr ])
        andBool isBody({ Mem [ Addr ] }:>List [0])

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
  //       any self-referential type has to be mediated by a struct which wraps a pointer
  rule #prj( projectionElemDeref,                    Ptr( Next, Meta ) ) => #loadPtr(Next, Meta)
  rule #prj( projectionElemField(fieldIdx(I), _),    Struct( _, Flds ) ) => #loadField(I, Flds)
  rule #prj( projectionElemIndex(Idx),               Range( Mem )      ) => #loadIndex(#loadLocal(Idx), Mem)
  rule #prj( projectionElemConstantIndex(Off, _, _), Range( Mem )      ) => #loadIndex(Off, Mem)
  rule #prj( projectionElemSubslice(From, To, Dir),  Range( Mem )      ) => #loadSlice(From, To, Dir, Mem)
  rule #prj( projectionElemDowncast(_),              Val               ) => Val
  rule #prj( projectionElemOpaqueCast(_),            Val               ) => Val
  rule #prj( projectionElemSubtype(_),               Val               ) => Val

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

  rule #readScalar( Scalar( Val, _Width, _Signed ) )     => Val
  rule #readAddrAsInt( Ptr( GlobalAddr( Addr, _ ), _ ) ) => Addr
  rule #readAddr( Ptr( Addr, _ ) )                       => Addr
  rule #isTrue( Scalar( Val, 1, false ) )                => Val =/=Int 0

  rule #makeFnPtrValue( Addr ) => Ptr( GlobalAddr( Addr, .ProjectionElems ), NoValue )
  rule #makeStructValue( Id, Args ) => Struct( Id, Args )

  // Special Address Creation
  rule #getNoOpFnAddr()       => #makeFnPtrValue( -1 ) // TODO: implement NOP using correct intrinsic mapping
  rule #getIntrinsicAddr( _ ) => #makeFnPtrValue( -2 ) // TODO: implement correct intrinsic mapping
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
  imports MAP

  // Initialization

  rule <k> #init( FnAddr, Mem, Allocs )
        => #setupFakeStackFrame()
        ~> #prepareCall( #makeFnPtrValue( FnAddr ), .List, place(local(0), .ProjectionElems), noBasicBlockIdx, unwindActionTerminate )
        ~> #setProcRetVal
           ...
       </k>
       <globals> .Map => Mem </globals>
       <allocs> .Map => Allocs </allocs>

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
  rule #evalArgs(terminatorKindGoto(_TARGET))                                        => .K
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

  rule <k> #evalArgs( ListItem( operandConstant(CONST)    => CONST ) _ARGS, _EVALED ) ... </k>
  rule <k> #evalArgs( ListItem( constOperand(_, _, CONST) => CONST ) _ARGS, _EVALED ) ... </k>

  rule <k> #evalArgs( ListItem( tyConst( KIND, _TID ) => KIND ) _ARGS, _EVALED ) ... </k>

  rule <k> #evalArgs( ListItem( TYCONST:TyConstKind ) ARGS, EVALED )
        => #evalArgs( ARGS, ListItem( #evalTyConst(TYCONST) ) EVALED )
           ...
       </k>

  rule <k> #evalArgs( ListItem( mirConst( KIND, TY, mirConstId(CID) )  ) ARGS, EVALED )
        => #evalArgs( ARGS, ListItem( #evalMirConst( TY, CID, KIND ) ) EVALED )
           ...
       </k>

  rule <k> #evalArgs( ListItem( PLACE:Place ) ARGS, EVALED )
        => #evalArgs( ARGS, ListItem( #loadPlace( PLACE ) ) EVALED )
           ...
       </k>

  rule <k> #evalArgs( .List, ARGS ) => #operands( ARGS ) ... </k>

  syntax Value ::= #evalMirConst( Ty, Int, ConstantKind ) [function]
                 | #evalTyConst( TyConstKind )            [function]

  rule #evalMirConst( _TY, _CID, constantKindZeroSized                                                     ) => #makeStructValue ( 0, .List )
  rule #evalMirConst(  TY, _CID, constantKindAllocated( ALLOC )                                            ) => #loadAllocation( TY, ALLOC )
  rule #evalMirConst(  TY, _CID, constantKindUnevaluated( unevaluatedConst( DEF, _ARGS, PROMOTED_INDEX ) ) ) => #loadUnevalConst( TY, DEF, PROMOTED_INDEX )
  rule #evalMirConst( _TY, _CID, constantKindTy( tyConst( KIND, _ID ) )                                    ) => #evalTyConst( KIND )
  // Handle extended function constant types
  rule #evalMirConst( _TY, _CID, constantKindFnDef( Addr )                                                 ) => #makeFnPtrValue( Addr )
  rule #evalMirConst( _TY, _CID, constantKindNoOp                                                          ) => #getNoOpFnAddr()
  rule #evalMirConst( _TY, _CID, constantKindIntrinsic( Sym )                                              ) => #getIntrinsicAddr( Sym )

  rule #evalTyConst( tyConstKindZSTValue( _TY )           ) => #makeStructValue( 0, .List )
  rule #evalTyConst( tyConstKindValue( TY, ALLOC )        ) => #loadAllocation( TY, ALLOC )
  // NOTE: tyConstKindUnevaluated( DEF, ARGS ) should not occur --- all type system constants must be fully evaluated

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

  // Statements: https://doc.rust-lang.org/nightly/nightly-rustc/rustc_middle/mir/enum.StatementKind.html
  //
  // NOTE: To the best of our understanding, all statements here which are currently NoOps actually are uneffectful.
  // The most complex case is PlaceMention: it attempts to compute a place _without_ loading it.
  // In practice, such a read can only indirectly affect machine state through cache/page table updates, instruction pipelining, etc...
  // However, since we do not model either of these effects, for us, this is a NoOp.

  syntax KItem ::= #assign(Place)

  rule <k> #exec(statementKindAssign(PLACE, RVAL))                           => #evalArgs(RVAL) ~> #eval(RVAL) ~> #assign(PLACE) ... </k>
  rule <k> #value(VAL) ~> #assign(PLACE)                                     => #setPlace(PLACE, VAL)                            ... </k>
  rule <k> #exec(statementKindIntrinsic(INT))                                => #evalArgs(INT) ~> #eval(INT)                     ... </k>
  rule <k> #exec(statementKindSetDiscriminant(PLACE, variantIdx(IDX)))       => #setDisc(PLACE, IDX)                             ... </k>
  rule <k> #exec(deinit(PLACE))                                              => #deinitPlace(PLACE)                              ... </k>
  rule <k> #exec(statementKindPlaceMention(_Place))                          => .K                                               ... </k>
  rule <k> #exec(statementKindFakeRead(_FakeReadCause, _Place))              => .K                                               ... </k>
  rule <k> #exec(statementKindStorageLive(_Local))                           => .K                                               ... </k>
  rule <k> #exec(statementKindStorageDead(_Local))                           => .K                                               ... </k>
  rule <k> #exec(statementKindRetag(_RetagKind, _Place))                     => .K                                               ... </k>
  rule <k> #exec(statementKindAscribeUserType(_Place, _UserType, _Variance)) => .K                                               ... </k>
  rule <k> #exec(statementKindCoverage(_Coverage))                           => .K                                               ... </k>
  rule <k> #exec(statementKindConstEvalCounter)                              => .K                                               ... </k>
  rule <k> #exec(statementKindNop)                                           => .K                                               ... </k>

  // Terminators: https://doc.rust-lang.org/nightly/nightly-rustc/rustc_middle/mir/enum.TerminatorKind.html
  //
  // NOTE: Internal MIR terminator UnwindTermiante maps to stable MIR Abort.
  // NOTE: Some internal MIR terminators are not implemented in stable MIR yet --- we do not implement these either.
  // TODO: implement resume/abort --- i.e. logic for panicking

  syntax KItem ::= "#stuck"
                 | #goto( Int )
                 | #goto( BasicBlockIdx )
                 | #jump( Int, Branches, BasicBlockIdx )
                 | #prepareCall( Value, List, Place, MaybeBasicBlockIdx, UnwindAction )
                 | #call(        Value, List, Place, MaybeBasicBlockIdx, UnwindAction )
                 | #assert( Value )

  rule <k>                    #exec( terminatorKindGoto( basicBlockIdx( N ) ) )                         => #goto( N )                                                               ... </k>
  rule <k> #operands(ARGS) ~> #exec(terminatorKindSwitchInt(_ARG, TARGETS))                             => #jump(#readScalar(#getArg(ARGS)), branches(TARGETS), otherwise(TARGETS)) ... </k>
  rule <k>                    #exec(terminatorKindResume)                                               => .K                                                                       ... </k>
  rule <k>                    #exec(terminatorKindAbort)                                                => .K                                                                       ... </k>
  rule <k>                    #exec(terminatorKindReturn)                                               => #saveRetVal ~> #return                                                   ... </k>
  rule <k>                    #exec(terminatorKindUnreachable)                                          => #stuck                                                                   ... </k>
  rule <k>                    #exec(terminatorKindDrop(PLACE, _TARGET, _ACT))                           => #deinitPlace(PLACE)                                                      ... </k>
  rule <k> #operands(ARGS) ~> #exec(terminatorKindCall(_FUNC, _ARGS, DEST, TARGET, ACT))                => #prepareCall(#getFstArg(ARGS), #getRestArgs(ARGS), DEST, TARGET, ACT)    ... </k>
  rule <k> #operands(ARGS) ~> #exec(assert(_COND, _EXPECTED, _MSG, _TARGET, _ACT))                      => #assert(#getArg(ARGS))                                                   ... </k>
  rule <k>                    #exec(terminatorKindInlineAsm(_TMPL, _ARGS, _OPTS, _SPNS, _TARGET, _ACT)) => #stuck                                                                   ... </k>

  // Goto Terminator

  rule <k> #goto(                    basicBlockIdx( N )   ) => #goto( N )             ... </k>
  rule <k> #goto( someBasicBlockIdx( basicBlockIdx( N ) ) ) => #goto( N )             ... </k>
  rule <k> #goto( N )                                       => #getBlock( N, Blocks ) ... </k>
       <body> Blocks </body>
    requires N <Int #numBlocks(Blocks)


  // Jump Terminator

  rule <k> #jump( I, branch(J, BBIdx) TGTS, OWISE) => #if I ==Int J #then #goto(BBIdx) #else #jump(I, TGTS, OWISE) #fi ... </k>
  rule <k> #jump(_I, .Branches,             OWISE) => #goto(OWISE)                                                     ... </k>

  // Assert Terminator

  rule <k> #assert( Val:Value ) => #if #isTrue( Val ) #then .K #else #stuck #fi ... </k>

  // Call Terminator

  syntax Int ::= #numLocals( LocalDecls ) [function]

  rule <k> #prepareCall( Func, Args, Dest, Target, Act ) => #loadFnPtr( Func ) ~> #call( Func, Args, Dest, Target, Act ) ... </k>

  rule <k> #function(body(Blocks, Locals, ArgCount, _DebugInfo, _SpreadArg, _Span))
        ~> #call( Func, Args, Dest, Target, Act )
        => #setupStackFrame( Func, Blocks, Args, ArgCount, Locals, #numLocals(Locals), Dest, Target, Act )
        ~> #goto( 0 )
           ...
       </k>

  // Terminator Helper Functions

  syntax Int ::= #numBlocks( BasicBlocks ) [function]
  rule #numBlocks( _ BS ) => 1 +Int #numBlocks( BS )
  rule #numBlocks( .BasicBlocks ) => 0

  syntax BasicBlock ::= #getBlock( Int, BasicBlocks ) [function]
  rule #getBlock( I, _Block  Blocks ) => #getBlock( I -Int 1, Blocks ) requires I >Int 0
  rule #getBlock( 0,  Block _Blocks ) => Block

  rule #numLocals( _:LocalDecl Rest:LocalDecls ) => 1 +Int #numLocals( Rest )
  rule #numLocals( .LocalDecls )                 => 0
endmodule
