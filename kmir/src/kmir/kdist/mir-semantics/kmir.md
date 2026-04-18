# MIR Semantics in K

```k
requires "kmir-ast.md"
requires "rt/data.md"
requires "rt/configuration.md"
requires "lemmas/kmir-lemmas.md"
requires "cheatcodes.md"
requires "intrinsics.md"
```

## Syntax of MIR in K

The MIR syntax is largely defined in [KMIR-AST](./kmir-ast.md) and its
submodules. The execution is initialised based on a loaded `Pgm` read
from a json format of stable-MIR, and the name of the function to execute.

## (Dynamic) Semantics

### Execution Configuration

The _configuration_ that this MIR semantics operates on carries the entire state of the running program, including local variables of the current function item, the whole call stack, as well as all code items that may potentially be executed.

See [`rt/configuration.md`](./rt/configuration.md) for a detailed description of the configuration.

### Execution Control Flow

```k
module KMIR-CONTROL-FLOW
  imports BOOL
  imports COLLECTIONS
  imports LIST
  imports MAP
  imports STRING
  imports K-EQUAL

  imports MONO
  imports TYPES

  imports KMIR-CONFIGURATION
  imports RT-DATA
```

Execution of a program begins by creating a stack frame for the `main`
function and executing its function body. Before execution begins, the
function map and the initial memory have to be set up.

All of this is done in the client code so we omit the initialisation code which was historically placed here.


#### Function Execution


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
  rule [execStmt]: <k> #execStmt(statement(statementKindAssign(place(local(I), _PROJ) #as PLACE, RVAL), _SPAN))
         =>
            #setLocalValue(PLACE, RVAL)
         ...
       </k>
       <locals> LOCALS </locals>
       <slotStore> ... #frameSlotId(LOCALS, I) |-> LOCAL:TypedLocal ... </slotStore>
       requires 0 <=Int I andBool I <Int size(LOCALS)
        andBool notBool #isUnionType(lookupTy(tyOfLocal(LOCAL)))
       [preserves-definedness]

  rule [execStmt.union]: <k> #execStmt(statement(statementKindAssign(place(local(I), _PROJ) #as PLACE, RVAL), _SPAN))
         =>
            #setLocalValue(PLACE, #evalUnion(RVAL))
         ...
       </k>
       <locals> LOCALS </locals>
       <slotStore> ... #frameSlotId(LOCALS, I) |-> LOCAL:TypedLocal ... </slotStore>
       requires 0 <=Int I andBool I <Int size(LOCALS)
        andBool #isUnionType(lookupTy(tyOfLocal(LOCAL)))
       [preserves-definedness]

  // RVAL evaluation is implemented in rt/data.md

  rule <k> #execStmt(statement(statementKindSetDiscriminant(_PLACE, _VARIDX), _SPAN))
         =>
           .K // write variant discriminator for given index to PLACE
         ...
       </k>

  // Fallback: other non-diverging intrinsics are currently no-ops
  rule <k> #execStmt(statement(statementKindIntrinsic(_INTRINSIC), _SPAN))
         =>
           .K // effect of calling INTRINSIC
         ...
       </k> [owise]

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
  rule [termGoto]: <k> #execTerminator(terminator(terminatorKindGoto(I), _SPAN)) ~> _CONT
         =>
           #execBlockIdx(I)
       </k>
```

A `SwitchInt` terminator selects one of the blocks given as _targets_,
depending on the value of a _discriminant_. If the discriminant is an
an integer, it is always interpretted as the _unsigned_ value (even if
negative). E.g. if branching is occuring on `-127_i8`, the discriminant
will be `129`.

```k
  syntax KItem ::= #selectBlock ( SwitchTargets , Evaluation ) [strict(2)]

  rule [termSwitchInt]: <k> #execTerminator(terminator(terminatorKindSwitchInt(DISCR, TARGETS), _SPAN)) ~> _CONT
         =>
           #selectBlock(TARGETS, DISCR)
       </k>

  // These rules preserve definedness because all the same subterms show up on each side except:
  // - `branch(...)`, which is a constructor.
  // - `#switchMatch(...)`, which is a total function, but can't be marked total because the LLVM backend complains.

  rule <k> #selectBlock(switchTargets(.Branches, BBIDX), _) => #execBlockIdx(BBIDX) ... </k>

  rule <k> #selectBlock(switchTargets(branch(MI, BBIDX) _, _), V) => #execBlockIdx(BBIDX) ... </k>
    requires #switchMatch(MI, V)
     andBool #switchCanUse(V)
    [preserves-definedness]

  rule <k> #selectBlock(switchTargets(branch(MI, _) BRANCHES => BRANCHES, _), V) ... </k>
    requires notBool #switchMatch(MI, V)
     andBool #switchCanUse(V)
    [preserves-definedness]

  syntax Bool ::= #switchMatch   ( MIRInt , Value ) [function]

  rule #switchMatch(0, BoolVal(B)           ) => notBool B
  rule #switchMatch(1, BoolVal(B)           ) => B
  rule #switchMatch(I, Integer(I2, WIDTH, _)) => I ==Int truncate(I2, WIDTH, Unsigned) requires 0 <Int WIDTH
  rule #switchMatch(I, Integer(I2,   0  , _)) => I ==Int I2

  syntax Bool ::= #switchCanUse ( Value ) [function, total]
  // ------------------------------------------------------
  rule #switchCanUse(Integer(_, _, _)) => true
  rule #switchCanUse(  BoolVal( _ )  ) => true
  rule #switchCanUse(   thunk( _ )   ) => true
  rule #switchCanUse(   _OTHER       ) => false [owise]
```

`Return` simply returns from a function call, using the information
stored in the top stack frame to pass the returned value. The return
value is the value in local `_0`, and will go to the _destination_ in
the `LOCALS` of the caller's stack frame. Execution continues with the
context of the enclosing stack frame, at the _target_.

If the local `_0` does not have a value (i.e., it remained uninitialised), the function returns unit and writing the value is skipped.

```k
  syntax KItem ::= #dropSlots(List)

  rule <k> #dropSlots(SLOTS) => .K ... </k>
       <slotStore> STORE => removeAll(STORE, List2Set(SLOTS)) </slotStore>

  rule [termReturnSome]: <k> #execTerminator(terminator(terminatorKindReturn, _SPAN)) ~> _
         =>
           #setLocalValue(DEST, VAL) ~> #dropSlots(LOCALS) ~> #execBlockIdx(TARGET)
       </k>
       <currentFunc> _ => CALLER </currentFunc>
       //<currentFrame>
         <currentBody> _ => #getBlocks(CALLER) </currentBody>
         <caller> CALLER => NEWCALLER </caller>
         <dest> DEST => NEWDEST </dest>
         <target> someBasicBlockIdx(TARGET) => NEWTARGET </target>
         <unwind> _ => UNWIND </unwind>
         <locals> LOCALS => NEWLOCALS </locals>
       //</currentFrame>
       <slotStore> ... #frameSlotId(LOCALS, 0) |-> typedValue(VAL:Value, _, _) ... </slotStore>
       // remaining call stack (without top frame)
       <stack> ListItem(StackFrame(NEWCALLER, NEWDEST, NEWTARGET, UNWIND, NEWLOCALS)) STACK => STACK </stack>

  // no value to return, skip writing
  rule [termReturnNone]: <k> #execTerminator(terminator(terminatorKindReturn, _SPAN)) ~> _
         =>
           #dropSlots(LOCALS) ~> #execBlockIdx(TARGET)
       </k>
       <currentFunc> _ => CALLER </currentFunc>
       //<currentFrame>
         <currentBody> _ => #getBlocks(CALLER) </currentBody>
         <caller> CALLER => NEWCALLER </caller>
         <dest> _ => NEWDEST </dest>
         <target> someBasicBlockIdx(TARGET) => NEWTARGET </target>
         <unwind> _ => UNWIND </unwind>
         <locals> LOCALS => NEWLOCALS </locals>
       //</currentFrame>
       <slotStore> ... #frameSlotId(LOCALS, 0) |-> newLocal(_, _) ... </slotStore>
       // remaining call stack (without top frame)
       <stack> ListItem(StackFrame(NEWCALLER, NEWDEST, NEWTARGET, UNWIND, NEWLOCALS)) STACK => STACK </stack>

  syntax List ::= #getBlocks( Ty )               [function, total]
                | #getBlocksAux( MonoItemKind )  [function, total]

  rule #getBlocks(TY) => #getBlocksAux(lookupFunction(TY))

  // returns blocks from the body
  rule #getBlocksAux(monoItemFn(_, _, noBody)) => .List
  rule #getBlocksAux(monoItemFn(_, _, someBody(body(BLOCKS, _, _, _, _, _)))) => toKList(BLOCKS)
  // other item kinds are not expected or supported
  rule #getBlocksAux(monoItemStatic(_, _, _)) => .List // should not occur in calls
  rule #getBlocksAux(monoItemGlobalAsm(_)) => .List // not supported
  rule #getBlocksAux(IntrinsicFunction(_)) => .List // intrinsics have no body

  syntax List ::= toKList(BasicBlocks) [function, total]
  // ---------------------------------------------------
  rule toKList( .BasicBlocks )                => .List
  rule toKList(B:BasicBlock REST:BasicBlocks) => ListItem(B) toKList(REST)
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
         <locals> LOCALS </locals>
         ...
       </currentFrame>
       <slotStore> ... #frameSlotId(LOCALS, 0) |-> typedValue(VAL:Value, _, _) ... </slotStore>

  rule [endprogram-no-return]:
       <k> #execTerminator(terminator(terminatorKindReturn, _SPAN)) ~> _
         =>
           #EndProgram
       </k>
       <currentFrame>
         <target> noBasicBlockIdx </target>
         <locals> LOCALS </locals>
         ...
       </currentFrame>
       <slotStore> ... #frameSlotId(LOCALS, 0) |-> newLocal(_, _) ... </slotStore>
```


`Call` is calling another function, setting up its stack frame and
where the returned result should go.

```k
  syntax KItem ::= #execTerminatorCall(fty: Ty, func: MonoItemKind, args: Operands, destination: Place, target: MaybeBasicBlockIdx, unwind: UnwindAction, Span)

  rule <k> #execTerminator(terminator(terminatorKindCall(operandConstant(constOperand(_, _, mirConst(constantKindZeroSized, Ty, _))), ARGS, DEST, TARGET, UNWIND), SPAN))
        => #execTerminatorCall(Ty, lookupFunction(Ty), ARGS, DEST, TARGET, UNWIND, SPAN)
        ...
       </k>

  rule <k> #execTerminator(terminator(terminatorKindCall(operandMove(place(local(I), PROJS)), ARGS, DEST, TARGET, UNWIND), SPAN))
        => #execTerminatorCall({getTyOf(tyOfLocal(LOCAL), PROJS)}:>Ty, lookupFunction({getTyOf(tyOfLocal(LOCAL), PROJS)}:>Ty), ARGS, DEST, TARGET, UNWIND, SPAN)
        ...
       </k>
      <locals> LOCALS </locals>
      <slotStore> ... #frameSlotId(LOCALS, I) |-> LOCAL:TypedLocal ... </slotStore>
    requires 0 <=Int I andBool I <Int size(LOCALS)
     andBool isTy(getTyOf(tyOfLocal(LOCAL), PROJS))
    [preserves-definedness] // valid local indexing checked, projected call target must resolve to a Ty

  // Intrinsic function call - execute directly without state switching
  rule [termCallIntrinsic]:
        <k> #execTerminatorCall(_, FUNC, ARGS, DEST, TARGET, _UNWIND, SPAN) ~> _
         => #execIntrinsic(FUNC, ARGS, DEST, SPAN) ~> #continueAt(TARGET)
        </k>
    requires isIntrinsicFunction(FUNC)
     andBool notBool #functionNameMatchesEnv(getFunctionName(FUNC))

  // Intrinsic function call to a function in the break-on set - same as termCallIntrinsic but separate rule id for cut-point
  rule [termCallIntrinsicFilter]:
        <k> #execTerminatorCall(_, FUNC, ARGS, DEST, TARGET, _UNWIND, SPAN) ~> _
         => #execIntrinsic(FUNC, ARGS, DEST, SPAN) ~> #continueAt(TARGET)
        </k>
    requires isIntrinsicFunction(FUNC)
     andBool #functionNameMatchesEnv(getFunctionName(FUNC))

  // Regular function call - state switch into the callee and defer argument materialization.
  rule [termCallFunction]:
       <k> #execTerminatorCall(
             FTY,
             monoItemFn(_, _, someBody(body((FIRST:BasicBlock _) #as BLOCKS, NEWLOCALS, _, _, _, _))) #as FUNC,
             ARGS,
             DEST,
             TARGET,
             UNWIND,
             _SPAN
           ) ~> _
        => #loadCallArgs(FUNC, ARGS) ~> #execBlock(FIRST)
       </k>
       <currentFunc> CALLER => FTY </currentFunc>
       <nextSlot> NEXT:Int => #reserveNextSlot(NEXT, NEWLOCALS) </nextSlot>
       <slotStore> STORE => #reserveSlotStore(STORE, NEXT, NEWLOCALS) </slotStore>
       <currentFrame>
         <currentBody> _ => toKList(BLOCKS) </currentBody>
         <caller> OLDCALLER => CALLER </caller>
         <dest> OLDDEST => DEST </dest>
         <target> OLDTARGET => TARGET </target>
         <unwind> OLDUNWIND => UNWIND </unwind>
         <locals> LOCALS => #reserveLocals(NEXT, NEWLOCALS) </locals>
       </currentFrame>
       <stack> STACK => ListItem(StackFrame(OLDCALLER, OLDDEST, OLDTARGET, OLDUNWIND, LOCALS)) STACK </stack>
    requires notBool isIntrinsicFunction(FUNC)
     andBool notBool #functionNameMatchesEnv(getFunctionName(FUNC))

  // Same as termCallFunction but separate rule id for cut-point filtering.
  rule [termCallFunctionFilter]:
       <k> #execTerminatorCall(
             FTY,
             monoItemFn(_, _, someBody(body((FIRST:BasicBlock _) #as BLOCKS, NEWLOCALS, _, _, _, _))) #as FUNC,
             ARGS,
             DEST,
             TARGET,
             UNWIND,
             _SPAN
           ) ~> _
        => #loadCallArgs(FUNC, ARGS) ~> #execBlock(FIRST)
       </k>
       <currentFunc> CALLER => FTY </currentFunc>
       <nextSlot> NEXT:Int => #reserveNextSlot(NEXT, NEWLOCALS) </nextSlot>
       <slotStore> STORE => #reserveSlotStore(STORE, NEXT, NEWLOCALS) </slotStore>
       <currentFrame>
         <currentBody> _ => toKList(BLOCKS) </currentBody>
         <caller> OLDCALLER => CALLER </caller>
         <dest> OLDDEST => DEST </dest>
         <target> OLDTARGET => TARGET </target>
         <unwind> OLDUNWIND => UNWIND </unwind>
         <locals> LOCALS => #reserveLocals(NEXT, NEWLOCALS) </locals>
       </currentFrame>
       <stack> STACK => ListItem(StackFrame(OLDCALLER, OLDDEST, OLDTARGET, OLDUNWIND, LOCALS)) STACK </stack>
    requires notBool isIntrinsicFunction(FUNC)
     andBool #functionNameMatchesEnv(getFunctionName(FUNC))

  syntax Bool ::= isIntrinsicFunction(MonoItemKind) [function]
  rule isIntrinsicFunction(IntrinsicFunction(_)) => true
  rule isIntrinsicFunction(_) => false [owise]

  syntax String ::= getFunctionName(MonoItemKind) [function, total]
  //---------------------------------------------------------------
  rule getFunctionName(monoItemFn(symbol(NAME), _, _)) => NAME
  rule getFunctionName(monoItemStatic(symbol(NAME), _, _)) => NAME
  rule getFunctionName(monoItemGlobalAsm(_)) => ""
  rule getFunctionName(IntrinsicFunction(symbol(NAME))) => NAME

  // Check whether a function name matches any filter in the break-on-functions list.
  syntax Bool ::= #functionNameMatchesEnv(String) [function, total]
  //----------------------------------------------------------------
  rule #functionNameMatchesEnv(NAME) => #functionNameMatchesEnvStr(NAME, #breakOnFunctionsString(0))

  // The Int argument is unused; it exists only so the Haskell backend can
  // pattern-match on it and not error since zero-argument functions cannot use [owise].
  syntax String ::= #breakOnFunctionsString(Int) [function, total, symbol(breakOnFunctionsString)]
  //-----------------------------------------------------------------------------------------------
  rule #breakOnFunctionsString(_) => "" [owise] // This gets overridden by corresponding python function

  syntax Bool ::= #functionNameMatchesEnvStr(String, String) [function, total]
  //--------------------------------------------------------------------------
  rule #functionNameMatchesEnvStr(_, "") => false
  rule #functionNameMatchesEnvStr(NAME, ENV) => #functionNameMatchesAnyList(NAME, #splitSemicolon(ENV))
    requires ENV =/=String ""

  syntax List ::= #splitSemicolon(String) [function, total]
  //--------------------------------------------------------
  rule #splitSemicolon(S) => #splitSemicolonAux(S, findString(S, ";", 0))

  syntax List ::= #splitSemicolonAux(String, Int) [function, total]
  //-----------------------------------------------------------------
  rule #splitSemicolonAux(S, -1) => ListItem(S)
  rule #splitSemicolonAux(S, I) =>
      ListItem(substrString(S, 0, I)) #splitSemicolon(substrString(S, I +Int 1, lengthString(S)))
    requires I >=Int 0

  syntax Bool ::= #functionNameMatchesAnyList(String, List) [function, total]
  //-------------------------------------------------------------------------
  rule #functionNameMatchesAnyList(_, .List) => false
  rule #functionNameMatchesAnyList(NAME, ListItem(FILTER:String) REST) =>
      0 <=Int findString(NAME, FILTER, 0) orBool #functionNameMatchesAnyList(NAME, REST)
  rule #functionNameMatchesAnyList(_, _) => false [owise]

  syntax KItem ::= #continueAt(MaybeBasicBlockIdx)
  rule <k> #continueAt(someBasicBlockIdx(TARGET)) => #execBlockIdx(TARGET) ... </k>
  rule <k> #continueAt(noBasicBlockIdx) => .K ... </k>
```

After entering the callee, argument materialization is performed separately.
Arguments refer to the caller's runtime slots on the stack, while the current frame already contains the reserved callee locals.

```k
  syntax Int ::= #reserveNextSlot(Int, LocalDecls) [function, total]
  syntax List ::= #reserveLocals(Int, LocalDecls) [function, total]
  syntax Map ::= #reserveSlotStore(Map, Int, LocalDecls) [function, total]

  rule #reserveNextSlot(NEXT, .LocalDecls) => NEXT
  rule #reserveNextSlot(NEXT, localDecl(_, _, _) REST:LocalDecls) => #reserveNextSlot(NEXT +Int 1, REST)

  rule #reserveLocals(_, .LocalDecls) => .List
  rule #reserveLocals(NEXT, localDecl(_, _, _) REST:LocalDecls) => ListItem(NEXT) #reserveLocals(NEXT +Int 1, REST)

  rule #reserveSlotStore(STORE, _, .LocalDecls) => STORE
  rule #reserveSlotStore(STORE, NEXT, localDecl(TY, _, MUT) REST:LocalDecls)
    => #reserveSlotStore(STORE[NEXT <- newLocal(TY, MUT)], NEXT +Int 1, REST)

  syntax KItem ::= #loadCallArgs(MonoItemKind, Operands)
                 | #setArgsFromStack ( Int, Operands)
                 | #setArgFromStack ( Int, Operand)
                 | #execIntrinsic ( MonoItemKind, Operands, Place, Span )

  rule <k> #loadCallArgs(
              monoItemFn(_, _, someBody(body(_, _, _, _, _, _))),
              operandMove(place(local(CLOSURE:Int), .ProjectionElems))
              operandMove(place(local(TUPLE), .ProjectionElems))
              .Operands
            )
        => #setTupleArgs(2, TUPLEVAL)
        ...
       </k>
       <stack> ListItem(StackFrame(_, _, _, _, CALLERLOCALS)) _:List </stack>
       <slotStore>
         ... #frameSlotId(CALLERLOCALS, TUPLE) |-> (typedValue(TUPLEVAL:Value, TUPLETY:Ty, _) => typedValue(Moved, TUPLETY, mutabilityMut))
             #frameSlotId(CALLERLOCALS, CLOSURE) |-> (CLOSURELOCAL:TypedLocal => typedValue(Moved, tyOfLocal(CLOSURELOCAL), mutabilityMut)) ...
       </slotStore>
    requires 0 <=Int CLOSURE andBool CLOSURE <Int size(CALLERLOCALS)
     andBool 0 <=Int TUPLE andBool TUPLE <Int size(CALLERLOCALS)
     andBool isTupleType(lookupTy(TUPLETY))
     andBool isTypedLocal(CLOSURELOCAL)
     andBool (
               typeInfoVoidType ==K lookupTy(tyOfLocal(CLOSURELOCAL))
               orBool isFunType(lookupTy(tyOfLocal(CLOSURELOCAL)))
             )
    [priority(40), preserves-definedness]

  rule <k> #loadCallArgs(
              monoItemFn(_, _, someBody(body(_, _, _, _, _, _))),
              operandMove(place(local(CLOSURE:Int), .ProjectionElems))
              operandMove(place(local(TUPLE), .ProjectionElems))
              .Operands
            )
        => #setLocalValue(place(local(1), .ProjectionElems), CLOSUREVAL) ~> #setTupleArgs(2, TUPLEVAL)
        ...
       </k>
       <stack> ListItem(StackFrame(_, _, _, _, CALLERLOCALS)) _:List </stack>
       <slotStore>
         ... #frameSlotId(CALLERLOCALS, TUPLE) |-> (typedValue(TUPLEVAL:Value, TUPLETY:Ty, _) => typedValue(Moved, TUPLETY, mutabilityMut))
             #frameSlotId(CALLERLOCALS, CLOSURE) |-> (typedValue(CLOSUREVAL:Value, CLOSURETY:Ty, _) => typedValue(Moved, CLOSURETY, mutabilityMut)) ...
       </slotStore>
    requires 0 <=Int CLOSURE andBool CLOSURE <Int size(CALLERLOCALS)
     andBool 0 <=Int TUPLE andBool TUPLE <Int size(CALLERLOCALS)
     andBool isTupleType(lookupTy(TUPLETY))
     andBool isRefType(lookupTy(CLOSURETY))
     andBool isTy(pointeeTy(lookupTy(CLOSURETY)))
     andBool (
               lookupTy({pointeeTy(lookupTy(CLOSURETY))}:>Ty) ==K typeInfoVoidType
               orBool isFunType(lookupTy({pointeeTy(lookupTy(CLOSURETY))}:>Ty))
             )
    [priority(45), preserves-definedness]

  rule <k> #loadCallArgs(_FUNC, ARGS) => #setArgsFromStack(1, ARGS) ... </k> [owise]

  // once all arguments have been retrieved, execute
  rule <k> #setArgsFromStack(_, .Operands) ~> CONT => CONT </k>

  // set arguments one by one, marking off moved operands in the provided (caller) LOCALS
  rule <k> #setArgsFromStack(IDX, OP:Operand MORE:Operands) ~> CONT
        =>
           #setArgFromStack(IDX, OP) ~> #setArgsFromStack(IDX +Int 1, MORE) ~> CONT
       </k>

  rule <k> #setArgFromStack(IDX, operandConstant(_) #as CONSTOPERAND)
        =>
           #setLocalValue(place(local(IDX), .ProjectionElems), CONSTOPERAND)
        ...
       </k>

  rule <k> #setArgFromStack(IDX, operandCopy(place(local(I), .ProjectionElems)))
        =>
           #setLocalValue(place(local(IDX), .ProjectionElems), VAL)
        ...
       </k>
       <stack> ListItem(StackFrame(_, _, _, _, CALLERLOCALS)) _:List </stack>
       <slotStore> ... #frameSlotId(CALLERLOCALS, I) |-> typedValue(VAL:Value, _, _) ... </slotStore>
    requires 0 <=Int I
     andBool I <Int size(CALLERLOCALS)
    [preserves-definedness] // valid list indexing checked

  // TODO: This is not safe, need to add more checks to this.
  rule <k> #setArgFromStack(IDX, operandMove(place(local(I), _)))
        =>
           #setLocalValue(place(local(IDX), .ProjectionElems), VAL)
        ...
       </k>
       <stack> ListItem(StackFrame(_, _, _, _, CALLERLOCALS)) _:List </stack>
       <slotStore>
         ... #frameSlotId(CALLERLOCALS, I) |-> (typedValue(VAL:Value, TY:Ty, _)
           => typedValue(Moved, TY, mutabilityMut)) ...
       </slotStore>
    requires 0 <=Int I
     andBool I <Int size(CALLERLOCALS)
    [preserves-definedness] // valid list indexing checked
```

For closures (like `|x,y| { things using x and y }`), a special calling convention is in effect:
The first argument of the closure is its environment.
Its type is currently not extracted (KMIR does not currently support variable-capturing) and it is not initialised.
The second argument is a _tuple_ of all the arguments, however the function body expects these arguments as single locals.

Using this calling convention should be indicated by the `spread_arg` field in the function body.[^spread_arg]
However, this field is usually `None` for _closures_, it is only set for internal functions of the Rust execution mechanism.
Therefore a heuristics is used here:
* The function has two arguments,
* the 1st argument has an unknown type (or refers to one),
* and the 2nd argument is a tuple.

[^spread_arg]: https://doc.rust-lang.org/beta/nightly-rustc/rustc_public/mir/body/struct.Body.html#structfield.spread_arg

```k
  syntax Bool ::= isTupleType ( TypeInfo ) [function, total]
                | isRefType ( TypeInfo ) [function, total]
                | isFunType ( TypeInfo ) [function, total]
  // -------------------------------------------------------
  rule isTupleType(typeInfoTupleType(_, _)) => true
  rule isTupleType(    _                  ) => false [owise]
  rule isRefType(typeInfoRefType(_)) => true
  rule isRefType(    _             ) => false [owise]
  rule isFunType(typeInfoFunType(_)) => true
  rule isFunType(    _             ) => false [owise]

  syntax KItem ::= #setTupleArgs ( Int , Value )
                 | #setTupleArgs ( Int , List )

  // unpack tuple and set arguments individually
  rule <k> #setTupleArgs(IDX, Aggregate(variantIdx(0), ARGS)) => #setTupleArgs(IDX, ARGS) ... </k>

  rule <k> #setTupleArgs(IDX, VAL:Value)
        => #setTupleArgs(IDX, ListItem(VAL))
        ...
       </k> [owise]

  rule <k> #setTupleArgs(_, .List ) => .K ... </k>

  rule <k> #setTupleArgs(IDX, ListItem(VAL) REST:List)
        => #setLocalValue(place(local(IDX), .ProjectionElems), VAL) ~> #setTupleArgs(IDX +Int 1, REST)
        ...
       </k>
```


#### Assert

The `Assert` terminator checks that an operand holding a boolean value (which has previously been computed, e.g., an overflow flag for arithmetic operations) has the expected value (e.g., that this overflow flag is `false` - a very common case).
If the condition value is as expected, the program proceeds with the given `target` block.
Otherwise the provided message is passed to a `panic!` call, ending the program with an error, modelled as an `AssertError` in the semantics.

```k
  syntax MIRError ::= AssertError ( AssertMessage )

  rule [termAssert]: <k> #execTerminator(terminator(assert(COND, EXPECTED, MSG, TARGET, _UNWIND), _SPAN)) ~> _CONT
         =>
           #expect(COND, EXPECTED, MSG) ~> #execBlockIdx(TARGET)
       </k>

  syntax KItem ::= #expect ( Evaluation, Bool, AssertMessage ) [strict(1)]

  rule <k> #expect(BoolVal(COND), EXPECTED, _MSG) => .K ... </k>
    requires COND ==Bool EXPECTED

  rule <k> #expect(BoolVal(COND), EXPECTED, MSG) => AssertError(MSG) ... </k>
    requires COND =/=Bool EXPECTED
```
If the specific assertion rules above for `#expect` are matched, then we definitely know that there is or is not an assertion failure (respective to the matched rule).
However if a `thunk` wrapper exists inside an `#expect` we want to non-deterministically explore both branches.
This does not sacrifice unsoundness as we would not eliminate any assertion failures with `thunk`, but instead will create unnecessary ones in the cases the `thunk(#expect(...))` would evaluate to true.

```k
  rule <k> #expect(thunk(_), _, _MSG) => .K ... </k>

  rule <k> #expect(thunk(_), _, MSG) => AssertError(MSG) ... </k>
```

Other terminators that matter at the MIR level "Runtime" are `Drop` and `Unreachable`.
Drops are elaborated to Noops but still define the continuing control flow. Unreachable terminators lead to a program error.

```k
  rule [termDrop]: <k> #execTerminator(terminator(terminatorKindDrop(_PLACE, TARGET, _UNWIND), _SPAN))
         =>
           #execBlockIdx(TARGET)
        ...
       </k>

  syntax MIRError ::= "ReachedUnreachable"

  rule [termUnreachable]: <k> #execTerminator(terminator(terminatorKindUnreachable, _SPAN))
         =>
           ReachedUnreachable
        ...
       </k>
```

### Stopping on Program Errors

The semantics has a dedicated error sort to stop execution when flawed input or undefined behaviour is detected.
This includes cases of invalid MIR (e.g., accessing non-existing locals in a block or jumping to non-existing blocks), mutation of immutable values, or accessing uninitialised locals, but also user errors such as division by zero or overflowing unchecked arithmetic operations.

The execution will stop with the respective error information as soon as an error condition is detected.

```k
  syntax KItem ::= #ProgramError ( MIRError )

  rule [program-error]:
    <k> ERR:MIRError => #ProgramError(ERR) ...</k>
```

```k
endmodule
```

## Top-level Module

The top-level module `KMIR` includes both the control flow constructs (and transitively all modules related to runtime operations and AST) and a collection of simplification lemmas required for symbolic execution of MIR programs.

```k
module KMIR
  imports KMIR-AST // Necessary for the external Python parser
  imports KMIR-CONTROL-FLOW
  imports KMIR-CHEATCODES
  imports KMIR-INTRINSICS
  imports KMIR-LEMMAS
endmodule
