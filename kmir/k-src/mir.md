```k
require "mir-configuration.md"
require "mir-rvalue-eval.md"
require "panics.md"
```

Mir execution operational semantics
===================================

```k
module MIR
  imports MIR-CONFIGURATION
  imports MIR-RVALUE-EVAL
  imports PANICS
  imports K-EQUAL

  configuration
    <k> $PGM:Mir </k>
    <returncode exit=""> 4 </returncode>     // the simulator exit code
    <mir/>
```

Interpreter initialization
--------------------------

### Function definition processing

* Normal functions:
```k
  rule <k> (fn PATH:FunctionPath (PARAMS:ParameterList) -> RETURN_TYPE:Type { BODY:FunctionBody }):Function REST
        => #initFunctionLike(Fn(PATH), PARAMS, BODY, RETURN_TYPE) ~> REST ...
       </k>
```

* Promoted definitions:
```k
  rule <k> (promoted[ INDEX:Int ] in PATH:FunctionPath : TYPE:Type = { BODY:FunctionBody }):FunctionForPromoted REST
        => #initFunctionLike(Promoted(PATH, INDEX), .ParameterList, BODY, TYPE) ~> REST ...
       </k>
```

* Data definitions:

```k
    // TODO
```


The tree rules above invoke the following internal initializer rule:

```k
  syntax MirSimulation ::= #initFunctionLike(FunctionLikeKey, ParameterList, FunctionBody, Type)
  //--------------------------------------------------------------------------------------------
  rule <k> #initFunctionLike(FN_KEY:FunctionLikeKey,
                         _PARAMS:ParameterList,
                         _DEBUGS:DebugList _BINDINGS:BindingList _SCOPES:ScopeList _BLOCKS:BasicBlockList,
                         _RETURN_TYPE:Type)
        => #internalPanic(FN_KEY, DuplicateFunction, FN_KEY)
        ...
       </k>
       <functions>
         <function>
           <fnKey> FN_KEY </fnKey>
           ...
         </function>
         ...
       </functions>
  rule <k> #initFunctionLike(FN_KEY:FunctionLikeKey,
                         _PARAMS:ParameterList,
                         _DEBUGS:DebugList BINDINGS:BindingList _SCOPES:ScopeList BLOCKS:BasicBlockList,
                         _RETURN_TYPE:Type)
        => #initBindings(FN_KEY, BINDINGS)
        ~> #initBasicBlocks(FN_KEY, BLOCKS)
        ...
       </k>
       <functions>
         (.Bag => <function>
                    <fnKey> FN_KEY </fnKey>
                    ...
                  </function>
         )
         ...
       </functions> [owise]
```


#### Bindings declaration

Bindings are declared at their locations. The function's return value is a special binding at location `0`.

TODO: initialize `Mutability` basing in syntax, for now it's just declared as `Not` (immutable)
TODO: figure out how to deal with duplicate bindings. For now, we panic.

```k
  syntax MirSimulation ::= #initBindings(FunctionLikeKey, BindingList)
  //---------------------------------------------------------------
  rule <k> #initBindings(_FN_KEY, .BindingList)               => .K ... </k>
  rule <k> #initBindings(FN_KEY, (let _MUT:OptMut LOCAL:Local : _TYPE:Type ;):Binding _REST:BindingList)
        => #internalPanic(FN_KEY, DuplicateBinding, LOCAL)
        ...
       </k>
       <function>
         <fnKey> FN_KEY </fnKey>
         <localDecls>
           <localDecl>
             <index>      KEY              </index>
             ...
           </localDecl>
           ...
         </localDecls>
         ...
       </function> requires KEY ==Int Local2Int(LOCAL)
  rule <k> #initBindings(FN_KEY, (let _MUT:OptMut LOCAL:Local : TYPE:Type ;):Binding REST:BindingList) => #initBindings(FN_KEY, REST) ... </k>
       <function>
         <fnKey> FN_KEY </fnKey>
         <localDecls>
           (.Bag => <localDecl>
                      <index>       Local2Int(LOCAL) </index>
                      <mutability>  Not:Mutability   </mutability>
                      <internal>    false            </internal>
                      <ty>          TYPE:Type        </ty>
                      <value>       0:MIRValue       </value> //TODO: initialize with Type? or None?
                    </localDecl>
           )
           ...
         </localDecls>
         ...
       </function> [owise]
```

#### Basic blocks declaration

```k
  syntax MirSimulation ::= #initBasicBlocks(FunctionLikeKey, BasicBlockList)
  //-------------------------------------------------------
  rule <k> #initBasicBlocks(_FN_KEY, .BasicBlockList)               => .K ... </k>
  rule <k> #initBasicBlocks(FN_KEY, ((NAME:BBName CLEANUP:MaybeBBCleanup):BB : _BODY:BasicBlockBody):BasicBlock _REST:BasicBlockList)
        => #internalPanic(FN_KEY, DuplicateBasicBlock, (NAME:BBName CLEANUP:MaybeBBCleanup))
        ...
       </k>
       <function>
         <fnKey> FN_KEY </fnKey>
         <basicBlocks>
           <basicBlock>
             <bbName> KEY </bbName>
             ...
           </basicBlock>
           ...
         </basicBlocks>
         ...
       </function> requires KEY ==Int BBName2Int(NAME)
  rule <k> #initBasicBlocks(FN_KEY, ((NAME:BBName _:MaybeBBCleanup):BB : BODY:BasicBlockBody):BasicBlock REST:BasicBlockList)
        => #initBasicBlocks(FN_KEY, REST) ... </k>
       <function>
         <fnKey> FN_KEY </fnKey>
         <basicBlocks>
           (.Bag => <basicBlock>
                      <bbName> BBName2Int(NAME) </bbName>
                      <bbBody> BODY:BasicBlockBody </bbBody>
                    </basicBlock>
           )
           ...
         </basicBlocks>
         ...
       </function> [owise]

```

Execution
---------

```k
  rule <k> .Mir => #executeFunctionLike(Fn(String2IdentifierToken("main"):: .FunctionPath)) ... </k>
       <phase> Initialization => Execution </phase>
```

```k
  syntax MirSimulation ::= #executeFunctionLike(FunctionLikeKey)
  //------------------------------------------------------------
  rule <k> #executeFunctionLike(FN_KEY)
        => #executeBasicBlock(FN_KEY, 0)
        ...
       </k>
       <currentFnKey> _ => FN_KEY </currentFnKey>
```

### Single basic block execution

The following rule executes a specific basic block (refereed by index) in a function-like,
or panics if the function-like or the block is missing:

```k
  syntax MirSimulation ::= #executeBasicBlock(FunctionLikeKey, Int)
  //---------------------------------------------------------------
  rule <k> #executeBasicBlock(FN_KEY, INDEX)
        => #executeStatements(STATEMENTS)
        ~> #executeTerminator(TERMINATOR)
        ...
       </k>
       <currentBasicBlock> _ => INDEX </currentBasicBlock>
       <function>
         <fnKey> FN_KEY </fnKey>
         <basicBlocks>
           <basicBlock>
             <bbName> INDEX </bbName>
             <bbBody> {STATEMENTS:StatementList TERMINATOR:Terminator ;}:BasicBlockBody </bbBody>
           </basicBlock>
           ...
         </basicBlocks>
         ...
       </function>
  rule <k> #executeBasicBlock(FN_KEY, INDEX)
        => #internalPanic(FN_KEY, MissingBasicBlock, INDEX)
        ...
       </k> [owise]
```

### Statements and terminators execution

#### Statements

```k
  syntax MirSimulation ::= #executeStatements(StatementList)
                         | #executeStatement(Statement)
  //--------------------------------------------------------
  rule <k> #executeStatements(FIRST; REST)
        => #executeStatement(FIRST)
        ~> #executeStatements(REST)
        ...
       </k>
  rule <k> #executeStatements(.StatementList)
        => .K
        ...
       </k>
```

##### Assignment

```k
  rule <k> #executeStatement(PLACE:Local = RVALUE)
        => .K
        ...
       </k>
       <currentFnKey> FN_KEY </currentFnKey>
       <function>
         <fnKey> FN_KEY </fnKey>
         <localDecl>
           <index> INDEX  </index>
           <value> _ => fromInterpResult(evalRValue(RVALUE)) </value>
           ...
         </localDecl>
         ...
       </function>
    requires INDEX ==Int Local2Int(PLACE)
     andBool isRValueResult(evalRValue(RVALUE))
  rule <k> #executeStatement(PLACE:Local = (OPERATION((X:RValue, Y:RValue, .ArgumentList):ArgumentList)):CallLike)
        => .K
        ...
       </k>
       <currentFnKey> FN_KEY </currentFnKey>
       <function>
         <fnKey> FN_KEY </fnKey>
         <localDecl>
           <index> INDEX  </index>
           <value> _ => {evalRValue(X)}:>Int >Int {evalRValue(Y)}:>Int </value>
           ...
         </localDecl>
         ...
       </function>
    requires INDEX ==Int Local2Int(PLACE)
     andBool isInt(evalRValue(X))
     andBool isInt(evalRValue(Y))
     andBool OPERATION ==K String2IdentifierToken("Gt"):Callable
  rule <k> #executeStatement(PLACE:Local = RVALUE)
        => #internalPanic(FN_KEY, RValueEvalError, evalRValue(RVALUE))
        ...
       </k>
       <currentFnKey> FN_KEY </currentFnKey>
    requires notBool isRValueResult(evalRValue(RVALUE))
```

#### Terminators

```k
  syntax MirSimulation ::= #executeTerminator(Terminator)
  //-----------------------------------------------------
  rule <k> #executeTerminator(return)
        => #return(FN_KEY, RETURN_VALUE)
        ...
       </k>
       <currentFnKey> FN_KEY </currentFnKey>
       <function>
         <fnKey> FN_KEY </fnKey>
         <localDecl>
           <index> 0  </index>
           <value> RETURN_VALUE </value>
           ...
         </localDecl>
         ...
       </function>
  rule <k> #executeTerminator(assert(ARGS) -> ((NEXT:BBName _):BB):TerminatorDestination)
        => #assert(FN_KEY, ARGS) ~> #executeBasicBlock(FN_KEY, BBName2Int(NEXT))
        ...
       </k>
       <currentFnKey> FN_KEY </currentFnKey>
  rule <k> #executeTerminator(TERMIANTOR:Terminator)
        => #internalPanic(FN_KEY, NotImplemented, TERMIANTOR)
        ...
       </k>
       <currentFnKey> FN_KEY </currentFnKey> [owise]
```

* `return`
```k
  syntax MirSimulation ::= #return(FunctionLikeKey, RValueResult)
```
The `return` terminator's semantics is defined in the [Interpreter finalization]() section.

* `assert`

The `#assert` production will be eliminated from the `<k>` cell if the assertion succeeds, or leave
a `#panic` (or `#internalPanic`) production otherwise.

```k
  syntax MirSimulation ::= #assert(FunctionLikeKey, AssertArgumentList)
  //-------------------------------------------------------------------
```

Positive assertion succeeds if the argument evaluates to true, but fails if either:
* argument evaluates to false --- assertion error
* argument is not boolean --- internal type error --- should be impossible with real Mir.

```k
  rule <k> #assert(FN_KEY, (ASSERTION:BasicRValue) , .AssertArgumentList)
        => .K
        ...
       </k>
   requires isBool(evalBasicRValue(ASSERTION))
    andBool evalBasicRValue(ASSERTION) ==K true
  rule <k> #assert(FN_KEY, (ASSERTION:BasicRValue) , .AssertArgumentList)
        => #panic(FN_KEY, AssertionViolation, ASSERTION)
        ...
       </k>
   requires isBool(evalBasicRValue(ASSERTION))
    andBool evalBasicRValue(ASSERTION) ==K false
  rule <k> #assert(FN_KEY, (ASSERTION:BasicRValue) , .AssertArgumentList)
        => #internalPanic(FN_KEY, TypeError, assert(ASSERTION))
        ...
       </k>
   requires notBool isBool(evalBasicRValue(ASSERTION))
```

Negative assertions are similar to positive ones but need special treatment for error reporting.
TODO: maybe we should unify positive and negative assertions.

```k
  rule <k> #assert(FN_KEY, (! ASSERTION:BasicRValue)  , .AssertArgumentList)
        => .K
        ...
       </k>
   requires isBool(evalBasicRValue(ASSERTION))
    andBool evalBasicRValue(ASSERTION) ==K false
  rule <k> #assert(FN_KEY, (! ASSERTION:BasicRValue) , .AssertArgumentList)
        => #panic(FN_KEY, AssertionViolation, (! ASSERTION))
        ...
       </k>
   requires isBool(evalBasicRValue(ASSERTION))
    andBool evalBasicRValue(ASSERTION) ==K true
  rule <k> #assert(FN_KEY, (! ASSERTION:BasicRValue) , .AssertArgumentList)
        => #internalPanic(FN_KEY, TypeError, assert(! ASSERTION))
        ...
       </k>
   requires notBool isBool(evalBasicRValue(ASSERTION))
```

```k
  rule <k> #assert(FN_KEY, ARGS)
        => #internalPanic(FN_KEY, NotImplemented, assert(ARGS))
        ...
       </k> [owise]
```

Interpreter finalization
------------------------

### Success

Execution finishes successfully if the `main` function returns `Unit`.
TODO: support other types that implement the `Termination` trait.

```k
  rule <k> #return(FUNCTION_KEY, Unit) => .K ... </k>
       <phase> Execution => Finalization </phase>
       <returncode> _ => 0 </returncode>
    requires FUNCTION_KEY ==K Fn(String2IdentifierToken("main"))
```

### Internal panic

These are internal panics that are specific to KMIR.

```k
  syntax KItem ::= #internalPanic(FunctionLikeKey, InternalPanic, KItem)
  //--------------------------------------------------------------------
  rule <k> #internalPanic(_FN_KEY, _PANIC, _MSG) ~> (_ITEM:KItem => .K) ... </k>
       <returncode> _ => 1 </returncode>
```

### Regular panic

These panics are not specific to KMIR and caused by program-level reasons, i.e. assertion violations.

```k
  syntax KItem ::= #panic(FunctionLikeKey, Panic, KItem)
  //----------------------------------------------------
  rule <k> #panic(_FN_KEY, _PANIC, _MSG) ~> (_ITEM:KItem => .K) ... </k>
       <returncode> _ => 2 </returncode>
```

```k
endmodule
```

