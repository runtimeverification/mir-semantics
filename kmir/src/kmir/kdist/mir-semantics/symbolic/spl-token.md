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

```k
module KMIR-SPL-TOKEN
  imports KMIR-P-TOKEN
```

## Helper syntax

```k
  syntax Value ::= SPLRc ( Value ) // work as reference to data and lamports
                 | SPLRefCell ( Place , Value , Bool )
                 | SPLDataBuffer ( Value )
                 | SPLDataBorrow ( Place , Value )
                 | SPLDataBorrowMut ( Place , Value )

  syntax Ty ::= #SPLAccountInfoTy() [function, total, symbol(#SPLAccountInfoTy)]
  rule #SPLAccountInfoTy() => ty(0)
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
                SPLRc(SPLRefCell(
                  place(LOCAL, appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(1), #SPLAccountInfoTy()) .ProjectionElems)),
                  Integer(?SplLamports:Int, 64, false),
                  true
                ))
              )                                                           // lamports: Rc<RefCell<&'a mut u64>>
              ListItem( // data: Rc<RefCell<&'a mut [u8]>>
                SPLRc(SPLRefCell(
                  place(LOCAL, appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(2), #SPLAccountInfoTy()) .ProjectionElems)),
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
              ),
                  true
                ))
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
    ensures size(?SplAccountKey) ==Int 32 andBool allBytes(?SplAccountKey)
      andBool size(?SplOwnerKey) ==Int 32 andBool allBytes(?SplOwnerKey)
      andBool 0 <=Int ?SplLamports andBool ?SplLamports <Int 18446744073709551616
      andBool 0 <=Int ?SplRentEpoch andBool ?SplRentEpoch <Int 18446744073709551616
      andBool size(?SplMintKey) ==Int 32 andBool allBytes(?SplMintKey)
      andBool size(?SplTokenOwnerKey) ==Int 32 andBool allBytes(?SplTokenOwnerKey)
      andBool 0 <=Int ?SplAmount andBool ?SplAmount <Int (1 <<Int 64)
      andBool 0 <=Int ?SplAccountState andBool ?SplAccountState <Int 256
      andBool 0 <=Int ?SplDelegatedAmount andBool ?SplDelegatedAmount <Int (1 <<Int 64)
      andBool (
        (?SplDelegateCOpt ==K Aggregate(variantIdx(0), .List))
        orBool
        (?SplDelegateCOpt ==K Aggregate(variantIdx(1), ListItem(Range(?SplDelegateKey:List)))
          andBool size(?SplDelegateKey) ==Int 32
          andBool allBytes(?SplDelegateKey))
      )
      andBool (
        (?SplCloseAuthCOpt ==K Aggregate(variantIdx(0), .List))
        orBool
        (?SplCloseAuthCOpt ==K Aggregate(variantIdx(1), ListItem(Range(?SplCloseAuthorityKey:List)))
          andBool size(?SplCloseAuthorityKey) ==Int 32
          andBool allBytes(?SplCloseAuthorityKey))
      )
      andBool (
        (?SplIsNativeCOpt ==K Aggregate(variantIdx(0), .List))
        orBool
        (?SplIsNativeCOpt ==K Aggregate(variantIdx(1), ListItem(Integer(?SplIsNativeAmount:Int, 64, false)))
          andBool 0 <=Int ?SplIsNativeAmount
          andBool ?SplIsNativeAmount <Int (1 <<Int 64))
      )
    [priority(30), preserves-definedness]
```

## Accessing `Rc<RefCell<_>>`

We shortcut the MIR field access that `<Rc<_> as Deref>::deref` performs and
expose the wrapped payload directly.

```k
  // rule <k> #traverseProjection(
  //            DEST,
  //            SPLRc(VALUE),
  //            projectionElemDeref PROJS,
  //            CTXTS
  //          )
  //       => #traverseProjection(
  //            DEST,
  //            VALUE,
  //            PROJS,
  //            CtxSPLRc CTXTS
  //          )
  //       ...
  //       </k>
  //   [priority(30)]

  // syntax Context ::= "CtxSPLRc"

  // rule #buildUpdate(VAL, CtxSPLRc CTXS) => #buildUpdate(SPLRc(VAL), CTXS)
  // rule #projectionsFor(CtxSPLRc CTXS, PROJS) => #projectionsFor(CTXS, projectionElemDeref PROJS)

  rule [spl-rc-deref]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, OP:Operand OPS:Operands, DEST, TARGET, UNWIND), _SPAN))
      => #finishSPLRcDeref(OP, DEST, TARGET, FUNC, OP OPS, UNWIND)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC)))
              ==String "<std::rc::Rc<std::cell::RefCell<std::vec::Vec<u8>>> as std::ops::Deref>::deref"
    [priority(30), preserves-definedness]

  syntax KItem ::= #finishSPLRcDeref ( Evaluation , Place , MaybeBasicBlockIdx , Operand , Operands , UnwindAction ) [seqstrict(1)]
                  | #resolveSPLRcRef ( Value , Place , MaybeBasicBlockIdx , Operand , Operands , UnwindAction )
                  | #finishResolvedSPLRc ( Place , MaybeBasicBlockIdx , Operand , Operands , UnwindAction )

  rule <k> #finishSPLRcDeref(Reference(OFFSET, PLACE, MUT, META), DEST, TARGET, FUNC, ARGS, UNWIND)
        => #resolveSPLRcRef(Reference(OFFSET, PLACE, MUT, META), DEST, TARGET, FUNC, ARGS, UNWIND)
       ...
      </k>

  rule <k> #resolveSPLRcRef(Reference(0, place(local(I), PROJS), _, _), DEST, TARGET, FUNC, ARGS, UNWIND)
        => #traverseProjection(
             toLocal(I),
             getValue(LOCALS, I),
             PROJS,
             .Contexts
           )
           ~> #readProjection(false)
           ~> #finishResolvedSPLRc(DEST, TARGET, FUNC, ARGS, UNWIND)
       ...
      </k>
      <locals> LOCALS </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])

  rule <k> #resolveSPLRcRef(Reference(OFFSET, place(local(I), PROJS), _, _), DEST, TARGET, FUNC, ARGS, UNWIND)
        => #traverseProjection(
             toStack(OFFSET, local(I)),
             #localFromFrame({STACK[OFFSET -Int 1]}:>StackFrame, local(I), OFFSET),
             PROJS,
             .Contexts
           )
           ~> #readProjection(false)
           ~> #finishResolvedSPLRc(DEST, TARGET, FUNC, ARGS, UNWIND)
       ...
      </k>
      <stack> STACK </stack>
    requires 0 <Int OFFSET
     andBool OFFSET <=Int size(STACK)
     andBool isStackFrame(STACK[OFFSET -Int 1])
     andBool 0 <=Int I
  
  rule <k> SPLRc(PAYLOAD) ~> #finishResolvedSPLRc(DEST, TARGET, _FUNC, _ARGS, _UNWIND)
        => #setLocalValue(DEST, PAYLOAD) ~> #continueAt(TARGET)
       ...
      </k>

  rule [spl-rc-deref-fallback]:
    <k> #finishSPLRcDeref(_VAL:Value, DEST, TARGET, FUNC, ARGS, UNWIND)
        => #setUpCalleeData(lookupFunction(#tyOfCall(FUNC)), ARGS)
        ...
       </k>
       <currentFunc> CALLER => #tyOfCall(FUNC) </currentFunc>
       <currentFrame>
         <currentBody> _ </currentBody>
         <caller> OLDCALLER => CALLER </caller>
         <dest> OLDDEST => DEST </dest>
         <target> OLDTARGET => TARGET </target>
         <unwind> OLDUNWIND => UNWIND </unwind>
         <locals> LOCALS </locals>
       </currentFrame>
       <stack> STACK => ListItem(StackFrame(OLDCALLER, OLDDEST, OLDTARGET, OLDUNWIND, LOCALS)) STACK </stack>
    [owise]
```

```k
  // rule <k> #traverseProjection(
  //            DEST,
  //            SPLRefCell(_, VALUE, _),
  //            projectionElemField(fieldIdx(2), TY) PROJS,
  //            CTXTS
  //          )
  //       => #traverseProjection(
  //            DEST,
  //            VALUE,
  //            PROJS,
  //            CtxSPLRefCell(TY) CTXTS
  //          )
  //       ...
  //       </k>
  //   [priority(30)]

  // syntax Context ::= CtxSPLRefCell ( Ty )

  // rule #buildUpdate(VAL, CtxSPLRefCell(_) CTXS) => #buildUpdate(SPLRefCell(_, VAL, _), CTXS)
  // rule #projectionsFor(CtxSPLRefCell(TY) CTXS, PROJS) => #projectionsFor(CTXS, projectionElemField(fieldIdx(2), TY) PROJS)
```

## Borrowed buffer projections

```k
  syntax Context ::= "CtxSPLDataBuffer"
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

  rule #buildUpdate(VAL, CtxSPLDataBuffer CTXS)
    => #buildUpdate(SPLDataBuffer(VAL), CTXS)
  rule #buildUpdate(VAL, CtxSPLDataBorrow(PLACE) CTXS)
    => #buildUpdate(SPLDataBorrow(PLACE, SPLDataBuffer(VAL)), CTXS)
  rule #buildUpdate(VAL, CtxSPLDataBorrowMut(PLACE) CTXS)
    => #buildUpdate(SPLDataBorrowMut(PLACE, SPLDataBuffer(VAL)), CTXS)

  rule #projectionsFor(CtxSPLDataBuffer CTXS, PROJS) => #projectionsFor(CTXS, PROJS)
  rule #projectionsFor(CtxSPLDataBorrow(_) CTXS, PROJS) => #projectionsFor(CTXS, PROJS)
  rule #projectionsFor(CtxSPLDataBorrowMut(_) CTXS, PROJS) => #projectionsFor(CTXS, PROJS)
```

## RefCell::<&mut [u8]> helpers

```k
  rule [spl-borrow-data]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(place(LOCAL, PROJS)) .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkSPLBorrowData(DEST, operandCopy(place(LOCAL, PROJS)), place(LOCAL, PROJS), false)
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "std::cell::RefCell::<std::vec::Vec<u8>>::borrow"
    [priority(30), preserves-definedness]

  rule [spl-borrow-mut-data]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(place(LOCAL, PROJS)) .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkSPLBorrowData(DEST, operandCopy(place(LOCAL, PROJS)), place(LOCAL, PROJS), true)
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "std::cell::RefCell::<std::vec::Vec<u8>>::borrow_mut"
    [priority(30), preserves-definedness]

  syntax KItem ::= #mkSPLBorrowData ( Place , Evaluation , Place , Bool ) [seqstrict(2)]

  rule <k> #mkSPLBorrowData(DEST, SPLRc(VAL), SRC, MUT)
        => #mkSPLBorrowData(DEST, VAL, SRC, MUT)
       ...
      </k>

  rule <k> #mkSPLBorrowData(DEST, SPLRefCell(PLACE, BUF, _), _SRC, false)
        => #setLocalValue(DEST, SPLDataBorrow(PLACE, BUF))
        ...
       </k>

  rule <k> #mkSPLBorrowData(DEST, SPLRefCell(PLACE, BUF, true), _SRC, true)
        => #setLocalValue(DEST, SPLDataBorrowMut(PLACE, BUF))
        ...
       </k>
```

## Vec::<u8> helpers

```k
  rule [spl-vec-as-slice]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(ARG) .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkSPLVecAsSlice(DEST, operandCopy(ARG))
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "std::vec::Vec::<u8>::as_slice"
    [priority(30), preserves-definedness]

  rule [spl-vec-deref]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(ARG) .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkSPLVecAsSlice(DEST, operandCopy(ARG))
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "<std::vec::Vec<u8> as std::ops::Deref>::deref"
    [priority(30), preserves-definedness]

  rule [spl-vec-index-mut-copy]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(ARG) _OPS:Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkSPLVecAsSlice(DEST, operandCopy(ARG))
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC)))
              ==String "<std::vec::Vec<u8> as std::ops::IndexMut<std::ops::RangeFull>>::index_mut"
    [priority(30), preserves-definedness]

  rule [spl-vec-index-mut-move]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandMove(ARG) _OPS:Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkSPLVecAsSlice(DEST, operandMove(ARG))
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC)))
              ==String "<std::vec::Vec<u8> as std::ops::IndexMut<std::ops::RangeFull>>::index_mut"
    [priority(30), preserves-definedness]

  syntax KItem ::= #mkSPLVecAsSlice ( Place , Evaluation ) [seqstrict(2)]

  rule <k> #mkSPLVecAsSlice(DEST, SPLDataBorrow(PLACE, BUF))
        => #setLocalValue(DEST, SPLDataBorrow(PLACE, BUF))
        ...
       </k>

  rule <k> #mkSPLVecAsSlice(DEST, SPLDataBorrowMut(PLACE, BUF))
        => #setLocalValue(DEST, SPLDataBorrowMut(PLACE, BUF))
        ...
       </k>

  rule [spl-vec-as-slice-owise]:
    <k> #mkSPLVecAsSlice(DEST, VAL)
        => #setLocalValue(DEST, VAL)
       ...
      </k>
    [owise]
```

## `Ref`/`RefMut` deref shortcuts

```k
  rule [spl-ref-deref-copy]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(ARG) _OPS:Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkSPLRefDeref(DEST, operandCopy(ARG))
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC)))
              ==String "<std::cell::Ref<'_, std::vec::Vec<u8>> as std::ops::Deref>::deref"
         orBool #functionName(lookupFunction(#tyOfCall(FUNC)))
              ==String "<std::cell::RefMut<'_, std::vec::Vec<u8>> as std::ops::Deref>::deref"
         orBool #functionName(lookupFunction(#tyOfCall(FUNC)))
              ==String "<std::cell::RefMut<'_, std::vec::Vec<u8>> as std::ops::DerefMut>::deref_mut"
         orBool #functionName(lookupFunction(#tyOfCall(FUNC)))
              ==String "<core::cell::RefMut<'_, alloc::vec::Vec<u8>> as core::ops::DerefMut>::deref_mut"
         orBool #functionName(lookupFunction(#tyOfCall(FUNC)))
              ==String "<std::cell::RefMut<'_, alloc::vec::Vec<u8>> as std::ops::DerefMut>::deref_mut"
         orBool #functionName(lookupFunction(#tyOfCall(FUNC)))
              ==String "<core::cell::RefMut<'_, std::vec::Vec<u8>> as core::ops::DerefMut>::deref_mut"
         orBool #functionName(lookupFunction(#tyOfCall(FUNC)))
              ==String "_ZN74_$LT$core..cell..RefMut$LT$T$GT$$u20$as$u20$core..ops..deref..DerefMut$GT$9deref_mut17h1f6c73b55db865d0E"
    [priority(30), preserves-definedness]

  rule [spl-ref-deref-move]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandMove(ARG) _OPS:Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkSPLRefDeref(DEST, operandMove(ARG))
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC)))
              ==String "<std::cell::Ref<'_, std::vec::Vec<u8>> as std::ops::Deref>::deref"
         orBool #functionName(lookupFunction(#tyOfCall(FUNC)))
              ==String "<std::cell::RefMut<'_, std::vec::Vec<u8>> as std::ops::Deref>::deref"
         orBool #functionName(lookupFunction(#tyOfCall(FUNC)))
              ==String "<std::cell::RefMut<'_, std::vec::Vec<u8>> as std::ops::DerefMut>::deref_mut"
         orBool #functionName(lookupFunction(#tyOfCall(FUNC)))
              ==String "<core::cell::RefMut<'_, alloc::vec::Vec<u8>> as core::ops::DerefMut>::deref_mut"
         orBool #functionName(lookupFunction(#tyOfCall(FUNC)))
              ==String "<std::cell::RefMut<'_, alloc::vec::Vec<u8>> as std::ops::DerefMut>::deref_mut"
         orBool #functionName(lookupFunction(#tyOfCall(FUNC)))
              ==String "<core::cell::RefMut<'_, std::vec::Vec<u8>> as core::ops::DerefMut>::deref_mut"
         orBool #functionName(lookupFunction(#tyOfCall(FUNC)))
              ==String "_ZN74_$LT$core..cell..RefMut$LT$T$GT$$u20$as$u20$core..ops..deref..DerefMut$GT$9deref_mut17h1f6c73b55db865d0E"
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
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(ARG) .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkSPLAccountUnpack(DEST, operandCopy(ARG))
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires (
        #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "spl_token::state::Account::unpack_unchecked"
      orBool
        #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "spl_token::state::Account::unpack"
      orBool
        #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "Account::unpack_unchecked"
    )
    [priority(30), preserves-definedness]

  syntax KItem ::= #mkSPLAccountUnpack ( Place , Evaluation ) [seqstrict(2)]

  rule <k> #mkSPLAccountUnpack(DEST, Reference(0, place(local(I), .ProjectionElems), _, _))
        => #mkSPLAccountUnpack(DEST, getValue(LOCALS, I))
       ...
      </k>
      <locals> LOCALS </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])

  rule <k> #mkSPLAccountUnpack(DEST, Reference(OFFSET, place(local(I), .ProjectionElems), _, _))
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

  rule [spl-account-pack-copy-copy]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(SRC) operandCopy(BUF) .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkSPLAccountPack(operandCopy(SRC), operandCopy(BUF), DEST)
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires (
        #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "spl_token::state::Account::pack"
      orBool
        #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "Account::pack"
    )
    [priority(30), preserves-definedness]

  rule [spl-account-pack-move-copy]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandMove(SRC) operandCopy(BUF) .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkSPLAccountPack(operandMove(SRC), operandCopy(BUF), DEST)
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires (
        #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "spl_token::state::Account::pack"
      orBool
        #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "Account::pack"
    )
    [priority(30), preserves-definedness]

  rule [spl-account-pack-copy-move]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(SRC) operandMove(BUF) .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkSPLAccountPack(operandCopy(SRC), operandMove(BUF), DEST)
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires (
        #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "spl_token::state::Account::pack"
      orBool
        #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "Account::pack"
    )
    [priority(30), preserves-definedness]

  rule [spl-account-pack-move-move]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandMove(SRC) operandMove(BUF) .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkSPLAccountPack(operandMove(SRC), operandMove(BUF), DEST)
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires (
        #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "spl_token::state::Account::pack"
      orBool
        #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "Account::pack"
    )
    [priority(30), preserves-definedness]

  syntax KItem ::= #mkSPLAccountPack ( Evaluation , Evaluation , Place ) [seqstrict(1,2)]

  rule <k> #mkSPLAccountPack(ACCOUNT, SPLDataBorrowMut(PLACE, SPLDataBuffer(_)), DEST)
        => #forceSetPlaceValue(
             PLACE,
             SPLRc(SPLRefCell(PLACE, SPLDataBuffer(ACCOUNT), true))
           )
         ~> #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(Aggregate(variantIdx(0), .List))))
        ...
       </k>
```

```k
endmodule
```
