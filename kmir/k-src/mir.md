```k
require "mir-configuration.md"
require "panics.md"
```

Mir execution operational semantics
===================================

```k
module MIR
  imports MIR-CONFIGURATION
  imports PANICS

  configuration
    <k> $PGM:Mir </k>
    <returncode exit=""> 4 </returncode>     // the simulator exit code
    <mir/>
```

Interpreter initialization
--------------------------

### Function definition processing

```k
  rule <k> (fn PATH:FunctionPath (PARAMS:ParameterList) -> RETURN_TYPE:Type { BODY:FunctionBody }):Function REST
        => #initFunction(Fn(PATH), PARAMS, BODY, RETURN_TYPE) ~> REST ...
       </k>

  syntax MirSimulation ::= #initFunction(FunctionLikeKey, ParameterList, FunctionBody, Type)
  //----------------------------------------------------------------------------------------
  rule <k> #initFunction(FN_KEY:FunctionLikeKey,
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
  rule <k> #initFunction(FN_KEY:FunctionLikeKey,
                         _PARAMS:ParameterList,
                         _DEBUGS:DebugList BINDINGS:BindingList _SCOPES:ScopeList BLOCKS:BasicBlockList,
                         RETURN_TYPE:Type)
        => #initBindings(FN_KEY, BINDINGS)
        ~> #initBasicBlocks(FN_KEY, BLOCKS)
        ~> #initReturnValue(FN_KEY, RETURN_TYPE)
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

#### Return value declaration

The function's return value is a special binding at location `0`.

TODO: how do we initialize it? For now, we initialize it if it's missing or don't touch it if it was initialized in `#initBindings`.

```k
  syntax MirSimulation ::= #initReturnValue(FunctionLikeKey, Type)
  //-----------------------------------------------------------
  rule <k> #initReturnValue(FN_KEY:FunctionLikeKey, _TYPE:Type)
        => .K
        ...
       </k>
       <function>
         <fnKey> FN_KEY </fnKey>
         <localDecls>
           <localDecl>
             <index>      KEY                         </index>
             ...
           </localDecl>
           ...
         </localDecls>
         ...
       </function> requires KEY ==Int 0
  rule <k> #initReturnValue(FN_KEY:FunctionLikeKey, TYPE:Type) => .K ... </k>
       <function>
         <fnKey> FN_KEY </fnKey>
         <localDecls>
           (.Bag => <localDecl>
                      <index>       0:Int </index>
                      <mutability>  Not:Mutability   </mutability>
                      <internal>    false            </internal>
                      <ty>          TYPE:Type        </ty>
                    </localDecl>
           )
           ...
         </localDecls>
         ...
       </function> [owise]
```

#### Bindings declaration

Other bindings are declared by at their locations.

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

Interpreter finalization
------------------------

### Success

At the moment, we consider the execution successful if the `<k>` cell contains

TODO: design better success indication

```k
  rule <k> .Mir => .K </k>
       <returncode> _ => 0 </returncode>

```

### Internal panic

```k
  syntax KItem ::= #internalPanic(FunctionLikeKey, InternalPanic, KItem)
  //-----------------------------------------------------------------
  rule <k> #internalPanic(_FN_KEY, _PANIC, _MSG) ~> (_ITEM:KItem => .K) ... </k>
       <returncode> _ => 1 </returncode>
```

```k
endmodule
```

