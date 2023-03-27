```k
require "mir-configuration.md"
require "panics.md"
```

Mir execution operational semantics
===================================

Top-level modules
-----------------

The `MIR` module is the main module of the concrete execution semantics to be used with the LLVM backend. It imports the following modules:

* `MIR-CONFIGURATION` defines the runtime configuration of the interpreter;
* `MIR-INITIALIZATION` defines rules that disambiguated the parsed program and initializes the runtime configuration;
* `MIR-EXECUTION` defines the execution rules for function, basic blocks, statements and expressions. NOT IMPLEMENTED.
* `MIR-FINALIZATION` defines the successful and panicking interpreter finalization rules.

```k
module MIR
  imports MIR-CONFIGURATION
  imports MIR-INITIALIZATION
  imports MIR-FINALIZATION

  syntax KItem ::= #initialized()

  rule <k> .Mir => #initialized() ... </k>
       <phase> Initialization </phase>
       <returncode> _ => 0 </returncode>

endmodule
```

`MIR-SYMBOLIC` is a stub module to be used with the Haskell backend in the future.

```k
module MIR-SYMBOLIC
  imports MIR-CONFIGURATION

endmodule
```

Interpreter initialization
--------------------------

The `MIR-INITIALIZATION` module defines rules that construct the initial runtime configuration based on the parsed MIR program abstract syntax tree.
Note that this modules imports the `MIR-AMBIGUITIES` which defines how to reserve parsing ambiguities, hence the `MIR-INITIALIZATION` cannot be used
with the Haskell backend at the moment.

TODO: consult the C semantics team on how to use the Haskell backend in presence of parsing ambiguities.

```k
module MIR-INITIALIZATION
  imports MIR-CONFIGURATION
  imports PANICS
  imports MIR-AMBIGUITIES
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
 We assume that the binding `_0` exists, as it should in a valid compiler-generated Mir file.

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
                      <bbBody> disambiguateBasicBlockBody(BODY) </bbBody>
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
  rule <k> #internalPanic(_FN_KEY, _PANIC, _MSG) ~> (_ITEM:KItem => .K) ... </k>
       <returncode> _ => 1 </returncode>
```

### Regular panic

These panics are not specific to KMIR and caused by program-level reasons, i.e. assertion violations.

```k
  rule <k> #panic(_FN_KEY, _PANIC, _MSG) ~> (_ITEM:KItem => .K) ... </k>
       <returncode> _ => 2 </returncode>
```

```k
endmodule
```

