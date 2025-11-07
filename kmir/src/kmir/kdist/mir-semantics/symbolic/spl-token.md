```k
requires "../kmir-ast.md"
requires "../rt/data.md"
requires "../kmir.md"
requires "../rt/configuration.md"
```

This module now provides a standalone SPL Token modelling path instead of
reusing the Pinocchio helper pipeline.  For determinism we rebuild the domain
data that `cheatcode_is_spl_account` needs directly inside this module (other
cheatcodes will be ported later).

```k
module KMIR-SPL-TOKEN
  imports KMIR-P-TOKEN
```

## Cheatcode handling

```k
  rule [cheatcode-is-spl-account]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(PLACE) .Operands, _DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkSPLTokenAccount(PLACE) ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "spl_token::entrypoint::cheatcode_is_spl_account"
    [priority(30), preserves-definedness]
```

## SPL account constructor

We mirror the `p-token.md` modelling strategy but construct the symbolic account
value locally.  This avoids the `#addAccount` detour that attempted to reuse the
Pinocchio helpers via synthetic aggregates.

```k
  syntax KItem ::= #mkSPLTokenAccount ( Place )

  rule
    <k> #mkSPLTokenAccount(place(LOCAL, PROJS))
      => #setLocalValue(
            place(LOCAL, appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(0), #hack()) projectionElemDeref .ProjectionElems)),
            #mkSPLAccountValue()
         )
    ...
    </k>
```
```k
  syntax Value ::= #mkSPLAccountValue ( )
```

```{.k .symbolic}
  rule #mkSPLAccountValue()
      => PAccountAccount(
           PAcc(
             U8(?SplBorrowState:Int),
             U8(?SplIsSigner:Int),
             U8(?SplIsWritable:Int),
             U8(?SplExecutable:Int),
             I32(?SplResizeDelta:Int),
             Key(?SplAccountKey:List),
             Key(?SplOwnerKey:List),
             U64(?SplLamports:Int),
             U64(165) // size_of(Account)
           ),
           IAcc(
             Key(?SplMintKey:List),
             Key(?SplTokenOwner:List),
             Amount(?SplAmount:Int),
             Flag(?SplDelegateFlag:Int),
             Key(?SplDelegateKey:List),
             U8(?SplAccountState:Int),
             Flag(?SplNativeFlag:Int),
             Amount(?SplNativeAmount:Int),
             Amount(?SplDelegateAmount:Int),
             Flag(?SplCloseFlag:Int),
             Key(?SplCloseAuthorityKey:List)
           )
         )
    ensures 0 <=Int ?SplBorrowState andBool ?SplBorrowState <Int 256
      andBool 0 <=Int ?SplIsSigner andBool ?SplIsSigner <Int 256
      andBool 0 <=Int ?SplIsWritable andBool ?SplIsWritable <Int 256
      andBool 0 <=Int ?SplExecutable andBool ?SplExecutable <Int 256
      andBool -2147483648 <=Int ?SplResizeDelta andBool ?SplResizeDelta <=Int 2147483647
      andBool size(?SplAccountKey) ==Int 32 andBool allBytes(?SplAccountKey)
      andBool size(?SplOwnerKey) ==Int 32 andBool allBytes(?SplOwnerKey)
      andBool 0 <=Int ?SplLamports andBool ?SplLamports <Int 18446744073709551616
      andBool size(?SplMintKey) ==Int 32 andBool allBytes(?SplMintKey)
      andBool size(?SplTokenOwner) ==Int 32 andBool allBytes(?SplTokenOwner)
      andBool size(?SplDelegateKey) ==Int 32 andBool allBytes(?SplDelegateKey)
      andBool size(?SplCloseAuthorityKey) ==Int 32 andBool allBytes(?SplCloseAuthorityKey)
      andBool 0 <=Int ?SplAmount andBool ?SplAmount <Int (1 <<Int 64)
      andBool 0 <=Int ?SplNativeAmount andBool ?SplNativeAmount <Int (1 <<Int 64)
      andBool 0 <=Int ?SplDelegateAmount andBool ?SplDelegateAmount <Int (1 <<Int 64)
      andBool 0 <=Int ?SplDelegateFlag andBool ?SplDelegateFlag <=Int 1
      andBool 0 <=Int ?SplNativeFlag andBool ?SplNativeFlag <=Int 1
      andBool 0 <=Int ?SplCloseFlag andBool ?SplCloseFlag <=Int 1
      andBool 0 <=Int ?SplAccountState andBool ?SplAccountState <Int 256
```

## Pack/borrow helpers

The remaining helpers still map SPL harness calls onto the Pinocchio
representations so the downstream projections keep working.

```k
  // Account::unpack* wrappers -------------------------------------------------

  rule [spl-pack-account-result]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, OPERAND .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkPAccountRef(DEST, OPERAND, PAccountIAcc, true)
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires (
        #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "spl_token::state::Account::unpack_unchecked"
      orBool
        #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "spl_token::state::Account::unpack"
    )
    [priority(30), preserves-definedness]

  // Mint::unpack* wrappers ----------------------------------------------------

  rule [spl-pack-mint-result]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, OPERAND .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkPAccountRef(DEST, OPERAND, PAccountIMint, true)
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires (
        #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "spl_token::state::Mint::unpack_unchecked"
      orBool
        #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "spl_token::state::Mint::unpack"
    )
    [priority(30), preserves-definedness]

  // Rent::from_account_info ---------------------------------------------------

  rule [spl-rent-from-account-info]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, OPERAND .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkPAccountRef(DEST, OPERAND, PAccountPRent, false)
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "solana_rent::Rent::from_account_info"
    [priority(30), preserves-definedness]
```

```k
  // RefCell::<&mut [u8]> borrow helpers ---------------------------------------

  rule [spl-borrow-data]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(place(LOCAL, PROJS)) .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkPAccByteRef(DEST, operandCopy(place(LOCAL, appendP(PROJS, projectionElemField(fieldIdx(2), #hack()) projectionElemDeref .ProjectionElems))), mutabilityNot)
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "core::cell::RefCell::<&mut [u8]>::borrow"
    [priority(30), preserves-definedness]

  rule [spl-borrow-mut-data]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(place(LOCAL, PROJS)) .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkPAccByteRef(DEST, operandCopy(place(LOCAL, appendP(PROJS, projectionElemField(fieldIdx(2), #hack()) projectionElemDeref .ProjectionElems))), mutabilityMut)
         ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "core::cell::RefCell::<&mut [u8]>::borrow_mut"
    [priority(30), preserves-definedness]
```

```k
endmodule
```
