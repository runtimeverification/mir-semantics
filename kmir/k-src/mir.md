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
         (.Bag => <localDecl>
                    <index>       0:Int </index>
                    <mutability>  Mut:Mutability   </mutability>
                    <internal>    false            </internal>
                    <ty>          TYPE:Type        </ty>
                  </localDecl>
         )
         ...
       </localDecls>
```

#### Bindings declaration

Other bindings are declared by at their locations.

TODO: initialize `Mutability` basing in syntax, for now it's just declared as `Not` (immutable)

```k
  syntax MirSimulation ::= #initBindings(BindingList)
  //-------------------------------------------------
  rule <k> #initBindings(.BindingList)               => .K ... </k>
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
       </localDecls>
```

#### Basic blocks declaration

```k
  syntax MirSimulation ::= #initBasicBlocks(BasicBlockList)
  //-------------------------------------------------------

```


```k
endmodule
```

