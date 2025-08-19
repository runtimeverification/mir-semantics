### Reproduce stuck in `entrypoint::test_process_initialize_multisig`

```
#traverseProjection ( toLocal ( 2 ) , thunk ( #decodeConstant ( constantKindAllocated ( allocation ( ... bytes: b"\x00\x00\x00\x00\x00\x00\x00\x00" , provenance: provenanceMap ( ... ptrs: provenanceMapEntry ( ... provSize: 0 , allocId: allocId ( 98 ) )  .ProvenanceMapEntries ) , align: align ( 8 ) , mutability: mutabilityMut ) ) , ty ( 500125 ) , typeInfoRefType ( ty ( 500016 ) ) ) ) , projectionElemDeref  .ProjectionElems , .Contexts )
```

Can be reproduced through `thunk_decode_constant.rs`, see details in `thunk_decode_constant.md`

```
#traverseProjection ( toLocal ( 8 ) , thunk ( #decodeConstant ( constantKindAllocated ( allocation ( ... bytes: b"\x00\x00\x00\x00\x00\x00\x00\x00" , provenance: provenanceMap ( ... ptrs: provenanceMapEntry ( ... provSize: 0 , allocId: allocId ( 0 ) )  .ProvenanceMapEntries ) , align: align ( 8 ) , mutability: mutabilityMut ) ) , ty ( 25 ) , typeInfoRefType ( ty ( 16 ) ) ) ) , projectionElemDeref  .ProjectionElems , .Contexts )
```