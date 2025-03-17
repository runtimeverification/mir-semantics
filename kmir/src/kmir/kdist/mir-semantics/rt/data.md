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

  syntax Value ::= #decodeConstant ( ConstantKind, RigidTy ) [function]
```

### Local variables

A list `locals` of local variables of a stack frame is stored as values together
with their type information (to enable type-checking assignments). Also, the
`Mutability` is remembered to prevent mutation of immutable values.

```k
  // local storage of the stack frame
  // syntax TypedLocals ::= List {TypedLocal, ","} but then we lose size, update, indexing

  syntax TypedLocal ::= typedLocal ( Value, MaybeTy, Mutability ) // regular value
                      | "Moved"                                   // inaccessible
                      | noValue ( Ty, Mutability )                // not initialised

  // the type of aggregates cannot be determined from the data provided when they
  // occur as `RValue`, therefore we have to make the `Ty` field optional here.
  syntax MaybeTy ::= Ty
                   | "TyUnknown"

  // accessors
  syntax Bool ::= hasValue ( TypedLocal )  [function, total]
                | isNoValue ( TypedLocal ) [function, total]
  rule hasValue(typedLocal(_, _, _)) => true
  rule hasValue(Moved)               => false
  rule hasValue(noValue(_, _))       => false

  rule isNoValue(typedLocal(_, _, _)) => false
  rule isNoValue(Moved)               => false
  rule isNoValue(noValue(_, _))       => true

  syntax MaybeTy ::= tyOfLocal ( TypedLocal ) [function, total]
  rule tyOfLocal(typedLocal(_, TY, _)) => TY
  rule tyOfLocal(Moved)                => TyUnknown
  rule tyOfLocal(noValue(TY, _))       => TY

  syntax Bool ::= isMutable ( TypedLocal ) [function, total]
  rule isMutable(typedLocal(_, _, mutabilityMut)) => true
  rule isMutable(typedLocal(_, _, mutabilityNot)) => false
  rule isMutable(Moved)                           => false
  rule isMutable(noValue(_, mutabilityMut))       => true
  rule isMutable(noValue(_, mutabilityNot))       => false
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
                            | "ValueMoved"
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
     andBool isRigidTy(TYPEMAP[TY])
    [preserves-definedness] // valid Map lookup checked
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
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isTypedLocal(LOCALS[I])
     andBool hasValue({LOCALS[I]}:>TypedLocal)
    [preserves-definedness] // valid list indexing checked

  rule <k> #readOperand(operandCopy(place(local(I) #as LOCAL, .ProjectionElems)))
        =>
           #LocalError(LocalMoved(LOCAL))
        ...
       </k>
       <locals> LOCALS </locals>
    requires LOCALS[I] ==K Moved
     andBool 0 <=Int I
     andBool I <Int size(LOCALS)
    [preserves-definedness] // valid list indexing checked

  rule <k> #readOperand(operandCopy(place(local(I), .ProjectionElems)))
        =>
           #LocalError(Uninitialised)
        ...
       </k>
       <locals> LOCALS </locals>
    requires isNoValue({LOCALS[I]}:>TypedLocal)
     andBool I <Int size(LOCALS)
     andBool 0 <=Int I
     andBool isTypedLocal(LOCALS[I])
    [preserves-definedness] // valid list indexing checked
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
       <locals> LOCALS => LOCALS[I <- Moved]</locals>
    requires hasValue({LOCALS[I]}:>TypedLocal)
     andBool 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isTypedLocal(LOCALS[I])
    [preserves-definedness] // valid list indexing checked

  rule <k> #readOperand(operandMove(place(local(I) #as LOCAL, .ProjectionElems)))
        =>
           #LocalError(LocalMoved(LOCAL))
        ...
       </k>
       <locals> LOCALS </locals>
    requires LOCALS[I] ==K Moved
     andBool 0 <=Int I
     andBool I <Int size(LOCALS)
    [preserves-definedness] // valid list indexing checked

  rule <k> #readOperand(operandMove(place(local(I), .ProjectionElems)))
        =>
           #LocalError(Uninitialised)
        ...
       </k>
       <locals> LOCALS </locals>
    requires isNoValue({LOCALS[I]}:>TypedLocal)
     andBool 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isTypedLocal(LOCALS[I])
    [preserves-definedness] // valid list indexing checked
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
     andBool isTypedLocal(LOCALS[I])
     andBool hasValue({LOCALS[I]}:>TypedLocal)
    [preserves-definedness] // valid list indexing checked
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
    requires I <Int size(LOCALS)
     andBool 0 <=Int I
     andBool isTypedLocal(LOCALS[I])
     andBool TY =/=K TyUnknown
     andBool tyOfLocal({LOCALS[I]}:>TypedLocal) =/=K TY
    [preserves-definedness] // list index checked before lookup

  // setting a local to Moved is an error
  rule <k> _:TypedLocal ~> #setLocalValue( place(local(I), _))
          =>
           #LocalError(LocalMoved(local(I)))
          ...
       </k>
       <locals> LOCALS </locals>
    requires LOCALS[I] ==K Moved

  // setting a non-mutable local that is initialised is an error
  rule <k> typedLocal(_, _, _) ~> #setLocalValue( place(local(I) #as LOCAL, .ProjectionElems))
          =>
           #LocalError(LocalNotMutable(LOCAL))
          ...
       </k>
       <locals> LOCALS </locals>
    requires I <Int size(LOCALS)
     andBool 0 <=Int I
     andBool isTypedLocal(LOCALS[I])
     andBool notBool isMutable({LOCALS[I]}:>TypedLocal) // not mutable
     andBool notBool isNoValue({LOCALS[I]}:>TypedLocal) // noValue(_, mutabilityNot) is mutable once

  // writing no value is a no-op
  rule <k> noValue(_, _) ~> #setLocalValue( _) => .K ... </k>
   // FIXME some zero-sized values are not initialised. Otherwise we could use a special value `ZeroSized` here

  // writing a moved value is an error
  rule <k> Moved ~> #setLocalValue( _) => #LocalError(ValueMoved) ... </k>

  // if all is well, write the value
  //
  rule <k> typedLocal(VAL:Value, TY, _ ) ~> #setLocalValue(place(local(I), .ProjectionElems))
          =>
           .K
          ...
       </k>
       <locals> LOCALS => LOCALS[I <- typedLocal(VAL, tyOfLocal({LOCALS[I]}:>TypedLocal), mutabilityMut)] </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isTypedLocal(LOCALS[I])
     andBool (tyOfLocal({LOCALS[I]}:>TypedLocal) ==K TY orBool TY ==K TyUnknown) // matching or unknown type
     andBool isMutable({LOCALS[I]}:>TypedLocal)        // mutable
    [preserves-definedness] // valid list indexing checked

  // special case for non-mutable uninitialised values: mutable once
  rule <k> typedLocal(VAL:Value, TY, _ ) ~> #setLocalValue(place(local(I), .ProjectionElems))
          =>
           .K
          ...
       </k>
       <locals> LOCALS => LOCALS[I <- typedLocal(VAL, tyOfLocal({LOCALS[I]}:>TypedLocal), mutabilityNot)] </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isTypedLocal(LOCALS[I])
     andBool (tyOfLocal({LOCALS[I]}:>TypedLocal) ==K TY orBool TY ==K TyUnknown) // matching or unknown type
     andBool notBool isMutable({LOCALS[I]}:>TypedLocal)        // not mutable but
     andBool isNoValue({LOCALS[I]}:>TypedLocal)                // not initialised yet
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
// BinaryOp, UnaryOp. NullaryOp: dependent on value representation. See below
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

References can be created using a particular region kind (not used here) and `BorrowKind`.
The `BorrowKind` indicates mutability of the value through the reference, but also provides more find-grained characteristics of mutable references. These fine-grained borrow kinds are not represented here, as some of them are disallowed in the compiler phase targeted by this semantics, and others related to memory management in lower-level artefacts[^borrowkind]. Therefore, reference values are represented with a simple `Mutability` flag instead of `BorrowKind`

[^borrowkind]: https://doc.rust-lang.org/nightly/nightly-rustc/rustc_middle/mir/enum.BorrowKind.html

```k
  rule <k> rvalueRef(_REGION, KIND, PLACE)
         =>
           typedLocal(Reference(0, PLACE, #mutabilityOf(KIND)), TyUnknown, #mutabilityOf(KIND))
       ...
       </k>

  syntax Mutability ::= #mutabilityOf ( BorrowKind ) [function, total]

  rule #mutabilityOf(borrowKindShared)  => mutabilityNot
  rule #mutabilityOf(borrowKindFake(_)) => mutabilityNot // Shallow fake borrow disallowed in late stages
  rule #mutabilityOf(borrowKindMut(_))  => mutabilityMut // all mutable kinds behave equally for us

// AddressOf, CopyForDeref: not implemented yet
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
                 | Reference( Int , Place , Mutability ) // stack depth (initially 0), place, borrow kind
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
- references to a place in the current or an enclosing stack frame
- arrays and slices (with homogenous element types)

**This sort is work in progress and will be extended and modified as we go**

```k
module RT-DATA-HIGH-SYNTAX
  imports RT-DATA-SYNTAX

  syntax Value ::= Integer( Int, Int, Bool )
                   // value, bit-width, signedness   for un/signed int
                 | BoolVal( Bool )
                   // boolean
                 | Aggregate( List )
                   // heterogenous value list        for tuples and structs (standard, tuple, or anonymous)
                 | Float( Float, Int )
                   // value, bit-width               for f16-f128
                 | Reference( Int , Place , Mutability )
                   // stack depth (initially 0), place, borrow kind
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

  // Boolean: should be one byte with value one or zero
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyBool) => BoolVal(false)
    requires 0 ==Int Bytes2Int(BYTES, LE, Unsigned) andBool lengthBytes(BYTES) ==Int 1
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyBool) => BoolVal(true)
    requires 1 ==Int Bytes2Int(BYTES, LE, Unsigned) andBool lengthBytes(BYTES) ==Int 1

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
        Integer(Bytes2Int(BYTES, LE, Unsigned), 8, false)
    requires lengthBytes(BYTES) ==Int 1
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyUint(uintTyU16))
      =>
        Integer(Bytes2Int(BYTES, LE, Unsigned), 16, false)
    requires lengthBytes(BYTES) ==Int 2
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyUint(uintTyU32))
      =>
        Integer(Bytes2Int(BYTES, LE, Unsigned), 32, false)
    requires lengthBytes(BYTES) ==Int 4
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyUint(uintTyU64))
      =>
        Integer(Bytes2Int(BYTES, LE, Unsigned), 64, false)
    requires lengthBytes(BYTES) ==Int 8
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyUint(uintTyU128))
      =>
        Integer(Bytes2Int(BYTES, LE, Unsigned), 128, false)
    requires lengthBytes(BYTES) ==Int 16
  // Usize for 64bit platforms
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyUint(uintTyUsize))
      =>
        Integer(Bytes2Int(BYTES, LE, Unsigned), 64, false)
    requires lengthBytes(BYTES) ==Int 8
  /////////////////////////////////////////////////////////////////////////////////////////////////
  // Int decoding
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyInt(intTyI8))
      =>
        Integer(Bytes2Int(BYTES, LE, Signed), 8, true)
    requires lengthBytes(BYTES) ==Int 1
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyInt(intTyI16))
      =>
        Integer(Bytes2Int(BYTES, LE, Signed), 16, true)
    requires lengthBytes(BYTES) ==Int 2
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyInt(intTyI32))
      =>
        Integer(Bytes2Int(BYTES, LE, Signed), 32, true)
    requires lengthBytes(BYTES) ==Int 4
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyInt(intTyI64))
      =>
        Integer(Bytes2Int(BYTES, LE, Signed), 64, true)
    requires lengthBytes(BYTES) ==Int 8
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyInt(intTyI128))
      =>
        Integer(Bytes2Int(BYTES, LE, Signed), 128, true)
    requires lengthBytes(BYTES) ==Int 16
  // Isize for 64bit platforms
  rule #decodeConstant(constantKindAllocated(allocation(BYTES, _, _, _)), rigidTyInt(intTyIsize)) => Integer(Bytes2Int(BYTES, LE, Signed), 64, false) requires lengthBytes(BYTES) ==Int 8
  /////////////////////////////////////////////////////////////////////////////////////////////////
  // TODO Float decoding: not supported natively in K

  rule #decodeConstant(_, _) => Any [owise]
```

### Type casts

Casts between signed and unsigned integral numbers of different width exist, with a
truncating semantics **TODO: reference**.
These casts can only operate on the `Integer` variant of the `Value` type, adjusting
bit width, signedness, and possibly truncating or 2s-complementing the value.

```k
  // int casts
  rule <k> typedLocal(Integer(VAL, WIDTH, _SIGNEDNESS), _, MUT) ~> #cast(castKindIntToInt, TY) ~> CONT
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
        Integer(
          truncate(VAL, #bitWidth(INTTYPE), Signed),
          #bitWidth(INTTYPE),
          true
        )
    requires #bitWidth(INTTYPE) <=Int WIDTH
    [preserves-definedness] // positive shift, divisor non-zero

  // widening: nothing to do: VAL does change (enough bits to represent, no sign change possible)
  rule #intAsType(VAL, WIDTH, INTTYPE:IntTy)
      =>
        Integer(VAL, #bitWidth(INTTYPE), true)
    requires WIDTH <Int #bitWidth(INTTYPE)

  // converting to unsigned int types
  // truncate (if necessary), then add bias to make non-negative, then truncate again
  rule #intAsType(VAL, _, UINTTYPE:UintTy)
      =>
        Integer(
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
* value is not a `Integer`

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
    requires 0 <=Int I
     andBool I <Int size(ARGS)
     andBool isTypedLocal(ARGS[I])
    [preserves-definedness] // valid list indexing checked
```

A `Deref` projection operates on `Reference`s that refer to locals in the same or an enclosing stack frame, indicated by the stack height in the `Reference` value. `Deref` reads the referred place (and may proceed with further projections).

In the simplest case, the reference refers to a local in the same stack frame (height 0), which is directly read.

```k
  rule <k> #readProjection(
              typedLocal(Reference(0, place(local(I:Int), PLACEPROJS:ProjectionElems), _), _, _),
              projectionElemDeref PROJS:ProjectionElems
            )
         =>
           #readProjection({LOCALS[I]}:>TypedLocal, appendP(PLACEPROJS, PROJS))
       ...
       </k>
       <locals> LOCALS </locals>
    requires 0 <Int I
     andBool I <Int size(LOCALS)
     andBool isTypedLocal(LOCALS[I])
    [preserves-definedness] // valid list indexing checked

  // why do we not have this automatically for user-defined lists?
  syntax ProjectionElems ::= appendP ( ProjectionElems , ProjectionElems ) [function, total]
  rule appendP(.ProjectionElems, TAIL) => TAIL
  rule appendP(X:ProjectionElem REST:ProjectionElems, TAIL) => X appendP(REST, TAIL)

```

For references to enclosing stack frames, the local must be retrieved from the respective stack frame.
An important prerequisite of this rule is that when passing references to a callee as arguments, the stack height must be adjusted.

```k
  rule <k> #readProjection(
              typedLocal(Reference(FRAME, place(LOCAL:Local, PLACEPROJS), _), _, _),
              projectionElemDeref PROJS
            )
         =>
           #readProjection(#localFromFrame({STACK[FRAME -Int 1]}:>StackFrame, LOCAL), appendP(PLACEPROJS, PROJS))
       ...
       </k>
       <stack> STACK </stack>
    requires 0 <Int FRAME
     andBool FRAME <=Int size(STACK)
     andBool isStackFrame(STACK[FRAME -Int 1])
    [preserves-definedness] // valid list indexing checked

    syntax TypedLocal ::= #localFromFrame ( StackFrame, Local ) [function]

    rule #localFromFrame(StackFrame(... locals: LOCALS), local(I:Int)) => {LOCALS[I]}:>TypedLocal
      requires 0 <=Int I
       andBool I <Int size(LOCALS)
       andBool isTypedLocal(LOCALS[I])
      [preserves-definedness] // valid list indexing checked

  syntax TypedLocal ::= #incrementRef ( TypedLocal ) [function, total]
                      | #decrementRef ( TypedLocal ) [function]

  rule #incrementRef(typedLocal(Reference(HEIGHT, PLACE, REFMUT), TY, MUT))
    => typedLocal(Reference(HEIGHT +Int 1, PLACE, REFMUT), TY, MUT)
  rule #incrementRef(TL) => TL [owise]

  rule #decrementRef(typedLocal(Reference(HEIGHT, PLACE, REFMUT), TY, MUT))
    => typedLocal(Reference(HEIGHT -Int 1, PLACE, REFMUT), TY, MUT)
    // requires 0 <Int HEIGHT
  rule #decrementRef(TL) => TL [owise]

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
     andBool isTypedLocal(LOCALS[I])
    [preserves-definedness]
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
     andBool isTypedLocal(LOCALS[I])
    [preserves-definedness] // valid list indexing checked

  syntax KItem ::= #markMoved ( TypedLocal, Local, ProjectionElems )
                |  #forceSetLocal ( Local )

  rule <k> VAL:TypedLocal ~> #markMoved(OLDLOCAL, LOCAL, PROJECTIONS) ~> CONT
        =>
           #updateProjected(OLDLOCAL, PROJECTIONS, Moved)
           ~> #forceSetLocal(LOCAL)
           ~> VAL
           ~> CONT
       </k>
    [preserves-definedness] // projections already used when reading, updateProjected should succeed

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

For binary operations generally, both arguments have to be read from the provided operands, followed by checking the types and then performing the actual operation (both implemented in `#compute`), which can return a `TypedLocal` or an error. A flag carries the information whether to perform an overflow check through to this function for `CheckedBinaryOp`.

```k
  syntax KItem ::= #suspend ( BinOp, Operand, Bool)
                |  #ready ( BinOp, TypedLocal, Bool )
                |  #compute ( BinOp, TypedLocal, TypedLocal, Bool ) [function, total]

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

There are also a few _unary_ operations (`UnOpNot`, `UnOpNeg`, `UnOpPtrMetadata`)  used in `RValue:UnaryOp`. These operations only read a single operand and do not need a `#suspend` helper.

```k
  syntax KItem ::= #applyUnOp ( UnOp )

  rule <k> rvalueUnaryOp(UNOP, OP1)
        =>
           #readOperand(OP1) ~> #applyUnOp(UNOP)
       ...
       </k>
```

#### Potential errors

```k
  syntax KItem ::= #OperationError( OperationError )

  syntax OperationError ::= TypeMismatch ( BinOp, Ty, Ty )
                          | OperandMismatch ( BinOp, Value, Value )
                          | OperandError( BinOp, TypedLocal, TypedLocal)
                          | OperandMismatch ( UnOp, Value )
                          | OperandError( UnOp, TypedLocal)
                          // errors above are compiler bugs or invalid MIR
                          | Unimplemented ( BinOp, TypedLocal, TypedLocal)
                          // errors below are program errors
                          | "DivisionByZero"
                          | "Overflow_U_B" // better than getting stuck

  // catch pathological cases where ARG1 or ARG2, or both, are Moved or NoValue.
  rule #compute(OP, ARG1, ARG2, _FLAG) => #OperationError(OperandError(OP, ARG1, ARG2))
    requires notBool (hasValue(ARG1) andBool hasValue(ARG2))

  // catch-all rule to make `#compute` total
  rule #compute(OP, ARG1, ARG2, _FLAG)
      =>
        #OperationError(Unimplemented(OP, ARG1, ARG2))
    [owise]
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
          typedLocal(Integer(ARG1, WIDTH, SIGNEDNESS), TY, _),
          typedLocal(Integer(ARG2, WIDTH, SIGNEDNESS), TY, _),
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
            ListItem(typedLocal(Integer(truncate(onInt(BOP, ARG1, ARG2), WIDTH, Signed), WIDTH, true), TY, mutabilityNot))
            ListItem(
              typedLocal(
                BoolVal(
                  // overflow: Result outside valid range
                  (1 <<Int (WIDTH -Int 1)) <=Int onInt(BOP, ARG1, ARG2)
                    orBool
                  onInt(BOP, ARG1, ARG2) <Int 0 -Int (1 <<Int (WIDTH -Int 1))
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
            ListItem(typedLocal(Integer(truncate(onInt(BOP, ARG1, ARG2), WIDTH, Unsigned), WIDTH, false), TY, mutabilityNot))
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

  // performing unchecked operations may result in undefined behaviour, which we signal.
  // The check it the same as the one for the overflow flag above

  rule #arithmeticInt(BOP, ARG1, ARG2, WIDTH, true, TY, false)
    => typedLocal(Integer(truncate(onInt(BOP, ARG1, ARG2), WIDTH, Signed), WIDTH, true), TY, mutabilityNot)
    requires isArithmetic(BOP)
    // infinite precision result must equal truncated result
     andBool truncate(onInt(BOP, ARG1, ARG2), WIDTH, Signed) ==Int onInt(BOP, ARG1, ARG2)
    [preserves-definedness]

  // unsigned numbers: simple overflow check using a bit mask
  rule #arithmeticInt(BOP, ARG1, ARG2, WIDTH, false, TY, false)
    => typedLocal(Integer(truncate(onInt(BOP, ARG1, ARG2), WIDTH, Unsigned), WIDTH, false), TY, mutabilityNot)
    requires isArithmetic(BOP)
    // infinite precision result must equal truncated result
     andBool truncate(onInt(BOP, ARG1, ARG2), WIDTH, Unsigned) ==Int onInt(BOP, ARG1, ARG2)
    [preserves-definedness]

  rule #arithmeticInt(BOP, _, _, _, _, _, false) => #OperationError(Overflow_U_B)
    requires isArithmetic(BOP)
    [owise]

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

  rule #compute(OP, typedLocal(_, TY, _), typedLocal(_, TY2, _), _) => #OperationError(TypeMismatch(OP, TY, TY2))
    requires isComparison(OP)
     andBool TY =/=K TY2

  rule #compute(OP, typedLocal(Integer(VAL1, WIDTH, SIGN), TY, _), typedLocal(Integer(VAL2, WIDTH, SIGN), TY, _), _)
      =>
        typedLocal(BoolVal(cmpOpInt(OP, VAL1, VAL2)), TyUnknown, mutabilityNot)
    requires isComparison(OP)

  rule #compute(OP, typedLocal(BoolVal(VAL1), TY, _), typedLocal(BoolVal(VAL2), TY, _), _)
      =>
        typedLocal(BoolVal(cmpOpBool(OP, VAL1, VAL2)), TyUnknown, mutabilityNot)
    requires isComparison(OP)

  rule #compute(OP, typedLocal(ARG1, TY, _), typedLocal(ARG2, TY, _), _)
      =>
        #OperationError(OperandMismatch(OP, ARG1, ARG2))
    [owise]
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

  rule #compute(binOpCmp, typedLocal(Integer(VAL1, WIDTH, SIGN), TY, _), typedLocal(Integer(VAL2, WIDTH, SIGN), TY, _), _)
      =>
        typedLocal(Integer(cmpInt(VAL1, VAL2), 8, true), TyUnknown, mutabilityNot)

  rule #compute(binOpCmp, typedLocal(BoolVal(VAL1), TY, _), typedLocal(BoolVal(VAL2), TY, _), _)
      =>
        typedLocal(Integer(cmpBool(VAL1, VAL2), 8, true), TyUnknown, mutabilityNot)

```

#### Unary operations on Boolean and integral values

The `unOpNeg` operation only works signed integral (and floating point) numbers.
An overflow can happen when negating the minimal representable integral value (in the given `WIDTH`). The semantics of the operation in this case is to wrap around (with the given bit width).

```k
  rule <k> typedLocal(Integer(VAL, WIDTH, true), TY, _) ~> #applyUnOp(unOpNeg)
          =>
            typedLocal(Integer(truncate(0 -Int VAL, WIDTH, Signed), WIDTH, true), TY, mutabilityNot)
        ...
        </k>

  // TODO add rule for Floats once they are supported.
```

The `unOpNot` operation works on boolean and integral values, with the usual semantics for booleans and a bitwise semantics for integral values (overflows cannot occur).

```k
  rule <k> typedLocal(BoolVal(VAL), TY, _) ~> #applyUnOp(unOpNot)
          =>
            typedLocal(BoolVal(notBool VAL), TY, mutabilityNot)
        ...
        </k>

  rule <k> typedLocal(Integer(VAL, WIDTH, true), TY, _) ~> #applyUnOp(unOpNot)
          =>
            typedLocal(Integer(truncate(~Int VAL, WIDTH, Signed), WIDTH, true), TY, mutabilityNot)
        ...
        </k>

  rule <k> typedLocal(Integer(VAL, WIDTH, false), TY, _) ~> #applyUnOp(unOpNot)
          =>
            typedLocal(Integer(truncate(~Int VAL, WIDTH, Unsigned), WIDTH, false), TY, mutabilityNot)
        ...
        </k>
```

```k
  rule <k> typedLocal(VAL, _, _) ~> #applyUnOp(OP) => #OperationError(OperandMismatch(OP, VAL)) ... </k>
    [owise]
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
  rule <k> rvalueNullaryOp(nullOpUbChecks, _) => typedLocal(BoolVal(false), TyUnknown, mutabilityNot) ... </k>
```

#### "Nullary" operations reifying type information

`nullOpSizeOf`
`nullOpAlignOf`
`nullOpOffsetOf(VariantAndFieldIndices)`

#### Other operations

`binOpOffset`

`unOpPtrMetadata`

```k
endmodule
```
