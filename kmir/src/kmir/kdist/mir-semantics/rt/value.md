# Value and Local Variable Sorts in MIR-Semantics

This is the base module for all data in KMIR at runtime. It defines how values and local variables (holding those) are represented.

```k
requires "../ty.md"
requires "../body.md"
requires "../lib.md"
requires "../mono.md"

module RT-VALUE-SYNTAX
  imports TYPES
  imports BODY
  imports LIB
  imports MONO
```

## Values in MIR

Values in MIR are represented at a certain abstraction level, interpreting the given `Bytes` of a constant according to the desired type. This allows for implementing operations on values using the higher-level type and improves readability of the program data in the K configuration.

High-level values can be
- a range of built-in types (signed and unsigned integer numbers, floats, `str` and `bool`)
- built-in product type constructs (`struct`s, `enum`s, and tuples, with heterogenous component types)
- references to a place in the current or an enclosing stack frame
- arrays and slices (with homogenous element types)

The special `Moved` value represents values that have been used and should not be accessed any more.
`Moved` values may be overwritten with a new value but using them will halt execution.

```k
  syntax Value ::= Integer( Int, Int, Bool )              [symbol(Value::Integer)]
                   // value, bit-width, signedness   for un/signed int
                 | BoolVal( Bool )                        [symbol(Value::BoolVal)]
                   // boolean
                 | StringVal( String )                    [symbol(Value::StringVal)]
                   // UTF-8 encoded Unicode string
                 | Aggregate( VariantIdx , List )         [symbol(Value::Aggregate)]
                   // heterogenous value list        for tuples and structs (standard, tuple, or anonymous)
                 | Float( Float, Int )                    [symbol(Value::Float)]
                   // value, bit-width               for f16-f128
                 | Reference( Int , Place , Mutability , Metadata)
                                                          [symbol(Value::Reference)]
                   // stack depth (initially 0), place, borrow kind, metadata (size, pointer offset, origin size)
                 | Range( List )                          [symbol(Value::Range)]
                   // homogenous values              for array/slice
                 | PtrLocal( Int , Place , Mutability, Metadata )
                                                          [symbol(Value::PtrLocal)]
                   // pointer to a local TypedValue (on the stack)
                   // fields are the same as in Reference
                 | AllocRef ( AllocId , ProjectionElems , Metadata )
                                                          [symbol(Value::AllocRef)]
                   // reference to static allocation, by AllocId, possibly projected, carrying metadata if applicable
                 | "Moved"
                   // The value has been used and is gone now
```

### Metadata for References and Pointers

Because the semantics uses abstract high-level values, Rust's concept of _fat and thin_
pointers has to be emulated when handling reference and pointer data.

A _thin pointer_ in Rust is simply an address of data in the heap or on the stack.

A _fat pointer_ in Rust is a pair of an address and [additional metadata about the pointee](https://doc.rust-lang.org/std/ptr/trait.Pointee.html#associatedtype.Metadata).
This is necessary for dynamically-sized pointee types (most prominently slices) and dynamic trait objects.

References to arrays and slices carry `Metadata`. In Rust `Metadata` is only a size, but we need more information to detect UB, so we track `(Size, Ptr Offset, Origin Size)`
For array types with statically-known size, the metadata size is set to `staticSize` to avoid repeated type lookups.
Other types without metadata use `noMetadataSize`.

```k
  // Origin size is since a pointer might not have size iteself but should be in bounds of an aggregate origin
  syntax Metadata ::= metadata ( MetadataSize, Int, MetadataSize) [symbol(Metadata)]
                            // ( Size, Pointer Offset, Origin Size )

  syntax MetadataSize ::= "noMetadataSize" [symbol(noMetadataSize)]
                    | staticSize  ( Int )  [symbol(staticSize)]
                    | dynamicSize ( Int )  [symbol(dynamicSize)]
```

## Local variables

A list `locals` of local variables of a stack frame is stored as values together
with their type information (to enable type-checking assignments). Also, the
`Mutability` is remembered to prevent mutation of immutable values.

The local variables may be actual values (`typedValue`) or uninitialised (`NewLocal`).

```k
  // local storage of the stack frame
  syntax TypedLocal ::= TypedValue | NewLocal

  syntax TypedValue ::= typedValue ( Value , Ty , Mutability ) [symbol(typedValue)]

  syntax NewLocal ::= newLocal ( Ty , Mutability )             [symbol(newLocal)]

  // accessors
  syntax Ty ::= tyOfLocal ( TypedLocal ) [function, total]
  // -----------------------------------------------------
  rule tyOfLocal(typedValue(_, TY, _)) => TY
  rule tyOfLocal(newLocal(TY, _))      => TY

  syntax Mutability ::= mutabilityOf ( TypedLocal ) [function, total]
  // ----------------------------------------------------------------
  rule mutabilityOf(typedValue(_, _, MUT)) => MUT
  rule mutabilityOf(newLocal(_, MUT))      => MUT

  syntax Value ::= valueOf ( TypedValue ) [function, total]
  // ------------------------------------------------------
  rule valueOf(typedValue(V, _, _)) => V
```

## Evaluating Items to `Value`s

Many built-in operations (`RValue` or type casts) use `Operand`s that will evaluate to a value of sort `Value`.
The basic operations of reading and writing those values can use K's "heating" and "cooling" rules to describe their evaluation to `Value`s.

```k
  syntax Evaluation ::= Value // other sorts are added at the first use site

  syntax KResult ::= Value
```

## A generic MIR Error sort

```k
  syntax MIRError

```

# Static data

These functions are global static data  accessed from many places, and will be extended for the particular program.

**TODO find a better home for these definitions.**

```k
  // // function store, Ty -> MonoItemFn
  syntax MonoItemKind ::= lookupFunction ( Ty ) [function, total, symbol(lookupFunction)]
  // ------------------------------------------------------------
  rule lookupFunction(ty(TY)) => monoItemFn(symbol("** UNKNOWN FUNCTION **"), defId(TY), noBody) [owise] // HACK
  // cannot be total without a default "error" element. `Ty` is key for both functions and data.

  // // static allocations: AllocId -> AllocData (Value or error)
  syntax Evaluation ::= lookupAlloc ( AllocId ) [function, total, symbol(lookupAlloc)]
  // -----------------------------------------------------------
  rule lookupAlloc(ID) => InvalidAlloc(ID) [owise]

  syntax Evaluation ::= InvalidAlloc ( AllocId )

  // // static information about the base type interning in the MIR: Ty -> TypeInfo
  syntax TypeInfo ::= lookupTy ( Ty )    [function, total, symbol(lookupTy)]
  // -----------------------------------------------------
  rule lookupTy(_TY) => typeInfoVoidType [owise] // HACK
```

```k
endmodule
```
