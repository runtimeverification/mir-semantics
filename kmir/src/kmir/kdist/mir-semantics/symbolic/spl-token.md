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
  -> #isSPLUnpackFunc / #isSPLPackFunc (rule [spl-account-unpack])
```


```k
module KMIR-SPL-TOKEN
  imports KMIR-P-TOKEN
  imports KMIR-INTRINSICS
```

## Helper operations for projected writes

```k
  syntax KItem ::= #forceSetPlaceValue ( Place , Evaluation ) [seqstrict(2)]
                 | #writeProjectionForce ( Value )

  rule <k> #forceSetPlaceValue(place(local(I), .ProjectionElems), VAL) => .K ... </k>
       <locals>
          LOCALS => LOCALS[I <- typedValue(VAL, tyOfLocal(getLocal(LOCALS, I)), mutabilityOf(getLocal(LOCALS, I)))]
       </locals>
    requires 0 <=Int I andBool I <Int size(LOCALS)
     andBool isTypedLocal(LOCALS[I])
    [preserves-definedness]

  rule <k> #forceSetPlaceValue(place(local(I), PROJ), VAL)
        => #traverseProjection(toLocal(I), getValue(LOCALS, I), PROJ, .Contexts)
        ~> #writeProjectionForce(VAL)
       ...
       </k>
       <locals> LOCALS </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool PROJ =/=K .ProjectionElems
     andBool isTypedLocal(LOCALS[I])
    [preserves-definedness]

  rule <k> #traverseProjection(toLocal(I), _ORIGINAL, .ProjectionElems, CONTEXTS)
        ~> #writeProjectionForce(NEW)
        => #forceSetLocal(local(I), #buildUpdate(NEW, CONTEXTS))
       ...
       </k>
       <locals> LOCALS </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     [preserves-definedness]

  rule <k> #traverseProjection(toStack(FRAME, local(I)), _ORIGINAL, .ProjectionElems, CONTEXTS)
        ~> #writeProjectionForce(NEW)
        => .K
       ...
       </k>
       <stack> STACK
            => STACK[(FRAME -Int 1) <-
                      #updateStackLocal(
                        {STACK[FRAME -Int 1]}:>StackFrame,
                        I,
                        #adjustRef(#buildUpdate(NEW, CONTEXTS), 0 -Int FRAME)
                      )
                    ]
       </stack>
    requires 0 <Int FRAME andBool FRAME <=Int size(STACK)
     andBool isStackFrame(STACK[FRAME -Int 1])
    [preserves-definedness]
```

## Helper syntax

```k
  syntax Value ::= SPLRefCell ( Place , Value )
                 | SPLDataBuffer ( Value )
                 | SPLDataBorrow ( Place , Value )
                 | SPLDataBorrowMut ( Place , Value )
                 | SPLPubkeyRef ( Value )
```

## Helper predicates

```k
  syntax Bool ::= #isSplPubkey ( List ) [function, total]
  rule #isSplPubkey(KEY) => size(KEY) ==Int 32 andBool allBytes(KEY)

  syntax Bool ::= #isSplCOptionPubkey ( Value ) [function, total]
  rule #isSplCOptionPubkey(Aggregate(variantIdx(0), .List)) => true
  rule #isSplCOptionPubkey(Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(0), ListItem(Range(KEY))))))
    => #isSplPubkey(KEY)
  rule #isSplCOptionPubkey(_) => false [owise]

  syntax Bool ::= #isSplCOptionU64 ( Value ) [function, total]
  rule #isSplCOptionU64(Aggregate(variantIdx(0), .List)) => true
  rule #isSplCOptionU64(Aggregate(variantIdx(1), ListItem(Integer(AMT, 64, false)) REST))
    => 0 <=Int AMT andBool AMT <Int (1 <<Int 64)
    requires REST ==K .List
  rule #isSplCOptionU64(_) => false [owise]

  // AccountState in SPL semantics is carried as an enum variantIdx(0..2); accept legacy u8 too.
  syntax Bool ::= #isSplAccountStateVal ( Value ) [function, total]
  rule #isSplAccountStateVal(Aggregate(variantIdx(N), .List)) => 0 <=Int N andBool N <=Int 2
  rule #isSplAccountStateVal(_) => false [owise]

  syntax Bool ::= #isSPLRcRefCellDerefFunc ( String ) [function, total]
  rule #isSPLRcRefCellDerefFunc("<std::rc::Rc<std::cell::RefCell<&mut [u8]>> as std::ops::Deref>::deref") => true
  rule #isSPLRcRefCellDerefFunc("<std::rc::Rc<std::cell::RefCell<&mut u64>> as std::ops::Deref>::deref") => true
  rule #isSPLRcRefCellDerefFunc(_) => false [owise]

  syntax Bool ::= #isSPLBorrowFunc ( String ) [function, total]
  rule #isSPLBorrowFunc("std::cell::RefCell::<&mut [u8]>::borrow") => true
  rule #isSPLBorrowFunc("std::cell::RefCell::<&mut [u8]>::borrow_mut") => true
  rule #isSPLBorrowFunc("std::cell::RefCell::<&mut u64>::borrow") => true
  rule #isSPLBorrowFunc("std::cell::RefCell::<&mut u64>::borrow_mut") => true
  rule #isSPLBorrowFunc(_) => false [owise]

  syntax Bool ::= #isSPLBorrowMutFunc ( String ) [function, total]
  rule #isSPLBorrowMutFunc("std::cell::RefCell::<&mut [u8]>::borrow_mut") => true
  rule #isSPLBorrowMutFunc("std::cell::RefCell::<&mut u64>::borrow_mut") => true
  rule #isSPLBorrowMutFunc(_) => false [owise]

  syntax Bool ::= #isSPLRefDerefFunc      ( String ) [function, total]
  rule #isSPLRefDerefFunc("<std::cell::Ref<'_, &mut [u8]> as std::ops::Deref>::deref") => true
  rule #isSPLRefDerefFunc("<std::cell::RefMut<'_, &mut [u8]> as std::ops::DerefMut>::deref_mut") => true
  rule #isSPLRefDerefFunc("<std::cell::Ref<'_, &mut u64> as std::ops::Deref>::deref") => true
  rule #isSPLRefDerefFunc("<std::cell::RefMut<'_, &mut u64> as std::ops::DerefMut>::deref_mut") => true
  rule #isSPLRefDerefFunc(_) => false [owise]

  syntax Bool ::= #isSPLUnpackFunc ( String ) [function, total]
  rule #isSPLUnpackFunc(_) => false [owise]
  // spl-token account
  rule #isSPLUnpackFunc("solana_program_pack::<spl_token_interface::state::Account as solana_program_pack::Pack>::unpack_unchecked") => true
  rule #isSPLUnpackFunc("solana_program_pack::<spl_token_interface::state::Account as solana_program_pack::Pack>::unpack") => true
  // mock account
  rule #isSPLUnpackFunc("Account::unpack_unchecked") => true
  // spl-token mint
  rule #isSPLUnpackFunc("solana_program_pack::<spl_token_interface::state::Mint as solana_program_pack::Pack>::unpack_unchecked") => true
  rule #isSPLUnpackFunc("solana_program_pack::<spl_token_interface::state::Mint as solana_program_pack::Pack>::unpack") => true
  // mock mint
  rule #isSPLUnpackFunc("Mint::unpack_unchecked") => true

  syntax Bool ::= #isSPLPackFunc   ( String ) [function, total]
  rule #isSPLPackFunc(_) => false [owise]
  // spl-token account
  rule #isSPLPackFunc("solana_program_pack::<spl_token_interface::state::Account as solana_program_pack::Pack>::pack") => true
  // mock account
  rule #isSPLPackFunc("Account::pack") => true
  // spl-token mint
  rule #isSPLPackFunc("solana_program_pack::<spl_token_interface::state::Mint as solana_program_pack::Pack>::pack") => true
  // mock mint
  rule #isSPLPackFunc("Mint::pack") => true

  // Rent sysvar calls (includes mock harness direct calls to Rent::from_account_info / Rent::get)
  syntax Bool ::= #isSPLRentFromAccountInfoFunc ( String ) [function, total]
  rule #isSPLRentFromAccountInfoFunc(_) => false [owise]
  rule #isSPLRentFromAccountInfoFunc("Rent::from_account_info") => true   // mock harness
  rule #isSPLRentFromAccountInfoFunc("solana_sysvar::<solana_rent::Rent as solana_sysvar::Sysvar>::from_account_info") => true

  syntax Bool ::= #isSPLRentGetFunc ( String ) [function, total]
  rule #isSPLRentGetFunc(_) => false [owise]
  rule #isSPLRentGetFunc("Rent::get") => true   // mock harness
  rule #isSPLRentGetFunc("solana_sysvar::rent::<impl Sysvar for solana_rent::Rent>::get") => true
```

## Slice metadata for SPL account buffers

```k
  // Account data (&mut [u8]) length hints (Account::LEN)
  rule #maybeDynamicSize(
         dynamicSize(_),
         SPLDataBuffer(
         Aggregate(variantIdx(0),
           ListItem(Aggregate(variantIdx(0), ListItem(Range(_))))          // mint
           ListItem(Aggregate(variantIdx(0), ListItem(Range(_))))          // owner
           ListItem(Integer(_, 64, false))                                // amount
           ListItem(_DELEG)                                               // delegate COption
           ListItem(STATE)                                                // state
           ListItem(_IS_NATIVE)                                           // is_native COption
           ListItem(Integer(_, 64, false))                                // delegated_amount
           ListItem(_CLOSE)                                               // close_authority COption
         )
       )
      )
       => dynamicSize(165)
       requires #isSplAccountStateVal(STATE)
       [priority(30)]

  rule #maybeDynamicSize(
         dynamicSize(_),
         SPLDataBorrow(_, SPLDataBuffer(
         Aggregate(variantIdx(0),
           ListItem(Aggregate(variantIdx(0), ListItem(Range(_))))
           ListItem(Aggregate(variantIdx(0), ListItem(Range(_))))
           ListItem(Integer(_, 64, false))
           ListItem(_DELEG)
           ListItem(STATE)
           ListItem(_IS_NATIVE)
           ListItem(Integer(_, 64, false))
           ListItem(_CLOSE)
         )
       ))
      )
       => dynamicSize(165)
       requires #isSplAccountStateVal(STATE)
       [priority(30)]

  rule #maybeDynamicSize(
         dynamicSize(_),
         SPLDataBorrowMut(_, SPLDataBuffer(
         Aggregate(variantIdx(0),
           ListItem(Aggregate(variantIdx(0), ListItem(Range(_))))
           ListItem(Aggregate(variantIdx(0), ListItem(Range(_))))
           ListItem(Integer(_, 64, false))
           ListItem(_DELEG)
           ListItem(STATE)
           ListItem(_IS_NATIVE)
           ListItem(Integer(_, 64, false))
           ListItem(_CLOSE)
         )
       ))
      )
       => dynamicSize(165)
       requires #isSplAccountStateVal(STATE)
       [priority(30)]

  // Mint data (&mut [u8]) length hints (Mint::LEN)
  rule #maybeDynamicSize(
         dynamicSize(_),
         SPLDataBuffer(
           Aggregate(variantIdx(0),
             ListItem(_AUTH)                    // mint_authority COption
             ListItem(Integer(_, 64, false))    // supply
             ListItem(Integer(_, 8, false))     // decimals
             ListItem(BoolVal(_))               // is_initialized
             ListItem(_FREEZE)                  // freeze_authority COption
           )
         )
       )
       => dynamicSize(82)
       [priority(30)]

  rule #maybeDynamicSize(
         dynamicSize(_),
         SPLDataBorrow(_, SPLDataBuffer(
           Aggregate(variantIdx(0),
             ListItem(_AUTH)
             ListItem(Integer(_, 64, false))
             ListItem(Integer(_, 8, false))
             ListItem(BoolVal(_))
             ListItem(_FREEZE)
           )
         ))
       )
       => dynamicSize(82)
       [priority(30)]

  rule #maybeDynamicSize(
         dynamicSize(_),
         SPLDataBorrowMut(_, SPLDataBuffer(
           Aggregate(variantIdx(0),
             ListItem(_AUTH)
             ListItem(Integer(_, 64, false))
             ListItem(Integer(_, 8, false))
             ListItem(BoolVal(_))
             ListItem(_FREEZE)
           )
         ))
       )
       => dynamicSize(82)
       [priority(30)]

  // Rent data (&mut [u8]) length hints (Rent::LEN)
  rule #maybeDynamicSize(
         dynamicSize(_),
         SPLDataBuffer(
           Aggregate(variantIdx(0),
             ListItem(Integer(_, 64, false))    // lamports_per_byte_year
             ListItem(Float(2.0, 64))           // exemption_threshold
             ListItem(Integer(_, 8, false))     // burn_percent
           )
         )
       )
       => dynamicSize(17)
       [priority(30)]

  rule #maybeDynamicSize(
         dynamicSize(_),
         SPLDataBorrow(_, SPLDataBuffer(
           Aggregate(variantIdx(0),
             ListItem(Integer(_, 64, false))
             ListItem(Float(2.0, 64))
             ListItem(Integer(_, 8, false))
           )
         ))
       )
       => dynamicSize(17)
       [priority(30)]

  rule #maybeDynamicSize(
         dynamicSize(_),
         SPLDataBorrowMut(_, SPLDataBuffer(
           Aggregate(variantIdx(0),
             ListItem(Integer(_, 64, false))
             ListItem(Float(2.0, 64))
             ListItem(Integer(_, 8, false))
           )
         ))
       )
       => dynamicSize(17)
       [priority(30)]
```

## Cheatcode handling
```{.k .symbolic}
  rule [cheatcode-is-spl-account]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(place(LOCAL, PROJS)) .Operands, _DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #setLocalValue(
            place(LOCAL, appendP(PROJS, projectionElemDeref .ProjectionElems)),
            Aggregate(variantIdx(0),
              ListItem(SPLPubkeyRef(Aggregate(variantIdx(0), ListItem(Range(?SplAccountKey:List)))))              // pub key: &'a Pubkey
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
                        ListItem(Aggregate(variantIdx(0), ListItem(Range(?SplMintKey:List))))        // Account.mint: Pubkey
                        ListItem(Aggregate(variantIdx(0), ListItem(Range(?SplTokenOwnerKey:List))))  // Account.owner: Pubkey
                        ListItem(Integer(?SplAmount:Int, 64, false))             // Account.amount: u64
                        // Model COption<Pubkey> as
                        // Some(pubkey); None is not represented here.
                        ListItem(Aggregate(variantIdx(1),
                          ListItem(Aggregate(variantIdx(0), ListItem(Range(?SplDelegateKey:List))))))
                        ListItem(Aggregate(variantIdx(?SplAccountState:Int), .List)) // Account.state: AccountState (repr u8)
                        // Allow COption<u64> with a symbolic variant (0=None, 1=Some(amount)).
                        ListItem(Aggregate(variantIdx(?SplIsNativeLamportsVariant:Int),
                          ListItem(Integer(?SplIsNativeLamports:Int, 64, false))))
                        ListItem(Integer(?SplDelegatedAmount:Int, 64, false))    // Account.delegated_amount: u64
                        // Model COption<Pubkey> as
                        // Some(pubkey); None is not represented here.
                        ListItem(Aggregate(variantIdx(1),
                          ListItem(Aggregate(variantIdx(0), ListItem(Range(?SplCloseAuthKey:List))))))
                    )
                  )
                )
              )
              ListItem(SPLPubkeyRef(Aggregate(variantIdx(0), ListItem(Range(?SplOwnerKey:List)))))               // owner: &'a Pubkey
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
      andBool #isSplPubkey(?SplDelegateKey)
      andBool #isSplPubkey(?SplCloseAuthKey)
      andBool 0 <=Int ?SplAmount andBool ?SplAmount <Int (1 <<Int 64)
      andBool 0 <=Int ?SplAccountState andBool ?SplAccountState <=Int 2
      andBool 0 <=Int ?SplDelegatedAmount andBool ?SplDelegatedAmount <Int (1 <<Int 64)
      andBool 0 <=Int ?SplIsNativeLamportsVariant andBool ?SplIsNativeLamportsVariant <=Int 1
      andBool 0 <=Int ?SplIsNativeLamports andBool ?SplIsNativeLamports <Int (1 <<Int 64)
    [priority(30), preserves-definedness]

  rule [cheatcode-is-spl-mint]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(place(LOCAL, PROJS)) .Operands, _DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #setLocalValue(
            place(LOCAL, appendP(PROJS, projectionElemDeref .ProjectionElems)),
            Aggregate(variantIdx(0),
              ListItem(SPLPubkeyRef(Aggregate(variantIdx(0), ListItem(Range(?SplMintAccountKey:List)))))    // pub key: &'a Pubkey
              ListItem(
                  SPLRefCell(
                    place(
                      LOCAL,
                      appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(1), #hack()) .ProjectionElems)
                    ),
                    Integer(?SplMintLamports:Int, 64, false)
                  )
              )
              ListItem(
                  SPLRefCell(
                    place(
                      LOCAL,
                      appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(2), #hack()) .ProjectionElems)
                    ),
                    SPLDataBuffer(
                      Aggregate(variantIdx(0),
                        // Model COption<Pubkey> as
                        // Some(pubkey); None is not represented here.
                        ListItem(Aggregate(variantIdx(1),
                          ListItem(Aggregate(variantIdx(0), ListItem(Range(?SplMintAuthorityKey:List))))))
                        ListItem(Integer(?SplMintSupply:Int, 64, false))
                        ListItem(Integer(?SplMintDecimals:Int, 8, false))
                        ListItem(BoolVal(false))
                        // Model COption<Pubkey> as
                        // Some(pubkey); None is not represented here.
                        ListItem(Aggregate(variantIdx(1),
                          ListItem(Aggregate(variantIdx(0), ListItem(Range(?SplMintFreezeAuthorityKey:List))))))
                      )
                    )
                  )
              )
              ListItem(SPLPubkeyRef(Aggregate(variantIdx(0), ListItem(Range(?SplMintOwnerKey:List)))))     // owner: &'a Pubkey
              ListItem(Integer(?SplMintRentEpoch:Int, 64, false))
              ListItem(BoolVal(?_SplMintIsSigner:Bool))
              ListItem(BoolVal(?_SplMintIsWritable:Bool))
              ListItem(BoolVal(?_SplMintExecutable:Bool))
            )
         )
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "spl_token::entrypoint::cheatcode_is_spl_mint"
      orBool #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "cheatcode_is_spl_mint"
    ensures #isSplPubkey(?SplMintAccountKey)
      andBool #isSplPubkey(?SplMintOwnerKey)
      andBool #isSplPubkey(?SplMintAuthorityKey)
      andBool #isSplPubkey(?SplMintFreezeAuthorityKey)
      andBool 0 <=Int ?SplMintLamports andBool ?SplMintLamports <Int 18446744073709551616
      andBool 0 <=Int ?SplMintRentEpoch andBool ?SplMintRentEpoch <Int 18446744073709551616
      andBool 0 <=Int ?SplMintSupply andBool ?SplMintSupply <Int (1 <<Int 64)
      andBool 0 <=Int ?SplMintDecimals andBool ?SplMintDecimals <Int 256
    [priority(30), preserves-definedness]

  rule [cheatcode-is-spl-rent]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(place(LOCAL, PROJS)) .Operands, _DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #setLocalValue(
            place(LOCAL, appendP(PROJS, projectionElemDeref .ProjectionElems)),
            Aggregate(variantIdx(0),
              ListItem(SPLPubkeyRef(Aggregate(variantIdx(0), ListItem(Range(?SplRentAccountKey:List))))) // pub key: &'a Pubkey
              ListItem(
                  SPLRefCell(
                    place(
                      LOCAL,
                      appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(1), #hack()) .ProjectionElems)
                    ),
                    Integer(?SplRentLamports:Int, 64, false)
                  )
              ) // lamports: Rc<RefCell<&'a mut u64>>
              ListItem( // data: Rc<RefCell<&'a mut [u8]>>
                  SPLRefCell(
                    place(
                      LOCAL,
                      appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(2), #hack()) .ProjectionElems)
                    ),
                    SPLDataBuffer(
                      Aggregate(variantIdx(0),
                        ListItem(Integer(?SplRentLamportsPerByteYear:Int, 64, false))
                        ListItem(Float(2.0, 64))
                        ListItem(Integer(?SplRentBurnPercent:Int, 8, false))
                      )
                    )
                  )
                )
              ListItem(SPLPubkeyRef(Aggregate(variantIdx(0), ListItem(Range(?SplRentOwnerKey:List))))) // owner: &'a Pubkey
              ListItem(Integer(?SplRentRentEpoch:Int, 64, false))              // rent_epoch: u64
              ListItem(BoolVal(false))                                          // is_signer: bool
              ListItem(BoolVal(false))                                          // is_writable: bool
              ListItem(BoolVal(false))                                          // executable: bool
            )
         )
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "spl_token::entrypoint::cheatcode_is_spl_rent"
      orBool #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "cheatcode_is_spl_rent"
    ensures #isSplPubkey(?SplRentAccountKey)
      andBool #isSplPubkey(?SplRentOwnerKey)
      andBool 0 <=Int ?SplRentLamports andBool ?SplRentLamports <Int 18446744073709551616
      andBool 0 <=Int ?SplRentRentEpoch andBool ?SplRentRentEpoch <Int 18446744073709551616
      andBool 0 <=Int ?SplRentLamportsPerByteYear andBool ?SplRentLamportsPerByteYear <Int (1 <<Int 32)
      andBool 0 <=Int ?SplRentBurnPercent andBool ?SplRentBurnPercent <=Int 100
    [priority(30), preserves-definedness]
```

## Accessing `Rc<RefCell<_>>`

We shortcut the MIR field access that `<Rc<_> as Deref>::deref` performs and
expose the wrapped payload directly.

```k
  rule [spl-rc-deref]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, OP:Operand .Operands, DEST, TARGET, _UNWIND), _SPAN))
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

## Pubkey references

```k
  syntax Context ::= "CtxSPLPubkeyRef"

  rule <k> #traverseProjection(
             DEST,
             SPLPubkeyRef(VAL),
             projectionElemDeref PROJS,
             CTXTS
           )
        => #traverseProjection(
             DEST,
             VAL,
             PROJS,
             CtxSPLPubkeyRef CTXTS
           )
        ...
       </k>
    [priority(30)]
  rule #buildUpdate(VAL, CtxSPLPubkeyRef CTXS) => #buildUpdate(SPLPubkeyRef(VAL), CTXS)
  rule #projectionsFor(CtxSPLPubkeyRef CTXS, PROJS) => #projectionsFor(CTXS, projectionElemDeref PROJS)
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

## `Ref`/`RefMut` deref shortcuts

```k
  rule [spl-ref-deref]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, ARG_OP:Operand .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
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
    requires #isSPLUnpackFunc(#functionName(lookupFunction(#tyOfCall(FUNC))))
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
    requires #isSPLPackFunc(#functionName(lookupFunction(#tyOfCall(FUNC))))
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

```{.k .symbolic}
  // Rent::from_account_info
  rule [spl-rent-from-account-info]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, OP .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkSPLRentFromAccountInfo(DEST, OP)
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #isSPLRentFromAccountInfoFunc(#functionName(lookupFunction(#tyOfCall(FUNC))))
    [priority(30), preserves-definedness]

  syntax KItem ::= #mkSPLRentFromAccountInfo ( Place , Evaluation ) [seqstrict(2)]


  // Accept references without an explicit deref projection (e.g., borrowed AccountInfo locals on the stack)
  rule <k> #mkSPLRentFromAccountInfo(DEST, Reference(0, place(local(I), .ProjectionElems), _, _))
        => #mkSPLRentFromAccountInfo(DEST, getValue(LOCALS, I))
       ...
      </k>
      <locals> LOCALS </locals>
    requires 0 <=Int I
     andBool I <Int size(LOCALS)
     andBool isTypedValue(LOCALS[I])

  rule <k> #mkSPLRentFromAccountInfo(DEST, Reference(OFFSET, place(local(I), .ProjectionElems), _, _))
        => #mkSPLRentFromAccountInfo(
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

  rule <k> #mkSPLRentFromAccountInfo(
            DEST,
            Aggregate(variantIdx(0),
              ListItem(_KEY)
              ListItem(_LAMPORTS_CELL)
              ListItem(SPLRefCell(_, SPLDataBuffer(RENT_DATA)))
              _REST:List
            )
           )
        => #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(RENT_DATA)))
       ...
      </k>
```

```{.k .symbolic}
  // Rent::get (stable value, stored once in outermost frame like p-token SysRent)
  rule [spl-rent-get]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #writeSPLSysRent(DEST)
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #isSPLRentGetFunc(#functionName(lookupFunction(#tyOfCall(FUNC))))
    [priority(30), preserves-definedness]

  syntax KItem ::= #writeSPLSysRent ( Place )

  // reuse existing Rent value if already initialised in outermost frame
  rule <k> #writeSPLSysRent(DEST) => #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(RENTVAL))) ... </k>
       <stack>
          STACK:List
          ListItem(StackFrame(_, _, _, _, ListItem(typedValue(RENTVAL, _, _)) _REST))
       </stack>
    requires 0 <Int size(STACK)
    [preserves-definedness]

  rule <k> #writeSPLSysRent(DEST) => #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(RENTVAL))) ... </k>
       <stack>
          ListItem(StackFrame(_, _, _, _, ListItem(typedValue(RENTVAL, _, _)) _REST))
       </stack>
    [preserves-definedness]

  // first access: create SysRent in outermost frame's return slot (local 0)
  rule [mk-spl-sys-rent]:
      <k> #writeSPLSysRent(_DEST) ~> _CONT </k>
      <stack>
        _:List
        ListItem(StackFrame(_, _, _, _,
          ListItem(newLocal(_, _) =>
            typedValue(
              Aggregate(variantIdx(0),
                ListItem(Integer(?SplSysRentLamportsPerByteYear:Int, 64, false))
                ListItem(Float(2.0, 64))
                ListItem(Integer(?SplSysRentBurnPercent:Int, 8, false))
              ),
              ty(0),
              mutabilityNot
            )
          ) _:List
        ))
      </stack>
    ensures 0 <=Int ?SplSysRentLamportsPerByteYear
      andBool ?SplSysRentLamportsPerByteYear <Int (1 <<Int 32)
      andBool 0 <=Int ?SplSysRentBurnPercent
      andBool ?SplSysRentBurnPercent <=Int 100
    [preserves-definedness]
```

## Pubkey comparison shortcut
```k
  rule [spl-cmp-pubkeys]:
    <k> #execTerminator(
          terminator(
            terminatorKindCall(FUNC, ARG1:Operand ARG2:Operand .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND),
            _SPAN
          )
        )
      => #execSPLCmpPubkeys( DEST, #withDeref(ARG1), #withDeref(ARG2))
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "spl_token::processor::Processor::cmp_pubkeys"
    [priority(30), preserves-definedness]

  syntax KItem ::= #execSPLCmpPubkeys( Place , Evaluation , Evaluation ) [seqstrict(2,3)]
  rule <k> #execSPLCmpPubkeys(DEST, Aggregate(variantIdx(0), ListItem(Range(KEY1))), Aggregate(variantIdx(0), ListItem(Range(KEY2))))
        => #setLocalValue(DEST, BoolVal(KEY1 ==K KEY2))
       ... </k>
    [preserves-definedness]
```

```k
endmodule
```
