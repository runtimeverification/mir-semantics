# Helpers for type metadata (`TypeInfo`)

```k
requires "../ty.md"

module RT-TYPES
  imports BOOL
  imports MAP
  imports K-EQUAL

  imports TYPES

```

Type metadata from Stable MIR JSON is present in a type lookup table `Ty -> TypeInfo` at runtime. 

This module contains helper funcitons to operate on this type information.

## Compatibility of types (high-level representation)

When two types use the same representation for their values, these
values, and pointers to them, can be converted from one type to the other.
The `#typesCompatible` function determines this compatibility, and is by default `false`.

```k
  syntax Bool ::= #typesCompatible ( TypeInfo , TypeInfo , Map ) [function, total]

  // by default, only identical types are compatible
  rule #typesCompatible (             T1           ,           T2             ,   _    ) => T1 ==K T2 [priority(60)] 
  // arrays and slices are compatible if their element type is (ignoring length)
  rule #typesCompatible ( typeInfoArrayType(TY1, _), typeInfoArrayType(TY2, _), TYPEMAP) => #typesCompatible({TYPEMAP[TY1]}:>TypeInfo, {TYPEMAP[TY2]}:>TypeInfo, TYPEMAP)
    requires isTypeInfo(TYPEMAP[TY1])
     andBool isTypeInfo(TYPEMAP[TY2])
  // pointers are compatible if their pointee types are
  rule #typesCompatible ( typeInfoPtrType(TY1)     , typeInfoPtrType(TY2)     , TYPEMAP) => #typesCompatible({TYPEMAP[TY1]}:>TypeInfo, {TYPEMAP[TY2]}:>TypeInfo, TYPEMAP)
    requires isTypeInfo(TYPEMAP[TY1])
     andBool isTypeInfo(TYPEMAP[TY2])
```

```k
endmodule
```
