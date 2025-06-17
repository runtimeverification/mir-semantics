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

This module contains helper functions to operate on this type information.

## Compatibility of types (high-level representation)

When two types use the same representation for their values, these
values, and pointers to them, can be converted from one type to the other.
The `#typesCompatible` function determines this compatibility, and is by default `false`.

```k
  syntax Bool ::= #typesCompatible ( TypeInfo , TypeInfo , Map ) [function, total]

  // by default, only identical types are compatible
  rule #typesCompatible (             T            ,           T              ,   _    ) => true  [priority(60)] 
  rule #typesCompatible (             _            ,           _              ,   _    ) => false [owise] 
```

Arrays and slices are compatible if their element type is (ignoring length)
```k
  rule #typesCompatible ( typeInfoArrayType(TY1, _), typeInfoArrayType(TY2, _), TYPEMAP) => #typesCompatible({TYPEMAP[TY1]}:>TypeInfo, {TYPEMAP[TY2]}:>TypeInfo, TYPEMAP)
    requires isTypeInfo(TYPEMAP[TY1])
     andBool isTypeInfo(TYPEMAP[TY2])
```

Pointers are compatible if their pointee types are
```k
  rule #typesCompatible ( typeInfoPtrType(TY1)     , typeInfoPtrType(TY2)     , TYPEMAP) => true
    requires isTypeInfo(TYPEMAP[TY1])
     andBool isTypeInfo(TYPEMAP[TY2])
     andBool #typesCompatible({TYPEMAP[TY1]}:>TypeInfo, {TYPEMAP[TY2]}:>TypeInfo, TYPEMAP)
     [priority(59)]
```

Pointers to arrays/slices are compatible with pointers to the element type
```k
  rule #typesCompatible ( typeInfoPtrType(TY1)     , typeInfoPtrType(TY2)     , TYPEMAP) => true
    requires isTypeInfo(TYPEMAP[TY1])
     andBool #isArrayOf({TYPEMAP[TY1]}:>TypeInfo, TY2)

  rule #typesCompatible ( typeInfoPtrType(TY1)     , typeInfoPtrType(TY2)     , TYPEMAP) => true
    requires isTypeInfo(TYPEMAP[TY2])
     andBool #isArrayOf({TYPEMAP[TY2]}:>TypeInfo, TY1)

  syntax Bool ::= #isArrayOf ( TypeInfo , Ty ) [function, total]

  rule #isArrayOf(typeInfoArrayType(TY, _), TY) => true
  rule #isArrayOf(      _                 , _ ) => false [owise]
```



```k
endmodule
```
