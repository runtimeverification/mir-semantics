```k
requires "../kmir-ast.md"
requires "../rt/data.md"
requires "../kmir.md"
requires "../rt/configuration.md"
```

This module provides specialised data types and associated access rules
for data used by the p-token contract and its operations.

```k
module KMIR-P-TOKEN
  imports TYPES
  imports BODY
  imports RT-DATA
  imports KMIR-CONTROL-FLOW
```

## Special-purpose types for P-token

The `pinocchio::account_info::AccountInfo` type contains a (mutable) pointer to a `pinocchio::account_info::Account`.
However, in practice the pointed-at memory is assumed to contain additional data _after_ this `Account`.
The additional data is commonly an instance of `Transmutable` (assumed here), which limits the choices to 3 structs:
- `pinocchio_token_interface::state::Account`, modelled as sort `IAcc`;
- `pinocchio_token_interface::state::Mint`, modelled as sort `IMint`;
- `pinocchio_token_interface::state::Multisig`, modelled as sort `IMulti`.

A fourth kind of struct following the `Account` can be a "rent sysvar".
The `Rent` sysvar holds constants that determine whether or not rent has to be paid for account storage.

We model this special assumption through a special subsort of `Value` with rules to create and access the contained inner structure as an aggregate of its own.

```k
  syntax Value ::= PAccount

  syntax PAccount ::=
      PAccountAccount( PAcc , IAcc )    // p::Account and iface::Account structs
    | PAccountMint( PAcc , IMint )      // p::Account and iface::Mint structs
    // | PAccountMultisig( PAcc , IMulti ) // p::Account and iface::Multisig structs
    | PAccountRent ( PAcc, PRent )      // p::Account and p::sysvars::rent::Rent

  syntax PAccount2nd ::= IAcc | IMint | PRent // all sorts that can be 2nd component
```

### Pinocchio Account

The `pinocchio::account_info::Account` type is the first "component" of the special data structure.
It is modelled as a `PAcc` sort in K.
The code uses some helper sorts for better readability.

```k
  // pinocchio Account structure
  syntax PAcc ::= PAcc ( U8, U8, U8, U8, I32, Key, Key , U64, U64)
                | PAccError ( Value )

  syntax PAcc ::= #toPAcc ( Value ) [function, total]
  // -------------------------------------------------------
  rule #toPAcc(
        Aggregate(variantIdx(0),
                  ListItem(Integer(A, 8, false))  // borrow_state (custom solution to manage read/write borrows)
                  ListItem(Integer(B, 8, false))  // is_signer (comment: whether transaction was signed by this account)
                  ListItem(Integer(C, 8, false))  // is_writable
                  ListItem(Integer(D, 8, false))  // executable (comment: whether this account represents a program)
                  ListItem(Integer(E, 32, true))  // resize_delta (comment: "guaranteed to be zero at start")
                  ListItem(KEY1BYTES)             // account key
                  ListItem(KEY2BYTES)             // owner key
                  ListItem(Integer(X, 64, false)) // lamports
                  ListItem(Integer(Y, 64, false)) // data_len (dependent on 2nd component, must be ensured)
        ))
      =>
       PAcc (U8(A), U8(B), U8(C), U8(D), I32(E), toKey(KEY1BYTES), toKey(KEY2BYTES), U64(X), U64(Y))
  rule #toPAcc(OTHER) => PAccError(OTHER) [owise]


  syntax Value ::= #fromPAcc ( PAcc ) [function, total]
  // -----------------------------------------------------------
  rule #fromPAcc(PAcc (U8(A), U8(B), U8(C), U8(D), I32(E), KEY1, KEY2, U64(X), U64(Y)))
      =>
        Aggregate(variantIdx(0),
                  ListItem(Integer(A, 8, false))
                  ListItem(Integer(B, 8, false))
                  ListItem(Integer(C, 8, false))
                  ListItem(Integer(D, 8, false))
                  ListItem(Integer(E, 32, true))
                  ListItem(fromKey(KEY1))
                  ListItem(fromKey(KEY2))
                  ListItem(Integer(X, 64, false))
                  ListItem(Integer(Y, 64, false))
        )
  rule #fromPAcc(PAccError(OTHER)) => OTHER

  rule #toPAcc(#fromPAcc(PACC)) => PACC [simplification, preserves-definedness]
  rule #fromPAcc(#toPAcc(PACC)) => PACC [simplification, preserves-definedness]

  syntax U8 ::= U8( Int )
  syntax I32 ::= I32 ( Int )
  syntax U64 ::= U64 ( Int )

  syntax Key ::= Key( List ) // 32 bytes
               | KeyError ( Value )

  syntax Key ::= toKey ( Value ) [function, total]
  // -----------------------------------------------------------
  rule toKey(Range(ELEMS)) => Key( ELEMS ) requires size(ELEMS) ==Int 32 andBool allBytes(ELEMS) [preserves-definedness]
  rule toKey(VAL) => KeyError(VAL) [owise]

  syntax Bool ::= allBytes ( List ) [function, total]
  // ------------------------------------------------
  rule allBytes(.List) => true
  rule allBytes( ListItem(Integer(_, 8, false)) REST:List) => allBytes(REST)
  rule allBytes( ListItem(_OTHER) _:List) => false [owise]

  syntax Value ::= fromKey ( Key ) [function, total]
  // -----------------------------------------------------------
  // We assume that the Key always contains valid data, because it is constructed via toKey.
  rule fromKey(KeyError(VAL)) => VAL
  rule fromKey(Key(VAL))      => Range(VAL) [preserves-definedness]
```

### SPL Token Interface Account

```k
  // interface account structure
  syntax IAcc ::= IAcc ( Key, Key, Amount, Flag, Key, U8, Flag, Amount, Amount, Flag, Key )

  // fromIAcc function to create an Aggregate, used when dereferencing the data pointer
  syntax Value ::= #fromIAcc ( IAcc ) [function, total]
  // --------------------------------------------------
  rule #fromIAcc(IAcc(MINT, OWNER, AMT, DLG_FLAG, DLG_KEY, U8(STATE), NATIVE_FLAG, NATIVE_AMT, DLG_AMT, CLOSE_FLAG, CLOSE_KEY))
    =>
      Aggregate(variantIdx(0),
                ListItem(fromKey(MINT))
                ListItem(fromKey(OWNER))
                ListItem(fromAmount(AMT))
                ListItem(Aggregate(variantIdx(0), ListItem(fromFlag(DLG_FLAG)) ListItem(fromKey(DLG_KEY))))
                ListItem(Integer(STATE, 8, false))
                ListItem(fromFlag(NATIVE_FLAG))
                ListItem(fromAmount(NATIVE_AMT))
                ListItem(fromAmount(DLG_AMT))
                ListItem(Aggregate(variantIdx(0), ListItem(fromFlag(CLOSE_FLAG)) ListItem(fromKey(CLOSE_KEY))))
      )

  syntax IAcc ::= #toIAcc ( Value ) [function]
  // --------------------------------------------------
  rule #toIAcc(
          Aggregate(variantIdx(0),
                ListItem(MINT)
                ListItem(OWNER)
                ListItem(AMT)
                ListItem(Aggregate(variantIdx(0), ListItem(DLG_FLAG) ListItem(DLG_KEY)))
                ListItem(Integer(STATE, 8, false))
                ListItem(NATIVE_FLAG)
                ListItem(NATIVE_AMT)
                ListItem(DLG_AMT)
                ListItem(Aggregate(variantIdx(0), ListItem(CLOSE_FLAG) ListItem(CLOSE_KEY)))
          )
        )
      => IAcc(toKey(MINT),
              toKey(OWNER),
              toAmount(AMT),
              toFlag(DLG_FLAG),
              toKey(DLG_KEY),
              U8(STATE),
              toFlag(NATIVE_FLAG),
              toAmount(NATIVE_AMT),
              toAmount(DLG_AMT),
              toFlag(CLOSE_FLAG),
              toKey(CLOSE_KEY)
          )

  rule #toIAcc(#fromIAcc(IACC)) => IACC [simplification, preserves-definedness]
  rule #fromIAcc(#toIAcc(VAL)) => VAL   [simplification]

  syntax Amount ::= Amount(Int) // 8 bytes , but model as u64. From = LE bytes , to = decode(LE)
                  | AmountError( Value )

  syntax Amount ::= toAmount ( Value) [function, total]
  // -----------------------------------------------------------
  rule toAmount(Range(AMOUNTBYTES)) => Amount(Bytes2Int(#bytesFrom(AMOUNTBYTES), LE, Unsigned))
    requires allBytes(AMOUNTBYTES) andBool size(AMOUNTBYTES) ==Int 8 [preserves-definedness]
  rule toAmount(OTHER) => AmountError(OTHER) [owise]

  syntax Bytes ::= #bytesFrom ( List ) [function]
  // --------------------------------------------
  rule #bytesFrom(.List) => .Bytes
  rule #bytesFrom(ListItem(Integer(X, 8, false)) REST) => Int2Bytes(1, X, LE) +Bytes #bytesFrom(REST)

  syntax Value ::= fromAmount ( Amount ) [function, total]
  // -----------------------------------------------------------
  rule fromAmount(Amount(X)) => Range(#asU8s(X)) [preserves-definedness]
  rule fromAmount(AmountError(VAL)) => VAL

  syntax List ::= #asU8s ( Int )            [function]
                | #asU8List ( List , Int ) [function]
  // -------------------------------------
  rule #asU8s(X) => #asU8List(.List, X)
  rule #asU8List(ACC, _) => ACC requires 8 <=Int size(ACC) [priority(40)] // always cut at 8 bytes
  rule #asU8List(ACC, X) => #asU8List( ACC ListItem(Integer( X &Int 255, 8, false)) , X >>Int 8) [preserves-definedness]

  rule toAmount(fromAmount(AMT)) => AMT [simplification, preserves-definedness]
  rule fromAmount(toAmount(VAL)) => VAL [simplification, preserves-definedness]

  syntax Flag ::= Flag ( Int )       // 4 bytes , first byte representing bool. From = 4 bytes, to = read/check all bytes
                | FlagError ( Value ) // to make converters total, add an error constructor

  syntax Value ::= fromFlag ( Flag ) [function, total]
  // -----------------------------------------------------------
  rule fromFlag( Flag(B)) => Range(ListItem(Integer(B, 8, false)) ListItem(Integer(0, 8, false)) ListItem(Integer(0, 8, false)) ListItem(Integer(0, 8, false)))
    requires 0 <=Int B andBool B <=Int 1
  rule fromFlag( FlagError(VAL)) => VAL

  syntax Flag ::= toFlag ( Value ) [function, total]
  // -----------------------------------------------------------
  rule toFlag( Range(ListItem(Integer(X, 8, false)) REST:List)) => Flag(X)
    requires 0 <=Int X andBool X <=Int 1 andBool size(REST) ==Int 3 andBool allZeroBytes(REST)
  rule toFlag( VAL ) => FlagError(VAL) [owise]

  syntax Bool ::= allZeroBytes(List) [function, total]
  // ---------------------------------------------
  rule allZeroBytes(.List) => true
  rule allZeroBytes(ListItem(Integer(0, 8, false)) REST) => allZeroBytes(REST)
  rule allZeroBytes(ListItem(_OTHER) _:List) => false [owise]

  rule fromFlag(toFlag(VAL)) => VAL [simplification, preserves-definedness]
  rule toFlag(fromFlag(FLG)) => FLG [simplification, preserves-definedness]
```

### SPL Token Interfact Mint
```k
  // Mint struct: optional mint authority, supply, decimals, initialised flag, optional freeze authority
  syntax IMint ::= IMint ( Flag, Key , Amount , U8 , U8 , Flag , Key )

  syntax IMint ::= #toIMint ( Value ) [function]
  // ------------------------------------------
  rule #toIMint(
          Aggregate(variantIdx(0),
                ListItem(Aggregate(variantIdx(0), ListItem(MINT_AUTH_FLAG) ListItem(MINT_AUTH_KEY)))
                ListItem(SUPPLY)
                ListItem(Integer(DECIMALS, 8, false))
                ListItem(Integer(INITIALISED, 8, false))
                ListItem(Aggregate(variantIdx(0), ListItem(FREEZE_AUTH_FLAG) ListItem(FREEZE_AUTH_KEY)))
          )
        )
      => IMint(toFlag(MINT_AUTH_FLAG),
               toKey(MINT_AUTH_KEY),
               toAmount(SUPPLY),
               U8(DECIMALS),
               U8(INITIALISED),
               toFlag(FREEZE_AUTH_FLAG),
               toKey(FREEZE_AUTH_KEY)
          )

    syntax Value ::= #fromIMint ( IMint ) [function, total]
    // ----------------------------------------------------
    rule #fromIMint(IMint(MINT_AUTH_FLAG, MINT_AUTH_KEY, SUPPLY, U8(DECIMALS), U8(INITIALISED), FREEZE_AUTH_FLAG, FREEZE_AUTH_KEY))
      => Aggregate(variantIdx(0),
                   ListItem(Aggregate(variantIdx(0), ListItem(fromFlag(MINT_AUTH_FLAG)) ListItem(fromKey(MINT_AUTH_KEY))))
                   ListItem(fromAmount(SUPPLY))
                   ListItem(Integer(DECIMALS, 8, false))
                   ListItem(Integer(INITIALISED, 8, false))
                   ListItem(Aggregate(variantIdx(0), ListItem(fromFlag(FREEZE_AUTH_FLAG)) ListItem(fromKey(FREEZE_AUTH_KEY))))
          )

    rule #toIMint(#fromIMint(IMINT)) => IMINT [simplification, preserves-definedness]
    rule #fromIMint(#toIMint(IMINT)) => IMINT [simplification]
```
### Pinocchio Rent sysvar

```k
  syntax F64 ::= F64 ( Float )

  syntax PRent ::= PRent ( U64, F64 , U8 )
                 | PRentError ( Value )

  syntax PRent ::= #toPRent ( Value ) [function, total]
  // --------------------------------------------------
  rule #toPRent(
          Aggregate(variantIdx(0),
                  ListItem(Integer(LMP_PER_BYTEYEAR, 64, false))
                  ListItem(Float(EXEMPT_THRESHOLD, 64))
                  ListItem(Integer(BURN_PCT, 8, false))
          )
        ) => PRent(U64(LMP_PER_BYTEYEAR), F64(EXEMPT_THRESHOLD), U8(BURN_PCT))
  rule #toPRent(VAL) => PRentError(VAL) [owise]

  syntax Value ::= #fromPRent ( PRent ) [function, total]
  // ----------------------------------------------------
  rule #fromPRent(PRent(U64(LMP_PER_BYTEYEAR), F64(EXEMPT_THRESHOLD), U8(BURN_PCT)))
      => Aggregate(variantIdx(0),
                  ListItem(Integer(LMP_PER_BYTEYEAR, 64, false))
                  ListItem(Float(EXEMPT_THRESHOLD, 64))
                  ListItem(Integer(BURN_PCT, 8, false))
          )
  rule #fromPRent(PRentError(VAL)) => VAL

  rule #fromPRent(#toPRent(VAL)) => VAL [simplification, preserves-definedness]
  rule #toPRent(#fromPRent(RNT)) => RNT [simplification, preserves-definedness]

```


### Access to the pinocchio `Account` struct

When accessing the special value's fields, it is transformed to a normal `Aggregate` struct on the fly
in order to avoid having to encode each field access individually.

Read access will only happen in the `traverseProjection` operation (reading fields of the struct.
Write access (as well as moving reads) uses `traverseProjection` and also requires a special context node to reconstruct the custom value.

```k
  // special traverseProjection rules that call fromPAcc on demand when needed.
  // NB Only applies when more projections follow.
  rule <k> #traverseProjection(DEST, PAccountAccount(PACC, IACC), PROJ PROJS, CTXTS)
        => #traverseProjection(DEST, #fromPAcc(PACC)            , PROJ PROJS, CtxPAccountPAcc(IACC) CTXTS)
        ...
        </k>
    [priority(30)]
  rule <k> #traverseProjection(DEST, PAccountMint(PACC, IMINT), PROJ PROJS, CTXTS)
        => #traverseProjection(DEST, #fromPAcc(PACC)          , PROJ PROJS, CtxPAccountPAcc(IMINT) CTXTS)
        ...
        </k>
    [priority(30)]
  rule <k> #traverseProjection(DEST, PAccountRent(PACC, PRENT), PROJ PROJS, CTXTS)
        => #traverseProjection(DEST, #fromPAcc(PACC)          , PROJ PROJS, CtxPAccountPAcc(PRENT) CTXTS)
        ...
        </k>
    [priority(30)]

  // special context node(s) storing the second component
  syntax Context ::= CtxPAccountPAcc ( PAccount2nd )

  // restore the custom value in #buildUpdate
  rule #buildUpdate(VAL, CtxPAccountPAcc(IACC:IAcc) CTXS)
    => #buildUpdate(PAccountAccount(#toPAcc(VAL), IACC), CTXS)
    [preserves-definedness] // by construction, VAL has the correct shape from introducing the context
  rule #buildUpdate(VAL, CtxPAccountPAcc(IMINT:IMint) CTXS)
    => #buildUpdate(PAccountMint(#toPAcc(VAL), IMINT), CTXS)
    [preserves-definedness] // by construction, VAL has the correct shape from introducing the context
  rule #buildUpdate(VAL, CtxPAccountPAcc(PRENT:PRent) CTXS)
    => #buildUpdate(PAccountRent(#toPAcc(VAL), PRENT), CTXS)
    [preserves-definedness] // by construction, VAL has the correct shape from introducing the context

  // transforming PAccountAccount(PACC, _) to PACC is automatic, no projection required
  rule #projectionsFor(CtxPAccountPAcc(_) CTXTS, PROJS) => #projectionsFor(CTXTS, PROJS)

```

### Introducing the special types with a cheat code

The special values are introduced by special function calls (cheat code functions).
An `AccountInfo` reference is passed to the function.

```k
  syntax String ::= #functionName ( MonoItemKind ) [function, total]
  // ---------------------------------------------------------------
  rule #functionName(monoItemFn(symbol(NAME), _, _)) => NAME
  rule #functionName(monoItemStatic(symbol(NAME), _, _)) => NAME
  rule #functionName(monoItemGlobalAsm(_)) => "#ASM"
  rule #functionName(IntrinsicFunction(symbol(NAME))) => NAME
```

```{.k .symbolic}
  // special rule to intercept the cheat code function calls and replace them by #mkPToken<thing>
  rule [cheatcode-is-account]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(PLACE) .Operands, _DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkPTokenAccount(PLACE) ~> #execBlockIdx(TARGET)
    ...
    </k>
    <functions> FUNCTIONS </functions>
    requires #tyOfCall(FUNC) in_keys(FUNCTIONS)
     andBool isMonoItemKind(FUNCTIONS[#tyOfCall(FUNC)])
     andBool #functionName({FUNCTIONS[#tyOfCall(FUNC)]}:>MonoItemKind) ==String "pinocchio_token_program::entrypoint::cheatcode_is_account"
    [priority(30), preserves-definedness]
  rule [cheatcode-is-mint]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(PLACE) .Operands, _DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkPTokenMint(PLACE) ~> #execBlockIdx(TARGET)
    ...
    </k>
    <functions> FUNCTIONS </functions>
    requires #tyOfCall(FUNC) in_keys(FUNCTIONS)
     andBool isMonoItemKind(FUNCTIONS[#tyOfCall(FUNC)])
     andBool #functionName({FUNCTIONS[#tyOfCall(FUNC)]}:>MonoItemKind) ==String "pinocchio_token_program::entrypoint::cheatcode_is_mint"
    [priority(30), preserves-definedness]
  rule [cheatcode-is-rent]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(PLACE) .Operands, _DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkPTokenRent(PLACE) ~> #execBlockIdx(TARGET)
    ...
    </k>
    <functions> FUNCTIONS </functions>
    requires #tyOfCall(FUNC) in_keys(FUNCTIONS)
     andBool isMonoItemKind(FUNCTIONS[#tyOfCall(FUNC)])
     andBool #functionName({FUNCTIONS[#tyOfCall(FUNC)]}:>MonoItemKind) ==String "pinocchio_token_program::entrypoint::cheatcode_is_rent"
    [priority(30), preserves-definedness]

  // cheat codes and rules to create a special PTokenAccount flavour
  syntax KItem ::= #mkPTokenAccount ( Place )
                 | #mkPTokenMint ( Place )
                 | #mkPTokenRent ( Place )
                //  | #mkPTokenMultisig ( Place )

  // place assumed to be a ref to an AccountInfo, having 1 field holding a pointer to an account
  // dereference, then read and dereference pointer in field 1 to read the account data
  // modify the pointee, creating additional data (different kinds) with fresh variables
  //
  rule
    <k> #mkPTokenAccount(place(LOCAL, PROJS))
      => #setLocalValue(
            place(LOCAL, appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(0), ?HACK) projectionElemDeref .ProjectionElems)),
            #addAccount(operandCopy(place(LOCAL, appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(0), ?HACK) projectionElemDeref .ProjectionElems)))))
      ...
    </k>

  rule
    <k> #mkPTokenMint(place(LOCAL, PROJS))
      => #setLocalValue(
            place(LOCAL, appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(0), ?HACK) projectionElemDeref .ProjectionElems)),
            #addMint(operandCopy(place(LOCAL, appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(0), ?HACK) projectionElemDeref .ProjectionElems)))))
      ...
    </k>

  rule
    <k> #mkPTokenRent(place(LOCAL, PROJS))
      => #setLocalValue(
            place(LOCAL, appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(0), ?HACK) projectionElemDeref .ProjectionElems)),
            #addRent(operandCopy(place(LOCAL, appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(0), ?HACK) projectionElemDeref .ProjectionElems)))))
      ...
    </k>

  syntax Evaluation ::= #addAccount ( Evaluation )  [seqstrict()]
                      | #addMint ( Evaluation )     [seqstrict()]
                      | #addRent ( Evaluation )     [seqstrict()]
                      // | #addMultisig ( Evaluation ) [seqstrict()]

  // NB these rewrites also ensure the data_len field in PAcc is set correctly for the given data
  rule #addAccount(Aggregate(variantIdx(0), _:List ListItem(Integer(DATA_LEN, 64, false))) #as P_ACC)
      => PAccountAccount(
            #toPAcc(P_ACC),
            IAcc(Key(?MINT),
                 Key(?OWNER),
                 Amount(?AMOUNT),
                 Flag(?DELEGATEFLAG), Key(?DELEGATE),
                 U8(?STATE),
                 Flag(?NATIVEFLAG),
                 Amount(?NATIVE_AMOUNT),
                 Amount(?DELEG_AMOUNT),
                 Flag(?CLOSEFLAG), Key(?CLOSE_AUTH)
              )
          )
    ensures 0 <=Int ?STATE andBool ?STATE <Int 256
    andBool 0 <=Int ?DELEGATEFLAG andBool ?DELEGATEFLAG <=Int 1 // not allowed any other values
    andBool 0 <=Int ?NATIVEFLAG andBool ?NATIVEFLAG <=Int 1 // not allowed any other values
    andBool 0 <=Int ?CLOSEFLAG andBool ?CLOSEFLAG <=Int 1 // not allowed any other values
    andBool size(?MINT)  ==Int 32      andBool allBytes(?MINT)
    andBool size(?OWNER) ==Int 32      andBool allBytes(?OWNER)
    andBool size(?DELEGATE) ==Int 32   andBool allBytes(?DELEGATE)
    andBool size(?CLOSE_AUTH) ==Int 32 andBool allBytes(?CLOSE_AUTH)
    andBool 0 <=Int ?AMOUNT andBool ?AMOUNT <Int 1 <<Int 64
    andBool 0 <=Int ?NATIVE_AMOUNT andBool ?NATIVE_AMOUNT <Int 1 <<Int 64
    andBool 0 <=Int ?DELEG_AMOUNT andBool ?DELEG_AMOUNT <Int 1 <<Int 64
    andBool DATA_LEN ==Int 165 // size_of(Account), see pinocchio_token_interface::state::Transmutable instance

  rule #addMint(Aggregate(variantIdx(0), _:List ListItem(Integer(DATA_LEN, 64, false))) #as P_ACC)
      => PAccountMint(
            #toPAcc(P_ACC),
            IMint(Flag(?MINT_AUTH_FLAG), Key(?MINT_AUTH_KEY),
                  Amount(?SUPPLY),
                  U8(?DECIMALS),
                  U8(?INITIALISED),
                  Flag(?FREEZE_AUTH_FLAG), Key(?FREEZE_AUTH_KEY)
              )
          )
    ensures 0 <=Int ?DECIMALS andBool ?DECIMALS <Int 256
    andBool 0 <=Int ?INITIALISED andBool ?INITIALISED <=Int 1 // not allowed any other values
    andBool 0 <=Int ?MINT_AUTH_FLAG andBool ?MINT_AUTH_FLAG <=Int 1 // not allowed any other values
    andBool 0 <=Int ?FREEZE_AUTH_FLAG andBool ?FREEZE_AUTH_FLAG <=Int 1 // not allowed any other values
    andBool size(?MINT_AUTH_KEY)  ==Int 32  andBool allBytes(?MINT_AUTH_KEY)
    andBool size(?FREEZE_AUTH_KEY) ==Int 32 andBool allBytes(?FREEZE_AUTH_KEY)
    andBool 0 <=Int ?SUPPLY andBool ?SUPPLY <Int 1 <<Int 64
    andBool DATA_LEN ==Int 82 // size_of(Mint), see pinocchio_token_interface::state::Transmutable instance

  rule #addRent(Aggregate(variantIdx(0), _:List ListItem(Integer(DATA_LEN, 64, false))) #as P_ACC)
      => PAccountRent(
            #toPAcc(P_ACC),
            PRent(U64(?LMP_PER_BYTEYEAR), F64(?_EXEMPT_THRESHOLD), U8(?BURN_PCT))
          )
    ensures 0 <=Int ?LMP_PER_BYTEYEAR andBool ?LMP_PER_BYTEYEAR <Int 1 <<Int 64
    andBool 0 <=Int ?BURN_PCT andBool ?BURN_PCT <Int 256
    andBool DATA_LEN ==Int 17 // size_of(Rent), see pinocchio::sysvars::rent::Rent::LEN
```

### Establishing Access to the Second Component of a `PAccount`-sorted Value

Access to the data structure that follow a pinocchio account is usually via characteristic sequences of statements:
Code within `pinocchio` itself uses the `Transmutable` methods `load`, `load_mut` or respective `*_unchecked` variants.
- calling `borrow_data_unchecked` or `borrow_mut_data_unchecked` (returns a ref to a `[u8]` slice)
- then calling `load_unchecked` (maybe via `load`) or `load_mut_unchecked` from the desired `Transmutable` instance
  - `load_unchecked` checks the slice length and then casts the slice pointer (`slice.as_ptr`) to a `T` pointer and then a reference
  - `load` calls `load_unchecked` and then checks for initialisation data
  - both functions return the ref within a `Result::Ok`

Since the access pattern spans several function calls in sequence, we introduce
a special reference-like marker for the intermediate state where `borrow_[mut_]data_unchecked` has been performed,
which gets eliminated by the call to `load_[mut_]unchecked`.

- identify the call to `borrow_[mut_]data_unchecked`
- the (single) argument (expected to be `&AccountInfo`) is dereferenced, and its field evaluated
  - this yields a PtrLocal to the custom data structure of sort `PAccount` (not checked)
- the return value (DEST) is filled with a special reference to where the data is stored, derived from the pointer inside the `AccountInfo` struct. This value has Rust type `*const u8` or `*mut u8`.

```k
  syntax Value ::= PAccByteRef ( Int , Place , Mutability , Int )
```

The `PAccByteRef` carries a stack offset, so it must be adjusted on reads.

```k
  rule #adjustRef(PAccByteRef(HEIGHT, PLACE, MUT, LEN), OFFSET) => PAccByteRef(HEIGHT +Int OFFSET, PLACE, MUT, LEN)
```

```{.k .symbolic}
  // intercept calls to `borrow_data_unchecked` and write `PAccountRef` to destination
  rule [cheatcode-borrow-data]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(place(LOCAL, PROJS)) .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
    => #mkPAccByteRef(DEST, operandCopy(place(LOCAL, appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(0), ?_HACK) .ProjectionElems))), mutabilityNot)
      ~> #execBlockIdx(TARGET)
    ...
    </k>
    <functions> FUNCTIONS </functions>
    requires #tyOfCall(FUNC) in_keys(FUNCTIONS)
     andBool isMonoItemKind(FUNCTIONS[#tyOfCall(FUNC)])
     andBool #functionName({FUNCTIONS[#tyOfCall(FUNC)]}:>MonoItemKind) ==String "pinocchio::account_info::AccountInfo::borrow_data_unchecked"
    [priority(30), preserves-definedness]

  // intercept calls to `borrow_mut_data_unchecked` and write `PAccountRef` to destination
  rule [cheatcode-borrow-mut-data]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(place(LOCAL, PROJS)) .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
    => #mkPAccByteRef(DEST, operandCopy(place(LOCAL, appendP(PROJS, projectionElemDeref projectionElemField(fieldIdx(0), ?_HACK) .ProjectionElems))), mutabilityMut)
      ~> #execBlockIdx(TARGET)
    ...
    </k>
    <functions> FUNCTIONS </functions>
    requires #tyOfCall(FUNC) in_keys(FUNCTIONS)
     andBool isMonoItemKind(FUNCTIONS[#tyOfCall(FUNC)])
     andBool #functionName({FUNCTIONS[#tyOfCall(FUNC)]}:>MonoItemKind) ==String "pinocchio::account_info::AccountInfo::borrow_mut_data_unchecked"
    [priority(30), preserves-definedness]

  syntax KItem ::= #mkPAccByteRef( Place , Evaluation , Mutability ) [seqstrict(2)]

  // TODO additional projections not supported at the moment, assumed ref is on stack not local
  rule <k> #mkPAccByteRef(DEST, PtrLocal(OFFSET, place(LOCAL, .ProjectionElems) #as PLACE, _MUT, _EMUL), MUT)
        => #mkPAccByteRefLen(DEST, OFFSET, PLACE, MUT, #localFromFrame({STACK[OFFSET -Int 1]}:>StackFrame, LOCAL, OFFSET))
        ...
       </k>
       <stack> STACK </stack>
    requires 0 <Int OFFSET
     andBool isStackFrame(STACK[OFFSET -Int 1])
    [preserves-definedness]
```

### Length validation for inlined `from_bytes` function

The Rust `from_bytes` function is inlined and contains a length check: `if bytes.len() < Self::LEN`.
Since we intercept `from_bytes_unchecked` instead of the inlined `from_bytes`,
we need to handle the length validation ourselves.
We determine the data type (IAcc/IMint/PRent) by examining the `PAccount` value and
set an appropriate `LEN` constant in `PAccByteRef` so that `PtrMetadata` operations
(which implement `bytes.len()`) return the correct length.
The expected length is also stored inside the PAcc data structure (last field),
this field is expected to be constrained accordingly in the path condition.

```k
  syntax KItem ::= #mkPAccByteRefLen ( Place , Int , Place , Mutability , Value )
  // -------------------------------------------------------------------------------------
  rule <k> #mkPAccByteRefLen(DEST, OFFSET, PLACE, MUT, PAccountAccount(PAcc(_, _, _, _, _, _, _, _, U64(DATA_LEN)), _))
        => #setLocalValue(DEST, PAccByteRef(OFFSET, PLACE, MUT, 165))
        ...
       </k>
    requires DATA_LEN ==Int 165 // IAcc length
  rule <k> #mkPAccByteRefLen(DEST, OFFSET, PLACE, MUT, PAccountMint(PAcc(_, _, _, _, _, _, _, _, U64(DATA_LEN)), _))
        => #setLocalValue(DEST, PAccByteRef(OFFSET, PLACE, MUT, 82))
        ...
       </k>
    requires DATA_LEN ==Int 82 // IMint length
    rule <k> #mkPAccByteRefLen(DEST, OFFSET, PLACE, MUT, PAccountRent(PAcc(_, _, _, _, _, _, _, _, U64(DATA_LEN)), _))
        => #setLocalValue(DEST, PAccByteRef(OFFSET, PLACE, MUT, 17))
        ...
       </k>
    requires DATA_LEN ==Int 17 // PRent length

  // Handle PtrMetadata for PAccByteRef to return the stored length
  rule <k> #applyUnOp(unOpPtrMetadata, PAccByteRef(_, _, _, LEN)) => Integer(LEN, 64, false) ... </k>
```

This intermediate representation will be eliminated by an intercepted call to `load_[mut_]unchecked` , the
latter returning a reference to the second data structure within the `PAccount`-sorted value.
While the `PAccByteRef` is generic, the `load_*` functions are specific to the contained type (instances of `Transmutable`).
A (small) complication is that the reference is returned within a `Result` enum.
NB Both `load_unchecked` and `load_mut_unchecked` are intercepted in the same way, mutability information is already held in the `PAccountByteRef`.

```{.k .symbolic}
  // intercept calls to `load_unchecked` and `load_mut_unchecked`
  rule [cheatcode-mk-iface-account-ref]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, OPERAND .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
    => #mkPAccountRef(DEST, OPERAND, PAccountIAcc, true)
      ~> #execBlockIdx(TARGET)
    ...
    </k>
    <functions> FUNCTIONS </functions>
    requires #tyOfCall(FUNC) in_keys(FUNCTIONS)
     andBool isMonoItemKind(FUNCTIONS[#tyOfCall(FUNC)])
     andBool (
          #functionName({FUNCTIONS[#tyOfCall(FUNC)]}:>MonoItemKind) ==String "pinocchio_token_interface::state::load_unchecked::<pinocchio_token_interface::state::account::Account>"
        orBool
          #functionName({FUNCTIONS[#tyOfCall(FUNC)]}:>MonoItemKind) ==String "pinocchio_token_interface::state::load_mut_unchecked::<pinocchio_token_interface::state::account::Account>"
     )
    [priority(30), preserves-definedness]

  rule [cheatcode-mk-imint-ref]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, OPERAND .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
    => #mkPAccountRef(DEST, OPERAND, PAccountIMint, true)
      ~> #execBlockIdx(TARGET)
    ...
    </k>
    <functions> FUNCTIONS </functions>
    requires #tyOfCall(FUNC) in_keys(FUNCTIONS)
     andBool isMonoItemKind(FUNCTIONS[#tyOfCall(FUNC)])
     andBool (
          #functionName({FUNCTIONS[#tyOfCall(FUNC)]}:>MonoItemKind) ==String "pinocchio_token_interface::state::load_unchecked::<pinocchio_token_interface::state::mint::Mint>"
        orBool
          #functionName({FUNCTIONS[#tyOfCall(FUNC)]}:>MonoItemKind) ==String "pinocchio_token_interface::state::load_mut_unchecked::<pinocchio_token_interface::state::mint::Mint>"
     )
    [priority(30), preserves-definedness]

  rule [cheatcode-mk-prent-ref]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, OPERAND .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
    => #mkPAccountRef(DEST, OPERAND, PAccountPRent, false)
      ~> #execBlockIdx(TARGET)
    ...
    </k>
    <functions> FUNCTIONS </functions>
    requires #tyOfCall(FUNC) in_keys(FUNCTIONS)
     andBool isMonoItemKind(FUNCTIONS[#tyOfCall(FUNC)])
     andBool #functionName({FUNCTIONS[#tyOfCall(FUNC)]}:>MonoItemKind) ==String "pinocchio::sysvars::rent::Rent::from_bytes_unchecked"
    [priority(30), preserves-definedness]

  // expect the Evaluation to return a `PAccByteRef` referring to a `PAccount<Thing>` (not checked)
  // return a reference to the second component <Thing> within this PAccount data.
  // We could check the pointee and, if it is a different data structure, return an error (as the length check in the original code)
  syntax KItem ::= #mkPAccountRef ( Place , Evaluation , ProjectionElem , Bool ) [seqstrict(2)]

  rule <k> #mkPAccountRef(DEST, PAccByteRef(OFFSET, place(LOCAL, PROJS), MUT, _LEN), ACCESS_PROJ, true)
        => #setLocalValue(
              DEST,
              Aggregate(variantIdx(0),
                ListItem(Reference(OFFSET, place(LOCAL, appendP(PROJS, ACCESS_PROJ)), MUT, noMetadata))
              )
            )
        ...
       </k>
  rule <k> #mkPAccountRef(DEST, PAccByteRef(OFFSET, place(LOCAL, PROJS), MUT, _LEN), ACCESS_PROJ, false)
        => #setLocalValue(
              DEST,
              Reference(OFFSET, place(LOCAL, appendP(PROJS, ACCESS_PROJ)), MUT, noMetadata)
            )
        ...
       </k>
```

### Reading and Writing the Second Component

The access to the second component of the `PAccount` value is implemented with a special projection.
This ensures that the data structure can be written to (by constructing and writing the enclosing `PAccount`).
NB The projection rule must have higher priority than the one which auto-projects to the `PAcc` part of the `PAccount`.

```k
  syntax ProjectionElem ::= "PAccountIAcc" | "PAccountIMint" | "PAccountPRent"

  // special traverseProjection rules that call fromPAcc on demand when needed
  rule <k> #traverseProjection(DEST, PAccountAccount(PACC, IACC), PAccountIAcc PROJS, CTXTS)
        => #traverseProjection(DEST, #fromIAcc(IACC)            , PROJS, CtxPAccountIAcc(PACC) CTXTS)
        ...
        </k>
     [priority(20)] // avoid matching the default rule to access PAcc

  rule <k> #traverseProjection(DEST, PAccountMint(PACC, IMINT), PAccountIMint PROJS, CTXTS)
        => #traverseProjection(DEST, #fromIMint(IMINT)        , PROJS, CtxPAccountIMint(PACC) CTXTS)
        ...
        </k>
     [priority(20)] // avoid matching the default rule to access PAcc

  rule <k> #traverseProjection(DEST, PAccountRent(PACC, PRENT), PAccountPRent PROJS, CTXTS)
        => #traverseProjection(DEST, #fromPRent(PRENT)        , PROJS, CtxPAccountPRent(PACC) CTXTS)
        ...
        </k>
     [priority(20)] // avoid matching the default rule to access PAcc


  syntax Context ::= CtxPAccountIAcc( PAcc )
                   | CtxPAccountIMint( PAcc )
                   | CtxPAccountPRent( PAcc )

  rule #projectionsFor(CtxPAccountIAcc(_) CTXS, PROJS) => #projectionsFor(CTXS, PAccountIAcc PROJS)
  rule #projectionsFor(CtxPAccountIMint(_) CTXS, PROJS) => #projectionsFor(CTXS, PAccountIMint PROJS)
  rule #projectionsFor(CtxPAccountPRent(_) CTXS, PROJS) => #projectionsFor(CTXS, PAccountPRent PROJS)

  rule #buildUpdate(VAL, CtxPAccountIAcc(PACC) CTXS) => #buildUpdate(PAccountAccount(PACC, #toIAcc(VAL)), CTXS)
    [preserves-definedness] // by construction, VAL has the right shape from introducing the context
  rule #buildUpdate(VAL, CtxPAccountIMint(PACC) CTXS) => #buildUpdate(PAccountMint(PACC, #toIMint(VAL)), CTXS)
    [preserves-definedness] // by construction, VAL has the right shape from introducing the context
  rule #buildUpdate(VAL, CtxPAccountPRent(PACC) CTXS) => #buildUpdate(PAccountRent(PACC, #toPRent(VAL)), CTXS)
    [preserves-definedness] // by construction, VAL has the right shape from introducing the context
```

```k
endmodule
```
