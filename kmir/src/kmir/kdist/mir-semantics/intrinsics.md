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
    [priority(100)]

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

#### Count Leading Zeros (`std::intrinsics::ctlz_nonzero`, `std::intrinsics::ctlz`)

The `ctlz_nonzero` intrinsic counts the number of leading zeros in the binary representation of a nonzero integer.
It assumes the input is nonzero (undefined behavior if zero). The `ctlz` intrinsic is the same but defined for
all integers (returns `WIDTH` for zero). Both intrinsics evaluate their operand to a `Value`, then compute the
count of leading zeros. For an integer with value `V` and bit width `W`, the count of leading zeros is
`W - 1 - log2Int(V)` for nonzero values (using the unsigned representation of the bit pattern).

```k
  // ctlz_nonzero: count leading zeros, assumes input is nonzero
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("ctlz_nonzero")), ARG:Operand .Operands, DEST, _SPAN)
        => #execCtlz(DEST, ARG)
       ... </k>

  // ctlz: count leading zeros, returns WIDTH for zero
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("ctlz")), ARG:Operand .Operands, DEST, _SPAN)
        => #execCtlz(DEST, ARG)
       ... </k>

  syntax KItem ::= #execCtlz(Place, Evaluation) [strict(2)]

  // Unsigned nonzero: leading zeros = WIDTH - 1 - log2Int(VAL)
  // Result is always u32 (32-bit unsigned) per Rust ABI for bit-counting intrinsics
  rule <k> #execCtlz(DEST, Integer(VAL, WIDTH, false))
        => #setLocalValue(DEST, Integer(WIDTH -Int 1 -Int log2Int(VAL), 32, false))
       ... </k>
    requires VAL >Int 0
    [preserves-definedness]

  // Signed nonzero: convert to unsigned bit pattern first
  rule <k> #execCtlz(DEST, Integer(VAL, WIDTH, true))
        => #setLocalValue(DEST, Integer(WIDTH -Int 1 -Int log2Int(VAL &Int ((1 <<Int WIDTH) -Int 1)), 32, false))
       ... </k>
    requires VAL =/=Int 0
     andBool WIDTH >Int 0
    [preserves-definedness]

  // Zero case (for ctlz, not ctlz_nonzero, but we handle it uniformly)
  rule <k> #execCtlz(DEST, Integer(0, WIDTH, _SIGNED))
        => #setLocalValue(DEST, Integer(WIDTH, 32, false))
       ... </k>
```

#### Count Trailing Zeros (`std::intrinsics::cttz_nonzero`, `std::intrinsics::cttz`)

The `cttz_nonzero` intrinsic counts the number of trailing zeros in the binary representation of a nonzero integer.
It assumes the input is nonzero (undefined behavior if zero). The `cttz` intrinsic is the same but defined for
all integers (returns `WIDTH` for zero). For a nonzero value, the count of trailing zeros equals the position of
the lowest set bit, computed as `log2Int(VAL &Int (0 -Int VAL))` where `VAL &Int (-VAL)` isolates the lowest set bit.

```k
  // cttz_nonzero: count trailing zeros, assumes input is nonzero
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("cttz_nonzero")), ARG:Operand .Operands, DEST, _SPAN)
        => #execCttz(DEST, ARG)
       ... </k>

  // cttz: count trailing zeros, returns WIDTH for zero
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("cttz")), ARG:Operand .Operands, DEST, _SPAN)
        => #execCttz(DEST, ARG)
       ... </k>

  syntax KItem ::= #execCttz(Place, Evaluation) [strict(2)]

  // Unsigned nonzero: trailing zeros = log2Int(VAL &Int (0 -Int VAL))
  // Result is always u32 (32-bit unsigned) per Rust ABI for bit-counting intrinsics
  rule <k> #execCttz(DEST, Integer(VAL, _WIDTH, false))
        => #setLocalValue(DEST, Integer(log2Int(VAL &Int (0 -Int VAL)), 32, false))
       ... </k>
    requires VAL >Int 0
    [preserves-definedness]

  // Signed nonzero: convert to unsigned bit pattern, then find trailing zeros
  rule <k> #execCttz(DEST, Integer(VAL, WIDTH, true))
        => #execCttz(DEST, Integer(VAL &Int ((1 <<Int WIDTH) -Int 1), WIDTH, false))
       ... </k>
    requires VAL =/=Int 0
     andBool WIDTH >Int 0
    [preserves-definedness]

  // Zero case (for cttz, not cttz_nonzero, but we handle it uniformly)
  rule <k> #execCttz(DEST, Integer(0, WIDTH, _SIGNED))
        => #setLocalValue(DEST, Integer(WIDTH, 32, false))
       ... </k>
```

#### Population Count (`std::intrinsics::ctpop`)

The `ctpop` intrinsic counts the number of set bits (1-bits) in the binary representation of an integer,
also known as the Hamming weight or population count. The implementation converts the value to its unsigned
bit pattern and uses a recursive helper function `#popCount` to count the bits.

```k
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("ctpop")), ARG:Operand .Operands, DEST, _SPAN)
        => #execCtpop(DEST, ARG)
       ... </k>

  syntax KItem ::= #execCtpop(Place, Evaluation) [strict(2)]

  // Unsigned: count set bits
  // Result is always u32 (32-bit unsigned) per Rust ABI for bit-counting intrinsics
  rule <k> #execCtpop(DEST, Integer(VAL, _WIDTH, false))
        => #setLocalValue(DEST, Integer(#popCount(VAL), 32, false))
       ... </k>
    requires VAL >=Int 0
    [preserves-definedness]

  // Signed: convert to unsigned bit pattern first
  rule <k> #execCtpop(DEST, Integer(VAL, WIDTH, true))
        => #execCtpop(DEST, Integer(VAL &Int ((1 <<Int WIDTH) -Int 1), WIDTH, false))
       ... </k>
    requires WIDTH >Int 0
    [preserves-definedness]

  // Recursive population count helper
  syntax Int ::= #popCount(Int) [function, total]
  rule #popCount(0) => 0
  rule #popCount(N) => (N &Int 1) +Int #popCount(N >>Int 1) requires N >Int 0
  rule #popCount(_) => 0 [owise]
```

#### Byte Swap (`std::intrinsics::bswap`)

The `bswap` intrinsic reverses the byte order of an integer value. For a `WIDTH`-bit integer, it swaps the
bytes from little-endian to big-endian order (or vice versa). The implementation converts the value to its
unsigned bit pattern and uses a recursive helper function `#bswap` to reverse the bytes.

```k
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("bswap")), ARG:Operand .Operands, DEST, _SPAN)
        => #execBswap(DEST, ARG)
       ... </k>

  syntax KItem ::= #execBswap(Place, Evaluation) [strict(2)]

  // Unsigned: byte-swap
  rule <k> #execBswap(DEST, Integer(VAL, WIDTH, SIGNED))
        => #setLocalValue(DEST, Integer(
             truncate(#bswapAux(VAL &Int ((1 <<Int WIDTH) -Int 1), WIDTH /Int 8, 0), WIDTH, #signedness(SIGNED)),
             WIDTH, SIGNED))
       ... </k>
    requires WIDTH >Int 0
    [preserves-definedness]

  syntax Signedness ::= #signedness(Bool) [function, total]
  rule #signedness(true) => Signed
  rule #signedness(false) => Unsigned

  // Recursive byte-swap helper: #bswapAux(VAL, BYTES_REMAINING, ACCUMULATOR)
  syntax Int ::= #bswapAux(Int, Int, Int) [function, total]
  rule #bswapAux(_, 0, ACC) => ACC
  rule #bswapAux(VAL, N, ACC) => #bswapAux(VAL >>Int 8, N -Int 1, (ACC <<Int 8) |Int (VAL &Int 255))
    requires N >Int 0
  rule #bswapAux(_, _, ACC) => ACC [owise]
```

#### Bit Rotation (`std::intrinsics::rotate_left`, `std::intrinsics::rotate_right`)

The `rotate_left` and `rotate_right` intrinsics perform circular bit rotations within the integer's fixed bit
width. Bits shifted out on one side wrap around to the other side. The implementation first normalizes the
rotation amount modulo the bit width, then applies the corresponding masked rotate formula to the unsigned bit
pattern. The result keeps the same width and signedness as the input integer.

```k
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("rotate_left")), ARG1:Operand ARG2:Operand .Operands, DEST, _SPAN)
        => #execRotateLeft(DEST, ARG1, ARG2)
       ... </k>

  rule <k> #execIntrinsic(IntrinsicFunction(symbol("rotate_right")), ARG1:Operand ARG2:Operand .Operands, DEST, _SPAN)
        => #execRotateRight(DEST, ARG1, ARG2)
       ... </k>

  syntax KItem ::= #execRotateLeft(Place, Evaluation, Evaluation) [seqstrict(2,3)]
  syntax KItem ::= #execRotateRight(Place, Evaluation, Evaluation) [seqstrict(2,3)]

  rule <k> #execRotateLeft(DEST, Integer(VAL, WIDTH, SIGNED), Integer(SHIFT, _, _))
        => #setLocalValue(DEST, Integer(
             truncate(
               ((VAL &Int ((1 <<Int WIDTH) -Int 1)) <<Int #rotateAmount(SHIFT, WIDTH))
               |Int
               ((VAL &Int ((1 <<Int WIDTH) -Int 1)) >>Int (WIDTH -Int #rotateAmount(SHIFT, WIDTH))),
               WIDTH,
               #signedness(SIGNED)),
             WIDTH, SIGNED))
       ... </k>
    requires WIDTH >Int 0
    [preserves-definedness]

  rule <k> #execRotateRight(DEST, Integer(VAL, WIDTH, SIGNED), Integer(SHIFT, _, _))
        => #setLocalValue(DEST, Integer(
             truncate(
               ((VAL &Int ((1 <<Int WIDTH) -Int 1)) >>Int #rotateAmount(SHIFT, WIDTH))
               |Int
               ((VAL &Int ((1 <<Int WIDTH) -Int 1)) <<Int (WIDTH -Int #rotateAmount(SHIFT, WIDTH))),
               WIDTH,
               #signedness(SIGNED)),
             WIDTH, SIGNED))
       ... </k>
    requires WIDTH >Int 0
    [preserves-definedness]

  syntax Int ::= #rotateAmount(Int, Int) [function, total]
  rule #rotateAmount(SHIFT, WIDTH) => SHIFT %Int WIDTH
    requires WIDTH >Int 0
  rule #rotateAmount(_, _) => 0 [owise]
```

#### Bit Reverse (`std::intrinsics::bitreverse`)

The `bitreverse` intrinsic reverses the full bit order of an integer value. Bit `0` moves to position
`WIDTH - 1`, bit `1` moves to position `WIDTH - 2`, and so on. The implementation operates on the unsigned
bit pattern and reconstructs the reversed integer one bit at a time.

```k
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("bitreverse")), ARG:Operand .Operands, DEST, _SPAN)
        => #execBitreverse(DEST, ARG)
       ... </k>

  syntax KItem ::= #execBitreverse(Place, Evaluation) [strict(2)]

  rule <k> #execBitreverse(DEST, Integer(VAL, WIDTH, SIGNED))
        => #setLocalValue(DEST, Integer(
             truncate(#bitreverseAux(VAL &Int ((1 <<Int WIDTH) -Int 1), WIDTH, 0), WIDTH, #signedness(SIGNED)),
             WIDTH, SIGNED))
       ... </k>
    requires WIDTH >Int 0
    [preserves-definedness]

  syntax Int ::= #bitreverseAux(Int, Int, Int) [function, total]
  rule #bitreverseAux(_, 0, ACC) => ACC
  rule #bitreverseAux(VAL, N, ACC) => #bitreverseAux(VAL >>Int 1, N -Int 1, (ACC <<Int 1) |Int (VAL &Int 1))
    requires N >Int 0
  rule #bitreverseAux(_, _, ACC) => ACC [owise]
```

#### Saturating Add (`std::intrinsics::saturating_add`)

The `saturating_add` intrinsic performs saturating integer addition. Instead of wrapping on overflow, the result
is clamped to the maximum (or minimum for signed underflow) value representable by the type.

```k
  rule <k> #execIntrinsic(IntrinsicFunction(symbol("saturating_add")), ARG1:Operand ARG2:Operand .Operands, DEST, _SPAN)
        => #execSaturatingAdd(DEST, ARG1, ARG2)
       ... </k>

  syntax KItem ::= #execSaturatingAdd(Place, Evaluation, Evaluation) [seqstrict(2,3)]

  // Unsigned saturating add: clamp at (2^WIDTH - 1)
  rule <k> #execSaturatingAdd(DEST, Integer(VAL1, WIDTH, false), Integer(VAL2, WIDTH, false))
        => #setLocalValue(DEST, Integer(minInt(VAL1 +Int VAL2, (1 <<Int WIDTH) -Int 1), WIDTH, false))
       ... </k>
    [preserves-definedness]

  // Signed saturating add: clamp at min/max of signed range
  rule <k> #execSaturatingAdd(DEST, Integer(VAL1, WIDTH, true), Integer(VAL2, WIDTH, true))
        => #setLocalValue(DEST, Integer(
             #clampSigned(VAL1 +Int VAL2, WIDTH),
             WIDTH, true))
       ... </k>
    requires WIDTH >Int 0
    [preserves-definedness]

  // Helper: clamp a value to the signed range [-2^(W-1), 2^(W-1) - 1]
  syntax Int ::= #clampSigned(Int, Int) [function, total]
  rule #clampSigned(VAL, WIDTH) => (1 <<Int (WIDTH -Int 1)) -Int 1
    requires WIDTH >Int 0 andBool VAL >=Int (1 <<Int (WIDTH -Int 1))
  rule #clampSigned(VAL, WIDTH) => 0 -Int (1 <<Int (WIDTH -Int 1))
    requires WIDTH >Int 0 andBool VAL <Int (0 -Int (1 <<Int (WIDTH -Int 1)))
  rule #clampSigned(VAL, WIDTH) => VAL
    requires WIDTH >Int 0
     andBool VAL <Int (1 <<Int (WIDTH -Int 1))
     andBool VAL >=Int (0 -Int (1 <<Int (WIDTH -Int 1)))
  rule #clampSigned(VAL, _) => VAL [owise]
```

```k
endmodule
```
