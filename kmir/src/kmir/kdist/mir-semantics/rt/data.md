# Handling Data for MIR Execution

This module addresses all aspects of handling "values" i.e., data, at runtime during MIR execution.


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

  syntax Value
  syntax MaybeValue ::= Value
                      | "NoValue" // not initialized
                      | "Moved"   // inaccessible

  syntax Value ::= #decodeConstant ( ConstantKind, RigidTy ) [function]

  syntax Address // FIXME essential to the memory model, leaving it unspecified for now
```

### Local variables

A list `locals` of local variables of a stack frame is stored as values together
with their type information (to enable type-checking assignments). Also, the
`Mutability` is remembered to prevent mutation of immutable values.

```k
  // local storage of the stack frame
  // syntax TypedLocals ::= List {TypedLocal, ","} but then we lose size, update, indexing

  syntax TypedLocal ::= typedLocal ( MaybeValue, MaybeTy, Mutability )

  // the type of aggregates cannot be determined from the data provided when they
  // occur as `RValue`, therefore we have to make the `Ty` field optional here.
  syntax MaybeTy ::= Ty
                   | "TyUnknown"

  // accessors
  syntax MaybeValue ::= valueOfLocal ( TypedLocal ) [function, total]
  rule valueOfLocal(typedLocal(V, _, _)) => V

  syntax MaybeTy ::= tyOfLocal ( TypedLocal ) [function, total]
  rule tyOfLocal(typedLocal(_, TY, _)) => TY

  syntax Bool ::= isMutable ( TypedLocal ) [function, total]
  rule isMutable(typedLocal(_, _, mutabilityMut)) => true
  rule isMutable(typedLocal(_, _, mutabilityNot)) => false
```

Access to a `TypedLocal` (whether reading or writing( may fail for a number of reasons.
Every access is modelled as a _function_ whose result needs to be checked by the caller.

```k
  syntax LocalAccessError ::= InvalidLocal ( Local )
                            | TypeMismatch( Local, MaybeTy, TypedLocal )
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

### Reading operands (local variables and constants)

```k
  syntax KItem ::= #readOperand ( Operand )
```

_Read_ access to `Operand`s (which may be local values) may have similar errors as write access.

Constant operands are simply decoded according to their type.

```k
  rule <k> #readOperand(operandConstant(constOperand(_, _, mirConst(KIND, TY, _))))
        =>
           typedLocal(#decodeConstant(KIND, {TYPEMAP[TY]}:>RigidTy), TY, mutabilityNot)
        ...
      </k>
      <basetypes> TYPEMAP </basetypes>
    requires TY in_keys(TYPEMAP)
```

The code which copies/moves function arguments into the locals of a stack frame works
in a similar way, but accesses the locals of the _caller_ instead of the locals of the
current function.

Reading a _Copied_ operand means to simply put it in the K sequence. Obviously, a _Moved_
local value cannot be read, though, and the value should be initialised.

```k
  rule <k> #readOperand(operandCopy(place(local(I), .ProjectionElems)))
        =>
           LOCALS[I]
        ...
       </k>
       <locals> LOCALS </locals>
    requires isValue(valueOfLocal({LOCALS[I]}:>TypedLocal))

  rule <k> #readOperand(operandCopy(place(local(I) #as LOCAL, .ProjectionElems)))
        =>
           #LocalError(LocalMoved(LOCAL))
        ...
       </k>
       <locals> LOCALS </locals>
    requires valueOfLocal({LOCALS[I]}:>TypedLocal) ==K Moved

  rule <k> #readOperand(operandCopy(place(local(I), .ProjectionElems)))
        =>
           #LocalError(Uninitialised)
        ...
       </k>
       <locals> LOCALS </locals>
    requires valueOfLocal({LOCALS[I]}:>TypedLocal) ==K NoValue
    // TODO how about zero-sized types
```

Reading an `Operand` using `operandMove` has to invalidate the respective local, to prevent any
further access. Apart from that, the same caveats apply as for operands that are _copied_.

```k
  rule <k> #readOperand(operandMove(place(local(I), .ProjectionElems)))
        =>
           LOCALS[I]
        ...
       </k>
       <locals> LOCALS => LOCALS[I <- typedLocal(Moved, tyOfLocal({LOCALS[I]}:>TypedLocal), mutabilityNot)]</locals>
    requires isValue(valueOfLocal({LOCALS[I]}:>TypedLocal))

  rule <k> #readOperand(operandMove(place(local(I) #as LOCAL, .ProjectionElems)))
        =>
           #LocalError(LocalMoved(LOCAL))
        ...
       </k>
       <locals> LOCALS </locals>
    requires valueOfLocal({LOCALS[I]}:>TypedLocal) ==K Moved

  rule <k> #readOperand(operandMove(place(local(I), .ProjectionElems)))
        =>
           #LocalError(Uninitialised)
        ...
       </k>
       <locals> LOCALS </locals>
    requires valueOfLocal({LOCALS[I]}:>TypedLocal) ==K NoValue
    // TODO how about zero-sized types
```

### Reading places with projections

`#readOperand` above is only implemented for reading a `Local`, without any projecting modifications.
Projections operate on the data stored in the `TypedLocal` and are therefore specific to the `Value` implementation. The following function provides an abstraction for reading with projections, its equations are co-located with the `Value` implementation(s).

```k
  syntax KItem ::= #readProjection ( TypedLocal , ProjectionElems )

  rule <k> #readOperand(operandCopy(place(local(I), PROJECTIONS)))
        =>
           #readProjection({LOCALS[I]}:>TypedLocal, PROJECTIONS)
        ...
       </k>
       <locals> LOCALS </locals>
    requires PROJECTIONS =/=K .ProjectionElems
     andBool 0 <=Int I
     andBool I <Int size(LOCALS)
```

When an operand is `Moved` by the read, the original has to be invalidated. In case of a projected value, this is a write operation nested in the data that is being read.
In contrast to regular write operations, the value does not have to be _mutable_ in order to get moved,
so we need to copy the respective code for writing, or make it generic.

Related code currently resides in the value-implementing module.

### Setting local variables (including error cases)

The `#setLocalValue` operation writes a `TypedLocal` value preceeding it in the K sequence  to a given `Place` within the `List` of local variables currently on top of the stack. This may fail because a local may not be accessible, moved away, or not mutable.

```k
  syntax KItem ::= #setLocalValue( Place )

  // error cases first
  rule <k> _:TypedLocal ~> #setLocalValue( place(local(I) #as LOCAL, _)) => #LocalError(InvalidLocal(LOCAL)) ... </k>
       <locals> LOCALS </locals>
    requires size(LOCALS) <=Int I orBool I <Int 0

  rule <k> typedLocal(_, TY, _) #as VAL ~> #setLocalValue( place(local(I) #as LOCAL, .ProjectionElems))
          =>
           #LocalError(TypeMismatch(LOCAL, tyOfLocal({LOCALS[I]}:>TypedLocal), VAL))
          ...
       </k>
       <locals> LOCALS </locals>
    requires TY =/=K TyUnknown
     andBool tyOfLocal({LOCALS[I]}:>TypedLocal) =/=K TY

  rule <k> _:TypedLocal ~> #setLocalValue( place(local(I), _))
          =>
           #LocalError(LocalMoved(local(I)))
          ...
       </k>
       <locals> LOCALS </locals>
    requires valueOfLocal({LOCALS[I]}:>TypedLocal) ==K Moved

  rule <k> _:TypedLocal ~> #setLocalValue( place(local(I) #as LOCAL, .ProjectionElems))
          =>
           #LocalError(LocalNotMutable(LOCAL))
          ...
       </k>
       <locals> LOCALS </locals>
    requires notBool isMutable({LOCALS[I]}:>TypedLocal)         // not mutable
     andBool valueOfLocal({LOCALS[I]}:>TypedLocal) =/=K NoValue // and already written to


  // writing no value is a no-op
  rule <k> typedLocal(NoValue, _, _) ~> #setLocalValue( _) => .K ... </k>
   // FIXME or should this be NoValueToWrite ? But some zero-sized values are not initialised

  // writing a moved value is an error
  rule <k> typedLocal(Moved, _, _) #as VALUE ~> #setLocalValue( _) => #LocalError(ValueMoved(VALUE)) ... </k>

  // if all is well, write the value
  // mutable case
  rule <k> typedLocal(VAL:Value, TY, _ ) ~> #setLocalValue(place(local(I), .ProjectionElems))
          =>
           .K
          ...
       </k>
       <locals> LOCALS => LOCALS[I <- typedLocal(VAL, tyOfLocal({LOCALS[I]}:>TypedLocal), mutabilityMut)] </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool (tyOfLocal({LOCALS[I]}:>TypedLocal) ==K TY orBool TY ==K TyUnknown) // matching or unknown type
     andBool isMutable({LOCALS[I]}:>TypedLocal)        // mutable
    [preserves-definedness] // valid list indexing checked

  // uninitialised case
  rule <k> typedLocal(VAL:Value, TY, _ ) ~> #setLocalValue(place(local(I), .ProjectionElems))
          =>
           .K
          ...
       </k>
       <locals> LOCALS => LOCALS[I <- typedLocal(VAL, tyOfLocal({LOCALS[I]}:>TypedLocal), mutabilityNot)] </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool (tyOfLocal({LOCALS[I]}:>TypedLocal) ==K TY orBool TY ==K TyUnknown) // matching or unknown type
     andBool notBool isMutable({LOCALS[I]}:>TypedLocal)        // not mutable but
     andBool valueOfLocal({LOCALS[I]}:>TypedLocal) ==K NoValue // not initialised yet
    [preserves-definedness] // valid list indexing checked
```

## Evaluation of RValues

The `RValue` sort in MIR represents various operations that produce a value which can be assigned to a `Place`.

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
  rule  <k> rvalueUse(OPERAND) => #readOperand(OPERAND) ... </k>

  rule <k> rvalueCast(CASTKIND, OPERAND, TY) => #readOperand(OPERAND) ~> #cast(CASTKIND, TY) ... </k>
```

A number of unary and binary operations exist, (which are dependent on the operand types).

```k
// BinaryOp, UnaryOp. NullaryOp: not implemented yet.
```

Other `RValue`s exist in order to construct or operate on arrays and slices, which are built into the language.

```k
// Repeat, Len: not implemented yet
```

Likewise built into the language are aggregates (tuples and `struct`s) and variants (`enum`s).

Tuples and structs are built as `Aggregate` values with a list of argument values.

```k
  rule <k> rvalueAggregate(KIND, ARGS) => #readOperands(ARGS) ~> #mkAggregate(KIND) ... </k>

  // #mkAggregate produces an aggregate TypedLocal value of given kind from a preceeding list of values
  syntax KItem ::= #mkAggregate ( AggregateKind )

  rule <k> ARGS:List ~> #mkAggregate(_)
        =>
            typedLocal(Aggregate(ARGS), TyUnknown, mutabilityNot)
            // NB ty not determined     ^^^^^^^^^
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
           #readOperand(OP) ~> #readOn(ACC, REST)
        ...
       </k>

  rule <k> VAL:TypedLocal ~> #readOn(ACC, REST)
        =>
           #readOperandsAux(ACC ListItem(VAL), REST)
        ...
       </k>

// Discriminant, ShallowIntBox: not implemented yet
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
  syntax KItem ::= #cast( CastKind, Ty )

endmodule
```

## Low level representation

```k
module RT-DATA-LOW-SYNTAX
  imports RT-DATA-SYNTAX
```

Values in MIR are allocated arrays of `Bytes` that are interpreted according to their intended type, encoded as a `Ty` (type ID consistent across the program), and representing a `RigidTy` (other `TyKind` variants are not values that we need to operate on).

```k
  syntax Value ::= value ( Bytes , RigidTy )
                 | Aggregate( List ) // retaining field structure of struct or tuple types
```

```k
endmodule

module RT-DATA-LOW
  imports RT-DATA-LOW-SYNTAX
  imports RT-DATA

  // for low-level representations, decoding bytes is trivial
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), RIGIDTY)
      => value(BYTES, RIGIDTY)

endmodule
```

## High level representation

Values in MIR can also be represented at a certain abstraction level, interpreting the given `Bytes` of a constant according to the desired type. This allows for implementing operations on values using the higher-level type and improves readability of the program data in the K configuration.

High-level values can be
- a range of built-in types (signed and unsigned integer numbers, floats, `str` and `bool`)
- built-in product type constructs (`struct`s, `enum`s, and tuples, with heterogenous component types)
- arrays and slices (with homogenous element types)

**This sort is work in progress and will be extended and modified as we go**

```k
module RT-DATA-HIGH-SYNTAX
  imports RT-DATA-SYNTAX

  syntax Value ::= Scalar( Int, Int, Bool )
                   // value, bit-width, signedness   for un/signed int
                 | BoolVal( Bool )
                   // boolean
                 | Aggregate( List )
                   // heterogenous value list        for tuples and structs (standard, tuple, or anonymous)
                 | Float( Float, Int )
                   // value, bit-width               for f16-f128
                //  | Ptr( Address, MaybeValue ) // FIXME why maybe? why value?
                   // address, metadata              for ref/ptr
                //  | Range( List )
                   // homogenous values              for array/slice
                 | "Any"
                   // arbitrary value                for transmute/invalid ptr lookup

endmodule

module RT-DATA-HIGH
  imports RT-DATA-HIGH-SYNTAX
  imports RT-DATA
```

### Decoding constants from their bytes representation to values

The `Value` sort above operates at a higher level than the bytes representation found in the MIR syntax for constant values. The bytes have to be interpreted according to the given `RigidTy` to produce the higher-level value.

```k
  //////////////////////////////////////////////////////////////////////////////////////
  // decoding the correct amount of bytes depending on base type size
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyBool)
      => // bytes should be one or zero, but all non-zero is taken as true
       BoolVal(0 =/=Int Bytes2Int(BYTES, LE, Unsigned))
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

### Type casts

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
  // narrowing or converting unsigned->signed: use truncation for signed numbers
  rule #intAsType(VAL, WIDTH, INTTYPE:IntTy)
      =>
        Scalar(
          truncate(VAL, #bitWidth(INTTYPE), Signed),
          #bitWidth(INTTYPE),
          true
        )
    requires #bitWidth(INTTYPE) <=Int WIDTH
    [preserves-definedness] // positive shift, divisor non-zero

  // widening: nothing to do: VAL does change (enough bits to represent, no sign change possible)
  rule #intAsType(VAL, WIDTH, INTTYPE:IntTy)
      =>
        Scalar(VAL, #bitWidth(INTTYPE), true)
    requires WIDTH <Int #bitWidth(INTTYPE)

  // converting to unsigned int types
  // truncate (if necessary), then add bias to make non-negative, then truncate again
  rule #intAsType(VAL, _, UINTTYPE:UintTy)
      =>
        Scalar(
          (VAL %Int (1 <<Int #bitWidth(UINTTYPE) )
            +Int (1 <<Int #bitWidth(UINTTYPE)))
          %Int (1 <<Int #bitWidth(UINTTYPE) )
          ,
          #bitWidth(UINTTYPE),
          false
        )
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

### Projections on `TypedLocal` values

The implementation of projections (a list `ProjectionElems`) accesses the structure of a stored value and therefore depends on the value representation. Function `#readProjection ( TypedLocal , Projectionelems) -> TypedLocal` is therefore implemented in the more specific module that provides a `Value` implementation.

#### Reading data from places with projections

The `ProjectionElems` list contains a sequence of projections which is applied (left-to-right) to the value in a `TypedLocal` to obtain a derived value or component thereof. The `TypedLocal` argument is there for the purpose of recursion over the projections. We don't expect the operation to apply to an empty projection `.ProjectionElems`, the base case exists for the recursion.

```k
  // syntax KItem ::= #readProjection ( TypedLocal , ProjectionElems )
  rule <k> #readProjection(TL, .ProjectionElems) => TL ... </k>
```

A `Field` access projection operates on `struct`s and tuples, which are represented as `Aggregate` values. The field is numbered from zero (in source order), and the field type is provided (not checked here).

```k
  rule <k> #readProjection(
              typedLocal(Aggregate(ARGS), _, _),
              projectionElemField(fieldIdx(I), _TY) PROJS
            )
         =>
           #readProjection({ARGS[I]}:>TypedLocal, PROJS)
       ...
       </k>
```

#### Writing data to places with projections

When writing data to a place with projections, the updated value gets constructed recursively by a function over the projections.

```k
  syntax TypedLocal ::= #updateProjected( TypedLocal, ProjectionElems, TypedLocal) [function]

  rule #updateProjected(_, .ProjectionElems, NEW) => NEW

  rule #updateProjected(
          typedLocal(Aggregate(ARGS), TY, MUT),
          projectionElemField(fieldIdx(I), _TY) PROJS,
          NEW)
      =>
       typedLocal(Aggregate(ARGS[I <- #updateProjected({ARGS[I]}:>TypedLocal, PROJS, NEW)]), TY, MUT)
```

Potential errors caused by invalid projections or type mismatch will materialise as unevaluted function calls.
Mutability of the nested components is not checked (but also not modified) while computing the value.
We could first read the original value using `#readProjection` and compare the types to uncover these errors.

```k
  rule <k> VAL ~> #setLocalValue(place(local(I), PROJ))
         =>
           // #readProjection(LOCAL, PROJ) ~> #checkTypeMatch(VAL) ~> // optional, type-check and projection check
           #updateProjected({LOCALS[I]}:>TypedLocal, PROJ, VAL) ~> #setLocalValue(place(local(I), .ProjectionElems))
       ...
       </k>
       <locals> LOCALS </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool PROJ =/=K .ProjectionElems
```

Reading `Moved` operands requires a write operation to the read place, too, however the mutability should be ignored.
Therefore a wrapper `#forceSetLocal` is used to side-step the mutability error in `#setLocalValue`.

```k
  rule <k> #readOperand(operandMove(place(local(I) #as LOCAL, PROJECTIONS)))
        => // read first, then write moved marker (use type from before)
           #readProjection({LOCALS[I]}:>TypedLocal, PROJECTIONS) ~>
           #markMoved({LOCALS[I]}:>TypedLocal, LOCAL, PROJECTIONS)
        ...
       </k>
       <locals> LOCALS </locals>
    requires PROJECTIONS =/=K .ProjectionElems
     andBool 0 <=Int I
     andBool I <Int size(LOCALS)

  syntax KItem ::= #markMoved ( TypedLocal, Local, ProjectionElems )
                |  #forceSetLocal ( Local )

  rule <k> VAL:TypedLocal ~> #markMoved(OLDLOCAL, LOCAL, PROJECTIONS) ~> CONT
        =>
           #updateProjected(OLDLOCAL, PROJECTIONS, typedLocal(Moved, tyOfLocal(VAL), mutabilityNot)) 
           ~> #forceSetLocal(LOCAL)
           ~> VAL
           ~> CONT
       </k>

  // #forceSetLocal sets the given value unconditionally
  rule <k> VALUE:TypedLocal ~> #forceSetLocal(local(I))
          =>
           .K
          ...
       </k>
       <locals> LOCALS => LOCALS[I <- VALUE] </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
    [preserves-definedness] // valid list indexing checked
```

### Primitive operations on numeric data

The `RValue:BinaryOp` performs built-in binary operations on two operands. As [described in the `stable_mir` crate](https://doc.rust-lang.org/nightly/nightly-rustc/stable_mir/mir/enum.Rvalue.html#variant.BinaryOp), its semantics depends on the operations and the types of operands (including variable return types). Certain operation-dependent types apply to the arguments and determine the result type.
Likewise, `RValue:UnaryOp` only operates on certain operand types, notably `bool` and numeric types for arithmetic and bitwise negation.

Arithmetics is usually performed using `RValue:CheckedBinaryOp(BinOp, Operand, Operand)`. Its semantics is the same as for `BinaryOp`, but it yields `(T, bool)` with a `bool` indicating an error condition. For addition, subtraction, and multiplication on integers the error condition is set when the infinite precision result would not be equal to the actual result.[^checkedbinaryop]
This is specific to Stable MIR, the MIR AST instead uses `<OP>WithOverflow` as the `BinOp` (which conversely do not exist in the Stable MIR AST). Where `CheckedBinaryOp(<OP>, _, _)` returns the wrapped result together with the boolean overflow indicator, the `<Op>Unchecked` operation has _undefined behaviour_ on overflows (i.e., when the infinite precision result is unequal to the actual wrapped result).

[^checkedbinaryop]: See [description in `stable_mir` crate](https://doc.rust-lang.org/nightly/nightly-rustc/stable_mir/mir/enum.Rvalue.html#variant.CheckedBinaryOp) and the difference between [MIR `BinOp`](https://doc.rust-lang.org/nightly/nightly-rustc/rustc_middle/mir/enum.BinOp.html) and its [Stable MIR correspondent](https://doc.rust-lang.org/nightly/nightly-rustc/stable_mir/mir/enum.BinOp.html).

Generally, both arguments have to be read from the provided operands, followed by checking the types and then performing the actual operation (both implemented in `#compute`), which can return a `TypedLocal` or an error.
A flag carries the information whether to perform an overflow check through to this function for `CheckedBinaryOp`.

```k
  syntax KItem ::= #suspend ( BinOp, Operand, Bool)
                |  #ready ( BinOp, TypedLocal, Bool )
                |  #compute ( BinOp, TypedLocal, TypedLocal, Bool ) [function]

  rule <k> rvalueBinaryOp(BINOP, OP1, OP2)
        =>
           #readOperand(OP1) ~> #suspend(BINOP, OP2, false)
       ...
       </k>

  rule <k> rvalueCheckedBinaryOp(BINOP, OP1, OP2)
        =>
           #readOperand(OP1) ~> #suspend(BINOP, OP2, true)
       ...
       </k>

  rule <k> ARG1:TypedLocal ~> #suspend(BINOP, OP2, CHECKFLAG)
        =>
           #readOperand(OP2) ~> #ready(BINOP, ARG1, CHECKFLAG)
       ...
       </k>

  rule <k> ARG2:TypedLocal ~> #ready(BINOP, ARG1,CHECKFLAG)
        =>
           #compute(BINOP, ARG1, ARG2, CHECKFLAG)
       ...
       </k>
```
#### Potential errors

```k
  syntax KItem ::= #OperationError( OperationError )

  syntax OperationError ::= TypeMismatch ( BinOp, Ty, Ty )
                          | OperandMismatch ( BinOp, Value, Value )
                          // errors above are compiler bugs or invalid MIR
                          // errors below are program errors
                          | "DivisionByZero"
                          | "Overflow_U_B" // better than getting stuck
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

  rule #compute(
          BOP,
          typedLocal(Scalar(ARG1, WIDTH, SIGNEDNESS), TY, _),
          typedLocal(Scalar(ARG2, WIDTH, SIGNEDNESS), TY, _),
          CHK)
    =>
      #arithmeticInt(BOP, ARG1, ARG2, WIDTH, SIGNEDNESS, TY, CHK)
    requires isArithmetic(BOP)
    [preserves-definedness]

  // error cases:
    // non-scalar arguments
  rule #compute(BOP, typedLocal(ARG1, TY, _), typedLocal(ARG2, TY, _), _)
    =>
       #OperationError(OperandMismatch(BOP, ARG1, ARG2))
    requires isArithmetic(BOP)
    [owise]

    // different argument types
  rule #compute(BOP, typedLocal(_, TY1, _), typedLocal(_, TY2, _), _)
    =>
       #OperationError(TypeMismatch(BOP, TY1, TY2))
    requires TY1 =/=K TY2
     andBool isArithmetic(BOP)
    [owise]

  // helper function to truncate int values
  syntax Int ::= truncate(Int, Int, Signedness) [function, total]
  // -------------------------------------------------------------
  // unsigned values can be truncated using a simple bitmask
  // NB if VAL is negative (underflow), the truncation will yield a positive number
  rule truncate(VAL, WIDTH, Unsigned)
      => // mask with relevant bits
        VAL &Int ((1 <<Int WIDTH) -Int 1)
    requires 0 <Int WIDTH
    [preserves-definedness]
  rule truncate(VAL, WIDTH, Unsigned)
      => VAL // shortcut when there is nothing to do
    requires 0 <Int WIDTH andBool VAL <Int 1 <<Int WIDTH
    [simplification, preserves-definedness]
  // for signed values we need to preserve/restore the sign
  rule truncate(VAL, WIDTH, Signed)
      => // bit-based truncation, then establishing the sign by subtracting a bias
          (VAL &Int ((1 <<Int WIDTH) -Int 1))
            -Int #if VAL &Int ((1 <<Int WIDTH) -Int 1) >=Int (1 <<Int (WIDTH -Int 1))
                #then 1 <<Int WIDTH
                #else 0
                #fi
    requires 0 <Int WIDTH
    [preserves-definedness]

  // perform arithmetic operations on integral types of given width
  syntax KItem ::= #arithmeticInt ( BinOp, Int , Int, Int,  Bool,      Ty,    Bool         ) [function]
  //                                       arg1  arg2 width signedness result overflowcheck
  // signed numbers: must check for wrap-around (operation specific)
  rule #arithmeticInt(BOP, ARG1, ARG2, WIDTH, true, TY, true)
    =>
       typedLocal(
          Aggregate(
            ListItem(typedLocal(Scalar(truncate(onInt(BOP, ARG1, ARG2), WIDTH, Signed), WIDTH, true), TY, mutabilityNot))
            ListItem(
              typedLocal(
                BoolVal(
                  // overflow: Result must be in valid range
                  onInt(BOP, ARG1, ARG2) <Int (1 <<Int (WIDTH -Int 1))
                    andBool
                  0 -Int (1 <<Int (WIDTH -Int 1)) <=Int onInt(BOP, ARG1, ARG2)
                  // alternatively: compare with and without truncation
                  // truncate(onInt(BOP, ARG1, ARG2), WIDTH, Signed) =/=Int onInt BOP, ARG1, ARG2
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
  rule #arithmeticInt(BOP, ARG1, ARG2, WIDTH, false, TY, true)
    =>
       typedLocal(
          Aggregate(
            ListItem(typedLocal(Scalar(truncate(onInt(BOP, ARG1, ARG2), WIDTH, Unsigned), WIDTH, false), TY, mutabilityNot))
            ListItem(
              typedLocal(
                BoolVal(
                  // overflow flag: true if infinite precision result is not equal to truncated result
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

  // These are additional high priority rules to detect/report divbyzero and div/rem overflow/underflow
  // (the latter can only happen for signed Ints with dividend minInt and divisor -1
  rule #arithmeticInt(binOpDiv, _, DIVISOR, _, _, _, _)
      =>
        #OperationError(DivisionByZero)
    requires DIVISOR ==Int 0
    [priority(40)]
  rule #arithmeticInt(binOpRem, _, DIVISOR, _, _, _, _)
      =>
        #OperationError(DivisionByZero)
    requires DIVISOR ==Int 0
    [priority(40)]

  rule #arithmeticInt(binOpDiv, DIVIDEND, DIVISOR, WIDTH, true, _, _)
      =>
        #OperationError(Overflow_U_B)
    requires DIVISOR ==Int -1
     andBool DIVIDEND ==Int 0 -Int (1 <<Int (WIDTH -Int 1)) // == minInt
    [priority(40)]
  rule #arithmeticInt(binOpRem, DIVIDEND, DIVISOR, WIDTH, true, _, _)
      =>
        #OperationError(Overflow_U_B)
    requires DIVISOR ==Int -1
     andBool DIVIDEND ==Int 0 -Int (1 <<Int (WIDTH -Int 1)) // == minInt
    [priority(40)]
```

#### Bit-oriented operations

`binOpBitXor`
`binOpBitAnd`
`binOpBitOr`
`binOpShl`
`binOpShlUnchecked`
`binOpShr`
`binOpShrUnchecked`

`unOpNot`
`unOpNeg`

#### Comparison operations

`binOpEq`
`binOpLt`
`binOpLe`
`binOpNe`
`binOpGe`
`binOpGt`
`binOpCmp`

#### "Nullary" operations (reifying type information)

`nullOpSizeOf`
`nullOpAlignOf`
`nullOpOffsetOf(VariantAndFieldIndices)`
`nullOpUbChecks`

#### Other operations

`binOpOffset`

`unOpPtrMetadata`

```k
endmodule
```
