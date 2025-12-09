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
Account::unpack_from_slice(&acc.data.borrow())
Account::pack_into_slice(&a, &mut acc.data.borrow_mut())
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

  syntax Place ::= placeOf ( Operand ) [function]
  rule placeOf(operandCopy(P)) => P
  rule placeOf(operandMove(P)) => P

  syntax Operand ::= #appendProjsOp ( Operand , ProjectionElems ) [function]
  rule #appendProjsOp(operandCopy(place(L, PROJS)), EXTRA) => operandCopy(place(L, appendP(PROJS, EXTRA)))
  rule #appendProjsOp(operandMove(place(L, PROJS)), EXTRA) => operandMove(place(L, appendP(PROJS, EXTRA)))
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
  rule #isSPLUnpackFunc("<state::Account as solana_program_pack::Pack>::unpack_from_slice") => true
  rule #isSPLUnpackFunc("Account::unpack_from_slice") => true
  // spl-token mint
  rule #isSPLUnpackFunc("<state::Mint as solana_program_pack::Pack>::unpack_from_slice") => true
  rule #isSPLUnpackFunc("Mint::unpack_from_slice") => true

  syntax Bool ::= #isSPLPackFunc   ( String ) [function, total]
  rule #isSPLPackFunc(_) => false [owise]
  // spl-token account
  rule #isSPLPackFunc("<state::Account as solana_program_pack::Pack>::pack_into_slice") => true
  rule #isSPLPackFunc("Account::pack_into_slice") => true
  // spl-token mint
  rule #isSPLPackFunc("<state::Mint as solana_program_pack::Pack>::pack_into_slice") => true
  rule #isSPLPackFunc("Mint::pack_into_slice") => true

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
      => #forceSetPlaceValue(
           place(LOCAL, appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(2), #hack()) projectionElemField(fieldIdx(0), #hack()) projectionElemField(fieldIdx(0), #hack()) projectionElemDeref projectionElemField(fieldIdx(2), #hack()) projectionElemField(fieldIdx(1), #hack()) projectionElemField(fieldIdx(0), #hack()) projectionElemDeref .ProjectionElems)),
           SPLDataBuffer(
             Aggregate(variantIdx(0),
               ListItem(Aggregate(variantIdx(0), ListItem(Range(?SplMintKey:List))))        // Account.mint: Pubkey
               ListItem(Aggregate(variantIdx(0), ListItem(Range(?SplTokenOwnerKey:List))))  // Account.owner: Pubkey
               ListItem(Integer(?SplAmount:Int, 64, false))                                 // Account.amount: u64
               ListItem(Aggregate(variantIdx(1),                                            // delegate COption<Pubkey>
                 ListItem(Aggregate(variantIdx(0), ListItem(Range(?SplDelegateKey:List))))))
               ListItem(Aggregate(variantIdx(?SplAccountState:Int), .List))                 // Account.state: AccountState
               ListItem(Aggregate(variantIdx(?SplIsNativeLamportsVariant:Int),              // is_native COption<u64>
                 ListItem(Integer(?SplIsNativeLamports:Int, 64, false))))
               ListItem(Integer(?SplDelegatedAmount:Int, 64, false))                        // Account.delegated_amount: u64
               ListItem(Aggregate(variantIdx(1),                                            // close_authority COption<Pubkey>
                 ListItem(Aggregate(variantIdx(0), ListItem(Range(?SplCloseAuthKey:List))))))
             )
           )
         )
      ~> #forceSetPlaceValue(
         place(LOCAL, appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(2), #hack()) projectionElemField(fieldIdx(0), #hack()) projectionElemField(fieldIdx(0), #hack()) projectionElemDeref .ProjectionElems)),
        #initBorrow(operandCopy(place(LOCAL, appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(2), #hack()) projectionElemField(fieldIdx(0), #hack()) projectionElemField(fieldIdx(0), #hack()) projectionElemDeref .ProjectionElems))), 165)
     )    
      ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "spl_token::entrypoint::cheatcode_is_spl_account"
      orBool #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "cheatcode_is_spl_account"
    ensures #isSplPubkey(?SplMintKey)
      andBool #isSplPubkey(?SplTokenOwnerKey)
      andBool #isSplPubkey(?SplDelegateKey)
      andBool #isSplPubkey(?SplCloseAuthKey)
      andBool 0 <=Int ?SplAmount andBool ?SplAmount <Int (1 <<Int 64)
      andBool 0 <=Int ?SplAccountState andBool ?SplAccountState <=Int 2
      andBool 0 <=Int ?SplDelegatedAmount andBool ?SplDelegatedAmount <Int (1 <<Int 64)
      andBool 0 <=Int ?SplIsNativeLamportsVariant andBool ?SplIsNativeLamportsVariant <=Int 1
      andBool 0 <=Int ?SplIsNativeLamports andBool ?SplIsNativeLamports <Int (1 <<Int 64)
    [priority(30), preserves-definedness]

  syntax Evaluation ::= #initBorrow(Evaluation, Int) [seqstrict(1)]
  rule <k> #initBorrow(Aggregate ( variantIdx ( 0 ) ,
                    ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Integer ( _ , 64 , false ))))))
                    ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Integer ( _ , 64 , false ))))))
                    ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Integer ( _ , 64 , true ))))))
                    ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Reference ( OFFSET , PLACE , MUT , metadata ( dynamicSize ( _ ) , 0 , dynamicSize ( _ ))))))))
             ), N)
          => Aggregate ( variantIdx ( 0 ) ,
                    ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Integer ( 0 , 64 , false ))))))
                    ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Integer ( 0 , 64 , false ))))))
                    ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Integer ( 0 , 64 , true ))))))
                    ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Reference ( OFFSET , PLACE , MUT , metadata ( dynamicSize ( N ) , 0 , dynamicSize ( N ))))))))
             ) ...
      </k>

  rule <k> #traverseProjection(DEST, SPLDataBuffer(VAL), .ProjectionElems, CTXTS) ~> #derefTruncate(dynamicSize (_), PROJS)
        => #traverseProjection(DEST, SPLDataBuffer(VAL), PROJS, CTXTS) ...
       </k>

  rule [cheatcode-is-spl-mint]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(place(LOCAL, PROJS)) .Operands, _DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #forceSetPlaceValue(
           place(LOCAL, appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(2), #hack()) projectionElemField(fieldIdx(0), #hack()) projectionElemField(fieldIdx(0), #hack()) projectionElemDeref projectionElemField(fieldIdx(2), #hack()) projectionElemField(fieldIdx(1), #hack()) projectionElemField(fieldIdx(0), #hack()) projectionElemDeref .ProjectionElems)),
           SPLDataBuffer(
             Aggregate(variantIdx(0),
               // optional key. The model always carries a payload key (never to be read if None)
               ListItem(Aggregate(variantIdx(?SplMintHasAuthKey:Int),                                 // mint_authority COption<Pubkey>
                 ListItem(Aggregate(variantIdx(0), ListItem(Range(?SplMintAuthorityKey:List))))))
               ListItem(Integer(?SplMintSupply:Int, 64, false))                                       // supply: u64
               ListItem(Integer(?SplMintDecimals:Int, 8, false))                                      // decimals: u8
               ListItem(BoolVal(?_SplMintInitialised:Bool))                                           // is_initialized: bool
               // optional key. The model always carries a payload key (never to be read if None)
               ListItem(Aggregate(variantIdx(?SplMintHasFreezeKey:Int),                               // freeze_authority COption<Pubkey>
                 ListItem(Aggregate(variantIdx(0), ListItem(Range(?SplMintFreezeAuthorityKey:List))))))
             )
           )
         )
      ~> #forceSetPlaceValue(
         place(LOCAL, appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(2), #hack()) projectionElemField(fieldIdx(0), #hack()) projectionElemField(fieldIdx(0), #hack()) projectionElemDeref .ProjectionElems)),
        #initBorrow(operandCopy(place(LOCAL, appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(2), #hack()) projectionElemField(fieldIdx(0), #hack()) projectionElemField(fieldIdx(0), #hack()) projectionElemDeref .ProjectionElems))), 82)
     )
      ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "spl_token::entrypoint::cheatcode_is_spl_mint"
      orBool #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "cheatcode_is_spl_mint"
    ensures 0 <=Int ?SplMintHasAuthKey andBool ?SplMintHasAuthKey <=Int 1
      andBool #isSplPubkey(?SplMintAuthorityKey)
      andBool 0 <=Int ?SplMintHasFreezeKey andBool ?SplMintHasFreezeKey <=Int 1
      andBool #isSplPubkey(?SplMintFreezeAuthorityKey)
      andBool 0 <=Int ?SplMintSupply andBool ?SplMintSupply <Int (1 <<Int 64)
      andBool 0 <=Int ?SplMintDecimals andBool ?SplMintDecimals <Int 256
    [priority(30), preserves-definedness]

  rule [cheatcode-is-spl-rent]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(place(LOCAL, PROJS)) .Operands, _DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #forceSetPlaceValue(
           place(LOCAL, appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(2), #hack()) projectionElemField(fieldIdx(0), #hack()) projectionElemField(fieldIdx(0), #hack()) projectionElemDeref projectionElemField(fieldIdx(2), #hack()) projectionElemField(fieldIdx(1), #hack()) projectionElemField(fieldIdx(0), #hack()) projectionElemDeref .ProjectionElems)),
           SPLDataBuffer(
             Aggregate(variantIdx(0),
               ListItem(Integer(?SplRentLamportsPerByteYear:Int, 64, false))                          // lamports_per_byte_year: u64
               ListItem(Float(2.0, 64))                                                               // exemption_threshold: f64
               ListItem(Integer(?SplRentBurnPercent:Int, 8, false))                                   // burn_percent: u8
             )
           )
         )
      ~> #forceSetPlaceValue(
         place(LOCAL, appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(2), #hack()) projectionElemField(fieldIdx(0), #hack()) projectionElemField(fieldIdx(0), #hack()) projectionElemDeref .ProjectionElems)),
        #initBorrow(operandCopy(place(LOCAL, appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(2), #hack()) projectionElemField(fieldIdx(0), #hack()) projectionElemField(fieldIdx(0), #hack()) projectionElemDeref .ProjectionElems))), 17)
     )
      ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "spl_token::entrypoint::cheatcode_is_spl_rent"
      orBool #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "cheatcode_is_spl_rent"
    ensures 0 <=Int ?SplRentLamportsPerByteYear andBool ?SplRentLamportsPerByteYear <Int (1 <<Int 32)
      andBool 0 <=Int ?SplRentBurnPercent andBool ?SplRentBurnPercent <=Int 100
    [priority(30), preserves-definedness]
```

## RefCell::<&mut [u8]> helpers

```k
  rule [spl-borrow-data]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(place(LOCAL, PROJS)) .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #setSPLBorrowData(DEST, operandCopy(place(LOCAL, PROJS)))
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #isSPLBorrowFunc(#functionName(lookupFunction(#tyOfCall(FUNC))))
    [priority(30), preserves-definedness]

  syntax KItem ::= #setSPLBorrowData ( Place , Evaluation ) [seqstrict(2)]
  rule <k> #setSPLBorrowData(DEST, Reference(OFFSET, place(LOCAL, PROJS), MUT, META))
        => #setLocalValue(DEST, Aggregate(variantIdx(0),
             ListItem(Aggregate(variantIdx(0), ListItem(PtrLocal(OFFSET, place(LOCAL, appendP(PROJS, projectionElemField(fieldIdx(1), #hack())  projectionElemField(fieldIdx(0), #hack()) .ProjectionElems)), MUT, META))))
             ListItem(Aggregate(variantIdx(0), ListItem(Reference(OFFSET, place (LOCAL, appendP(PROJS, projectionElemField(fieldIdx(0), #hack()) .ProjectionElems)), MUT, META)))))) ...
       </k>
```

## Account::unpack_from_slice / Account::pack_into_slice
```k
  rule [spl-account-unpack]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, OP:Operand .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #splUnpack(DEST, #withDeref(OP))
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #isSPLUnpackFunc(#functionName(lookupFunction(#tyOfCall(FUNC))))
    [priority(30), preserves-definedness]

  syntax KItem ::= #splUnpack ( Place , Evaluation ) [seqstrict(2)]
  rule <k> #splUnpack(DEST, SPLDataBuffer(VAL))
        => #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(VAL))) ...
       </k>

  rule [spl-account-pack]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, SRC:Operand DST:Operand .Operands, _DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #splPack(SRC, #withDeref(DST)) ~> #execBlockIdx(TARGET) ...
    </k>
    requires #isSPLPackFunc(#functionName(lookupFunction(#tyOfCall(FUNC))))
    [priority(30), preserves-definedness]

  syntax KItem ::= #splPack ( Evaluation , Evaluation ) [seqstrict(1)]
  rule <k> #splPack(VAL, DEST) => #setLocalValue(placeOf(DEST), SPLDataBuffer(VAL)) ... </k>
```

```{.k .symbolic}
  // Rent::from_account_info - navigate to data buffer using projection path from cheatcode
  rule [spl-rent-from-account-info]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, OP:Operand .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #splUnpack(DEST, #appendProjsOp(OP, projectionElemDeref projectionElemField(fieldIdx(2), #hack()) projectionElemField(fieldIdx(0), #hack()) projectionElemField(fieldIdx(0), #hack()) projectionElemDeref projectionElemField(fieldIdx(2), #hack()) projectionElemField(fieldIdx(1), #hack()) projectionElemField(fieldIdx(0), #hack()) projectionElemDeref .ProjectionElems))
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #isSPLRentFromAccountInfoFunc(#functionName(lookupFunction(#tyOfCall(FUNC))))
    [priority(30), preserves-definedness]
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
