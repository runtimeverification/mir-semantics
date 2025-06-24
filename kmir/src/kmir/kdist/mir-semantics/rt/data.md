# Handling Data for MIR Execution

This module addresses all aspects of handling "values" i.e., data, at runtime during MIR execution.


```k
requires "../body.md"
requires "../ty.md"
requires "./types.md"
requires "./value.md"
requires "./numbers.md"

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
  syntax TypedLocal ::= "InvalidLocal" // error token only

  syntax TypedLocal ::= getLocal ( List, Int ) [function, total]
  // ----------------------------------------------
  rule getLocal(LOCALS, IDX) => {LOCALS[IDX]}:>TypedLocal
    requires 0 <=Int IDX andBool IDX <Int size(LOCALS)
     andBool isTypedLocal(LOCALS[IDX])

  rule getLocal(_, _) => InvalidLocal [owise]

  syntax TypedValue ::= getValue ( List, Int ) [function]
  // ----------------------------------------------
  rule getValue(LOCALS, IDX) => {LOCALS[IDX]}:>TypedValue
    requires 0 <=Int IDX andBool IDX <Int size(LOCALS)
     andBool isTypedValue(LOCALS[IDX])


```

### Evaluating Items to `TypedValue` or `TypedLocal`

Some built-in operations (`RValue` or type casts) use constructs that will evaluate to a value of sort `TypedValue`.
The basic operations of reading and writing those values can use K's "heating" and "cooling" rules to describe their evaluation.
Other uses of heating and cooling are to _read_ local variables as operands.
`TypedValue` ai the `Result` sort, read access to `Moved` locals or uninitialised `NewLocal`s is an error and will get stuck.

```k
  syntax Evaluation ::= TypedLocal // other sorts are added at the first use site

  // TODO change to TypedValue
  syntax KResult ::= TypedLocal
```

### `thunk`

We also create a subsort of `TypedValue` that is a `thunk` which takes an `Evaluation` as an argument.
The `thunk` captures any `Evaluation` that we cannot make further progress on, and turns that into a `TypedValue` so that we may continue execution (instead of getting stuck).
In particular, if we have pointer arithmetic with abstract pointers (not able to be resolved into concrete ints/bytes directly), then it will wrapper the operations in a `thunk`.
It is also useful to capture unimplemented semantic constructs so that we can have test / proof driven development.

```k
  syntax Value ::= thunk ( Evaluation )

  rule <k> EV:Evaluation => typedValue(thunk(EV), TyUnknown, mutabilityNot) ... </k> requires notBool isTypedValue(EV) [owise]
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
        => #decodeConstant(KIND, TY, {TYPEMAP[TY]}:>TypeInfo)
       ...
       </k>
       <types> TYPEMAP </types>
    requires TY in_keys(TYPEMAP)
     andBool isTypeInfo(TYPEMAP[TY])
    [preserves-definedness] // valid Map lookup checked
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

The `#setLocalValue` operation writes a `TypedLocal` value to a given `Place` within the `List` of local variables currently on top of the stack.
This may fail because a local may not be accessible, moved away, or not mutable.
If we are setting a value at a `Place` which has `Projection`s in it, then we must first traverse the projections before setting the value.
A variant `#forceSetLocal` is provided for setting the local value without checking the mutability of the location.

```k
  syntax KItem ::= #setLocalValue( Place, Evaluation ) [strict(2)]
                 | #forceSetLocal ( Local , TypedLocal )

  rule <k> #setLocalValue(place(local(I), .ProjectionElems), typedValue(VAL:Value, _, _ )) => .K ... </k>
       <locals>
          LOCALS => LOCALS[I <- typedValue(VAL, tyOfLocal(getLocal(LOCALS, I)), mutabilityMut)]
       </locals>
    requires 0 <=Int I andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])
     andBool mutabilityOf(getLocal(LOCALS, I)) ==K mutabilityMut
    [preserves-definedness] // valid list indexing checked

  rule <k> #setLocalValue(place(local(I), .ProjectionElems), typedValue(VAL:Value, _, _ )) => .K ... </k>
       <locals>
          LOCALS => LOCALS[I <- typedValue(VAL, tyOfLocal(getLocal(LOCALS, I)), mutabilityOf(getLocal(LOCALS, I)))]
       </locals>
    requires 0 <=Int I andBool I <Int size(LOCALS)
     andBool isNewLocal(LOCALS[I])
    [preserves-definedness] // valid list indexing checked

  rule <k> #setLocalValue(place(local(I), .ProjectionElems), typedValue(VAL:Value, _, _ )) => .K ... </k>
       <locals>
          LOCALS => LOCALS[I <- typedValue(VAL, tyOfLocal(getLocal(LOCALS, I)), mutabilityOf(getLocal(LOCALS, I)))]
       </locals>
    requires 0 <=Int I andBool I <Int size(LOCALS)
     andBool isMovedLocal(LOCALS[I])
    [preserves-definedness] // valid list indexing checked

  rule <k> #setLocalValue(place(local(I), PROJ), VAL)
        => #traverseProjection(toLocal(I), getLocal(LOCALS, I), PROJ, .Contexts)
        ~> #writeProjection(VAL)
       ...
       </k>
       <locals> LOCALS </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool PROJ =/=K .ProjectionElems
     andBool isTypedValue(LOCALS[I])
    [preserves-definedness]

  rule <k> #forceSetLocal(local(I), VALUE) => .K ... </k>
       <locals> LOCALS => LOCALS[I <- VALUE] </locals>
    requires 0 <=Int I andBool I <Int size(LOCALS)
    [preserves-definedness] // valid list indexing checked
```

### Traversing Projections for Reads and Writes

Read and write operations to places that include (a chain of) projections are handled by a special rewrite symbol `#traverseProjection`.
This helper does the projection lookup and maintains the context chain along the lookup path, then passes control back to `#readProjection` and `#writeProjection`.
A `Deref` projection in the projections list changes the target of the write operation, while `Field` updates change the value that is being written (updating just one field of it), recursively.

```k
  syntax KItem ::= #traverseProjection ( WriteTo , TypedLocal, ProjectionElems, Contexts )
                 | #readProjection ( Bool )
                 | #writeProjection ( TypedValue )
                 | "#writeMoved"

  rule <k> #traverseProjection(_, VAL:TypedValue, .ProjectionElems, _) ~> #readProjection(false) => VAL ... </k>
  rule <k> #traverseProjection(_, VAL:TypedValue, .ProjectionElems, _) ~> (#readProjection(true) => #writeMoved ~> VAL) ... </k>

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
                      #updateStackLocal({STACK[FRAME -Int 1]}:>StackFrame, I, #buildUpdate(NEW, CONTEXTS))
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
                      #updateStackLocal({STACK[FRAME -Int 1]}:>StackFrame, I, #buildUpdate(Moved, CONTEXTS)) // TODO retain Ty and Mutability from _ORIGINAL
                    ]
       </stack>
    requires 0 <Int FRAME andBool FRAME <=Int size(STACK)
     andBool isStackFrame(STACK[FRAME -Int 1])
     [preserves-definedness] // valid context ensured upon context construction
```

These helpers mark down, as we traverse the projection, what `Place` we are currently looking up in the traversal.
`#buildUpdate` helps to reconstruct the new value stored at that `Place` if we need to do a write (using the `Context` built during traversal).

```k
  // stores the target of the write operation, which may change when references are dereferenced.
  syntax WriteTo ::= toLocal ( Int )
                   | toStack ( Int , Local )

  // retains information about the value that was deconstructed by a projection
  syntax Context ::= CtxField( Ty, VariantIdx, List, Int )
                   | CtxIndex( Ty, List , Int ) // array index constant or has been read before

  syntax Contexts ::= List{Context, ""}

  syntax TypedLocal ::= #buildUpdate ( TypedLocal, Contexts ) [function]

  rule #buildUpdate(VAL, .Contexts) => VAL
     [preserves-definedness]

  rule #buildUpdate(VAL, CtxField(TY, IDX, ARGS, I) CTXS)
      => #buildUpdate(typedValue(Aggregate(IDX, ARGS[I <- VAL]), TY, mutabilityMut), CTXS)
     [preserves-definedness] // valid list indexing checked upon context construction

  rule #buildUpdate(VAL, CtxIndex(TY, ELEMS, I) CTXS)
      => #buildUpdate(typedValue(Range(ELEMS[I <- VAL]), TY, mutabilityMut), CTXS)
     [preserves-definedness] // valid list indexing checked upon context construction

  syntax StackFrame ::= #updateStackLocal ( StackFrame, Int, TypedLocal ) [function]

  rule #updateStackLocal(StackFrame(CALLER, DEST, TARGET, UNWIND, LOCALS), I, Moved)
      => StackFrame(CALLER, DEST, TARGET, UNWIND, LOCALS[I <- Moved])
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
    [preserves-definedness]

  rule #updateStackLocal(StackFrame(CALLER, DEST, TARGET, UNWIND, LOCALS), I, typedValue(VAL, _, _))
      => StackFrame(CALLER, DEST, TARGET, UNWIND, LOCALS[I <- typedValue(VAL, tyOfLocal(getLocal(LOCALS, I)), mutabilityMut)])
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
    [preserves-definedness]

  syntax ProjectionElems ::= appendP ( ProjectionElems , ProjectionElems ) [function, total]
  rule appendP(.ProjectionElems, TAIL) => TAIL
  rule appendP(X:ProjectionElem REST:ProjectionElems, TAIL) => X appendP(REST, TAIL)

  syntax TypedValue ::= #localFromFrame ( StackFrame, Local, Int ) [function]

  rule #localFromFrame(StackFrame(... locals: LOCALS), local(I:Int), OFFSET) => #adjustRef(getValue(LOCALS, I), OFFSET)
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])
    [preserves-definedness] // valid list indexing checked

  syntax TypedValue ::= #incrementRef ( TypedValue )  [function, total]
                      | #decrementRef ( TypedValue )  [function, total]
                      | #adjustRef (TypedValue, Int ) [function, total]

  rule #adjustRef(typedValue(Reference(HEIGHT, PLACE, REFMUT), TY, MUT), OFFSET)
    => typedValue(Reference(HEIGHT +Int OFFSET, PLACE, REFMUT), TY, MUT)
  rule #adjustRef(typedValue(PtrLocal(HEIGHT, PLACE, REFMUT), TY, MUT), OFFSET)
    => typedValue(PtrLocal(HEIGHT +Int OFFSET, PLACE, REFMUT), TY, MUT)
  rule #adjustRef(TL, _) => TL [owise]

  rule #incrementRef(TL) => #adjustRef(TL, 1)
  rule #decrementRef(TL) => #adjustRef(TL, -1)
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
             typedValue(Aggregate(IDX, ARGS), TY, _MUT),
             projectionElemField(fieldIdx(I), _) PROJS,
             CTXTS
           )
        => #traverseProjection(
             DEST,
             getLocal(ARGS, I),
             PROJS,
             CtxField(TY, IDX, ARGS, I) CTXTS
           )
        ...
        </k>
    requires 0 <=Int I andBool I <Int size(ARGS)
     andBool isTypedLocal(ARGS[I])
     [preserves-definedness] // valid list indexing checked

  rule <k> #traverseProjection(
             DEST,
             typedValue(Aggregate(_, ARGS), TY, MUT),
             projectionElemDowncast(IDX) PROJS,
             CTXTS
           )
        => #traverseProjection(
             DEST,
             typedValue(Aggregate(IDX, ARGS), TY, MUT),
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
             typedValue(Range(ELEMENTS), TY, _MUT),
             projectionElemIndex(local(LOCAL)) PROJS,
             CTXTS
           )
        => #traverseProjection(
             DEST,
             getValue(ELEMENTS, #expectUsize(getValue(LOCALS, LOCAL))),
             PROJS,
             CtxIndex(TY, ELEMENTS, #expectUsize(getValue(LOCALS, LOCAL))) CTXTS
           )
        ...
        </k>
        <locals> LOCALS </locals>
    requires 0 <=Int LOCAL andBool LOCAL <Int size(LOCALS)
     andBool isTypedValue(LOCALS[LOCAL])
     andBool isInt(#expectUsize(getValue(LOCALS, LOCAL)))
     andBool 0 <=Int #expectUsize(getValue(LOCALS, LOCAL)) andBool #expectUsize(getValue(LOCALS, LOCAL)) <Int size(ELEMENTS)
     andBool isTypedValue(ELEMENTS[#expectUsize(getValue(LOCALS, LOCAL))])
    [preserves-definedness] // index checked, valid Int can be read, ELEMENT indexable and writeable or forced

  rule <k> #traverseProjection(
             DEST,
             typedValue(Range(ELEMENTS), TY, _MUT),
             projectionElemConstantIndex(OFFSET:Int, _MINLEN, false) PROJS,
             CTXTS
           )
        => #traverseProjection(
             DEST,
             getValue(ELEMENTS, OFFSET),
             PROJS,
             CtxIndex(TY, ELEMENTS, OFFSET) CTXTS
           )
        ...
        </k>
    requires 0 <=Int OFFSET andBool OFFSET <Int size(ELEMENTS)
     andBool isTypedValue(ELEMENTS[OFFSET])
    [preserves-definedness] // ELEMENT indexable and writeable or forced

  rule <k> #traverseProjection(
             DEST,
             typedValue(Range(ELEMENTS), TY, _MUT),
             projectionElemConstantIndex(OFFSET:Int, MINLEN, true) PROJS, // from end
             CTXTS
           )
        => #traverseProjection(
             DEST,
             getValue(ELEMENTS, OFFSET),
             PROJS,
             CtxIndex(TY, ELEMENTS, MINLEN -Int OFFSET) CTXTS
           )
        ...
        </k>
    requires 0 <Int OFFSET andBool OFFSET <=Int MINLEN
     andBool MINLEN ==Int size(ELEMENTS) // assumed for valid MIR code
     andBool isTypedValue(ELEMENTS[MINLEN -Int OFFSET])
    [preserves-definedness] // ELEMENT indexable and writeable or forced

  syntax Int ::= #expectUsize ( TypedValue ) [function]

  rule #expectUsize(typedValue(Integer(I, 64, false), _, _)) => I
```

#### References

A `Deref` projection operates on `Reference`s that refer to locals in the same or an enclosing stack frame, indicated by the stack height in the `Reference` value.
`Deref` reads the referred place (and may proceed with further projections).
In the simplest case, the reference refers to a local in the same stack frame (height 0), which is directly read.

```k
  rule <k> #traverseProjection(
             _DEST,
             typedValue(Reference(OFFSET, place(LOCAL, PLACEPROJ), _MUT), _, _),
             projectionElemDeref PROJS,
             _CTXTS
           )
        => #traverseProjection(
             toStack(OFFSET, LOCAL),
             #localFromFrame({STACK[OFFSET -Int 1]}:>StackFrame, LOCAL, OFFSET),
             appendP(PLACEPROJ, PROJS), // apply reference projections first, then rest
             .Contexts // previous contexts obsolete
           )
        ...
        </k>
        <stack> STACK </stack>
    requires 0 <Int OFFSET andBool OFFSET <=Int size(STACK)
     andBool isStackFrame(STACK[OFFSET -Int 1])
    [preserves-definedness]

  rule <k> #traverseProjection(
             _DEST,
             typedValue(Reference(OFFSET, place(local(I), PLACEPROJ), _MUT), _, _),
             projectionElemDeref PROJS,
             _CTXTS
           )
        => #traverseProjection(
             toLocal(I),
             getLocal(LOCALS, I),
             appendP(PLACEPROJ, PROJS), // apply reference projections first, then rest
             .Contexts // previous contexts obsolete
           )
        ...
        </k>
        <locals> LOCALS </locals>
    requires OFFSET ==Int 0
     andBool 0 <=Int I andBool I <Int size(LOCALS)
     andBool isTypedLocal(LOCALS[I])
    [preserves-definedness]


  rule <k> #traverseProjection(
             _DEST,
             typedValue(PtrLocal(OFFSET, place(LOCAL, PLACEPROJ), _MUT), _, _),
             projectionElemDeref PROJS,
             _CTXTS
           )
        => #traverseProjection(
             toStack(OFFSET, LOCAL),
             #localFromFrame({STACK[OFFSET -Int 1]}:>StackFrame, LOCAL, OFFSET),
             appendP(PLACEPROJ, PROJS), // apply reference projections first, then rest
             .Contexts // previous contexts obsolete
           )
        ...
        </k>
        <stack> STACK </stack>
    requires 0 <Int OFFSET andBool OFFSET <=Int size(STACK)
     andBool isStackFrame(STACK[OFFSET -Int 1])
    [preserves-definedness]

  rule <k> #traverseProjection(
             _DEST,
             typedValue(PtrLocal(OFFSET, place(local(I), PLACEPROJ), _MUT), _, _),
             projectionElemDeref PROJS,
             _CTXTS
           )
        => #traverseProjection(
             toLocal(I),
             getLocal(LOCALS, I),
             appendP(PLACEPROJ, PROJS), // apply reference projections first, then rest
             .Contexts // previous contexts obsolete
           )
        ...
        </k>
        <locals> LOCALS </locals>
    requires OFFSET ==Int 0
     andBool 0 <=Int I andBool I <Int size(LOCALS)
    [preserves-definedness]
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

  rule <k> rvalueCast(CASTKIND, OPERAND, TY) => #cast(OPERAND, CASTKIND, TY) ... </k>
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
  syntax KItem ::= #mkArray ( Evaluation , Int ) [strict(1)]

  rule <k> rvalueRepeat(ELEM, tyConst(KIND, _)) => #mkArray(ELEM, readTyConstInt(KIND, TYPES)) ... </k>
       <types> TYPES </types>
    requires isInt(readTyConstInt(KIND, TYPES))
    [preserves-definedness]

  rule <k> #mkArray(ELEMENT:TypedValue, N) => typedValue(Range(makeList(N, ELEMENT)), TyUnknown, mutabilityNot) ... </k>
    requires 0 <=Int N
    [preserves-definedness]

  // reading Int-valued TyConsts from allocated bytes
  syntax Int ::= readTyConstInt ( TyConstKind , Map ) [function]
  // -----------------------------------------------------------
  rule readTyConstInt( tyConstKindValue(TY, allocation(BYTES, _, _, _)), TYPEMAP) => Bytes2Int(BYTES, LE, Unsigned)
    requires isUintTy(#numTypeOf({TYPEMAP[TY]}:>TypeInfo))
     andBool lengthBytes(BYTES) ==Int #bitWidth(#numTypeOf({TYPEMAP[TY]}:>TypeInfo)) /Int 8
    [preserves-definedness]

  rule readTyConstInt( tyConstKindValue(TY, allocation(BYTES, _, _, _)), TYPEMAP) => Bytes2Int(BYTES, LE, Signed  )
    requires isIntTy(#numTypeOf({TYPEMAP[TY]}:>TypeInfo))
     andBool lengthBytes(BYTES) ==Int #bitWidth(#numTypeOf({TYPEMAP[TY]}:>TypeInfo)) /Int 8
    [preserves-definedness]


  // length of arrays or slices
  syntax KItem ::= #lengthU64 ( Evaluation ) [strict(1)]

  rule <k> rvalueLen(PLACE) => #lengthU64(operandCopy(PLACE)) ... </k>

  rule <k> #lengthU64(typedValue(Range(LIST), _, _))
        =>
            typedValue(Integer(size(LIST), 64, false), TyUnknown, mutabilityNot)  // returns usize
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
  syntax KItem ::= #mkAggregate ( AggregateKind )

  rule <k> ARGS:List ~> #mkAggregate(aggregateKindAdt(ADTDEF, VARIDX, _, _, _))
        =>
            typedValue(Aggregate(VARIDX, ARGS), {ADTMAPPING[ADTDEF]}:>MaybeTy, mutabilityNot)
        ...
       </k>
       <adt-to-ty> ADTMAPPING </adt-to-ty>
    requires isTy(ADTMAPPING[ADTDEF])

  rule <k> ARGS:List ~> #mkAggregate(aggregateKindArray(_TY))
        =>
            typedValue(Range(ARGS), TyUnknown, mutabilityNot)
        ...
       </k>


  rule <k> ARGS:List ~> #mkAggregate(aggregateKindTuple)
        =>
            typedValue(Aggregate(variantIdx(0), ARGS), TyUnknown, mutabilityNot)
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

  rule <k> VAL:TypedValue ~> #readOn(ACC, REST)
        =>
           #readOperandsAux(ACC ListItem(VAL), REST)
        ...
       </k>
```

The `Aggregate` type carries a `VariantIdx` to distinguish the different variants for an `enum`.
This variant index is used to look up the _discriminant_ from a table in the type metadata during evaluation of the `Rvalue::Discriminant`.
Note that the discriminant may be different from the variant index for user-defined discriminants and uninhabited variants.

```k
  syntax KItem ::= #discriminant ( Evaluation ) [strict(1)]

  rule <k> rvalueDiscriminant(PLACE) => #discriminant(operandCopy(PLACE)) ... </k>

  rule <k> #discriminant(typedValue(Aggregate(IDX, _), TY, _))
        =>
           typedValue(
              Integer(#lookupDiscriminant({TYPEMAP[TY]}:>TypeInfo, IDX), 128, false), // parameters for storead u128
              TyUnknown,
              mutabilityNot
            )
        ...
       </k>
       <types> TYPEMAP </types>
    requires isTypeInfo(TYPEMAP[TY])

  syntax Int ::= #lookupDiscriminant ( TypeInfo , VariantIdx )  [function, total]
               | #lookupDiscrAux ( Discriminants , VariantIdx ) [function]
  // --------------------------------------------------------------------
  rule #lookupDiscriminant(typeInfoEnumType(_, _, DISCRIMINANTS), IDX) => #lookupDiscrAux(DISCRIMINANTS, IDX)
    requires isInt(#lookupDiscrAux(DISCRIMINANTS, IDX)) [preserves-definedness]
  rule #lookupDiscriminant(_OTHER, _) => 0 [owise, preserves-definedness] // default 0. May be undefined behaviour, though.
  // --------------------------------------------------------------------
  rule #lookupDiscrAux( Discriminant(IDX, RESULT)    _        , IDX) => RESULT
  rule #lookupDiscrAux( _OTHER:Discriminant MORE:Discriminants, IDX) => #lookupDiscrAux(MORE, IDX) [owise]

// ShallowIntBox: not implemented yet
```

### References and Dereferencing

References and de-referencing give rise to another family of `RValue`s.

References can be created using a particular region kind (not used here) and `BorrowKind`.
The `BorrowKind` indicates mutability of the value through the reference, but also provides more find-grained characteristics of mutable references.
These fine-grained borrow kinds are not represented here, as some of them are disallowed in the compiler phase targeted by this semantics, and others related to memory management in lower-level artefacts[^borrowkind].
Therefore, reference values are represented with a simple `Mutability` flag instead of `BorrowKind`

[^borrowkind]: https://doc.rust-lang.org/nightly/nightly-rustc/rustc_middle/mir/enum.BorrowKind.html

```k
  rule <k> rvalueRef(_REGION, KIND, PLACE)
         =>
           typedValue(Reference(0, PLACE, #mutabilityOf(KIND)), TyUnknown, #mutabilityOf(KIND))
       ...
       </k>

  syntax Mutability ::= #mutabilityOf ( BorrowKind ) [function, total]

  rule #mutabilityOf(borrowKindShared)  => mutabilityNot
  rule #mutabilityOf(borrowKindFake(_)) => mutabilityNot // Shallow fake borrow disallowed in late stages
  rule #mutabilityOf(borrowKindMut(_))  => mutabilityMut // all mutable kinds behave equally for us
```

A `CopyForDeref` `RValue` has the semantics of a simple `Use(operandCopy(...))`, except that the compiler guarantees the only use of the copied value will be for dereferencing, which enables optimisations in the borrow checker and in code generation.

```k
  rule <k> rvalueCopyForDeref(PLACE) => rvalueUse(operandCopy(PLACE)) ... </k>
```

The `RValue::AddressOf` operation is very similar to creating a reference, since it also
refers to a given _place_. However, the raw pointer obtained by `AddressOf` can be subject
to casts and pointer arithmetic using `BinOp::Offset`.

```k
  rule <k> rvalueAddressOf(MUT, PLACE)
         =>
           typedValue(PtrLocal(0, PLACE, MUT), TyUnknown, MUT)
           // we should use #alignOf to emulate the address
       ...
       </k>
```

In practice, the `AddressOf` can often be found applied to references that get dereferenced first,
turning a borrowed value into a raw pointer. To shorten out chains of Deref and AddressOf/Reference,
a special rule for this case is applied with higher priority.

```k
  rule <k> rvalueAddressOf(MUT, place(local(I), projectionElemDeref .ProjectionElems))
         =>
           typedValue(refToPtrLocal(getValue(LOCALS, I)), TyUnknown, MUT)
           // we should use #alignOf to emulate the address
       ...
       </k>
       <locals> LOCALS </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])
     andBool isRef(getValue(LOCALS, I))
    [priority(40), preserves-definedness] // valid indexing checked, toPtrLocal can convert the reference

  syntax Bool ::= isRef ( TypedValue ) [function, total]
  // -----------------------------------------------------
  rule isRef(typedValue(Reference(_, _, _), _, _)) => true
  rule isRef(           _OTHER                   ) => false [owise]

  syntax Value ::= refToPtrLocal ( TypedValue ) [function]

  rule refToPtrLocal(typedValue(Reference(OFFSET, PLACE, MUT), _, _)) => PtrLocal(OFFSET, PLACE, MUT)
```

## Type casts

Type casts between a number of different types exist in MIR.

```k
  syntax Evaluation ::= #cast( Evaluation, CastKind, Ty ) [strict(1)]
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
  rule <k> #cast(typedValue(Integer(VAL, WIDTH, _SIGNEDNESS), _, MUT), castKindIntToInt, TY)
          =>
            typedValue(#intAsType(VAL, WIDTH, #numTypeOf({TYPEMAP[TY]}:>TypeInfo)), TY, MUT)
          ...
        </k>
        <types> TYPEMAP </types>
      requires #isIntType({TYPEMAP[TY]}:>TypeInfo)
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

```k
  rule <k> #cast(typedValue(VALUE, TY1, MUT), castKindPtrToPtr, TY2)
          =>
            typedValue(VALUE, TY2, MUT)
          ...
        </k>
        <types> TYPEMAP </types>
      requires #typesCompatible({TYPEMAP[TY1]}:>TypeInfo, {TYPEMAP[TY2]}:>TypeInfo, TYPEMAP)
```

`PointerCoercion` may achieve a simmilar effect, or deal with function and closure pointers, depending on the coercion type:

| CastKind                           | PointerCoercion          | Description                        |
|------------------------------------|--------------------------|-----------------------             |
| PointerCoercion(_, CoercionSource) | ArrayToPointer           | from `*const [T; N]` to `*const T` |
|                                    | Unsize                   | drop size information              |
|                                    | ReifyFnPointer           |                                    |
|                                    | UnsafeFnPointer          |                                    |
|                                    | ClosureFnPointer(Safety) |                                    |
|                                    | DynStar                  | create a dyn* object               |
|                                    | MutToConstPointer        | make a mutable pointer immutable   |


```k
  // not checking whether types are actually compatible (trusting the compiler)
  rule <k> #cast(typedValue(VALUE, _TY, MUT), castKindPointerCoercion(pointerCoercionUnsize), TY)
          =>
            typedValue(VALUE, TY, MUT)
          ...
        </k>
```

### Other casts involving pointers

| CastKind                     | Description |
|------------------------------|-------------|
| PointerExposeProvenance      |             |
| PointerWithExposedProvenance |             |
| FnPtrToPtr                   |             |
| Transmute                    |             |


## Decoding constants from their bytes representation to values

The `Value` sort above operates at a higher level than the bytes representation found in the MIR syntax for constant values.
The bytes have to be interpreted according to the given `TypeInfo` to produce the higher-level value.
This is currently only defined for `PrimitiveType`s (primitive types in MIR).

```k
  syntax Evaluation ::= #decodeConstant ( ConstantKind, Ty, TypeInfo )

  //////////////////////////////////////////////////////////////////////////////////////
  // decoding the correct amount of bytes depending on base type size

  // Boolean: should be one byte with value one or zero
  rule <k> #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), TY, typeInfoPrimitiveType(primTypeBool))
        => typedValue(BoolVal(false), TY, mutabilityNot) ... </k>
    requires 0 ==Int Bytes2Int(BYTES, LE, Unsigned) andBool lengthBytes(BYTES) ==Int 1

  rule <k> #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), TY, typeInfoPrimitiveType(primTypeBool))
        => typedValue(BoolVal(true), TY, mutabilityNot) ... </k>
    requires 1 ==Int Bytes2Int(BYTES, LE, Unsigned) andBool lengthBytes(BYTES) ==Int 1

  // Integer: handled in separate module for numeric operations
  rule <k> #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), TY, TYPEINFO)
        => typedValue(#decodeInteger(BYTES, #intTypeOf(TYPEINFO)), TY, mutabilityNot) ... </k>
    requires #isIntType(TYPEINFO)
     andBool lengthBytes(BYTES) ==K #bitWidth(#intTypeOf(TYPEINFO)) /Int 8
     [preserves-definedness]

  // zero-sized struct types
  rule <k> #decodeConstant(constantKindZeroSized, TY, typeInfoStructType(_, _, _))
        => typedValue(Aggregate(variantIdx(0), .List), TY, mutabilityNot) ... </k>

  // TODO Char type
  // rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), typeInfoPrimitiveType(primTypeChar)) => typedValue(Str(...), TY, mutabilityNot)
  // TODO Float decoding: not supported natively in K

  // unimplemented cases stored as thunks
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
  rule onInt(binOpAdd, X, Y)          => X +Int Y
  rule onInt(binOpAddUnchecked, X, Y) => X +Int Y
  rule onInt(binOpSub, X, Y)          => X -Int Y
  rule onInt(binOpSubUnchecked, X, Y) => X -Int Y
  rule onInt(binOpMul, X, Y)          => X *Int Y
  rule onInt(binOpMulUnchecked, X, Y) => X *Int Y
  rule onInt(binOpDiv, X, Y)          => X /Int Y
    requires Y =/=Int 0
  rule onInt(binOpRem, X, Y)          => X %Int Y
    requires Y =/=Int 0
  // operation undefined otherwise

  // error cases for isArithmetic(BOP):
  // * arguments must be Numbers

  // Checked operations return a pair of the truncated value and an overflow flag
  // signed numbers: must check for wrap-around (operation specific)
  rule #applyBinOp(
          BOP,
          typedValue(Integer(ARG1, WIDTH, true), _, _), //signed
          typedValue(Integer(ARG2, WIDTH, true), _, _),
          true) // checked
    =>
       typedValue(
          Aggregate(
            variantIdx(0),
            ListItem(typedValue(Integer(truncate(onInt(BOP, ARG1, ARG2), WIDTH, Signed), WIDTH, true), TyUnknown, mutabilityNot))
            ListItem(
              typedValue(
                BoolVal(
                  // overflow: compare with and without truncation
                  truncate(onInt(BOP, ARG1, ARG2), WIDTH, Signed) =/=Int onInt(BOP, ARG1, ARG2)
                ),
                TyUnknown,
                mutabilityNot
              )
            )
          ),
          TyUnknown,
          mutabilityNot
        )
    requires isArithmetic(BOP)
    [preserves-definedness]

  // unsigned numbers: simple overflow check using a bit mask
  rule #applyBinOp(
          BOP,
          typedValue(Integer(ARG1, WIDTH, false), _, _), // unsigned
          typedValue(Integer(ARG2, WIDTH, false), _, _),
          true) // checked
    =>
       typedValue(
          Aggregate(
            variantIdx(0),
            ListItem(typedValue(Integer(truncate(onInt(BOP, ARG1, ARG2), WIDTH, Unsigned), WIDTH, false), TyUnknown, mutabilityNot))
            ListItem(
              typedValue(
                BoolVal(
                  // overflow flag: compare to truncated result
                  truncate(onInt(BOP, ARG1, ARG2), WIDTH, Unsigned) =/=Int onInt(BOP, ARG1, ARG2)
                ),
                TyUnknown,
                mutabilityNot
              )
            )
          ),
          TyUnknown,
          mutabilityNot
        )
    requires isArithmetic(BOP)
    [preserves-definedness]

  // Unchecked operations signal undefined behaviour on overflow. The checks are the same as for the flags above.

  rule #applyBinOp(
          BOP,
          typedValue(Integer(ARG1, WIDTH, true), _, _), // signed
          typedValue(Integer(ARG2, WIDTH, true), _, _),
          false) // unchecked
    => typedValue(Integer(truncate(onInt(BOP, ARG1, ARG2), WIDTH, Signed), WIDTH, true), TyUnknown, mutabilityNot)
    requires isArithmetic(BOP)
    // infinite precision result must equal truncated result
     andBool truncate(onInt(BOP, ARG1, ARG2), WIDTH, Signed) ==Int onInt(BOP, ARG1, ARG2)
    [preserves-definedness]

  // unsigned numbers: simple overflow check using a bit mask
  rule #applyBinOp(
          BOP,
          typedValue(Integer(ARG1, WIDTH, false), _, _), // unsigned
          typedValue(Integer(ARG2, WIDTH, false), _, _),
          false) // unchecked
    => typedValue(Integer(truncate(onInt(BOP, ARG1, ARG2), WIDTH, Unsigned), WIDTH, false), TyUnknown, mutabilityNot)
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

  rule #applyBinOp(OP, typedValue(Integer(VAL1, WIDTH, SIGN), _, _), typedValue(Integer(VAL2, WIDTH, SIGN), _, _), _)
      =>
        typedValue(BoolVal(cmpOpInt(OP, VAL1, VAL2)), TyUnknown, mutabilityNot)
    requires isComparison(OP)
    [preserves-definedness] // OP known to be a comparison

  rule #applyBinOp(OP, typedValue(BoolVal(VAL1), _, _), typedValue(BoolVal(VAL2), _, _), _)
      =>
        typedValue(BoolVal(cmpOpBool(OP, VAL1, VAL2)), TyUnknown, mutabilityNot)
    requires isComparison(OP)
    [preserves-definedness] // OP known to be a comparison
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

  rule #applyBinOp(binOpCmp, typedValue(Integer(VAL1, WIDTH, SIGN), _, _), typedValue(Integer(VAL2, WIDTH, SIGN), _, _), _)
      =>
        typedValue(Integer(cmpInt(VAL1, VAL2), 8, true), TyUnknown, mutabilityNot)

  rule #applyBinOp(binOpCmp, typedValue(BoolVal(VAL1), _, _), typedValue(BoolVal(VAL2), _, _), _)
      =>
        typedValue(Integer(cmpBool(VAL1, VAL2), 8, true), TyUnknown, mutabilityNot)
```

#### Unary operations on Boolean and integral values

The `unOpNeg` operation only works signed integral (and floating point) numbers.
An overflow can happen when negating the minimal representable integral value (in the given `WIDTH`).
The semantics of the operation in this case is to wrap around (with the given bit width).

```k
  rule <k> #applyUnOp(unOpNeg, typedValue(Integer(VAL, WIDTH, true), TY, _))
          =>
            typedValue(Integer(truncate(0 -Int VAL, WIDTH, Signed), WIDTH, true), TY, mutabilityNot)
        ...
        </k>

  // TODO add rule for Floats once they are supported.
```

The `unOpNot` operation works on boolean and integral values, with the usual semantics for booleans and a bitwise semantics for integral values (overflows cannot occur).

```k
  rule <k> #applyUnOp(unOpNot, typedValue(BoolVal(VAL), TY, _))
          =>
            typedValue(BoolVal(notBool VAL), TY, mutabilityNot)
        ...
        </k>

  rule <k> #applyUnOp(unOpNot, typedValue(Integer(VAL, WIDTH, true), TY, _))
          =>
            typedValue(Integer(truncate(~Int VAL, WIDTH, Signed), WIDTH, true), TY, mutabilityNot)
        ...
        </k>

  rule <k> #applyUnOp(unOpNot, typedValue(Integer(VAL, WIDTH, false), TY, _))
          =>
            typedValue(Integer(truncate(~Int VAL, WIDTH, Unsigned), WIDTH, false), TY, mutabilityNot)
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
          typedValue(Integer(ARG1, WIDTH, SIGNED), TY, _),
          typedValue(Integer(ARG2, WIDTH, SIGNED), TY, _),
          false) // unchecked
    =>
       typedValue(
          Integer(onInt(BOP, ARG1, ARG2), WIDTH, SIGNED),
          TY,
          mutabilityNot
        )
    requires isBitwise(BOP)
    [preserves-definedness]

  rule #applyBinOp(
          BOP,
          typedValue(BoolVal(ARG1), TY, _),
          typedValue(BoolVal(ARG2), TY, _),
          false) // unchecked
    =>
       typedValue(
          BoolVal(onBool(BOP, ARG1, ARG2)),
          TY,
          mutabilityNot
        )
    requires isBitwise(BOP)
    [preserves-definedness]

  rule #applyBinOp(
          BOP,
          typedValue(Integer(ARG1, WIDTH, false), TY, _),
          typedValue(Integer(ARG2, _, _), _, _),
          false) // unchecked
    =>
       typedValue(
          Integer(truncate(onShift(BOP, ARG1, ARG2, WIDTH), WIDTH, Unsigned), WIDTH, false),
          TY,
          mutabilityNot
        )
    requires isShift(BOP) andBool ((notBool isUncheckedShift(BOP)) orBool ARG2 <Int WIDTH)
    [preserves-definedness]

  rule #applyBinOp(
          BOP,
          typedValue(Integer(ARG1, WIDTH, true), TY, _),
          typedValue(Integer(ARG2, _, _), _, _),
          false) // unchecked
    =>
       typedValue(
          Integer(truncate(onShift(BOP, ARG1, ARG2, WIDTH), WIDTH, Signed), WIDTH, true),
          TY,
          mutabilityNot
        )
    requires isShift(BOP) andBool ((notBool isUncheckedShift(BOP)) orBool ARG2 <Int WIDTH)
    [preserves-definedness]
```


#### Nullary operations for activating certain checks

`nullOpUbChecks` is supposed to return `BoolVal(true)` if checks for undefined behaviour were activated in the compilation.
For our MIR semantics this means to either retain this information (which we don't) or to decide whether or not these checks are useful and should be active during execution.

One important use case of `UbChecks` is to determine overflows in unchecked arithmetic operations.
Since our arithmetic operations signal undefined behaviour on overflow independently, the value returned by `UbChecks` is `false` for now.

```k
  rule <k> rvalueNullaryOp(nullOpUbChecks, _) => typedValue(BoolVal(false), TyUnknown, mutabilityNot) ... </k>
```

#### "Nullary" operations reifying type information

`nullOpSizeOf`
`nullOpAlignOf`
`nullOpOffsetOf(VariantAndFieldIndices)`

```k
// FIXME: 64 is hardcoded since usize not supported
rule <k> rvalueNullaryOp(nullOpAlignOf, TY)
      =>
         typedValue(
           Integer(#alignOf({TYPEMAP[TY]}:>TypeInfo), 64, false),
           TyUnknown,
           mutabilityNot
         )
         ...
     </k>
     <types> TYPEMAP </types>
    requires TY in_keys(TYPEMAP)
     andBool isTypeInfo(TYPEMAP[TY])
```

#### Other operations

The unary operation `unOpPtrMetadata`, when given a reference to an array or slice, will return the array length of the slice length (which is dynamic, not statically known), as a `usize`.

```k
  rule <k> #applyUnOp(unOpPtrMetadata, typedValue(Reference(OFFSET, place(local(I), PROJECTIONS), _), _, _))
        => #traverseProjection(toLocal(I), getValue(LOCALS, I), PROJECTIONS, .Contexts)
        ~> #readProjection(false)
        ~> #arrayLength()
        ...
       </k>
       <locals> LOCALS </locals>
    requires OFFSET ==Int 0
     andBool 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])
    [preserves-definedness] // LOCALS indexing checked

  rule <k> #applyUnOp(unOpPtrMetadata, typedValue(Reference(OFFSET, place(LOCAL, PROJECTIONS), _), _, _))
        => #traverseProjection(toStack(OFFSET, LOCAL), #localFromFrame({STACK[OFFSET -Int 1]}:>StackFrame, LOCAL, OFFSET), PROJECTIONS, .Contexts)
        ~> #readProjection(false)
        ~> #arrayLength()
        ...
       </k>
       <stack> STACK </stack>
    requires 0 <Int OFFSET
     andBool OFFSET <=Int size(STACK)
     andBool isStackFrame(STACK[OFFSET -Int 1])

  syntax KItem ::= #arrayLength()

  rule <k> typedValue(Range(LIST), _, _) ~> #arrayLength() => typedValue(Integer(size(LIST), 64, false), TyUnknown, mutabilityNot) ... </k>
```



`binOpOffset`

```k
endmodule
```
