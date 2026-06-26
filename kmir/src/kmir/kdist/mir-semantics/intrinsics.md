# Rust Intrinsic Functions in K

```k
// This looks like a circular import but only module KMIR in kmir.md imports KMIR-INTRINSICS
requires "kmir.md"

module KMIR-INTRINSICS
  imports KMIR-CONTROL-FLOW
```

### Intrinsic Functions

Intrinsic functions are built-in functions provided by the compiler that don't have regular MIR bodies.
They are handled specially in the execution semantics through the `#execIntrinsic` mechanism.
When an intrinsic function is called, the execution bypasses the normal function call setup and directly
executes the intrinsic-specific logic.

#### Black Box (`std::hint::black_box`)

The `black_box` intrinsic serves as an optimization barrier, preventing the compiler from making assumptions
about the value passed through it. In the semantics, it acts as an identity function that simply passes
its argument to the destination without modification.

```k
  // Black box intrinsic implementation - identity function
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("black_box")), ARG:Operand .Operands, DEST, _SPAN)
        => #setLocalValue(DEST, ARG)
       ... </k>
```

#### Cold Path (`std::hint::cold_path`)

The `cold_path` intrinsic is a compiler hint indicating that the current execution path is unlikely to be taken.
It provides metadata for the optimiser and code generator to improve layout and branch predicition but is
a NO OP for program semantics. `std::intrinsics::likely` and `std::intrinsics::unlikely` are
"normal" `MonoItemFn`s that call the `cold_path` intrinsic.

```k
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("cold_path")), .Operands, _DEST, _SPAN) => .K ... </k>
```

#### Prefetch (`std::intrinsics::prefetch_*`)

The `prefetch_read_data`, `prefetch_write_data`, `prefetch_read_instruction`, and `prefetch_write_instruction`
intrinsics in Rust are performance hints that request the CPU to load or prepare a memory address in cache
before it's used. They have no effect on program semantics, and are implemented as a NO OP in this semantics.

```k
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("prefetch_read_data")),  _ARG1:Operand _ARG2:Operand .Operands, _DEST, _SPAN) => .K ... </k>
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("prefetch_write_data")), _ARG1:Operand _ARG2:Operand .Operands, _DEST, _SPAN) => .K ... </k>

  rule <k> #execIntrinsic(IntrinsicFunction(symbol("prefetch_read_instruction")),  _ARG1:Operand _ARG2:Operand .Operands, _DEST, _SPAN) => .K ... </k>
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("prefetch_write_instruction")), _ARG1:Operand _ARG2:Operand .Operands, _DEST, _SPAN) => .K ... </k>
```

#### Assert Inhabited (`std::intrinsics::assert_inhabited`)

The `assert_inhabited` instrinsic asserts that a type is "inhabited" (able to be instantiated). Types such as
`Never` (`!`) cannot be instantiated and are uninhabited types. The target / codegen decides how to handle this
intrinsic, it is not required to panic if the type is not inhabited, it could also perform a NO OP. We have witnessed
in the case that there is an uninhabited type that the following basic block is `noBasicBlockIdx`, and so we
error with `#AssertInhabitedFailure` if we see that following the intrinsic. Otherwise, we perform a NO OP.

```k
  syntax MIRError ::= "AssertInhabitedFailure"
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("assert_inhabited")), .Operands, _DEST, _SPAN)
            ~> #continueAt(noBasicBlockIdx)
        => AssertInhabitedFailure
       ...
      </k>

  rule <k> #execIntrinsic(IntrinsicFunction(symbol("assert_inhabited")), .Operands, _DEST, _SPAN)
        => .K
       ...
      </k>
      [owise]
```

#### Raw Eq (`std::intrinsics::raw_eq`)

The `raw_eq` intrinsic performs byte-by-byte equality comparison of the memory contents pointed to by two references.
It returns a boolean value indicating whether the referenced values are equal. The implementation dereferences the
provided references to access the underlying values, then compares them using K's built-in equality operator.

**Type Safety:**
The implementation requires operands to have identical types (`TY1 ==K TY2`) before performing the comparison.
Execution gets stuck (no matching rule) when operands have different types or unknown type information.

```k
  // Raw eq: dereference operands, extract types, and delegate to typed comparison
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("raw_eq")), ARG1:Operand ARG2:Operand .Operands, PLACE, _SPAN)
        => #execRawEqTyped(PLACE, #withDeref(ARG1), #extractOperandType(TYPESMAP, #withDeref(ARG1), LOCALS),
                                  #withDeref(ARG2), #extractOperandType(TYPESMAP, #withDeref(ARG2), LOCALS))
       ... </k>
       <locals> LOCALS </locals>
       <types> TYPESMAP </types>

  // Compare values only if types are identical
  syntax KItem ::= #execRawEqTyped(Place, Evaluation, MaybeTy, Evaluation, MaybeTy) [seqstrict(2,4)]
  rule <k> #execRawEqTyped(DEST, VAL1:Value, TY1:Ty, VAL2:Value, TY2:Ty)
        => #setLocalValue(DEST, BoolVal(VAL1 ==K VAL2))
       ... </k>
    requires TY1 ==K TY2
    [preserves-definedness]

  // Add deref projection to operands
  syntax Operand ::= #withDeref(Operand) [function, total]
  rule #withDeref(operandCopy(place(LOCAL, PROJ)))
    => operandCopy(place(LOCAL, appendP(PROJ, projectionElemDeref .ProjectionElems)))
  rule #withDeref(operandMove(place(LOCAL, PROJ)))
    => operandCopy(place(LOCAL, appendP(PROJ, projectionElemDeref .ProjectionElems)))
       // must not overwrite the value, just the reference is moved!
  rule #withDeref(OP) => OP [owise]

  // Extract type from operands (locals with projections, constants, fallback to unknown)
```

```{.k .concrete}
  syntax MaybeTy ::= #extractOperandType(MaybeMap, Operand, List) [function, total]
  rule #extractOperandType(TYPESMAP, operandCopy(place(local(I), PROJS)), LOCALS)
       => getTyOf(TYPESMAP, tyOfLocal({LOCALS[I]}:>TypedLocal), PROJS)
    requires 0 <=Int I andBool I <Int size(LOCALS) andBool isTypedLocal(LOCALS[I])
    [preserves-definedness]
  rule #extractOperandType(TYPESMAP, operandMove(place(local(I), PROJS)), LOCALS)
       => getTyOf(TYPESMAP, tyOfLocal({LOCALS[I]}:>TypedLocal), PROJS)
    requires 0 <=Int I andBool I <Int size(LOCALS) andBool isTypedLocal(LOCALS[I])
    [preserves-definedness]
```

```{.k .symbolic}
  syntax MaybeTy ::= #extractOperandType(MaybeMap, Operand, List) [function, total, no-evaluators]
  rule #extractOperandType(_, operandCopy(place(local(I), PROJS)), LOCALS)
       => getTyOf(noMap, tyOfLocal({LOCALS[I]}:>TypedLocal), PROJS)
    requires 0 <=Int I andBool I <Int size(LOCALS) andBool isTypedLocal(LOCALS[I])
    [preserves-definedness]
  rule #extractOperandType(_, operandMove(place(local(I), PROJS)), LOCALS)
       => getTyOf(noMap, tyOfLocal({LOCALS[I]}:>TypedLocal), PROJS)
    requires 0 <=Int I andBool I <Int size(LOCALS) andBool isTypedLocal(LOCALS[I])
    [preserves-definedness]
```

```k
  rule #extractOperandType(_, operandConstant(constOperand(_, _, mirConst(_, TY, _))), _) => TY
  rule #extractOperandType(_, _, _) => TyUnknown [owise]
```

#### Volatile Store (`std::intrinsics::volatile_store`, `std::ptr::write_volatile`)

The `volatile_store` intrinsic writes a value to a memory location through a pointer, ensuring the write is not
optimized away by the compiler. Unlike normal stores, volatile stores are guaranteed to occur exactly once and
in order with respect to other volatile operations. In the semantics, this is equivalent to a regular store
through a dereferenced pointer. We extract the place from the pointer operand, add a deref projection, and
write the value to that location.

```k
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("volatile_store")), operandCopy(place(LOCAL, PROJ)) ARG2:Operand .Operands, _DEST, _SPAN)
        => #setLocalValue(place(LOCAL, appendP(PROJ, projectionElemDeref .ProjectionElems)), ARG2)
       ... </k>

  rule <k> #execIntrinsic(IntrinsicFunction(symbol("volatile_store")), operandMove(place(LOCAL, PROJ)) ARG2:Operand .Operands, _DEST, _SPAN)
        => #setLocalValue(place(LOCAL, appendP(PROJ, projectionElemDeref .ProjectionElems)), ARG2)
       ... </k>
```

#### Volatile Load (`std::intrinsics::volatile_load`, `std::ptr::read_volatile`)

The `volatile_load` intrinsic reads a value from a memory location through a pointer, ensuring the read is not
optimised away by the compiler. Unlike normal loads, volatile loads are guaranteed to occur exactly once and
in order with respect to other volatile operations. In the semantics, this is equivalent to a regular load
through a dereferenced pointer. We extract the place from the pointer operand, add a deref projection, and
read the value from that location into the destination. Since `#setLocalValue` is strict in its second argument,
the dereferenced operand is evaluated (i.e., the value is read from memory) before being written to `DEST`.

```k
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("volatile_load")), operandCopy(place(LOCAL, PROJ)) .Operands, DEST, _SPAN)
        => #setLocalValue(DEST, operandCopy(place(LOCAL, appendP(PROJ, projectionElemDeref .ProjectionElems))))
       ... </k>

  // for `operandMove` the pointer is moved, but the pointed-to value is copied (read, not consumed)
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("volatile_load")), operandMove(place(LOCAL, PROJ)) .Operands, DEST, _SPAN)
        => #setLocalValue(DEST, operandCopy(place(LOCAL, appendP(PROJ, projectionElemDeref .ProjectionElems))))
       ... </k>
```

#### Rotate Left (`std::intrinsics::rotate_left`)

The `rotate_left` intrinsic performs a bitwise left rotation on an integer value. For an N-bit integer,
`rotate_left(x, r)` shifts bits left by `r` positions, wrapping the overflowing bits back to the right.
The rotation amount is taken modulo N. We use a helper with `seqstrict` to evaluate both operands before
computing the rotation.

```k
  syntax KItem ::= #execRotateLeft(Place, Evaluation, Evaluation) [seqstrict(2,3)]

  rule <k> #execIntrinsic(IntrinsicFunction(symbol("rotate_left")), ARG1:Operand ARG2:Operand .Operands, DEST, _SPAN)
        => #execRotateLeft(DEST, ARG1, ARG2)
       ... </k>

  syntax Int ::= #rotateLeftInt(Int, Int, Int) [function, total]
  rule #rotateLeftInt(VAL, WIDTH, ROT) => (VAL <<Int (ROT modInt WIDTH)) |Int (VAL >>Int (WIDTH -Int (ROT modInt WIDTH)))
    requires WIDTH >Int 0
  rule #rotateLeftInt(_, _, _) => 0 [owise]

  rule <k> #execRotateLeft(DEST, Integer(VAL, WIDTH, SIGN), Integer(ROT, _, _))
        => #setLocalValue(DEST, Integer(#rotateLeftInt(truncate(VAL, WIDTH, Unsigned), WIDTH, ROT), WIDTH, SIGN))
       ... </k>
    [preserves-definedness]
```

#### Byte Swap (`std::intrinsics::bswap`)

The `bswap` intrinsic reverses the byte order of an integer value. This is used for endianness conversion.
We convert the integer to little-endian bytes, then read them back as big-endian (which reverses the order).

```k
  syntax KItem ::= #execBswap(Place, Evaluation) [strict(2)]

  rule <k> #execIntrinsic(IntrinsicFunction(symbol("bswap")), ARG:Operand .Operands, DEST, _SPAN)
        => #execBswap(DEST, ARG)
       ... </k>

  rule <k> #execBswap(DEST, Integer(VAL, WIDTH, SIGN))
        => #setLocalValue(DEST, Integer(Bytes2Int(Int2Bytes(WIDTH /Int 8, truncate(VAL, WIDTH, Unsigned), LE), BE, Unsigned), WIDTH, SIGN))
       ... </k>
    requires WIDTH >Int 0
    [preserves-definedness]
```

#### Count Set Bits (`std::intrinsics::ctpop`)

The `ctpop` intrinsic counts the number of set bits (population count) in an integer value.

```k
  syntax KItem ::= #execCtpop(Place, Evaluation) [strict(2)]

  rule <k> #execIntrinsic(IntrinsicFunction(symbol("ctpop")), ARG:Operand .Operands, DEST, _SPAN)
        => #execCtpop(DEST, ARG)
       ... </k>

  syntax Int ::= #popcount(Int) [function, total]
  rule #popcount(0) => 0
  rule #popcount(N) => (N &Int 1) +Int #popcount(N >>Int 1)
    requires N >Int 0
  rule #popcount(N) => #popcount(N *Int -1)
    requires N <Int 0

  rule <k> #execCtpop(DEST, Integer(VAL, WIDTH, SIGN))
        => #setLocalValue(DEST, Integer(#popcount(truncate(VAL, WIDTH, Unsigned)), WIDTH, SIGN))
       ... </k>
    [preserves-definedness]
```

#### Count Leading Zeros (`std::intrinsics::ctlz_nonzero`)

The `ctlz_nonzero` intrinsic counts the number of leading zero bits in an integer value that is
guaranteed to be nonzero. For an N-bit integer with value V, this is N minus the position of the
highest set bit.

```k
  syntax KItem ::= #execCtlz(Place, Evaluation) [strict(2)]

  rule <k> #execIntrinsic(IntrinsicFunction(symbol("ctlz_nonzero")), ARG:Operand .Operands, DEST, _SPAN)
        => #execCtlz(DEST, ARG)
       ... </k>

  rule <k> #execCtlz(DEST, Integer(VAL, WIDTH, SIGN))
        => #setLocalValue(DEST, Integer(WIDTH -Int 1 -Int log2Int(truncate(VAL, WIDTH, Unsigned)), WIDTH, SIGN))
       ... </k>
    requires truncate(VAL, WIDTH, Unsigned) >Int 0
    [preserves-definedness]
```

#### Ptr Offset Computations (`std::intrinsics::ptr_offset_from`, `std::intrinsics::ptr_offset_from_unsigned`)

The `ptr_offset_from[_unsigned]` calculates the distance between two pointers within the same allocation,
i.e., pointers that refer to the same place and only differ in their offset from a given base.

Additionally, for `ptr_offset_from_unsigned`, it is _known_ that the first argument has a greater offset than
the second argument, so the returned difference is always positive.


```k
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("ptr_offset_from")), ARG1:Operand ARG2:Operand .Operands, DEST, _SPAN)
        => #ptrOffsetDiff(ARG1, ARG2, true, DEST)
        ...
       </k>

  rule <k> #execIntrinsic(IntrinsicFunction(symbol("ptr_offset_from_unsigned")), ARG1:Operand ARG2:Operand .Operands, DEST, _SPAN)
        => #ptrOffsetDiff(ARG1, ARG2, false, DEST)
        ...
       </k>

  syntax KItem ::= #ptrOffsetDiff ( Evaluation , Evaluation , Bool , Place ) [seqstrict(1,2)]

  syntax MIRError ::= UBPtrOffsetDiff

  syntax UBPtrOffsetDiff ::= #UBErrorPtrOffsetDiff( Value , Value , Bool )

  rule <k> 
        #ptrOffsetDiff(
          PtrLocal(HEIGHT, PLACE, _, metadata( _ , OFF1, _)),
          PtrLocal(HEIGHT, PLACE, _, metadata( _ , OFF2, _)),
          SIGNED_FLAG,
          DEST
       ) => #setLocalValue(DEST, Integer(OFF1 -Int OFF2, 64, SIGNED_FLAG))
        ...
       </k>
    requires (SIGNED_FLAG orBool OFF1 >=Int OFF2)

  rule <k> 
        #ptrOffsetDiff(
          PtrLocal(_, _, _, _) #as PTR1,
          PtrLocal(_, _, _, _) #as PTR2,
          SIGNED_FLAG,
          _DEST
       ) => #UBErrorPtrOffsetDiff(PTR1, PTR2, SIGNED_FLAG)
        ...
       </k>
    [priority(100)]
```

#### Size of a value (`std::intrinsics::size_of_val`)

`size_of_val` returns the size in bytes of the value its argument points to. The pointee type is
computed from the argument's type and its size from the existing `#sizeOf`.

Only statically-sized pointees are handled here: the rule requires the pointee not to be a
dynamically-sized type (`#metadataSize =/=K dynamicSize(1)`). Dynamically-sized pointees (slices,
`str`, `dyn`) need the runtime metadata carried by the fat pointer and are left for later (the
intrinsic stays stuck on them rather than returning a wrong size).

```k
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("size_of_val")), ARG:Operand .Operands, DEST, _SPAN)
        => #setLocalValue(DEST, Integer(#sizeOf(TYPESMAP, lookupTy(TYPESMAP, {pointeeTy(lookupTy(TYPESMAP, {#extractOperandType(TYPESMAP, ARG, LOCALS)}:>Ty))}:>Ty)), 64, false))
       ... </k>
       <locals> LOCALS </locals>
       <types> TYPESMAP </types>
    requires isTy(#extractOperandType(TYPESMAP, ARG, LOCALS))
     andBool isTy(pointeeTy(lookupTy(TYPESMAP, {#extractOperandType(TYPESMAP, ARG, LOCALS)}:>Ty)))
     andBool #metadataSize(TYPESMAP, pointeeTy(lookupTy(TYPESMAP, {#extractOperandType(TYPESMAP, ARG, LOCALS)}:>Ty))) =/=K dynamicSize(1)
    [preserves-definedness]
```

#### Minimum alignment of a value (`std::intrinsics::min_align_of_val`)

`min_align_of_val` returns the minimum alignment of the value its argument points to.
The pointee type is computed from the argument's type and the alignment from the existing `#alignOf`. Again only statically-sized pointee types are handled here.
Dynamically-sized ones are left for later, so the intrinsic stays stuck if one reaches here.

```k
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("min_align_of_val")), ARG:Operand .Operands, DEST, _SPAN)
        => #setLocalValue(DEST, Integer(#alignOf(TYPESMAP, lookupTy(TYPESMAP, {pointeeTy(lookupTy(TYPESMAP, {#extractOperandType(TYPESMAP, ARG, LOCALS)}:>Ty))}:>Ty)), 64, false))
       ... </k>
       <locals> LOCALS </locals>
       <types> TYPESMAP </types>
    requires isTy(#extractOperandType(TYPESMAP, ARG, LOCALS))
     andBool isTy(pointeeTy(lookupTy(TYPESMAP, {#extractOperandType(TYPESMAP, ARG, LOCALS)}:>Ty)))
     andBool #metadataSize(TYPESMAP, pointeeTy(lookupTy(TYPESMAP, {#extractOperandType(TYPESMAP, ARG, LOCALS)}:>Ty))) =/=K dynamicSize(1)
    [preserves-definedness]
```

```k
endmodule
```
