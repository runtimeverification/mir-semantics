# Handling Return Values

When a function returns a value, we need to decrement the reference count of the value. Because the current stack frame is destroyed after the return and will keep unchanged, it's safe and necessary to traverse the projection until no current stack frame is needed. Otherwise, the semantics will lose the real meaning of the value to return.

## Preliminaries

```k
requires "./data.md"

module RT-RETURN
  imports RT-DATA
```

## Return Value

`#returnValue` is the main function to handle the return value. It has two arguments:
- `Value`: the value to return
- `List`: locals of the current stack frame (transfer from `<locals>` cell)

It will traverse the projection of the locals and decrement the reference count of the value.

```k
  syntax Value ::= #returnValue ( Value , List ) [function, total]

  rule #returnValue(Reference(_, _, _, _) #as VAL, LOCALS)
    => #decrementRef(#traverseLocalProjection(VAL, LOCALS, .ProjectionElems))
  rule #returnValue(PtrLocal(_, _, _, _) #as VAL, LOCALS)
    => #decrementRef(#traverseLocalProjection(VAL, LOCALS, .ProjectionElems))
  rule #returnValue(TL, _) => #decrementRef(TL) [owise]
```

## Traverse Local Projection

`#traverseLocalProjection` only resolves local-related projections and removes these projections from the projection list, since locals will be discarded after return, making local-related projections useless. However, we also need to preserve all projections that remain in the stack.

> **TODO**: Consider integrating this function with `#traverseProjection`, since their functionalities are quite similar. This function should serve as a preliminary step before cross-frame traversal in `#traverseProjection`, but there are some functional differences. For example, `#traverseProjection` must preserve context for write operations, while this function does not.

It has three arguments:
- `Value`: the value to traverse or a list of values to traverse
- `List`: locals of the current stack frame
- `ProjectionElems`: the projections to traverse

```k
  syntax Value ::= #traverseLocalProjection ( Value , List , ProjectionElems ) [function, total]
  syntax List  ::= #traverseLocalProjectionList ( List , List , ProjectionElems ) [function, total]
  
  rule #traverseLocalProjectionList(ListItem(ELEM:Value) REST:List, LOCALS, PROJS)
    => ListItem(#traverseLocalProjection(ELEM, LOCALS, PROJS)) #traverseLocalProjectionList(REST, LOCALS, PROJS)
  rule #traverseLocalProjectionList(.List, _, _) => .List
  // This case is not possible, since the list of values to traverse is always a list of values.
  rule #traverseLocalProjectionList(ListItem(OTHER) REST:List, LOCALS, PROJS)
    => ListItem(OTHER) #traverseLocalProjectionList(REST, LOCALS, PROJS) [owise]
```

For references and pointers, we traverse the local values as long as the height is zero, indicating that the value still refers to the current stack frame. 

> **Note**: The mutability of the value (`_MUT`) is irrelevant here, since the value will be discarded after the return.

```k
  rule #traverseLocalProjection
       (Reference(HEIGHT, place(local(I), projectionElemDeref PROJS), _MUT, META), LOCALS, OLDPROJS)
    => #traverseLocalProjection
       (getValue(LOCALS, I), LOCALS, appendP(PROJS, projectionElemMetadata(META) OLDPROJS))
    requires HEIGHT ==Int 0
  rule #traverseLocalProjection
       (PtrLocal(HEIGHT, place(local(I), projectionElemDeref PROJS), _MUT, ptrEmulation(META)), LOCALS, OLDPROJS)
    => #traverseLocalProjection
       (getValue(LOCALS, I), LOCALS, appendP(PROJS, projectionElemMetadata(META) OLDPROJS))
    requires HEIGHT ==Int 0
```

If the height is greater than zero, this indicates that the value points to a previous stack frame.

> **Note**: Since we assume that `height` is always non-negative, references and pointers can only point to the current or previous stack frames, never to future ones. Thus, at this stage, it is appropriate to stop the traversal, combine the projections, and discard the `_LOCALS` of the current stack frame.

```k
  rule #traverseLocalProjection
       (Reference(HEIGHT, place(LOCAL, PROJS                   ), MUT, META), _LOCALS, OLDPROJS)
    =>  Reference(HEIGHT, place(LOCAL, appendP(PROJS, OLDPROJS)), MUT, META)
    requires HEIGHT >Int 0
  rule #traverseLocalProjection
       (PtrLocal(HEIGHT, place(LOCAL, PROJS                   ), MUT, ptrEmulation(META)), _LOCALS, OLDPROJS)
    =>  PtrLocal(HEIGHT, place(LOCAL, appendP(PROJS, OLDPROJS)), MUT, ptrEmulation(META))
    requires HEIGHT >Int 0
```

By introducing `projectionElemMetadata`, we automate the handling of metadata operations. In essence, this is mainly to perform the same operation as `#derefTruncate`.

```k
  syntax ProjectionElem ::= projectionElemMetadata ( Metadata ) [symbol(ProjectionElem::Metadata)]

  rule #traverseLocalProjection(VAL, LOCALS, projectionElemMetadata(noMetadata) PROJS)
    => #traverseLocalProjection(VAL, LOCALS, PROJS)
  // staticSize metadata requires an array of suitable length and truncates it
  rule #traverseLocalProjection(Range(ELEMS), LOCALS, projectionElemMetadata(staticSize(SIZE)) PROJS)
    => #traverseLocalProjection(Range(range(ELEMS, 0, size(ELEMS) -Int SIZE)), LOCALS, PROJS)
    requires 0 <=Int SIZE andBool SIZE <=Int size(ELEMS) [preserves-definedness] // range parameters checked
  // dynamicSize metadata requires an array of suitable length and truncates it
  rule #traverseLocalProjection(Range(ELEMS), LOCALS, projectionElemMetadata(dynamicSize(SIZE)) PROJS)
    => #traverseLocalProjection(Range(range(ELEMS, 0, size(ELEMS) -Int SIZE)), LOCALS, PROJS)
    requires 0 <=Int SIZE andBool SIZE <=Int size(ELEMS) [preserves-definedness] // range parameters checked
```

For aggregates, the behavior mirrors that of `#traverseProjection`.

```k
  rule #traverseLocalProjection(Aggregate(_, ARGS), LOCALS, projectionElemField(fieldIdx(I), _) PROJS)
    => #traverseLocalProjection(getValue(ARGS, I) , LOCALS, PROJS)
    requires 0 <=Int I andBool I <Int size(ARGS) 
     andBool isValue(ARGS[I])
    [preserves-definedness] // valid list indexing checked
  rule #traverseLocalProjection(Aggregate(_, ARGS)  , LOCALS, projectionElemDowncast(IDX) PROJS)
    => #traverseLocalProjection(Aggregate(IDX, ARGS), LOCALS, PROJS)
  // Return traversed Aggregate when PROJS is empty
  rule #traverseLocalProjection(Aggregate(IDX, ARGS), LOCALS, .ProjectionElems)
    => Aggregate(IDX, #traverseLocalProjectionList(ARGS, LOCALS, .ProjectionElems))
```

For ranges, the behavior mirrors that of `#traverseProjection`.

```k
  rule #traverseLocalProjection(Range(ELEMS), LOCALS, projectionElemIndex(local(LOCAL)) PROJS)
    => #traverseLocalProjection(getValue(ELEMS, #expectUsize(getValue(LOCALS, LOCAL))), LOCALS, PROJS)
    requires 0 <=Int LOCAL andBool LOCAL <Int size(LOCALS)
     andBool isTypedValue(LOCALS[LOCAL])
     andBool isInt(#expectUsize(getValue(LOCALS, LOCAL)))
     andBool 0 <=Int #expectUsize(getValue(LOCALS, LOCAL)) andBool #expectUsize(getValue(LOCALS, LOCAL)) <Int size(ELEMS)
     andBool isValue(ELEMS[#expectUsize(getValue(LOCALS, LOCAL))])
    [preserves-definedness] // index checked, valid Int can be read, ELEMENT indexable and writeable or forced
  rule #traverseLocalProjection(Range(ELEMS), LOCALS, projectionElemConstantIndex(OFFSET:Int, _MINLEN, false) PROJS)
    => #traverseLocalProjection(getValue(ELEMS, OFFSET), LOCALS, PROJS)
    requires 0 <=Int OFFSET andBool OFFSET <Int size(ELEMS)
     andBool isValue(ELEMS[OFFSET])
    [preserves-definedness] // ELEMENT indexable and writeable or forced
  rule #traverseLocalProjection(Range(ELEMS), LOCALS, projectionElemConstantIndex(OFFSET:Int, MINLEN, true) PROJS)
    => #traverseLocalProjection(getValue(ELEMS, MINLEN -Int OFFSET), LOCALS, PROJS)
    requires 0 <Int OFFSET andBool OFFSET <=Int MINLEN
     andBool MINLEN ==Int size(ELEMS) // assumed for valid MIR code
     andBool isValue(ELEMS[MINLEN -Int OFFSET])
    [preserves-definedness] // ELEMENT indexable and writeable or forced
  rule #traverseLocalProjection(Range(ELEMS), LOCALS, projectionElemSubslice(START, END, false) PROJS)
    => #traverseLocalProjection(Range(range(ELEMS, START, size(ELEMS) -Int END)), LOCALS, PROJS)
    requires 0 <=Int START andBool START <=Int size(ELEMS)
     andBool 0 <Int END andBool END <=Int size(ELEMS)
     andBool START <Int END
    [preserves-definedness] // Indexes checked to be in range for ELEMENTS
  rule #traverseLocalProjection(Range(ELEMS), LOCALS, projectionElemSubslice(START, END, true) PROJS)
    => #traverseLocalProjection(Range(range(ELEMS, START, END)), LOCALS, PROJS)
    requires 0 <=Int START andBool START <=Int size(ELEMS)
     andBool 0 <=Int END andBool END <Int size(ELEMS)
     andBool START <=Int size(ELEMS) -Int END
    [preserves-definedness] // Indexes checked to be in range for ELEMENTS
  // Return traversed Range when PROJS is empty
  rule #traverseLocalProjection(Range(ELEMS), LOCALS, .ProjectionElems)
    => Range(#traverseLocalProjectionList(ELEMS, LOCALS, .ProjectionElems))
```

If the list of `projectionElems` is empty, return the value directly.

```k
  rule #traverseLocalProjection(VAL, _, .ProjectionElems) => VAL [priority(55)]
```

For any cases not handled above, we wrap the value in a thunk for easier debugging.

```k
  syntax Value ::= thunkTraverseLocalProjection ( Value , List , ProjectionElems ) [symbol(Value::thunk::TraverseLocalProjection)]
  rule #traverseLocalProjection(VAL, LOCALS, PROJS)
    => thunkTraverseLocalProjection(VAL, LOCALS, PROJS) [owise]
```

```k
endmodule
```