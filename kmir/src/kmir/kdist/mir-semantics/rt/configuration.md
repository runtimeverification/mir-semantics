# KMIR Configuration

This is the configuration of a running program in the MIR semantics.

Essential parts of the configuration:
* the `k` cell to control the execution
* a `stack` of `StackFrame`s describing function calls and their data
* `currentFrame`, an unpacked version of the top of `stack`
* the `functions` map to look up function bodies when they are called
* the `memory` cell which abstracts allocated heap data

The entire program's return value (`retVal`) is held in a separate cell.

Besides the `caller` (to return to) and `dest` and `target` to specify where the return value should be written, a `StackFrame` includes information about the `locals` of the currently-executing function/item. Each function's code will only access local values (or heap data referenced by them). Local variables carry type information (see `RT-DATA`).

```k
requires "./value.md"

module KMIR-CONFIGURATION
  imports INT-SYNTAX
  imports BOOL-SYNTAX
  imports SET
  imports RT-VALUE-SYNTAX

  syntax RetVal ::= return( Value )
                  | "noReturn"

  syntax StackFrame ::= StackFrame(caller:Ty,                 // index of caller function
                                   dest:Place,                // place to store return value
                                   target:MaybeBasicBlockIdx, // basic block to return to
                                   UnwindAction,              // action to perform on panic
                                   locals:List)               // return val, args, local variables

  configuration <kmir>
                  <k> $PGM:KItem </k>
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
                  // set of function names to break on when called
                  <breakOnFunctions> .Set </breakOnFunctions>
                </kmir>
```

Additional fields of the configuration contain _static_ information.

* The function store mapping `Ty` to `MonoItemFn` (and `IntrinsicFn`). This is essentially the entire program.
* The allocation store, mapping `AllocId` to `Value` (or error markers if undecoded)
* The type metadata map, associating `Ty` with a `TypeInfo` (which may contain more `Ty`s)
* The mapping from `AdtDef` ID to `Ty`

For better performance, this information is reified to K functions,
rather than carrying static `Map` structures with the configuration.

The functions are defined in the `RT-VALUE` module for now but should have their own module.

```k
endmodule
```
