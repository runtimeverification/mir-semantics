```k
requires "../kmir-ast.md"
requires "../rt/data.md"
requires "../kmir.md"
requires "../rt/configuration.md"
```

This module extends the `KMIR-P-TOKEN` semantics so that existing Pinocchio-specific
data modelling rules can be reused for the SPL Token runtime verification harness.
It maps the SPL cheatcodes (and the helper entry points they rely on) onto the
same symbolic constructors used by `p-token.md`.

```k
module KMIR-SPL-TOKEN
  imports KMIR-P-TOKEN
```

## Cheatcode aliases

```k
  rule [cheatcode-is-spl-account]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(PLACE) .Operands, _DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkPTokenAccount(PLACE) ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "spl_token::entrypoint::cheatcode_is_spl_account"
    [priority(30), preserves-definedness]

  rule [cheatcode-is-spl-mint]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(PLACE) .Operands, _DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkPTokenMint(PLACE) ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "spl_token::entrypoint::cheatcode_is_spl_mint"
    [priority(30), preserves-definedness]

  rule [cheatcode-is-spl-rent]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(PLACE) .Operands, _DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkPTokenRent(PLACE) ~> #execBlockIdx(TARGET)
    ...
    </k>
    requires #functionName(lookupFunction(#tyOfCall(FUNC))) ==String "spl_token::entrypoint::cheatcode_is_spl_rent"
    [priority(30), preserves-definedness]
```

## Account data helpers

The SPL harness uses `spl_token::state::{Account,Mint,Multisig}` `Pack` helpers
instead of Pinocchio's `Transmutable` APIs.  These rules redirect the calls to
the existing symbolic constructors so that previously defined projections and
updates keep working without duplication.

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

## Borrow helpers

Pinocchio uses bespoke `borrow_*_unchecked` helpers; the SPL harness implements
borrows via `RefCell`.  The following aliases keep the symbolic `PAccByteRef`
representation consistent by mapping the standard library calls to the existing
constructor.

```k
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
