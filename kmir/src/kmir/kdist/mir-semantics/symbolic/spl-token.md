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
                 | SPLRefCell ( Value )
                 | SPLDataBuffer ( Value )
                 | SPLDataBorrow ( Place , Value )
                 | SPLDataBorrowMut ( Place , Value )
```


## Cheatcode handling
```{.k .symbolic}
  rule [cheatcode-is-spl-account]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(place(LOCAL, PROJS)) .Operands, _DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #setLocalValue(
            place(LOCAL, appendP(PROJS, projectionElemDeref .ProjectionElems)),
            Aggregate(variantIdx(0),
              ListItem(Range(?SplAccountKey:List))                         // pub key: &'a Pubkey
              ListItem(SPLRc(SPLRefCell(Integer(?SplLamports:Int, 64, false)))) // lamports: Rc<RefCell<&'a mut u64>>
              ListItem(Aggregate(variantIdx(0), ListItem( Aggregate(variantIdx(0), ListItem( // data: Rc<RefCell<&'a mut [u8]>>
                SPLRc(SPLRefCell(SPLDataBuffer( // data: Rc<RefCell<&'a mut [u8]>>, Aggregate is for &account.data
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
              ))))))))
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


```k
  rule <k> #cast(SPLRc(VALUE), castKindPtrToPtr, TY_SOURCE, TY_TARGET)
          => SPLRc(VALUE) ...
        </k>
      requires #typesCompatible(lookupTy(TY_SOURCE), lookupTy(TY_TARGET))
      [preserves-definedness] // valid map lookups checked
```

We shortcut the MIR field access that `<Rc<_> as Deref>::deref` performs and
expose the wrapped payload directly.

```k
  rule <k> #traverseProjection(
             DEST,
             SPLRc(VALUE),
             projectionElemDeref PROJS,
             CTXTS
           )
        => #traverseProjection(
             DEST,
             VALUE,
             PROJS,
             CtxSPLRc CTXTS
           )
        ...
        </k>
    [priority(30)]

  syntax Context ::= "CtxSPLRc"

  rule #buildUpdate(VAL, CtxSPLRc CTXS) => #buildUpdate(SPLRc(VAL), CTXS)
  rule #projectionsFor(CtxSPLRc CTXS, PROJS) => #projectionsFor(CTXS, projectionElemDeref PROJS)

  rule [spl-rc-deref]:
    <k> #execTerminator(
           terminator(
             terminatorKindCall(FUNC, OP:Operand OPS:Operands, DEST, TARGET, UNWIND),
             _SPAN))
      => #finishSPLRcDeref(OP, DEST, TARGET, FUNC, OP OPS, UNWIND)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC)))
              ==String "<std::rc::Rc<std::cell::RefCell<std::vec::Vec<u8>>> as std::ops::Deref>::deref"
    [priority(30), preserves-definedness]

  syntax KItem ::= #finishSPLRcDeref ( Evaluation , Place , MaybeBasicBlockIdx , Operand , Operands , UnwindAction ) [seqstrict(1)]

  // rule <k> #finishSPLRcDeref(SPLRc(VALUE), DEST, TARGET, _FUNC, _ARGS, _UNWIND)
  //       => #setLocalValue(DEST, VALUE) ~> #continueAt(TARGET)
  //       ...
  //      </k>

  // rule [spl-rc-deref-fallback]:
  //   <k> #finishSPLRcDeref(_VAL:Value, DEST, TARGET, FUNC, ARGS, UNWIND)
  //       => #setUpCalleeData(lookupFunction(#tyOfCall(FUNC)), ARGS)
  //       ...
  //      </k>
  //      <currentFunc> CALLER => #tyOfCall(FUNC) </currentFunc>
  //      <currentFrame>
  //        <currentBody> _ </currentBody>
  //        <caller> OLDCALLER => CALLER </caller>
  //        <dest> OLDDEST => DEST </dest>
  //        <target> OLDTARGET => TARGET </target>
  //        <unwind> OLDUNWIND => UNWIND </unwind>
  //        <locals> LOCALS </locals>
  //      </currentFrame>
  //      <stack> STACK => ListItem(StackFrame(OLDCALLER, OLDDEST, OLDTARGET, OLDUNWIND, LOCALS)) STACK </stack>
  //   [owise]
```

```k
  rule <k> #traverseProjection(
             DEST,
             SPLRefCell(VALUE),
             projectionElemField(fieldIdx(2), TY) PROJS,
             CTXTS
           )
        => #traverseProjection(
             DEST,
             VALUE,
             PROJS,
             CtxSPLRefCell(TY) CTXTS
           )
        ...
        </k>
    [priority(30)]

  syntax Context ::= CtxSPLRefCell ( Ty )

  rule #buildUpdate(VAL, CtxSPLRefCell(_) CTXS) => #buildUpdate(SPLRefCell(VAL), CTXS)
  rule #projectionsFor(CtxSPLRefCell(TY) CTXS, PROJS) => #projectionsFor(CTXS, projectionElemField(fieldIdx(2), TY) PROJS)
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

  // rule <k> #mkSPLBorrowData(DEST, SPLRefCellData(BUF), SRC, false)
  //       => #setLocalValue(DEST, SPLDataBorrow(SRC, BUF))
  //       ...
  //      </k>

  // rule <k> #mkSPLBorrowData(DEST, SPLRefCellData(BUF), SRC, true)
  //       => #setLocalValue(DEST, SPLDataBorrowMut(SRC, BUF))
  //       ...
  //      </k>
```

```k
endmodule
```
