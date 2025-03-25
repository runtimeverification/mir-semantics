# MIR Semantics in K

```k
requires "kmir-ast.md"
requires "rt/data.md"
requires "lemmas/kmir-lemmas.md"
```

## Syntax of MIR in K

The MIR syntax is largely defined in [KMIR-AST](./kmir-ast.md) and its
submodules. The execution is initialised based on a loaded `Pgm` read
from a json format of stable-MIR, and the name of the function to execute.

```k
module KMIR-SYNTAX
  imports KMIR-AST

  syntax KItem ::= #init( Pgm )

endmodule
```

## (Dynamic) Semantics

### Execution Configuration

The execution (dynamic) semantics of MIR in K is defined based on the
configuration of the running program.

Essential parts of the configuration:
* the `k` cell to control the execution
* a `stack` of `StackFrame`s describing function calls and their data
* `currentFrame`, an unpacked version of the top of `stack`
* the `functions` map to look up function bodies when they are called
* the `memory` cell which abstracts allocated heap data

The entire program's return value (`retVal`) is held in a separate cell.

Besides the `caller` (to return to) and `dest` and `target` to specify where the return value should be written, a `StackFrame` includes information about the `locals` of the currently-executing function/item. Each function's code will only access local values (or heap data referenced by them). Local variables carry type information (see `RT-DATA`).

```k
module KMIR-CONFIGURATION
  imports KMIR-SYNTAX
  imports INT-SYNTAX
  imports BOOL-SYNTAX
  imports RT-DATA-HIGH-SYNTAX

  syntax RetVal ::= return( Value )
                  | "noReturn"

  syntax StackFrame ::= StackFrame(caller:Ty,                 // index of caller function
                                   dest:Place,                // place to store return value
                                   target:MaybeBasicBlockIdx, // basic block to return to
                                   UnwindAction,              // action to perform on panic
                                   locals:List)               // return val, args, local variables

  configuration <kmir>
                  <k> #init($PGM:Pgm) </k>
                  <retVal> noReturn </retVal>
                  <currentFunc> ty(-1) </currentFunc> // to retrieve caller
                  // unpacking the top frame to avoid frequent stack read/write operations
                  <currentFrame>
                    <currentBody> .List </currentBody>
                    <caller> ty(-1) </caller>
                    <dest> place(local(-1), .ProjectionElems)</dest>
                    <target> noBasicBlockIdx </target>
                    <unwind> unwindActionUnreachable </unwind>
                    <locals> .List </locals>
                  </currentFrame>
                  // remaining call stack (without top frame)
                  <stack> .List </stack>
                  // function store, Ty -> MonoItemFn
                  <functions> .Map </functions>
                  // heap
                  <memory> .Map </memory> // FIXME unclear how to model
                  // FIXME where do we put the "GlobalAllocs"? in the heap, presumably?
                  <start-symbol> symbol($STARTSYM:String) </start-symbol>
                  // static information about the base type interning in the MIR
                  <basetypes> .Map </basetypes>
                </kmir>

endmodule
```


### Execution Control Flow

```k
module KMIR-CONTROL-FLOW
  imports KMIR-SYNTAX
  imports KMIR-CONFIGURATION
  imports MONO
  imports RT-DATA-HIGH
  imports TYPES

  imports BOOL
  imports LIST
  imports MAP
  imports K-EQUAL
```

Execution of a program begins by creating a stack frame for the `main`
function and executing its function body. Before execution begins, the
function map and the initial memory have to be set up.

```k
  // #init step, assuming a singleton in the K cell
  rule <k> #init(_NAME:Symbol _ALLOCS:GlobalAllocs FUNCTIONS:FunctionNames ITEMS:MonoItems TYPES:BaseTypes)
         =>
           #execFunction(#findItem(ITEMS, FUNCNAME), FUNCTIONS)
       </k>
       <functions> _ => #mkFunctionMap(FUNCTIONS, ITEMS) </functions>
       <start-symbol> FUNCNAME </start-symbol>
       <basetypes> _ => #mkTypeMap(.Map, TYPES) </basetypes>
```

The `Map` of types is static information used for decoding constants and allocated data into `Value`s.
It maps `Ty` IDs to `RigidTy` that can be supplied to decoding functions.

```k
  syntax Map ::= #mkTypeMap ( Map, BaseTypes ) [function, total]

  rule #mkTypeMap(ACC, .BaseTypes) => ACC

  // build map of Ty -> RigidTy from suitable pairs
  rule #mkTypeMap(ACC, baseType(TY, tyKindRigidTy(RIGID)) MORE:BaseTypes)
      =>
       #mkTypeMap(ACC[TY <- RIGID], MORE)
    requires notBool TY in_keys(ACC)
    [preserves-definedness] // key collision checked

  // skip anything that is not a RigidTy or causes a key collision
  rule #mkTypeMap(ACC, baseType(_TY, _OTHERTYKIND) MORE:BaseTypes)
      =>
       #mkTypeMap(ACC, MORE)
    [owise]
```


The `Map` of `functions` is constructed from the lookup table of `FunctionNames`,
composed with a secondary lookup of `Item`s via `symbolName`. This composed map will
only be populated for `MonoItemFn` items that are indeed _called_ in the code (i.e.,
they are callee in a `Call` terminator within an `Item`).

The function _names_ and _ids_ are not relevant for calls and therefore dropped.

```k
  syntax Map ::= #mkFunctionMap ( FunctionNames, MonoItems ) [ function, total ]
               | #accumFunctions ( Map, Map, FunctionNames ) [ function, total ]
               | #accumItems ( Map, MonoItems )              [ function, total ]

  rule #mkFunctionMap(Functions, Items)
    =>
       #accumFunctions(#mainIsMinusOne(Items), #accumItems(.Map, Items), Functions)
  //////////////////// ^^^^^^^^^^^^^^^^^^^^^^ HACK Adds "main" as function with ty(-1)
  syntax Map ::= #mainIsMinusOne(MonoItems) [function]
  rule #mainIsMinusOne(ITEMS) => ty(-1) |-> monoItemKind(#findItem(ITEMS, symbol("main")))
  ////////////////////////////////////////////////////////////////

  // accumulate map of symbol_name -> function (MonoItemFn), discarding duplicate IDs
  rule #accumItems(Acc, .MonoItems) => Acc

  rule #accumItems(Acc, monoItem(SymName, monoItemFn(_, _, _) #as Function) Rest:MonoItems)
     =>
       #accumItems(Acc (SymName |-> Function), Rest)
    requires notBool (SymName in_keys(Acc))
    [ preserves-definedness ] // key collisions checked

  // discard other items and duplicate symbolNames
  rule #accumItems(Acc, _:MonoItem Rest:MonoItems)
     =>
       #accumItems(Acc, Rest)
    [ owise ]

  // accumulate composed map of Ty -> MonoItemFn, using item map from before and function names
  rule #accumFunctions(Acc, _, .List) => Acc

  rule #accumFunctions(Acc, ItemMap, ListItem(functionName(TyIdx, functionNormalSym(SymName))) Rest )
    =>
      #accumFunctions(Acc (TyIdx |-> ItemMap[SymName]), ItemMap, Rest)
    requires SymName in_keys(ItemMap)
     andBool notBool (TyIdx in_keys(Acc))
    [preserves-definedness]

  // TODO handle NoOpSym and IntrinsicSym cases here

  // discard anything else:
  // - duplicate Ty mappings (impossible by construction in stable-mir-json)
  // - unknown symbol_name (impossible by construction in stable-mir-json)
  rule #accumFunctions(Acc, ItemMap, ListItem(_) Rest)
    =>
       #accumFunctions(Acc, ItemMap, Rest)
    [ owise ]

```

Executing a given named function means to create the `currentFrame` data
structure from its function body and then execute the first basic
block of the body. The function's `Ty` index in the `functions` map must
be known to populate the `currentFunc` field.

```k
  // find function through its MonoItemFn.name
  syntax MonoItem ::= #findItem ( MonoItems, Symbol ) [ function ]

  rule #findItem( (monoItem(_, monoItemFn(N, _, _)) #as ITEM) _REST, NAME )
     =>
       ITEM
    requires N ==K NAME
  rule #findItem( _:MonoItem REST:MonoItems, NAME )
     =>
       #findItem(REST, NAME)
    [owise]
  // rule #findItem( .MonoItems, _NAME) => error!

  syntax KItem ::= #execFunction ( MonoItem, FunctionNames )

  rule <k> #execFunction(
              monoItem(
                SYMNAME,
                monoItemFn(_, _, someBody(body((FIRST:BasicBlock _) #as BLOCKS,LOCALS, _, _, _, _)))
              ),
              FUNCTIONNAMES
            )
         =>
           #execBlock(FIRST)
         ...
       </k>
       <currentFunc> _ => #tyFromName(SYMNAME, FUNCTIONNAMES) </currentFunc>
       <currentFrame>
         <currentBody> _ => toKList(BLOCKS) </currentBody>
         <caller> _ => ty(-1) </caller> // no caller
         <dest> _ => place(local(-1), .ProjectionElems)</dest>
         <target> _ => noBasicBlockIdx </target>
         <unwind> _ => unwindActionUnreachable </unwind>
         <locals> _ => #reserveFor(LOCALS)  </locals>
       </currentFrame>

  // This function performs a reverse lookup in the functions table (looks up a `Ty` by name)
  // It defaults to `Ty(-1)` which is currently what `main` gets (`main` is not in the functions table)
  syntax Ty ::= #tyFromName( Symbol, FunctionNames ) [function, total]

  rule #tyFromName(NAME, ListItem(functionName(TY, FNAME)) _) => TY
    requires NAME ==K FNAME
  rule #tyFromName(NAME, ListItem(_) REST:List) => #tyFromName(NAME, REST)
    [owise]

  rule #tyFromName(_, .List) => ty(-1) // HACK see #mainIsMinusOne above

  syntax List ::= toKList(BasicBlocks) [function, total]

  rule toKList( .BasicBlocks )                => .List
  rule toKList(B:BasicBlock REST:BasicBlocks) => ListItem(B) toKList(REST)

  syntax List ::= #reserveFor( LocalDecls ) [function, total]

  rule #reserveFor(.LocalDecls) => .List

  rule #reserveFor(localDecl(TY, _, MUT) REST:LocalDecls)
      =>
       ListItem(noValue(TY, MUT)) #reserveFor(REST)
```

Executing a function body consists of repeated calls to `#execBlock`
for the basic blocks that, together, constitute the function body. The
execution of blocks is straightforward (first execute all statements,
then finish with the terminator that may branch, call other basic
blocks, or call another function).

```k
  // execution of blocks (composed of statements and terminator)
  syntax KItem ::= #execBlockIdx ( BasicBlockIdx )
                 | #execBlock ( BasicBlock )
                 | #execStmts ( Statements )
                 | #execStmt ( Statement )
                 | #execTerminator ( Terminator )

  rule <k> #execBlockIdx(basicBlockIdx(I))
         =>
           #execBlock( {BLOCKS[I]}:>BasicBlock )
         ...
       </k>
       <currentBody> BLOCKS </currentBody>
    requires 0 <=Int I
     andBool I <Int size(BLOCKS)
     andBool isBasicBlock(BLOCKS[I])
    [preserves-definedness] // valid list indexing checked

  rule <k> #execBlock(basicBlock(STATEMENTS, TERMINATOR))
         =>
           #execStmts(STATEMENTS) ~> #execTerminator(TERMINATOR)
         ...
       </k>

  rule <k> #execStmts(.Statements) => .K  ... </k>

  rule <k> #execStmts(STATEMENT:Statement STATEMENTS:Statements)
         =>
           #execStmt(STATEMENT) ~> #execStmts(STATEMENTS)
         ...
       </k>
```

`Statement` execution handles the different `StatementKind`s. Some of
these are irrelevant at the MIR level that this semantics is modeling
(e.g., all statements related to compile-time checks like borrowing
will effectively be no-ops at this level).

```k

  // all memory accesses relegated to another module (to be added)
  rule <k> #execStmt(statement(statementKindAssign(PLACE, RVAL), _SPAN))
         =>
           RVAL ~> #assign(PLACE)
         ...
       </k>

  // RVAL evaluation is implemented in rt/data.md

  syntax KItem ::= #assign ( Place )

  rule <k> VAL:TypedLocal ~> #assign(PLACE) ~> CONT
        =>
           VAL ~> #setLocalValue(PLACE) ~> CONT
        </k>

  rule <k> #execStmt(statement(statementKindSetDiscriminant(_PLACE, _VARIDX), _SPAN))
         =>
           .K // FIXME! write variant index to PLACE
         ...
       </k>

  rule <k> #execStmt(statement(statementKindIntrinsic(_INTRINSIC), _SPAN))
         =>
           .K // FIXME! effect of calling INTRINSIC
         ...
       </k>

  // statements related to locals allocation (not modelled here)
  rule <k> #execStmt(statement(statementKindDeinit(_PLACE)     , _SPAN)) => .K ... </k>
  rule <k> #execStmt(statement(statementKindStorageLive(_LOCAL), _SPAN)) => .K ... </k>
  rule <k> #execStmt(statement(statementKindStorageDead(_LOCAL), _SPAN)) => .K ... </k>


  // no-op statements
  rule <k> #execStmt(statement(statementKindRetag(_, _)             , _SPAN)) => .K ... </k>
  rule <k> #execStmt(statement(statementKindPlaceMention(_)         , _SPAN)) => .K ... </k>
  rule <k> #execStmt(statement(statementKindFakeRead(_, _)          , _SPAN)) => .K ... </k>
  rule <k> #execStmt(statement(statementKindAscribeUserType(_, _, _), _SPAN)) => .K ... </k>
  rule <k> #execStmt(statement(statementKindCoverage(_)             , _SPAN)) => .K ... </k>
  rule <k> #execStmt(statement(statementKindConstEvalCounter        , _SPAN)) => .K ... </k>
  rule <k> #execStmt(statement(statementKindNop                     , _SPAN)) => .K ... </k>
```

Execution of a `Terminator` can mean to jump to another block, branch
to more than one block (based on a variant index), or to perform a
function call, pushing a new stack frame and returning to a different
block after the call returns.

```k
  rule <k> #execTerminator(terminator(terminatorKindGoto(I), _SPAN))
         =>
           #execBlockIdx(I)
         ... // FIXME: We assume this is empty. Explicitly throw away or check that it is?
       </k>
```

A `SwitchInt` terminator selects one of the blocks given as _targets_,
depending on the value of a _discriminant_.

```k
  rule <k> #execTerminator(terminator(terminatorKindSwitchInt(DISCR, TARGETS), _SPAN)) ~> _CONT
         =>
           #readOperand(DISCR) ~> #selectBlock(TARGETS)
       </k>

  rule <k> typedLocal(Integer(I, _, _), _, _) ~> #selectBlock(TARGETS)
         =>
           #execBlockIdx(#selectBlock(I, TARGETS))
       ...
       </k>

  rule <k> typedLocal(BoolVal(false), _, _) ~> #selectBlock(TARGETS)
         =>
           #execBlockIdx(#selectBlock(0, TARGETS))
       ...
       </k>

  rule <k> typedLocal(BoolVal(true), _, _) ~> #selectBlock(TARGETS)
         =>
           #execBlockIdx(#selectBlock(1, TARGETS))
       ...
       </k>

  syntax KItem ::= #selectBlock ( SwitchTargets )

  syntax BasicBlockIdx ::= #selectBlock ( Int , SwitchTargets)              [function, total]
                         | #selectBlockAux ( Int, Branches, BasicBlockIdx ) [function, total]

  rule #selectBlock(I, switchTargets(BRANCHES, OTHERWISE)) => #selectBlockAux(I, BRANCHES, OTHERWISE)

  rule #selectBlockAux(I, branch( J       , IDX) _REST, _      ) => IDX
    requires I ==Int J
  rule #selectBlockAux(I, branch(mirInt(J), IDX) _REST, _      ) => IDX
    requires I ==Int J

  rule #selectBlockAux(I, branch( J       , _  ) REST , DEFAULT) => #selectBlockAux(I, REST, DEFAULT)
    requires I =/=Int J
  rule #selectBlockAux(I, branch(mirInt(J), _  ) REST , DEFAULT) => #selectBlockAux(I, REST, DEFAULT)
    requires I =/=Int J

  rule #selectBlockAux(_,                   .Branches , DEFAULT) => DEFAULT

```

`Return` simply returns from a function call, using the information
stored in the top stack frame to pass the returned value. The return
value is the value in local `_0`, and will go to the _destination_ in
the `LOCALS` of the caller's stack frame. Execution continues with the
context of the enclosing stack frame, at the _target_.

If the returned value is a `Reference`, its stack height must be decremented because a stack frame is popped.
NB that a stack height of `0` cannot occur here, because the compiler prevents local variable references from escaping.

```k
  rule <k> #execTerminator(terminator(terminatorKindReturn, _SPAN)) ~> _
         =>
           #decrementRef(LOCAL0) ~> #setLocalValue(DEST) ~> #execBlockIdx(TARGET) ~> .K
       </k>
       <currentFunc> _ => CALLER </currentFunc>
       //<currentFrame>
         <currentBody> _ => #getBlocks(FUNCS, CALLER) </currentBody>
         <caller> CALLER => NEWCALLER </caller>
         <dest> DEST => NEWDEST </dest>
         <target> someBasicBlockIdx(TARGET) => NEWTARGET </target>
         <unwind> _ => UNWIND </unwind>
         <locals> ListItem(LOCAL0:TypedLocal) _ => NEWLOCALS </locals>
       //</currentFrame>
       // remaining call stack (without top frame)
       <stack> ListItem(StackFrame(NEWCALLER, NEWDEST, NEWTARGET, UNWIND, NEWLOCALS)) STACK => STACK </stack>
       <functions> FUNCS </functions>
     requires CALLER in_keys(FUNCS)
      // andBool DEST #within(LOCALS)
     [preserves-definedness] // CALLER lookup defined, DEST within locals TODO

  syntax List ::= #getBlocks(Map, Ty) [function]
                | #getBlocksAux(MonoItemKind)  [function, total]

  rule #getBlocks(FUNCS, ID) => #getBlocksAux({FUNCS[ID]}:>MonoItemKind)
    requires ID in_keys(FUNCS)

  // returns blocks from the body
  rule #getBlocksAux(monoItemFn(_, _, noBody)) => .List
  rule #getBlocksAux(monoItemFn(_, _, someBody(body(BLOCKS, _, _, _, _, _)))) => toKList(BLOCKS)
  // other item kinds are not expected or supported FIXME: Just getting stuck for now
  rule #getBlocksAux(monoItemStatic(_, _, _)) => .List // should not occur in calls at all
  rule #getBlocksAux(monoItemGlobalAsm(_)) => .List // not supported. FIXME Should error, maybe during #init
```

When a `terminatorKindReturn` is executed but the optional target is empty
(`noBasicBlockIdx`), the program is ended, using the returned value from `_0`
as the program's `retVal`.
The call stack is not necessarily empty at this point so it is left untouched.

```k
  syntax KItem ::= "#EndProgram"

  rule [endprogram-return]:
       <k> #execTerminator(terminator(terminatorKindReturn, _SPAN)) ~> _
         =>
           #EndProgram
       </k>
       <retVal> _ => return(VAL) </retVal>
       <currentFrame>
         <target> noBasicBlockIdx </target>
         <locals> ListItem(typedLocal(VAL, _, _)) ... </locals>
         ...
       </currentFrame>

  rule [endprogram-no-return]:
       <k> #execTerminator(terminator(terminatorKindReturn, _SPAN)) ~> _
         =>
           #EndProgram
       </k>
       <currentFrame>
         <target> noBasicBlockIdx </target>
         <locals> ListItem(noValue(_, _)) ... </locals>
         ...
       </currentFrame>
```


`Call` is calling another function, setting up its stack frame and
where the returned result should go.


```k
  rule <k> #execTerminator(terminator(terminatorKindCall(FUNC, ARGS, DEST, TARGET, UNWIND), _SPAN))
         =>
           #setUpCalleeData({FUNCTIONS[#tyOfCall(FUNC)]}:>MonoItemKind, ARGS)
         ...
       </k>
       <currentFunc> CALLER => #tyOfCall(FUNC) </currentFunc>
       <currentFrame>
         <currentBody> _ </currentBody>
         <caller> OLDCALLER => CALLER </caller>
         <dest> OLDDEST => DEST </dest>
         <target> OLDTARGET => TARGET </target>
         <unwind> OLDUNWIND => UNWIND </unwind>
         <locals> LOCALS </locals>
       </currentFrame>
       <stack> STACK => ListItem(StackFrame(OLDCALLER, OLDDEST, OLDTARGET, OLDUNWIND, LOCALS)) STACK </stack>
       <functions> FUNCTIONS </functions>
    requires #tyOfCall(FUNC) in_keys(FUNCTIONS)
     andBool isMonoItemKind(FUNCTIONS[#tyOfCall(FUNC)])
    [preserves-definedness] // callee lookup defined

  syntax Ty ::= #tyOfCall( Operand ) [function, total]

  rule #tyOfCall(operandConstant(constOperand(_, _, mirConst(constantKindZeroSized, Ty, _))))
    => Ty
  rule #tyOfCall(_) => ty(-1) [owise] // copy, move, non-zero size: not supported
```

The local data has to be set up for the call, which requires information about the local variables of a call. This step is separate from the above call stack setup because it needs to retrieve the locals declaration from the body. Arguments to the call are `Operands` which refer to the old locals (`OLDLOCALS` below), and the data is either _copied_ into the new locals using `#setArgs`, or it needs to be _shared_ via references.

An operand may be a `Reference` (the only way a function could access another function call's `local` variables). For this case, the stack height in the `Reference` must be incremented because a stack frame is added.

```k
  syntax KItem ::= #setUpCalleeData(MonoItemKind, Operands)

  // reserve space for local variables and copy/move arguments from old locals into their place
  rule <k> #setUpCalleeData(
              monoItemFn(_, _, someBody(body((FIRST:BasicBlock _) #as BLOCKS, NEWLOCALS, _, _, _, _))),
              ARGS
              )
         =>
           #setArgsFromStack(1, ARGS) ~> #execBlock(FIRST)
         ...
       </k>
       //<currentFunc> CALLEE </currentFunc>
       <currentFrame>
         <currentBody> _ => toKList(BLOCKS) </currentBody>
        //  <caller> CALLER </caller>
        //  <dest> DEST </dest>
        //  <target> TARGET </target>
        //  <unwind> UNWIND </unwind>
         <locals> _ => #reserveFor(NEWLOCALS) </locals>
         // assumption: arguments stored as _1 .. _n before actual "local" data
         ...
       </currentFrame>
  // TODO: Haven't handled "noBody" case

  syntax KItem ::= #setArgsFromStack ( Int, Operands)
                 | #setArgFromStack ( Int, Operand)

  // once all arguments have been retrieved, execute
  rule <k> #setArgsFromStack(_, .Operands) ~> CONT => CONT </k>

  // set arguments one by one, marking off moved operands in the provided (caller) LOCALS
  rule <k> #setArgsFromStack(IDX, OP:Operand MORE:Operands) ~> CONT
        =>
           #setArgFromStack(IDX, OP) ~> #setArgsFromStack(IDX +Int 1, MORE) ~> CONT
       </k>

  rule <k> #setArgFromStack(IDX, operandConstant(_) #as CONSTOPERAND)
        =>
           #readOperand(CONSTOPERAND) ~> #setLocalValue(place(local(IDX), .ProjectionElems))
        ...
       </k>

  rule <k> #setArgFromStack(IDX, operandCopy(place(local(I), .ProjectionElems)))
        =>
           #incrementRef({CALLERLOCALS[I]}:>TypedLocal) ~> #setLocalValue(place(local(IDX), .ProjectionElems))
        ...
       </k>
       <stack> ListItem(StackFrame(_, _, _, _, CALLERLOCALS)) _:List </stack>
    requires 0 <=Int I
     andBool I <Int size(CALLERLOCALS)
     andBool isTypedLocal(CALLERLOCALS[I])
     andBool CALLERLOCALS[I] =/=K Moved
    [preserves-definedness] // valid list indexing checked

  rule <k> #setArgFromStack(IDX, operandMove(place(local(I), .ProjectionElems)))
        =>
           #incrementRef({CALLERLOCALS[I]}:>TypedLocal) ~> #setLocalValue(place(local(IDX), .ProjectionElems))
        ...
       </k>
       <stack> ListItem(StackFrame(_, _, _, _, CALLERLOCALS => CALLERLOCALS[I <- Moved])) _:List
        </stack>
    requires 0 <=Int I
     andBool I <Int size(CALLERLOCALS)
     andBool isTypedLocal(CALLERLOCALS[I])
     andBool CALLERLOCALS[I] =/=K Moved
    [preserves-definedness] // valid list indexing checked
```
The `Assert` terminator checks that an operand holding a boolean value (which has previously been computed, e.g., an overflow flag for arithmetic operations) has the expected value (e.g., that this overflow flag is `false` - a very common case).
If the condition value is as expected, the program proceeds with the given `target` block.
Otherwise the provided message is passed to a `panic!` call, ending the program with an error, modelled as an `#AssertError` in the semantics.

```k
  syntax KItem ::= #AssertError ( AssertMessage )

  rule <k> #execTerminator(terminator(assert(COND, EXPECTED, MSG, TARGET, _UNWIND), _SPAN)) ~> _CONT
         =>
           #readOperand(COND) ~> #expect(EXPECTED, MSG) ~> #execBlockIdx(TARGET)
       </k>

  syntax KItem ::= #expect ( Bool, AssertMessage )

  rule <k> typedLocal(BoolVal(COND), _, _) ~> #expect(EXPECTED, _MSG) => .K ... </k>
    requires COND ==Bool EXPECTED

  rule <k> typedLocal(BoolVal(COND), _, _) ~> #expect(EXPECTED, MSG) => #AssertError(MSG) ... </k>
    requires COND =/=Bool EXPECTED
```

```k
endmodule
```

## Top-level Module

The top-level module `KMIR` includes both the control flow constructs (and transitively all modules related to runtime operations and AST) and a collection of simplification lemmas required for symbolic execution of MIR programs.

```k
module KMIR
  imports KMIR-CONTROL-FLOW
  imports KMIR-LEMMAS

endmodule
