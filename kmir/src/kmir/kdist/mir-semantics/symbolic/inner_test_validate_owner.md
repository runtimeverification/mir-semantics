# Lemma rules for `expected_validate_owner_result` and `inner_test_validate_owner`

## Overview

These lemma modules summarize two functions from the test harness
(`specs/shared/inner_test_validate_owner.rs`) that specify the expected behavior
of `validate_owner` in the SPL Token program. Instead of letting the K prover
symbolically execute these functions step-by-step (which produces hundreds of
splits from nested iterator loops), the lemma rules intercept each function call
and directly produce the result in a single rewrite step.

Both functions implement the same case analysis over the `validate_owner` logic.
The difference is that `expected_validate_owner_result` computes and returns the
expected `Result<(), ProgramError>`, while `inner_test_validate_owner` takes an
additional `result` parameter and asserts (`assert_eq!`) that it matches the
expected outcome at each error branch.

## Case analysis

The branching structure follows the Rust code in `expected_validate_owner_result`
(and identically in `inner_test_validate_owner`):

| Case | Condition | Result |
|------|-----------|--------|
| 1 | `expected_owner != key!(owner_account_info)` | `Err(Custom(4))` |
| 2 | owner matches, non-multisig, `!is_signer` | `Err(MissingRequiredSignature)` |
| 3 | owner matches, non-multisig, `is_signer` | `Ok(())` |
| 4 | owner matches, multisig, `owner != PROGRAM_ID`, `!is_signer` | `Err(MissingRequiredSignature)` |
| 5 | owner matches, multisig, `owner != PROGRAM_ID`, `is_signer` | `Ok(())` |
| 6 | owner matches, multisig, `owner == PROGRAM_ID`, `is_initialized()` returns `Err` | `Err(InvalidAccountData)` |
| 7 | owner matches, multisig, `owner == PROGRAM_ID`, `is_initialized()` returns `Ok(false)` | `Err(UninitializedAccount)` |
| 8 | owner matches, multisig, `owner == PROGRAM_ID`, initialized, `unsigned_exists` | `Err(MissingRequiredSignature)` |
| 9 | owner matches, multisig, `owner == PROGRAM_ID`, initialized, `!unsigned_exists`, `signers_count < m` | `Err(MissingRequiredSignature)` |
| 10 | owner matches, multisig, `owner == PROGRAM_ID`, initialized, `!unsigned_exists`, `signers_count >= m` | `Ok(())` |

Cases 1-3 apply when `maybe_multisig_is_initialised` is `None` (non-multisig
path, used by `test_validate_owner`). Case 1 also applies to the multisig path
since the owner check happens first regardless.

Cases 4-5 are the multisig fallthrough: the account was passed as a multisig
(`maybe_multisig_is_initialised` is `Some(...)`) but its `owner` field does not
equal `PROGRAM_ID`, so the multisig signer-checking is skipped and the code
falls through to the simple `is_signer` check.

Cases 6-7 are multisig early exits based on the `is_initialized()` result
(which comes from the `is_initialized` field of the `Multisig` struct: 0 means
`Ok(false)`, 1 means `Ok(true)`, anything else means `Err(InvalidAccountData)`).

Cases 8-10 are the multisig signer-checking phase, which involves two nested
loops over tx_signers (transaction signer accounts from the input array) and
`multisig.signers[0..n]` (the first `n` registered signer keys). The loop
nesting order differs between the two checks:

- **`unsigned_exists`** (case 8): outer loop over tx_signers, inner loop over
  registered keys. True if any tx_signer matches a registered key but has
  `is_signer == false`.
- **`signers_count`** (cases 9-10): outer loop over registered keys, inner loop
  over tx_signers. Counts how many registered keys have a matching signed
  tx_signer.

Cases 9 and 10 are only reachable when `unsigned_exists` is false (no unsigned
signer matched a registered key). Case 9 then checks if `signers_count < m`
(not enough signatures). Case 10 is the success path where
`signers_count >= m`.

## Signer-checking helpers

The signer-checking logic in cases 8-10 uses list-based helper functions
(`#unsignedExists`, `#signersCount`) that work generically over any number of
signers, rather than having separate rules for each combination of tx_signer
count and registered signer count.

The two dimensions are:
- **`n`** (registered signers, from `multisig.n`): can be 1, 2, or 3 (bounded
  by `MAX_SIGNERS = 3`). Handled by matching `U8(N)` concretely in the
  `IMulti` pattern and using `firstN(N, SKEYS)` to slice the registered keys.
- **tx_signer count** (from the test input array size): any number. Handled
  generically by manual heating/cooling rules that walk the `Range` pointer
  list, evaluate each tx_signer account one at a time, and collect the results
  into a `List`. The `#toKeyAndIsSignerList` function then extracts key and
  is_signer fields from each evaluated account. No new rules are needed when
  the tx_signer count changes.

Both values of `n` and the tx_signer count are independent — any combination is
handled.

`n` is matched concretely (not passed as a symbolic argument) because when `n`
is symbolic, `firstN` produces non-deterministic branches and a stuck node that
the prover cannot prune.

`m` (the threshold) remains symbolic throughout and is only used in the final
comparison `#signersCount(...) <Int M` / `>=Int M`.

## Heating/cooling for tx_signer evaluation

The tx_signer accounts are evaluated using manual heating/cooling rather than
`seqstrict`. This is because `seqstrict` only works on fixed positional
arguments of a syntax term, not on elements of a `List`. Manual heating/cooling
walks the `Range` pointer list, evaluates each tx_signer account one at a time
via `operandCopy`, and collects the resulting `Value`s into a `List`. This makes
the tx_signer count fully generic — no dispatch rules per count.

The tx_signer count is always concrete (it comes from the test harness array
size), unlike `n` which is symbolic. So there is no risk of non-deterministic
branching.

Each lemma module has its own heating/cooling loop (`#evalTxSignersExpected` /
`#evalTxSigners`) because the `inner_test_validate_owner` version carries an
additional `RESULT` parameter. The shared `#toKeyAndIsSignerList` function in
`VALIDATE-OWNER-COMMON` handles the extraction step separately.

## Module structure

- **`VALIDATE-OWNER-COMMON`**: shared helpers — `Result2String`, `#programIdKey`,
  `#txSignerAccountProjs`, `#bool2Int`, `firstN`, `#unsignedExists`,
  `#signersCount`, `keyAndIsSigner`, `#toKeyAndIsSignerList`.
- **`EXPECTED-VALIDATE-OWNER-RESULT-P-TOKEN-LEMMA`**: intercepts
  `expected_validate_owner_result` (4 arguments), directly returns the result.
- **`INNER-TEST-VALIDATE-OWNER-P-TOKEN-LEMMA`**: intercepts
  `inner_test_validate_owner` (5 arguments, includes `result` parameter). Error
  cases have pass/fail rule pairs; success cases return `Ok(())` without
  asserting.

## `inner_test_validate_owner` pass/fail rules

For each error case (1, 2, 4, 6, 7, 8, 9), the `inner_test_validate_owner`
lemma has two rules:
- **Pass**: the `result` argument matches the expected error value (bound with
  `#as RESULT`), so the rule returns it via `#setLocalValue(DEST, RESULT)`.
- **Fail**: the `result` argument does not match, so the rule produces
  `#ValidateOwnerAssertFailed(...)` with a diagnostic message showing the
  mismatch.

For the success cases (3, 5, 10), there is no assertion on `result` — the rule
unconditionally returns `Ok(())`, matching the Rust code which does not call
`assert_eq!` on the success path.

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
  // The heating/cooling loop collects evaluated account Values into a list,
  // then #toKeyAndIsSignerList extracts key/is_signer pairs for these helpers.
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

  syntax KeyAndIsSigner ::= keyAndIsSigner( List, Int )

  syntax List ::= firstN( Int, List ) [function, total]
  // -------------------------------------------------
  rule firstN(0, _) => .List
  rule firstN(N, ListItem(X) REST) => ListItem(X) firstN(N -Int 1, REST) requires N >Int 0
  rule firstN(_, .List) => .List [owise]

  // --- #unsignedExists: outer over tx_signers, inner over registered keys ---

  syntax Bool ::= #unsignedExists( List, List ) [function, total]
  // -----------------------------------------------------------
  rule #unsignedExists(.List, _REGS) => false
  rule #unsignedExists(ListItem(keyAndIsSigner(KEY, IS)) REST, REGS)
    => #unsignedExistsInner(KEY, IS, REGS)
    orBool #unsignedExists(REST, REGS)
  rule #unsignedExists(ListItem(_) REST, REGS)
    => #unsignedExists(REST, REGS) [owise] // to make the function total

  syntax Bool ::= #unsignedExistsInner( List, Int, List ) [function, total]
  // -----------------------------------------------------------------------
  rule #unsignedExistsInner(_KEY, _IS, .List) => false
  rule #unsignedExistsInner(KEY, IS, ListItem(Key(SKEY)) REST)
    => ( IS ==Int 0 andBool SKEY ==K KEY )
    orBool #unsignedExistsInner(KEY, IS, REST)
  rule #unsignedExistsInner(KEY, IS, ListItem(_) REST)
    => #unsignedExistsInner(KEY, IS, REST) [owise] // to make the function total

  // --- #signersCount: outer over registered keys, inner over tx_signers ---

  syntax Int ::= #signersCount( List, List ) [function, total]
  // ---------------------------------------------------------
  rule #signersCount(_TXSIGNERS, .List) => 0
  rule #signersCount(TXSIGNERS, ListItem(SKEY) REST)
    => 1 +Int #signersCount(TXSIGNERS, REST)
    requires #signerMatchedInner(SKEY, TXSIGNERS)
  rule #signersCount(TXSIGNERS, ListItem(_) REST)
    => #signersCount(TXSIGNERS, REST)
    [owise]

  syntax Bool ::= #signerMatchedInner( Key, List ) [function, total]
  // ---------------------------------------------------------------
  rule #signerMatchedInner(_SKEY, .List) => false
  rule #signerMatchedInner(Key(SKEY), ListItem(keyAndIsSigner(KEY, IS)) REST)
    => ( SKEY ==K KEY andBool IS =/=Int 0 )
    orBool #signerMatchedInner(Key(SKEY), REST)
  rule #signerMatchedInner(_SKEY, ListItem(_OTHER) _REST) => false [owise] // to make the function total

  // =========================================================================
  // Extract key and is_signer from a list of evaluated tx_signer account
  // Values. Each account is an Aggregate with 9 fields; field 1 (0-indexed)
  // is is_signer (u8), field 5 is the account key (Range of 32 bytes).
  // =========================================================================

  syntax List ::= #toKeyAndIsSignerList( List ) [function]
  // -------------------------------------------------------------
  rule #toKeyAndIsSignerList(.List) => .List
  rule #toKeyAndIsSignerList(
      ListItem(Aggregate(variantIdx(0),
          ListItem(_) ListItem(Integer(IS, 8, false))
          ListItem(_) ListItem(_) ListItem(_)
          ListItem(Range(KEY)) ListItem(_) ListItem(_) ListItem(_)))
      REST)
    => ListItem(keyAndIsSigner(KEY, IS)) #toKeyAndIsSignerList(REST)
    [preserves-definedness]

endmodule
```

## Lemma rules for `expected_validate_owner_result`

These intercept the call to `expected_validate_owner_result` and directly
produce the return value, bypassing the function body.

```k
module EXPECTED-VALIDATE-OWNER-RESULT-P-TOKEN-LEMMA
  imports VALIDATE-OWNER-COMMON

  // =========================================================================
  // Intercept rule
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
      => #evalTxSignerAccountsExpected(
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
      => #evalTxSignerAccountsExpected(
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
      => #evalTxSignerAccountsExpected(
            M, firstN(1, SKEYS),
            operandCopy(place(LOCAL2, appendP(PROJS2, projectionElemDeref .ProjectionElems))),
            place(LOCAL2, PROJS2),
            DEST, TARGET)
    </k>
    requires EXPECTED_OWNER ==K fromKey(OWNER_KEY)
     andBool OWNER_OF_ACCOUNT ==K #programIdKey
    [priority(30)]

  // =========================================================================
  // Evaluate tx_signer accounts via manual heating/cooling.
  // Walks the Range pointer list, evaluates each tx_signer account one at a
  // time, and collects the resulting Values into a list.
  // =========================================================================

  syntax KItem ::= #evalTxSignerAccountsExpected(
      Int, List,             // M, REGS (already-sliced registered keys)
      Evaluation,            // deref'd slice (evaluates to Range value)
      Place,                 // original tx_signers Place
      Place, MaybeBasicBlockIdx
    ) [seqstrict(3)]

  // After the Range is evaluated, start the eval loop.
  rule [resolve-signers-expected-start]:
    <k> #evalTxSignerAccountsExpected(
            M, REGS,
            Range(PTRS),
            place(LOCAL2, PROJS2),
            DEST, TARGET)
      => #evalTxSignersExpected(
            M, REGS,
            0, size(PTRS),
            PTRS,
            .List,
            place(LOCAL2, PROJS2),
            DEST, TARGET)
    </k>
    [priority(30)]

  syntax KItem ::= #evalTxSignersExpected(
      Int, List,             // M, REGS
      Int, Int,              // I (current index), N (total tx_signers)
      List,                  // remaining pointers
      List,                  // accumulator of evaluated Values
      Place,                 // original tx_signers Place
      Place, MaybeBasicBlockIdx )

  syntax KItem ::= #evalTxSignersExpectedCont(
      Int, List,             // M, REGS
      Int, Int,              // I+1, N
      List,                  // remaining pointers
      List,                  // accumulator
      Place,                 // original tx_signers Place
      Place, MaybeBasicBlockIdx )

  // Heat: evaluate the I-th tx_signer account.
  rule [eval-tx-signer-expected-heat]:
    <k> #evalTxSignersExpected(
            M, REGS,
            I, N,
            ListItem(_) REST,
            ACC,
            place(LOCAL2, PROJS2),
            DEST, TARGET)
      => operandCopy(place(LOCAL2, appendP(PROJS2, #txSignerAccountProjs(I, N))))
      ~> #evalTxSignersExpectedCont(
            M, REGS,
            I +Int 1, N,
            REST,
            ACC,
            place(LOCAL2, PROJS2),
            DEST, TARGET)
    </k>
    [priority(30)]

  // Cool: collect the evaluated Value into the accumulator.
  rule [eval-tx-signer-expected-cool]:
    <k> Aggregate(variantIdx(0),
          ListItem(_) ListItem(Integer(_, 8, false))
          ListItem(_) ListItem(_) ListItem(_)
          ListItem(Range(_)) ListItem(_) ListItem(_) ListItem(_)) #as VAL:Value
      ~> #evalTxSignersExpectedCont(
            M, REGS,
            I, N,
            REST,
            ACC,
            PLACE,
            DEST, TARGET)
      => #evalTxSignersExpected(
            M, REGS,
            I, N,
            REST,
            ACC ListItem(VAL),
            PLACE,
            DEST, TARGET)
    </k>
    [priority(30)]

  // Done: all tx_signers evaluated, check signatures.
  rule [eval-tx-signers-expected-done]:
    <k> #evalTxSignersExpected(
            M, REGS,
            _I, _N,
            .List,
            ACC,
            _PLACE,
            DEST, TARGET)
      => #checkSignersExpected(M, REGS, #toKeyAndIsSignerList(ACC), DEST, TARGET)
    </k>
    [priority(30), preserves-definedness] // ACC assumed to contain suitable values by construction

  // =========================================================================
  // Generic signer checking (cases 8-10) for expected_validate_owner_result.
  // =========================================================================

  syntax KItem ::= #checkSignersExpected(
      Int, List,             // M, REGS
      List,                  // tx_signers as keyAndIsSigner pairs
      Place, MaybeBasicBlockIdx )

  rule [validate-owner-expected-multisig-unsigned]:
    <k> #checkSignersExpected(_M, REGS, TXSIGNERS, DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))) ~> #continueAt(TARGET)  // Err(MissingRequiredSignature)
    </k>
    requires #unsignedExists(TXSIGNERS, REGS)
    [priority(30)]

  rule [validate-owner-expected-multisig-not-enough]:
    <k> #checkSignersExpected(M, REGS, TXSIGNERS, DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))) ~> #continueAt(TARGET)  // Err(MissingRequiredSignature)
    </k>
    requires notBool #unsignedExists(TXSIGNERS, REGS)
     andBool #signersCount(TXSIGNERS, REGS) <Int M
    [priority(30)]

  rule [validate-owner-expected-multisig-ok]:
    <k> #checkSignersExpected(M, REGS, TXSIGNERS, DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(Aggregate(variantIdx(0), .List)))) ~> #continueAt(TARGET)  // Ok(())
    </k>
    requires notBool #unsignedExists(TXSIGNERS, REGS)
     andBool #signersCount(TXSIGNERS, REGS) >=Int M
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
  // Intercept rule
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
      => #evalTxSignerAccounts(
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
      => #evalTxSignerAccounts(
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
      => #evalTxSignerAccounts(
            M, firstN(1, SKEYS),
            operandCopy(place(LOCAL2, appendP(PROJS2, projectionElemDeref .ProjectionElems))),
            place(LOCAL2, PROJS2),
            RESULT,
            DEST, TARGET)
    </k>
    requires EXPECTED_OWNER ==K fromKey(OWNER_KEY)
     andBool OWNER_OF_ACCOUNT ==K #programIdKey
    [priority(30)]

  // =========================================================================
  // Evaluate tx_signer accounts via manual heating/cooling.
  // Same structure as the Expected module, but carries RESULT for assertions.
  // =========================================================================

  syntax KItem ::= #evalTxSignerAccounts(
      Int, List,             // M, REGS (already-sliced registered keys)
      Evaluation,            // deref'd slice (evaluates to Range value)
      Place,                 // original tx_signers Place
      Value,                 // RESULT
      Place, MaybeBasicBlockIdx
    ) [seqstrict(3)]

  // After the Range is evaluated, start the eval loop.
  rule [resolve-signers-start]:
    <k> #evalTxSignerAccounts(
            M, REGS,
            Range(PTRS),
            place(LOCAL2, PROJS2),
            RESULT,
            DEST, TARGET)
      => #evalTxSigners(
            M, REGS,
            0, size(PTRS),
            PTRS,
            .List,
            place(LOCAL2, PROJS2),
            RESULT,
            DEST, TARGET)
    </k>
    [priority(30)]

  syntax KItem ::= #evalTxSigners(
      Int, List,             // M, REGS
      Int, Int,              // I (current index), N (total tx_signers)
      List,                  // remaining pointers
      List,                  // accumulator of evaluated Values
      Place,                 // original tx_signers Place
      Value,                 // RESULT
      Place, MaybeBasicBlockIdx )

  syntax KItem ::= #evalTxSignersCont(
      Int, List,             // M, REGS
      Int, Int,              // I+1, N
      List,                  // remaining pointers
      List,                  // accumulator
      Place,                 // original tx_signers Place
      Value,                 // RESULT
      Place, MaybeBasicBlockIdx )

  // Heat: evaluate the I-th tx_signer account.
  rule [eval-tx-signer-heat]:
    <k> #evalTxSigners(
            M, REGS,
            I, N,
            ListItem(_) REST,
            ACC,
            place(LOCAL2, PROJS2),
            RESULT,
            DEST, TARGET)
      => operandCopy(place(LOCAL2, appendP(PROJS2, #txSignerAccountProjs(I, N))))
      ~> #evalTxSignersCont(
            M, REGS,
            I +Int 1, N,
            REST,
            ACC,
            place(LOCAL2, PROJS2),
            RESULT,
            DEST, TARGET)
    </k>
    [priority(30)]

  // Cool: collect the evaluated Value into the accumulator.
  rule [eval-tx-signer-cool]:
    <k> Aggregate(variantIdx(0),
          ListItem(_) ListItem(Integer(_, 8, false))
          ListItem(_) ListItem(_) ListItem(_)
          ListItem(Range(_)) ListItem(_) ListItem(_) ListItem(_)) #as VAL:Value
      ~> #evalTxSignersCont(
            M, REGS,
            I, N,
            REST,
            ACC,
            PLACE,
            RESULT,
            DEST, TARGET)
      => #evalTxSigners(
            M, REGS,
            I, N,
            REST,
            ACC ListItem(VAL),
            PLACE,
            RESULT,
            DEST, TARGET)
    </k>
    [priority(30)]

  // Done: all tx_signers evaluated, check signatures.
  rule [eval-tx-signers-done]:
    <k> #evalTxSigners(
            M, REGS,
            _I, _N,
            .List,
            ACC,
            _PLACE,
            RESULT,
            DEST, TARGET)
      => #checkSigners(M, REGS, #toKeyAndIsSignerList(ACC), RESULT, DEST, TARGET)
    </k>
    [priority(30), preserves-definedness] // ACC assumed to contain suitable values by construction

  // =========================================================================
  // Generic signer checking (cases 8-10) for inner_test_validate_owner.
  // Each case has pass/fail rule pairs for the assert_eq! check.
  // =========================================================================

  syntax KItem ::= #checkSigners(
      Int, List,             // M, REGS
      List,                  // tx_signers as keyAndIsSigner pairs
      Value,                 // RESULT
      Place, MaybeBasicBlockIdx )

  // Case 8: unsigned signer exists => assert result == Err(MissingRequiredSignature)
  rule [inner-validate-owner-multisig-unsigned]:
    <k> #checkSigners(
            _M, REGS, TXSIGNERS,
            Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List))) #as RESULT,
            DEST, TARGET)
      => #setLocalValue(DEST, RESULT) ~> #continueAt(TARGET)
    </k>
    requires #unsignedExists(TXSIGNERS, REGS)
    [priority(30)]

  rule [inner-validate-owner-multisig-unsigned-fail]:
    <k> #checkSigners(
            _M, REGS, TXSIGNERS,
            RESULT,
            _DEST, _TARGET)
      => #ValidateOwnerAssertFailed(Result2String(RESULT) +String " =/= " +String Result2String(Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))))
    </k>
    requires #unsignedExists(TXSIGNERS, REGS)
     andBool RESULT =/=K Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))
    [priority(30)]

  // Case 9: not enough signers => assert result == Err(MissingRequiredSignature)
  rule [inner-validate-owner-multisig-not-enough]:
    <k> #checkSigners(
            M, REGS, TXSIGNERS,
            Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List))) #as RESULT,
            DEST, TARGET)
      => #setLocalValue(DEST, RESULT) ~> #continueAt(TARGET)
    </k>
    requires notBool #unsignedExists(TXSIGNERS, REGS)
     andBool #signersCount(TXSIGNERS, REGS) <Int M
    [priority(30)]

  rule [inner-validate-owner-multisig-not-enough-fail]:
    <k> #checkSigners(
            M, REGS, TXSIGNERS,
            RESULT,
            _DEST, _TARGET)
      => #ValidateOwnerAssertFailed(Result2String(RESULT) +String " =/= " +String Result2String(Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))))
    </k>
    requires notBool #unsignedExists(TXSIGNERS, REGS)
     andBool #signersCount(TXSIGNERS, REGS) <Int M
     andBool RESULT =/=K Aggregate(variantIdx(1), ListItem(Aggregate(variantIdx(7), .List)))
    [priority(30)]

  // Case 10: enough signers => Ok(()) (no assert on result)
  rule [inner-validate-owner-multisig-ok]:
    <k> #checkSigners(
            M, REGS, TXSIGNERS,
            _RESULT,
            DEST, TARGET)
      => #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(Aggregate(variantIdx(0), .List)))) ~> #continueAt(TARGET)  // Ok(())
    </k>
    requires notBool #unsignedExists(TXSIGNERS, REGS)
     andBool #signersCount(TXSIGNERS, REGS) >=Int M
    [priority(30)]

endmodule
