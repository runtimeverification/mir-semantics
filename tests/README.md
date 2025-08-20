### Reproduce stuck in `entrypoint::test_process_initialize_multisig`

```
#traverseProjection ( toLocal ( 2 ) , thunk ( #decodeConstant ( constantKindAllocated ( allocation ( ... bytes: b"\x00\x00\x00\x00\x00\x00\x00\x00" , provenance: provenanceMap ( ... ptrs: provenanceMapEntry ( ... provSize: 0 , allocId: allocId ( 98 ) )  .ProvenanceMapEntries ) , align: align ( 8 ) , mutability: mutabilityMut ) ) , ty ( 500125 ) , typeInfoRefType ( ty ( 500016 ) ) ) ) , projectionElemDeref  .ProjectionElems , .Contexts )
```

Can be reproduced through `thunk_decode_constant.rs`, see details in `thunk_decode_constant.md`

```
#traverseProjection ( toLocal ( 8 ) , thunk ( #decodeConstant ( constantKindAllocated ( allocation ( ... bytes: b"\x00\x00\x00\x00\x00\x00\x00\x00" , provenance: provenanceMap ( ... ptrs: provenanceMapEntry ( ... provSize: 0 , allocId: allocId ( 0 ) )  .ProvenanceMapEntries ) , align: align ( 8 ) , mutability: mutabilityMut ) ) , ty ( 25 ) , typeInfoRefType ( ty ( 16 ) ) ) ) , projectionElemDeref  .ProjectionElems , .Contexts )
```

## TypeError: 'NoneType' object is not subscriptable

mock_borrow_data_unchecked.rs

```
INFO 2025-08-19 13:08:34,055 kmir.cargo - Deleted: /Users/steven/Desktop/projs/solana-token/p-token/test-properties/mir-semantics/tests/mock_borrow_data_unchecked.smir.json
Traceback (most recent call last):
  File "/Users/steven/Desktop/projs/solana-token/p-token/test-properties/mir-semantics/kmir/.venv/bin/kmir", line 10, in <module>
    sys.exit(main())
  File "/Users/steven/Desktop/projs/solana-token/p-token/test-properties/mir-semantics/kmir/src/kmir/__main__.py", line 451, in main
    kmir(sys.argv[1:])
  File "/Users/steven/Desktop/projs/solana-token/p-token/test-properties/mir-semantics/kmir/src/kmir/__main__.py", line 218, in kmir
    _kmir_prove_rs(opts)
  File "/Users/steven/Desktop/projs/solana-token/p-token/test-properties/mir-semantics/kmir/src/kmir/__main__.py", line 66, in _kmir_prove_rs
    proof = kmir.prove_rs(opts)
  File "/Users/steven/Desktop/projs/solana-token/p-token/test-properties/mir-semantics/kmir/src/kmir/kmir.py", line 186, in prove_rs
    smir_info = smir_info.reduce_to(opts.start_symbol)
  File "/Users/steven/Desktop/projs/solana-token/p-token/test-properties/mir-semantics/kmir/src/kmir/smir.py", line 156, in reduce_to
    _LOGGER.debug(f'Reducing items, starting at {start_ty}. Call Edges {self.call_edges}')
  File "/opt/homebrew/Cellar/python@3.10/3.10.17/Frameworks/Python.framework/Versions/3.10/lib/python3.10/functools.py", line 981, in __get__
    val = self.func(instance)
  File "/Users/steven/Desktop/projs/solana-token/p-token/test-properties/mir-semantics/kmir/src/kmir/smir.py", line 183, in call_edges
    for b in item['mono_item_kind']['MonoItemFn']['body']['blocks']
TypeError: 'NoneType' object is not subscriptable
```

## Mock borrow_data_unchecked but encountered different stuck

`mock_borrow_data_unchecked_failed.rs`