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
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("black_box")), ARG:Operand .Operands, DEST)
        => #setLocalValue(DEST, ARG)
       ... </k>
```

#### Cold Path (`std::hint::cold_path`)

The `cold_path` intrinsic is a compiler hint indicating that the current execution path is unlikely to be taken.
It provides metadata for the optimiser and code generator to improve layout and branch predicition but is
a NO OP for program semantics. `std::intrinsics::likely` and `std::intrinsics::unlikely` are
"normal" `MonoItemFn`s that call the `cold_path` intrinsic.

```k
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("cold_path")), .Operands, _DEST) => .K ... </k>
```

#### Prefetch (`std::intrinsics::prefetch_*`)

The `prefetch_read_data`, `prefetch_write_data`, `prefetch_read_instruction`, and `prefetch_write_instruction`
intrinsics in Rust are performance hints that request the CPU to load or prepare a memory address in cache
before it's used. They have no effect on program semantics, and are implemented as a NO OP in this semantics.

```k
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("prefetch_read_data")),  _ARG1:Operand _ARG2:Operand .Operands, _DEST) => .K ... </k>
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("prefetch_write_data")), _ARG1:Operand _ARG2:Operand .Operands, _DEST) => .K ... </k>

  rule <k> #execIntrinsic(IntrinsicFunction(symbol("prefetch_read_instruction")),  _ARG1:Operand _ARG2:Operand .Operands, _DEST) => .K ... </k>
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("prefetch_write_instruction")), _ARG1:Operand _ARG2:Operand .Operands, _DEST) => .K ... </k>
```

#### Assert Inhabited (`std::intrinsics::assert_inhabited`)

The `assert_inhabited` instrinsic asserts that a type is "inhabited" (able to be instantiated). Types such as
`Never` (`!`) cannot be instantiated and are uninhabited types. The target / codegen decides how to handle this
intrinsic, it is not required to panic if the type is not inhabited, it could also perform a NO OP. We have witnessed
in the case that there is an uninhabited type that the following basic block is `noBasicBlockIdx`, and so we
error with `#AssertInhabitedFailure` if we see that following the intrinsic. Otherwise, we perform a NO OP.

```k
  syntax MIRError ::= "AssertInhabitedFailure"
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("assert_inhabited")), .Operands, _DEST)
            ~> #continueAt(noBasicBlockIdx)
        => AssertInhabitedFailure
       ...
      </k>

  rule <k> #execIntrinsic(IntrinsicFunction(symbol("assert_inhabited")), .Operands, _DEST)
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
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("raw_eq")), ARG1:Operand ARG2:Operand .Operands, PLACE)
        => #execRawEqTyped(PLACE, #withDeref(ARG1), #extractOperandType(#withDeref(ARG1), LOCALS),
                                  #withDeref(ARG2), #extractOperandType(#withDeref(ARG2), LOCALS))
       ... </k>
       <locals> LOCALS </locals>

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
  syntax MaybeTy ::= #extractOperandType(Operand, List) [function, total]
  rule #extractOperandType(operandCopy(place(local(I), PROJS)), LOCALS)
       => getTyOf(tyOfLocal({LOCALS[I]}:>TypedLocal), PROJS)
    requires 0 <=Int I andBool I <Int size(LOCALS) andBool isTypedLocal(LOCALS[I])
    [preserves-definedness]
  rule #extractOperandType(operandMove(place(local(I), PROJS)), LOCALS)
       => getTyOf(tyOfLocal({LOCALS[I]}:>TypedLocal), PROJS)
    requires 0 <=Int I andBool I <Int size(LOCALS) andBool isTypedLocal(LOCALS[I])
    [preserves-definedness]
  rule #extractOperandType(operandConstant(constOperand(_, _, mirConst(_, TY, _))), _) => TY
  rule #extractOperandType(_, _) => TyUnknown [owise]
```

#### Ptr Offset Computations (`std::intrinsics::ptr_offset_from`, `std::intrinsics::ptr_offset_from_unsigned`)

The `ptr_offset_from[_unsigned]` calculates the distance between two pointers within the same allocation,
i.e., pointers that refer to the same place and only differ in their offset from a given base.

Additionally, for `ptr_offset_from_unsigned`, it is _known_ that the first argument has a greater offset than
the second argument, so the returned difference is always positive.


```k
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("ptr_offset_from")), ARG1:Operand ARG2:Operand .Operands, DEST)
        => #ptrOffsetDiff(ARG1, ARG2, true, DEST)
        ...
       </k>

  rule <k> #execIntrinsic(IntrinsicFunction(symbol("ptr_offset_from_unsigned")), ARG1:Operand ARG2:Operand .Operands, DEST)
        => #ptrOffsetDiff(ARG1, ARG2, false, DEST)
        ...
       </k>

  syntax KItem ::= #ptrOffsetDiff ( Evaluation , Evaluation , Bool , Place ) [seqstrict(1,2)]

  syntax MIRError ::= UBPtrOffsetDiff

  syntax UBPtrOffsetDiff ::= #UBErrorPtrOffsetDiff( Value , Value , Bool )

  rule <k> 
        #ptrOffsetDiff(
          PtrLocal(HEIGHT, PLACE, _, EMUL1),
          PtrLocal(HEIGHT, PLACE, _, EMUL2),
          SIGNED_FLAG,
          DEST
       ) => #setLocalValue(DEST, Integer(offsetOf(EMUL1) -Int offsetOf(EMUL2), 64, SIGNED_FLAG))
        ...
       </k>
    requires (SIGNED_FLAG orBool offsetOf(EMUL1) >=Int offsetOf(EMUL2))

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

```k
endmodule
```
