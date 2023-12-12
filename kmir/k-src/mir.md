```k
require "mir-configuration.md"
require "panics.md"
```

MIR executable operational semantics
===================================

Top-level modules
-----------------

The `MIR` module is the main module of the concrete execution semantics to be used with the LLVM backend. It imports the following modules:

* `MIR-CONFIGURATION` defines the runtime configuration of the interpreter;
* `MIR-INITIALIZATION` defines rules that disambiguated the parsed program and initializes the runtime configuration;
* `MIR-EXECUTION` defines the execution rules for function, basic blocks, statements and expressions. NOT IMPLEMENTED.
* `MIR-FINALIZATION` defines the successful and panicking interpreter finalization rules.

The rules included in the top-level `MIR` module are related to starting and finishing execution.

```k
module MIR
  imports MIR-CONFIGURATION
  imports MIR-INITIALIZATION
  imports MIR-EXECUTION
  imports MIR-FINALIZATION

  syntax KItem ::= #initialized()
```

The presence of the empty program, `.Mir`, on the `<k>` cell indicates that the initialization phase of the semantics is finished, and we can start the execution phase.

```k
  rule <k> .Mir => #initialized() ... </k>
       <phase> Initialization </phase>
  rule <k> #initialized() => #executeFunctionLike(Fn(main :: .FunctionPath), .OperandList) ... </k>
       <phase> Initialization => Execution </phase>
```

The `#return` rule is triggered by the `return` terminator. We need to give it different treatment if we currently execute the `main` function.
If we are, then we stop execution and enter the finalization phase. Otherwise, if we're not currently in `main`, we return control to the caller function.

```k
  rule <k> #return(Fn(main), Unit) => #halt ... </k>
       <callStack> ListItem(Fn(main)) => .List </callStack>
       <phase> Execution => Finalization </phase>
       <returncode> _ => 0 </returncode>
  rule <k> #return(FUNCTION_KEY, _) => .K ... </k>
       <callStack> ListItem(FUNCTION_KEY) XS => XS </callStack>
    requires FUNCTION_KEY =/=K Fn(main)
```

The `#halt` construct is used to signify the end of execution. Any remaining items on the `<k>` cell will be removed.

```k
  syntax KItem ::= "#halt"
  //----------------------
  rule [halt]: <k> #halt ~> (_:MirSimulation => .K) </k>
  rule         <k> #halt ~> (#initialized()  => .K) </k>
endmodule
```

`MIR-SYMBOLIC` is a stub module to be used with the Haskell backend in the future. It does not import `MIR-AMBIGUITIES`, since `amb` productions are not supported by the Haskell backend. We may need to consult the C semantics team when we start working on symbolic execution.

```k
module MIR-SYMBOLIC
  imports MIR

    syntax KItem ::= runLemma ( Step ) | doneLemma ( Step )
    // -------------------------------------------------------
    rule <k> runLemma(S) => doneLemma(S) ... </k>

    syntax Step ::= Bool | Int | MIRValue
endmodule
```

Interpreter initialization
--------------------------

The `MIR-INITIALIZATION` module defines rules that construct the initial runtime configuration based on the parsed MIR program abstract syntax tree.
Note that this modules imports the `MIR-AMBIGUITIES` which defines how to reserve parsing ambiguities, hence the `MIR-INITIALIZATION` cannot be used
with the Haskell backend at the moment.

```k
module MIR-INITIALIZATION
  imports MIR-CONFIGURATION
  imports PANICS
  //imports MIR-AMBIGUITIES
```

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

The rule below is the generic function-like initializar rule invoked by the three rules above.

```k
  syntax MirSimulation ::= #initFunctionLike(FunctionLikeKey, ParameterList, FunctionBody, Type)
  //--------------------------------------------------------------------------------------------
```

The first case is the failure when such function-like already exists (it should be impossible in a valid compiler-generated MIR):

```k

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
```

The success case does the following:
* add a new `<function>` cell
* Collect the bindings from three sources:
  - the normal function bindings, i.e. `BINDINGS:BindingList`;
  - function arguments, i.e. `PARAMS:ParameterList`. See the "Function parameters processing" section below;
  - the user-defined variables that live in scopes, i.e. `SCOPES:ScopeList`. See the "Scopes processing" section below.

```k
  rule <k> #initFunctionLike(FN_KEY:FunctionLikeKey,
                         PARAMS:ParameterList,
                         _DEBUGS:DebugList BINDINGS:BindingList SCOPES:ScopeList BLOCKS:BasicBlockList,
                         _RETURN_TYPE:Type)
        => #initBindings(FN_KEY, BINDINGS +BindingList (parametersToBindings(PARAMS) +BindingList collectBindings(SCOPES)))
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

#### Function arguments processing

Function arguments need to be converted to `Binding`s to be inserted in the `<localDecls>` of a `<function>`.
For now, we convert them into immutable variables, but that may need to be changed in future.

```k
  syntax BindingList ::= parametersToBindings(ParameterList) [function]
  //-------------------------------------------------------------------
  rule parametersToBindings(.ParameterList) => .BindingList
  rule parametersToBindings(((LOCAL:Local : TYPE:Type) , REST):ParameterList) => ((let LOCAL : TYPE ;):Binding parametersToBindings(REST))


```

#### Scopes processing

The scopes are a part of a function body that tracks the Rust-level user-defined local variables. i.e. named variables.
It is likely that we do not care about variables scoping within a function, but we still need to process the scope declarations, because
**scopes contain local declarations for user variables**. We need to traverse the scopes, collect these variables, and append them to the
bindings list of the function.

```k
  syntax BindingList ::= collectBindings(ScopeList) [function]
                       | collectBindingsImpl(ScopeList, BindingList) [function]
  //---------------------------------------------------------------------------
  rule collectBindings(SL:ScopeList) => collectBindingsImpl(SL, .BindingList)

  rule collectBindingsImpl(.ScopeList, COLLECTED_BINDINGS) => COLLECTED_BINDINGS
  rule collectBindingsImpl(
       (scope _SCOPE_ID { _DL:DebugList BL:BindingList NESTED_SCOPES:ScopeList }):Scope OTHER_SCOPES:ScopeList,
       COLLECTED_BINDINGS) => collectBindingsImpl(NESTED_SCOPES, BL) +BindingList collectBindingsImpl(OTHER_SCOPES, COLLECTED_BINDINGS)
```

Concatenate two `BindingList`s:

```k
  syntax BindingList ::= BindingList "+BindingList" BindingList [function, total]
  //-----------------------------------------------------------------------------
  rule .BindingList +BindingList .BindingList => .BindingList
  rule BL +BindingList .BindingList => BL
  rule .BindingList +BindingList BL => BL
  rule (X XS) +BindingList (Y YS) => X Y (XS +BindingList YS)
```

#### Bindings declaration

Bindings are declared at their locations. The function's return value is a special binding at location `0`.
 We assume that the binding `_0` exists, as it should in a valid compiler-generated Mir file.

TODO: initialize `Mutability` basing in syntax, for now it's just declared as `Not` (immutable)
TODO: figure out how to deal with duplicate bindings. For now, we panic.

```k
  syntax MirSimulation ::= #initBindings(FunctionLikeKey, BindingList)
  //------------------------------------------------------------------
  rule <k> #initBindings(_FN_KEY, .BindingList)               => .K ... </k>
  rule <k> #initBindings(FN_KEY, (let _MUT:OptMut LOCAL:Local : _TYPE:Type ;):Binding _REST:BindingList)
        => #internalPanic(FN_KEY, DuplicateBinding, LOCAL)
        ...
       </k>
       <function>
         <fnKey> FN_KEY </fnKey>
         <localDecls>
           <localDecl>
             <index> KEY </index>
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
                      <value>       defaultMIRValue(TYPE) </value>
                    </localDecl>
           )
           ...
         </localDecls>
         ...
       </function> [owise]
```

#### Basic blocks declaration

Basic blocks carry the actual executable code. When initializing a block, we pre-process its code with disambiguation functions from `MIR-AMBIGUITIES`.

This rule panics if it encounters a duplicate block.

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
                      <bbBody> BODY</bbBody>
                    </basicBlock>
           )
           ...
         </basicBlocks>
         ...
       </function> [owise]
```

```k
endmodule
```

Execution
---------

`MIR-EXECUTION` defines the execution rules for function, basic blocks, statements and expressions. NOT IMPLEMENTED.

```k
module MIR-EXECUTION
  imports MIR-SYNTAX
  imports MIR-TYPES
  imports MIR-SORT-CASTS
  imports MIR-RVALUE
  imports PANICS
  imports K-EQUAL
```

Executing a function-like means:
* instantiating its arguments in the context of the caller
* executing its first basic block

Note that the `main` function is special: it does not have a caller.

```k
  syntax IdentifierToken ::= "main" [token]

  syntax MirSimulation ::= #executeFunctionLike(FunctionLikeKey, OperandList)
  //--------------------------------------------------------------------------
  rule <k> #executeFunctionLike(FN_KEY, _ARGS)
        => #executeBasicBlock(FN_KEY, 0)
        ...
       </k>
       <callStack> .List => ListItem(FN_KEY) </callStack>
    requires FN_KEY ==K Fn(main :: .FunctionPath)
  rule <k> #executeFunctionLike(CALLEE_FN_KEY, ARGS)
        => #instantiateArguments(CALLER_FN_KEY, ARGS, 1)
        ~> #executeBasicBlock(CALLEE_FN_KEY, 0)
        ...
       </k>
       <callStack> ListItem(CALLER_FN_KEY) STACK => ListItem(CALLEE_FN_KEY) ListItem(CALLER_FN_KEY) STACK </callStack>
  rule <k> #executeFunctionLike(CALLEE_FN_KEY, ARGS)
        => #addRecursiveFrame(CALLEE_FN_KEY, ARGS)
        ...
       </k>
       <callStack> ListItem(CALLER_FN_KEY) _STACK </callStack>
       requires CALLER_FN_KEY ==K CALLEE_FN_KEY
  rule <k> #executeFunctionLike(Fn(PATH), ARGS)
        => #addRecursiveFrame(Fn(PATH), ARGS)
        ...
       </k>
       <callStack> ListItem(Rec(PATH, _)) _STACK </callStack> [priority(49)]

  // TODO: Either save unimplemented stack frame for correct initial values, or clear values
  syntax MirSimulation ::= #addRecursiveFrame(FunctionLikeKey, OperandList)
  //-------------------------------------------------------------------------
  rule <k> #addRecursiveFrame(Fn(PATH), ARGS)
        => #instantiateArguments(Rec(PATH, 0), ARGS, 1)
        ~> #executeBasicBlock(Rec(PATH, 0), 0)
        ...
       </k>
       <callStack> ListItem(Fn(PATH)) STACK => ListItem(Rec(PATH, 0)) ListItem(Fn(PATH)) STACK </callStack>
       <functions>...
         <function> <fnKey> Fn(PATH) </fnKey> REST </function>
         (.Bag => <function> <fnKey> Rec(PATH, 0) </fnKey> REST </function>)
       ...</functions>
  rule <k> #addRecursiveFrame(Fn(PATH), ARGS)
        => #instantiateArguments(Rec(PATH, DEPTH +Int 1), ARGS, 1)
        ~> #executeBasicBlock(Rec(PATH, DEPTH +Int 1), 0)
        ...
       </k>
       <callStack> ListItem(Rec(PATH, DEPTH)) STACK => ListItem(Rec(PATH, DEPTH +Int 1)) ListItem(Rec(PATH, DEPTH)) STACK </callStack>
       <functions>...
         <function> <fnKey> Fn(PATH) </fnKey> REST </function>
         (.Bag => <function> <fnKey> Rec(PATH, DEPTH +Int 1) </fnKey> REST </function>)
       ...</functions>
```

Assign arguments (actual parameters) to formal parameters of a function-like:

```k
  syntax MirSimulation ::= #instantiateArguments(FunctionLikeKey, OperandList, Int)
  //--------------------------------------------------------------------------------
  rule <k> #instantiateArguments(_FN_KEY, .OperandList, _) => .K ... </k>
  rule <k> #instantiateArguments(FN_KEY, (ARG, REST):OperandList, ARGUMENT_NUMBER:Int)
        => #writeLocal(CALLEE_FN_KEY, Int2Local(ARGUMENT_NUMBER), evalOperand(CALLER_FN_KEY, ARG))
        ~> #instantiateArguments(FN_KEY, REST, ARGUMENT_NUMBER +Int 1)
        ...
      </k>
      <callStack> ListItem(CALLEE_FN_KEY) ListItem(CALLER_FN_KEY) _STACK </callStack>
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
             <bbBody> {STATEMENTS:Statements TERMINATOR:Terminator ;}:BasicBlockBody </bbBody>
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
  syntax MirSimulation ::= #executeStatements(Statements)
                         | #executeStatement(StatementKind)
                         | #executeStatement(ResolvedStatementKind)
  //--------------------------------------------------------
  rule <k> #executeStatements(FIRST; REST)
        => #executeStatement(FIRST)
        ~> #executeStatements(REST)
        ...
       </k>
  rule <k> #executeStatements(.Statements)
        => .K
        ...
       </k>
```

##### Assignment

```k
  rule <k> #executeStatement(LOCAL:Local = RVALUE) => #executeStatement(Local2Int(LOCAL) = RVALUE) ...</k>

  rule <k> #executeStatement(INDEX:Int = RVALUE)
        => .K
        ...
       </k>
       <callStack> ListItem(FN_KEY) ... </callStack>
       <function>
         <fnKey> FN_KEY </fnKey>
         <localDecl>
           <index> INDEX  </index>
           <value> _ => fromInterpResult(evalRValue(FN_KEY, RVALUE)) </value>
           ...
         </localDecl>
         ...
       </function>
     requires isRValueResult(evalRValue(FN_KEY, RVALUE))
```

#### Terminators

```k
  syntax MirSimulation ::= #executeTerminator(Terminator)
  //-----------------------------------------------------
  rule <k> #executeTerminator(return)
        => #return(FN_KEY, RETURN_VALUE)
        ...
       </k>
       <callStack> ListItem(FN_KEY) ... </callStack>
       <function>
         <fnKey> FN_KEY </fnKey>
         <localDecl>
           <index> 0  </index>
           <value> RETURN_VALUE </value>
           ...
         </localDecl>
         ...
       </function>
  rule <k> #executeTerminator(assert(ARG:AssertArgument, KIND:AssertKind) -> ((NEXT:BBName _):BB))
        => #assert(FN_KEY, ARG, KIND) ~> #executeBasicBlock(FN_KEY, BBName2Int(NEXT))
        ...
       </k>
       <callStack> ListItem(FN_KEY) ... </callStack>
  rule <k> #executeTerminator(goto -> ((NEXT:BBName _):BB))
        => #executeBasicBlock(FN_KEY, BBName2Int(NEXT))
        ...
       </k>
       <callStack> ListItem(FN_KEY) ... </callStack>
  rule <k> #executeTerminator(DEST_LOCAL:Local = OTHER_FN_NAME:PathInExpression ( ARGS ) -> ((NEXT:BBName _):BB))
        => #executeFunctionLike(Fn(toFunctionPath(OTHER_FN_NAME)), ARGS)
        ~> #transferLocal(Fn(toFunctionPath(OTHER_FN_NAME)), Int2Local(0), FN_KEY, DEST_LOCAL)
        ~> #executeBasicBlock(FN_KEY, BBName2Int(NEXT))
        ...
       </k>
       <callStack> ListItem(FN_KEY) ... </callStack>
  rule <k> #executeTerminator(DEST_LOCAL:Local = OTHER_FN_NAME:PathInExpression ( ARGS ) -> ((NEXT:BBName _):BB))
        => #executeFunctionLike(Fn(toFunctionPath(OTHER_FN_NAME)), ARGS)
        ~> #transferLocal(Rec(toFunctionPath(OTHER_FN_NAME), 0), Int2Local(0), Fn(FNAME), DEST_LOCAL)
        ~> #executeBasicBlock(Fn(FNAME), BBName2Int(NEXT))
        ...
       </k>
       <callStack> ListItem(Fn(FNAME)) ... </callStack>
    requires FNAME ==K toFunctionPath(OTHER_FN_NAME) [priority(49)]
  rule <k> #executeTerminator(DEST_LOCAL:Local = OTHER_FN_NAME:PathInExpression ( ARGS ) -> ((NEXT:BBName _):BB))
        => #executeFunctionLike(Fn(toFunctionPath(OTHER_FN_NAME)), ARGS)
        ~> #transferLocal(Rec(toFunctionPath(OTHER_FN_NAME), DEPTH +Int 1), Int2Local(0), Rec(FNAME, DEPTH), DEST_LOCAL)
        ~> #executeBasicBlock(Rec(FNAME, DEPTH), BBName2Int(NEXT))
        ...
       </k>
       <callStack> ListItem(Rec(FNAME, DEPTH)) ... </callStack>
    requires FNAME ==K toFunctionPath(OTHER_FN_NAME) [priority(49)]
  rule <k> #executeTerminator(switchInt (ARG:Operand) -> [ TARGETS:SwitchTargets , otherwise : OTHERWISE:BB ])
        => #switchInt(FN_KEY, castMIRValueToInt(evalOperand(FN_KEY, ARG)), TARGETS, OTHERWISE)
        ...
       </k>
       <callStack> ListItem(FN_KEY) ... </callStack>
    requires isInt(castMIRValueToInt(evalOperand(FN_KEY, ARG)))
  rule <k> #executeTerminator(_:Local = PANIC_CALL (ARG, .OperandList))
        => #panic(FN_KEY, PanicCall, ARG)
        ...
       </k>
       <callStack> ListItem(FN_KEY) ... </callStack>
    requires PANIC_CALL ==K String2IdentifierToken("core") :: String2IdentifierToken("panicking") :: String2IdentifierToken("panic") :: .ExpressionPathList
  rule <k> #executeTerminator(TERMIANTOR:Terminator)
        => #internalPanic(FN_KEY, NotImplemented, TERMIANTOR)
        ...
       </k>
       <callStack> ListItem(FN_KEY) ... </callStack> [owise]

  // Option Unwrap Call
  rule <k> #executeTerminator(DEST_LOCAL:Local = Option :: < _TYPES > :: unwrap :: .ExpressionPathList ( ARG , .OperandList ) -> ((NEXT:BBName _):BB)) 
        => #executeStatement(DEST_LOCAL = #unwrap(ARG)) ~> #executeBasicBlock(FN_KEY, BBName2Int(NEXT)) ...
       </k>
       <callStack> ListItem(FN_KEY) ... </callStack> [priority(48)]
```

The following rule executes exists to copy a value of one local to another local, the locals may belong to different functions.
The rule **does not check types**!
The rule **gets stuck** of if does not find function/locals it needs.

```k
  syntax MirSimulation ::= #transferLocal(FunctionLikeKey, Local, FunctionLikeKey, Local)
  syntax MirSimulation ::= #transferLocalResolved(FunctionLikeKey, Int, FunctionLikeKey, Int)
  //-------------------------------------------------------------------------------------
  rule <k> #transferLocal(FN_KEY_SOURCE, LOCAL_SOURCE, FN_KEY_DEST, LOCAL_DEST) => #transferLocalResolved(FN_KEY_SOURCE, Local2Int(LOCAL_SOURCE), FN_KEY_DEST, Local2Int(LOCAL_DEST)) ... </k>
  rule <k> #transferLocalResolved(FN_KEY_SOURCE, INDEX_SOURCE, FN_KEY_DEST, INDEX_DEST) => .K ... </k>
       <function>
         <fnKey> FN_KEY_SOURCE </fnKey>
         <localDecl>
           <index> INDEX_SOURCE  </index>
           <value> VALUE </value>
           ...
         </localDecl>
         ...
       </function>
       <function>
         <fnKey> FN_KEY_DEST </fnKey>
         <localDecl>
           <index> INDEX_DEST  </index>
           <value> _ => VALUE </value>
           ...
         </localDecl>
         ...
       </function>

  syntax MirSimulation ::= #writeLocal(FunctionLikeKey, Local, MIRValue)
  //--------------------------------------------------------------------
  rule <k> #writeLocal(FN_KEY, LOCAL, VALUE) => .K ... </k>
       <function>
         <fnKey> FN_KEY </fnKey>
         <localDecl>
           <index> INDEX  </index>
           <value> _ => VALUE </value>
           ...
         </localDecl>
         ...
       </function>
    requires INDEX ==Int Local2Int(LOCAL)

  syntax MIRValue ::= readLocal(FunctionLikeKey, Local) [function]
  //--------------------------------------------------------------
  rule [[ readLocal(FN_KEY, LOCAL) => VALUE ]]
       <function>
         <fnKey> FN_KEY </fnKey>
         <localDecl>
           <index> INDEX  </index>
           <value> VALUE </value>
           ...
         </localDecl>
         ...
       </function>
    requires INDEX ==Int Local2Int(LOCAL)
```

* `switchInt`

```k
  syntax MirSimulation ::= #switchInt(FunctionLikeKey, Int, SwitchTargets, BB)
  //--------------------------------------------------------------------------
  rule <k> #switchInt(FN_KEY, _SWITCH:Int, .SwitchTargets, (OTHERWISE:BBName _):BB)
        => #executeBasicBlock(FN_KEY, BBName2Int(OTHERWISE))
        ...
       </k>
  rule <k> #switchInt(FN_KEY, SWITCH:Int, ((DISCRIMINANT:Int : (TARGET:BBName _):BB):SwitchTarget , _OTHER_TARGETS):SwitchTargets, _OTHERWISE:BB)
        => #executeBasicBlock(FN_KEY, BBName2Int(TARGET))
        ...
       </k>
    requires SWITCH ==Int DISCRIMINANT
  rule <k> #switchInt(FN_KEY, SWITCH:Int, ((DISCRIMINANT:Int : (_TARGET:BBName _):BB):SwitchTarget , OTHER_TARGETS):SwitchTargets, OTHERWISE:BB)
        => #switchInt(FN_KEY, SWITCH, OTHER_TARGETS , OTHERWISE)
        ...
       </k>
    requires SWITCH =/=Int DISCRIMINANT
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
  syntax MirSimulation ::= #assert(FunctionLikeKey, AssertArgument, AssertKind)
  //-------------------------------------------------------------------
```

Positive assertion succeeds if the argument evaluates to true, but fails if either:
* argument evaluates to false --- assertion error
* argument is not boolean --- internal type error --- should be impossible with real MIR.

```k
  rule <k> #assert(FN_KEY, ASSERTION:Operand, _KIND:AssertKind)
        => .K
        ...
       </k>
   requires isBool(evalOperand(FN_KEY, ASSERTION))
    andBool evalOperand(FN_KEY, ASSERTION) ==K true
  rule <k> #assert(FN_KEY, ASSERTION:Operand, _KIND:AssertKind)
        => #panic(FN_KEY, AssertionViolation, ASSERTION)
        ...
       </k>
   requires isBool(evalOperand(FN_KEY, ASSERTION))
    andBool evalOperand(FN_KEY, ASSERTION) ==K false
  rule <k> #assert(FN_KEY, ASSERTION:Operand, KIND:AssertKind)
        => #internalPanic(FN_KEY, TypeError, assert(ASSERTION, KIND))
        ...
       </k>
   requires notBool isBool(evalOperand(FN_KEY, ASSERTION))
```

Negative assertions are similar to positive ones but need special treatment for error reporting.
TODO: maybe we should unify positive and negative assertions.

```k
  rule <k> #assert(FN_KEY, ! ASSERTION:Operand, _KIND:AssertKind)
        => .K
        ...
       </k>
   requires isBool(evalOperand(FN_KEY, ASSERTION))
    andBool evalOperand(FN_KEY, ASSERTION) ==K false
  rule <k> #assert(FN_KEY, ! ASSERTION:Operand, _KIND:AssertKind)
        => #panic(FN_KEY, AssertionViolation, (! ASSERTION)) //TODO!
        ...
       </k>
   requires isBool(evalOperand(FN_KEY, ASSERTION))
    andBool evalOperand(FN_KEY, ASSERTION) ==K true
  rule <k> #assert(FN_KEY, (! ASSERTION:Operand), KIND:AssertKind)
        => #internalPanic(FN_KEY, TypeError, assert(! ASSERTION, KIND))
        ...
       </k>
   requires notBool isBool(evalOperand(FN_KEY, ASSERTION))
```

```k
  rule <k> #assert(FN_KEY, ARG, KIND)
        => #internalPanic(FN_KEY, NotImplemented, assert(ARG, KIND))
        ...
       </k> [owise]
```

```k
endmodule
```

Interpreter finalization
------------------------

```k
module MIR-FINALIZATION
  imports MIR-CONFIGURATION
  imports PANICS
  imports K-EQUAL
```

### Internal panic

These are internal panics that are specific to KMIR.

```k
  rule [iPanic]: <k> #internalPanic(_FN_KEY, _PANIC, _MSG) ~> (_ITEM:KItem => .K) ... </k>
       <returncode> 4 => 1 </returncode>
```

### Regular panic

These panics are not specific to KMIR and caused by program-level reasons, i.e. assertion violations.

```k
  rule [panic]: <k> #panic(_FN_KEY, _PANIC, _MSG) ~> (_ITEM:KItem => .K) ... </k>
       <returncode> 4 => 2 </returncode>
```

```k
endmodule
```

