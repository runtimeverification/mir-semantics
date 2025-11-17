```k
requires "../kmir-ast.md"
requires "../rt/data.md"
requires "../kmir.md"
requires "../rt/configuration.md"
```

We mirror the Solana `AccountInfo` layout so that MIR code can traverse the
fields exactly as it would against the real SPL runtime.  The account data
contains the real SPL `Account` struct layout described in `info.md`
(`mint`, `owner`, `amount`, `COption<Pubkey>`, `AccountState`, `COption<u64>`,
`delegated_amount`, `COption<Pubkey>`).  No Pinocchio-specific payloads are
embedded.

## Data Access Overview

```
cheatcode_is_spl_account(acc)
Account::unpack_unchecked(&acc.data.borrow())
Account::pack(a, &mut acc.data.borrow_mut())
  -> #isSPLRcRefCellDerefFunc                        (rule [spl-rc-deref])
  -> #isSPLBorrowFunc                                (rule [spl-borrow-data])
  -> #isSPLRefDerefFunc                              (rule [spl-ref-deref])
  -> Borrowed buffer projections
  -> #isSPLAccountUnpackFunc / #isSPLAccountPackFunc (rule [spl-account-unpack])
```


```k
module KMIR-SPL-TOKEN
  imports KMIR-P-TOKEN
```

## Helper syntax

```k
  syntax Value ::= SPLRefCell ( Place , Value )
                 | SPLDataBuffer ( Value )
                 | SPLDataBorrow ( Place , Value )
                 | SPLDataBorrowMut ( Place , Value )
```

## Helper predicates

```k
  syntax Bool ::= #isSplPubkey ( List ) [function, total]
  rule #isSplPubkey(KEY) => size(KEY) ==Int 32 andBool allBytes(KEY)

  syntax Bool ::= #isSplCOptionPubkey ( Value ) [function, total]
  rule #isSplCOptionPubkey(Aggregate(variantIdx(0), .List)) => true
  rule #isSplCOptionPubkey(Aggregate(variantIdx(1), ListItem(Range(KEY)) REST))
    => #isSplPubkey(KEY)
    requires REST ==K .List
  rule #isSplCOptionPubkey(_) => false [owise]

  syntax Bool ::= #isSplCOptionU64 ( Value ) [function, total]
  rule #isSplCOptionU64(Aggregate(variantIdx(0), .List)) => true
  rule #isSplCOptionU64(Aggregate(variantIdx(1), ListItem(Integer(AMT, 64, false)) REST))
    => 0 <=Int AMT andBool AMT <Int (1 <<Int 64)
    requires REST ==K .List
  rule #isSplCOptionU64(_) => false [owise]

  syntax Bool ::= #isSPLRcRefCellDerefFunc ( String ) [function, total]
  // mock
  rule #isSPLRcRefCellDerefFunc("<std::rc::Rc<std::cell::RefCell<std::vec::Vec<u8>>> as std::ops::Deref>::deref") => true
  // real
  rule #isSPLRcRefCellDerefFunc("<std::rc::Rc<std::cell::RefCell<&mut [u8]>> as std::ops::Deref>::deref") => true
  rule #isSPLRcRefCellDerefFunc(_) => false [owise]

  syntax Bool ::= #isSPLBorrowFunc ( String ) [function, total]
  // mock
  rule #isSPLBorrowFunc("std::cell::RefCell::<std::vec::Vec<u8>>::borrow") => true
  rule #isSPLBorrowFunc("std::cell::RefCell::<std::vec::Vec<u8>>::borrow_mut") => true
  // real
  rule #isSPLBorrowFunc("std::cell::RefCell::<&mut [u8]>::borrow") => true
  rule #isSPLBorrowFunc("std::cell::RefCell::<&mut [u8]>::borrow_mut") => true
  rule #isSPLBorrowFunc(_) => false [owise]

  syntax Bool ::= #isSPLBorrowMutFunc ( String ) [function, total]
  // mock
  rule #isSPLBorrowMutFunc("std::cell::RefCell::<std::vec::Vec<u8>>::borrow_mut") => true
  // real
  rule #isSPLBorrowMutFunc("std::cell::RefCell::<&mut [u8]>::borrow_mut") => true
  rule #isSPLBorrowMutFunc(_) => false [owise]

//                 | #isSPLVecSliceFunc      ( String ) [function, total]

//   rule #isSPLVecSliceFunc("std::vec::Vec::<u8>::as_slice") => true
//   rule #isSPLVecSliceFunc("std::vec::Vec::<u8>::as_mut_slice") => true
//   rule #isSPLVecSliceFunc("<std::vec::Vec<u8> as std::ops::Deref>::deref") => true
//   rule #isSPLVecSliceFunc("<std::vec::Vec<u8> as std::ops::DerefMut>::deref_mut") => true
//   rule #isSPLVecSliceFunc("<std::vec::Vec<u8> as std::ops::IndexMut<std::ops::RangeFull>>::index_mut") => true
//   rule #isSPLVecSliceFunc(_) => false [owise]


  syntax Bool ::= #isSPLRefDerefFunc      ( String ) [function, total]
  // mock
  rule #isSPLRefDerefFunc("<std::cell::Ref<'_, std::vec::Vec<u8>> as std::ops::Deref>::deref") => true
  // real
  rule #isSPLRefDerefFunc("<std::cell::Ref<'_, &mut [u8]> as std::ops::Deref>::deref") => true
  rule #isSPLRefDerefFunc("<std::cell::RefMut<'_, &mut [u8]> as std::ops::DerefMut>::deref_mut") => true
  rule #isSPLRefDerefFunc(_) => false [owise]
//   rule #isSPLRefDerefFunc("<std::cell::RefMut<'_, std::vec::Vec<u8>> as std::ops::Deref>::deref") => true
//   rule #isSPLRefDerefFunc("<std::cell::RefMut<'_, std::vec::Vec<u8>> as std::ops::DerefMut>::deref_mut") => true
//   rule #isSPLRefDerefFunc("<std::cell::RefMut<'_, &mut [u8]> as std::ops::Deref>::deref") => true
//   rule #isSPLRefDerefFunc("<std::cell::RefMut<'_, &mut [u8]> as std::ops::DerefMut>::deref_mut") => true
//   rule #isSPLRefDerefFunc("<core::cell::RefMut<'_, alloc::vec::Vec<u8>> as core::ops::DerefMut>::deref_mut") => true
//   rule #isSPLRefDerefFunc("<std::cell::RefMut<'_, alloc::vec::Vec<u8>> as std::ops::DerefMut>::deref_mut") => true
//   rule #isSPLRefDerefFunc("<core::cell::RefMut<'_, std::vec::Vec<u8>> as core::ops::DerefMut>::deref_mut") => true

  syntax Bool ::= #isSPLAccountUnpackFunc ( String ) [function, total]
  rule #isSPLAccountUnpackFunc("solana_program_pack::<spl_token_interface::state::Account as solana_program_pack::Pack>::unpack_unchecked") => true
  rule #isSPLAccountUnpackFunc("solana_program_pack::<spl_token_interface::state::Account as solana_program_pack::Pack>::unpack") => true
  rule #isSPLAccountUnpackFunc("Account::unpack_unchecked") => true
  rule #isSPLAccountUnpackFunc(_) => false [owise]

   syntax Bool ::= #isSPLAccountPackFunc   ( String ) [function, total]
  rule #isSPLAccountPackFunc("solana_program_pack::<spl_token_interface::state::Account as solana_program_pack::Pack>::pack") => true
  rule #isSPLAccountPackFunc("Account::pack") => true
  rule #isSPLAccountPackFunc(_) => false [owise]
```


## Cheatcode handling
```{.k .symbolic}
  rule [cheatcode-is-spl-account]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(place(LOCAL, PROJS)) .Operands, _DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #setLocalValue(
            place(LOCAL, appendP(PROJS, projectionElemDeref .ProjectionElems)),
            Aggregate(variantIdx(0),
              ListItem(Range(?SplAccountKey:List))                         // pub key: &'a Pubkey
              ListItem(
                  SPLRefCell(
                    place(
                      LOCAL,
                      appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(1), #hack()) .ProjectionElems)
                    ),
                    Integer(?SplLamports:Int, 64, false)
                  )
              ) // lamports: Rc<RefCell<&'a mut u64>>
              ListItem( // data: Rc<RefCell<&'a mut [u8]>>
                  SPLRefCell(
                    place(
                      LOCAL,
                      appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(2), #hack()) .ProjectionElems)
                    ),
                    SPLDataBuffer( // data: Rc<RefCell<&'a mut [u8]>>, Aggregate is for &account.data
                      Aggregate(variantIdx(0),
                        ListItem(Range(?SplMintKey:List))                        // Account.mint: Pubkey
                        ListItem(Range(?SplTokenOwnerKey:List))                  // Account.owner: Pubkey
                        ListItem(Integer(?SplAmount:Int, 64, false))             // Account.amount: u64
                        ListItem(?SplDelegateCOpt:Value)                         // Account.delegate: COption<Pubkey>
                        ListItem(Integer(?SplAccountState:Int, 8, false))        // Account.state: AccountState (repr u8)
                        ListItem(?SplIsNativeCOpt:Value)                         // Account.is_native: COption<u64>
                        ListItem(Integer(?SplDelegatedAmount:Int, 64, false))    // Account.delegated_amount: u64
                        ListItem(?SplCloseAuthCOpt:Value)                        // Account.close_authority: COption<Pubkey>
                    )
                  )
                )
              )
              ListItem(Range(?SplOwnerKey))                                // owner: &'a Pubkey
              ListItem(Integer(?SplRentEpoch:Int, 64, false))              // rent_epoch: u64
              ListItem(BoolVal(?_SplIsSigner:Bool))                        // is_signer: bool
              ListItem(BoolVal(?_SplIsWritable:Bool))                      // is_writable: bool
              ListItem(BoolVal(?_SplExecutable:Bool))                      // executable: bool
            )
         )
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "spl_token::entrypoint::cheatcode_is_spl_account"
      orBool #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "cheatcode_is_spl_account" 
    ensures #isSplPubkey(?SplAccountKey)
      andBool #isSplPubkey(?SplOwnerKey)
      andBool 0 <=Int ?SplLamports andBool ?SplLamports <Int 18446744073709551616
      andBool 0 <=Int ?SplRentEpoch andBool ?SplRentEpoch <Int 18446744073709551616
      andBool #isSplPubkey(?SplMintKey)
      andBool #isSplPubkey(?SplTokenOwnerKey)
      andBool 0 <=Int ?SplAmount andBool ?SplAmount <Int (1 <<Int 64)
      andBool 0 <=Int ?SplAccountState andBool ?SplAccountState <Int 256
      andBool 0 <=Int ?SplDelegatedAmount andBool ?SplDelegatedAmount <Int (1 <<Int 64)
      andBool #isSplCOptionPubkey(?SplDelegateCOpt)
      andBool #isSplCOptionPubkey(?SplCloseAuthCOpt)
      andBool #isSplCOptionU64(?SplIsNativeCOpt)
    [priority(30), preserves-definedness]
```

## Accessing `Rc<RefCell<_>>`

We shortcut the MIR field access that `<Rc<_> as Deref>::deref` performs and
expose the wrapped payload directly.

```k
  rule [spl-rc-deref]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, OP:Operand _OPS:Operands, DEST, TARGET, _UNWIND), _SPAN))
      => #finishSPLRcDeref(OP, DEST, TARGET)
    ...
    </k>
    requires #isSPLRcRefCellDerefFunc(#functionName(lookupFunction(#tyOfCall(FUNC))))
    [priority(30), preserves-definedness]

  syntax KItem ::= #finishSPLRcDeref ( Evaluation , Place , MaybeBasicBlockIdx ) [seqstrict(1)]
                  | #resolveSPLRcRef ( Value , Place , MaybeBasicBlockIdx )
                  | #finishResolvedSPLRc ( Place , MaybeBasicBlockIdx )

  rule <k> #finishSPLRcDeref(Reference(OFFSET, PLACE, MUT, META), DEST, TARGET)
        => #resolveSPLRcRef(Reference(OFFSET, PLACE, MUT, META), DEST, TARGET)
       ...
      </k>

  rule <k> #resolveSPLRcRef(Reference(0, place(local(I), PROJS), _, _), DEST, TARGET)
        => #traverseProjection(
             toLocal(I),
             getValue(LOCALS, I),
             PROJS,
             .Contexts
           )
           ~> #readProjection(false)
           ~> #finishResolvedSPLRc(DEST, TARGET)
       ...
      </k>
      <locals> LOCALS </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])

  rule <k> #resolveSPLRcRef(Reference(OFFSET, place(local(I), PROJS), _, _), DEST, TARGET)
        => #traverseProjection(
             toStack(OFFSET, local(I)),
             #localFromFrame({STACK[OFFSET -Int 1]}:>StackFrame, local(I), OFFSET),
             PROJS,
             .Contexts
           )
           ~> #readProjection(false)
           ~> #finishResolvedSPLRc(DEST, TARGET)
       ...
      </k>
      <stack> STACK </stack>
    requires 0 <Int OFFSET
     andBool OFFSET <=Int size(STACK)
     andBool isStackFrame(STACK[OFFSET -Int 1])
     andBool 0 <=Int I

  // If the deref doesn't return `SPLRefCell`, it will stuck there;
  // TODO: fallback to ordinary call when it's not `SPLRefCell`
  rule <k> SPLRefCell(PLACE, VAL) ~> #finishResolvedSPLRc(DEST, TARGET)
        => #setLocalValue(DEST, SPLRefCell(PLACE, VAL)) ~> #continueAt(TARGET)
       ...
      </k>
```

## Borrowed buffer projections

```k
  // Step 1
  syntax Context ::= CtxSPLRefCell ( Place )
  rule <k> #traverseProjection(
             DEST,
             SPLRefCell(PLACE, VAL),
             projectionElemDeref PROJS,
             CTXTS
           )
        => #traverseProjection(
             DEST,
             VAL,
             PROJS,
             CtxSPLRefCell(PLACE) CTXTS
           )
        ...
       </k>
    [priority(30)]
  rule #buildUpdate(VAL, CtxSPLRefCell(PLACE) CTXS) => #buildUpdate(SPLRefCell(PLACE, VAL), CTXS)
  rule #projectionsFor(CtxSPLRefCell(_) CTXS, PROJS) => #projectionsFor(CTXS, projectionElemDeref PROJS)

  // Step 2 
  syntax Context ::= CtxSPLDataBorrow ( Place )
  rule <k> #traverseProjection(
             DEST,
             SPLDataBorrow(PLACE, VAL),
             projectionElemDeref PROJS,
             CTXTS
           )
        => #traverseProjection(
             DEST,
             VAL,
             PROJS,
             CtxSPLDataBorrow(PLACE) CTXTS
           )
        ...
       </k>
    [priority(30)]
  rule #buildUpdate(VAL, CtxSPLDataBorrow(PLACE) CTXS) => #buildUpdate(SPLDataBorrow(PLACE, SPLDataBuffer(VAL)), CTXS)
  rule #projectionsFor(CtxSPLDataBorrow(_) CTXS, PROJS) => #projectionsFor(CTXS, projectionElemDeref PROJS)

  syntax Context ::= CtxSPLDataBorrowMut ( Place )
  rule <k> #traverseProjection(
             DEST,
             SPLDataBorrowMut(PLACE, VAL),
             projectionElemDeref PROJS,
             CTXTS
           )
        => #traverseProjection(
             DEST,
             VAL,
             PROJS,
             CtxSPLDataBorrowMut(PLACE) CTXTS
           )
        ...
       </k>
    [priority(30)]
  rule #buildUpdate(VAL, CtxSPLDataBorrowMut(PLACE) CTXS) => #buildUpdate(SPLDataBorrowMut(PLACE, SPLDataBuffer(VAL)), CTXS)
  rule #projectionsFor(CtxSPLDataBorrowMut(_) CTXS, PROJS) => #projectionsFor(CTXS, projectionElemDeref PROJS)

  // Step 3
  syntax Context ::= "CtxSPLDataBuffer"
  rule <k> #traverseProjection(
             DEST,
             SPLDataBuffer(VALUE),
             projectionElemDeref PROJS,
             CTXTS
           )
        => #traverseProjection(
             DEST,
             VALUE,
             PROJS,
             CtxSPLDataBuffer CTXTS
           )
        ...
       </k>
    [priority(30)]
  rule #buildUpdate(VAL, CtxSPLDataBuffer CTXS) => #buildUpdate(SPLDataBuffer(VAL), CTXS)
  rule #projectionsFor(CtxSPLDataBuffer CTXS, PROJS) => #projectionsFor(CTXS, projectionElemDeref PROJS)
```

``` 
                   | CtxSPLRefCell       ( Place )
                   | CtxSPLDataBorrow    ( Place )
                   | CtxSPLDataBorrowMut ( Place )

  rule <k> #traverseProjection(
             DEST,
             SPLDataBuffer(VALUE),
             PROJS,
             CTXTS
           )
        => #traverseProjection(
             DEST,
             VALUE,
             PROJS,
             CtxSPLDataBuffer CTXTS
           )
        ...
       </k>
    requires PROJS =/=K .ProjectionElems
    [priority(30)]

  rule <k> #traverseProjection(
             DEST,
             SPLDataBorrow(PLACE, SPLDataBuffer(VALUE)),
             projectionElemDeref PROJS,
             CTXTS
           )
        => #traverseProjection(
             DEST,
             VALUE,
             PROJS,
             CtxSPLDataBorrow(PLACE) CTXTS
           )
        ...
       </k>
    [priority(25)]

  rule <k> #traverseProjection(
             DEST,
             SPLDataBorrow(PLACE, SPLDataBuffer(VALUE)),
             PROJS,
             CTXTS
           )
        => #traverseProjection(
             DEST,
             VALUE,
             PROJS,
             CtxSPLDataBorrow(PLACE) CTXTS
           )
        ...
       </k>
    requires PROJS =/=K .ProjectionElems
    [priority(30)]

  // real
  rule <k> #traverseProjection(
             DEST,
             SPLDataBorrowMut(PLACE, SPLDataBuffer(VALUE)),
             projectionElemDeref PROJS,
             CTXTS
           )
        => #traverseProjection(
             DEST,
             VALUE,
             PROJS,
             CtxSPLDataBorrowMut(PLACE) CTXTS
           )
        ...
       </k>
    [priority(25)]

  rule <k> #traverseProjection(
             DEST,
             SPLDataBorrowMut(PLACE, SPLDataBuffer(VALUE)),
             PROJS,
             CTXTS
           )
        => #traverseProjection(
             DEST,
             VALUE,
             PROJS,
             CtxSPLDataBorrowMut(PLACE) CTXTS
           )
        ...
       </k>
    requires PROJS =/=K .ProjectionElems
    [priority(30)]

  rule #buildUpdate(VAL, CtxSPLRefCell(PLACE) CTXS)
    => #buildUpdate(SPLRefCell(PLACE, VAL), CTXS)
  rule #buildUpdate(VAL, CtxSPLDataBuffer CTXS)
    => #buildUpdate(SPLDataBuffer(VAL), CTXS)
  rule #buildUpdate(VAL, CtxSPLDataBorrow(PLACE) CTXS)
    => #buildUpdate(SPLDataBorrow(PLACE, SPLDataBuffer(VAL)), CTXS)
  rule #buildUpdate(VAL, CtxSPLDataBorrowMut(PLACE) CTXS)
    => #buildUpdate(SPLDataBorrowMut(PLACE, SPLDataBuffer(VAL)), CTXS)

  rule #projectionsFor(CtxSPLRefCell(_) CTXS, PROJS) => #projectionsFor(CTXS, PROJS)
  rule #projectionsFor(CtxSPLDataBuffer CTXS, PROJS) => #projectionsFor(CTXS, PROJS)
  rule #projectionsFor(CtxSPLDataBorrow(_) CTXS, PROJS) => #projectionsFor(CTXS, PROJS)
  rule #projectionsFor(CtxSPLDataBorrowMut(_) CTXS, PROJS) => #projectionsFor(CTXS, PROJS)
```

## RefCell::<&mut [u8]> helpers

```k
  rule [spl-borrow-data]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(place(LOCAL, PROJS)) .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkSPLBorrowData(
           DEST,
           operandCopy(place(LOCAL, PROJS)),
           place(LOCAL, PROJS),
           #isSPLBorrowMutFunc(#functionName(lookupFunction(#tyOfCall(FUNC))))
         )
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #isSPLBorrowFunc(#functionName(lookupFunction(#tyOfCall(FUNC))))
    [priority(30), preserves-definedness]

  syntax KItem ::= #mkSPLBorrowData ( Place , Evaluation , Place , Bool ) [seqstrict(2)]

  rule <k> #mkSPLBorrowData(DEST, SPLRefCell(PLACE, BUF), _SRC, false)
        => #setLocalValue(DEST, SPLRefCell(PLACE, SPLDataBorrow(PLACE, BUF)))
        ...
       </k>

  rule <k> #mkSPLBorrowData(DEST, SPLRefCell(PLACE, BUF), _SRC, true)
        => #setLocalValue(DEST, SPLRefCell(PLACE, SPLDataBorrowMut(PLACE, BUF)))
        ...
       </k>
```

## Vec::<u8> helpers

``` 
  rule [spl-vec-as-slice-copy]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, OP:Operand _OPS:Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #setLocalValue(DEST, OP) ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #isSPLVecSliceFunc(#functionName(lookupFunction(#tyOfCall(FUNC))))
    [priority(30), preserves-definedness]
```

## `Ref`/`RefMut` deref shortcuts

```k
  rule [spl-ref-deref]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, ARG_OP:Operand _OPS:Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkSPLRefDeref(DEST, ARG_OP)
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #isSPLRefDerefFunc(#functionName(lookupFunction(#tyOfCall(FUNC))))
    [priority(30), preserves-definedness]

  syntax KItem ::= #mkSPLRefDeref ( Place , Evaluation ) [seqstrict(2)]

  rule <k> #mkSPLRefDeref(DEST, Reference(0, place(local(I), .ProjectionElems), _, _))
        => #mkSPLRefDeref(DEST, getValue(LOCALS, I))
       ...
      </k>
      <locals> LOCALS </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])

  rule <k> #mkSPLRefDeref(DEST, Reference(OFFSET, place(local(I), .ProjectionElems), _, _))
        => #mkSPLRefDeref(
             DEST,
             #localFromFrame({STACK[OFFSET -Int 1]}:>StackFrame, local(I), OFFSET)
           )
       ...
      </k>
      <stack> STACK </stack>
    requires 0 <Int OFFSET
     andBool OFFSET <=Int size(STACK)
     andBool isStackFrame(STACK[OFFSET -Int 1])
     andBool 0 <=Int I

  rule <k> #mkSPLRefDeref(DEST, SPLDataBorrow(_, _) #as BORROW)
        => #setLocalValue(DEST, BORROW)
        ...
       </k>

  rule <k> #mkSPLRefDeref(DEST, SPLDataBorrowMut(_, _) #as BORROW)
        => #setLocalValue(DEST, BORROW)
        ...
       </k>

  rule [spl-ref-deref-owise]:
    <k> #mkSPLRefDeref(DEST, VAL)
        => #setLocalValue(DEST, VAL)
       ...
      </k>
    [owise]
```

## Account::unpack / Account::pack
```k
  rule [spl-account-unpack]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, OP:Operand .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkSPLAccountUnpack(DEST, OP)
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #isSPLAccountUnpackFunc(#functionName(lookupFunction(#tyOfCall(FUNC))))
    [priority(30), preserves-definedness]

  syntax KItem ::= #mkSPLAccountUnpack ( Place , Evaluation ) [seqstrict(2)]

  rule <k> #mkSPLAccountUnpack(DEST, Reference(0, place(local(I), projectionElemDeref .ProjectionElems), _, _))
        => #mkSPLAccountUnpack(DEST, getValue(LOCALS, I))
       ...
      </k>
      <locals> LOCALS </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])

  rule <k> #mkSPLAccountUnpack(DEST, Reference(OFFSET, place(local(I), projectionElemDeref .ProjectionElems), _, _))
        => #mkSPLAccountUnpack(
             DEST,
             #localFromFrame({STACK[OFFSET -Int 1]}:>StackFrame, local(I), OFFSET)
           )
       ...
      </k>
      <stack> STACK </stack>
    requires 0 <Int OFFSET
     andBool OFFSET <=Int size(STACK)
     andBool isStackFrame(STACK[OFFSET -Int 1])
     andBool 0 <=Int I

  rule <k> #mkSPLAccountUnpack(DEST, SPLDataBorrow(_, SPLDataBuffer(ACCOUNT)))
      => #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(ACCOUNT)))
      ...
      </k>

  rule <k> #mkSPLAccountUnpack(DEST, SPLDataBorrowMut(_, SPLDataBuffer(ACCOUNT)))
        => #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(ACCOUNT)))
        ...
       </k>
```

```k
  rule [spl-account-pack]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, SRC_OP:Operand BUF_OP:Operand .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkSPLAccountPack(SRC_OP, BUF_OP, DEST)
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #isSPLAccountPackFunc(#functionName(lookupFunction(#tyOfCall(FUNC))))
    [priority(30), preserves-definedness]

  syntax KItem ::= #mkSPLAccountPack ( Evaluation , Evaluation , Place ) [seqstrict(1,2)]

  rule <k> #mkSPLAccountPack(ACCOUNT, SPLDataBorrowMut(PLACE, SPLDataBuffer(_)), DEST)
        => #forceSetPlaceValue(
             PLACE,
             SPLRefCell(PLACE, SPLDataBuffer(ACCOUNT))
           )
         ~> #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(Aggregate(variantIdx(0), .List))))
        ...
       </k>
```

```k
endmodule
```
