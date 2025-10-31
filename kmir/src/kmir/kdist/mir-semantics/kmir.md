# MIR Semantics in K

```k
requires "kmir-ast.md"
requires "rt/data.md"
requires "rt/configuration.md"
requires "lemmas/kmir-lemmas.md"
requires "cheatcodes.md"

requires "symbolic/p-token.md"
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
  imports LIST
  imports MAP
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
  rule [execStmt]: <k> #execStmt(statement(statementKindAssign(PLACE, RVAL), _SPAN))
         =>
            #setLocalValue(PLACE, RVAL)
         ...
       </k>

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

  rule <k> #selectBlock(switchTargets(branch(MI, BBIDX) _, _), V) => #execBlockIdx(BBIDX) ... </k> requires #switchMatch(MI, V) [preserves-definedness]

  rule <k> #selectBlock(switchTargets(branch(MI, _) BRANCHES => BRANCHES, _), V) ... </k> requires notBool #switchMatch(MI, V) [preserves-definedness]

  syntax Bool ::= #switchMatch   ( MIRInt , Value ) [function]

  rule #switchMatch(0, BoolVal(B)           ) => notBool B
  rule #switchMatch(1, BoolVal(B)           ) => B
  rule #switchMatch(I, Integer(I2, WIDTH, _)) => I ==Int truncate(I2, WIDTH, Unsigned)
```

`Return` simply returns from a function call, using the information
stored in the top stack frame to pass the returned value. The return
value is the value in local `_0`, and will go to the _destination_ in
the `LOCALS` of the caller's stack frame. Execution continues with the
context of the enclosing stack frame, at the _target_.

If the returned value is a `Reference`, its stack height must be decremented because a stack frame is popped.
NB that a stack height of `0` cannot occur here, because the compiler prevents local variable references from escaping.

If the local `_0` does not have a value (i.e., it remained uninitialised), the function returns unit and writing the value is skipped.

```k
  rule [termReturnSome]: <k> #execTerminator(terminator(terminatorKindReturn, _SPAN)) ~> _
         =>
           #setLocalValue(DEST, #decrementRef(VAL)) ~> #execBlockIdx(TARGET)
       </k>
       <currentFunc> _ => CALLER </currentFunc>
       //<currentFrame>
         <currentBody> _ => #getBlocks(CALLER) </currentBody>
         <caller> CALLER => NEWCALLER </caller>
         <dest> DEST => NEWDEST </dest>
         <target> someBasicBlockIdx(TARGET) => NEWTARGET </target>
         <unwind> _ => UNWIND </unwind>
         <locals> ListItem(typedValue(VAL:Value, _, _)) _ => NEWLOCALS </locals>
       //</currentFrame>
       // remaining call stack (without top frame)
       <stack> ListItem(StackFrame(NEWCALLER, NEWDEST, NEWTARGET, UNWIND, NEWLOCALS)) STACK => STACK </stack>

  // no value to return, skip writing
  rule [termReturnNone]: <k> #execTerminator(terminator(terminatorKindReturn, _SPAN)) ~> _
         =>
           #execBlockIdx(TARGET)
       </k>
       <currentFunc> _ => CALLER </currentFunc>
       //<currentFrame>
         <currentBody> _ => #getBlocks(CALLER) </currentBody>
         <caller> CALLER => NEWCALLER </caller>
         <dest> _ => NEWDEST </dest>
         <target> someBasicBlockIdx(TARGET) => NEWTARGET </target>
         <unwind> _ => UNWIND </unwind>
         <locals> ListItem(_:NewLocal) _ => NEWLOCALS </locals>
       //</currentFrame>
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
         <locals> ListItem(typedValue(VAL, _, _)) ... </locals>
         ...
       </currentFrame>

  rule [endprogram-no-return]:
       <k> #execTerminator(terminator(terminatorKindReturn, _SPAN)) ~> _
         =>
           #EndProgram
       </k>
       <currentFrame>
         <target> noBasicBlockIdx </target>
         <locals> ListItem(newLocal(_, _)) ... </locals>
         ...
       </currentFrame>
```


`Call` is calling another function, setting up its stack frame and
where the returned result should go.


```k
  // Intrinsic function call - execute directly without state switching
  rule [termCallIntrinsic]: <k> #execTerminator(terminator(terminatorKindCall(FUNC, ARGS, DEST, TARGET, _UNWIND), _SPAN)) ~> _
         =>
           #execIntrinsic(lookupFunction(#tyOfCall(FUNC)), ARGS, DEST) ~> #continueAt(TARGET)
       </k>
    requires isIntrinsicFunction(lookupFunction(#tyOfCall(FUNC)))

  // Regular function call - full state switching and stack setup
  rule [termCallFunction]: <k> #execTerminator(terminator(terminatorKindCall(FUNC, ARGS, DEST, TARGET, UNWIND), _SPAN)) ~> _
         =>
           #setUpCalleeData(lookupFunction(#tyOfCall(FUNC)), ARGS)
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
    requires notBool isIntrinsicFunction(lookupFunction(#tyOfCall(FUNC)))

  syntax Bool ::= isIntrinsicFunction(MonoItemKind) [function]
  rule isIntrinsicFunction(IntrinsicFunction(_)) => true
  rule isIntrinsicFunction(_) => false [owise]

  syntax KItem ::= #continueAt(MaybeBasicBlockIdx)
  rule <k> #continueAt(someBasicBlockIdx(TARGET)) => #execBlockIdx(TARGET) ... </k>
  rule <k> #continueAt(noBasicBlockIdx) => .K ... </k>

  syntax Ty ::= #tyOfCall( Operand ) [function, total]

  rule #tyOfCall(operandConstant(constOperand(_, _, mirConst(constantKindZeroSized, Ty, _)))) => Ty
  rule #tyOfCall(_) => ty(-1) [owise] // copy, move, non-zero size: not supported
```

The local data has to be set up for the call, which requires information about the local variables of a call. This step is separate from the above call stack setup because it needs to retrieve the locals declaration from the body. Arguments to the call are `Operands` which refer to the old locals (`OLDLOCALS` below), and the data is either _copied_ into the new locals using `#setArgs`, or it needs to be _shared_ via references.

An operand may be a `Reference` (the only way a function could access another function call's `local` variables). For this case, the stack height in the `Reference` must be incremented because a stack frame is added.

```k
  syntax KItem ::= #setUpCalleeData(MonoItemKind, Operands)

  // reserve space for local variables and copy/move arguments from old locals into their place
  rule [setupCalleeData]: <k> #setUpCalleeData(
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

  syntax List ::= #reserveFor( LocalDecls ) [function, total]

  rule #reserveFor(.LocalDecls) => .List

  rule #reserveFor(localDecl(TY, _, MUT) REST:LocalDecls)
      =>
       ListItem(newLocal(TY, MUT)) #reserveFor(REST)


  syntax KItem ::= #setArgsFromStack ( Int, Operands)
                 | #setArgFromStack ( Int, Operand)
                 | #execIntrinsic ( MonoItemKind, Operands, Place )

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
           #setLocalValue(place(local(IDX), .ProjectionElems), #incrementRef(getValue(CALLERLOCALS, I)))
        ...
       </k>
       <stack> ListItem(StackFrame(_, _, _, _, CALLERLOCALS)) _:List </stack>
    requires 0 <=Int I
     andBool I <Int size(CALLERLOCALS)
     andBool isTypedValue(CALLERLOCALS[I])
    [preserves-definedness] // valid list indexing checked

  rule <k> #setArgFromStack(IDX, operandMove(place(local(I), .ProjectionElems)))
        =>
           #setLocalValue(place(local(IDX), .ProjectionElems), #incrementRef(getValue(CALLERLOCALS, I)))
        ...
       </k>
       <stack> (ListItem(StackFrame(_, _, _, _, CALLERLOCALS) #as CALLERFRAME => #updateStackLocal(CALLERFRAME, I, Moved))) _:List
        </stack>
    requires 0 <=Int I
     andBool I <Int size(CALLERLOCALS)
     andBool isTypedValue(CALLERLOCALS[I])
    [preserves-definedness] // valid list indexing checked
```
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

### Intrinsic Functions

Intrinsic functions are built-in functions provided by the compiler that don't have regular MIR bodies.
They are handled specially in the execution semantics through the `#execIntrinsic` mechanism.
When an intrinsic function is called, the execution bypasses the normal function call setup and directly
executes the intrinsic-specific logic.

#### Black Box (`std::hint::black_box`)

The `black_box` intrinsic serves as an optimization barrier, preventing the compiler from making assumptions
about the value passed through it. In the semantics, it acts as an identity function that simply passes
its argument to the destination without modification.

```k
  // Black box intrinsic implementation - identity function
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("black_box")), ARG:Operand .Operands, DEST)
        => #setLocalValue(DEST, ARG)
       ... </k>
```

#### Raw Eq (`std::intrinsics::raw_eq`)

The `raw_eq` intrinsic performs byte-by-byte equality comparison of the memory contents pointed to by two references.
It returns a boolean value indicating whether the referenced values are equal. The implementation dereferences the
provided references to access the underlying values, then compares them using K's built-in equality operator.

**Type Safety:**
The implementation requires operands to have identical types (`TY1 ==K TY2`) before performing the comparison.
Execution gets stuck (no matching rule) when operands have different types or unknown type information.

```k
  // Raw eq: dereference operands, extract types, and delegate to typed comparison
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("raw_eq")), ARG1:Operand ARG2:Operand .Operands, PLACE)
        => #execRawEqTyped(PLACE, #withDeref(ARG1), #extractOperandType(#withDeref(ARG1), LOCALS),
                                  #withDeref(ARG2), #extractOperandType(#withDeref(ARG2), LOCALS))
       ... </k>
       <locals> LOCALS </locals>

  // Compare values only if types are identical
  syntax KItem ::= #execRawEqTyped(Place, Evaluation, MaybeTy, Evaluation, MaybeTy) [seqstrict(2,4)]
  rule <k> #execRawEqTyped(DEST, VAL1:Value, TY1:Ty, VAL2:Value, TY2:Ty)
        => #setLocalValue(DEST, BoolVal(VAL1 ==K VAL2))
       ... </k>
    requires TY1 ==K TY2
    [preserves-definedness]

  // Add deref projection to operands
  syntax Operand ::= #withDeref(Operand) [function, total]
  rule #withDeref(operandCopy(place(LOCAL, PROJ)))
    => operandCopy(place(LOCAL, appendP(PROJ, projectionElemDeref .ProjectionElems)))
  rule #withDeref(operandMove(place(LOCAL, PROJ)))
    => operandCopy(place(LOCAL, appendP(PROJ, projectionElemDeref .ProjectionElems)))
       // must not overwrite the value, just the reference is moved!
  rule #withDeref(OP) => OP [owise]

  // Extract type from operands (locals with projections, constants, fallback to unknown)
  syntax MaybeTy ::= #extractOperandType(Operand, List) [function, total]
  rule #extractOperandType(operandCopy(place(local(I), PROJS)), LOCALS)
       => getTyOf(tyOfLocal({LOCALS[I]}:>TypedLocal), PROJS)
    requires 0 <=Int I andBool I <Int size(LOCALS) andBool isTypedLocal(LOCALS[I])
    [preserves-definedness]
  rule #extractOperandType(operandMove(place(local(I), PROJS)), LOCALS)
       => getTyOf(tyOfLocal({LOCALS[I]}:>TypedLocal), PROJS)
    requires 0 <=Int I andBool I <Int size(LOCALS) andBool isTypedLocal(LOCALS[I])
    [preserves-definedness]
  rule #extractOperandType(operandConstant(constOperand(_, _, mirConst(_, TY, _))), _) => TY
  rule #extractOperandType(_, _) => TyUnknown [owise]
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
  imports KMIR-LEMMAS

  imports KMIR-P-TOKEN // cheat codes
endmodule
```
