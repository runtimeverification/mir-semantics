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

  configuration <memoryConfig>
                  <stack> .List </stack>
                  <heap>  .Map  </heap>
                </memoryConfig>
endmodule

module KMIR-MEMORY-API
  imports KMIR-SYNTAX

  syntax Address
  syntax Value
  syntax KItem ::= #setValue( Address, Value ) // non-functional due to state update
                 | #setLocal( Local, Value )   [function]

  syntax Value ::= #loadValue( Address )       [function]
                 | #loadLocal( Local )         [function]
                 | #loadPtr( Address, Value )  [function]
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

  // Memory Implementation Structures

  syntax Address ::= LocalAddr( Int,                     // stack frame height
                                Place )                  // stack local address
                   | GlobalAddr( Int,                    // global address
                                 ProjectionElems )       // projection out of global address

  syntax Value ::= Scalar( Int, Int, Bool )              // value, bit-width, signedness   for bool, un/signed int
                 | Float( Float, Int )                   // value, bit-width               for f16-f128
                 | Ptr( Address, MaybeValue )            // address, metadata              for ref/ptr
                 | Range( List )                         // homogenous values              for array/slice
                 | Struct( List )                        // heterogenous value list        for tuples and structs (standard, tuple, or anonymous) | Uninit()                              // for uninitialized values
                 | "Any"                                 // arbitrary value                for transmute/invalid ptr lookup

  syntax StackFrameRecord ::= Frame( Address,            // address of caller function
                                     MaybeBasicBlockIdx, // basic block to return to
                                     Place,              // place to store return value
                                     UnwindAction,       // action to perform if we panic
                                     List )              // stack locals

  syntax MemoryWrite ::= MemWrite( writeAddr: Int,       // address to overwrite
                                   writeVal:  Value )    // value to store at address

  // Memory Implementation Rules

  syntax ProjectionElems ::= #getProj( Address )                        [function] // get projections from Address

  syntax Value ::= #prj( Address, ProjectionElem, Value )               [function] // project point out of Value located at address

  syntax MemoryWrite ::= #set( Int, ProjectionElems, Value, Value )     [function] // update Value1 at projected point with Value2 and store at Int address
                       | #inj( Int, PrjectionElem, Value, MemoryWrite ) [function] // perform Write, accumulating any missing context
                       | #inj(      PrjectionElem, Value, MemoryWrite ) [function] // helper function for #inj

  syntax List ::= #update1(List, Int, Value )                           [function] // updates an index in the list
                | #updateN(List, Int, Int, Bool, Value )                [function] // updates multiple indices in the list

  syntax KItem ::= #write( MemoryWrite )                                       // perform memory write

  rule <k> #setValue( Addr, Val ) => #write( #set( #prj(Addr), #loadValue( Addr ), Val ) ) ... </k>

  rule #getProj(LocalAddr(_, place(_, Prjs))) => Prjs
  rule #getProj(GlobalAddr(_, Prjs))          => Prjs

  rule #set( Addr, Prj Prjs, Scrutinee, Val )
    => #if NoOpProjection(Prj)
         #then #set( Addr, Prjs, Scrutinee, Val )
         #else #if Prj ==K projectionElemDeref
           #then #set( Addr, Prjs, #prj( Addr, Prj, Scrutinee ) )
           #else #inj( Addr, Prj, Scrutinee, #set( Addr, Prjs, #prj( Prj, Scrutinee ) Val ) )
       #fi #fi

  // TODO: deal with self-referential pointers
  rule #prj( Addr, projectionElemDeref,                          Ptr(Next, Meta) ) => #loadPtr(Addr, Meta)
  rule #prj( Addr, projectionElemField(fieldIdx(I), _),          Struct( Flds )  ) => #loadField(I, Flds)
  rule #prj( Addr, projectionElemIndex(local(Idx)),              Range(Mem)      ) => #loadIndex(#loadLocal(Idx), Mem)
  rule #prj( Addr, projectionElemConstantIndex(Off, _, FromEnd), Range(Mem)      ) => #loadIndex(Off, Mem)
  rule #prj( Addr, projectionElemSubslice(From, To, Dir),        Range(Mem)      ) => #loadSlice(From, To, Dir, Mem)

  rule #inj( Orig, Prj, Scrutinee, MemWrite(Addr, Val) )
    => #if Orig =/= Addr
         #then MemWrite(Addr, Val)
         #else #inj( Prj, Scrutinee, MemWrite(Orig, Val) )
       #fi

  rule #inj( projectionElemField(fieldIdx(I), _),          Struct( Flds ),  MemWrite(Addr, Val) ) => MemWrite(Addr, #update1(Flds, I,               Val))
  rule #inj( projectionElemIndex(local(Idx)),              Range(Mem),      MemWrite(Addr, Val) ) => MemWrite(Addr, #update1(Mem,  I,               Val))
  rule #inj( projectionElemConstantIndex(Off, _, FromEnd), Range(Mem),      MemWrite(Addr, Val) ) => MemWrite(Addr, #update1(Mem,  #loadLocal(Idx), Val))
  rule #inj( projectionElemSubslice(From, To, Dir),        Range(Mem),      MemWrite(Addr, Val) ) => MemWrite(Addr, #updateN(Mem,  From, To, Dir,   Val))

  rule #update1( Mem, Idx, Val )
    => #if Idx >=Int size(Mem)
         #then Mem
         #else Mem [ Idx <- Val ]
       #else
    requires Idx >=Int 0

  rule #updateN( Mem, From, To, Dir, Range(New) )
    => #if From >= size(Mem)
         #then Mem
         #else updateList(Mem, From, range(New, 0, 
    requires From >=Int 0
     andBool To   >=Int 0
     andBool (notBool Dir) impliesBool (                To  -Int From ==Int size(New))
     andBool          Dir  impliesBool ((size(Mem) -Int To) -Int From ==Int size(New))
endmodule

module KMIR
  imports KMIR-SYNTAX
  imports LIST
  imports STRING
  imports BOOL
  imports BYTES
  imports K-EQUAL



  // Operand Evaluation

  // Statement/Terminator Evaluation
  //
  syntax KItem ::= #exec(StatementKind)
                 | #exec(TerminatorKind)

  // Terminators

  syntax KItem ::= #goto( Int )
                 | #goto( MaybeBasicBlockIdx )

  rule <k> basicBlock( .Statements, terminator( terminatorKindGoto( basicBlockIdx( N ) ), _SPAN ))
        => #exec( terminatorKindGoto( basicBlockIdx( N ) ) )
           ...
       </k>

  rule <k> #exec( terminatorKindGoto( basicBlockIdx( N ) ) ) => #goto( N ) ... </k>

  rule <k> #goto( N ) => #getBlock(N, Blocks) ... </k>
       <body> Blocks </body>
    requires N <Int #numBlocks(Blocks)

endmodule
