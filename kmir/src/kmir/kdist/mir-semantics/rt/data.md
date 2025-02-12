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

**TODO** We might step away from this byte-oriented representation for values to a higher-level representation outlined below. This would assume that a `#decode` function `(Ty, Bytes( -> HiLevelValue` is available.

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

### Setting local variables (including error cases)

The `#setLocalValue` operation writes a `TypedLocal` value to a given `Place` within the `List` of local variables currently on top of the stack. This may fail because a local may not be accessible, moved away, or not mutable.

```k
  syntax KItem ::= #setLocalValue( Place, TypedLocal )

  // error cases first
  rule <k> #setLocalValue( place(local(I) #as LOCAL, _), _) => #LocalError(InvalidLocal(LOCAL)) ... </k>
       <locals> LOCALS </locals>
    requires size(LOCALS) <Int I orBool I <=Int 0

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
  rule <k> #setLocalValue( _, typedLocal(NoValue, _, _)) => .K ... </k>

  // if all is well, write the value
  // mutable case
  rule <k> #setLocalValue(place(local(I), .ProjectionElems), typedLocal(VAL, TY, _ )) ~> CONT
          =>
           CONT
          ...
       </k>
       <locals> LOCALS[I <- typedLocal(VAL, TY, mutabilityMut)] </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isValue(VAL)
     andBool tyOfLocal({LOCALS[I]}:>TypedLocal) ==K TY // matching type
     andBool isMutable({LOCALS[I]}:>TypedLocal)        // mutable
    [preserves-definedness] // valid list indexing checked

  // uninitialised case
  rule <k> #setLocalValue(place(local(I), .ProjectionElems), typedLocal(VAL, TY, _ )) ~> CONT
          =>
           CONT
          ...
       </k>
       <locals> LOCALS[I <- typedLocal(VAL, TY, mutabilityNot)] </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool VAL =/=K NoValue
     andBool tyOfLocal({LOCALS[I]}:>TypedLocal) ==K TY         // matching type
     andBool notBool isMutable({LOCALS[I]}:>TypedLocal)        // not mutable but
     andBool valueOfLocal({LOCALS[I]}:>TypedLocal) ==K NoValue // not initialised yet
    [preserves-definedness] // valid list indexing checked

  // projections not supported yet
  rule <k> #setLocalValue(place(local(_:Int), PROJECTION:ProjectionElems), _ )
          =>
           #LocalError(Unsupported(""))
          ...
       </k>
    requires PROJECTION =/=K .ProjectionElems
```


```k
endmodule
```
