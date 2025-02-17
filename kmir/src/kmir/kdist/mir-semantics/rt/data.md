# Handling Data for MIR Execution

This module addresses all aspects of handling "values"i.e., data), at runtime during MIR execution.


```k
requires "../ty.md"
requires "../body.md"

module RT-DATA-SYNTAX
  imports INT-SYNTAX
  imports FLOAT-SYNTAX
  imports LIST
  imports MAP
  imports BOOL-SYNTAX

  imports TYPES
  imports BODY
```

Values in MIR are allocated arrays of `Bytes` that are interpreted according to their intended type, encoded as a `Ty` (type ID consistent across the program), and representing a `RigidTy` (other `TyKind` variants are not values that we need to operate on).

```k
  syntax LowLevelValue ::= value ( Bytes, Ty, RigidTy ) // TODO redundant information (Ty <-- -> RigidTy)
                         | "MovedValue"
                         | "Uninitialized" // do we need this? Or can we use zero bytes?

  syntax LowLevelValue ::= #newValue ( Ty , Map ) [ function ] // TODO not total

```

**TODO** We might step away from this byte-oriented representation for values to a higher-level representation outlined below. This would assume that a `#decode` function `(Ty, Bytes) -> Value` is available.

```k
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
                      | "NoValue" // not initialized
                      | "Moved"   // inaccessible

  syntax Address // FIXME essential to the memory model, leaving it unspecified for now
```

### Local variables

A list `locals` of local variables of a stack frame is stored as values together
with their type information (to enable type-checking assignments). Also, the
`Mutability` is remembered to prevent mutation of immutable values.

```k
  // local storage of the stack frame
  // syntax TypedLocals ::= List {TypedLocal, ","} but then we lose size, update, indexing

  syntax TypedLocal ::= typedLocal ( MaybeValue, Ty, Mutability )
  // QUESTION: what can and what cannot be stored as a local? (i.e., live on the stack)
  // This limits the Ty that can be used here.

  // accessors
  syntax MaybeValue ::= valueOfLocal ( TypedLocal ) [function, total]
  rule valueOfLocal(typedLocal(V, _, _)) => V

  syntax Ty ::= tyOfLocal ( TypedLocal ) [function, total]
  rule tyOfLocal(typedLocal(_, TY, _)) => TY

  syntax Bool ::= isMutable ( TypedLocal ) [function, total]
  rule isMutable(typedLocal(_, _, mutabilityMut)) => true
  rule isMutable(typedLocal(_, _, mutabilityNot)) => false
```

Access to a `TypedLocal` (whether reading or writing( may fail for a number of reasons.
Every access is modelled as a _function_ whose result needs to be checked by the caller.

```k
  syntax LocalAccessError ::= InvalidLocal ( Local )
                            | TypeMismatch( Local, Ty, TypedLocal )
                            | LocalMoved( Local )
                            | LocalNotMutable ( Local )
                            | "Uninitialised"
                            | "NoValueToWrite"
                            | ValueMoved( TypedLocal )
                            | Unsupported ( String ) // draft code

  syntax KItem ::= #LocalError ( LocalAccessError )

endmodule
```

## Operations on local variables

```k
module RT-DATA
  imports INT
  imports FLOAT
  imports BOOL
  imports BYTES
  imports MAP
  imports K-EQUAL

  imports RT-DATA-SYNTAX
  imports KMIR-CONFIGURATION
```

```k
  //////////////////////////////////////////////////////////////////////////////////////
  syntax Value ::= #decodeConstant ( ConstantKind, RigidTy ) [function]

  // decoding the correct amount of bytes depending on base type size
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, align(ALIGN), _)), rigidTyBool)
      => // bytes should be one or zero, but all non-zero is taken as true
       Scalar(Bytes2Int(BYTES, LE, Unsigned), ALIGN, false)
       // TODO should we insist on known alignment and size of BYTES?
  ////////////////////////////////////////////////////////////////////////////////////////////////
  // FIXME Char and str types
  // rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyChar)
  //     =>
  //      Str(...)
  // rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyStr)
  //     =>
  //      Str(...)
  /////////////////////////////////////////////////////////////////////////////////////////////////
  // UInt decoding
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyUint(uintTyU8))
      =>
        Scalar(Bytes2Int(BYTES, LE, Unsigned), 8, false)
    requires lengthBytes(BYTES) ==Int 1
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyUint(uintTyU16))
      =>
        Scalar(Bytes2Int(BYTES, LE, Unsigned), 16, false)
    requires lengthBytes(BYTES) ==Int 2
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyUint(uintTyU32))
      =>
        Scalar(Bytes2Int(BYTES, LE, Unsigned), 32, false)
    requires lengthBytes(BYTES) ==Int 4
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyUint(uintTyU64))
      =>
        Scalar(Bytes2Int(BYTES, LE, Unsigned), 64, false)
    requires lengthBytes(BYTES) ==Int 8
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyUint(uintTyU128))
      =>
        Scalar(Bytes2Int(BYTES, LE, Unsigned), 128, false)
    requires lengthBytes(BYTES) ==Int 16
  // Usize for 64bit platforms
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyUint(uintTyUsize))
      =>
        Scalar(Bytes2Int(BYTES, LE, Unsigned), 64, false)
    requires lengthBytes(BYTES) ==Int 8
  /////////////////////////////////////////////////////////////////////////////////////////////////
  // Int decoding
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyInt(intTyI8))
      =>
        Scalar(Bytes2Int(BYTES, LE, Signed), 8, true)
    requires lengthBytes(BYTES) ==Int 1
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyInt(intTyI16))
      =>
        Scalar(Bytes2Int(BYTES, LE, Signed), 16, true)
    requires lengthBytes(BYTES) ==Int 2
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyInt(intTyI32))
      =>
        Scalar(Bytes2Int(BYTES, LE, Signed), 32, true)
    requires lengthBytes(BYTES) ==Int 4
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyInt(intTyI64))
      =>
        Scalar(Bytes2Int(BYTES, LE, Signed), 64, true)
    requires lengthBytes(BYTES) ==Int 8
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyInt(intTyI128))
      =>
        Scalar(Bytes2Int(BYTES, LE, Signed), 128, true)
    requires lengthBytes(BYTES) ==Int 16
  // Isize for 64bit platforms
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyInt(intTyIsize)) => Scalar(Bytes2Int(BYTES, LE, Signed), 64, false) requires lengthBytes(BYTES) ==Int 8
  /////////////////////////////////////////////////////////////////////////////////////////////////
  // TODO Float decoding: not supported natively in K

  rule #decodeConstant(_, _) => Any [owise]
```

### Setting local variables (including error cases)

The `#setLocalValue` operation writes a `TypedLocal` value to a given `Place` within the `List` of local variables currently on top of the stack. This may fail because a local may not be accessible, moved away, or not mutable.

```k
  syntax KItem ::= #setLocalValue( Place, TypedLocal )

  // error cases first
  rule <k> #setLocalValue( place(local(I) #as LOCAL, _), _) => #LocalError(InvalidLocal(LOCAL)) ... </k>
       <locals> LOCALS </locals>
    requires size(LOCALS) <Int I orBool I <Int 0

  rule <k> #setLocalValue( place(local(I) #as LOCAL, .ProjectionElems), typedLocal(_, TY, _) #as VAL)
          =>
           #LocalError(TypeMismatch(LOCAL, tyOfLocal({LOCALS[I]}:>TypedLocal), VAL))
          ...
        </k>
       <locals> LOCALS </locals>
    requires tyOfLocal({LOCALS[I]}:>TypedLocal) =/=K TY

  rule <k> #setLocalValue( place(local(I), _), _)
          =>
           #LocalError(LocalMoved(local(I)))
          ...
        </k>
       <locals> LOCALS </locals>
    requires valueOfLocal({LOCALS[I]}:>TypedLocal) ==K Moved

  rule <k> #setLocalValue( place(local(I) #as LOCAL, .ProjectionElems), _)
          =>
           #LocalError(LocalNotMutable(LOCAL))
          ...
        </k>
       <locals> LOCALS </locals>
    requires notBool isMutable({LOCALS[I]}:>TypedLocal)         // not mutable
     andBool valueOfLocal({LOCALS[I]}:>TypedLocal) =/=K NoValue // and already written to


  // writing no value is a no-op
  rule <k> #setLocalValue( _, typedLocal(NoValue, _, _)) => .K ... </k>
   // FIXME or should this be NoValueToWrite ? But some zero-sized values are not initialised

  // writing a moved value is an error
  rule <k> #setLocalValue( _, typedLocal(Moved, _, _) #as VALUE) => ValueMoved(VALUE) ... </k>

  // if all is well, write the value
  // mutable case
  rule <k> #setLocalValue(place(local(I), .ProjectionElems), typedLocal(VAL, TY, _ ))
          =>
           .K
          ...
       </k>
       <locals> LOCALS => LOCALS[I <- typedLocal(VAL, TY, mutabilityMut)] </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isValue(VAL)
     andBool tyOfLocal({LOCALS[I]}:>TypedLocal) ==K TY // matching type
     andBool isMutable({LOCALS[I]}:>TypedLocal)        // mutable
    [preserves-definedness] // valid list indexing checked

  // uninitialised case
  rule <k> #setLocalValue(place(local(I), .ProjectionElems), typedLocal(VAL, TY, _ ))
          =>
           .K
          ...
       </k>
       <locals> LOCALS => LOCALS[I <- typedLocal(VAL, TY, mutabilityNot)] </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isValue(VAL)
     andBool tyOfLocal({LOCALS[I]}:>TypedLocal) ==K TY         // matching type
     andBool notBool isMutable({LOCALS[I]}:>TypedLocal)        // not mutable but
     andBool valueOfLocal({LOCALS[I]}:>TypedLocal) ==K NoValue // not initialised yet
    [preserves-definedness] // valid list indexing checked

  // projections not supported yet
  rule <k> #setLocalValue(place(local(_:Int), PROJECTION:ProjectionElems), _ )
          =>
           #LocalError(Unsupported("Projections"))
          ...
       </k>
    requires PROJECTION =/=K .ProjectionElems
```

### Reading local variables

_Read_ access to local variables as `Operand`s may have similar errors as write access.

The code which copies/moves function arguments into the locals of a stack frame works
in a similar way, but accesses the locals of the _caller_ instead of the locals of the
current function.

Constant operands are simply decoded according to their type.

```k
  syntax KItem ::= #readLocalValue ( Operand )

  rule <k> #readLocalValue(operandConstant(constOperand(_, _, mirConst(KIND, TY, _))))
        =>
           typedLocal(#decodeConstant(KIND, {TYPEMAP[TY]}:>RigidTy), TY, mutabilityNot)
        ...
      </k>
      <basetypes> TYPEMAP </basetypes>
    requires TY in_keys(TYPEMAP)
```

Reading a _Copied_ operand means to simply put it in the K sequence. Obviously, a _Moved_
local value cannot be read, though, and the value should be initialised.

```k
  rule <k> #readLocalValue(operandCopy(place(local(I), .ProjectionElems)))
        =>
           LOCALS[I]
        ...
        </k>
        <locals> LOCALS </locals>
    requires isValue(valueOfLocal({LOCALS[I]}:>TypedLocal))

  rule <k> #readLocalValue(operandCopy(place(local(I) #as LOCAL, .ProjectionElems)))
        =>
           #LocalError(LocalMoved(LOCAL))
        ...
        </k>
        <locals> LOCALS </locals>
    requires valueOfLocal({LOCALS[I]}:>TypedLocal) ==K Moved

  rule <k> #readLocalValue(operandCopy(place(local(I), .ProjectionElems)))
        =>
           #LocalError(Uninitialised)
        ...
        </k>
        <locals> LOCALS </locals>
    requires valueOfLocal({LOCALS[I]}:>TypedLocal) ==K NoValue
    // TODO how about zero-sized types

  rule <k> #readLocalValue(operandCopy(place(_, PROJECTIONS)))
        =>
           #LocalError(Unsupported("Projections(read)"))
        ...
        </k>
    requires PROJECTIONS =/=K .ProjectionElems
    // TODO how about zero-sized types
```

Reading an `Operand` using `operandMove` has to invalidate the respective local, to prevent any
further access. Apart from that, the same caveats apply as for operands that are _copied_.

```k
  rule <k> #readLocalValue(operandMove(place(local(I), .ProjectionElems)))
        =>
           LOCALS[I]
        ...
        </k>
        <locals> LOCALS => LOCALS[I <- typedLocal(Moved, tyOfLocal({LOCALS[I]}:>TypedLocal), mutabilityNot)]</locals>
    requires isValue(valueOfLocal({LOCALS[I]}:>TypedLocal))

  rule <k> #readLocalValue(operandMove(place(local(I) #as LOCAL, .ProjectionElems)))
        =>
           #LocalError(LocalMoved(LOCAL))
        ...
        </k>
        <locals> LOCALS </locals>
    requires valueOfLocal({LOCALS[I]}:>TypedLocal) ==K Moved

  rule <k> #readLocalValue(operandMove(place(local(I), .ProjectionElems)))
        =>
           #LocalError(Uninitialised)
        ...
        </k>
        <locals> LOCALS </locals>
    requires valueOfLocal({LOCALS[I]}:>TypedLocal) ==K NoValue
    // TODO how about zero-sized types

  rule <k> #readLocalValue(operandMove(place(_, PROJECTIONS)))
        =>
           #LocalError(Unsupported("Projections(read)"))
        ...
        </k>
    requires PROJECTIONS =/=K .ProjectionElems
    // TODO how about zero-sized types
```

## Evaluation of RValues

The `RValue` sort in MIR represents various operations that produce a value which can be assigned to a `Place`.

The most basic ones are simply accessing an operand, either directly or by way of a type cast.

```k
  rule  <k> rvalueUse(OPERAND) => #readLocalValue(OPERAND) ... </k>

  rule <k> rvalueCast(CASTKIND, OPERAND, TY) => #readLocalValue(OPERAND) ~> #cast(CASTKIND, TY) ... </k>
```

A number of unary and binary operations exist, (which are dependent on the operand types).

```k
// BiarnyOp, UnaryOp. NullaryOp: not implemented yet.
```

Other `RValue`s exist in order to construct or operate on arrays and slices, which are built into the language.

```k
// Repeat, Len: not implemented yet
```

Likewise built into the language are aggregates (`struct`s) and variants (`enum`s).

```k
// Discriminant, Aggregate, ShallowIntBox: not implemented yet
```


References and de-referencing is another family of `RValue`s.

```k
// Ref, AddressOf, CopyForDeref: not implemented yet
```

## Type casts

Type casts between a number of different types exist in MIR. We implement a type
cast from a `TypedLocal` to another when it is followed by a `#cast` item,
rewriting `typedLocal(...) ~> #cast(...) ~> REST` to `typedLocal(...) ~> REST`.

```k
  syntax KITEM ::= #cast( CastKind, Ty )
```

Casts between signed and unsigned integral numbers of different width exist, with a
truncating semantics **TODO: reference**.
These casts can only operate on the `Scalar` variant of the `Value` type, adjusting
bit width, signedness, and possibly truncating or 2s-complementing the value.

```k
  // int casts
  rule <k> typedLocal(Scalar(VAL, WIDTH, _SIGNEDNESS), _, MUT) ~> #cast(castKindIntToInt, TY) ~> CONT
          =>
            typedLocal(#intAsType(VAL, WIDTH, #numTypeOf({TYPEMAP[TY]}:>RigidTy)), TY, MUT) ~> CONT
        </k>
        <basetypes> TYPEMAP </basetypes>
      requires #isIntType({TYPEMAP[TY]}:>RigidTy)
      [preserves-definedness] // ensures #numTypeOf is defined

  // helpers
  syntax NumTy ::= IntTy | UintTy | FloatTy

  syntax Int ::= #bitWidth( NumTy ) [function, total]
  // ------------------------------
  rule #bitWidth(intTyIsize) => 64 // on 64-bit systems
  rule #bitWidth(intTyI8   ) => 8
  rule #bitWidth(intTyI16  ) => 16
  rule #bitWidth(intTyI32  ) => 32
  rule #bitWidth(intTyI64  ) => 64
  rule #bitWidth(intTyI128 ) => 128
  rule #bitWidth(uintTyUsize) => 64 // on 64-bit systems
  rule #bitWidth(uintTyU8   ) => 8
  rule #bitWidth(uintTyU16  ) => 16
  rule #bitWidth(uintTyU32  ) => 32
  rule #bitWidth(uintTyU64  ) => 64
  rule #bitWidth(uintTyU128 ) => 128
  rule #bitWidth(floatTyF16 ) => 16
  rule #bitWidth(floatTyF32 ) => 32
  rule #bitWidth(floatTyF64 ) => 64
  rule #bitWidth(floatTyF128) => 128

  syntax NumTy ::= #numTypeOf( RigidTy ) [function]
  // ----------------------------------------------
  rule #numTypeOf(rigidTyInt(INTTY)) => INTTY
  rule #numTypeOf(rigidTyUint(UINTTY)) => UINTTY
  rule #numTypeOf(rigidTyFloat(FLOATTY)) => FLOATTY

  syntax Bool ::= #isIntType ( RigidTy ) [function, total]
  // -----------------------------------------------------
  rule #isIntType(rigidTyInt(_))  => true
  rule #isIntType(rigidTyUint(_)) => true
  rule #isIntType(_)              => false [owise]

  syntax Value ::= #intAsType( Int, Int, NumTy ) [function]
  // ------------------------------------------------------
  // converting to signed int types:
  // narrowing: truncate using bit operations
  rule #intAsType(VAL, WIDTH, INTTYPE:IntTy)
      =>
        Scalar(
          VAL &Int (1 <<Int #bitWidth(INTTYPE) -Int 1),
          #bitWidth(INTTYPE),
          true
        )
    requires #bitWidth(INTTYPE) <Int WIDTH
    [preserves-definedness] // positive shift, divisor non-zero

  // widening: use arithmetic shift for sign extension
  rule #intAsType(VAL, WIDTH, INTTYPE:IntTy)
      =>
        Scalar(
          (VAL <<Int (#bitWidth(INTTYPE) -Int WIDTH) >>Int (#bitWidth(INTTYPE) -Int WIDTH))
             %Int (1 <<Int #bitWidth(INTTYPE)),
          #bitWidth(INTTYPE),
          true
        )
    requires WIDTH <=Int #bitWidth(INTTYPE)
    [preserves-definedness] // positive shift, divisor non-zero

  // converting to unsigned int types
  // narrowing: truncate using bit operations
  rule #intAsType(VAL, WIDTH, UINTTYPE:UintTy)
      =>
        Scalar(
          VAL &Int (1 <<Int #bitWidth(UINTTYPE) -Int 1),
          #bitWidth(UINTTYPE),
          true
        )
    requires #bitWidth(UINTTYPE) <Int WIDTH
    [preserves-definedness] // positive shift, divisor non-zero
  // widening: use arithmetic shift for sign extension
  rule #intAsType(VAL, WIDTH, UINTTYPE:UintTy)
      =>
        Scalar(
          VAL <<Int (#bitWidth(UINTTYPE) -Int WIDTH) >>Int (#bitWidth(UINTTYPE) -Int WIDTH),
          #bitWidth(UINTTYPE),
          true
        )
    requires WIDTH <=Int #bitWidth(UINTTYPE)
    [preserves-definedness] // positive shift, divisor non-zero

```

Error cases for `castKindIntToInt`
* unknown target type (not in `basetypes`)
* target type is not an `Int` type
* value is not a `Scalar`

```k
  rule <k> (_:TypedLocal ~> #cast(castKindIntToInt, TY) ~> _CONT) #as STUFF
          =>
            #LocalError(Unsupported("Int-to-Int type cast to unknown type")) ~> STUFF
        </k>
        <basetypes> TYPEMAP </basetypes>

    requires notBool isRigidTy(TYPEMAP[TY])

  rule <k> (_:TypedLocal ~> #cast(castKindIntToInt, TY) ~> _CONT) #as STUFF
          =>
            #LocalError(Unsupported("Int-to-Int type cast to unexpected non-int type")) ~> STUFF
        </k>
        <basetypes> TYPEMAP </basetypes>
    requires notBool (#isIntType({TYPEMAP[TY]}:>RigidTy))

  rule <k> (_:TypedLocal ~> #cast(castKindIntToInt, _TY) ~> _CONT) #as STUFF
          =>
            #LocalError(Unsupported("Int-to-Int type cast of non-int value")) ~> STUFF
        </k>
    [owise]
```


**TODO** Other type casts are not implemented.

```k
  rule <k> (_:TypedLocal ~> #cast(CASTKIND, _TY) ~> _CONT) #as STUFF
          =>
            #LocalError(Unsupported("Type casts not implemented")) ~> STUFF
        </k>
    requires CASTKIND =/=K castKindIntToInt
    [owise]
```


```k
endmodule
```
