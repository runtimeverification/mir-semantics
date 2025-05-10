# Handling Data for MIR Execution

This module addresses all aspects of handling "values" i.e., data, at runtime during MIR execution.


```k
requires "../ty.md"
requires "../body.md"
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
  imports KMIR-CONFIGURATION
```

## Operations on local variables

### Evaluating Items to `TypedValue` or `TypedLocal`

Some built-in operations (`RValue` or type casts) use constructs that will evaluate to a value of sort `TypedValue`.
The basic operations of reading and writing those values can use K's "heating" and "cooling" rules to describe their evaluation.
Other uses of heating and cooling are to _read_ local variables as operands. This may include `Moved` locals or uninitialised `NewLocal`s (as error cases). Therefore we use the supersort `TypedLocal` of `TypedValue` as the `Result` sort.

```k
  syntax Evaluation ::= TypedLocal // other sorts are added at the first use site

  syntax KResult ::= TypedLocal
```

### Errors Related to Accessing Local Variables

Access to a `TypedLocal` (whether reading or writing) may fail for a number of reasons.
It is an error to read a `Moved` local or an uninitialised `NewLocal`.
Also, locals are accessed via their index in list `<locals>` in a stack frame, which may be out of bounds
(but the compiler should guarantee that all local indexes are valid).
Types (`Ty`, an opaque number assigned by the Stable MIR extraction) are not checked, the local's type is used.

### Reading Operands (Local Variables and Constants)

```k
  syntax Evaluation ::= Operand
```

_Read_ access to `Operand`s (which may be local values) may have similar errors as write access.

Constant operands are simply decoded according to their type.

```k
  rule <k> operandConstant(constOperand(_, _, mirConst(KIND, TY, _)))
        =>
           typedValue(#decodeConstant(KIND, {TYPEMAP[TY]}:>TypeInfo), TY, mutabilityNot)
        ...
      </k>
      <types> TYPEMAP </types>
    requires TY in_keys(TYPEMAP)
     andBool isTypeInfo(TYPEMAP[TY])
    [preserves-definedness] // valid Map lookup checked
```

The code which copies/moves function arguments into the locals of a stack frame works
in a similar way, but accesses the locals of the _caller_ instead of the locals of the
current function.

Reading a _Copied_ operand means to simply put it in the K sequence. Obviously, a _Moved_
local value cannot be read, though, and the value should be initialised.

```k
  rule <k> operandCopy(place(local(I), .ProjectionElems))
        =>
           LOCALS[I]
        ...
       </k>
       <locals> LOCALS </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])
    [preserves-definedness] // valid list indexing checked

    // error cases (NewLocal, Moved) get stuck
```

Reading an `Operand` using `operandMove` has to invalidate the respective local, to prevent any
further access. Apart from that, the same caveats apply as for operands that are _copied_.

```k
  rule <k> operandMove(place(local(I), .ProjectionElems))
        =>
           LOCALS[I]
        ...
       </k>
       <locals> LOCALS => LOCALS[I <- Moved]</locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])
    [preserves-definedness] // valid list indexing checked

    // error cases (NewLocal, Moved) get stuck
```

#### Reading places with projections

Reading an `Operand` above is only implemented for reading a `Local`, without any projecting modifications.
Projections operate on the data stored in the `TypedLocal` and are therefore specific to the `Value` implementation. The following function provides an abstraction for reading with projections, its equations are co-located with the `Value` implementation(s).
A projection can only be applied to an initialised value, so this operation requires `TypedValue`.

```k
  rule <k> operandCopy(place(local(I), PROJECTIONS))
        =>
           #readProjection({LOCALS[I]}:>TypedValue, PROJECTIONS)
        ...
       </k>
       <locals> LOCALS </locals>
    requires PROJECTIONS =/=K .ProjectionElems
     andBool 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])
    [preserves-definedness] // valid list indexing checked

  syntax KItem ::= #readProjection ( TypedValue , ProjectionElems )
```

The `ProjectionElems` list contains a sequence of projections which is applied (left-to-right) to the value in a `TypedLocal` to obtain a derived value or component thereof. The `TypedLocal` argument is there for the purpose of recursion over the projections. We don't expect the operation to apply to an empty projection `.ProjectionElems`, the base case exists for the recursion.

```k
  rule <k> #readProjection(VAL, .ProjectionElems) => VAL ... </k>
```

A `Field` access projection operates on `struct`s and tuples, which are represented as `Aggregate` values. The field is numbered from zero (in source order), and the field type is provided (not checked here).

```k
  rule <k> #readProjection(
              typedValue(Aggregate(_, ARGS), _, _),
              projectionElemField(fieldIdx(I), _TY) PROJS
            )
         =>
           #readProjection({ARGS[I]}:>TypedValue, PROJS)
       ...
       </k>
    requires 0 <=Int I
     andBool I <Int size(ARGS)
     andBool isTypedValue(ARGS[I])
    [preserves-definedness] // valid list indexing checked
```

An `Index` projection operates on an array or slice (`Range`) value, to access an element of the array. The index can either be read from another operand, or it can be a constant (`ConstantIndex`).

For a normal `Index` projection, the index is read from a given local which is expected to hold a `usize` value in the valid range between 0 and the array/slice length.

```k
  rule <k> #readProjection(
              typedValue(Range(ELEMENTS), _, _),
              projectionElemIndex(local(LOCAL)) PROJS
           )
          => #readProjection({ELEMENTS[#expectUsize({LOCALS[LOCAL]}:>TypedValue)]}:>TypedValue, PROJS)
        ...
        </k>
        <locals> LOCALS </locals>
    requires 0 <=Int LOCAL
     andBool LOCAL <Int size(LOCALS)
     andBool isTypedValue(LOCALS[LOCAL])
     andBool isInt(#expectUsize({LOCALS[LOCAL]}:>TypedValue))
     andBool 0 <=Int #expectUsize({LOCALS[LOCAL]}:>TypedValue)
     andBool #expectUsize({LOCALS[LOCAL]}:>TypedValue) <Int size(ELEMENTS)
     andBool isTypedValue(ELEMENTS[#expectUsize({LOCALS[LOCAL]}:>TypedValue)])
    [preserves-definedness] // index checked, valid Int can be read, ELEMENT indexable

  syntax Int ::= #expectUsize ( TypedValue ) [function]

  rule #expectUsize(typedValue(Integer(I, 64, false), _, _)) => I

  syntax MIRError ::= MIRIndexError ( List , Local )
                    | MIRConstantIndexError ( List , Int )

  rule <k> #readProjection(
              typedValue(Range(ELEMENTS), _, _),
              projectionElemIndex(LOCAL) _PROJS
           )
          => MIRIndexError(ELEMENTS, LOCAL)
        ...
        </k>
      [owise]
```

In case of a `ConstantIndex`, the index is provided as an immediate value, together with a "minimum length" of the array/slice and a flag indicating whether indexing should be performed from the end (in which case the minimum length must be exact).

```k
  rule <k> #readProjection(
              typedValue(Range(ELEMENTS), _, _),
              projectionElemConstantIndex(OFFSET:Int, _MINLEN, false) PROJS
           )
          => #readProjection({ELEMENTS[OFFSET]}:>TypedValue, PROJS)
        ...
        </k>
    requires 0 <=Int OFFSET
     andBool OFFSET <Int size(ELEMENTS)
     andBool isTypedValue(ELEMENTS[OFFSET])


  rule <k> #readProjection(
              typedValue(Range(ELEMENTS), _, _),
              projectionElemConstantIndex(OFFSET:Int, MINLEN, true) PROJS
           )
          => #readProjection({ELEMENTS[0 -Int OFFSET]}:>TypedValue, PROJS)
        ...
        </k>
    requires 0 <Int OFFSET
     andBool OFFSET <=Int size(ELEMENTS)
     andBool MINLEN ==Int size(ELEMENTS)
     andBool isTypedValue(ELEMENTS[0 -Int OFFSET])

  rule <k> #readProjection(
              typedValue(Range(ELEMENTS), _, _),
              projectionElemConstantIndex(OFFSET:Int, _, FROM_END) _PROJS
           )
          => MIRConstantIndexError(ELEMENTS, #if FROM_END #then 0 -Int OFFSET #else OFFSET #fi)
        ...
        </k>
      [owise]
```

A `Deref` projection operates on `Reference`s that refer to locals in the same or an enclosing stack frame, indicated by the stack height in the `Reference` value. `Deref` reads the referred place (and may proceed with further projections).

In the simplest case, the reference refers to a local in the same stack frame (height 0), which is directly read.

```k
  rule <k> #readProjection(
              typedValue(Reference(0, place(local(I:Int), PLACEPROJS:ProjectionElems), _), _, _),
              projectionElemDeref PROJS:ProjectionElems
            )
         =>
           #readProjection({LOCALS[I]}:>TypedValue, appendP(PLACEPROJS, PROJS))
       ...
       </k>
       <locals> LOCALS </locals>
    requires 0 <Int I
     andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])
    [preserves-definedness] // valid list indexing checked

  // Moved and NewLocal get stuck

  // why do we not have this automatically for user-defined lists?
  syntax ProjectionElems ::= appendP ( ProjectionElems , ProjectionElems ) [function, total]
  rule appendP(.ProjectionElems, TAIL) => TAIL
  rule appendP(X:ProjectionElem REST:ProjectionElems, TAIL) => X appendP(REST, TAIL)

```

For references to enclosing stack frames, the local must be retrieved from the respective stack frame.
An important prerequisite of this rule is that when passing references to a callee as arguments, the stack height must be adjusted.

```k
  rule <k> #readProjection(
              typedValue(Reference(FRAME, place(LOCAL:Local, PLACEPROJS), _), _, _),
              projectionElemDeref PROJS
            )
         =>
           #readProjection(
              {#localFromFrame({STACK[FRAME -Int 1]}:>StackFrame, LOCAL, FRAME)}:>TypedValue,
              appendP(PLACEPROJS, PROJS)
            )
       ...
       </k>
       <stack> STACK </stack>
    requires 0 <Int FRAME
     andBool FRAME <=Int size(STACK)
     andBool isStackFrame(STACK[FRAME -Int 1])
     andBool isTypedValue(#localFromFrame({STACK[FRAME -Int 1]}:>StackFrame, LOCAL, FRAME))
    [preserves-definedness] // valid list indexing checked

    // TODO case of MovedLocal and NewLocal

    syntax TypedLocal ::= #localFromFrame ( StackFrame, Local, Int ) [function]

    rule #localFromFrame(StackFrame(... locals: LOCALS), local(I:Int), OFFSET) => #adjustRef({LOCALS[I]}:>TypedLocal, OFFSET)
      requires 0 <=Int I
       andBool I <Int size(LOCALS)
       andBool isTypedLocal(LOCALS[I])
      [preserves-definedness] // valid list indexing checked

  syntax TypedLocal ::= #incrementRef ( TypedLocal )  [function, total]
                      | #decrementRef ( TypedLocal )  [function, total]
                      | #adjustRef (TypedLocal, Int ) [function, total]

  rule #adjustRef(typedValue(Reference(HEIGHT, PLACE, REFMUT), TY, MUT), OFFSET)
    => typedValue(Reference(HEIGHT +Int OFFSET, PLACE, REFMUT), TY, MUT)
  rule #adjustRef(TL, _) => TL [owise]

  rule #incrementRef(TL) => #adjustRef(TL, 1)
  rule #decrementRef(TL) => #adjustRef(TL, -1)
```

#### _Moving_ Operands Under Projections

When an operand is `Moved` by the read, the original has to be invalidated. In case of a projected value, this is a write operation nested in the data that is being read. The `#projectedUpdate` function for writing projected values is used (defined below).
In contrast to regular write operations, the value does not have to be _mutable_ in order for `Moved` to be written. The `#projectedUpdate` operation therefore carries a `force` flag to override the mutability check.


```k
  rule <k> operandMove(place(local(I) #as LOCAL, PROJECTIONS))
        => // read first, then write moved marker (use type from before)
           #readProjection({LOCALS[I]}:>TypedValue, PROJECTIONS) ~>
           #markMoved({LOCALS[I]}:>TypedLocal, LOCAL, PROJECTIONS)
        ...
       </k>
       <locals> LOCALS </locals>
    requires PROJECTIONS =/=K .ProjectionElems
     andBool 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])
    [preserves-definedness] // valid list indexing checked

  // TODO case of MovedLocal and NewLocal

  syntax KItem ::= #markMoved ( TypedLocal, Local, ProjectionElems )

  rule <k> VAL:TypedLocal ~> #markMoved(OLDLOCAL, local(I), PROJECTIONS) ~> CONT
        =>
           #projectedUpdate(makeProjectedUpdate(toLocal(I), OLDLOCAL, PROJECTIONS, .Contexts, true, STACK, LOCALS), Moved)
           ~> VAL
           ~> CONT
       </k>
       <stack> STACK </stack>
       <locals> LOCALS </locals>
    [preserves-definedness] // projections already used when reading
```


### Setting Local Variables

The `#setLocalValue` operation writes a `TypedLocal` value to a given `Place` within the `List` of local variables currently on top of the stack. This may fail because a local may not be accessible, moved away, or not mutable.

```k
  syntax KItem ::= #setLocalValue( Place, Evaluation ) [strict(2)]

  // error cases (not checked, just matched below to prevent them)

  // no type check, the local's type is used.

  // setting a non-mutable local that is initialised is an error

  // if all is well, write the value
  // mutable local
  rule <k> #setLocalValue(place(local(I), .ProjectionElems), typedValue(VAL:Value, _, _ ))
          =>
           .K
          ...
       </k>
       <locals>
          LOCALS => LOCALS[I <- typedValue(VAL, tyOfLocal({LOCALS[I]}:>TypedLocal), mutabilityMut)]
       </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])
     andBool mutabilityOf({LOCALS[I]}:>TypedLocal) ==K mutabilityMut
    [preserves-definedness] // valid list indexing checked

  // non-mutable uninitialised values are mutable once
  rule <k> #setLocalValue(place(local(I), .ProjectionElems), typedValue(VAL:Value, _, _ ))
          =>
           .K
          ...
       </k>
       <locals>
          LOCALS => LOCALS[I <- typedValue(VAL, tyOfLocal({LOCALS[I]}:>TypedLocal), mutabilityOf({LOCALS[I]}:>TypedLocal))]
       </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isNewLocal(LOCALS[I])
    [preserves-definedness] // valid list indexing checked

  // reusing a local which was Moved is allowed
  rule <k> #setLocalValue(place(local(I), .ProjectionElems), typedValue(VAL:Value, _, _ ))
          =>
           .K
          ...
       </k>
       <locals>
          LOCALS => LOCALS[I <- typedValue(VAL, tyOfLocal({LOCALS[I]}:>TypedLocal), mutabilityOf({LOCALS[I]}:>TypedLocal))]
       </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isMovedLocal(LOCALS[I])
    [preserves-definedness] // valid list indexing checked
```

### Writing Data to Places With Projections

Write operations to places that include (a chain of) projections are handled by a special rewrite symbol `#projectedUpdate`.

```k
  syntax KItem ::= #projectedUpdate ( ProjectedUpdate , TypedLocal )
  syntax ProjectedUpdate ::= makeProjectedUpdate(WriteTo, TypedLocal, ProjectionElems, Contexts, Bool, List, List) [function] // total
                           | ProjectedUpdate(WriteTo, Contexts, Bool)

  rule <k> #setLocalValue(place(local(I), PROJ), VAL)
        => #projectedUpdate(makeProjectedUpdate(toLocal(I), {LOCALS[I]}:>TypedLocal, PROJ, .Contexts, false, STACK, LOCALS), VAL)
       ...
       </k>
       <stack> STACK </stack>
       <locals> LOCALS </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool PROJ =/=K .ProjectionElems
     andBool isTypedValue(LOCALS[I])
    [preserves-definedness]

```

A `Deref` projection in the projections list changes the target of the write operation, while `Field` updates change the value that is being written (updating just one field of it), recursively. `Index`ing operations may have to read an index from another local, which is another rewrite. Therefore a simple update _function_ cannot cater for all projections, neither can a rewrite (the context of the recursion would need to be held explicitly).

The solution is to use rewrite operations in a downward pass through the projections, and build the resulting updated value in an upward pass with information collected in the downward one.

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

  rule makeProjectedUpdate(DEST, typedValue(Aggregate(IDX, ARGS), TY, MUT), projectionElemField(fieldIdx(I), _) PROJS,                            CTXTS, FORCE, STACK, LOCALS)
    => makeProjectedUpdate(DEST, {ARGS[I]}:>TypedLocal,                                                         PROJS, CtxField(TY, IDX, ARGS, I) CTXTS, FORCE, STACK, LOCALS)
    requires 0 <=Int I
     andBool I <Int size(ARGS)
     andBool isTypedLocal(ARGS[I])
     andBool (FORCE orBool MUT ==K mutabilityMut)
     [preserves-definedness] // valid list indexing checked

  rule makeProjectedUpdate(DEST, typedValue(Range(ELEMENTS), TY, MUT),                              projectionElemIndex(local(LOCAL)) PROJS,                                                                   CTXTS, FORCE, STACK, LOCALS)
    => makeProjectedUpdate(DEST, {ELEMENTS[#expectUsize({LOCALS[LOCAL]}:>TypedValue)]}:>TypedValue,                                   PROJS, CtxIndex(TY, ELEMENTS, #expectUsize({LOCALS[LOCAL]}:>TypedValue)) CTXTS, FORCE, STACK, LOCALS)
    requires 0 <=Int LOCAL
     andBool LOCAL <Int size(LOCALS)
     andBool isTypedValue(LOCALS[LOCAL])
     andBool isInt(#expectUsize({LOCALS[LOCAL]}:>TypedValue))
     andBool 0 <=Int #expectUsize({LOCALS[LOCAL]}:>TypedValue)
     andBool #expectUsize({LOCALS[LOCAL]}:>TypedValue) <Int size(ELEMENTS)
     andBool isTypedValue(ELEMENTS[#expectUsize({LOCALS[LOCAL]}:>TypedValue)])
     andBool (FORCE orBool MUT ==K mutabilityMut)
    [preserves-definedness] // index checked, valid Int can be read, ELEMENT indexable and writeable or forced

  rule makeProjectedUpdate(DEST, typedValue(Range(ELEMENTS), TY, MUT), projectionElemConstantIndex(OFFSET:Int, _MINLEN, false) PROJS,                                CTXTS, FORCE, STACK, LOCALS)
    => makeProjectedUpdate(DEST, {ELEMENTS[OFFSET]}:>TypedValue,                                                               PROJS, CtxIndex(TY, ELEMENTS, OFFSET) CTXTS, FORCE, STACK, LOCALS)
    requires 0 <=Int OFFSET
     andBool OFFSET <Int size(ELEMENTS)
     andBool isTypedValue(ELEMENTS[OFFSET])
     andBool (FORCE orBool MUT ==K mutabilityMut)
    [preserves-definedness] // ELEMENT indexable and writeable or forced

  rule makeProjectedUpdate(DEST, typedValue(Range(ELEMENTS), TY, MUT), projectionElemConstantIndex(OFFSET:Int, MINLEN, true) PROJS,                                            CTXTS, FORCE, STACK, LOCALS)
    => makeProjectedUpdate(DEST, {ELEMENTS[OFFSET]}:>TypedValue,                                                             PROJS, CtxIndex(TY, ELEMENTS, MINLEN -Int OFFSET) CTXTS, FORCE, STACK, LOCALS)
    requires 0 <Int OFFSET
     andBool OFFSET <=Int MINLEN
     andBool MINLEN ==Int size(ELEMENTS) // assumed for valid MIR code
     andBool isTypedValue(ELEMENTS[MINLEN -Int OFFSET])
     andBool (FORCE orBool MUT ==K mutabilityMut)
    [preserves-definedness] // ELEMENT indexable and writeable or forced

  rule makeProjectedUpdate(_DEST,                  typedValue(Reference(OFFSET, place(LOCAL, PLACEPROJ), MUT), _, _),  projectionElemDeref PROJS, _CTXTS,    FORCE, STACK, LOCALS)
    => makeProjectedUpdate(toStack(OFFSET, LOCAL), #localFromFrame({STACK[OFFSET -Int 1]}:>StackFrame, LOCAL, OFFSET), appendP(PLACEPROJ, PROJS), .Contexts, FORCE, STACK, LOCALS)
    requires 0 <Int OFFSET
     andBool OFFSET <=Int size(STACK)
     andBool isStackFrame(STACK[OFFSET -Int 1])
     andBool (FORCE orBool MUT ==K mutabilityMut)
    [preserves-definedness]

  rule makeProjectedUpdate(_DEST,      typedValue(Reference(OFFSET, place(local(I), PLACEPROJ), MUT), _, _), projectionElemDeref PROJS, _CTXTS,    FORCE, STACK, LOCALS)
    => makeProjectedUpdate(toLocal(I), {LOCALS[I]}:>TypedLocal,                                              appendP(PLACEPROJ, PROJS), .Contexts, FORCE, STACK, LOCALS)
    requires OFFSET ==Int 0
     andBool 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool (FORCE orBool MUT ==K mutabilityMut)
    [preserves-definedness]

  rule makeProjectedUpdate(DEST, _:TypedValue, .ProjectionElems, CONTEXTS, FORCE, _, _)
    => ProjectedUpdate(DEST, CONTEXTS, FORCE)

  rule <k> #projectedUpdate(ProjectedUpdate(toLocal(I), CONTEXTS, false), NEW)
        => #setLocalValue(place(local(I), .ProjectionElems), #buildUpdate(NEW, CONTEXTS))
        ...
       </k>
     [preserves-definedness] // valid conmtext ensured upon context construction

  rule <k> #projectedUpdate(ProjectedUpdate(toLocal(I), CONTEXTS, true), NEW)
        => #forceSetLocal(local(I), #buildUpdate(NEW, CONTEXTS))
        ...
       </k>
     [preserves-definedness] // valid conmtext ensured upon context construction

  syntax KItem ::= #forceSetLocal ( Local , TypedLocal )

  // #forceSetLocal sets the given value unconditionally (to write Moved values)
  rule <k> #forceSetLocal(local(I), VALUE) => .K ... </k>
       <locals> LOCALS => LOCALS[I <- VALUE] </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
    [preserves-definedness] // valid list indexing checked

  rule <k> #projectedUpdate(ProjectedUpdate(toStack(FRAME, local(I)), CONTEXTS, _), NEW) => .K ... </k>
       <stack> STACK => STACK[(FRAME -Int 1) <- #updateStackLocal({STACK[FRAME -Int 1]}:>StackFrame, I, #buildUpdate(NEW, CONTEXTS)) ] </stack>
    requires 0 <Int FRAME
     andBool FRAME <=Int size(STACK)
     andBool isStackFrame(STACK[FRAME -Int 1])

  syntax StackFrame ::= #updateStackLocal ( StackFrame, Int, TypedLocal ) [function]

  rule #updateStackLocal(StackFrame(CALLER, DEST, TARGET, UNWIND, LOCALS), I, Moved)
      => StackFrame(CALLER, DEST, TARGET, UNWIND, LOCALS[I <- Moved])
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
    [preserves-definedness]

  rule #updateStackLocal(StackFrame(CALLER, DEST, TARGET, UNWIND, LOCALS), I, typedValue(VAL, _, _))
      => StackFrame(CALLER, DEST, TARGET, UNWIND, LOCALS[I <- typedValue(VAL, tyOfLocal({LOCALS[I]}:>TypedLocal), mutabilityMut)])
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
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

  rule  <k> rvalueUse(OPERAND) => OPERAND ... </k>

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
Besides their list of arguments, `enum`s also carry a `VariantIdx` indicating which variant was used. For tuples and `struct`s, this index is always 0.

Tuples, `struct`s, and `enum`s are built as `Aggregate` values with a list of argument values.
For `enums`, the `VariantIdx` is set, and for `struct`s and `enum`s, the type ID (`Ty`) is retrieved from a special mapping of `AdtDef` to `Ty`.

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

  rule <k> ARGS:List ~> #mkAggregate(_OTHERKIND)
        =>
            typedValue(Aggregate(variantIdx(0), ARGS), TyUnknown, mutabilityNot)
        ...
       </k>
    [owise]


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
This variant index is used to look up the _discriminant_ from a table in the type metadata during evaluation of the `Rvalue::Discriminant`. Note that the discriminant may be different from the variant index for user-defined discriminants and uninhabited variants.

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
The `BorrowKind` indicates mutability of the value through the reference, but also provides more find-grained characteristics of mutable references. These fine-grained borrow kinds are not represented here, as some of them are disallowed in the compiler phase targeted by this semantics, and others related to memory management in lower-level artefacts[^borrowkind]. Therefore, reference values are represented with a simple `Mutability` flag instead of `BorrowKind`

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

// AddressOf: not implemented yet
```

## Type casts

Type casts between a number of different types exist in MIR. We implement a type
cast from a `TypedLocal` to another when it is followed by a `#cast` item,
rewriting `typedLocal(...) ~> #cast(...) ~> REST` to `typedLocal(...) ~> REST`.

```k
  syntax KItem ::= #cast( Evaluation, CastKind, Ty ) [strict(1)]

  syntax MIRError ::= CastError

  syntax CastError ::= UnknownCastTarget ( Ty , Map )
                     | UnexpectedCastTarget ( CastKind, TypeInfo )
                     | UnexpectedCastArgument ( TypedLocal, CastKind )
                     | CastNotimplemented ( CastKind )

```

### Integer Type Casts

Casts between signed and unsigned integral numbers of different width exist, with a
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

Error cases for `castKindIntToInt`
* unknown target type (not in `types`)
* target type is not an `Int` type
* value is not a `Integer`

```k
  rule <k> #cast(_, castKindIntToInt, TY) => UnknownCastTarget(TY, TYPEMAP) ... </k>
       <types> TYPEMAP </types>
    requires notBool isTypeInfo(TYPEMAP[TY])
    [preserves-definedness]

  rule <k> #cast(_, castKindIntToInt, TY) => UnexpectedCastTarget(castKindIntToInt, {TYPEMAP[TY]}:>TypeInfo) ... </k>
       <types> TYPEMAP </types>
    requires notBool (#isIntType({TYPEMAP[TY]}:>TypeInfo))
    [preserves-definedness]

  rule <k> #cast(NONINT, castKindIntToInt, _TY) => UnexpectedCastArgument(NONINT, castKindIntToInt) ... </k>
    [owise]
```

### Other type casts

Other type casts are not implemented yet.

```k
  rule <k> #cast(_, CASTKIND, _TY) => CastNotimplemented(CASTKIND)... </k>
    requires CASTKIND =/=K castKindIntToInt
    [owise]
```


## Decoding constants from their bytes representation to values

The `Value` sort above operates at a higher level than the bytes representation found in the MIR syntax for constant values. The bytes have to be interpreted according to the given `TypeInfo` to produce the higher-level value. This is currently only defined for `PrimitiveType`s (primitive types in MIR).

```k
  syntax Value ::= #decodeConstant ( ConstantKind, TypeInfo ) [function]

  //////////////////////////////////////////////////////////////////////////////////////
  // decoding the correct amount of bytes depending on base type size

  // Boolean: should be one byte with value one or zero
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), typeInfoPrimitiveType(primTypeBool)) => BoolVal(false)
    requires 0 ==Int Bytes2Int(BYTES, LE, Unsigned) andBool lengthBytes(BYTES) ==Int 1
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), typeInfoPrimitiveType(primTypeBool)) => BoolVal(true)
    requires 1 ==Int Bytes2Int(BYTES, LE, Unsigned) andBool lengthBytes(BYTES) ==Int 1

  // Integer: handled in separate module for numeric operations
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), TYPEINFO)
      =>
        #decodeInteger(BYTES, #intTypeOf(TYPEINFO))
    requires #isIntType(TYPEINFO)
     andBool lengthBytes(BYTES) ==K #bitWidth(#intTypeOf(TYPEINFO)) /Int 8
     [preserves-definedness]

  ////////////////////////////////////////////////////////////////////////////////////////////////
  // FIXME Char type
  // rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), typeInfoPrimitiveType(primTypeChar))
  //     =>
  //      Str(...)
  /////////////////////////////////////////////////////////////////////////////////////////////////


  /////////////////////////////////////////////////////////////////////////////////////////////////
  // TODO Float decoding: not supported natively in K

  rule #decodeConstant(_, _) => Any [owise]
```

## Primitive operations on numeric data

The `RValue:BinaryOp` performs built-in binary operations on two operands. As [described in the `stable_mir` crate](https://doc.rust-lang.org/nightly/nightly-rustc/stable_mir/mir/enum.Rvalue.html#variant.BinaryOp), its semantics depends on the operations and the types of operands (including variable return types). Certain operation-dependent types apply to the arguments and determine the result type.
Likewise, `RValue:UnaryOp` only operates on certain operand types, notably `bool` and numeric types for arithmetic and bitwise negation.

Arithmetics is usually performed using `RValue:CheckedBinaryOp(BinOp, Operand, Operand)`. Its semantics is the same as for `BinaryOp`, but it yields `(T, bool)` with a `bool` indicating an error condition. For addition, subtraction, and multiplication on integers the error condition is set when the infinite precision result would not be equal to the actual result.[^checkedbinaryop]
This is specific to Stable MIR, the MIR AST instead uses `<OP>WithOverflow` as the `BinOp` (which conversely do not exist in the Stable MIR AST). Where `CheckedBinaryOp(<OP>, _, _)` returns the wrapped result together with the boolean overflow indicator, the `<Op>Unchecked` operation has _undefined behaviour_ on overflows (i.e., when the infinite precision result is unequal to the actual wrapped result).

[^checkedbinaryop]: See [description in `stable_mir` crate](https://doc.rust-lang.org/nightly/nightly-rustc/stable_mir/mir/enum.Rvalue.html#variant.CheckedBinaryOp) and the difference between [MIR `BinOp`](https://doc.rust-lang.org/nightly/nightly-rustc/rustc_middle/mir/enum.BinOp.html) and its [Stable MIR correspondent](https://doc.rust-lang.org/nightly/nightly-rustc/stable_mir/mir/enum.BinOp.html).

For binary operations generally, both arguments have to be read from the provided operands, followed by checking the types and then performing the actual operation (both implemented in `#compute`), which can return a `TypedLocal` or an error. A flag carries the information whether to perform an overflow check through to this function for `CheckedBinaryOp`.

```k
  syntax KItem ::= #compute ( BinOp, Evaluation, Evaluation, Bool) [seqstrict(2,3)]

  rule <k> rvalueBinaryOp(BINOP, OP1, OP2)        => #compute(BINOP, OP1, OP2, false) ... </k>

  rule <k> rvalueCheckedBinaryOp(BINOP, OP1, OP2) => #compute(BINOP, OP1, OP2, true)  ... </k>
```

There are also a few _unary_ operations (`UnOpNot`, `UnOpNeg`, `UnOpPtrMetadata`)  used in `RValue:UnaryOp`. These operations only read a single operand and do not need a `#suspend` helper.

```k
  syntax KItem ::= #applyUnOp ( UnOp , Evaluation ) [strict(2)]

  rule <k> rvalueUnaryOp(UNOP, OP1) => #applyUnOp(UNOP, OP1) ... </k>
```

### Potential errors

```k
  syntax MIRError ::= OperationError

 // (dynamic) program errors causing undefined behaviour
  syntax OperationError ::= "DivisionByZero"
                          | "Overflow_U_B"

  // errors caused by invalid MIR code get stuck

  // Moved or uninitialised operands

  // specific errors for the particular operation types (argument or type mismatches)
```

#### Arithmetic

The arithmetic operations require operands of the same numeric type.

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
  // * arguments must have the same type (TY match)
  // * arguments must be Numbers

  // Checked operations return a pair of the truncated value and an overflow flag
  // signed numbers: must check for wrap-around (operation specific)
  rule #compute(
          BOP,
          typedValue(Integer(ARG1, WIDTH, true), TY, _), //signed
          typedValue(Integer(ARG2, WIDTH, true), TY, _),
          true) // checked
    =>
       typedValue(
          Aggregate(
            variantIdx(0),
            ListItem(typedValue(Integer(truncate(onInt(BOP, ARG1, ARG2), WIDTH, Signed), WIDTH, true), TY, mutabilityNot))
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
  rule #compute(
          BOP,
          typedValue(Integer(ARG1, WIDTH, false), TY, _), // unsigned
          typedValue(Integer(ARG2, WIDTH, false), TY, _),
          true) // checked
    =>
       typedValue(
          Aggregate(
            variantIdx(0),
            ListItem(typedValue(Integer(truncate(onInt(BOP, ARG1, ARG2), WIDTH, Unsigned), WIDTH, false), TY, mutabilityNot))
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

  rule #compute(
          BOP,
          typedValue(Integer(ARG1, WIDTH, true), TY, _), // signed
          typedValue(Integer(ARG2, WIDTH, true), TY, _),
          false) // unchecked
    => typedValue(Integer(truncate(onInt(BOP, ARG1, ARG2), WIDTH, Signed), WIDTH, true), TY, mutabilityNot)
    requires isArithmetic(BOP)
    // infinite precision result must equal truncated result
     andBool truncate(onInt(BOP, ARG1, ARG2), WIDTH, Signed) ==Int onInt(BOP, ARG1, ARG2)
    [preserves-definedness]

  // unsigned numbers: simple overflow check using a bit mask
  rule #compute(
          BOP,
          typedValue(Integer(ARG1, WIDTH, false), TY, _), // unsigned
          typedValue(Integer(ARG2, WIDTH, false), TY, _),
          false) // unchecked
    => typedValue(Integer(truncate(onInt(BOP, ARG1, ARG2), WIDTH, Unsigned), WIDTH, false), TY, mutabilityNot)
    requires isArithmetic(BOP)
    // infinite precision result must equal truncated result
     andBool truncate(onInt(BOP, ARG1, ARG2), WIDTH, Unsigned) ==Int onInt(BOP, ARG1, ARG2)
    [preserves-definedness]

  // lower-priority rule to catch undefined behaviour
  rule #compute(
          BOP,
          typedValue(Integer(_, WIDTH, SIGNEDNESS), TY, _),
          typedValue(Integer(_, WIDTH, SIGNEDNESS), TY, _),
          false) // unchecked
    => Overflow_U_B
    requires isArithmetic(BOP)
    [priority(60)]

  // These are additional high priority rules to detect/report divbyzero and div/rem overflow/underflow
  // (the latter can only happen for signed Ints with dividend minInt and divisor -1
  rule #compute(binOpDiv, _, typedValue(Integer(DIVISOR, _, _), _, _), _)
      =>
        DivisionByZero
    requires DIVISOR ==Int 0
    [priority(40)]

  rule #compute(binOpRem, _, typedValue(Integer(DIVISOR, _, _), _, _), _)
      =>
        DivisionByZero
    requires DIVISOR ==Int 0
    [priority(40)]

  rule #compute(
          binOpDiv,
          typedValue(Integer(DIVIDEND, WIDTH, true), TY, _), // signed
          typedValue(Integer(DIVISOR,  WIDTH, true), TY, _),
          _)
      =>
        Overflow_U_B
    requires DIVISOR ==Int -1
     andBool DIVIDEND ==Int 0 -Int (1 <<Int (WIDTH -Int 1)) // == minInt
    [priority(40)]

  rule #compute(
          binOpRem,
          typedValue(Integer(DIVIDEND, WIDTH, true), TY, _), // signed
          typedValue(Integer(DIVISOR,  WIDTH, true), TY, _),
          _)
      =>
        Overflow_U_B
    requires DIVISOR ==Int -1
     andBool DIVIDEND ==Int 0 -Int (1 <<Int (WIDTH -Int 1)) // == minInt
    [priority(40)]
```

#### Comparison operations

Comparison operations can be applied to all integral types and to boolean values (where `false < true`).
All operations except `binOpCmp` return a `BoolVal`. The argument types must be the same for all comparison operations.

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
  // * arguments must have the same type
  // * arguments must be numbers or Bool

  rule #compute(OP, typedValue(Integer(VAL1, WIDTH, SIGN), TY, _), typedValue(Integer(VAL2, WIDTH, SIGN), TY, _), _)
      =>
        typedValue(BoolVal(cmpOpInt(OP, VAL1, VAL2)), TyUnknown, mutabilityNot)
    requires isComparison(OP)
    [preserves-definedness] // OP known to be a comparison

  rule #compute(OP, typedValue(BoolVal(VAL1), TY, _), typedValue(BoolVal(VAL2), TY, _), _)
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

  rule #compute(binOpCmp, typedValue(Integer(VAL1, WIDTH, SIGN), TY, _), typedValue(Integer(VAL2, WIDTH, SIGN), TY, _), _)
      =>
        typedValue(Integer(cmpInt(VAL1, VAL2), 8, true), TyUnknown, mutabilityNot)

  rule #compute(binOpCmp, typedValue(BoolVal(VAL1), TY, _), typedValue(BoolVal(VAL2), TY, _), _)
      =>
        typedValue(Integer(cmpBool(VAL1, VAL2), 8, true), TyUnknown, mutabilityNot)
```

#### Unary operations on Boolean and integral values

The `unOpNeg` operation only works signed integral (and floating point) numbers.
An overflow can happen when negating the minimal representable integral value (in the given `WIDTH`). The semantics of the operation in this case is to wrap around (with the given bit width).

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

`binOpBitXor`
`binOpBitAnd`
`binOpBitOr`
`binOpShl`
`binOpShlUnchecked`
`binOpShr`
`binOpShrUnchecked`


#### Nullary operations for activating certain checks

`nullOpUbChecks` is supposed to return `BoolVal(true)` if checks for undefined behaviour were activated in the compilation. For our MIR semantics this means to either retain this information (which we don't) or to decide whether or not these checks are useful and should be active during execution.

One important use case of `UbChecks` is to determine overflows in unchecked arithmetic operations. Since our arithmetic operations signal undefined behaviour on overflow independently, the value returned by `UbChecks` is `false` for now.

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

`binOpOffset`

`unOpPtrMetadata`

```k
endmodule
```
