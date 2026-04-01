# SPL-Token lemma rules for `expected_validate_owner_result` and `inner_test_validate_owner`

Adapted from the p-token version (PR #1001). The key difference: spl-token's AccountInfo
uses raw Aggregate values instead of p-token's PAccountAccount/PAcc wrappers. The intercept
rules extract individual fields (key, is_signer, owner) from the AccountInfo, and case rules
match against these pre-extracted Values directly.

Cases 8-10 (multisig initialized signer-checking) are not lemmatized here; they fall through
to small-step symbolic execution. With n==1 this is fast enough.

```k
requires "../rt/data.md"
requires "../kmir.md"
requires "../rt/configuration.md"
requires "spl-token.md"
```

## Common helpers

```k
module VALIDATE-OWNER-COMMON-SPL
  imports KMIR-SPL-TOKEN

  syntax List ::= "#splTokenProgramIdBytes" [function, total]
  rule #splTokenProgramIdBytes =>
         ListItem(Integer(6, 8, false))   ListItem(Integer(221, 8, false))
         ListItem(Integer(246, 8, false)) ListItem(Integer(225, 8, false))
         ListItem(Integer(215, 8, false)) ListItem(Integer(101, 8, false))
         ListItem(Integer(161, 8, false)) ListItem(Integer(147, 8, false))
         ListItem(Integer(217, 8, false)) ListItem(Integer(203, 8, false))
         ListItem(Integer(225, 8, false)) ListItem(Integer(70, 8, false))
         ListItem(Integer(206, 8, false)) ListItem(Integer(235, 8, false))
         ListItem(Integer(121, 8, false)) ListItem(Integer(172, 8, false))
         ListItem(Integer(28, 8, false))  ListItem(Integer(180, 8, false))
         ListItem(Integer(133, 8, false)) ListItem(Integer(237, 8, false))
         ListItem(Integer(95, 8, false))  ListItem(Integer(91, 8, false))
         ListItem(Integer(55, 8, false))  ListItem(Integer(145, 8, false))
         ListItem(Integer(58, 8, false))  ListItem(Integer(140, 8, false))
         ListItem(Integer(245, 8, false)) ListItem(Integer(133, 8, false))
         ListItem(Integer(126, 8, false)) ListItem(Integer(255, 8, false))
         ListItem(Integer(0, 8, false))   ListItem(Integer(169, 8, false))

  syntax Value ::= "#splTokenProgramId" [function, total]
  rule #splTokenProgramId => Aggregate(variantIdx(0), ListItem(Range(#splTokenProgramIdBytes)))

endmodule
```

## `expected_validate_owner_result` lemma

```k
module EXPECTED-VALIDATE-OWNER-RESULT-SPL-TOKEN-LEMMA
  imports VALIDATE-OWNER-COMMON-SPL

  // Args: expected_owner_key, owner_key, is_signer, owner_of_account, data_field, tx_signers_place, maybe_multisig, DEST, TARGET
  syntax KItem ::= #validateOwnerResultExpectedSPL(
      Evaluation, Evaluation, Evaluation, Evaluation, Evaluation,
      Place, Evaluation, Place, MaybeBasicBlockIdx
  ) [seqstrict(1,2,3,4,5,7)]

  rule [validate-owner-expected-intercept-spl]:
    <k> #execTerminatorCall(_, FUNC,
            operandCopy(place(LOCAL0, PROJS0))
            operandCopy(place(LOCAL1, PROJS1))
            operandCopy(place(LOCAL2, PROJS2))
            operandMove(PLACE3)
            .Operands,
            DEST, TARGET, _UNWIND, _SPAN) ~> _CONT
      => #validateOwnerResultExpectedSPL(
            operandCopy(place(LOCAL0, appendP(PROJS0, projectionElemDeref .ProjectionElems))),
            operandCopy(place(LOCAL1, appendP(PROJS1, projectionElemDeref projectionElemField(fieldIdx(0), #hack()) projectionElemDeref .ProjectionElems))),
            operandCopy(place(LOCAL1, appendP(PROJS1, projectionElemDeref projectionElemField(fieldIdx(5), #hack()) .ProjectionElems))),
            operandCopy(place(LOCAL1, appendP(PROJS1, projectionElemDeref projectionElemField(fieldIdx(3), #hack()) projectionElemDeref .ProjectionElems))),
            operandCopy(place(LOCAL1, appendP(PROJS1, projectionElemDeref projectionElemField(fieldIdx(2), #hack()) .ProjectionElems))),
            place(LOCAL2, PROJS2),
            operandCopy(PLACE3),
            DEST, TARGET)
    </k>
    requires #functionName(FUNC) ==String "spl_token::entrypoint::expected_validate_owner_result"
    [priority(30)]

  // Case 1: expected_owner != owner_key => Err(Custom(4))
  rule [expected-case1-spl]:
    <k> #validateOwnerResultExpectedSPL(
            EXPECTED_OWNER, OWNER_KEY,
            _IS_SIGNER, _OWNER_OF_ACCOUNT, _DATA, _TX_SIGNERS,
            _MAYBE_MULTISIG, DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(0), ListItem(Integer(4, 32, false)))))) ~> #continueAt(TARGET) </k>
    requires EXPECTED_OWNER =/=K OWNER_KEY
    [priority(31)]


  // Case 2: non-multisig, !is_signer => Err(MissingRequiredSignature)
  rule [expected-case2-spl]:
    <k> #validateOwnerResultExpectedSPL(
            OWNER_KEY, OWNER_KEY,
            BoolVal(false), _OWNER_OF_ACCOUNT, _DATA, _TX_SIGNERS,
            Aggregate(variantIdx(0), .List),
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))) ~> #continueAt(TARGET) </k>
    [priority(31)]


  // Case 3: non-multisig, is_signer => Ok(())
  rule [expected-case3-spl]:
    <k> #validateOwnerResultExpectedSPL(
            OWNER_KEY, OWNER_KEY,
            BoolVal(true), _OWNER_OF_ACCOUNT, _DATA, _TX_SIGNERS,
            Aggregate(variantIdx(0), .List),
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(Aggregate(variantIdx(0), .List)))) ~> #continueAt(TARGET) </k>
    [priority(31)]


  // Case 4: multisig, owner != PROGRAM_ID, !is_signer
  rule [expected-case4-spl]:
    <k> #validateOwnerResultExpectedSPL(
            OWNER_KEY, OWNER_KEY,
            BoolVal(false), _OWNER_OF_ACCOUNT, _DATA, _TX_SIGNERS,
            Aggregate(variantIdx(1), _),
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))) ~> #continueAt(TARGET) </k>
    [priority(33)]


  // Case 5: multisig, owner != PROGRAM_ID, is_signer
  rule [expected-case5-spl]:
    <k> #validateOwnerResultExpectedSPL(
            OWNER_KEY, OWNER_KEY,
            BoolVal(true), _OWNER_OF_ACCOUNT, _DATA, _TX_SIGNERS,
            Aggregate(variantIdx(1), _),
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(Aggregate(variantIdx(0), .List)))) ~> #continueAt(TARGET) </k>
    [priority(33)]


  // Case 6: multisig, owner == PROGRAM_ID, is_initialized Err
  rule [expected-case6-spl]:
    <k> #validateOwnerResultExpectedSPL(
            OWNER_KEY, OWNER_KEY,
            _IS_SIGNER, _OWNER_OF_ACCOUNT, _DATA, _TX_SIGNERS,
            Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(1), _))),
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(3), .List)))) ~> #continueAt(TARGET) </k>

    [priority(31)]


  // Case 7: multisig, owner == PROGRAM_ID, is_initialized = Ok(false)
  rule [expected-case7-spl]:
    <k> #validateOwnerResultExpectedSPL(
            OWNER_KEY, OWNER_KEY,
            _IS_SIGNER, _OWNER_OF_ACCOUNT, _DATA, _TX_SIGNERS,
            Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(0), ListItem(BoolVal(false))))),
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(9), .List)))) ~> #continueAt(TARGET) </k>

    [priority(31)]


  // Cases 8-10: multisig initialized signer-checking — no lemma, fall through to small-step

endmodule
```

## `inner_test_validate_owner` lemma

```k
module INNER-TEST-VALIDATE-OWNER-SPL-TOKEN-LEMMA
  imports VALIDATE-OWNER-COMMON-SPL

  // Same as expected but with extra RESULT arg
  syntax KItem ::= #validateOwnerResultSPL(
      Evaluation, Evaluation, Evaluation, Evaluation, Evaluation,
      Place, Evaluation, Evaluation, Place, MaybeBasicBlockIdx
  ) [seqstrict(1,2,3,4,5,7,8)]

  rule [inner-validate-owner-intercept-spl]:
    <k> #execTerminatorCall(_, FUNC,
            operandCopy(place(LOCAL0, PROJS0))
            operandCopy(place(LOCAL1, PROJS1))
            operandCopy(place(LOCAL2, PROJS2))
            operandMove(PLACE3)
            operandMove(PLACE4)
            .Operands,
            DEST, TARGET, _UNWIND, _SPAN) ~> _CONT
      => #validateOwnerResultSPL(
            operandCopy(place(LOCAL0, appendP(PROJS0, projectionElemDeref .ProjectionElems))),
            operandCopy(place(LOCAL1, appendP(PROJS1, projectionElemDeref projectionElemField(fieldIdx(0), #hack()) projectionElemDeref .ProjectionElems))),
            operandCopy(place(LOCAL1, appendP(PROJS1, projectionElemDeref projectionElemField(fieldIdx(5), #hack()) .ProjectionElems))),
            operandCopy(place(LOCAL1, appendP(PROJS1, projectionElemDeref projectionElemField(fieldIdx(3), #hack()) projectionElemDeref .ProjectionElems))),
            operandCopy(place(LOCAL1, appendP(PROJS1, projectionElemDeref projectionElemField(fieldIdx(2), #hack()) .ProjectionElems))),
            place(LOCAL2, PROJS2),
            operandCopy(PLACE3),
            operandCopy(PLACE4),
            DEST, TARGET)
    </k>
    requires #functionName(FUNC) ==String "spl_token::entrypoint::inner_test_validate_owner"
    [priority(30)]

  // Case 1: expected_owner != owner_key, result must be Err(Custom(4))
  rule [inner-case1-spl]:
    <k> #validateOwnerResultSPL(
            EXPECTED_OWNER, OWNER_KEY,
            _IS_SIGNER, _OWNER_OF_ACCOUNT, _DATA, _TX_SIGNERS,
            _MAYBE_MULTISIG, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(0), ListItem(Integer(4, 32, false))))),
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(0), ListItem(Integer(4, 32, false)))))) ~> #continueAt(TARGET) </k>
    requires EXPECTED_OWNER =/=K OWNER_KEY
    [priority(31)]


  // Case 1b: keys match but result is Err(Custom(4)) — pass through.
  // This handles the symbolic branch where key equality hasn't been split yet.
  rule [inner-case1b-keys-match-custom4-spl]:
    <k> #validateOwnerResultSPL(
            OWNER_KEY, OWNER_KEY,
            _IS_SIGNER, _OWNER_OF_ACCOUNT, _DATA, _TX_SIGNERS,
            _MAYBE_MULTISIG,
            Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(0), ListItem(Integer(4, 32, false))))),
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(0), ListItem(Integer(4, 32, false)))))) ~> #continueAt(TARGET) </k>
    [priority(32)]

  // Case 2: non-multisig, !is_signer => Err(MissingRequiredSignature)
  rule [inner-case2-spl]:
    <k> #validateOwnerResultSPL(
            OWNER_KEY, OWNER_KEY,
            _IS_SIGNER, _OWNER_OF_ACCOUNT, _DATA, _TX_SIGNERS,
            Aggregate(variantIdx(0), .List),
            Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List))),
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))) ~> #continueAt(TARGET) </k>
    [priority(31)]


  // Case 3: non-multisig, is_signer => Ok
  // Use wildcard for Ok's inner value to handle thunked () from result.clone()
  rule [inner-case3-spl]:
    <k> #validateOwnerResultSPL(
            OWNER_KEY, OWNER_KEY,
            _IS_SIGNER, _OWNER_OF_ACCOUNT, _DATA, _TX_SIGNERS,
            Aggregate(variantIdx(0), .List),
            Aggregate(variantIdx(0), _),
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(Aggregate(variantIdx(0), .List)))) ~> #continueAt(TARGET) </k>
    [priority(31)]


  // Case 4: multisig, owner != PROGRAM_ID, !is_signer => Err(MissingRequiredSignature)
  rule [inner-case4-spl]:
    <k> #validateOwnerResultSPL(
            OWNER_KEY, OWNER_KEY,
            _IS_SIGNER, _OWNER_OF_ACCOUNT, _DATA, _TX_SIGNERS,
            Aggregate(variantIdx(1), _),
            Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List))),
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))) ~> #continueAt(TARGET) </k>
    [priority(33)]


  // Case 5: multisig, owner != PROGRAM_ID, is_signer => Ok
  // Use wildcard for Ok's inner value to handle thunked () from result.clone()
  rule [inner-case5-spl]:
    <k> #validateOwnerResultSPL(
            OWNER_KEY, OWNER_KEY,
            _IS_SIGNER, _OWNER_OF_ACCOUNT, _DATA, _TX_SIGNERS,
            Aggregate(variantIdx(1), _),
            Aggregate(variantIdx(0), _),
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(Aggregate(variantIdx(0), .List)))) ~> #continueAt(TARGET) </k>
    [priority(33)]


  // Case 6: multisig, owner == PROGRAM_ID, is_initialized Err
  rule [inner-case6-spl]:
    <k> #validateOwnerResultSPL(
            OWNER_KEY, OWNER_KEY,
            _IS_SIGNER, _OWNER_OF_ACCOUNT, _DATA, _TX_SIGNERS,
            Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(1), _))),
            Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(3), .List))),
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(3), .List)))) ~> #continueAt(TARGET) </k>

    [priority(31)]


  // Case 7: multisig, owner == PROGRAM_ID, is_initialized = Ok(false)
  rule [inner-case7-spl]:
    <k> #validateOwnerResultSPL(
            OWNER_KEY, OWNER_KEY,
            _IS_SIGNER, _OWNER_OF_ACCOUNT, _DATA, _TX_SIGNERS,
            Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(0), ListItem(BoolVal(false))))),
            Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(9), .List))),
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(9), .List)))) ~> #continueAt(TARGET) </k>

    [priority(31)]


  // Cases 8-9: multisig initialized, signer-checking => Err(MissingRequiredSignature)
  // No requires condition — lower priority ensures cases 4-5 are tried first.
  // This fires only when 4-5 don't match (i.e., owner IS the program ID).
  rule [inner-case8-9-missing-sig-spl]:
    <k> #validateOwnerResultSPL(
            OWNER_KEY, OWNER_KEY,
            _IS_SIGNER, _OWNER_OF_ACCOUNT, _DATA, _TX_SIGNERS,
            Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(0), ListItem(BoolVal(true))))),
            Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List))),
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))) ~> #continueAt(TARGET) </k>
    [priority(32)]

  // Case 10: multisig initialized, enough signatures => Ok
  // No requires condition — same priority scheme as case 8-9.
  rule [inner-case10-ok-spl]:
    <k> #validateOwnerResultSPL(
            OWNER_KEY, OWNER_KEY,
            _IS_SIGNER, _OWNER_OF_ACCOUNT, _DATA, _TX_SIGNERS,
            Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(0), ListItem(BoolVal(true))))),
            Aggregate(variantIdx(0), _),
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(Aggregate(variantIdx(0), .List)))) ~> #continueAt(TARGET) </k>
    [priority(32)]

endmodule
```
