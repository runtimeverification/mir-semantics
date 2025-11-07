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
  syntax Value ::= SPLRefCellData ( Value )
                 | SPLRefCellLamports ( U64 )
                 | SPLDataBuffer ( Value )
                 | SPLDataBorrow ( Place , Value )
                 | SPLDataBorrowMut ( Place , Value )

  syntax Value ::= #mkSPLAccountInfo ( )
                 | #mkSPLAccountPayload ( )
```

## Cheatcode handling

```k
  rule [cheatcode-is-spl-account]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(PLACE) .Operands, _DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkSPLTokenAccount(PLACE) ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "spl_token::entrypoint::cheatcode_is_spl_account"
      orBool #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "spl_token_domain_data::cheatcode_is_spl_account" 
    [priority(30), preserves-definedness]

  syntax KItem ::= #mkSPLTokenAccount ( Place )

  rule
    <k> #mkSPLTokenAccount(place(LOCAL, PROJS))
      => #setLocalValue(
            place(LOCAL, appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(0), #hack()) projectionElemDeref .ProjectionElems)),
            #mkSPLAccountInfo()
         )
    ...
    </k>
```

## AccountInfo construction

The following helpers use the exact field order from `solana_account_info::AccountInfo`
and `spl_token::state::Account`, so that MIR projections match the real SPL structures: 
key/lamports/data/owner/rent_epoch/is_signer/is_writable/executable for `AccountInfo`, 
and the eight-account fields described in the SPL Pack implementation.
```{.k .symbolic}
  rule #mkSPLAccountInfo()
      => Aggregate(variantIdx(0),
           ListItem(Range(?SplAccountKey:List))
           ListItem(SPLRefCellLamports(U64(?SplLamports:Int)))
           ListItem(SPLRefCellData(SPLDataBuffer(#mkSPLAccountPayload())))
           ListItem(Range(?SplOwnerKey))
           ListItem(Integer(?SplRentEpoch:Int, 64, false))
           ListItem(BoolVal(?_SplIsSigner:Bool))
           ListItem(BoolVal(?_SplIsWritable:Bool))
           ListItem(BoolVal(?_SplExecutable:Bool))
         )
    ensures size(?SplAccountKey) ==Int 32 andBool allBytes(?SplAccountKey)
      andBool size(?SplOwnerKey) ==Int 32 andBool allBytes(?SplOwnerKey)
      andBool 0 <=Int ?SplLamports andBool ?SplLamports <Int 18446744073709551616
      andBool 0 <=Int ?SplRentEpoch andBool ?SplRentEpoch <Int 18446744073709551616
```

```{.k .symbolic}
  rule #mkSPLAccountPayload()
      => Aggregate(variantIdx(0),
           ListItem(Range(?SplMintKey:List))
           ListItem(Range(?SplTokenOwnerKey:List))
           ListItem(Integer(?SplAmount:Int, 64, false))
           ListItem(?SplDelegateCOpt:Value)
           ListItem(Integer(?SplAccountState:Int, 8, false))
           ListItem(?SplIsNativeCOpt:Value)
           ListItem(Integer(?SplDelegatedAmount:Int, 64, false))
           ListItem(?SplCloseAuthCOpt:Value)
         )
    ensures size(?SplMintKey) ==Int 32 andBool allBytes(?SplMintKey)
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
```

## RefCell::<&mut [u8]> helpers

```k
  rule [spl-borrow-data]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(place(LOCAL, PROJS)) .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkSPLBorrowData(DEST, operandCopy(place(LOCAL, PROJS)), place(LOCAL, PROJS), false)
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "core::cell::RefCell::<&mut [u8]>::borrow"
    [priority(30), preserves-definedness]

  rule [spl-borrow-mut-data]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(place(LOCAL, PROJS)) .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkSPLBorrowData(DEST, operandCopy(place(LOCAL, PROJS)), place(LOCAL, PROJS), true)
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "core::cell::RefCell::<&mut [u8]>::borrow_mut"
    [priority(30), preserves-definedness]

  syntax KItem ::= #mkSPLBorrowData ( Place , Evaluation , Place , Bool ) [seqstrict(2)]

  rule <k> #mkSPLBorrowData(DEST, SPLRefCellData(BUF), SRC, false)
        => #setLocalValue(DEST, SPLDataBorrow(SRC, BUF))
        ...
       </k>

  rule <k> #mkSPLBorrowData(DEST, SPLRefCellData(BUF), SRC, true)
        => #setLocalValue(DEST, SPLDataBorrowMut(SRC, BUF))
        ...
       </k>
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
        #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "spl_token_domain_data::Account::unpack_unchecked"
    )
    [priority(30), preserves-definedness]

  syntax KItem ::= #mkSPLAccountUnpack ( Place , Evaluation ) [seqstrict(2)]

  rule <k> #mkSPLAccountUnpack(DEST, SPLDataBorrow(_, SPLDataBuffer(ACCOUNT)))
        => #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(ACCOUNT)))
        ...
       </k>

  rule <k> #mkSPLAccountUnpack(DEST, SPLDataBorrowMut(_, SPLDataBuffer(ACCOUNT)))
        => #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(ACCOUNT)))
        ...
       </k>

  rule [spl-account-pack]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(SRC) operandCopy(BUF) .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkSPLAccountPack(operandCopy(SRC), operandCopy(BUF), DEST)
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires (
        #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "spl_token::state::Account::pack"
      orBool
        #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "spl_token_domain_data::Account::pack"
    )
    [priority(30), preserves-definedness]

  syntax KItem ::= #mkSPLAccountPack ( Evaluation , Evaluation , Place ) [seqstrict(2)]

  rule <k> #mkSPLAccountPack(ACCOUNT, SPLDataBorrowMut(PLACE, SPLDataBuffer(_)), DEST)
        => #setLocalValue(
             PLACE,
             SPLRefCellData(SPLDataBuffer(ACCOUNT))
           )
         ~> #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(Aggregate(variantIdx(0), .List))))
        ...
       </k>
```

```k
endmodule
```
