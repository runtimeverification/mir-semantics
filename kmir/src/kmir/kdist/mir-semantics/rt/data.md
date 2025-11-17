# Handling Data for MIR Execution

This module addresses all aspects of handling "values" i.e., data, at runtime during MIR execution.


```k
requires "../body.md"
requires "../ty.md"
requires "./types.md"
requires "./value.md"
requires "./numbers.md"
requires "./decoding.md"

module RT-DATA
  imports INT
  imports FLOAT
  imports BOOL
  imports BYTES
  imports LIST
  imports MAP
  imports K-EQUAL

  imports BODY
  imports TYPES

  imports RT-VALUE-SYNTAX
  imports RT-NUMBERS
  imports RT-DECODING
  imports RT-TYPES
  imports KMIR-CONFIGURATION

```

## Operations on local variables

### Indexing into the List of Local Variables in a Stack Frame

The semantics uses lists for stack frames and locals.
More often than not, an element of the list must be selected by index and is required to be of a certain sort.
In case of the `<locals>`, we only expect `TypedLocal` to be in the list, and use a dedicated indexing function.
The same holds for lists used as arguments in the `Value` sort.

```k
  syntax TypedLocal ::= getLocal ( List, Int ) [function]
  // ----------------------------------------------
  rule getLocal(LOCALS, IDX) => {LOCALS[IDX]}:>TypedLocal
    requires 0 <=Int IDX andBool IDX <Int size(LOCALS)
     andBool isTypedLocal(LOCALS[IDX])
     [preserves-definedness] // valid indexing and sort coercion checked

  // indexing values out of TypedValue and Value lists
  syntax Value ::= getValue ( List, Int ) [function]
  // ----------------------------------------------
  rule getValue(LOCALS, IDX) => {valueOf({LOCALS[IDX]}:>TypedValue)}:>Value
    requires 0 <=Int IDX andBool IDX <Int size(LOCALS)
     andBool isTypedValue(LOCALS[IDX])
     andBool isValue(valueOf({LOCALS[IDX]}:>TypedValue))
     [preserves-definedness] // valid indexing and sort coercion checked

  rule getValue(VALUES, IDX) => {VALUES[IDX]}:>Value
    requires 0 <=Int IDX andBool IDX <Int size(VALUES)
     andBool isValue(VALUES[IDX])
     [preserves-definedness] // valid indexing and sort coercion checked
```

To ensure the sort coercions above do not cause any harm, some definedness-related rules are added here:

```k
  // data coerced to sort TypedLocal is not undefined if it is of that sort
  rule #Ceil({X}:>TypedLocal) => #Ceil(X)
    requires isTypedLocal(X)                         [simplification]

  // data coerced to sort Value is not undefined if it is of that sort
  rule #Ceil({X}:>Value) => #Ceil(X)
    requires isValue(X)                              [simplification]
```

### Evaluating Items to `Value`s

Many rules for MIR constructs in this module use heating and cooling
to evaluate expressions to results or read local variables as operands.
The `Evaluation` sort gathers all constructs that can evaluate to a `Value`, defined together with `Value`.

First, a `TypedValue` stored in a local is trivially rewritten to `Value` by projecting out the value.
It is an error to read `NewLocal` or `Moved`.

```k
  syntax Evaluation ::= TypedValue

  rule <k> typedValue(VAL, _, _) => VAL ... </k> [priority(100)]
```

Other subsorts of `Evaluation` are defined when first used.

### `thunk`

We also create a subsort of `Value` that is a `thunk` which takes an `Evaluation` as an argument.
The `thunk` captures any `Evaluation` that we cannot make further progress on, and turns that into a `Value` so that we may continue execution (instead of getting stuck).
In particular, if we have pointer arithmetic with abstract pointers (not able to be resolved into concrete ints/bytes directly), then it will wrapper the operations in a `thunk`.
It is also useful to capture unimplemented semantic constructs so that we can have test / proof driven development.

```k
  syntax Value ::= thunk ( Evaluation )

  rule [thunk]: <k> EV:Evaluation => thunk(EV) ... </k> requires notBool isValue(EV) andBool notBool isTypedValue(EV) [owise]
```

### Errors Related to Accessing Local Variables

Access to a `TypedLocal` (whether reading or writing) may fail for a number of reasons.
It is an error to read a `Moved` local or an uninitialised `NewLocal`.
Also, locals are accessed via their index in list `<locals>` in a stack frame, which may be out of bounds (but the compiler should guarantee that all local indexes are valid).
Types (`Ty`, an opaque number assigned by the Stable MIR extraction) are not checked, the local's type is used.

### Reading Operands (Local Variables and Constants)

```k
  syntax Evaluation ::= Operand
```

_Read_ access to `Operand`s (which may be local values) may have similar errors as write access.

Constant operands are simply decoded according to their type.

```k
  rule <k> operandConstant(constOperand(_, _, mirConst(KIND, TY, _)))
        => #decodeConstant(KIND, TY, lookupTy(TY))
       ...
       </k>
    requires typeInfoVoidType =/=K lookupTy(TY)
```

### Copying and Moving

When an operand is `Copied` by a read, the original remains valid (see `false` passed to `#readProjection`).
We ensure that any projections of the copy operation are traversed appropriately before performing the read.

```k
  rule <k> operandCopy(place(local(I), PROJECTIONS))
        => #traverseProjection(toLocal(I), getValue(LOCALS, I), PROJECTIONS, .Contexts)
        ~> #readProjection(false)
        ...
       </k>
       <locals> LOCALS </locals>
    requires 0 <=Int I andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])
    [preserves-definedness] // valid list indexing checked
```

When an operand is `Moved` by the read, the original has to be invalidated.
In case of a projected value, this is a write operation nested in the data that is being read.
In contrast to regular write operations, the value does not have to be _mutable_ in order for `Moved` to be written (`true` is passed to `#readProjection`).

```k
  rule <k> operandMove(place(local(I), PROJECTIONS))
        => #traverseProjection(toLocal(I), getValue(LOCALS, I), PROJECTIONS, .Contexts)
        ~> #readProjection(true)
       ...
       </k>
       <locals> LOCALS </locals>
    requires 0 <=Int I andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])
    [preserves-definedness] // valid list indexing checked
```

### Setting Local Variables

The `#setLocalValue` operation writes a `Value` value to a given `Place` within the `List` of local variables currently on top of the stack.
This may fail because a local may not be accessible or not mutable.
If we are setting a value at a `Place` which has `Projection`s in it, then we must first traverse the projections before setting the value.
A variant `#forceSetLocal` is provided for setting the local value without checking the mutability of the location.

```k
  syntax KItem ::= #setLocalValue( Place, Evaluation ) [strict(2)]
                 | #forceSetLocal ( Local , Evaluation ) [strict(2)]

  rule <k> #setLocalValue(place(local(I), .ProjectionElems), VAL) => .K ... </k>
       <locals>
          LOCALS => LOCALS[I <- typedValue(VAL, tyOfLocal(getLocal(LOCALS, I)), mutabilityMut)]
       </locals>
    requires 0 <=Int I andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])
     andBool mutabilityOf(getLocal(LOCALS, I)) ==K mutabilityMut
    [preserves-definedness] // valid list indexing checked

  rule <k> #setLocalValue(place(local(I), .ProjectionElems), VAL) => .K ... </k>
       <locals>
          LOCALS => LOCALS[I <- typedValue(VAL, tyOfLocal(getLocal(LOCALS, I)), mutabilityOf(getLocal(LOCALS, I)))]
       </locals>
    requires 0 <=Int I andBool I <Int size(LOCALS)
     andBool isNewLocal(LOCALS[I])
    [preserves-definedness] // valid list indexing checked

  rule <k> #setLocalValue(place(local(I), PROJ), VAL)
        => #traverseProjection(toLocal(I), getValue(LOCALS, I), PROJ, .Contexts)
        ~> #writeProjection(VAL)
       ...
       </k>
       <locals> LOCALS </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool PROJ =/=K .ProjectionElems
     andBool isTypedValue(LOCALS[I])
    [preserves-definedness] // valid list indexing and sort checked

  rule <k> #forceSetLocal(local(I), MBVAL:Value) => .K ... </k>
       <locals> LOCALS => LOCALS[I <- typedValue(MBVAL, tyOfLocal(getLocal(LOCALS, I)), mutabilityOf(getLocal(LOCALS, I)))] </locals>
    requires 0 <=Int I andBool I <Int size(LOCALS)
     andBool isTypedLocal(LOCALS[I])
    [preserves-definedness] // valid list indexing checked
```

### Traversing Projections for Reads and Writes

A `Place` to read from or write to is a `Local` variable (actually just its index), and a (potentially empty) vector of `ProjectionElem`ents.

There are different kinds of `ProjectionElem`s:
- `Deref`erencing references or pointers (or `Box`es allocated in the heap)
  - read data at the address given in the local
  - operates on a value that is a pointer or reference to another
- `Field` access in struct.s and tuples
  - fields are numbered from zero (in source order). The field type is also given.
  - operates on structs and tuples
- `Index`ing into arrays or slices
  - operates on a value that is an array (statically-known size) or slice (variable size)
  - indexes zero-based from the front
  - the index is provided in another local
- `ConstantIndex`ing with a constant offset
  - operates on a value that is an array (statically-known size) or slice (variable size)
  - the index was statically known and is therefore a `u64`
  - the `min_length` of the object to index into is provided as another `u64`
  - when `from_end` is true, this is  taken to be exact, and indexing happens from the end
- `Subslice`
  - a slice from `from` to `to` (the latter either from start or `from_end`)
  - operates on a value that is an array (statically-known size) or slice (variable size)
- Casting values (`OpaqueCast` or `Downcast` - variant narrowing) and `Subtype`ing

Read and write operations to places that include (a chain of) projections are handled by a special rewrite symbol `#traverseProjection`.
This helper does the projection lookup and maintains the context chain along the lookup path, then passes control back to `#readProjection` and `#writeProjection`/`#setMoved`.
A `Deref` projection in the projections list changes the target of the write operation, while `Field` updates change the value that is being written (updating just one field of it), recursively.

```k
  syntax KItem ::= #traverseProjection ( WriteTo , Value, ProjectionElems, Contexts )
                 | #readProjection ( Bool )
                 | #writeProjection ( Value )
                 | "#writeMoved"

  rule <k> #traverseProjection(_, VAL, .ProjectionElems, _) ~> #readProjection(false) => VAL ... </k>
  rule <k> #traverseProjection(_, VAL, .ProjectionElems, _) ~> (#readProjection(true) => #writeMoved ~> VAL) ... </k>

  rule <k> #traverseProjection(toLocal(I), _ORIGINAL, .ProjectionElems, CONTEXTS)
        ~> #writeProjection(NEW)
        => #setLocalValue(place(local(I), .ProjectionElems), #buildUpdate(NEW, CONTEXTS))
       ...
       </k>
     [preserves-definedness] // valid context ensured upon context construction

  rule <k> #traverseProjection(toLocal(I), _ORIGINAL, .ProjectionElems, CONTEXTS)
        ~> #writeMoved
        => #forceSetLocal(local(I), #buildUpdate(Moved, CONTEXTS)) // TODO retain Ty and Mutability from _ORIGINAL
       ...
       </k>
     [preserves-definedness] // valid context ensured upon context construction

  rule <k> #traverseProjection(toStack(FRAME, local(I)), _ORIGINAL, .ProjectionElems, CONTEXTS)
        ~> #writeProjection(NEW)
        => .K
        ...
       </k>
       <stack> STACK
            => STACK[(FRAME -Int 1) <-
                      #updateStackLocal(
                        {STACK[FRAME -Int 1]}:>StackFrame,
                        I,
                        #adjustRef(#buildUpdate(NEW, CONTEXTS), 0 -Int FRAME)
                      )
                    ]
       </stack>
    requires 0 <Int FRAME andBool FRAME <=Int size(STACK)
     andBool isStackFrame(STACK[FRAME -Int 1])
     [preserves-definedness] // valid context ensured upon context construction

  rule <k> #traverseProjection(toStack(FRAME, local(I)), _ORIGINAL, .ProjectionElems, CONTEXTS)
        ~> #writeMoved
        => .K
        ...
       </k>
       <stack> STACK
            => STACK[(FRAME -Int 1) <-
                      #updateStackLocal(
                        {STACK[FRAME -Int 1]}:>StackFrame,
                        I,
                        #adjustRef(#buildUpdate(Moved, CONTEXTS), 0 -Int FRAME)
                      ) // TODO retain Ty and Mutability from _ORIGINAL
                    ]
       </stack>
    requires 0 <Int FRAME andBool FRAME <=Int size(STACK)
     andBool isStackFrame(STACK[FRAME -Int 1])
     [preserves-definedness] // valid context ensured upon context construction

  // allocations should not be written to, therefore no rule for `toAlloc`
```

These helpers mark down, as we traverse the projection, what `Place` we are currently looking up in the traversal.
`#buildUpdate` helps to reconstruct the new value stored at that `Place` if we need to do a write (using the `Context` built during traversal).

```k
  // stores the target of the write operation, which may change when references are dereferenced.
  syntax WriteTo ::= toLocal ( Int )
                   | toStack ( Int , Local )
                   | toAlloc ( AllocId )

  // retains information about the value that was deconstructed by a projection
  syntax Context ::= CtxField( VariantIdx, List, Int , Ty )
                   | CtxIndex( List , Int ) // array index constant or has been read before
                   | CtxSubslice( List , Int , Int ) // start and end always counted from beginning
                   | CtxPointerOffset( List, Int, Int ) // pointer offset for accessing elements with an offset (Offset, Origin Length)

  syntax ProjectionElem ::= PointerOffset( Int, Int ) // Same as subslice but coming from BinopOffset injected by us

  syntax Contexts ::= List{Context, ""}

  syntax Value ::= #buildUpdate ( Value , Contexts ) [function]
  // ----------------------------------------------------------
  rule #buildUpdate(VAL, .Contexts) => VAL
     [preserves-definedness]

  rule #buildUpdate(VAL, CtxField(IDX, ARGS, I, _) CTXS)
      => #buildUpdate(Aggregate(IDX, ARGS[I <- VAL]), CTXS)
     [preserves-definedness] // valid list indexing checked upon context construction

  rule #buildUpdate(VAL, CtxIndex(ELEMS, I) CTXS)
      => #buildUpdate(Range(ELEMS[I <- VAL]), CTXS)
     [preserves-definedness] // valid list indexing checked upon context construction

  // we don't expect an update to happen on an entire _subslice_ but define a rule for it anyway
  rule #buildUpdate(Range(INNER), CtxSubslice(ELEMS, START, END) CTXS)
      => #buildUpdate( Range(updateList(ELEMS, START, INNER)), CTXS)
    requires size(INNER) ==Int END -Int START // ensures updateList is defined
     [preserves-definedness] // START,END indexes checked before, length check for update here

  // Update PointerOffset
  rule #buildUpdate(Range(INNER), CtxPointerOffset(ELEMS, START, END) CTXS)
      => #buildUpdate( Range(updateList(ELEMS, START, INNER)), CTXS)
    requires size(INNER) ==Int END -Int START // ensures updateList is defined
     [preserves-definedness] // START,END indexes checked before, length check for update here

  syntax StackFrame ::= #updateStackLocal ( StackFrame, Int, Value ) [function]

  rule #updateStackLocal(StackFrame(CALLER, DEST, TARGET, UNWIND, LOCALS), I, VAL)
      => StackFrame(CALLER, DEST, TARGET, UNWIND, LOCALS[I <- typedValue(VAL, tyOfLocal(getLocal(LOCALS, I)), mutabilityMut)])
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isTypedLocal(LOCALS[I])
    [preserves-definedness] // valid list indexing and sort checked

  syntax ProjectionElems ::= appendP ( ProjectionElems , ProjectionElems ) [function, total]
  rule appendP(.ProjectionElems, TAIL) => TAIL
  rule appendP(X:ProjectionElem REST:ProjectionElems, TAIL) => X appendP(REST, TAIL)

  syntax Value ::= #localFromFrame ( StackFrame, Local, Int ) [function]

  rule #localFromFrame(StackFrame(... locals: LOCALS), local(I:Int), OFFSET) => #adjustRef(getValue(LOCALS, I), OFFSET)
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])
    [preserves-definedness] // valid list indexing checked

  syntax Value ::= #adjustRef (Value, Int ) [function, total]
  // --------------------------------------------------------
  rule #adjustRef(Reference(HEIGHT, PLACE, REFMUT, META), OFFSET)
    => Reference(HEIGHT +Int OFFSET, PLACE, REFMUT, META)
  rule #adjustRef(PtrLocal(HEIGHT, PLACE, REFMUT, META), OFFSET)
    => PtrLocal(HEIGHT +Int OFFSET, PLACE, REFMUT, META)
  rule #adjustRef(Aggregate(IDX, ARGS), OFFSET)
    => Aggregate(IDX, #mapOffset(ARGS, OFFSET))
  rule #adjustRef(Range(ELEMS), OFFSET)
    => Range(#mapOffset(ELEMS, OFFSET))
  rule #adjustRef(TL, _) => TL [owise]

  syntax List ::= #mapOffset ( List, Int ) [function, total]
  // -------------------------------------------------------
  rule #mapOffset(.List, _)
    => .List
  rule #mapOffset(ListItem(ELEM:Value) REST, OFFSET)
    => ListItem(#adjustRef(ELEM, OFFSET)) #mapOffset(REST, OFFSET)
  rule #mapOffset(OTHER, _)
    => OTHER [owise] // should not happen

  syntax Value ::= #incrementRef ( Value )  [function, total]
                 | #decrementRef ( Value )  [function, total]
  // --------------------------------------------------------
  rule #incrementRef(TL) => #adjustRef(TL, 1)
  rule #decrementRef(TL) => #adjustRef(TL, -1)

  syntax Int ::= originSize ( MetadataSize ) [function, total]
  // ---------------------------------------------------------------------
  rule originSize(noMetadataSize) => 0 // TODO: Is this fair, noMetadataSize does not really mean zero
  rule originSize(staticSize(SIZE)) => SIZE
  rule originSize(dynamicSize(SIZE)) => SIZE
```

#### Aggregates

A `Field` access projection operates on `struct`s and tuples, which are represented as `Aggregate` values.
The field is numbered from zero (in source order), and the field type is provided (not checked here).

A `Downcast` projection operates on an `enum` (represented as an `Aggregate`), and interprets the fields stored in the `Aggregate` as belonging to the variant given in the `Downcast` (by setting the `variantIdx` of the `Aggregate` accordingly).
This is done without consideration of the validity of the Downcast[^downcast].

[^downcast]: See discussion in https://github.com/rust-lang/rust/issues/93688#issuecomment-1032929496.

```k
  rule <k> #traverseProjection(
             DEST,
             Aggregate(IDX, ARGS),
             projectionElemField(fieldIdx(I), TY) PROJS,
             CTXTS
           )
        => #traverseProjection(
             DEST,
             getValue(ARGS, I),
             PROJS,
             CtxField(IDX, ARGS, I, TY) CTXTS
           )
        ...
        </k>
    requires 0 <=Int I andBool I <Int size(ARGS)
     andBool isValue(ARGS[I])
    [preserves-definedness] // valid list indexing checked

  rule <k> #traverseProjection(
             DEST,
             Aggregate(_, ARGS),
             projectionElemDowncast(IDX) PROJS,
             CTXTS
           )
        => #traverseProjection(
             DEST,
             Aggregate(IDX, ARGS),
             PROJS,
             CTXTS
           )
       ...
       </k>
```

#### Ranges

An `Index` projection operates on an array or slice (`Range`) value, to access an element of the array.
The index can either be read from another operand, or it can be a constant (`ConstantIndex`).
For a normal `Index` projection, the index is read from a given local which is expected to hold a `usize` value in the valid range between 0 and the array/slice length.
In case of a `ConstantIndex`, the index is provided as an immediate value, together with a "minimum length" of the array/slice and a flag indicating whether indexing should be performed from the end (in which case the minimum length must be exact).

```k
  rule <k> #traverseProjection(
             DEST,
             Range(ELEMENTS),
             projectionElemIndex(local(LOCAL)) PROJS,
             CTXTS
           )
        => #traverseProjection(
             DEST,
             getValue(ELEMENTS, #expectUsize(getValue(LOCALS, LOCAL))),
             PROJS,
             CtxIndex(ELEMENTS, #expectUsize(getValue(LOCALS, LOCAL))) CTXTS
           )
        ...
        </k>
        <locals> LOCALS </locals>
    requires 0 <=Int LOCAL andBool LOCAL <Int size(LOCALS)
     andBool isTypedValue(LOCALS[LOCAL])
     andBool isInt(#expectUsize(getValue(LOCALS, LOCAL)))
     andBool 0 <=Int #expectUsize(getValue(LOCALS, LOCAL)) andBool #expectUsize(getValue(LOCALS, LOCAL)) <Int size(ELEMENTS)
     andBool isValue(ELEMENTS[#expectUsize(getValue(LOCALS, LOCAL))])
    [preserves-definedness] // index checked, valid Int can be read, ELEMENT indexable and writeable or forced

  rule <k> #traverseProjection(
             DEST,
             Range(ELEMENTS),
             projectionElemConstantIndex(OFFSET:Int, _MINLEN, false) PROJS,
             CTXTS
           )
        => #traverseProjection(
             DEST,
             getValue(ELEMENTS, OFFSET),
             PROJS,
             CtxIndex(ELEMENTS, OFFSET) CTXTS
           )
        ...
        </k>
    requires 0 <=Int OFFSET andBool OFFSET <Int size(ELEMENTS)
     andBool isValue(ELEMENTS[OFFSET])
    [preserves-definedness] // ELEMENT indexable and writeable or forced

  rule <k> #traverseProjection(
             DEST,
             Range(ELEMENTS),
             projectionElemConstantIndex(OFFSET:Int, MINLEN, true) PROJS, // from end
             CTXTS
           )
        => #traverseProjection(
             DEST,
             getValue(ELEMENTS, OFFSET),
             PROJS,
             CtxIndex(ELEMENTS, MINLEN -Int OFFSET) CTXTS
           )
        ...
        </k>
    requires 0 <Int OFFSET andBool OFFSET <=Int MINLEN
     andBool MINLEN ==Int size(ELEMENTS) // assumed for valid MIR code
     andBool isValue(ELEMENTS[MINLEN -Int OFFSET])
    [preserves-definedness] // ELEMENT indexable and writeable or forced

  syntax Int ::= #expectUsize ( Value ) [function]

  rule #expectUsize(Integer(I, 64, false)) => I
```

A `Subslice` projection operates on an array or slice (`Range`) value to extract a slice of the array from a start index to an end index (exclusive) [^subslice].
Start and end index are given as immediate values.
Similar to `ConstantIndex`, the slice _end_ index may count from the _end_  or the start of the array if flagged as such.

[^subslice]: https://doc.rust-lang.org/nightly/nightly-rustc/rustc_middle/mir/type.ProjectionKind.html#variant.Subslice

```k
  rule <k> #traverseProjection(
             DEST,
             Range(ELEMENTS),
             projectionElemSubslice(START, END, false) PROJS,
             CTXTS
           )
        => #traverseProjection(
             DEST,
             Range(range(ELEMENTS, START, size(ELEMENTS) -Int END)),
             PROJS,
             CtxSubslice(ELEMENTS, START, END) CTXTS
           )
        ...
        </k>
    requires 0 <=Int START andBool START <=Int size(ELEMENTS)
     andBool 0 <Int END andBool END <=Int size(ELEMENTS)
     andBool START <Int END
    [preserves-definedness] // Indexes checked to be in range for ELEMENTS

  rule <k> #traverseProjection(
             DEST,
             Range(ELEMENTS),
             projectionElemSubslice(START, END, true) PROJS, // END from end of ELEMS
             CTXTS
           )
        => #traverseProjection(
             DEST,
             Range(range(ELEMENTS, START, END)),
             PROJS,
             CtxSubslice(ELEMENTS, START, size(ELEMENTS) -Int END) CTXTS
           )
        ...
        </k>
    requires 0 <=Int START andBool START <=Int size(ELEMENTS)
     andBool 0 <=Int END andBool END <Int size(ELEMENTS)
     andBool START <=Int size(ELEMENTS) -Int END
    [preserves-definedness] // Indexes checked to be in range for ELEMENTS

  rule <k> #traverseProjection(
             DEST,
             Range(ELEMENTS),
             PointerOffset(OFFSET, _ORIGIN_LENGTH) PROJS, // TODO: seems strange to not use the ORIGIN_LENGTH...
             CTXTS
           )
        => #traverseProjection(
             DEST,
             Range(range(ELEMENTS, OFFSET, 0)),
             PROJS,
             CtxPointerOffset(ELEMENTS, OFFSET, size(ELEMENTS)) CTXTS
           )
        ...
        </k>
    requires 0 <=Int OFFSET andBool OFFSET <=Int size(ELEMENTS)
    [preserves-definedness] // Offset checked to be in range for ELEMENTS
```

#### References

A `Deref` projection operates on `Reference`s or pointers (`PtrLocal`) that refer to locals in the same or
an enclosing stack frame, indicated by the stack height in the value.
`Deref` reads the referred place (and may proceed with further projections).
In the simplest case, the reference refers to a local in the same stack frame (height 0), which is directly read.
If the offset height is greater than zero, the stack element is accessed.

Pointers and references may carry metadata indicating a _size_ (`dynamicSize`).
If present, the `Deref` is expected to access a _slice_ and the size determines how many elements are read from it.

An attempt to read more elements than the length of the accessed array is undefined behaviour and halts the execution.

```k
  // helper rewrite to implement truncating slices to required size
  syntax KItem ::= #derefTruncate ( MetadataSize , ProjectionElems )
  // ----------------------------------------------------------------------------------------
  // values other than `Range` do not have metadata anyway, they are passed along unchanged
  rule <k> #traverseProjection( DEST,         VAL                , .ProjectionElems, CTXTS) ~> #derefTruncate(noMetadataSize, PROJS)
        => #traverseProjection(DEST, VAL, PROJS, CTXTS)
        ...
       </k>
    requires notBool isRange(VAL)

  // TODO move these to value.md
  syntax Bool ::= isRange ( Value ) [function, total]
  // ------------------------------------------------
  rule isRange(Range(_)) => true
  rule isRange( _OTHER ) => false [owise]

  // staticSize metadata requires an array of suitable length and truncates it
  rule <k> #traverseProjection( DEST, Range(ELEMS), .ProjectionElems, CTXTS) ~> #derefTruncate(staticSize(SIZE), PROJS)
        => #traverseProjection(DEST, Range(range(ELEMS, 0, size(ELEMS) -Int SIZE)), PROJS, CTXTS)
        ...
       </k>
    requires 0 <=Int SIZE andBool SIZE <=Int size(ELEMS) [preserves-definedness] // range parameters checked
  // dynamicSize metadata requires an array of suitable length and truncates it
  rule <k> #traverseProjection( DEST, Range(ELEMS), .ProjectionElems, CTXTS) ~> #derefTruncate(dynamicSize(SIZE), PROJS)
        => #traverseProjection(DEST, Range(range(ELEMS, 0, size(ELEMS) -Int SIZE)), PROJS, CTXTS)
        ...
       </k>
    requires 0 <=Int SIZE andBool SIZE <=Int size(ELEMS) [preserves-definedness] // range parameters checked
  // If an array was projected to but no metadata is available, use the head element
  rule <k> #traverseProjection( DEST, Range(ListItem(VAL) _:List), .ProjectionElems, CTXTS) ~> #derefTruncate(noMetadataSize, PROJS)
        => #traverseProjection(DEST, VAL, PROJS, CTXTS)
        ...
       </k>
    [preserves-definedness]

  // Ref, 0 < OFFSET, 0 < PTR_OFFSET, ToStack
  rule <k> #traverseProjection(
             _DEST,
             Reference(OFFSET, place(LOCAL, PLACEPROJ), _MUT, metadata(SIZE, PTR_OFFSET, ORIGIN_SIZE)),
             projectionElemDeref PROJS,
             _CTXTS
           )
        => #traverseProjection(
            toStack(OFFSET, LOCAL),
             #localFromFrame({STACK[OFFSET -Int 1]}:>StackFrame, LOCAL, OFFSET),
             appendP(PLACEPROJ, PointerOffset(PTR_OFFSET, originSize(ORIGIN_SIZE))), // apply reference projections with pointer offset
             .Contexts
           )
          ~> #derefTruncate(SIZE, PROJS) // then truncate, then continue with remaining projections
        ...
        </k>
        <stack> STACK </stack>
    requires 0 <Int OFFSET andBool OFFSET <=Int size(STACK)
     andBool isStackFrame(STACK[OFFSET -Int 1])
     andBool 0 <Int PTR_OFFSET
    [preserves-definedness]

  // Ref, 0 < OFFSET, 0 == PTR_OFFSET, ToStack
  rule <k> #traverseProjection(
             _DEST,
             Reference(OFFSET, place(LOCAL, PLACEPROJ), _MUT, metadata(SIZE, PTR_OFFSET, _ORIGIN_SIZE)),
             projectionElemDeref PROJS,
             _CTXTS
           )
        => #traverseProjection(
            toStack(OFFSET, LOCAL),
             #localFromFrame({STACK[OFFSET -Int 1]}:>StackFrame, LOCAL, OFFSET),
             PLACEPROJ, // apply reference projections with pointer offset
             .Contexts
           )
          ~> #derefTruncate(SIZE, PROJS) // then truncate, then continue with remaining projections
        ...
        </k>
        <stack> STACK </stack>
    requires 0 <Int OFFSET andBool OFFSET <=Int size(STACK)
     andBool isStackFrame(STACK[OFFSET -Int 1])
     andBool PTR_OFFSET ==Int 0
    [preserves-definedness]

  // Ref, 0 == OFFSET, 0 < PTR_OFFSET, Local
  rule <k> #traverseProjection(
             _DEST,
             Reference(OFFSET, place(local(I), PLACEPROJ), _MUT, metadata(SIZE, PTR_OFFSET, ORIGIN_SIZE)),
             projectionElemDeref PROJS,
             _CTXTS
           )
        => #traverseProjection(
             toLocal(I),
             getValue(LOCALS, I),
             appendP(PLACEPROJ, PointerOffset(PTR_OFFSET, originSize(ORIGIN_SIZE))), // apply reference projections with pointer offset
             .Contexts
           )
          ~> #derefTruncate(SIZE, PROJS) // then truncate, then continue with remaining projections
        ...
        </k>
        <locals> LOCALS </locals>
    requires OFFSET ==Int 0
     andBool 0 <=Int I andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])
     andBool 0 <Int PTR_OFFSET
    [preserves-definedness]

  // Ref, 0 == OFFSET, 0 == PTR_OFFSET, Local
  rule <k> #traverseProjection(
             _DEST,
             Reference(OFFSET, place(local(I), PLACEPROJ), _MUT, metadata(SIZE, PTR_OFFSET, _ORIGIN_SIZE)),
             projectionElemDeref PROJS,
             _CTXTS
           )
        => #traverseProjection(
             toLocal(I),
             getValue(LOCALS, I),
             PLACEPROJ,
             .Contexts
           )
          ~> #derefTruncate(SIZE, PROJS) // then truncate, then continue with remaining projections
        ...
        </k>
        <locals> LOCALS </locals>
    requires OFFSET ==Int 0
     andBool 0 <=Int I andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])
     andBool PTR_OFFSET ==Int 0
    [preserves-definedness]

  // Ptr, 0 < OFFSET, 0 < PTR_OFFSET, ToStack
  rule <k> #traverseProjection(
             _DEST,
             PtrLocal(OFFSET, place(LOCAL, PLACEPROJ), _MUT, metadata(SIZE, PTR_OFFSET, ORIGIN_SIZE)),
             projectionElemDeref PROJS,
             _CTXTS
           )
        => #traverseProjection(
            toStack(OFFSET, LOCAL),
             #localFromFrame({STACK[OFFSET -Int 1]}:>StackFrame, LOCAL, OFFSET),
             appendP(PLACEPROJ, PointerOffset(PTR_OFFSET, originSize(ORIGIN_SIZE))), // apply reference projections with pointer offset
             .Contexts // previous contexts obsolete
           )
          ~> #derefTruncate(SIZE, PROJS) // then truncate, then continue with remaining projections
        ...
        </k>
        <stack> STACK </stack>
    requires 0 <Int OFFSET andBool OFFSET <=Int size(STACK)
     andBool isStackFrame(STACK[OFFSET -Int 1])
     andBool 0 <Int PTR_OFFSET
    [preserves-definedness]

  // Ptr, 0 < OFFSET, 0 == PTR_OFFSET, ToStack
  rule <k> #traverseProjection(
             _DEST,
             PtrLocal(OFFSET, place(LOCAL, PLACEPROJ), _MUT, metadata(SIZE, PTR_OFFSET, _ORIGIN_SIZE)),
             projectionElemDeref PROJS,
             _CTXTS
           )
        => #traverseProjection(
            toStack(OFFSET, LOCAL),
             #localFromFrame({STACK[OFFSET -Int 1]}:>StackFrame, LOCAL, OFFSET),
             PLACEPROJ, // apply reference projections
             .Contexts // add pointer offset context
           )
          ~> #derefTruncate(SIZE, PROJS) // then truncate, then continue with remaining projections
         ...
        </k>
        <stack> STACK </stack>
    requires 0 <Int OFFSET andBool OFFSET <=Int size(STACK)
     andBool isStackFrame(STACK[OFFSET -Int 1])
     andBool PTR_OFFSET ==Int 0
    [preserves-definedness]

  // Ptr, 0 == OFFSET, 0 < PTR_OFFSET, Local
  rule <k> #traverseProjection(
             _DEST,
             PtrLocal(OFFSET, place(local(I), PLACEPROJ), _MUT, metadata(SIZE, PTR_OFFSET, ORIGIN_SIZE)),
             projectionElemDeref PROJS,
             _CTXTS
           )
        => #traverseProjection(
             toLocal(I),
             getValue(LOCALS, I),
             appendP(PLACEPROJ, PointerOffset(PTR_OFFSET, originSize(ORIGIN_SIZE))), // apply reference projections with pointer offset
             .Contexts // previous contexts obsolete
           )
          ~> #derefTruncate(SIZE, PROJS) // then truncate, then continue with remaining projections
        ...
        </k>
        <locals> LOCALS </locals>
    requires OFFSET ==Int 0
     andBool 0 <=Int I andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])
     andBool 0 <Int PTR_OFFSET
    [preserves-definedness]

  // Ptr, 0 == OFFSET, 0 == PTR_OFFSET, Local
  rule <k> #traverseProjection(
             _DEST,
             PtrLocal(OFFSET, place(local(I), PLACEPROJ), _MUT, metadata(SIZE, PTR_OFFSET, _ORIGIN_SIZE)),
             projectionElemDeref PROJS,
             _CTXTS
           )
        => #traverseProjection(
             toLocal(I),
             getValue(LOCALS, I),
             PLACEPROJ, // apply reference projections
             .Contexts // add pointer offset context
           )
          ~> #derefTruncate(SIZE, PROJS) // then truncate, then continue with remaining projections
        ...
        </k>
        <locals> LOCALS </locals>
    requires OFFSET ==Int 0
     andBool 0 <=Int I andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])
     andBool 0 ==Int PTR_OFFSET
    [preserves-definedness]
```

References also exist into the `<memory>` heap which is populated with allocated constants.
A reference to a statically allocated constant is typically never written to,
even though this could be supported.

```k
  rule <k> #traverseProjection(
             _DEST,
             AllocRef(ALLOC_ID, ALLOC_PROJS, metadata(METADATA_SIZE, _PTR_OFFSET, _)), // FIXME can this be offset?
             projectionElemDeref PROJS,
             _CTXTS
           )
        => #traverseProjection(
             toAlloc(ALLOC_ID),
             {lookupAlloc(ALLOC_ID)}:>Value,
             ALLOC_PROJS, // alloc projections
             .Contexts // previous contexts obsolete
           )
          ~> #derefTruncate(METADATA_SIZE, PROJS) // then truncate, then continue with remaining projections
        ...
        </k>
    requires isValue(lookupAlloc(ALLOC_ID))
    [preserves-definedness] // sort projection checked
```

## Evaluation of R-Values (`Rvalue` sort)

The `Rvalue` sort in MIR represents various operations that produce a value which can be assigned to a `Place`.

| RValue         | Arguments                                       | Action                               |
|----------------|-------------------------------------------------|--------------------------------------|
| Use            | Operand                                         | use (i.e., copy) operand unmodified  |
| Cast           | CastKind, Operand, Ty                           | different kinds of type casts        |
| Aggregate      | Box<AggregateKind>, IndexVec<FieldIdx, Operand> | `struct`, tuple, or array            |
| Repeat         | Operand, Const                                  | create array [Operand;Const]         |
| Len            | Place                                           | array or slice size                  |
| Ref            | Region, BorrowKind, Place                       | create reference to place            |
| ThreadLocalRef | DefId                                           | thread-local reference (?)           |
| AddressOf      | Mutability, Place                               | creates pointer to place             |
|----------------|-------------------------------------------------|--------------------------------------|
| BinaryOp       | BinOp, Box<(Operand, Operand)>                  | different fixed operations           |
| NullaryOp      | NullOp, Ty                                      | on ints, bool, floats                |
| UnaryOp        | UnOp, Operand                                   | (see below)                          |
|----------------|-------------------------------------------------|--------------------------------------|
| Discriminant   | Place                                           | discriminant (of sums types) (?)     |
| ShallowInitBox | Operand, Ty                                     |                                      |
| CopyForDeref   | Place                                           | use (copy) contents of `Place`       |

The most basic ones are simply accessing an operand, either directly or by way of a type cast.

```k
  syntax Evaluation ::= Rvalue

  rule <k> rvalueUse(OPERAND) => OPERAND ... </k>

  rule <k> rvalueCast(CASTKIND, operandCopy(place(local(I), PROJS)) #as OPERAND, TY)
        => #cast(OPERAND, CASTKIND, getTyOf(tyOfLocal({LOCALS[I]}:>TypedLocal), PROJS), TY) ... </k>
       <locals> LOCALS </locals>
    requires 0 <=Int I andBool I <Int size(LOCALS)
     andBool isTypedLocal(LOCALS[I])
    [preserves-definedness] // valid list indexing checked

  rule <k> rvalueCast(CASTKIND, operandMove(place(local(I), PROJS)) #as OPERAND, TY)
        => #cast(OPERAND, CASTKIND, getTyOf(tyOfLocal({LOCALS[I]}:>TypedLocal), PROJS), TY) ... </k>
       <locals> LOCALS </locals>
    requires 0 <=Int I andBool I <Int size(LOCALS)
     andBool isTypedLocal(LOCALS[I])
    [preserves-definedness] // valid list indexing checked

  rule <k> rvalueCast(CASTKIND, operandConstant(constOperand(_, _, mirConst(_, CONST_TY, _))) #as OPERAND, TY)
        => #cast(OPERAND, CASTKIND, CONST_TY, TY) ... </k>
```

A number of unary and binary operations exist, (which are dependent on the operand types).

```k
// BinaryOp, UnaryOp. NullaryOp: dependent on value representation. See below
```

### Arrays

Other `RValue`s exist in order to construct or operate on arrays and slices, which are built into the MIR language.
The `RValue::Repeat` creates and array of (statically) fixed length by repeating a given element value.
`RValue::Len` returns the length of an array or slice stored at a place.

```k
  syntax Evaluation ::= #mkArray ( Evaluation , Int ) [strict(1)]

  rule <k> rvalueRepeat(ELEM, tyConst(KIND, _)) => #mkArray(ELEM, readTyConstInt(KIND)) ... </k>
    requires isInt(readTyConstInt(KIND))
    [preserves-definedness]

  rule <k> #mkArray(ELEMENT:Value, N) => Range(makeList(N, ELEMENT)) ... </k>
    requires 0 <=Int N
    [preserves-definedness]


  // length of arrays or slices
  syntax Evaluation ::= #lengthU64 ( Evaluation ) [strict(1)]

  rule <k> rvalueLen(PLACE) => #lengthU64(operandCopy(PLACE)) ... </k>

  rule <k> #lengthU64(Range(LIST))
        =>
            Integer(size(LIST), 64, false)  // returns usize
        ...
       </k>
```

### Aggregates

Likewise built into the language are aggregates (tuples and `struct`s) and variants (`enum`s).
Besides their list of arguments, `enum`s also carry a `VariantIdx` indicating which variant was used.
For tuples and `struct`s, this index is always 0.

Tuples, `struct`s, and `enum`s are built as `Aggregate` values with a list of argument values.
For `enums`, the `VariantIdx` is set, and for `struct`s and `enum`s, the type ID (`Ty`) is retrieved from a special mapping of `AdtDef` to `Ty`.

Literal arrays are also built using this RValue.

```k
  rule <k> rvalueAggregate(KIND, ARGS) => #readOperands(ARGS) ~> #mkAggregate(KIND) ... </k>

  // #mkAggregate produces an aggregate TypedLocal value of given kind from a preceeding list of values
  syntax Value ::= #mkAggregate ( AggregateKind )

  rule <k> ARGS:List ~> #mkAggregate(aggregateKindAdt(_ADTDEF, VARIDX, _, _, _))
        =>
            Aggregate(VARIDX, ARGS)
        ...
       </k>

  rule <k> ARGS:List ~> #mkAggregate(aggregateKindArray(_TY))
        =>
            Range(ARGS)
        ...
       </k>


  rule <k> ARGS:List ~> #mkAggregate(aggregateKindTuple)
        =>
            Aggregate(variantIdx(0), ARGS)
        ...
       </k>


  // #readOperands accumulates a list of `TypedLocal` values from operands
  syntax KItem ::= #readOperands ( Operands )
                 | #readOperandsAux( List , Operands )
                 | #readOn( List, Operands )

  rule <k> #readOperands(ARGS) => #readOperandsAux(.List, ARGS) ... </k>

  rule <k> #readOperandsAux(ACC, .Operands ) => ACC ... </k>

  rule <k> #readOperandsAux(ACC, OP:Operand REST)
        =>
           OP ~> #readOn(ACC, REST)
        ...
       </k>

  rule <k> VAL:Value ~> #readOn(ACC, REST)
        =>
           #readOperandsAux(ACC ListItem(VAL), REST)
        ...
       </k>
```

The `AggregateKind::RawPtr`, somewhat as a special case of a `struct` aggregate, constructs a raw pointer
from a given data pointer and metadata[^rawPtrAgg]. In case of a _thin_ pointer, the metadata is a unit value,
for _fat_ pointers it is a `usize` value indicating the data length.

[^rawPtrAgg]: https://doc.rust-lang.org/nightly/nightly-rustc/rustc_middle/mir/enum.AggregateKind.html#variant.RawPtr

```k
  rule <k> ListItem(PtrLocal(OFFSET, PLACE, _, metadata(_SIZE, PTR_OFFSET, ORIGIN_SIZE))) ListItem(Integer(LENGTH, 64, false)) ~> #mkAggregate(aggregateKindRawPtr(_TY, MUT))
        => PtrLocal(OFFSET, PLACE, MUT, metadata(dynamicSize(LENGTH), PTR_OFFSET, ORIGIN_SIZE))
        ...
       </k>

  rule <k> ListItem(PtrLocal(OFFSET, PLACE, _, metadata(_SIZE, PTR_OFFSET, ORIGIN_SIZE))) ListItem(Aggregate(_, .List)) ~> #mkAggregate(aggregateKindRawPtr(_TY, MUT))
        => PtrLocal(OFFSET, PLACE, MUT, metadata(noMetadataSize, PTR_OFFSET, ORIGIN_SIZE))
        ...
       </k>
```

The `Aggregate` type carries a `VariantIdx` to distinguish the different variants for an `enum`.
This variant index is used to look up the _discriminant_ from a table in the type metadata during evaluation of the `Rvalue::Discriminant`.
Note that the discriminant may be different from the variant index for user-defined discriminants and uninhabited variants.

The `Ty` of the aggregate is required in order to access the discriminant mapping table for the type in the type metadata.
The `getTyOf` helper applies the projections from the `Place` to determine the `Ty` it.

```k
  rule <k> rvalueDiscriminant(place(local(I), PROJS) #as PLACE)
        => #discriminant(operandCopy(PLACE), getTyOf(tyOfLocal({LOCALS[I]}:>TypedLocal), PROJS)) ... </k>
       <locals> LOCALS </locals>
    requires 0 <=Int I andBool I <Int size(LOCALS)
     andBool isTypedLocal(LOCALS[I])
    [preserves-definedness] // valid indexing and sort coercion

  syntax Evaluation ::= #discriminant ( Evaluation , MaybeTy ) [strict(1)]
  // ----------------------------------------------------------------
  rule <k> #discriminant(Aggregate(IDX, _), TY:Ty)
        => Integer(#lookupDiscriminant(lookupTy(TY), IDX), 0, false) // HACK: bit width 0 means "flexible"
        ...
       </k>

  syntax Int ::= #lookupDiscriminant ( TypeInfo , VariantIdx )  [function, total]
               | #lookupDiscrAux ( Discriminants , Int ) [function]
  // --------------------------------------------------------------------
  rule #lookupDiscriminant(typeInfoEnumType(_, _, DISCRIMINANTS, _, _), variantIdx(IDX)) => #lookupDiscrAux(DISCRIMINANTS, IDX)
    requires isInt(#lookupDiscrAux(DISCRIMINANTS, IDX)) [preserves-definedness]
  rule #lookupDiscriminant(_OTHER, _) => 0 [owise, preserves-definedness] // default 0. May be undefined behaviour, though.
  // --------------------------------------------------------------------
  rule #lookupDiscrAux( discriminant(RESULT)         _        , IDX) => RESULT requires IDX ==Int 0
  rule #lookupDiscrAux( _:Discriminant      MORE:Discriminants, IDX) => #lookupDiscrAux(MORE, IDX -Int 1) requires 0 <Int IDX [owise]
```

```k
// ShallowIntBox: not implemented yet
```

### References and Dereferencing

References and de-referencing give rise to another family of `RValue`s.

References can be created using a particular region kind (not used here) and `BorrowKind`.
The `BorrowKind` indicates mutability of the value through the reference, but also provides more find-grained characteristics of mutable references.
These fine-grained borrow kinds are not represented here, as some of them are disallowed in the compiler phase targeted by this semantics, and others related to memory management in lower-level artefacts[^borrowkind].
Therefore, reference values are represented with a simple `Mutability` flag instead of `BorrowKind`

[^borrowkind]: https://doc.rust-lang.org/nightly/nightly-rustc/rustc_middle/mir/enum.BorrowKind.html

References also carry pointer `Metadata`, which informs about the pointee size for dynamically-sized types.
For slices (represented as `Value::Range`), the metadata is the length (as a dynamic size).
For `struct`s (represented as `Value::Aggregate`), the metadata is that of the _last_ field (for dynamically-sized data).
Other `Value`s are not expected to have pointer `Metadata` as per their types.

As references are sometimes created by dereferencing other references or pointers, the referenced value is first evaluated (using `#traverseProjection`).
This eliminates any `Deref` projections from the place, and also resolves `Index` projections to `ConstantIndex` ones.

```k
  // reconstructs projections stored as context (used for Rvalues Ref and AddressOf )
  syntax ProjectionElems ::= #projectionsFor( Contexts )                   [function, total]
                           | #projectionsFor( Contexts , ProjectionElems ) [function, total]
  // ----------------------------------------------------------------------------------------
  rule #projectionsFor(CTXS) => #projectionsFor(CTXS, .ProjectionElems)
  rule #projectionsFor(       .Contexts          , PROJS) => PROJS
  rule #projectionsFor(CtxField(_, _, I, TY) CTXS, PROJS) => #projectionsFor(CTXS,     projectionElemField(fieldIdx(I), TY) PROJS)
  rule #projectionsFor(       CtxIndex(_, I) CTXS, PROJS) => #projectionsFor(CTXS, projectionElemConstantIndex(I, 0, false) PROJS)
  rule #projectionsFor( CtxSubslice(_, I, J) CTXS, PROJS) => #projectionsFor(CTXS,      projectionElemSubslice(I, J, false) PROJS)
  // rule #projectionsFor(CtxPointerOffset(OFFSET, ORIGIN_LENGTH) CTXS, PROJS) => #projectionsFor(CTXS, projectionElemSubslice(OFFSET, ORIGIN_LENGTH, false) PROJS)
  rule #projectionsFor(CtxPointerOffset( _, OFFSET, ORIGIN_LENGTH) CTXS, PROJS) => #projectionsFor(CTXS, PointerOffset(OFFSET, ORIGIN_LENGTH) PROJS)

  // Borrowing a zero-sized local that is still `NewLocal`: initialise it, then reuse the regular rule.
  rule <k> rvalueRef(REGION, KIND, place(local(I), PROJS))
        => #forceSetLocal(
              local(I),
              #decodeConstant(
                constantKindZeroSized,
                tyOfLocal(getLocal(LOCALS, I)),
                lookupTy(tyOfLocal(getLocal(LOCALS, I)))
              )
            )
        ~> rvalueRef(REGION, KIND, place(local(I), PROJS))
       ...
       </k>
       <locals> LOCALS </locals>
    requires 0 <=Int I andBool I <Int size(LOCALS)
     andBool isNewLocal(LOCALS[I])
     andBool #zeroSizedType(lookupTy(tyOfLocal(getLocal(LOCALS, I))))
    [preserves-definedness] // valid list indexing checked, zero-sized locals materialise trivially

  rule <k> rvalueRef(_REGION, KIND, place(local(I), PROJS))
        => #traverseProjection(toLocal(I), getValue(LOCALS, I), PROJS, .Contexts)
        ~> #forRef(#mutabilityOf(KIND), metadata(#metadataSize(tyOfLocal({LOCALS[I]}:>TypedLocal), PROJS), 0, noMetadataSize)) // TODO: Sus on this rule
       ...
       </k>
       <locals> LOCALS </locals>
    requires 0 <=Int I andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])
    [preserves-definedness] // valid list indexing checked, #metadataSize should only use static information

  syntax KItem ::= #forRef( Mutability , Metadata )

  // once traversal is finished, reconstruct the last projections and the reference offset/local, and possibly read the size
  rule <k> #traverseProjection(DEST, VAL:Value, .ProjectionElems, CTXTS) ~> #forRef(MUT, metadata(SIZE, OFFSET, ORIGIN_SIZE))
        => #mkRef(DEST, #projectionsFor(CTXTS), MUT, metadata(#maybeDynamicSize(SIZE, VAL), OFFSET, ORIGIN_SIZE) )
        ...
      </k>

  syntax Evaluation ::= #mkRef( WriteTo , ProjectionElems , Mutability , Metadata ) // [function, total]
  // -----------------------------------------------------------------------------------------------
  // Create Reference for local variable (stack depth 0, no offset)
  rule <k> #mkRef(       toLocal(I)     , PROJS, MUT, META) => Reference(   0  , place(local(I), PROJS), MUT, META) ... </k>

  // Create Reference for stack frame variable (stack depth OFFSET, with pointer offset)
  rule <k> #mkRef(toStack(OFFSET, LOCAL), PROJS, MUT, META) => Reference(OFFSET, place(  LOCAL , PROJS), MUT, META) ... </k>

  // Create AllocRef for heap allocation (assumed zero offset, no offset concept for heap)
  rule <k> #mkRef(toAlloc(ALLOC_ID)     , PROJS,  _ , META) => AllocRef(ALLOC_ID, PROJS, META) ... </k>

  syntax MetadataSize ::= #maybeDynamicSize ( MetadataSize , Value ) [function, total]
  // ---------------------------------------------------------------------------------
  rule #maybeDynamicSize(dynamicSize(_), Range(LIST)) => dynamicSize(size(LIST))
  rule #maybeDynamicSize(dynamicSize(_),   _OTHER   ) => noMetadataSize          [priority(100)]
  rule #maybeDynamicSize(   OTHER_META ,     _      ) => OTHER_META              [owise]

  syntax Mutability ::= #mutabilityOf ( BorrowKind ) [function, total]
  // -----------------------------------------------------------------
  rule #mutabilityOf(borrowKindShared)  => mutabilityNot
  rule #mutabilityOf(borrowKindFake(_)) => mutabilityNot // Shallow fake borrow disallowed in late stages
  rule #mutabilityOf(borrowKindMut(_))  => mutabilityMut // all mutable kinds behave equally for us
```

A `CopyForDeref` `RValue` has the semantics of a simple `Use(operandCopy(...))`,
except that the compiler guarantees the only use of the copied value will be for dereferencing,
which enables optimisations in the borrow checker and in code generation.

```k
  rule <k> rvalueCopyForDeref(PLACE) => rvalueUse(operandCopy(PLACE)) ... </k>
```

The `RValue::AddressOf` operation is very similar to creating a reference, since it also
refers to a given _place_. However, the raw pointer obtained by `AddressOf` can be subject
to casts and pointer arithmetic using `BinOp::Offset`.
The operation typically creates a pointer with empty metadata.

```k
  syntax KItem ::= #forPtr ( Mutability, Metadata )

  rule <k> rvalueAddressOf(MUT, place(local(I), PROJS))
         =>
           #traverseProjection(toLocal(I), getValue(LOCALS, I), PROJS, .Contexts)
          ~> #forPtr(MUT, metadata(#metadataSize(tyOfLocal({LOCALS[I]}:>TypedLocal), PROJS), 0, noMetadataSize)) // TODO These initial values might get overwrote
           // we should use #alignOf to emulate the address
       ...
       </k>
       <locals> LOCALS </locals>
    requires 0 <=Int I andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])
    [preserves-definedness] // valid list indexing checked, #metadataSize should only use static information

  // once traversal is finished, reconstruct the last projections and the reference offset/local, and possibly read the size
  rule <k> #traverseProjection(DEST, VAL:Value, .ProjectionElems, CTXTS) ~> #forPtr(MUT, metadata(SIZE, OFFSET, ORIGIN_SIZE))
        => #mkPtr(DEST, #projectionsFor(CTXTS), MUT, metadata(#maybeDynamicSize(SIZE, VAL), OFFSET, ORIGIN_SIZE))
        ...
      </k>

  syntax Evaluation ::= #mkPtr ( WriteTo, ProjectionElems, Mutability , Metadata ) // [function, total]
  // ------------------------------------------------------------------------------------------
  rule <k> #mkPtr(         toLocal(I)   , PROJS, MUT, META) => PtrLocal(    0 , place(local(I), PROJS), MUT, META) ... </k>
  rule <k> #mkPtr(toStack(STACK_OFFSET, LOCAL), PROJS, MUT, META) => PtrLocal(STACK_OFFSET, place(  LOCAL , PROJS), MUT, META) ... </k>
```

In practice, the `AddressOf` can often be found applied to references that get dereferenced first,
turning a borrowed value into a raw pointer. To shorten out chains of Deref and AddressOf/Reference,
a special rule for this case is applied with higher priority.

```k
  rule <k> rvalueAddressOf(MUT, place(local(I), projectionElemDeref .ProjectionElems))
         =>
           refToPtrLocal(getValue(LOCALS, I), MUT)
           // we should use #alignOf to emulate the address
       ...
       </k>
       <locals> LOCALS </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])
     andBool isRef(getValue(LOCALS, I))
    [priority(40), preserves-definedness] // valid indexing checked, toPtrLocal can convert the reference

  syntax Bool ::= isRef ( Value ) [function, total]
  // -----------------------------------------------------
  rule isRef(Reference(_, _, _, _)) => true
  rule isRef(     _OTHER          ) => false [owise]

  syntax Value ::= refToPtrLocal ( Value , Mutability ) [function]

  rule refToPtrLocal(Reference(STACK_OFFSET, PLACE, _, META), MUT) => PtrLocal(STACK_OFFSET, PLACE, MUT, META)
```

## Type casts

Type casts between a number of different types exist in MIR.

```k
  syntax Evaluation ::= #cast( Evaluation, CastKind, MaybeTy, Ty ) [strict(1)]
```

### Number Type Casts

The simplest case of a cast is conversion from one number type to another:

| CastKind     |
|--------------|
| IntToInt     |
| FloatToInt   |
| FloatToFloat |
| IntToFloat   |

`IntToInt` casts between signed and unsigned integral numbers of different width exist, with a
truncating semantics. These casts can only operate on the `Integer` variant of the `Value` type, adjusting
bit width, signedness, and possibly truncating or 2s-complementing the value.

```k
  // int casts
  rule <k> #cast(Integer(VAL, WIDTH, _SIGNEDNESS), castKindIntToInt, _, TY)
          =>
            #intAsType(VAL, WIDTH, #numTypeOf(lookupTy(TY)))
          ...
        </k>
      requires #isIntType(lookupTy(TY))
      [preserves-definedness] // ensures #numTypeOf is defined
```

Boolean values can also be cast to Integers (encoding `true` as `1`).

```k
  rule <k> #cast(BoolVal(VAL), castKindIntToInt, _, TY)
          =>
            #intAsType(1, 8, #numTypeOf(lookupTy(TY)))
          ...
        </k>
      requires #isIntType(lookupTy(TY))
       andBool VAL
      [preserves-definedness] // ensures #numTypeOf is defined

  rule <k> #cast(BoolVal(VAL), castKindIntToInt, _, TY)
          =>
            #intAsType(0, 8, #numTypeOf(lookupTy(TY)))
          ...
        </k>
      requires #isIntType(lookupTy(TY))
       andBool notBool VAL
      [preserves-definedness] // ensures #numTypeOf is defined
```

Casts involving `Float` values are currently not implemented.

### Casts between pointer types


| CastKind | Description                                                |
|----------|------------------------------------------------------------|
| PtrToPtr | Convert between references when representations compatible |

Pointers can be converted from one type to another (`PtrToPtr`) when the representations are compatible.
The compatibility of types (defined in `rt/types.md`) considers their representations (recursively) in
the `Value` sort.

Conversion is especially possible for the case of _Slices_ (of dynamic length) and _Arrays_ (of static length),
which have the same representation `Value::Range`.

When the cast crosses transparent wrappers (newtypes that just forward field `0` e.g. `struct Wrapper<T>(T)`), the pointer's
`Place` must be realigned. `#alignTransparentPlace` rewrites the projection list until the source and target
expose the same inner value:
- if the source unwraps more than the target, append an explicit `field(0)` so the target still sees that field;
- if the target unwraps more, strip any redundant tail projections with `#popTransparentTailTo`, leaving the
  canonical prefix shared by both sides.

```k
  rule <k> #cast(PtrLocal(OFFSET, PLACE, MUT, META), castKindPtrToPtr, TY_SOURCE, TY_TARGET)
          =>
            PtrLocal(
              OFFSET,
              #alignTransparentPlace(
                PLACE,
                #lookupMaybeTy(pointeeTy(lookupTy(TY_SOURCE))),
                #lookupMaybeTy(pointeeTy(lookupTy(TY_TARGET)))
              ),
              MUT,
              #convertMetadata(META, lookupTy(TY_TARGET))
            )
          ...
        </k>
      requires #typesCompatible(lookupTy(TY_SOURCE), lookupTy(TY_TARGET))
      [preserves-definedness] // valid map lookups checked

  syntax Place ::= #alignTransparentPlace ( Place , TypeInfo , TypeInfo ) [function, total]
  syntax ProjectionElems ::= #popTransparentTailTo ( ProjectionElems , TypeInfo ) [function, total]

  rule #alignTransparentPlace(place(LOCAL, PROJS), typeInfoStructType(_, _, FIELD_TY .Tys, LAYOUT) #as SOURCE, TARGET)
    => #alignTransparentPlace(
         place(
           LOCAL,
           appendP(PROJS, projectionElemField(fieldIdx(0), FIELD_TY) .ProjectionElems)
         ),
         lookupTy(FIELD_TY),
         TARGET
       )
    requires #transparentDepth(SOURCE) >Int #transparentDepth(TARGET)
     andBool #zeroFieldOffset(LAYOUT)

  rule #alignTransparentPlace(
         place(LOCAL, PROJS),
         SOURCE,
         typeInfoStructType(_, _, FIELD_TY .Tys, LAYOUT) #as TARGET
       )
    => #alignTransparentPlace(
         place(LOCAL, #popTransparentTailTo(PROJS, lookupTy(FIELD_TY))),
         SOURCE,
         lookupTy(FIELD_TY)
       )
    requires #transparentDepth(SOURCE) <Int #transparentDepth(TARGET)
     andBool #zeroFieldOffset(LAYOUT)
     andBool PROJS =/=K #popTransparentTailTo(PROJS, lookupTy(FIELD_TY))

  rule #alignTransparentPlace(PLACE, _, _) => PLACE [owise]

  rule #popTransparentTailTo(
         projectionElemField(fieldIdx(0), FIELD_TY) .ProjectionElems,
         TARGET
       )
    => .ProjectionElems
    requires lookupTy(FIELD_TY) ==K TARGET

  rule #popTransparentTailTo(
         X:ProjectionElem REST:ProjectionElems,
         TARGET
       )
    => X #popTransparentTailTo(REST, TARGET)
    requires REST =/=K .ProjectionElems

  rule #popTransparentTailTo(PROJS, _) => PROJS [owise]

  syntax Metadata ::= #convertMetadata ( Metadata , TypeInfo ) [function, total]
  // -------------------------------------------------------------------------------------
```

Pointers to slices can be converted to pointers to single elements, _losing_ their metadata.
```k
  rule #convertMetadata(     metadata(SIZE, OFFSET, _) , typeInfoRefType(POINTEE_TY) ) => metadata(noMetadataSize, OFFSET, SIZE)
    requires #metadataSize(POINTEE_TY) ==K noMetadataSize                                                      [priority(60)]
  rule #convertMetadata(     metadata(SIZE, OFFSET, _) , typeInfoPtrType(POINTEE_TY) ) => metadata(noMetadataSize, OFFSET, SIZE)
    requires #metadataSize(POINTEE_TY) ==K noMetadataSize                                                      [priority(60)]
```

Conversely, when casting a pointer to an element to a pointer to a slice or array,
the original allocation size must be checked to be sufficient.

**TODO** this is future work, requiring a "provenance" that retains the original allocation size. Invalid casts should be marked with special "InvalidCast" metadata.

```k
  // no metadata to begin with, fill it in from target type (NB dynamicSize(1) if dynamic)
  rule #convertMetadata(   metadata(noMetadataSize, OFFSET, _)    , typeInfoRefType(POINTEE_TY)) => metadata(#metadataSize(POINTEE_TY), OFFSET, noMetadataSize)
  rule #convertMetadata(   metadata(noMetadataSize, OFFSET, _)    , typeInfoPtrType(POINTEE_TY)) => metadata(#metadataSize(POINTEE_TY), OFFSET, noMetadataSize)
```

Conversion from an array to a slice pointer requires adding metadata (`dynamicSize`) with the previously-static length.
```k
  // convert static length to dynamic length
  rule #convertMetadata(metadata(staticSize(SIZE), OFFSET, _), typeInfoRefType(POINTEE_TY)) => metadata(dynamicSize(SIZE), OFFSET, staticSize(SIZE))
    requires #metadataSize(POINTEE_TY) ==K dynamicSize(1)
  rule #convertMetadata(metadata(staticSize(SIZE), OFFSET, _), typeInfoPtrType(POINTEE_TY)) => metadata(dynamicSize(SIZE), OFFSET, staticSize(SIZE))
    requires #metadataSize(POINTEE_TY) ==K dynamicSize(1)
```

Conversion from a slice to an array pointer, or between different static length array pointers, is allowed in all cases.
It may however be illegal to _dereference_ (i.e., access) the created pointer, depending on the original array length (see `traverseDeref`).

**TODO** we can mark cases of insufficient original length as "InvalidCast" in the future, similar to the above future work.

```k
  rule #convertMetadata(metadata(staticSize(_) #as ORIGIN_SIZE, OFFSET, _), typeInfoRefType(POINTEE_TY)) => metadata(#metadataSize(POINTEE_TY), OFFSET, ORIGIN_SIZE)
    requires #metadataSize(POINTEE_TY) =/=K dynamicSize(1)
  rule #convertMetadata(metadata(staticSize(_) #as ORIGIN_SIZE, OFFSET, _), typeInfoPtrType(POINTEE_TY)) => metadata(#metadataSize(POINTEE_TY), OFFSET, ORIGIN_SIZE)
    requires #metadataSize(POINTEE_TY) =/=K dynamicSize(1)

  rule #convertMetadata(metadata(dynamicSize(_) #as ORIGIN_SIZE, OFFSET, _), typeInfoRefType(POINTEE_TY)) => metadata(#metadataSize(POINTEE_TY), OFFSET, ORIGIN_SIZE)
    requires #metadataSize(POINTEE_TY) =/=K dynamicSize(1)
  rule #convertMetadata(metadata(dynamicSize(_) #as ORIGIN_SIZE, OFFSET, _), typeInfoPtrType(POINTEE_TY)) => metadata(#metadataSize(POINTEE_TY), OFFSET, ORIGIN_SIZE)
    requires #metadataSize(POINTEE_TY) =/=K dynamicSize(1)
```

For a cast bwetween two pointer types with `dynamicSize` metadata (unlikely to occur), the dynamic size value is retained.

```k
  rule #convertMetadata(metadata(dynamicSize(SIZE), OFFSET, _), typeInfoRefType(POINTEE_TY)) => metadata(dynamicSize(SIZE), OFFSET, dynamicSize(SIZE))
    requires #metadataSize(POINTEE_TY) ==K dynamicSize(1)
  rule #convertMetadata(metadata(dynamicSize(SIZE), OFFSET, _), typeInfoPtrType(POINTEE_TY)) => metadata(dynamicSize(SIZE), OFFSET, dynamicSize(SIZE))
    requires #metadataSize(POINTEE_TY) ==K dynamicSize(1)
```

```k
  // non-pointer and non-ref target type (should not happen!)
  rule #convertMetadata( metadata(SIZE, OFFSET, _)    ,  _OTHER_INFO               ) => metadata(noMetadataSize, OFFSET, SIZE) [priority(100)]
```

`PointerCoercion` may achieve a simmilar effect, or deal with function and closure pointers, depending on the coercion type:

| CastKind                           | PointerCoercion          | Description                        |
|------------------------------------|--------------------------|-----------------------             |
| PointerCoercion(_, CoercionSource) | ArrayToPointer           | from `*const [T; N]` to `*const T` |
|                                    | Unsize                   | reify size information             |
|                                    | ReifyFnPointer           |                                    |
|                                    | UnsafeFnPointer          |                                    |
|                                    | ClosureFnPointer(Safety) |                                    |
|                                    | DynStar                  | create a dyn* object               |
|                                    | MutToConstPointer        | make a mutable pointer immutable   |


The `Unsize` coercion converts from a sized pointee type to one that requires a `dynamicSize`.
Specifically, pointers to arrays of statically-known length are cast to pointers to slices, which requires adding the known size as a `dynamicSize`.
The original metadata is therefore already stored as `staticSize` to avoid having to look it up here.

```k
  rule <k> #cast(Reference(OFFSET, PLACE, MUT, metadata(staticSize(SIZE), PTR_OFFSET, ORIGIN_SIZE)), castKindPointerCoercion(pointerCoercionUnsize), _TY_SOURCE, _TY_TARGET)
          =>
            Reference(OFFSET, PLACE, MUT, metadata(dynamicSize(SIZE), PTR_OFFSET, ORIGIN_SIZE))
          ...
        </k>
      //   <types> TYPEMAP </types>
      // could look up the static size here instead of caching it:
      // requires TY_SOURCE in_keys(TYPEMAP)
      //  andBool isTypeInfo(TYPEMAP[TY_SOURCE])
      // andBool notBool hasMetadata(_TY_TARGET, TYPEMAP)
      // [preserves-definedness] // valid type map indexing and sort coercion

  rule <k> #cast(AllocRef(ID, PROJS, metadata(staticSize(SIZE), OFF, ORIG)), castKindPointerCoercion(pointerCoercionUnsize), _TY_SOURCE, _TY_TARGET)
          =>
            AllocRef(ID, PROJS, metadata(dynamicSize(SIZE), OFF, ORIG))
          ...
        </k>
```

### `Transmute` casts

An unsafe `transmute` operation in Rust is an arbitrary cast between unrelated types based on assumptions that the byte
representations of the source and target types are somewhat relatable (or else, under full consideration that they are not).

Support for `castKindTransmute` in this semantics is very limited because of the high-level data model applied.
What can be supported without additional layout consideration is trivial casts between the same underlying type (mutable or not).

```k
  rule <k> #cast(Reference(_, _, _, _) #as REF, castKindTransmute, TY_SOURCE, TY_TARGET) => REF ... </k>
      requires lookupTy(TY_SOURCE) ==K lookupTy(TY_TARGET)

  rule <k> #cast(AllocRef(_, _, _) #as REF, castKindTransmute, TY_SOURCE, TY_TARGET) => REF ... </k>
      requires lookupTy(TY_SOURCE) ==K lookupTy(TY_TARGET)

  rule <k> #cast(PtrLocal(_, _, _, _) #as PTR, castKindTransmute, TY_SOURCE, TY_TARGET) => PTR ... </k>
      requires lookupTy(TY_SOURCE) ==K lookupTy(TY_TARGET)
```

Transmuting a pointer to an integer discards provenance and reinterprets the pointer’s offset as a value of the target integer type.

```k
  syntax Int ::= #ptrOffsetBytes ( Int , MaybeTy ) [function, total]
  rule #ptrOffsetBytes(PTR_OFFSET, _TY:Ty) => 0
    requires PTR_OFFSET ==Int 0
  rule #ptrOffsetBytes(PTR_OFFSET, TY:Ty)
    => PTR_OFFSET *Int #elemSize(#lookupMaybeTy(elemTy(lookupTy(TY))))
    requires PTR_OFFSET =/=Int 0
     andBool #isUnsizedArrayType(lookupTy(TY))
  rule #ptrOffsetBytes(_, _) => -1 [owise] // should not happen

  syntax Bool ::= #isUnsizedArrayType ( TypeInfo ) [function, total]
  rule #isUnsizedArrayType(typeInfoArrayType(_, noTyConst)) => true
  rule #isUnsizedArrayType(_) => false [owise]
```

```k
  rule <k> #cast(
              PtrLocal(_, _, _, metadata(_, PTR_OFFSET, _)),
              castKindTransmute,
              TY_SOURCE,
              TY_TARGET
            )
          =>
            #intAsType(
              #ptrOffsetBytes(
                PTR_OFFSET,
                pointeeTy(#lookupMaybeTy(TY_SOURCE))
              ),
              #bitWidth(#numTypeOf(lookupTy(TY_TARGET))),
              #numTypeOf(lookupTy(TY_TARGET))
            )
          ...
        </k>
      requires #isIntType(lookupTy(TY_TARGET))
       andBool 0 <=Int #ptrOffsetBytes(PTR_OFFSET,pointeeTy(#lookupMaybeTy(TY_SOURCE)))
```

Other `Transmute` casts that can be resolved are round-trip casts from type A to type B and then directly back from B to A.
The first cast is reified as a `thunk`, the second one resolves it and eliminates the `thunk`:

```k
  rule <k> #cast(
              thunk(#cast(DATA, castKindTransmute, TY_SRC_INNER, TY_DEST_INNER)),
              castKindTransmute,
              TY_SRC_OUTER,
              TY_DEST_OUTER
            ) => DATA
          ...
       </k>
    requires lookupTy(TY_SRC_INNER) ==K lookupTy(TY_DEST_OUTER) // cast is a round-trip
     andBool lookupTy(TY_DEST_INNER) ==K lookupTy(TY_SRC_OUTER) // and is well-formed (invariant)
```

Casting a byte array/slice to an integer reinterprets the bytes in little-endian order.

```k
  rule <k> #cast(
              Range(ELEMS),
              castKindTransmute,
              _TY_SOURCE,
              TY_TARGET
            )
          =>
            #intAsType(
              #littleEndianFromBytes(ELEMS),
              size(ELEMS) *Int 8,
              #numTypeOf(lookupTy(TY_TARGET))
            )
          ...
        </k>
      requires #isIntType(lookupTy(TY_TARGET))
       andBool size(ELEMS) *Int 8 ==Int #bitWidth(#numTypeOf(lookupTy(TY_TARGET)))
       andBool #areLittleEndianBytes(ELEMS)
      [preserves-definedness] // ensures #numTypeOf is defined

  syntax Bool ::= #areLittleEndianBytes ( List ) [function, total]
  // -------------------------------------------------------------
  rule #areLittleEndianBytes(.List) => true
  rule #areLittleEndianBytes(ListItem(Integer(_, 8, false)) REST)
    => #areLittleEndianBytes(REST)
  rule #areLittleEndianBytes(ListItem(_OTHER) _) => false [owise]

  syntax Int ::= #littleEndianFromBytes ( List ) [function]
  // -----------------------------------------------------
  rule #littleEndianFromBytes(.List) => 0
  rule #littleEndianFromBytes(ListItem(Integer(BYTE, 8, false)) REST)
    => BYTE +Int 256 *Int #littleEndianFromBytes(REST)
```

Casting an integer to a `[u8; N]` array materialises its little-endian bytes.

```k
  rule <k> #cast(
              Integer(VAL, WIDTH, _SIGNEDNESS),
              castKindTransmute,
              _TY_SOURCE,
              TY_TARGET
            )
          =>
            Range(#littleEndianBytesFromInt(VAL, WIDTH))
          ...
        </k>
      requires #isStaticU8Array(lookupTy(TY_TARGET))
       andBool WIDTH ==Int #staticArrayLenBits(lookupTy(TY_TARGET))
      //  andBool WIDTH >=Int 0  ensured by the above
      //  andBool WIDTH % 8 == 0 ensured by the above
      [preserves-definedness] // ensures element type/length are well-formed

  syntax List ::= #littleEndianBytesFromInt ( Int, Int ) [function]
  // -------------------------------------------------------------
  rule #littleEndianBytesFromInt(VAL, WIDTH)
    => #littleEndianBytes(truncate(VAL, WIDTH, Unsigned), WIDTH >>Int 3)
    requires WIDTH &Int 7 ==Int 0 // WIDTH % 8 == 0
     andBool WIDTH >=Int 0
    [preserves-definedness]

  syntax List ::= #littleEndianBytes ( Int, Int ) [function]
  // -------------------------------------------------------------
  rule #littleEndianBytes(_, COUNT)
    => .List
    requires COUNT <=Int 0

  rule #littleEndianBytes(VAL, COUNT)
    => ListItem(Integer(VAL &Int 255, 8, false)) #littleEndianBytes(VAL >>Int 8, COUNT -Int 1)
    requires COUNT >Int 0
    [preserves-definedness]

  syntax Bool ::= #isStaticU8Array ( TypeInfo ) [function, total]
  // -------------------------------------------------------------
  rule #isStaticU8Array(typeInfoArrayType(ELEM_TY, someTyConst(_)))
    => lookupTy(ELEM_TY) ==K typeInfoPrimitiveType(primTypeUint(uintTyU8))
  rule #isStaticU8Array(_OTHER) => false [owise]

  syntax Int ::= #staticArrayLenBits ( TypeInfo ) [function, total]
  // -------------------------------------------------------------
  rule #staticArrayLenBits(typeInfoArrayType(_, someTyConst(tyConst(KIND, _))))
    => readTyConstInt(KIND) *Int 8
    [preserves-definedness]
  rule #staticArrayLenBits(_OTHER) => 0 [owise]
```

A transmutation from an integer to an enum is wellformed if:
- The bit width of the incoming integer is the same as the discriminant type of the enum
    (e.g. `u8 -> i8` fine, `u8 -> u16` not fine) - this is guaranteed by the compiler;
- The incoming integer has a bit pattern that matches a discriminant of the enum
    (e.g. `255_u8` and `-1_i8` fine iff `0b1111_1111` is a discriminant of the enum);

Note that discriminants are stored as `u128` in the type data even if they are signed
or unsigned at the source level. This means that our approach to soundly transmute an
integer into a enum is to treat the incoming integer as unsigned (converting if signed),
and check if the value is in the discriminants. If yes, find the corresponding variant
index; if not, return `#UBErrorInvalidDiscriminantsInEnumCast`.

```k
  syntax Bool ::= #isEnumWithoutFields ( TypeInfo ) [function, total]
  // ----------------------------------------------------------------
  rule #isEnumWithoutFields(typeInfoEnumType(_, _, _, FIELDSS, _)) => #noFields(FIELDSS)
  rule #isEnumWithoutFields(_OTHER) => false [owise]

  // TODO: Connect this with MirError
  syntax Evaulation ::= "#UBErrorInvalidDiscriminantsInEnumCast"
  rule <k>
           #cast( Integer ( VAL , WIDTH , _SIGNED ) , castKindTransmute , _TY_FROM , TY_TO ) ~> _REST
        =>
           #UBErrorInvalidDiscriminantsInEnumCast
      </k>
      requires #isEnumWithoutFields(lookupTy(TY_TO))
        andBool notBool #validDiscriminant( truncate(VAL, WIDTH, Unsigned) , lookupTy(TY_TO) )

  rule <k>
           #cast( Integer ( VAL , WIDTH , _SIGNED ) , castKindTransmute , _TY_FROM , TY_TO )
        =>
           Aggregate( #findVariantIdxFromTy( truncate(VAL, WIDTH, Unsigned), lookupTy(TY_TO) ) , .List )
       ...
      </k>
      requires #isEnumWithoutFields(lookupTy(TY_TO))
        andBool #validDiscriminant( truncate(VAL, WIDTH, Unsigned) , lookupTy(TY_TO))

  syntax VariantIdx ::= #findVariantIdxFromTy ( Int , TypeInfo ) [function, total]
  //------------------------------------------------------------------------------
  rule #findVariantIdxFromTy( VAL , typeInfoEnumType(_, _, DISCRIMINANTS, _, _) ) => #findVariantIdx( VAL, DISCRIMINANTS)
  rule #findVariantIdxFromTy( _ , _ ) => err("NotAnEnum") [owise]

  syntax Bool ::= #validDiscriminant    ( Int , TypeInfo )      [function, total]
  // ----------------------------------------------------------------------------
  rule #validDiscriminant( VAL , typeInfoEnumType(_, _, DISCRIMINANTS, _, _) ) => #validDiscriminantAux( VAL , DISCRIMINANTS )
  rule #validDiscriminant( _ , _ ) => false [owise]

  syntax Bool ::= #validDiscriminantAux ( Int , Discriminants ) [function, total]
  // ----------------------------------------------------------------------------
  rule #validDiscriminantAux( VAL, discriminant(mirInt(DISCRIMINANT)) REST ) => VAL ==Int DISCRIMINANT orBool #validDiscriminantAux( VAL, REST )
  rule #validDiscriminantAux( VAL, discriminant(    DISCRIMINANT    ) REST ) => VAL ==Int DISCRIMINANT orBool #validDiscriminantAux( VAL, REST )
  rule #validDiscriminantAux( _VAL, .Discriminants ) => false
```


### Other casts involving pointers

| CastKind                     | Description |
|------------------------------|-------------|
| PointerExposeAddress         |             |
| PointerWithExposedProvenance |             |
| FnPtrToPtr                   |             |

## Decoding constants from their bytes representation to values

The `Value` sort above operates at a higher level than the bytes representation found in the MIR syntax for constant values.
The bytes have to be interpreted according to the given `TypeInfo` to produce the higher-level value.

```k
  syntax Evaluation ::= #decodeConstant ( ConstantKind, Ty, TypeInfo )
```

For allocated constants without provenance, the decoder works directly with the bytes.

```k
  rule <k> #decodeConstant(
              constantKindAllocated(allocation(BYTES, provenanceMap(.ProvenanceMapEntries), _, _)),
              _TY,
              TYPEINFO
            )
        => #decodeValue(BYTES, TYPEINFO)
        ...
       </k>
```

Zero-sized types can be decoded trivially into their respective representation.

```k
  // zero-sized struct
  rule <k> #decodeConstant(constantKindZeroSized, _TY, typeInfoStructType(_, _, _, _))
        => Aggregate(variantIdx(0), .List) ... </k>
  // zero-sized tuple
  rule <k> #decodeConstant(constantKindZeroSized, _TY, typeInfoTupleType(_, _))
        => Aggregate(variantIdx(0), .List) ... </k>
  // zero-sized array
  rule <k> #decodeConstant(constantKindZeroSized, _TY, typeInfoArrayType(_, _))
        => Range(.List) ... </k>
```

Allocated constants of reference type with a single provenance map entry are decoded as references
into the `<memory>` heap where all allocated constants have been decoded at program start.

```k
  rule <k> #decodeConstant(
              constantKindAllocated(
                allocation(
                  BYTES,
                  provenanceMap(provenanceMapEntry(0, ALLOC_ID) .ProvenanceMapEntries),
                  _,
                  _)),
              _TY,
              typeInfoRefType(POINTEE_TY)
            )
        => AllocRef(ALLOC_ID, .ProjectionElems, metadata(#metadataSize(POINTEE_TY), 0, #metadataSize(POINTEE_TY)))
        ...
       </k>
    requires isValue(lookupAlloc(ALLOC_ID))
     andBool lengthBytes(BYTES) ==Int 8 // no dynamic metadata

  rule <k> #decodeConstant(
              constantKindAllocated(
                allocation(
                  BYTES,
                  provenanceMap(provenanceMapEntry(0, ALLOC_ID) .ProvenanceMapEntries),
                  _,
                  _)),
              _TY,
              typeInfoRefType(_)
            )
        => AllocRef(ALLOC_ID, .ProjectionElems, metadata(dynamicSize(Bytes2Int(substrBytes(BYTES, 8, 16), LE, Unsigned)), 0, dynamicSize(Bytes2Int(substrBytes(BYTES, 8, 16), LE, Unsigned)) ))
                                                            // assumes usize == u64
        ...
       </k>
    requires isValue(lookupAlloc(ALLOC_ID))
    andBool lengthBytes(BYTES) ==Int 16 // fat pointer (assumes usize == u64)
    [preserves-definedness] // Byte length checked to be sufficient
```


## Primitive operations on numeric data

The `RValue:BinaryOp` performs built-in binary operations on two operands.
As [described in the `stable_mir` crate](https://doc.rust-lang.org/nightly/nightly-rustc/stable_mir/mir/enum.Rvalue.html#variant.BinaryOp), its semantics depends on the operations and the types of operands (including variable return types).
Certain operation-dependent types apply to the arguments and determine the result type.
Likewise, `RValue:UnaryOp` only operates on certain operand types, notably `bool` and numeric types for arithmetic and bitwise negation.

Arithmetics is usually performed using `RValue:CheckedBinaryOp(BinOp, Operand, Operand)`.
Its semantics is the same as for `BinaryOp`, but it yields `(T, bool)` with a `bool` indicating an error condition.
For addition, subtraction, and multiplication on integers the error condition is set when the infinite precision result would not be equal to the actual result.[^checkedbinaryop]
This is specific to Stable MIR, the MIR AST instead uses `<OP>WithOverflow` as the `BinOp` (which conversely do not exist in the Stable MIR AST).
Where `CheckedBinaryOp(<OP>, _, _)` returns the wrapped result together with the boolean overflow indicator, the `<Op>Unchecked` operation has _undefined behaviour_ on overflows (i.e., when the infinite precision result is unequal to the actual wrapped result).

[^checkedbinaryop]: See [description in `stable_mir` crate](https://doc.rust-lang.org/nightly/nightly-rustc/stable_mir/mir/enum.Rvalue.html#variant.CheckedBinaryOp) and the difference between [MIR `BinOp`](https://doc.rust-lang.org/nightly/nightly-rustc/rustc_middle/mir/enum.BinOp.html) and its [Stable MIR correspondent](https://doc.rust-lang.org/nightly/nightly-rustc/stable_mir/mir/enum.BinOp.html).

For binary operations generally, both arguments have to be read from the provided operands, followed by checking the types and then performing the actual operation (both implemented in `#applyBinOp`), which can return a `TypedLocal` or an error.
A flag carries the information whether to perform an overflow check through to this function for `CheckedBinaryOp`.

```k
  syntax Evaluation ::= #applyBinOp ( BinOp, Evaluation, Evaluation, Bool) [seqstrict(2,3)]

  rule <k> rvalueBinaryOp(BINOP, OP1, OP2)        => #applyBinOp(BINOP, OP1, OP2, false) ... </k>

  rule <k> rvalueCheckedBinaryOp(BINOP, OP1, OP2) => #applyBinOp(BINOP, OP1, OP2, true)  ... </k>
```

There are also a few _unary_ operations (`UnOpNot`, `UnOpNeg`, `UnOpPtrMetadata`)  used in `RValue:UnaryOp`.
These operations only read a single operand.

```k
  syntax Evaluation ::= #applyUnOp ( UnOp , Evaluation ) [strict(2)]

  rule <k> rvalueUnaryOp(UNOP, OP1) => #applyUnOp(UNOP, OP1) ... </k>
```

#### Arithmetic

The arithmetic operations require operands of the same numeric type, however these rules assume the `Ty`s
are correct.

| `BinOp`           |                                        | Operands can be |
|-------------------|--------------------------------------- |-----------------|-------------------------------------- |
| `Add`             | (A + B truncated, bool overflow flag)  | int, float      | Context: `CheckedBinaryOp`            |
| `AddUnchecked`    | A + B                                  | int, float      | undefined behaviour on overflow       |
| `Sub`             | (A - B truncated, bool underflow flag) | int, float      | Context: `CheckedBinaryOp`            |
| `SubUnchecked`    | A - B                                  | int, float      | undefined behaviour on overflow       |
| `Mul`             | (A * B truncated, bool overflow flag)  | int, float      | Context: `CheckedBinaryOp`            |
| `MulUnchecked`    | A * B                                  | int, float      | undefined behaviour on overflow       |
| `Div`             | A / B or A `div` B                     | int, float      | undefined behaviour when divisor zero |
| `Rem`             | A `mod` B, rounding towards zero       | int             | undefined behaviour when divisor zero |

```k
  syntax Bool ::= isArithmetic ( BinOp ) [function, total]
  // -----------------------------------------------
  rule isArithmetic(binOpAdd)          => true
  rule isArithmetic(binOpAddUnchecked) => true
  rule isArithmetic(binOpSub)          => true
  rule isArithmetic(binOpSubUnchecked) => true
  rule isArithmetic(binOpMul)          => true
  rule isArithmetic(binOpMulUnchecked) => true
  rule isArithmetic(binOpDiv)          => true
  rule isArithmetic(binOpRem)          => true
  rule isArithmetic(_)                 => false [owise]

  // performs the given operation on infinite precision integers
  syntax Int ::= onInt( BinOp, Int, Int ) [function]
  // -----------------------------------------------
  rule onInt(binOpAdd, X, Y)          => X +Int Y [preserves-definedness]
  rule onInt(binOpAddUnchecked, X, Y) => X +Int Y [preserves-definedness]
  rule onInt(binOpSub, X, Y)          => X -Int Y [preserves-definedness]
  rule onInt(binOpSubUnchecked, X, Y) => X -Int Y [preserves-definedness]
  rule onInt(binOpMul, X, Y)          => X *Int Y [preserves-definedness]
  rule onInt(binOpMulUnchecked, X, Y) => X *Int Y [preserves-definedness]
  rule onInt(binOpDiv, X, Y)          => X /Int Y requires Y =/=Int 0 [preserves-definedness]
  rule onInt(binOpRem, X, Y)          => X %Int Y requires Y =/=Int 0 [preserves-definedness]
  // operation undefined otherwise

  // error cases for isArithmetic(BOP):
  // * arguments must be Numbers

  // Checked operations return a pair of the truncated value and an overflow flag
  // signed numbers: must check for wrap-around (operation specific)
  rule #applyBinOp(
          BOP,
          Integer(ARG1, WIDTH, true), //signed
          Integer(ARG2, WIDTH, true),
          true) // checked
    =>
          Aggregate(
            variantIdx(0),
            ListItem(Integer(truncate(onInt(BOP, ARG1, ARG2), WIDTH, Signed), WIDTH, true))
            ListItem(
              BoolVal(
                // overflow: compare with and without truncation
                truncate(onInt(BOP, ARG1, ARG2), WIDTH, Signed) =/=Int onInt(BOP, ARG1, ARG2)
              )
            )
          )
    requires isArithmetic(BOP)
    [preserves-definedness]

  // unsigned numbers: simple overflow check using a bit mask
  rule #applyBinOp(
          BOP,
          Integer(ARG1, WIDTH, false), // unsigned
          Integer(ARG2, WIDTH, false),
          true) // checked
    =>
          Aggregate(
            variantIdx(0),
            ListItem(Integer(truncate(onInt(BOP, ARG1, ARG2), WIDTH, Unsigned), WIDTH, false))
            ListItem(
              BoolVal(
                // overflow flag: compare to truncated result
                truncate(onInt(BOP, ARG1, ARG2), WIDTH, Unsigned) =/=Int onInt(BOP, ARG1, ARG2)
              )
            )
          )
    requires isArithmetic(BOP)
    [preserves-definedness]

  // Unchecked operations signal undefined behaviour on overflow. The checks are the same as for the flags above.

  rule #applyBinOp(
          BOP,
          Integer(ARG1, WIDTH, true), // signed
          Integer(ARG2, WIDTH, true),
          false) // unchecked
    => Integer(truncate(onInt(BOP, ARG1, ARG2), WIDTH, Signed), WIDTH, true)
    requires isArithmetic(BOP)
    // infinite precision result must equal truncated result
     andBool truncate(onInt(BOP, ARG1, ARG2), WIDTH, Signed) ==Int onInt(BOP, ARG1, ARG2)
    [preserves-definedness]

  // unsigned numbers: simple overflow check using a bit mask
  rule #applyBinOp(
          BOP,
          Integer(ARG1, WIDTH, false), // unsigned
          Integer(ARG2, WIDTH, false),
          false) // unchecked
    => Integer(truncate(onInt(BOP, ARG1, ARG2), WIDTH, Unsigned), WIDTH, false)
    requires isArithmetic(BOP)
    // infinite precision result must equal truncated result
     andBool truncate(onInt(BOP, ARG1, ARG2), WIDTH, Unsigned) ==Int onInt(BOP, ARG1, ARG2)
    [preserves-definedness]
```

#### Comparison operations

Comparison operations can be applied to all integral types and to boolean values (where `false < true`).
All operations except `binOpCmp` return a `BoolVal`.
The argument types must be the same for all comparison operations, however this is not checked by the rules.

```k
  syntax Bool ::= isComparison(BinOp) [function, total]

  rule isComparison(binOpEq) => true
  rule isComparison(binOpLt) => true
  rule isComparison(binOpLe) => true
  rule isComparison(binOpNe) => true
  rule isComparison(binOpGe) => true
  rule isComparison(binOpGt) => true
  rule isComparison(_) => false [owise]

  syntax Bool ::= cmpOpInt ( BinOp, Int, Int )    [function]
                | cmpOpBool ( BinOp, Bool, Bool ) [function]

  rule cmpOpInt(binOpEq,  X, Y) => X  ==Int Y
  rule cmpOpInt(binOpLt,  X, Y) => X   <Int Y
  rule cmpOpInt(binOpLe,  X, Y) => X  <=Int Y
  rule cmpOpInt(binOpNe,  X, Y) => X =/=Int Y
  rule cmpOpInt(binOpGe,  X, Y) => X  >=Int Y
  rule cmpOpInt(binOpGt,  X, Y) => X   >Int Y

  rule cmpOpBool(binOpEq,  X, Y) => X  ==Bool Y
  rule cmpOpBool(binOpLt,  X, Y) => notBool X andBool Y
  rule cmpOpBool(binOpLe,  X, Y) => notBool X orBool (X andBool Y)
  rule cmpOpBool(binOpNe,  X, Y) => X =/=Bool Y
  rule cmpOpBool(binOpGe,  X, Y) => cmpOpBool(binOpLe, Y, X)
  rule cmpOpBool(binOpGt,  X, Y) => cmpOpBool(binOpLt, Y, X)

  // error cases for isComparison and binOpCmp:
  // * arguments must be numbers or Bool

  rule #applyBinOp(OP, Integer(VAL1, WIDTH, SIGN), Integer(VAL2, WIDTH, SIGN), _)
      =>
        BoolVal(cmpOpInt(OP, VAL1, VAL2))
    requires isComparison(OP)
     andBool WIDTH =/=Int 0
    [preserves-definedness] // OP known to be a comparison

  // HACK: accept bit width 0 in comparisons (coming from discriminants)
  rule #applyBinOp(OP, Integer(VAL1, 0, false), Integer(VAL2, _WIDTH, _SIGN), _)
      =>
        BoolVal(cmpOpInt(OP, VAL1, VAL2))
    requires isComparison(OP)
    [priority(55), preserves-definedness] // OP known to be a comparison
  rule #applyBinOp(OP, Integer(VAL1, _WIDTH, _SIGN_), Integer(VAL2, 0, false), _)
      =>
        BoolVal(cmpOpInt(OP, VAL1, VAL2))
    requires isComparison(OP)
    [preserves-definedness] // OP known to be a comparison

  rule #applyBinOp(OP, BoolVal(VAL1), BoolVal(VAL2), _)
      =>
        BoolVal(cmpOpBool(OP, VAL1, VAL2))
    requires isComparison(OP)
    [priority(60), preserves-definedness] // OP known to be a comparison
```

The `binOpCmp` operation returns `-1`, `0`, or `+1` (the behaviour of Rust's `std::cmp::Ordering as i8`), indicating `LE`, `EQ`, or `GT`.

```k
  syntax Int ::= cmpInt  ( Int , Int )  [function , total]
               | cmpBool ( Bool, Bool ) [function , total]
  rule cmpInt(VAL1, VAL2) => -1 requires VAL1 <Int VAL2
  rule cmpInt(VAL1, VAL2) => 0  requires VAL1 ==Int VAL2
  rule cmpInt(VAL1, VAL2) => 1  requires VAL1 >Int VAL2

  rule cmpBool(X, Y) => -1 requires notBool X andBool Y
  rule cmpBool(X, Y) => 0  requires X ==Bool Y
  rule cmpBool(X, Y) => 1  requires X andBool notBool Y

  rule #applyBinOp(binOpCmp, Integer(VAL1, WIDTH, SIGN), Integer(VAL2, WIDTH, SIGN), _)
      =>
        Integer(cmpInt(VAL1, VAL2), 8, true)

  rule #applyBinOp(binOpCmp, BoolVal(VAL1), BoolVal(VAL2), _)
      =>
        Integer(cmpBool(VAL1, VAL2), 8, true)
```

#### Unary operations on Boolean and integral values

The `unOpNeg` operation only works signed integral (and floating point) numbers.
An overflow can happen when negating the minimal representable integral value (in the given `WIDTH`).
The semantics of the operation in this case is to wrap around (with the given bit width).

```k
  rule <k> #applyUnOp(unOpNeg, Integer(VAL, WIDTH, true))
          =>
            Integer(truncate(0 -Int VAL, WIDTH, Signed), WIDTH, true)
        ...
        </k>

  // TODO add rule for Floats once they are supported.
```

The `unOpNot` operation works on boolean and integral values, with the usual semantics for booleans and a bitwise semantics for integral values (overflows cannot occur).

```k
  rule <k> #applyUnOp(unOpNot, BoolVal(VAL))
          =>
            BoolVal(notBool VAL)
        ...
        </k>

  rule <k> #applyUnOp(unOpNot, Integer(VAL, WIDTH, true))
          =>
            Integer(truncate(~Int VAL, WIDTH, Signed), WIDTH, true)
        ...
        </k>

  rule <k> #applyUnOp(unOpNot, Integer(VAL, WIDTH, false))
          =>
            Integer(truncate(~Int VAL, WIDTH, Unsigned), WIDTH, false)
        ...
        </k>
```

#### Bit-oriented operations

Bitwise operations `binOpBitXor`, `binOpBitAnd`, and `binOpBitOr` are valid between integers, booleans, and borrows; but only if the type of left and right arguments is the same.

TODO: Borrows: Stuck on global allocs / promoteds

Shifts are valid on integers if the right argument (the shift amount) is strictly less than the width of the left argument.
Right shifts on negative numbers are arithmetic shifts and preserve the sign.
There are two variants (checked and unchecked), checked will wrap on overflow and not trigger UB, unchecked will trigger UB on overflow.
The UB case currently gets stuck.

```k
  syntax Bool ::= isBitwise ( BinOp ) [function, total]
  // --------------------------------------------------
  rule isBitwise(binOpBitXor)   => true
  rule isBitwise(binOpBitAnd)   => true
  rule isBitwise(binOpBitOr)    => true
  rule isBitwise(_)             => false [owise]
  rule onInt(binOpBitXor, X, Y) => X xorInt Y
  rule onInt(binOpBitAnd, X, Y) => X &Int Y
  rule onInt(binOpBitOr, X, Y)  => X |Int Y

  syntax Bool ::= onBool( BinOp, Bool, Bool ) [function]
  // ---------------------------------------------------
  rule onBool(binOpBitXor, X, Y)  => X xorBool Y
  rule onBool(binOpBitAnd, X, Y)  => X andBool Y
  rule onBool(binOpBitOr, X, Y)   => X orBool Y

  syntax Bool ::= isShift ( BinOp ) [function, total]
  // ------------------------------------------------
  rule isShift(binOpShl)          => true
  rule isShift(binOpShlUnchecked) => true
  rule isShift(binOpShr)          => true
  rule isShift(binOpShrUnchecked) => true
  rule isShift(_)                 => false [owise]

  syntax Bool ::= isUncheckedShift ( BinOp ) [function, total]
  // ------------------------------------------------
  rule isUncheckedShift(binOpShlUnchecked) => true
  rule isUncheckedShift(binOpShrUnchecked) => true
  rule isUncheckedShift(_)                 => false [owise]

  syntax Int ::= onShift( BinOp, Int, Int, Int ) [function]
  // ---------------------------------------------------
  rule onShift(binOpShl, X, Y, WIDTH)          => (X <<Int Y) modInt (1 <<Int WIDTH)
  rule onShift(binOpShr, X, Y, WIDTH)          => (X >>Int Y) modInt (1 <<Int WIDTH)
  rule onShift(binOpShlUnchecked, X, Y, WIDTH) => (X <<Int Y) modInt (1 <<Int WIDTH)
  rule onShift(binOpShrUnchecked, X, Y, WIDTH) => (X >>Int Y) modInt (1 <<Int WIDTH)

  rule #applyBinOp(
          BOP,
          Integer(ARG1, WIDTH, SIGNED),
          Integer(ARG2, WIDTH, SIGNED),
          false) // unchecked
    =>
          Integer(onInt(BOP, ARG1, ARG2), WIDTH, SIGNED)
    requires isBitwise(BOP)
    [preserves-definedness]

  rule #applyBinOp(
          BOP,
          BoolVal(ARG1),
          BoolVal(ARG2),
          false) // unchecked
    =>
          BoolVal(onBool(BOP, ARG1, ARG2))
    requires isBitwise(BOP)
    [preserves-definedness]

  rule #applyBinOp(
          BOP,
          Integer(ARG1, WIDTH, false),
          Integer(ARG2, _, _),
          false) // unchecked
    =>
          Integer(truncate(onShift(BOP, ARG1, ARG2, WIDTH), WIDTH, Unsigned), WIDTH, false)
    requires isShift(BOP) andBool ((notBool isUncheckedShift(BOP)) orBool ARG2 <Int WIDTH)
    [preserves-definedness]

  rule #applyBinOp(
          BOP,
          Integer(ARG1, WIDTH, true),
          Integer(ARG2, _, _),
          false) // unchecked
    =>
          Integer(truncate(onShift(BOP, ARG1, ARG2, WIDTH), WIDTH, Signed), WIDTH, true)
    requires isShift(BOP) andBool ((notBool isUncheckedShift(BOP)) orBool ARG2 <Int WIDTH)
    [preserves-definedness]
```


#### Nullary operations for activating certain checks

`nullOpUbChecks` is supposed to return `BoolVal(true)` if checks for undefined behaviour were activated in the compilation.
For our MIR semantics this means to either retain this information (which we don't) or to decide whether or not these checks are useful and should be active during execution.

One important use case of `UbChecks` is to determine overflows in unchecked arithmetic operations.
Since our arithmetic operations signal undefined behaviour on overflow independently, the value returned by `UbChecks` is `false` for now.

```k
  rule <k> rvalueNullaryOp(nullOpUbChecks, _) => BoolVal(false) ... </k>
```

#### "Nullary" operations reifying type information

`nullOpSizeOf`
`nullOpAlignOf`
`nullOpOffsetOf(VariantAndFieldIndices)`

```k
// FIXME: 64 is hardcoded since usize not supported
rule <k> rvalueNullaryOp(nullOpAlignOf, TY)
      =>
           Integer(#alignOf(lookupTy(TY)), 64, false)
         ...
     </k>
    requires lookupTy(TY) =/=K typeInfoVoidType
```

#### Other operations

The unary operation `unOpPtrMetadata`, when given a reference or pointer to a slice, will return the reference or pointer metadata.
* For slices with dynamic length (not statically known), this metadata is the `dynamicSize` and is returned as a `usize`.
* For values with statically-known size, this operation returns a _unit_ value. However, these calls should not occur in practical programs.

```k
  rule <k> #applyUnOp(unOpPtrMetadata, Reference(_, _, _, metadata(dynamicSize(SIZE), _, _))) => Integer(SIZE, 64, false) ... </k>
  rule <k> #applyUnOp(unOpPtrMetadata,  PtrLocal(_, _, _, metadata(dynamicSize(SIZE), _, _))) => Integer(SIZE, 64, false) ... </k>
  rule <k> #applyUnOp(unOpPtrMetadata,  AllocRef(  _ , _, metadata(dynamicSize(SIZE), _, _))) => Integer(SIZE, 64, false) ... </k>

  // could add a rule for cases without metadata
```

#### Pointer equality

Raw pointer comparisons ignore mutability, but require the address and metadata to match.

```k
  syntax Bool ::= #ptrLocalEq(Value, Value) [function, total]

  rule #ptrLocalEq(
          PtrLocal(OFFSET1, PLACE1, _, PTRMETA1),
          PtrLocal(OFFSET2, PLACE2, _, PTRMETA2)
       )
    =>  OFFSET1 ==Int OFFSET2
     andBool PLACE1 ==K PLACE2
     andBool PTRMETA1 ==K PTRMETA2
  rule #ptrLocalEq(_, _) => false [owise]

  rule #applyBinOp(
          binOpEq,
          PtrLocal(_, _, _, _) #as PTR1,
          PtrLocal(_, _, _, _) #as PTR2,
          _
       )
    => BoolVal(#ptrLocalEq(PTR1, PTR2))

  rule #applyBinOp(
          binOpNe,
          PtrLocal(_, _, _, _) #as PTR1,
          PtrLocal(_, _, _, _) #as PTR2,
          _
       )
    => BoolVal(notBool #ptrLocalEq(PTR1, PTR2))
```



#### Pointer Artithmetic
Addding an offset is currently restricted to unsigned values of an length, this may be too restrictive TODO Check.
A pointer is offset by adding the magnitude of the `Integer` provided, as along as it is within the bounds of the pointer.
It is valid to offset to the end of the pointer, however I believe it in not valid to read from there TODO: Check.
A trivial case where `binOpOffset` applies an offset of `0` is added with higher priority as it is returning the same pointer.

```k
  // Trivial case when adding 0 - valid for any pointer
  rule #applyBinOp(
          binOpOffset,
          PtrLocal( STACK_DEPTH , PLACE , MUT, POINTEE_METADATA ),
          Integer(VAL, _WIDTH, _SIGNED), // Trivial case when adding 0
          _CHECKED)
    =>
          PtrLocal( STACK_DEPTH , PLACE , MUT, POINTEE_METADATA )
  requires VAL ==Int 0
  [preserves-definedness, priority(40)]

  // Check offset bounds against origin pointer with dynamicSize metadata
  rule #applyBinOp(
          binOpOffset,
          PtrLocal( STACK_DEPTH , PLACE , MUT, metadata(CURRENT_SIZE, CURRENT_OFFSET, dynamicSize(ORIGIN_SIZE)) ),
          Integer(OFFSET_VAL, _WIDTH, false), // unsigned offset
          _CHECKED)
    =>
          PtrLocal( STACK_DEPTH , PLACE , MUT, metadata(CURRENT_SIZE, CURRENT_OFFSET +Int OFFSET_VAL, dynamicSize(ORIGIN_SIZE)) )
    requires OFFSET_VAL >=Int 0
     andBool CURRENT_OFFSET +Int OFFSET_VAL <=Int ORIGIN_SIZE
   [preserves-definedness]

  // Check offset bounds against origin pointer with staticSize metadata
  rule #applyBinOp(
          binOpOffset,
          PtrLocal( STACK_DEPTH , PLACE , MUT, metadata(CURRENT_SIZE, CURRENT_OFFSET, staticSize(ORIGIN_SIZE)) ),
          Integer(OFFSET_VAL, _WIDTH, false), // unsigned offset
          _CHECKED)
    =>
          PtrLocal( STACK_DEPTH , PLACE , MUT, metadata(CURRENT_SIZE, CURRENT_OFFSET +Int OFFSET_VAL, staticSize(ORIGIN_SIZE)) )
    requires OFFSET_VAL >=Int 0
     andBool CURRENT_OFFSET +Int OFFSET_VAL <=Int ORIGIN_SIZE
   [preserves-definedness]
```

```k
endmodule
```
