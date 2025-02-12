# Handling Data for MIR Execution

This module addresses all aspects of handling "values"i.e., data), at runtime during MIR execution.


```k
module RT-DATA
  imports INT
  imports FLOAT
  imports BOOL
  imports BYTES
  imports MAP
  imports K-EQUAL

  imports TYPES
  imports BODY
```

Values in MIR are allocated arrays of `Bytes` that are interpreted according to their intended type, encoded as a `Ty` (type ID consistent across the program), and representing a `RigidTy` (other `TyKind` variants are not values that we need to operate on).

```k
  syntax LowLevelValue ::= value ( Bytes, Ty, RigidTy ) // TODO redundant information (Ty <-- -> RigidTy)
                         | "Moved"
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

### Setting local variables (including error cases)

Access to a `TypedLocal` (whether reading or writing( may fail for a number of reasons.
Every access is modelled as a _function_ whose result needs to be checked by the caller.

```k
  syntax LocalAccessError ::= LocalMoved( Int )
                            | TypeMismatch( Int, Ty, Ty )
                            | LocalNotMutable ( Int )
                            | "NoValueToWrite" 
```

The `#setLocal` function writes a `TypedLocal` value to a given `Place` within the `List` of local variables.
This may fail because a local may not be accessible, moved away, or not mutable.


```k
  // set a local to a new value. Assumes the place is valid
  syntax List ::= #setLocalValue(List, Place, TypedLocal) [function]

  rule #setLocalValue(LOCALS, _, typedLocal(NoValue, _, _))
     =>
       LOCALS // FIXME NoValueToWrite ?

  rule #setLocalValue(LOCALS, place(local(I), .ProjectionElems), typedLocal(V:Value, TY, _))
     =>
       LOCALS[I <- V]
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool tyOfLocal({LOCALS[I]}:>TypedLocal) ==K TY // matching type
     andBool (isMutable({LOCALS[I]}:>TypedLocal)  // either mutable
             orBool
              valueOfLocal({LOCALS[I]}:>TypedLocal) ==K NoValue) // or not set before
    [preserves-definedness] // valid list indexing checked

    // TODO error cases

```


```k
endmodule
```
