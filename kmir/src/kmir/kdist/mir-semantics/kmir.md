# MIR Semantics in K

```k
requires "kmir-ast.md"
```

## Syntax of MIR in K

The MIR syntax is largely defined in [KMIR-AST](./kmir-ast.md) and its
submodules. The execution is initialised based on a loaded `Pgm` read
from a json format of stable-MIR.

```k
module KMIR-SYNTAX
  imports KMIR-AST
  imports INT-SYNTAX
  imports FLOAT-SYNTAX

  syntax KItem ::= #init( Pgm )

////////////////////////////////////////////
// FIXME things below related to memory and
// should maybe move to their own module.

  syntax Value ::= Scalar( Int, Int, Bool )
                   // value, bit-width, signedness   for bool, un/signed int
                 | Float( Float, Int )
                   // value, bit-width               for f16-f128
                 | Ptr( Address, MaybeValue ) // FIXME why maybe? why value?
                   // address, metadata              for ref/ptr
                 | Range( List )
                   // homogenous values              for array/slice
                 | Struct( Int, List )
                   // heterogenous value list        for tuples and structs (standard, tuple, or anonymous)
                 | "Any"
                   // arbitrary value                for transmute/invalid ptr lookup

  syntax MaybeValue ::= Value
                      | "NoValue"

  syntax Address // FIXME essential to the memory model, leaving it unspecified for now

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

```k
module KMIR-CONFIGURATION
  imports KMIR-SYNTAX
  imports INT-SYNTAX

  syntax RetVal ::= "NoRetVal"
                  | Int // FIXME is this enough?

  syntax StackFrame ::= StackFrame(caller:Int,    // index of caller function
                                   dest:Place,    // place to store return value
                                   target:Int,    // basic block to return to
                                   UnwindAction,  // action to perform on panic
                                   locals:List)   // return val, args, local variables

  configuration <kmir>
                  <k> #init($PGM:Pgm) </k>
                  <retVal> NoRetVal </retVal>
                  <currentFunc> defId(-1) </currentFunc> // necessary to retrieve caller
                  // unpacking the top frame to avoid frequent stack read/write operations
                  <currentFrame>
                    <currentBody> .BasicBlocks </currentBody>
                    <caller> defId(-1) </caller>
                    <dest> place(local(-1), .ProjectionElems)</dest>
                    <target> -1 </target>
                    <unwind> unwindActionUnreachable </unwind>
                    <locals> .List </locals>
                  </currentFrame>
                  // remaining call stack (without top frame)
                  <stack> .List </stack>
                  // FIXME where do we put the "GlobalAllocs"? in the heap, presumably?
                  // function store, Int -> Body
                  <functions> .Map </functions>
                  // heap
                  <memory> .Map </memory> // FIXME unclear how to model
                </kmir>
endmodule
```

### Execution Control Flow

```k
module KMIR
  imports KMIR-SYNTAX
  imports KMIR-CONFIGURATION
  imports MONO

  imports BOOL
  imports MAP
  imports K-EQUAL
```

Execution of a program begins by creating a stack frame for the `main`
function and executing its function body. Before execution begins, the
function map and the initial memory have to be set up.

```k
  // #init step, assuming a singleton in the K cell
  rule <k> #init(_Name:Symbol _Allocs:GlobalAllocs Items:MonoItems)
         =>
           #execMain(#findMainItem(Items))
       </k>
       <functions> _ => #mkFunctionMap(Items) </functions>
```

The `Map` of `functions` is keyed on the `DefId` of each `MonoItemFn`
found in the `MonoItems` of the program. The function _names_ are
not relevant for execution and therefore dropped.

```k
  syntax Map ::= #mkFunctionMap ( MonoItems )       [ function, total ]
               | #accumFunctions ( Map, MonoItems ) [ function, total ]

  rule #mkFunctionMap(Items) => #accumFunctions(.Map, Items)

  // accumulate function map discarding duplicate IDs
  rule #accumFunctions(Acc, .MonoItems) => Acc

  rule #accumFunctions(Acc, monoItem(_, monoItemFn(_, Id, Body)) Rest:MonoItems)
     =>
       #accumFunctions(Acc (Id |-> Body), Rest)
    requires notBool (Id in_keys(Acc))
    [ preserves-definedness ] // key collisions checked

  // discard other items and duplicate IDs
  rule #accumFunctions(Acc, _:MonoItem Rest:MonoItems)
     =>
       #accumFunctions(Acc, Rest)
    [ owise ]
```

Executing the `main` function means to create the `currentFrame` data
structure from its function body and then execute the first basic
block of the body.

```k
  // `main` is found through its MonoItemFn.name
  syntax MonoItemKind ::= #findMainItem ( MonoItems ) [ function ]

  rule #findMainItem( monoItem(_, monoItemFn(NAME, ID, BODY)) _ )
     =>
       monoItemFn(NAME, ID, BODY)
    requires NAME ==K symbol("main")
  rule #findMainItem( _:MonoItem Rest:MonoItems )
     =>
       #findMainItem(Rest)
    [owise]
  // rule #findMainItem( .MonoItems ) => error!

  syntax KItem ::= #execMain ( MonoItemKind )

  // NB differs from arbitrary function execution only by not pushing a stack frame
  rule <k> #execMain(monoItemFn(_, ID, body(FIRST:BasicBlock _ #as BLOCKS, LOCALS, _, _, _, _) .Bodies))
         =>
           #execBlock(FIRST)
         ...
       </k>
       <currentFunc> _ => ID </currentFunc>
       <currentFrame>
         <currentBody> _ => BLOCKS </currentBody>
         <caller> _ => defId(-1) </caller>
         <dest> _ => place(local(-1), .ProjectionElems)</dest>
         <target> _ => -1 </target>
         <unwind> _ => unwindActionUnreachable </unwind> // FIXME
         <locals> _ => #reserveFor(LOCALS)  </locals>
       </currentFrame>

  syntax List ::= #reserveFor( LocalDecls ) [function, total]
                  // basically `replicate (length LOCALS) Any`

  rule #reserveFor(.LocalDecls) => .List

  rule #reserveFor(_:LocalDecl REST:LocalDecls) => ListItem(Any) #reserveFor(REST)
```

```k
  // execution of blocks (composed of statements and terminator)
  syntax KItem ::= #execBlock ( BasicBlock )
                 | #execStmts ( Statements )
                 | #execStmt ( Statement )
                 | #execTerminator ( Terminator )


  // all memory accesses relegated to another module (to be added)

endmodule
```
