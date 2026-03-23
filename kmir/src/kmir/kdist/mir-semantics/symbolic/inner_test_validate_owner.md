```k
requires "../kmir-ast.md"
requires "../rt/data.md"
requires "../kmir.md"
requires "../rt/configuration.md"
requires "p-token.md"
```

## Common helpers for validate_owner lemmas

Shared constants, projection helpers, and signer-checking functions used by
both `expected_validate_owner_result` and `inner_test_validate_owner` lemmas.

```k
module VALIDATE-OWNER-COMMON
  imports KMIR-P-TOKEN

  // Result<(), ProgramError> values used in rules below (inlined as Aggregates):
  //   Ok(())                        = Aggregate(variantIdx(0), ListItem(Aggregate(variantIdx(0), .List)))
  //   Err(Custom(4))                = Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(0), ListItem(Integer(4, 32, false)))))
  //   Err(MissingRequiredSignature) = Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))
  //   Err(UninitializedAccount)     = Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(9), .List)))
  //   Err(InvalidAccountData)       = Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(3), .List)))

  // Convert a Result<(), ProgramError> Value to a human-readable string
  syntax String ::= Result2String ( Value ) [function, total]
  rule Result2String(Aggregate(variantIdx(0), ListItem(Aggregate(variantIdx(0), .List))))
    => "Ok(())"
  rule Result2String(Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(0), ListItem(Integer(4, 32, false))))))
    => "Err(Custom(4))"
  rule Result2String(Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List))))
    => "Err(MissingRequiredSignature)"
  rule Result2String(Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(9), .List))))
    => "Err(UninitializedAccount)"
  rule Result2String(Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(3), .List))))
    => "Err(InvalidAccountData)"
  rule Result2String(_) => "Unknown" [owise]

  // SPL Token Program ID as a Key (32 bytes).
  // Hex: 06 dd f6 e1 d7 65 a1 93 d9 cb e1 46 ce eb 79 ac
  //      1c b4 85 ed 5f 5b 37 91 3a 8c f5 85 7e ff 00 a9
  syntax Key ::= "#programIdKey" [function, total]
  rule #programIdKey => Key(
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
    )

  // Projection chain: from &[AccountInfo] Place to the ith tx_signer's
  // Account Aggregate (9-field struct behind the AccountInfo pointer).
  // Parameters: I = index, N = array length (min_length for ConstantIndex).
  syntax ProjectionElems ::= #txSignerAccountProjs(Int, Int) [function, total]
  rule #txSignerAccountProjs(I, N) =>
    projectionElemDeref
    projectionElemConstantIndex(I, N, false)
    projectionElemField(fieldIdx(0), #hack())
    projectionElemDeref
    .ProjectionElems

  // =========================================================================
  // Common helpers for signer checking
  // =========================================================================

  syntax Int ::= #bool2Int(Bool) [function, total]
  rule #bool2Int(true)  => 1
  rule #bool2Int(false) => 0

  // =========================================================================
  // Generic signer checking helpers (list-based)
  //
  // These work for any number of tx_signers and registered signers.
  // The caller constructs lists from the extracted values.
  //
  // keyAndIsSigner(KEY, IS) pairs a tx_signer's public key with its is_signer flag.
  // firstN(N, LIST) takes the first N elements of LIST (implements [0..n] slicing).
  //
  // #unsignedExists(TxSigners, RegisteredKeys):
  //   outer loop over tx_signers, inner loop over registered keys.
  //   True if any tx_signer matches a registered key and is NOT a signer.
  //
  // #signersCount(TxSigners, RegisteredKeys):
  //   outer loop over registered keys, inner loop over tx_signers.
  //   Counts how many registered keys have a matching signed tx_signer.
  // =========================================================================

  syntax KeyAndIsSigner ::= keyAndIsSigner( Value, Int )

  syntax List ::= firstN( Int, List ) [function, total]
  // -------------------------------------------------
  rule firstN(0, _) => .List
  rule firstN(N, ListItem(X) REST) => ListItem(X) firstN(N -Int 1, REST) requires N >Int 0
  rule firstN(_, .List) => .List [owise]

  // --- #unsignedExists: outer over tx_signers, inner over registered keys ---

  syntax Bool ::= #unsignedExists( List, List ) [function]
  // -----------------------------------------------------------
  rule #unsignedExists(.List, _REGS) => false
  rule #unsignedExists(ListItem(keyAndIsSigner(KEY, IS)) REST, REGS)
    => #unsignedExistsInner(KEY, IS, REGS)
    orBool #unsignedExists(REST, REGS)

  syntax Bool ::= #unsignedExistsInner( Value, Int, List ) [function]
  // -----------------------------------------------------------------------
  rule #unsignedExistsInner(_KEY, _IS, .List) => false
  rule #unsignedExistsInner(KEY, IS, ListItem(SKEY) REST)
    => ( IS ==Int 0 andBool fromKey(SKEY) ==K KEY )
    orBool #unsignedExistsInner(KEY, IS, REST)

  // --- #signersCount: outer over registered keys, inner over tx_signers ---

  syntax Int ::= #signersCount( List, List ) [function]
  // ---------------------------------------------------------
  rule #signersCount(_TXSIGNERS, .List) => 0
  rule #signersCount(TXSIGNERS, ListItem(SKEY) REST)
    => #bool2Int(#signerMatchedInner(SKEY, TXSIGNERS))
     +Int #signersCount(TXSIGNERS, REST)

  syntax Bool ::= #signerMatchedInner( Key, List ) [function]
  // ---------------------------------------------------------------
  rule #signerMatchedInner(_SKEY, .List) => false
  rule #signerMatchedInner(SKEY, ListItem(keyAndIsSigner(KEY, IS)) REST)
    => ( fromKey(SKEY) ==K KEY andBool IS =/=Int 0 )
    orBool #signerMatchedInner(SKEY, REST)

endmodule
```

## Lemma rules for `expected_validate_owner_result`

These intercept the call to `expected_validate_owner_result` and directly
produce the return value, bypassing the function body.

```k
module EXPECTED-VALIDATE-OWNER-RESULT-P-TOKEN-LEMMA
  imports VALIDATE-OWNER-COMMON

  // =========================================================================
  // Intercept rule and dispatch helper
  // =========================================================================

  syntax KItem ::= #validateOwnerResultExpected( Evaluation, Evaluation, Place, Evaluation, Place, MaybeBasicBlockIdx )
      [seqstrict(1,2,4)]

  rule [validate-owner-expected-intercept]:
    <k> #execTerminatorCall(_, FUNC,
            operandCopy(place(LOCAL0, PROJS0))
            operandCopy(place(LOCAL1, PROJS1))
            operandCopy(place(LOCAL2, PROJS2))
            operandMove(PLACE3)
            .Operands,
            DEST, TARGET, _UNWIND, _SPAN) ~> _CONT
      => #validateOwnerResultExpected(
            operandCopy(place(LOCAL0, appendP(PROJS0, projectionElemDeref .ProjectionElems))),
            operandCopy(place(LOCAL1, appendP(PROJS1, projectionElemDeref projectionElemField(fieldIdx(0), #hack()) projectionElemDeref .ProjectionElems))),
            place(LOCAL2, PROJS2),
            operandCopy(PLACE3),
            DEST, TARGET)
    </k>
    requires #functionName(FUNC) ==String "pinocchio_token_program::entrypoint::expected_validate_owner_result"
    [priority(30)]

  // =========================================================================
  // Case 1: expected_owner != key!(owner_account_info) => Err(Custom(4))
  // =========================================================================
  rule [validate-owner-expected-wrong-owner-nonmultisig]:
    <k> #validateOwnerResultExpected(
            EXPECTED_OWNER,
            PAccountAccount(PAcc(_,_,_,_,_, OWNER_KEY, _, _, _), _),
            _,
            _MAYBE_MULTISIG,
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(0), ListItem(Integer(4, 32, false)))))) ~> #continueAt(TARGET)  // Err(Custom(4))
    </k>
    requires EXPECTED_OWNER =/=K fromKey(OWNER_KEY)
    [priority(30)]

  rule [validate-owner-expected-wrong-owner-multisig]:
    <k> #validateOwnerResultExpected(
            EXPECTED_OWNER,
            PAccountMultisig(PAcc(_,_,_,_,_, OWNER_KEY, _, _, _), _),
            _,
            _MAYBE_MULTISIG,
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(0), ListItem(Integer(4, 32, false)))))) ~> #continueAt(TARGET)  // Err(Custom(4))
    </k>
    requires EXPECTED_OWNER =/=K fromKey(OWNER_KEY)
    [priority(30)]

  // =========================================================================
  // Case 2: non-multisig, not signer => Err(MissingRequiredSignature)
  // =========================================================================
  rule [validate-owner-expected-nonmultisig-not-signer]:
    <k> #validateOwnerResultExpected(
            EXPECTED_OWNER,
            PAccountAccount(PAcc(_, U8(IS_SIGNER), _,_,_, OWNER_KEY, _, _, _), _),
            _,
            Aggregate(variantIdx(0), .List),   // None
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))) ~> #continueAt(TARGET)  // Err(MissingRequiredSignature)
    </k>
    requires EXPECTED_OWNER ==K fromKey(OWNER_KEY)
     andBool IS_SIGNER ==Int 0
    [priority(30)]

  // =========================================================================
  // Case 3: non-multisig, is signer => Ok(())
  // =========================================================================
  rule [validate-owner-expected-nonmultisig-ok]:
    <k> #validateOwnerResultExpected(
            EXPECTED_OWNER,
            PAccountAccount(PAcc(_, U8(IS_SIGNER), _,_,_, OWNER_KEY, _, _, _), _),
            _,
            Aggregate(variantIdx(0), .List),   // None
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(Aggregate(variantIdx(0), .List)))) ~> #continueAt(TARGET)  // Ok(())
    </k>
    requires EXPECTED_OWNER ==K fromKey(OWNER_KEY)
     andBool IS_SIGNER =/=Int 0
    [priority(30)]

  // =========================================================================
  // Case 4: multisig fallthrough (owner!=PROGRAM_ID), not signer
  // =========================================================================
  rule [validate-owner-expected-multisig-fallthrough-not-signer]:
    <k> #validateOwnerResultExpected(
            EXPECTED_OWNER,
            PAccountMultisig(PAcc(_, U8(IS_SIGNER), _,_,_, OWNER_KEY, OWNER_OF_ACCOUNT, _, _), _),
            _,
            Aggregate(variantIdx(1), _),   // Some(...)
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))) ~> #continueAt(TARGET)  // Err(MissingRequiredSignature)
    </k>
    requires EXPECTED_OWNER ==K fromKey(OWNER_KEY)
     andBool OWNER_OF_ACCOUNT =/=K #programIdKey
     andBool IS_SIGNER ==Int 0
    [priority(30)]

  // =========================================================================
  // Case 5: multisig fallthrough (owner!=PROGRAM_ID), is signer
  // =========================================================================
  rule [validate-owner-expected-multisig-fallthrough-ok]:
    <k> #validateOwnerResultExpected(
            EXPECTED_OWNER,
            PAccountMultisig(PAcc(_, U8(IS_SIGNER), _,_,_, OWNER_KEY, OWNER_OF_ACCOUNT, _, _), _),
            _,
            Aggregate(variantIdx(1), _),   // Some(...)
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(Aggregate(variantIdx(0), .List)))) ~> #continueAt(TARGET)  // Ok(())
    </k>
    requires EXPECTED_OWNER ==K fromKey(OWNER_KEY)
     andBool OWNER_OF_ACCOUNT =/=K #programIdKey
     andBool IS_SIGNER =/=Int 0
    [priority(30)]

  // =========================================================================
  // Case 6: multisig, is_initialized returns Err => Err(InvalidAccountData)
  // =========================================================================
  rule [validate-owner-expected-multisig-invalid-data]:
    <k> #validateOwnerResultExpected(
            EXPECTED_OWNER,
            PAccountMultisig(PAcc(_,_,_,_,_, OWNER_KEY, OWNER_OF_ACCOUNT, _, _), _),
            _,
            Aggregate(variantIdx(1), ListItem(
              Aggregate(variantIdx(1), ListItem(
                Aggregate(variantIdx(3), .List))))),   // Some(Err(InvalidAccountData))
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(3), .List)))) ~> #continueAt(TARGET)  // Err(InvalidAccountData)
    </k>
    requires EXPECTED_OWNER ==K fromKey(OWNER_KEY)
     andBool OWNER_OF_ACCOUNT ==K #programIdKey
    [priority(30)]

  // =========================================================================
  // Case 7: multisig, is_initialized returns Ok(false) => Err(UninitializedAccount)
  // =========================================================================
  rule [validate-owner-expected-multisig-uninitialized]:
    <k> #validateOwnerResultExpected(
            EXPECTED_OWNER,
            PAccountMultisig(PAcc(_,_,_,_,_, OWNER_KEY, OWNER_OF_ACCOUNT, _, _), _),
            _,
            Aggregate(variantIdx(1), ListItem(
              Aggregate(variantIdx(0), ListItem(
                BoolVal(false))))),                    // Some(Ok(false))
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(9), .List)))) ~> #continueAt(TARGET)  // Err(UninitializedAccount)
    </k>
    requires EXPECTED_OWNER ==K fromKey(OWNER_KEY)
     andBool OWNER_OF_ACCOUNT ==K #programIdKey
    [priority(30)]

  // =========================================================================
  // Multisig signer-checking (Cases 8-10)
  // =========================================================================

  // N=3: all registered signers
  rule [validate-owner-expected-multisig-check-signers-n3]:
    <k> #validateOwnerResultExpected(
            EXPECTED_OWNER,
            PAccountMultisig(
                PAcc(_, _, _,_,_, OWNER_KEY, OWNER_OF_ACCOUNT, _, _),
                IMulti(U8(M), U8(3), _, // N=3
                    Signers(SKEYS))),
            place(LOCAL2, PROJS2),
            Aggregate(variantIdx(1), ListItem(
              Aggregate(variantIdx(0), ListItem(
                BoolVal(true))))),                    // Some(Ok(true))
            DEST, TARGET)
      => #resolveSignerCountExpected(
            M, SKEYS,
            operandCopy(place(LOCAL2, appendP(PROJS2, projectionElemDeref .ProjectionElems))),
            place(LOCAL2, PROJS2),
            DEST, TARGET)
    </k>
    requires EXPECTED_OWNER ==K fromKey(OWNER_KEY)
     andBool OWNER_OF_ACCOUNT ==K #programIdKey
    [priority(30)]

  // N=2: first 2 registered signers
  rule [validate-owner-expected-multisig-check-signers-n2]:
    <k> #validateOwnerResultExpected(
            EXPECTED_OWNER,
            PAccountMultisig(
                PAcc(_, _, _,_,_, OWNER_KEY, OWNER_OF_ACCOUNT, _, _),
                IMulti(U8(M), U8(2), _, // N=2
                    Signers(SKEYS))),
            place(LOCAL2, PROJS2),
            Aggregate(variantIdx(1), ListItem(
              Aggregate(variantIdx(0), ListItem(
                BoolVal(true))))),                    // Some(Ok(true))
            DEST, TARGET)
      => #resolveSignerCountExpected(
            M, firstN(2, SKEYS),
            operandCopy(place(LOCAL2, appendP(PROJS2, projectionElemDeref .ProjectionElems))),
            place(LOCAL2, PROJS2),
            DEST, TARGET)
    </k>
    requires EXPECTED_OWNER ==K fromKey(OWNER_KEY)
     andBool OWNER_OF_ACCOUNT ==K #programIdKey
    [priority(30)]

  // N=1: first registered signer only
  rule [validate-owner-expected-multisig-check-signers-n1]:
    <k> #validateOwnerResultExpected(
            EXPECTED_OWNER,
            PAccountMultisig(
                PAcc(_, _, _,_,_, OWNER_KEY, OWNER_OF_ACCOUNT, _, _),
                IMulti(U8(M), U8(1), _, // N=1
                    Signers(SKEYS))),
            place(LOCAL2, PROJS2),
            Aggregate(variantIdx(1), ListItem(
              Aggregate(variantIdx(0), ListItem(
                BoolVal(true))))),                    // Some(Ok(true))
            DEST, TARGET)
      => #resolveSignerCountExpected(
            M, firstN(1, SKEYS),
            operandCopy(place(LOCAL2, appendP(PROJS2, projectionElemDeref .ProjectionElems))),
            place(LOCAL2, PROJS2),
            DEST, TARGET)
    </k>
    requires EXPECTED_OWNER ==K fromKey(OWNER_KEY)
     andBool OWNER_OF_ACCOUNT ==K #programIdKey
    [priority(30)]

  syntax KItem ::= #resolveSignerCountExpected(
      Int, List,             // M, REGS (already-sliced registered keys)
      Evaluation,
      Place,
      Place, MaybeBasicBlockIdx
    ) [seqstrict(3)]

  rule [resolve-3-signers-expected]:
    <k> #resolveSignerCountExpected(
            M, REGS,
            Range(ListItem(_) ListItem(_) ListItem(_)),
            place(LOCAL2, PROJS2),
            DEST, TARGET)
      => #checkSigners3Expected(
            M, REGS,
            operandCopy(place(LOCAL2, appendP(PROJS2, #txSignerAccountProjs(0, 3)))),
            operandCopy(place(LOCAL2, appendP(PROJS2, #txSignerAccountProjs(1, 3)))),
            operandCopy(place(LOCAL2, appendP(PROJS2, #txSignerAccountProjs(2, 3)))),
            DEST, TARGET)
    </k>
    [priority(30)]

  rule [resolve-2-signers-expected]:
    <k> #resolveSignerCountExpected(
            M, REGS,
            Range(ListItem(_) ListItem(_)),
            place(LOCAL2, PROJS2),
            DEST, TARGET)
      => #checkSigners2Expected(
            M, REGS,
            operandCopy(place(LOCAL2, appendP(PROJS2, #txSignerAccountProjs(0, 2)))),
            operandCopy(place(LOCAL2, appendP(PROJS2, #txSignerAccountProjs(1, 2)))),
            DEST, TARGET)
    </k>
    [priority(30)]

  rule [resolve-1-signer-expected]:
    <k> #resolveSignerCountExpected(
            M, REGS,
            Range(ListItem(_)),
            place(LOCAL2, PROJS2),
            DEST, TARGET)
      => #checkSigners1Expected(
            M, REGS,
            operandCopy(place(LOCAL2, appendP(PROJS2, #txSignerAccountProjs(0, 1)))),
            DEST, TARGET)
    </k>
    [priority(30)]

  // --- 3 tx_signers ---
  // After evaluating the 3 tx_signer accounts, use generic list-based helpers.

  syntax KItem ::= #checkSigners3Expected(
      Int, List,             // M, REGS
      Evaluation, Evaluation, Evaluation,
      Place, MaybeBasicBlockIdx
    ) [seqstrict(3,4,5)]

  rule [validate-owner-expected-multisig-unsigned-3]:
    <k> #checkSigners3Expected(
            _M, REGS,
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS0, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY0) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS1, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY1) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS2, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY2) ListItem(_) ListItem(_) ListItem(_)),
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))) ~> #continueAt(TARGET)  // Err(MissingRequiredSignature)
    </k>
    requires #unsignedExists(
               ListItem(keyAndIsSigner(KEY0, IS0)) ListItem(keyAndIsSigner(KEY1, IS1)) ListItem(keyAndIsSigner(KEY2, IS2)),
               REGS)
    [priority(30)]

  rule [validate-owner-expected-multisig-not-enough-3]:
    <k> #checkSigners3Expected(
            M, REGS,
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS0, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY0) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS1, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY1) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS2, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY2) ListItem(_) ListItem(_) ListItem(_)),
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))) ~> #continueAt(TARGET)  // Err(MissingRequiredSignature)
    </k>
    requires notBool #unsignedExists(
               ListItem(keyAndIsSigner(KEY0, IS0)) ListItem(keyAndIsSigner(KEY1, IS1)) ListItem(keyAndIsSigner(KEY2, IS2)),
               REGS)
     andBool #signersCount(
               ListItem(keyAndIsSigner(KEY0, IS0)) ListItem(keyAndIsSigner(KEY1, IS1)) ListItem(keyAndIsSigner(KEY2, IS2)),
               REGS) <Int M
    [priority(30)]

  rule [validate-owner-expected-multisig-ok-3]:
    <k> #checkSigners3Expected(
            M, REGS,
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS0, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY0) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS1, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY1) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS2, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY2) ListItem(_) ListItem(_) ListItem(_)),
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(Aggregate(variantIdx(0), .List)))) ~> #continueAt(TARGET)  // Ok(())
    </k>
    requires notBool #unsignedExists(
               ListItem(keyAndIsSigner(KEY0, IS0)) ListItem(keyAndIsSigner(KEY1, IS1)) ListItem(keyAndIsSigner(KEY2, IS2)),
               REGS)
     andBool #signersCount(
               ListItem(keyAndIsSigner(KEY0, IS0)) ListItem(keyAndIsSigner(KEY1, IS1)) ListItem(keyAndIsSigner(KEY2, IS2)),
               REGS) >=Int M
    [priority(30)]

  // --- 2 tx_signers ---

  syntax KItem ::= #checkSigners2Expected(
      Int, List,             // M, REGS
      Evaluation, Evaluation,
      Place, MaybeBasicBlockIdx
    ) [seqstrict(3,4)]

  rule [validate-owner-expected-multisig-unsigned-2]:
    <k> #checkSigners2Expected(
            _M, REGS,
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS0, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY0) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS1, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY1) ListItem(_) ListItem(_) ListItem(_)),
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))) ~> #continueAt(TARGET)
    </k>
    requires #unsignedExists(
               ListItem(keyAndIsSigner(KEY0, IS0)) ListItem(keyAndIsSigner(KEY1, IS1)),
               REGS)
    [priority(30)]

  rule [validate-owner-expected-multisig-not-enough-2]:
    <k> #checkSigners2Expected(
            M, REGS,
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS0, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY0) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS1, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY1) ListItem(_) ListItem(_) ListItem(_)),
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))) ~> #continueAt(TARGET)
    </k>
    requires notBool #unsignedExists(
               ListItem(keyAndIsSigner(KEY0, IS0)) ListItem(keyAndIsSigner(KEY1, IS1)),
               REGS)
     andBool #signersCount(
               ListItem(keyAndIsSigner(KEY0, IS0)) ListItem(keyAndIsSigner(KEY1, IS1)),
               REGS) <Int M
    [priority(30)]

  rule [validate-owner-expected-multisig-ok-2]:
    <k> #checkSigners2Expected(
            M, REGS,
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS0, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY0) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS1, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY1) ListItem(_) ListItem(_) ListItem(_)),
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(Aggregate(variantIdx(0), .List)))) ~> #continueAt(TARGET)
    </k>
    requires notBool #unsignedExists(
               ListItem(keyAndIsSigner(KEY0, IS0)) ListItem(keyAndIsSigner(KEY1, IS1)),
               REGS)
     andBool #signersCount(
               ListItem(keyAndIsSigner(KEY0, IS0)) ListItem(keyAndIsSigner(KEY1, IS1)),
               REGS) >=Int M
    [priority(30)]

  // --- 1 tx_signer ---

  syntax KItem ::= #checkSigners1Expected(
      Int, List,             // M, REGS
      Evaluation,
      Place, MaybeBasicBlockIdx
    ) [seqstrict(3)]

  rule [validate-owner-expected-multisig-unsigned-1]:
    <k> #checkSigners1Expected(
            _M, REGS,
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS0, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY0) ListItem(_) ListItem(_) ListItem(_)),
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))) ~> #continueAt(TARGET)
    </k>
    requires #unsignedExists(
               ListItem(keyAndIsSigner(KEY0, IS0)),
               REGS)
    [priority(30)]

  rule [validate-owner-expected-multisig-not-enough-1]:
    <k> #checkSigners1Expected(
            M, REGS,
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS0, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY0) ListItem(_) ListItem(_) ListItem(_)),
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))) ~> #continueAt(TARGET)
    </k>
    requires notBool #unsignedExists(
               ListItem(keyAndIsSigner(KEY0, IS0)),
               REGS)
     andBool #signersCount(
               ListItem(keyAndIsSigner(KEY0, IS0)),
               REGS) <Int M
    [priority(30)]

  rule [validate-owner-expected-multisig-ok-1]:
    <k> #checkSigners1Expected(
            M, REGS,
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS0, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY0) ListItem(_) ListItem(_) ListItem(_)),
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(Aggregate(variantIdx(0), .List)))) ~> #continueAt(TARGET)
    </k>
    requires notBool #unsignedExists(
               ListItem(keyAndIsSigner(KEY0, IS0)),
               REGS)
     andBool #signersCount(
               ListItem(keyAndIsSigner(KEY0, IS0)),
               REGS) >=Int M
    [priority(30)]

endmodule
```

## Lemma rules for `inner_test_validate_owner`

This function has the same branching logic as `expected_validate_owner_result`,
but takes an additional `result` parameter and asserts (`assert_eq!`) that it
matches the expected outcome at each error branch. The success path returns
`Ok(())` without asserting.

```k
module INNER-TEST-VALIDATE-OWNER-P-TOKEN-LEMMA
  imports VALIDATE-OWNER-COMMON

  // =========================================================================
  // Intercept rule and dispatch helper
  // =========================================================================
  //
  // inner_test_validate_owner has 5 arguments:
  //   ARG0: expected_owner (&Pubkey)           - operandCopy
  //   ARG1: owner_account_info (&AccountInfo)  - operandCopy
  //   ARG2: tx_signers (&[AccountInfo])        - operandCopy
  //   ARG3: maybe_multisig_is_initialised      - operandMove
  //   ARG4: result (Result<(), ProgramError>)  - operandMove
  //
  // Positions 1, 2, 4, 5 are Evaluation (evaluated by seqstrict).
  // Position 3 is Place (tx_signers, unevaluated, used for projections).
  syntax KItem ::= #validateOwnerResult( Evaluation, Evaluation, Place, Evaluation, Evaluation, Place, MaybeBasicBlockIdx )
      [seqstrict(1,2,4,5)]
  //                                     ^expected_owner
  //                                                ^owner_account (PAccount)
  //                                                       ^tx_signers Place (NOT evaluated)
  //                                                                  ^maybe_multisig
  //                                                                             ^result
  //                                                                                        ^DEST  ^TARGET

  rule [inner-validate-owner-intercept]:
    <k> #execTerminatorCall(_, FUNC,
            operandCopy(place(LOCAL0, PROJS0))
            operandCopy(place(LOCAL1, PROJS1))
            operandCopy(place(LOCAL2, PROJS2))
            operandMove(PLACE3)
            operandMove(PLACE4)
            .Operands,
            DEST, TARGET, _UNWIND, _SPAN) ~> _CONT
      => #validateOwnerResult(
            // ARG0: deref &Pubkey to get Range(LIST)
            operandCopy(place(LOCAL0, appendP(PROJS0, projectionElemDeref .ProjectionElems))),
            // ARG1: deref &AccountInfo -> field(0) -> deref to get PAccount
            operandCopy(place(LOCAL1, appendP(PROJS1, projectionElemDeref projectionElemField(fieldIdx(0), #hack()) projectionElemDeref .ProjectionElems))),
            // ARG2: pass Place through unevaluated (used by multisig phase 2)
            place(LOCAL2, PROJS2),
            // ARG3: evaluate the Option value
            operandCopy(PLACE3),
            // ARG4: evaluate the result value
            operandCopy(PLACE4),
            DEST, TARGET)
    </k>
    requires #functionName(FUNC) ==String "pinocchio_token_program::entrypoint::inner_test_validate_owner"
    [priority(30)]

  // Custom MIRError for assert_eq failures in inner_test_validate_owner
  syntax MIRError ::= "#ValidateOwnerAssertFailed" "(" String ")"

  // =========================================================================
  // Case 1: expected_owner != key!(owner_account_info) => assert result == Err(Custom(4))
  // =========================================================================
  // Pass: result matches Err(Custom(4))
  rule [inner-validate-owner-wrong-owner-nonmultisig]:
    <k> #validateOwnerResult(
            EXPECTED_OWNER,
            PAccountAccount(PAcc(_,_,_,_,_, OWNER_KEY, _, _, _), _),
            _,
            _MAYBE_MULTISIG:Value,
            Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(0), ListItem(Integer(4, 32, false))))) #as RESULT,
            DEST, TARGET)
      => #setLocalValue(DEST, RESULT) ~> #continueAt(TARGET)
    </k>
    requires EXPECTED_OWNER =/=K fromKey(OWNER_KEY)
    [priority(30)]

  // Fail: result does not match Err(Custom(4))
  rule [inner-validate-owner-wrong-owner-nonmultisig-fail]:
    <k> #validateOwnerResult(
            EXPECTED_OWNER,
            PAccountAccount(PAcc(_,_,_,_,_, OWNER_KEY, _, _, _), _),
            _, _MAYBE_MULTISIG:Value, RESULT:Value, _DEST, _TARGET)
      => #ValidateOwnerAssertFailed(Result2String(RESULT) +String " =/= " +String Result2String(Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(0), ListItem(Integer(4, 32, false)))))))
    </k>
    requires EXPECTED_OWNER =/=K fromKey(OWNER_KEY)
     andBool RESULT =/=K Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(0), ListItem(Integer(4, 32, false)))))
    [priority(30)]

  // Pass: result matches Err(Custom(4))
  rule [inner-validate-owner-wrong-owner-multisig]:
    <k> #validateOwnerResult(
            EXPECTED_OWNER,
            PAccountMultisig(PAcc(_,_,_,_,_, OWNER_KEY, _, _, _), _),
            _,
            _MAYBE_MULTISIG:Value,
            Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(0), ListItem(Integer(4, 32, false))))) #as RESULT,
            DEST, TARGET)
      => #setLocalValue(DEST, RESULT) ~> #continueAt(TARGET)
    </k>
    requires EXPECTED_OWNER =/=K fromKey(OWNER_KEY)
    [priority(30)]

  // Fail: result does not match Err(Custom(4))
  rule [inner-validate-owner-wrong-owner-multisig-fail]:
    <k> #validateOwnerResult(
            EXPECTED_OWNER,
            PAccountMultisig(PAcc(_,_,_,_,_, OWNER_KEY, _, _, _), _),
            _, _MAYBE_MULTISIG:Value, RESULT:Value, _DEST, _TARGET)
      => #ValidateOwnerAssertFailed(Result2String(RESULT) +String " =/= " +String Result2String(Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(0), ListItem(Integer(4, 32, false)))))))
    </k>
    requires EXPECTED_OWNER =/=K fromKey(OWNER_KEY)
     andBool RESULT =/=K Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(0), ListItem(Integer(4, 32, false)))))
    [priority(30)]

  // =========================================================================
  // Case 2: non-multisig, not signer => assert result == Err(MissingRequiredSignature)
  // =========================================================================
  // Pass: result matches Err(MissingRequiredSignature)
  rule [inner-validate-owner-nonmultisig-not-signer]:
    <k> #validateOwnerResult(
            EXPECTED_OWNER,
            PAccountAccount(PAcc(_, U8(IS_SIGNER), _,_,_, OWNER_KEY, _, _, _), _),
            _,
            Aggregate(variantIdx(0), .List),   // None
            Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List))) #as RESULT,
            DEST, TARGET)
      => #setLocalValue(DEST, RESULT) ~> #continueAt(TARGET)
    </k>
    requires EXPECTED_OWNER ==K fromKey(OWNER_KEY)
     andBool IS_SIGNER ==Int 0
    [priority(30)]

  // Fail: result does not match Err(MissingRequiredSignature)
  rule [inner-validate-owner-nonmultisig-not-signer-fail]:
    <k> #validateOwnerResult(
            EXPECTED_OWNER,
            PAccountAccount(PAcc(_, U8(IS_SIGNER), _,_,_, OWNER_KEY, _, _, _), _),
            _,
            Aggregate(variantIdx(0), .List),   // None
            RESULT:Value,
            _DEST, _TARGET)
      => #ValidateOwnerAssertFailed(Result2String(RESULT) +String " =/= " +String Result2String(Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))))
    </k>
    requires EXPECTED_OWNER ==K fromKey(OWNER_KEY)
     andBool IS_SIGNER ==Int 0
     andBool RESULT =/=K Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))
    [priority(30)]

  // =========================================================================
  // Case 3: non-multisig, is signer => Ok(()) (no assert on result)
  // =========================================================================
  rule [inner-validate-owner-nonmultisig-ok]:
    <k> #validateOwnerResult(
            EXPECTED_OWNER,
            PAccountAccount(PAcc(_, U8(IS_SIGNER), _,_,_, OWNER_KEY, _, _, _), _),
            _,
            Aggregate(variantIdx(0), .List),   // None
            _RESULT,
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(Aggregate(variantIdx(0), .List)))) ~> #continueAt(TARGET)  // Ok(())
    </k>
    requires EXPECTED_OWNER ==K fromKey(OWNER_KEY)
     andBool IS_SIGNER =/=Int 0
    [priority(30)]

  // =========================================================================
  // Case 4: multisig fallthrough (owner!=PROGRAM_ID), not signer
  //         => assert result == Err(MissingRequiredSignature)
  // =========================================================================
  // Pass: result matches Err(MissingRequiredSignature)
  rule [inner-validate-owner-multisig-fallthrough-not-signer]:
    <k> #validateOwnerResult(
            EXPECTED_OWNER,
            PAccountMultisig(PAcc(_, U8(IS_SIGNER), _,_,_, OWNER_KEY, OWNER_OF_ACCOUNT, _, _), _),
            _,
            Aggregate(variantIdx(1), _),   // Some(...)
            Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List))) #as RESULT,
            DEST, TARGET)
      => #setLocalValue(DEST, RESULT) ~> #continueAt(TARGET)
    </k>
    requires EXPECTED_OWNER ==K fromKey(OWNER_KEY)
     andBool OWNER_OF_ACCOUNT =/=K #programIdKey
     andBool IS_SIGNER ==Int 0
    [priority(30)]

  // Fail: result does not match Err(MissingRequiredSignature)
  rule [inner-validate-owner-multisig-fallthrough-not-signer-fail]:
    <k> #validateOwnerResult(
            EXPECTED_OWNER,
            PAccountMultisig(PAcc(_, U8(IS_SIGNER), _,_,_, OWNER_KEY, OWNER_OF_ACCOUNT, _, _), _),
            _,
            Aggregate(variantIdx(1), _),   // Some(...)
            RESULT:Value,
            _DEST, _TARGET)
      => #ValidateOwnerAssertFailed(Result2String(RESULT) +String " =/= " +String Result2String(Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))))
    </k>
    requires EXPECTED_OWNER ==K fromKey(OWNER_KEY)
     andBool OWNER_OF_ACCOUNT =/=K #programIdKey
     andBool IS_SIGNER ==Int 0
     andBool RESULT =/=K Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))
    [priority(30)]

  // =========================================================================
  // Case 5: multisig fallthrough (owner!=PROGRAM_ID), is signer => Ok(())
  // =========================================================================
  rule [inner-validate-owner-multisig-fallthrough-ok]:
    <k> #validateOwnerResult(
            EXPECTED_OWNER,
            PAccountMultisig(PAcc(_, U8(IS_SIGNER), _,_,_, OWNER_KEY, OWNER_OF_ACCOUNT, _, _), _),
            _,
            Aggregate(variantIdx(1), _),   // Some(...)
            _RESULT,
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(Aggregate(variantIdx(0), .List)))) ~> #continueAt(TARGET)  // Ok(())
    </k>
    requires EXPECTED_OWNER ==K fromKey(OWNER_KEY)
     andBool OWNER_OF_ACCOUNT =/=K #programIdKey
     andBool IS_SIGNER =/=Int 0
    [priority(30)]

  // =========================================================================
  // Case 6: multisig, is_initialized returns Err
  //         => assert result == Err(InvalidAccountData)
  // =========================================================================
  // Pass: result matches Err(InvalidAccountData)
  rule [inner-validate-owner-multisig-invalid-data]:
    <k> #validateOwnerResult(
            EXPECTED_OWNER,
            PAccountMultisig(PAcc(_,_,_,_,_, OWNER_KEY, OWNER_OF_ACCOUNT, _, _), _),
            _,
            Aggregate(variantIdx(1), ListItem(
              Aggregate(variantIdx(1), ListItem(
                Aggregate(variantIdx(3), .List))))),   // Some(Err(InvalidAccountData))
            Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(3), .List))) #as RESULT,
            DEST, TARGET)
      => #setLocalValue(DEST, RESULT) ~> #continueAt(TARGET)
    </k>
    requires EXPECTED_OWNER ==K fromKey(OWNER_KEY)
     andBool OWNER_OF_ACCOUNT ==K #programIdKey
    [priority(30)]

  // Fail: result does not match Err(InvalidAccountData)
  rule [inner-validate-owner-multisig-invalid-data-fail]:
    <k> #validateOwnerResult(
            EXPECTED_OWNER,
            PAccountMultisig(PAcc(_,_,_,_,_, OWNER_KEY, OWNER_OF_ACCOUNT, _, _), _),
            _,
            Aggregate(variantIdx(1), ListItem(
              Aggregate(variantIdx(1), ListItem(
                Aggregate(variantIdx(3), .List))))),   // Some(Err(InvalidAccountData))
            RESULT:Value,
            _DEST, _TARGET)
      => #ValidateOwnerAssertFailed(Result2String(RESULT) +String " =/= " +String Result2String(Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(3), .List)))))
    </k>
    requires EXPECTED_OWNER ==K fromKey(OWNER_KEY)
     andBool OWNER_OF_ACCOUNT ==K #programIdKey
     andBool RESULT =/=K Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(3), .List)))
    [priority(30)]

  // =========================================================================
  // Case 7: multisig, is_initialized returns Ok(false)
  //         => assert result == Err(UninitializedAccount)
  // =========================================================================
  // Pass: result matches Err(UninitializedAccount)
  rule [inner-validate-owner-multisig-uninitialized]:
    <k> #validateOwnerResult(
            EXPECTED_OWNER,
            PAccountMultisig(PAcc(_,_,_,_,_, OWNER_KEY, OWNER_OF_ACCOUNT, _, _), _),
            _,
            Aggregate(variantIdx(1), ListItem(
              Aggregate(variantIdx(0), ListItem(
                BoolVal(false))))),                    // Some(Ok(false))
            Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(9), .List))) #as RESULT,
            DEST, TARGET)
      => #setLocalValue(DEST, RESULT) ~> #continueAt(TARGET)
    </k>
    requires EXPECTED_OWNER ==K fromKey(OWNER_KEY)
     andBool OWNER_OF_ACCOUNT ==K #programIdKey
    [priority(30)]

  // Fail: result does not match Err(UninitializedAccount)
  rule [inner-validate-owner-multisig-uninitialized-fail]:
    <k> #validateOwnerResult(
            EXPECTED_OWNER,
            PAccountMultisig(PAcc(_,_,_,_,_, OWNER_KEY, OWNER_OF_ACCOUNT, _, _), _),
            _,
            Aggregate(variantIdx(1), ListItem(
              Aggregate(variantIdx(0), ListItem(
                BoolVal(false))))),                    // Some(Ok(false))
            RESULT:Value,
            _DEST, _TARGET)
      => #ValidateOwnerAssertFailed(Result2String(RESULT) +String " =/= " +String Result2String(Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(9), .List)))))
    </k>
    requires EXPECTED_OWNER ==K fromKey(OWNER_KEY)
     andBool OWNER_OF_ACCOUNT ==K #programIdKey
     andBool RESULT =/=K Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(9), .List)))
    [priority(30)]

  // =========================================================================
  // Multisig signer-checking (Cases 8-10)
  // Uses generic list-based #unsignedExists and #signersCount helpers.
  // =========================================================================

  // N=3: all registered signers
  rule [inner-validate-owner-multisig-check-signers-n3]:
    <k> #validateOwnerResult(
            EXPECTED_OWNER,
            PAccountMultisig(
                PAcc(_, _, _,_,_, OWNER_KEY, OWNER_OF_ACCOUNT, _, _),
                IMulti(U8(M), U8(3), _, // N=3
                    Signers(SKEYS))),
            place(LOCAL2, PROJS2),
            Aggregate(variantIdx(1), ListItem(
              Aggregate(variantIdx(0), ListItem(
                BoolVal(true))))),                    // Some(Ok(true))
            RESULT,
            DEST, TARGET)
      => #resolveSignerCount(
            M, SKEYS,
            operandCopy(place(LOCAL2, appendP(PROJS2, projectionElemDeref .ProjectionElems))),
            place(LOCAL2, PROJS2),
            RESULT,
            DEST, TARGET)
    </k>
    requires EXPECTED_OWNER ==K fromKey(OWNER_KEY)
     andBool OWNER_OF_ACCOUNT ==K #programIdKey
    [priority(30)]

  // N=2: first 2 registered signers
  rule [inner-validate-owner-multisig-check-signers-n2]:
    <k> #validateOwnerResult(
            EXPECTED_OWNER,
            PAccountMultisig(
                PAcc(_, _, _,_,_, OWNER_KEY, OWNER_OF_ACCOUNT, _, _),
                IMulti(U8(M), U8(2), _, // N=2
                    Signers(SKEYS))),
            place(LOCAL2, PROJS2),
            Aggregate(variantIdx(1), ListItem(
              Aggregate(variantIdx(0), ListItem(
                BoolVal(true))))),                    // Some(Ok(true))
            RESULT,
            DEST, TARGET)
      => #resolveSignerCount(
            M, firstN(2, SKEYS),
            operandCopy(place(LOCAL2, appendP(PROJS2, projectionElemDeref .ProjectionElems))),
            place(LOCAL2, PROJS2),
            RESULT,
            DEST, TARGET)
    </k>
    requires EXPECTED_OWNER ==K fromKey(OWNER_KEY)
     andBool OWNER_OF_ACCOUNT ==K #programIdKey
    [priority(30)]

  // N=1: first registered signer only
  rule [inner-validate-owner-multisig-check-signers-n1]:
    <k> #validateOwnerResult(
            EXPECTED_OWNER,
            PAccountMultisig(
                PAcc(_, _, _,_,_, OWNER_KEY, OWNER_OF_ACCOUNT, _, _),
                IMulti(U8(M), U8(1), _, // N=1
                    Signers(SKEYS))),
            place(LOCAL2, PROJS2),
            Aggregate(variantIdx(1), ListItem(
              Aggregate(variantIdx(0), ListItem(
                BoolVal(true))))),                    // Some(Ok(true))
            RESULT,
            DEST, TARGET)
      => #resolveSignerCount(
            M, firstN(1, SKEYS),
            operandCopy(place(LOCAL2, appendP(PROJS2, projectionElemDeref .ProjectionElems))),
            place(LOCAL2, PROJS2),
            RESULT,
            DEST, TARGET)
    </k>
    requires EXPECTED_OWNER ==K fromKey(OWNER_KEY)
     andBool OWNER_OF_ACCOUNT ==K #programIdKey
    [priority(30)]

  syntax KItem ::= #resolveSignerCount(
      Int, List,             // M, REGS (already-sliced registered keys)
      Evaluation,            // 3: deref'd slice (evaluates to array value)
      Place,                 // 4: original tx_signers Place
      Value,                 // 5: RESULT
      Place, MaybeBasicBlockIdx
    ) [seqstrict(3)]

  // Dispatch: 3 tx_signers
  rule [resolve-3-signers]:
    <k> #resolveSignerCount(
            M, REGS,
            Range(ListItem(_) ListItem(_) ListItem(_)),
            place(LOCAL2, PROJS2),
            RESULT,
            DEST, TARGET)
      => #checkSigners3(
            M, REGS,
            operandCopy(place(LOCAL2, appendP(PROJS2, #txSignerAccountProjs(0, 3)))),
            operandCopy(place(LOCAL2, appendP(PROJS2, #txSignerAccountProjs(1, 3)))),
            operandCopy(place(LOCAL2, appendP(PROJS2, #txSignerAccountProjs(2, 3)))),
            RESULT,
            DEST, TARGET)
    </k>
    [priority(30)]

  // Dispatch: 2 tx_signers
  rule [resolve-2-signers]:
    <k> #resolveSignerCount(
            M, REGS,
            Range(ListItem(_) ListItem(_)),
            place(LOCAL2, PROJS2),
            RESULT,
            DEST, TARGET)
      => #checkSigners2(
            M, REGS,
            operandCopy(place(LOCAL2, appendP(PROJS2, #txSignerAccountProjs(0, 2)))),
            operandCopy(place(LOCAL2, appendP(PROJS2, #txSignerAccountProjs(1, 2)))),
            RESULT,
            DEST, TARGET)
    </k>
    [priority(30)]

  // Dispatch: 1 tx_signer
  rule [resolve-1-signer]:
    <k> #resolveSignerCount(
            M, REGS,
            Range(ListItem(_)),
            place(LOCAL2, PROJS2),
            RESULT,
            DEST, TARGET)
      => #checkSigners1(
            M, REGS,
            operandCopy(place(LOCAL2, appendP(PROJS2, #txSignerAccountProjs(0, 1)))),
            RESULT,
            DEST, TARGET)
    </k>
    [priority(30)]

  // =========================================================================
  // 3 tx_signers: #checkSigners3
  // Uses generic list-based #unsignedExists and #signersCount helpers.
  // =========================================================================

  syntax KItem ::= #checkSigners3(
      Int, List,             // M, REGS
      Evaluation, Evaluation, Evaluation,
      Value,                 // 6: RESULT
      Place, MaybeBasicBlockIdx
    ) [seqstrict(3,4,5)]

  // Case 8: unsigned signer exists => assert result == Err(MissingRequiredSignature)
  rule [inner-validate-owner-multisig-unsigned-3]:
    <k> #checkSigners3(
            _M, REGS,
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS0, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY0) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS1, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY1) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS2, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY2) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List))) #as RESULT,
            DEST, TARGET)
      => #setLocalValue(DEST, RESULT) ~> #continueAt(TARGET)
    </k>
    requires #unsignedExists(
               ListItem(keyAndIsSigner(KEY0, IS0)) ListItem(keyAndIsSigner(KEY1, IS1)) ListItem(keyAndIsSigner(KEY2, IS2)),
               REGS)
    [priority(30)]

  rule [inner-validate-owner-multisig-unsigned-3-fail]:
    <k> #checkSigners3(
            _M, REGS,
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS0, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY0) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS1, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY1) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS2, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY2) ListItem(_) ListItem(_) ListItem(_)),
            RESULT,
            _DEST, _TARGET)
      => #ValidateOwnerAssertFailed(Result2String(RESULT) +String " =/= " +String Result2String(Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))))
    </k>
    requires #unsignedExists(
               ListItem(keyAndIsSigner(KEY0, IS0)) ListItem(keyAndIsSigner(KEY1, IS1)) ListItem(keyAndIsSigner(KEY2, IS2)),
               REGS)
     andBool RESULT =/=K Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))
    [priority(30)]

  // Case 9: not enough signers => assert result == Err(MissingRequiredSignature)
  rule [inner-validate-owner-multisig-not-enough-3]:
    <k> #checkSigners3(
            M, REGS,
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS0, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY0) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS1, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY1) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS2, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY2) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List))) #as RESULT,
            DEST, TARGET)
      => #setLocalValue(DEST, RESULT) ~> #continueAt(TARGET)
    </k>
    requires notBool #unsignedExists(
               ListItem(keyAndIsSigner(KEY0, IS0)) ListItem(keyAndIsSigner(KEY1, IS1)) ListItem(keyAndIsSigner(KEY2, IS2)),
               REGS)
     andBool #signersCount(
               ListItem(keyAndIsSigner(KEY0, IS0)) ListItem(keyAndIsSigner(KEY1, IS1)) ListItem(keyAndIsSigner(KEY2, IS2)),
               REGS) <Int M
    [priority(30)]

  rule [inner-validate-owner-multisig-not-enough-3-fail]:
    <k> #checkSigners3(
            M, REGS,
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS0, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY0) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS1, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY1) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS2, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY2) ListItem(_) ListItem(_) ListItem(_)),
            RESULT,
            _DEST, _TARGET)
      => #ValidateOwnerAssertFailed(Result2String(RESULT) +String " =/= " +String Result2String(Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))))
    </k>
    requires notBool #unsignedExists(
               ListItem(keyAndIsSigner(KEY0, IS0)) ListItem(keyAndIsSigner(KEY1, IS1)) ListItem(keyAndIsSigner(KEY2, IS2)),
               REGS)
     andBool #signersCount(
               ListItem(keyAndIsSigner(KEY0, IS0)) ListItem(keyAndIsSigner(KEY1, IS1)) ListItem(keyAndIsSigner(KEY2, IS2)),
               REGS) <Int M
     andBool RESULT =/=K Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))
    [priority(30)]

  // Case 10: enough signers => Ok(()) (no assert on result)
  rule [inner-validate-owner-multisig-ok-3]:
    <k> #checkSigners3(
            M, REGS,
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS0, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY0) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS1, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY1) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS2, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY2) ListItem(_) ListItem(_) ListItem(_)),
            _RESULT,
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(Aggregate(variantIdx(0), .List)))) ~> #continueAt(TARGET)  // Ok(())
    </k>
    requires notBool #unsignedExists(
               ListItem(keyAndIsSigner(KEY0, IS0)) ListItem(keyAndIsSigner(KEY1, IS1)) ListItem(keyAndIsSigner(KEY2, IS2)),
               REGS)
     andBool #signersCount(
               ListItem(keyAndIsSigner(KEY0, IS0)) ListItem(keyAndIsSigner(KEY1, IS1)) ListItem(keyAndIsSigner(KEY2, IS2)),
               REGS) >=Int M
    [priority(30)]

  // --- 2 tx_signers ---

  syntax KItem ::= #checkSigners2(
      Int, List,             // M, REGS
      Evaluation, Evaluation,
      Value,                 // 5: RESULT
      Place, MaybeBasicBlockIdx
    ) [seqstrict(3,4)]

  rule [inner-validate-owner-multisig-unsigned-2]:
    <k> #checkSigners2(
            _M, REGS,
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS0, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY0) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS1, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY1) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List))) #as RESULT,
            DEST, TARGET)
      => #setLocalValue(DEST, RESULT) ~> #continueAt(TARGET)
    </k>
    requires #unsignedExists(
               ListItem(keyAndIsSigner(KEY0, IS0)) ListItem(keyAndIsSigner(KEY1, IS1)),
               REGS)
    [priority(30)]

  rule [inner-validate-owner-multisig-unsigned-2-fail]:
    <k> #checkSigners2(
            _M, REGS,
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS0, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY0) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS1, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY1) ListItem(_) ListItem(_) ListItem(_)),
            RESULT, _DEST, _TARGET)
      => #ValidateOwnerAssertFailed(Result2String(RESULT) +String " =/= " +String Result2String(Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))))
    </k>
    requires #unsignedExists(
               ListItem(keyAndIsSigner(KEY0, IS0)) ListItem(keyAndIsSigner(KEY1, IS1)),
               REGS)
     andBool RESULT =/=K Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))
    [priority(30)]

  rule [inner-validate-owner-multisig-not-enough-2]:
    <k> #checkSigners2(
            M, REGS,
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS0, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY0) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS1, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY1) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List))) #as RESULT,
            DEST, TARGET)
      => #setLocalValue(DEST, RESULT) ~> #continueAt(TARGET)
    </k>
    requires notBool #unsignedExists(
               ListItem(keyAndIsSigner(KEY0, IS0)) ListItem(keyAndIsSigner(KEY1, IS1)),
               REGS)
     andBool #signersCount(
               ListItem(keyAndIsSigner(KEY0, IS0)) ListItem(keyAndIsSigner(KEY1, IS1)),
               REGS) <Int M
    [priority(30)]

  rule [inner-validate-owner-multisig-not-enough-2-fail]:
    <k> #checkSigners2(
            M, REGS,
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS0, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY0) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS1, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY1) ListItem(_) ListItem(_) ListItem(_)),
            RESULT, _DEST, _TARGET)
      => #ValidateOwnerAssertFailed(Result2String(RESULT) +String " =/= " +String Result2String(Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))))
    </k>
    requires notBool #unsignedExists(
               ListItem(keyAndIsSigner(KEY0, IS0)) ListItem(keyAndIsSigner(KEY1, IS1)),
               REGS)
     andBool #signersCount(
               ListItem(keyAndIsSigner(KEY0, IS0)) ListItem(keyAndIsSigner(KEY1, IS1)),
               REGS) <Int M
     andBool RESULT =/=K Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))
    [priority(30)]

  rule [inner-validate-owner-multisig-ok-2]:
    <k> #checkSigners2(
            M, REGS,
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS0, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY0) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS1, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY1) ListItem(_) ListItem(_) ListItem(_)),
            _RESULT, DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(Aggregate(variantIdx(0), .List)))) ~> #continueAt(TARGET)
    </k>
    requires notBool #unsignedExists(
               ListItem(keyAndIsSigner(KEY0, IS0)) ListItem(keyAndIsSigner(KEY1, IS1)),
               REGS)
     andBool #signersCount(
               ListItem(keyAndIsSigner(KEY0, IS0)) ListItem(keyAndIsSigner(KEY1, IS1)),
               REGS) >=Int M
    [priority(30)]

  // --- 1 tx_signer ---

  syntax KItem ::= #checkSigners1(
      Int, List,             // M, REGS
      Evaluation,
      Value,                 // 4: RESULT
      Place, MaybeBasicBlockIdx
    ) [seqstrict(3)]

  rule [inner-validate-owner-multisig-unsigned-1]:
    <k> #checkSigners1(
            _M, REGS,
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS0, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY0) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List))) #as RESULT,
            DEST, TARGET)
      => #setLocalValue(DEST, RESULT) ~> #continueAt(TARGET)
    </k>
    requires #unsignedExists(
               ListItem(keyAndIsSigner(KEY0, IS0)),
               REGS)
    [priority(30)]

  rule [inner-validate-owner-multisig-unsigned-1-fail]:
    <k> #checkSigners1(
            _M, REGS,
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS0, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY0) ListItem(_) ListItem(_) ListItem(_)),
            RESULT, _DEST, _TARGET)
      => #ValidateOwnerAssertFailed(Result2String(RESULT) +String " =/= " +String Result2String(Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))))
    </k>
    requires #unsignedExists(
               ListItem(keyAndIsSigner(KEY0, IS0)),
               REGS)
     andBool RESULT =/=K Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))
    [priority(30)]

  rule [inner-validate-owner-multisig-not-enough-1]:
    <k> #checkSigners1(
            M, REGS,
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS0, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY0) ListItem(_) ListItem(_) ListItem(_)),
            Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List))) #as RESULT,
            DEST, TARGET)
      => #setLocalValue(DEST, RESULT) ~> #continueAt(TARGET)
    </k>
    requires notBool #unsignedExists(
               ListItem(keyAndIsSigner(KEY0, IS0)),
               REGS)
     andBool #signersCount(
               ListItem(keyAndIsSigner(KEY0, IS0)),
               REGS) <Int M
    [priority(30)]

  rule [inner-validate-owner-multisig-not-enough-1-fail]:
    <k> #checkSigners1(
            M, REGS,
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS0, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY0) ListItem(_) ListItem(_) ListItem(_)),
            RESULT, _DEST, _TARGET)
      => #ValidateOwnerAssertFailed(Result2String(RESULT) +String " =/= " +String Result2String(Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))))
    </k>
    requires notBool #unsignedExists(
               ListItem(keyAndIsSigner(KEY0, IS0)),
               REGS)
     andBool #signersCount(
               ListItem(keyAndIsSigner(KEY0, IS0)),
               REGS) <Int M
     andBool RESULT =/=K Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))
    [priority(30)]

  rule [inner-validate-owner-multisig-ok-1]:
    <k> #checkSigners1(
            M, REGS,
            Aggregate(variantIdx(0), ListItem(_) ListItem(Integer(IS0, 8, false)) ListItem(_) ListItem(_) ListItem(_) ListItem(KEY0) ListItem(_) ListItem(_) ListItem(_)),
            _RESULT, DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(Aggregate(variantIdx(0), .List)))) ~> #continueAt(TARGET)
    </k>
    requires notBool #unsignedExists(
               ListItem(keyAndIsSigner(KEY0, IS0)),
               REGS)
     andBool #signersCount(
               ListItem(keyAndIsSigner(KEY0, IS0)),
               REGS) >=Int M
    [priority(30)]

endmodule
