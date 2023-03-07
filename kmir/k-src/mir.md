```k
require "mir-configuration.md"
```

Mir execution operational semantics
===================================

```k
module MIR
  imports MIR-CONFIGURATION

  configuration
    <k> $PGM:Mir </k>
    <mir/>
```


Interpreter initialization
--------------------------

### Function definition processing

ATTENTION: this initialization routine only works if the mir file has a single function!

```k
  rule <k> (fn _PATH:FunctionPath (PARAMS:ParameterList) -> RETURN_TYPE:Type { BODY:FunctionBody }):Function REST
        => #initFunction(PARAMS, BODY, RETURN_TYPE) ~> REST ...
       </k>

  syntax MirSimulation ::= #initFunction(ParameterList, FunctionBody, Type)
  //-----------------------------------------------------------------------
  rule <k> #initFunction(_PARAMS:ParameterList,
                         _DEBUGS:DebugList BINDINGS:BindingList _SCOPES:ScopeList BLOCKS:BasicBlockList,
                         RETURN_TYPE:Type)
        => #initReturnValue(RETURN_TYPE)
        ~> #initBindings(BINDINGS)
        ~> #initBasicBlocks(BLOCKS)
        ...
       </k>
```

#### Return value declaration

The function's return value is a special binding at location `0`:

```k
  syntax MirSimulation ::= #initReturnValue(Type)
  //---------------------------------------------
  rule <k> #initReturnValue(TYPE:Type) => .K ... </k>
       <localDecls>
         <localDecl>
           <index>      KEY              </index>
           <mutability> _ => Mut         </mutability>
           <internal>   _ => false       </internal>
           <ty>         _:Type  => TYPE  </ty>
         </localDecl>
         ...
       </localDecls> requires KEY ==Int 0
  rule <k> #initReturnValue(TYPE:Type) => .K ... </k>
       <localDecls>
         (.Bag => <localDecl>
                    <index>       0:Int </index>
                    <mutability>  Mut:Mutability   </mutability>
                    <internal>    false            </internal>
                    <ty>          TYPE:Type        </ty>
                  </localDecl>
         )
         ...
       </localDecls> [owise]
```

#### Bindings declaration

Other bindings are declared by at their locations.

ATTENTION: this initialization routine only works if the mir file has a single function!

TODO: initialize `Mutability` basing in syntax, for now it's just declared as `Not` (immutable)
TODO: figure out how to deal with duplicate bindings. For now, we overwrite them

```k
  syntax MirSimulation ::= #initBindings(BindingList)
  //-------------------------------------------------
  rule <k> #initBindings(.BindingList)               => .K ... </k>
  rule <k> #initBindings((let _MUT:OptMut LOCAL:Local : TYPE:Type ;):Binding REST:BindingList) => #initBindings(REST) ... </k>
       <localDecls>
         <localDecl>
           <index>      KEY              </index>
           <mutability> _ => Not         </mutability>
           <internal>   _ => false       </internal>
           <ty>         _:Type  => TYPE  </ty>
         </localDecl>
         ...
       </localDecls> requires KEY ==Int Local2Int(LOCAL)
  rule <k> #initBindings((let _MUT:OptMut LOCAL:Local : TYPE:Type ;):Binding REST:BindingList) => #initBindings(REST) ... </k>
       <localDecls>
         (.Bag => <localDecl>
                    <index>       Local2Int(LOCAL) </index>
                    <mutability>  Not:Mutability   </mutability>
                    <internal>    false            </internal>
                    <ty>          TYPE:Type        </ty>
                  </localDecl>
         )
         ...
       </localDecls> [owise]
```

#### Basic blocks declaration

ATTENTION: this initialization routine only works if the mir file has a single function!

```k
  syntax MirSimulation ::= #initBasicBlocks(BasicBlockList)
  //-------------------------------------------------------
  rule <k> #initBasicBlocks(.BasicBlockList)               => .K ... </k>
  rule <k> #initBasicBlocks(((NAME:BBName _:MaybeBBCleanup):BB : BODY:BasicBlockBody):BasicBlock REST:BasicBlockList) => #initBasicBlocks(REST) ... </k>
       <basicBlocks>
         <basicBlock>
           <bbName> KEY </bbName>
           <bbBody> _ => BODY:BasicBlockBody </bbBody>
         </basicBlock>
         ...
       </basicBlocks> requires KEY ==Int BBName2Int(NAME)
  rule <k> #initBasicBlocks(((NAME:BBName _:MaybeBBCleanup):BB : BODY:BasicBlockBody):BasicBlock REST:BasicBlockList) => #initBasicBlocks(REST) ... </k>
       <basicBlocks>
         (.Bag => <basicBlock>
                    <bbName> BBName2Int(NAME) </bbName>
                    <bbBody> BODY:BasicBlockBody </bbBody>
                  </basicBlock>
         )
         ...
       </basicBlocks> [owise]

```


```k
endmodule
```

