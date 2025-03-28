# Value and Local Variable Sorts in MIR-Semantics

This is the base module for all data in KMIR at runtime. It defines how values and local variables (holding those) are represented.

```k
requires "../ty.md"
requires "../body.md"

module RT-VALUE-SYNTAX
  imports TYPES
  imports BODY
```

## Values in MIR

Values in MIR are represented at a certain abstraction level, interpreting the given `Bytes` of a constant according to the desired type. This allows for implementing operations on values using the higher-level type and improves readability of the program data in the K configuration.

High-level values can be
- a range of built-in types (signed and unsigned integer numbers, floats, `str` and `bool`)
- built-in product type constructs (`struct`s, `enum`s, and tuples, with heterogenous component types)
- references to a place in the current or an enclosing stack frame
- arrays and slices (with homogenous element types)

```k
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
```

## Local variables

A list `locals` of local variables of a stack frame is stored as values together
with their type information (to enable type-checking assignments). Also, the
`Mutability` is remembered to prevent mutation of immutable values.

The local variables may be actual values (`typedValue`), uninitialised (`NewLocal`) or `Moved`.

```k
  // local storage of the stack frame
  syntax TypedLocal ::= TypedValue | MovedLocal | NewLocal

  syntax TypedValue ::= typedValue ( Value , MaybeTy , Mutability )

  syntax MovedLocal ::= "Moved"

  syntax NewLocal ::= newLocal ( Ty , Mutability )

  // the type of aggregates cannot be determined from the data provided when they
  // occur as `RValue`, therefore we have to make the `Ty` field optional here.
  syntax MaybeTy ::= Ty
                   | "TyUnknown"

  // accessors
  syntax MaybeTy ::= tyOfLocal ( TypedLocal ) [function, total]
  // ----------------------------------------------------------
  rule tyOfLocal(typedValue(_, TY, _)) => TY
  rule tyOfLocal(Moved)                => TyUnknown
  rule tyOfLocal(newLocal(TY, _))      => TY

  syntax Mutability ::= mutabilityOf ( TypedLocal ) [function, total]
  // ----------------------------------------------------------------
  rule mutabilityOf(typedValue(_, _, MUT)) => MUT
  rule mutabilityOf(Moved)                 => mutabilityNot
  rule mutabilityOf(newLocal(_, MUT))      => MUT
```

## A generic MIR Error sort

```k
  syntax MIRError

```

```k
endmodule
```
