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
- `spl_token_interface::state::Account`, modelled as sort `IAcc`;
- `spl_token_interface::state::Mint`, modelled as sort `IMint`;
- `spl_token_interface::state::Multisig`, modelled as sort `IMulti`.

A fourth kind of struct following the `Account` can be a "rent sysvar".

We model this special assumption through a special subsort of `Value` with rules to create and access the contained inner structure as an aggregate of its own.

```k
  syntax Value ::= PAccount

  syntax PAccount ::=
      PAccountAccount( PAcc , IAcc )    // p::Account and iface::Account structs
    | PAccountMint( PAcc , IMint )      // p::Account and iface::Mint structs
    // | PAccountMultisig( PAcc , IMulti ) // p::Account and iface::Multisig structs
    // | PAccountRent ( PAcc, Value )

  syntax PAccount2nd ::= IAcc | IMint // all sorts that can be 2nd component
```

### Pinocchio Account

The `pinocchio::account_info::Account` type is the first "component" of the special data structure.
It is modelled as a `PAcc` sort in K.
The code uses some helper sorts for better readability.

```k
  // pinocchio Account structure
  syntax PAcc ::= PAcc ( U8, U8, U8, U8, U32, Key, Key , U64, U64)

  syntax PAcc ::= #toPAcc ( Value ) [function]
  // -------------------------------------------------------
  rule #toPAcc(
        Aggregate(variantIdx(0),
                  ListItem(Integer(A, 8, false))
                  ListItem(Integer(B, 8, false))
                  ListItem(Integer(C, 8, false))
                  ListItem(Integer(D, 8, false))
                  ListItem(Integer(E, 32, false))
                  ListItem(Range(KEY1BYTES))
                  ListItem(Range(KEY2BYTES))
                  ListItem(Integer(X, 64, false))
                  ListItem(Integer(Y, 64, false))
        ))
      =>
       PAcc (U8(A), U8(B), U8(C), U8(D), U32(E), toKey(KEY1BYTES), toKey(KEY2BYTES), U64(X), U64(Y))

  syntax Value ::= #fromPAcc ( PAcc ) [function, total]
  // -----------------------------------------------------------
  rule #fromPAcc(PAcc (U8(A), U8(B), U8(C), U8(D), U32(E), KEY1, KEY2, U64(X), U64(Y)))
      =>
        Aggregate(variantIdx(0),
                  ListItem(Integer(A, 8, false))
                  ListItem(Integer(B, 8, false))
                  ListItem(Integer(C, 8, false))
                  ListItem(Integer(D, 8, false))
                  ListItem(Integer(E, 32, false))
                  ListItem(Range(fromKey(KEY1)))
                  ListItem(Range(fromKey(KEY2)))
                  ListItem(Integer(X, 64, false))
                  ListItem(Integer(Y, 64, false))
        )

  syntax U8 ::= U8( Int )
  syntax U32 ::= U32 ( Int )
  syntax U64 ::= U64 ( Int )

  syntax Key ::= List {Int,""} // 32 bytes

  syntax Key ::= toKey ( List ) [function]
  // -----------------------------------------------------------
  rule toKey(.List) => .Key
  rule toKey( ListItem(Integer(X, 8, false)) REST:List) => X toKey(REST)

  syntax List ::= fromKey ( Key ) [function]
  // -----------------------------------------------------------
  rule fromKey(.Key) => .List
  rule fromKey( X:Int REST) => ListItem(Integer(X, 8, false)) fromKey(REST)
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
                ListItem(Range(fromKey(MINT)))
                ListItem(Range(fromKey(OWNER)))
                ListItem(Range(fromAmount(AMT)))
                ListItem(Aggregate(variantIdx(0), ListItem(Range(fromFlag(DLG_FLAG))) ListItem(Range(fromKey(DLG_KEY)))))
                ListItem(Integer(STATE, 8, false))
                ListItem(Range(fromFlag(NATIVE_FLAG)))
                ListItem(Range(fromAmount(NATIVE_AMT)))
                ListItem(Range(fromAmount(DLG_AMT)))
                ListItem(Aggregate(variantIdx(0), ListItem(Range(fromFlag(CLOSE_FLAG))) ListItem(Range(fromKey(CLOSE_KEY)))))
      )

  syntax IAcc ::= #toIAcc ( Value ) [function]
  // --------------------------------------------------
  rule #toIAcc(
          Aggregate(variantIdx(0),
                ListItem(Range(MINT))
                ListItem(Range(OWNER))
                ListItem(Range(AMT))
                ListItem(Aggregate(variantIdx(0), ListItem(Range(DLG_FLAG)) ListItem(Range(DLG_KEY))))
                ListItem(Integer(STATE, 8, false))
                ListItem(Range(NATIVE_FLAG))
                ListItem(Range(NATIVE_AMT))
                ListItem(Range(DLG_AMT))
                ListItem(Aggregate(variantIdx(0), ListItem(Range(CLOSE_FLAG)) ListItem(Range(CLOSE_KEY))))
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

  syntax Amount ::= List{Int,""} // 8 bytes
  syntax Amount ::= toAmount ( List ) [function]
  // -----------------------------------------------------------
  rule toAmount(.List) => .Amount
  rule toAmount( ListItem(Integer(X, 8, false)) REST:List) => X toAmount(REST)

  syntax List ::= fromAmount ( Amount ) [function]
  // -----------------------------------------------------------
  rule fromAmount(.Amount) => .List
  rule fromAmount( X:Int REST) => ListItem(Integer(X, 8, false)) fromAmount(REST)

  syntax Flag ::= List{Int,""} // 4 bytes

  syntax List ::= fromFlag ( Flag ) [function]
  // -----------------------------------------------------------
  rule fromFlag(.Flag) => .List
  rule fromFlag( X:Int REST) => ListItem(Integer(X, 8, false)) fromFlag(REST)

  syntax Flag ::= toFlag ( List ) [function]
  // -----------------------------------------------------------
  rule toFlag(.List) => .Flag
  rule toFlag( ListItem(Integer(X, 8, false)) REST:List) => X toFlag(REST)
```

### SPL Token Interfact Mint
```k
  // Mint struct: optional mint authority, supply, decimals, initialised flag, optional freeze authority
  syntax IMint ::= IMint ( Flag, Key , Amount , U8 , U8 , Flag , Key )

  syntax IMint ::= #toIMint ( Value ) [function]
  // ------------------------------------------
  rule #toIMint(
          Aggregate(variantIdx(0),
                ListItem(Aggregate(variantIdx(0), ListItem(Range(MINT_AUTH_FLAG)) ListItem(Range(MINT_AUTH_KEY))))
                ListItem(Range(SUPPLY))
                ListItem(Integer(DECIMALS, 8, false))
                ListItem(Integer(INITIALISED, 8, false))
                ListItem(Aggregate(variantIdx(0), ListItem(Range(FREEZE_AUTH_FLAG)) ListItem(Range(FREEZE_AUTH_KEY))))
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
                   ListItem(Aggregate(variantIdx(0), ListItem(Range(fromFlag(MINT_AUTH_FLAG))) ListItem(Range(fromKey(MINT_AUTH_KEY)))))
                   ListItem(Range(fromAmount(SUPPLY)))
                   ListItem(Integer(DECIMALS, 8, false))
                   ListItem(Integer(INITIALISED, 8, false))
                   ListItem(Aggregate(variantIdx(0), ListItem(Range(fromFlag(FREEZE_AUTH_FLAG))) ListItem(Range(fromKey(FREEZE_AUTH_KEY)))))
          )
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

  // special context node(s) storing the second component
  syntax Context ::= CtxPAccountPAcc ( PAccount2nd )

  // restore the custom value in #buildUpdate
  rule #buildUpdate(VAL, CtxPAccountPAcc(IACC:IAcc) CTXS)
    => #buildUpdate(PAccountAccount(#toPAcc(VAL), IACC), CTXS)
    [preserves-definedness] // by construction, VAL has the correct shape from introducing the context
  rule #buildUpdate(VAL, CtxPAccountPAcc(IMINT:IMint) CTXS)
    => #buildUpdate(PAccountMint(#toPAcc(VAL), IMINT), CTXS)
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
     andBool #functionName({FUNCTIONS[#tyOfCall(FUNC)]}:>MonoItemKind) ==String "entrypoint::cheatcode_is_account"
    [priority(30), preserves-definedness]
  rule [cheatcode-is-mint]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, operandCopy(PLACE) .Operands, _DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
      => #mkPTokenMint(PLACE) ~> #execBlockIdx(TARGET)
    ...
    </k>
    <functions> FUNCTIONS </functions>
    requires #tyOfCall(FUNC) in_keys(FUNCTIONS)
     andBool isMonoItemKind(FUNCTIONS[#tyOfCall(FUNC)])
     andBool #functionName({FUNCTIONS[#tyOfCall(FUNC)]}:>MonoItemKind) ==String "entrypoint::cheatcode_is_mint"
    [priority(30), preserves-definedness]

  // cheat codes and rules to create a special PTokenAccount flavour
  syntax KItem ::= #mkPTokenAccount ( Place )
                 | #mkPTokenMint ( Place )
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

  syntax Evaluation ::= #addAccount ( Evaluation )  [seqstrict()]
                      | #addMint ( Evaluation )     [seqstrict()]
                      // | #addMultisig ( Evaluation ) [seqstrict()]

  rule #addAccount(Aggregate(_, _) #as P_ACC)
      => PAccountAccount(#toPAcc(P_ACC), IAcc(?_MINT, ?_OWNER, ?_AMOUNT, ?_DELEGATEFLAG, ?_DELEGATE, U8(?STATE), ?_NATIVEFLAG, ?_NATIVE_AMOUNT, ?_DELEG_AMOUNT, ?_CLOSEFLAG, ?_CLOSE_AUTH))
    ensures 0 <=Int ?STATE andBool ?STATE <Int 256

  rule #addMint(Aggregate(_, _) #as P_ACC)
      => PAccountMint(#toPAcc(P_ACC), IMint(?_MINT_AUTH_FLAG, ?_MINT_AUTH_KEY, ?_SUPPLY, U8(?DECIMALS), U8(?INITIALISED), ?_FREEZE_AUTH_FLAG, ?_FREEZE_AUTH_KEY))
    ensures 0 <=Int ?DECIMALS andBool ?DECIMALS <Int 256
    andBool 0 <=Int ?INITIALISED andBool ?INITIALISED <=Int 1 // not allowed any other values
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
  syntax Value ::= PAccByteRef ( Int , Place , Mutability )
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
  // TODO intercept call to `borrow_mut_data_unchecked`

  syntax KItem ::= #mkPAccByteRef( Place , Evaluation , Mutability ) [seqstrict(2)]

  rule <k> #mkPAccByteRef(DEST, PtrLocal(OFFSET, PLACE, _MUT, _EMUL), MUT)
        => #setLocalValue(DEST, PAccByteRef(OFFSET, PLACE, MUT))
        ...
        </k>
```

This intermediate representation will be eliminated by an intercepted call to `load_[mut_]unchecked` , the
latter returning a reference to the second data structure within the `PAccount`-sorted value.
While the `PAccByteRef` is generic, the `load_*` functions are specific to the contained type (instances of `Transmutable`).
A (small) complication is that the reference is returned within a `Result` enum.

```{.k .symbolic}
  // intercept calls to `load_unchecked`
  rule [cheatcode-mk-iface-account-ref]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, OPERAND .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
    => #mkPAccountRef(DEST, OPERAND, PAccountIAcc)
      ~> #execBlockIdx(TARGET)
    ...
    </k>
    <functions> FUNCTIONS </functions>
    requires #tyOfCall(FUNC) in_keys(FUNCTIONS)
     andBool isMonoItemKind(FUNCTIONS[#tyOfCall(FUNC)])
     andBool #functionName({FUNCTIONS[#tyOfCall(FUNC)]}:>MonoItemKind) ==String "spl_token_interface::state::load_unchecked::<spl_token_interface::state::account::Account>"
    [priority(30), preserves-definedness]
  // TODO intercept call to `load_mut_unchecked`

  rule [cheatcode-mk-imint-ref]:
    <k> #execTerminator(terminator(terminatorKindCall(FUNC, OPERAND .Operands, DEST, someBasicBlockIdx(TARGET), _UNWIND), _SPAN))
    => #mkPAccountRef(DEST, OPERAND, PAccountIMint)
      ~> #execBlockIdx(TARGET)
    ...
    </k>
    <functions> FUNCTIONS </functions>
    requires #tyOfCall(FUNC) in_keys(FUNCTIONS)
     andBool isMonoItemKind(FUNCTIONS[#tyOfCall(FUNC)])
     andBool #functionName({FUNCTIONS[#tyOfCall(FUNC)]}:>MonoItemKind) ==String "spl_token_interface::state::load_unchecked::<spl_token_interface::state::mint::Mint>"
    [priority(30), preserves-definedness]
  // TODO intercept call to `load_mut_unchecked`

  // expect the Evaluation to return a `PAccByteRef` referring to a `PAccount<Thing>` (not checked)
  // return a reference to the second component <Thing> within this PAccount data.
  // We could check the pointee and, if it is a different data structure, return an error (as the length check in the original code)
  syntax KItem ::= #mkPAccountRef ( Place , Evaluation , ProjectionElem ) [seqstrict(2)]

  rule <k> #mkPAccountRef(DEST, PAccByteRef(OFFSET, place(LOCAL, PROJS), MUT), ACCESS_PROJ)
        => #setLocalValue(
              DEST,
              // Result type
              Aggregate(variantIdx(0),
                  ListItem(Reference(OFFSET, place(LOCAL, appendP(PROJS, ACCESS_PROJ)), MUT, noMetadata))
              )
            )
        ...
       </k>
```

### Reading and Writing the Second Component

The access to the second component of the `PAccount` value is implemented with a special projection.
This ensures that the data structure can be written to (by constructing and writing the enclosing `PAccount`).
NB The projection rule must have higher priority than the one which auto-projects to the `PAcc` part of the `PAccount`.

```k
  syntax ProjectionElem ::= "PAccountIAcc" | "PAccountIMint"

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


  syntax Context ::= CtxPAccountIAcc( PAcc )
                   | CtxPAccountIMint( PAcc )

  rule #projectionsFor(CtxPAccountIAcc(_) CTXS, PROJS) => #projectionsFor(CTXS, PAccountIAcc PROJS)
  rule #projectionsFor(CtxPAccountIMint(_) CTXS, PROJS) => #projectionsFor(CTXS, PAccountIMint PROJS)

  rule #buildUpdate(VAL, CtxPAccountIAcc(PACC) CTXS) => #buildUpdate(PAccountAccount(PACC, #toIAcc(VAL)), CTXS)
    [preserves-definedness] // by construction, VAL has the right shape from introducing the context
  rule #buildUpdate(VAL, CtxPAccountIMint(PACC) CTXS) => #buildUpdate(PAccountMint(PACC, #toIMint(VAL)), CTXS)
    [preserves-definedness] // by construction, VAL has the right shape from introducing the context
```

```k
endmodule
```
