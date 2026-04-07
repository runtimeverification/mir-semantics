```k
requires "../kmir-ast.md"
requires "../rt/data.md"
requires "../kmir.md"
requires "../rt/configuration.md"
```

We mirror the Solana `AccountInfo` layout so that MIR code can traverse the
fields exactly as it would against the real SPL runtime.

## Data Layout

The account data uses `SPLDataBuffer` wrapper containing the actual struct:
- **Account** (165 bytes): `mint`, `owner`, `amount`, `delegate`, `state`, `is_native`, `delegated_amount`, `close_authority`
- **Mint** (82 bytes): `mint_authority`, `supply`, `decimals`, `is_initialized`, `freeze_authority`
- **Rent** (17 bytes): `lamports_per_byte_year`, `exemption_threshold`, `burn_percent`

## Cheatcode Flow

```
cheatcode_is_spl_account(acc)   -> sets SPLDataBuffer at data field, initializes borrow metadata
cheatcode_is_spl_mint(acc)      -> sets SPLDataBuffer at data field, initializes borrow metadata
cheatcode_is_spl_rent(acc)      -> sets SPLDataBuffer at data field, initializes borrow metadata

Account::unpack_from_slice(buf) -> #splUnpack extracts value from SPLDataBuffer
Account::pack_into_slice(v,buf) -> #splPack writes value into SPLDataBuffer
bincode::deserialize(buf)       -> #splUnpack extracts Rent from SPLDataBuffer
Rent::get()                     -> returns cached or new symbolic Rent value
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
        => #setLocalValue(place(local(I), .ProjectionElems), #buildUpdate(NEW, CONTEXTS))
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
  syntax Value ::= SPLDataBuffer ( Value )

  syntax Operand ::= #appendProjsOp ( Operand , ProjectionElems ) [function, total]
  rule #appendProjsOp(operandCopy(place(L, PROJS)), EXTRA) => operandCopy(place(L, appendP(PROJS, EXTRA)))
  rule #appendProjsOp(operandMove(place(L, PROJS)), EXTRA) => operandMove(place(L, appendP(PROJS, EXTRA)))
  rule #appendProjsOp(OP, _) => OP [owise]
```

## Helper predicates

```k
  syntax Bool ::= #isSplPubkey ( List ) [function, total]
  rule #isSplPubkey(KEY) => size(KEY) ==Int 32 andBool allBytes(KEY)

  syntax Bool ::= #isZeroMemsetValue ( Value ) [function, total]
  rule #isZeroMemsetValue(Integer(0, _, _)) => true
  rule #isZeroMemsetValue(_) => false [owise]

  // Construct a 32-byte pubkey List from individual Int variables.
  // When used with existential variables (?Var:Int), this produces a concrete List structure
  // that ==K can decompose element-wise, avoiding opaque symbolic List equality in SMT.
  syntax List ::= #mkSplPubkey (
    Int , Int , Int , Int , Int , Int , Int , Int ,
    Int , Int , Int , Int , Int , Int , Int , Int ,
    Int , Int , Int , Int , Int , Int , Int , Int ,
    Int , Int , Int , Int , Int , Int , Int , Int ) [macro]
  rule #mkSplPubkey(
    B0,  B1,  B2,  B3,  B4,  B5,  B6,  B7,
    B8,  B9,  B10, B11, B12, B13, B14, B15,
    B16, B17, B18, B19, B20, B21, B22, B23,
    B24, B25, B26, B27, B28, B29, B30, B31 ) =>
      ListItem(Integer(B0,  8, false)) ListItem(Integer(B1,  8, false))
      ListItem(Integer(B2,  8, false)) ListItem(Integer(B3,  8, false))
      ListItem(Integer(B4,  8, false)) ListItem(Integer(B5,  8, false))
      ListItem(Integer(B6,  8, false)) ListItem(Integer(B7,  8, false))
      ListItem(Integer(B8,  8, false)) ListItem(Integer(B9,  8, false))
      ListItem(Integer(B10, 8, false)) ListItem(Integer(B11, 8, false))
      ListItem(Integer(B12, 8, false)) ListItem(Integer(B13, 8, false))
      ListItem(Integer(B14, 8, false)) ListItem(Integer(B15, 8, false))
      ListItem(Integer(B16, 8, false)) ListItem(Integer(B17, 8, false))
      ListItem(Integer(B18, 8, false)) ListItem(Integer(B19, 8, false))
      ListItem(Integer(B20, 8, false)) ListItem(Integer(B21, 8, false))
      ListItem(Integer(B22, 8, false)) ListItem(Integer(B23, 8, false))
      ListItem(Integer(B24, 8, false)) ListItem(Integer(B25, 8, false))
      ListItem(Integer(B26, 8, false)) ListItem(Integer(B27, 8, false))
      ListItem(Integer(B28, 8, false)) ListItem(Integer(B29, 8, false))
      ListItem(Integer(B30, 8, false)) ListItem(Integer(B31, 8, false))

  syntax Bool ::= #isByte ( Int ) [macro]
  rule #isByte(X) => 0 <=Int X andBool X <Int 256

  // AccountState in SPL semantics is carried as an enum variantIdx(0..2); accept legacy u8 too.
  syntax Bool ::= #isSplAccountStateVal ( Value ) [function, total]
  rule #isSplAccountStateVal(Aggregate(variantIdx(N), .List)) => 0 <=Int N andBool N <=Int 2
  rule #isSplAccountStateVal(_) => false [owise]

  syntax Bool ::= #isSPLBorrowFunc ( String ) [function, total]
  rule #isSPLBorrowFunc("std::cell::RefCell::<&mut [u8]>::borrow") => true
  rule #isSPLBorrowFunc("std::cell::RefCell::<&mut [u8]>::borrow_mut") => true
  rule #isSPLBorrowFunc("std::cell::RefCell::<&mut u64>::borrow") => true
  rule #isSPLBorrowFunc("std::cell::RefCell::<&mut u64>::borrow_mut") => true
  rule #isSPLBorrowFunc(_) => false [owise]

  syntax Bool ::= #isSPLUnpackFunc ( String ) [function, total]
  rule #isSPLUnpackFunc(_) => false [owise]
  // spl-token account
  rule #isSPLUnpackFunc("<state::Account as solana_program_pack::Pack>::unpack_from_slice") => true
  rule #isSPLUnpackFunc("Account::unpack_from_slice") => true
  // spl-token mint
  rule #isSPLUnpackFunc("<state::Mint as solana_program_pack::Pack>::unpack_from_slice") => true
  rule #isSPLUnpackFunc("Mint::unpack_from_slice") => true
  // spl-token rent
  rule #isSPLUnpackFunc("bincode::deserialize::<'_, solana_rent::Rent>") => true
  rule #isSPLUnpackFunc("Rent::unpack") => true
  // spl-token multisig
  rule #isSPLUnpackFunc("<state::Multisig as solana_program_pack::Pack>::unpack_from_slice") => true
  rule #isSPLUnpackFunc("Multisig::unpack_from_slice") => true

  syntax Bool ::= #isSPLPackFunc   ( String ) [function, total]
  rule #isSPLPackFunc(_) => false [owise]
  // spl-token account
  rule #isSPLPackFunc("<state::Account as solana_program_pack::Pack>::pack_into_slice") => true
  rule #isSPLPackFunc("Account::pack_into_slice") => true
  // spl-token mint
  rule #isSPLPackFunc("<state::Mint as solana_program_pack::Pack>::pack_into_slice") => true
  rule #isSPLPackFunc("Mint::pack_into_slice") => true
  // spl-token multisig
  rule #isSPLPackFunc("<state::Multisig as solana_program_pack::Pack>::pack_into_slice") => true
  rule #isSPLPackFunc("Multisig::pack_into_slice") => true

  syntax Bool ::= #isSPLRentGetFunc ( String ) [function, total]
  rule #isSPLRentGetFunc(_) => false [owise]
  rule #isSPLRentGetFunc("Rent::get") => true   // mock harness
  rule #isSPLRentGetFunc("solana_sysvar::rent::<impl Sysvar for solana_rent::Rent>::get") => true

  syntax Bool ::= #isSPLSolMemsetFunc ( String ) [function, total]
  rule #isSPLSolMemsetFunc(_) => false [owise]
  rule #isSPLSolMemsetFunc("solana_program_memory::sol_memset") => true
```

## Slice metadata for SPL account buffers

```k
  // Account data buffer length (Account::LEN = 165)
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

  // Mint data buffer length (Mint::LEN = 82)
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

  // Rent data buffer length (Rent::LEN = 17)
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

  // Multisig data buffer length (runtime-verification Multisig::LEN = 99)
  rule #maybeDynamicSize(
         dynamicSize(_),
         SPLDataBuffer(
           Aggregate(variantIdx(0),
             ListItem(Integer(_, 8, false))     // m
             ListItem(Integer(_, 8, false))     // n
             ListItem(BoolVal(_))               // is_initialized
             ListItem(Range(                    // signers: [Pubkey; 3]
               ListItem(_) ListItem(_) ListItem(_)
             ))
           )
         )
       )
       => dynamicSize(99)
       [priority(30)]

  syntax Int ::= #splBufferLen ( Value ) [function, total]

  rule #splBufferLen(
         SPLDataBuffer(
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
       )
      )
       => 165
       requires #isSplAccountStateVal(STATE)
       [priority(30)]

  rule #splBufferLen(
         SPLDataBuffer(
           Aggregate(variantIdx(0),
             ListItem(_AUTH)
             ListItem(Integer(_, 64, false))
             ListItem(Integer(_, 8, false))
             ListItem(BoolVal(_))
             ListItem(_FREEZE)
           )
         )
       )
       => 82
       [priority(30)]

  rule #splBufferLen(
         SPLDataBuffer(
           Aggregate(variantIdx(0),
             ListItem(Integer(_, 64, false))
             ListItem(Float(2.0, 64))
             ListItem(Integer(_, 8, false))
           )
         )
       )
       => 17
       [priority(30)]

  rule #splBufferLen(
         SPLDataBuffer(
           Aggregate(variantIdx(0),
             ListItem(Integer(_, 8, false))
             ListItem(Integer(_, 8, false))
             ListItem(BoolVal(_))
             ListItem(Range(
               ListItem(_) ListItem(_) ListItem(_)
             ))
           )
         )
       )
       => 99 // Multisig layout: m (1) + n (1) + is_initialized (1) + 3 * 32 signer bytes (MAX_SIGNERS = 3)
       [priority(30)]

  rule #splBufferLen(_) => 0 [owise]
```

## Cheatcode handling

The cheatcode functions receive an `&AccountInfo` argument. To access the underlying
data buffer, we navigate through the following Solana AccountInfo structure:

```
AccountInfo (arg is &AccountInfo, so first deref)
├── field 0: key: &Pubkey
├── field 1: lamports: Rc<RefCell<&mut u64>>
├── field 2: data: Rc<RefCell<&mut [u8]>>      <- we want this
│   └── Rc<T>
│       └── field 0: RcInner<T>
│           └── field 0: Cell<usize>           (strong count)
│           └── field 1: Cell<usize>           (weak count)
│           └── field 2: T = RefCell<&mut [u8]>
│               └── field 0: Cell<BorrowFlag>
│               └── field 1: UnsafeCell<&mut [u8]>
│                   └── field 0: &mut [u8]     <- the actual data buffer (deref to get [u8])
├── field 3: owner: &Pubkey
├── ...
```

**Projection path to data buffer** (DATA_BUFFER_PROJS):
```
Deref                      -> AccountInfo       (deref &AccountInfo)
Field(2)                   -> .data             (Rc<RefCell<&mut [u8]>>)
Field(0)                   -> RcInner           (NonNull<RcInner<RefCell<...>>>)
Field(0)                   -> actual pointer    (*RcInner<RefCell<...>>)
Deref                      -> RefCell content   (deref the pointer inside Rc)
Field(2)                   -> RefCell.value     (UnsafeCell<&mut [u8]>)
Field(1)                   -> UnsafeCell.value  (the &mut [u8] reference)
Field(0)                   -> inner value
Deref                      -> [u8]              (the actual byte slice)
```

**Projection path to RefCell** (REFCELL_PROJS) - used for initializing borrow metadata:
```
Deref                      -> AccountInfo
Field(2)                   -> .data
Field(0)                   -> RcInner
Field(0)                   -> RefCell location
Deref                      -> RefCell content
```

**RefCell<&mut [u8]> structure** - used by `#initBorrow` to set correct buffer size:
```
RefCell<&mut [u8]>
├── field 0: Cell<isize>              (BorrowFlag - borrow state counter)
├── field 1: Cell<usize>              (borrow count for runtime checking)
├── field 2: UnsafeCell<&mut [u8]>
│   └── field 0: &mut [u8]            (the actual reference)
│       └── metadata: dynamicSize(N)  (buffer length: Account=165, Mint=82, Rent=17)
```
The `#initBorrow` helper resets borrow counters to 0 and sets the correct dynamicSize.

```k
  // #initBorrow(RefCell, N) - Initialize RefCell borrow metadata with correct buffer size
  // RefCell<&mut [u8]> layout:
  //   field 0: BorrowFlag (Cell<isize>) - borrow state counter
  //   field 1: borrow count (for runtime borrow checking)
  //   field 2: UnsafeCell<&mut [u8]> containing the actual reference with metadata
  // This rule:
  //   1. Resets borrow counters to 0 (no active borrows)
  //   2. Sets the dynamicSize in metadata to N (the known buffer length: 165/82/17)
  syntax Evaluation ::= #initBorrow(Evaluation, Int) [seqstrict(1)]
  rule <k> #initBorrow(Aggregate ( variantIdx ( 0 ) ,
                    ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Integer ( _ , 64 , false ))))))   // borrow flag
                    ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Integer ( _ , 64 , false ))))))   // borrow count
                    ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Integer ( _ , 64 , true ))))))   // inner wrapper
                    ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Reference ( OFFSET , PLACE , MUT , metadata ( dynamicSize ( _ ) , 0 , dynamicSize ( _ ))))))))  // &mut [u8] reference
             ), N)
          => Aggregate ( variantIdx ( 0 ) ,
                    ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Integer ( 0 , 64 , false ))))))   // reset borrow flag to 0
                    ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Integer ( 0 , 64 , false ))))))   // reset borrow count to 0
                    ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Integer ( 0 , 64 , true ))))))
                    ListItem (Aggregate ( variantIdx ( 0 ) , ListItem (Reference ( OFFSET , PLACE , MUT , metadata ( dynamicSize ( N ) , 0 , dynamicSize ( N ))))))))  // set size to N
             ) ...
      </k>
```

```{.k .symbolic}
  // Projection path constants for navigating AccountInfo structure
  // Path to the actual data buffer: AccountInfo -> data -> Rc -> RcInner -> RefCell -> UnsafeCell -> &mut [u8] -> [u8]
  syntax ProjectionElems ::= "DATA_BUFFER_PROJS" [alias]
  rule DATA_BUFFER_PROJS => projectionElemDeref                        // deref &AccountInfo
                            projectionElemField(fieldIdx(2), #hack())  // .data (Rc<RefCell<&mut [u8]>>)
                            projectionElemField(fieldIdx(0), #hack())  // RcInner
                            projectionElemField(fieldIdx(0), #hack())  // first field (RefCell location)
                            projectionElemDeref                        // deref Rc pointer
                            projectionElemField(fieldIdx(2), #hack())  // RefCell.value (UnsafeCell)
                            projectionElemField(fieldIdx(1), #hack())  // UnsafeCell.value
                            projectionElemField(fieldIdx(0), #hack())  // inner
                            projectionElemDeref                        // deref to [u8]
                            .ProjectionElems

  // Path to RefCell for borrow metadata: AccountInfo -> data -> Rc -> RcInner -> RefCell
  syntax ProjectionElems ::= "REFCELL_PROJS" [alias]
  rule REFCELL_PROJS => projectionElemDeref                        // deref &AccountInfo
                        projectionElemField(fieldIdx(2), #hack())  // .data
                        projectionElemField(fieldIdx(0), #hack())  // RcInner
                        projectionElemField(fieldIdx(0), #hack())  // RefCell location
                        projectionElemDeref                        // deref Rc pointer
                        .ProjectionElems

  rule [cheatcode-is-spl-account]:
    <k> #execTerminatorCall(_, FUNC, operandCopy(place(LOCAL, PROJS)) .Operands, _DEST, TARGET, _UNWIND, _SPAN) ~> _CONT
      => #forceSetPlaceValue(
           place(LOCAL, appendP(PROJS, DATA_BUFFER_PROJS)),  // navigate to [u8] data buffer
           SPLDataBuffer(
             Aggregate(variantIdx(0),
               ListItem(Aggregate(variantIdx(0), ListItem(Range(?SplMintKey:List))))        // Account.mint: Pubkey
               ListItem(Aggregate(variantIdx(0), ListItem(Range(?SplTokenOwnerKey:List))))  // Account.owner: Pubkey
               ListItem(Integer(?SplAmount:Int, 64, false))                                 // Account.amount: u64
               ListItem(Aggregate(variantIdx(?SplHasDelegateKey:Int),                       // delegate COption<Pubkey>
                 ListItem(Aggregate(variantIdx(0), ListItem(Range(?SplDelegateKey:List))))))
               ListItem(Aggregate(variantIdx(?SplAccountState:Int), .List))                 // Account.state: AccountState
               ListItem(Aggregate(variantIdx(?SplIsNativeLamportsVariant:Int),              // is_native COption<u64>
                 ListItem(Integer(?SplIsNativeLamports:Int, 64, false))))
               ListItem(Integer(?SplDelegatedAmount:Int, 64, false))                        // Account.delegated_amount: u64
               ListItem(Aggregate(variantIdx(?SplHasCloseAuthKey:Int),                      // close_authority COption<Pubkey>
                 ListItem(Aggregate(variantIdx(0), ListItem(Range(?SplCloseAuthKey:List))))))
             )
           )
         )
      ~> #forceSetPlaceValue(
           place(LOCAL, appendP(PROJS, REFCELL_PROJS)),      // navigate to RefCell for borrow init
           #initBorrow(operandCopy(place(LOCAL, appendP(PROJS, REFCELL_PROJS))), 165)
         )
      ~> #continueAt(TARGET)
    </k>
    requires #functionName(FUNC) ==String "spl_token::entrypoint::cheatcode_is_spl_account"
      orBool #functionName(FUNC) ==String "cheatcode_is_spl_account"
    ensures #isSplPubkey(?SplMintKey)
      andBool #isSplPubkey(?SplTokenOwnerKey)
      andBool 0 <=Int ?SplHasDelegateKey andBool ?SplHasDelegateKey <=Int 1
      andBool (0 ==Int #lookupDiscrAux(discriminant(0) discriminant(1) .Discriminants, variantIdx(?SplHasDelegateKey)) orBool 1 ==Int #lookupDiscrAux(discriminant(0) discriminant(1) .Discriminants, variantIdx(?SplHasDelegateKey)))
      andBool #isSplPubkey(?SplDelegateKey)
      andBool 0 <=Int ?SplAmount andBool ?SplAmount <Int (1 <<Int 64)
      andBool 0 <=Int ?SplAccountState andBool ?SplAccountState <=Int 2
      andBool 0 <=Int ?SplDelegatedAmount andBool ?SplDelegatedAmount <Int (1 <<Int 64)
      andBool 0 <=Int ?SplIsNativeLamportsVariant andBool ?SplIsNativeLamportsVariant <=Int 1
      andBool (0 ==Int #lookupDiscrAux(discriminant(0) discriminant(1) .Discriminants, variantIdx(?SplIsNativeLamportsVariant)) orBool 1 ==Int #lookupDiscrAux(discriminant(0) discriminant(1) .Discriminants, variantIdx(?SplIsNativeLamportsVariant)))
      andBool 0 <=Int ?SplIsNativeLamports andBool ?SplIsNativeLamports <Int (1 <<Int 64)
      andBool 0 <=Int ?SplHasCloseAuthKey andBool ?SplHasCloseAuthKey <=Int 1
      andBool (0 ==Int #lookupDiscrAux(discriminant(0) discriminant(1) .Discriminants, variantIdx(?SplHasCloseAuthKey)) orBool 1 ==Int #lookupDiscrAux(discriminant(0) discriminant(1) .Discriminants, variantIdx(?SplHasCloseAuthKey)))
      andBool #isSplPubkey(?SplCloseAuthKey)
    [priority(30), preserves-definedness]

  rule <k> #traverseProjection(DEST, SPLDataBuffer(VAL), .ProjectionElems, CTXTS) ~> #derefTruncate(dynamicSize (_), PROJS)
        => #traverseProjection(DEST, SPLDataBuffer(VAL), PROJS, CTXTS) ...
       </k>

  rule [cheatcode-is-spl-mint]:
    <k> #execTerminatorCall(_, FUNC, operandCopy(place(LOCAL, PROJS)) .Operands, _DEST, TARGET, _UNWIND, _SPAN) ~> _CONT
      => #forceSetPlaceValue(
           place(LOCAL, appendP(PROJS, DATA_BUFFER_PROJS)),  // navigate to [u8] data buffer
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
           place(LOCAL, appendP(PROJS, REFCELL_PROJS)),      // navigate to RefCell for borrow init
           #initBorrow(operandCopy(place(LOCAL, appendP(PROJS, REFCELL_PROJS))), 82)
         )
      ~> #continueAt(TARGET)
    </k>
    requires #functionName(FUNC) ==String "spl_token::entrypoint::cheatcode_is_spl_mint"
      orBool #functionName(FUNC) ==String "cheatcode_is_spl_mint"
    ensures 0 <=Int ?SplMintHasAuthKey andBool ?SplMintHasAuthKey <=Int 1
      andBool (0 ==Int #lookupDiscrAux(discriminant(0) discriminant(1) .Discriminants, variantIdx(?SplMintHasAuthKey)) orBool 1 ==Int #lookupDiscrAux(discriminant(0) discriminant(1) .Discriminants, variantIdx(?SplMintHasAuthKey)))
      andBool #isSplPubkey(?SplMintAuthorityKey)
      andBool 0 <=Int ?SplMintHasFreezeKey andBool ?SplMintHasFreezeKey <=Int 1
      andBool (0 ==Int #lookupDiscrAux(discriminant(0) discriminant(1) .Discriminants, variantIdx(?SplMintHasFreezeKey)) orBool 1 ==Int #lookupDiscrAux(discriminant(0) discriminant(1) .Discriminants, variantIdx(?SplMintHasFreezeKey)))
      andBool #isSplPubkey(?SplMintFreezeAuthorityKey)
      andBool 0 <=Int ?SplMintSupply andBool ?SplMintSupply <Int (1 <<Int 64)
      andBool 0 <=Int ?SplMintDecimals andBool ?SplMintDecimals <Int 256
    [priority(30), preserves-definedness]

  rule [cheatcode-is-spl-rent]:
    <k> #execTerminatorCall(_, FUNC, operandCopy(place(LOCAL, PROJS)) .Operands, _DEST, TARGET, _UNWIND, _SPAN) ~> _CONT
      => #forceSetPlaceValue(
           place(LOCAL, appendP(PROJS, DATA_BUFFER_PROJS)),  // navigate to [u8] data buffer
           SPLDataBuffer(
             Aggregate(variantIdx(0),
               ListItem(Integer(?SplRentLamportsPerByteYear:Int, 64, false))                          // lamports_per_byte_year: u64
               ListItem(Float(2.0, 64))                                                               // exemption_threshold: f64
               ListItem(Integer(?SplRentBurnPercent:Int, 8, false))                                   // burn_percent: u8
             )
           )
         )
      ~> #forceSetPlaceValue(
           place(LOCAL, appendP(PROJS, REFCELL_PROJS)),      // navigate to RefCell for borrow init
           #initBorrow(operandCopy(place(LOCAL, appendP(PROJS, REFCELL_PROJS))), 17)
         )
      ~> #continueAt(TARGET)
    </k>
    requires #functionName(FUNC) ==String "spl_token::entrypoint::cheatcode_is_spl_rent"
      orBool #functionName(FUNC) ==String "cheatcode_is_spl_rent"
    ensures 0 <=Int ?SplRentLamportsPerByteYear andBool ?SplRentLamportsPerByteYear <Int (1 <<Int 32)
      andBool 0 <=Int ?SplRentBurnPercent andBool ?SplRentBurnPercent <=Int 100
    [priority(30), preserves-definedness]

  // Multisig cheatcode: decompose signer pubkeys into individual byte variables.
  // Each ?SplSiNBj:Int is a single byte (0..255), giving 32 concrete ListItems per signer.
  // This allows ==K on pubkey Lists to decompose into integer equalities (fast for SMT),
  // instead of opaque symbolic List equality (causes Z3 timeout at scale).
  rule [cheatcode-is-spl-multisig]:
    <k> #execTerminatorCall(_, FUNC, operandCopy(place(LOCAL, PROJS)) .Operands, _DEST, TARGET, _UNWIND, _SPAN) ~> _CONT
      => #forceSetPlaceValue(
           place(LOCAL, appendP(PROJS, DATA_BUFFER_PROJS)),  // navigate to [u8] data buffer
           SPLDataBuffer(
             Aggregate(variantIdx(0),
               ListItem(Integer(?SplMultisigM:Int, 8, false))                                             // m: u8
               ListItem(Integer(?SplMultisigN:Int, 8, false))                                             // n: u8
               ListItem(BoolVal(?_SplMultisigInitialised:Bool))                                           // is_initialized: bool
               ListItem(Range(                                                                            // signers: [Pubkey; 3]
                 ListItem(Aggregate(variantIdx(0), ListItem(Range(#mkSplPubkey(
                   ?SplSi0B0:Int,  ?SplSi0B1:Int,  ?SplSi0B2:Int,  ?SplSi0B3:Int,
                   ?SplSi0B4:Int,  ?SplSi0B5:Int,  ?SplSi0B6:Int,  ?SplSi0B7:Int,
                   ?SplSi0B8:Int,  ?SplSi0B9:Int,  ?SplSi0B10:Int, ?SplSi0B11:Int,
                   ?SplSi0B12:Int, ?SplSi0B13:Int, ?SplSi0B14:Int, ?SplSi0B15:Int,
                   ?SplSi0B16:Int, ?SplSi0B17:Int, ?SplSi0B18:Int, ?SplSi0B19:Int,
                   ?SplSi0B20:Int, ?SplSi0B21:Int, ?SplSi0B22:Int, ?SplSi0B23:Int,
                   ?SplSi0B24:Int, ?SplSi0B25:Int, ?SplSi0B26:Int, ?SplSi0B27:Int,
                   ?SplSi0B28:Int, ?SplSi0B29:Int, ?SplSi0B30:Int, ?SplSi0B31:Int)))))
                 ListItem(Aggregate(variantIdx(0), ListItem(Range(#mkSplPubkey(
                   ?SplSi1B0:Int,  ?SplSi1B1:Int,  ?SplSi1B2:Int,  ?SplSi1B3:Int,
                   ?SplSi1B4:Int,  ?SplSi1B5:Int,  ?SplSi1B6:Int,  ?SplSi1B7:Int,
                   ?SplSi1B8:Int,  ?SplSi1B9:Int,  ?SplSi1B10:Int, ?SplSi1B11:Int,
                   ?SplSi1B12:Int, ?SplSi1B13:Int, ?SplSi1B14:Int, ?SplSi1B15:Int,
                   ?SplSi1B16:Int, ?SplSi1B17:Int, ?SplSi1B18:Int, ?SplSi1B19:Int,
                   ?SplSi1B20:Int, ?SplSi1B21:Int, ?SplSi1B22:Int, ?SplSi1B23:Int,
                   ?SplSi1B24:Int, ?SplSi1B25:Int, ?SplSi1B26:Int, ?SplSi1B27:Int,
                   ?SplSi1B28:Int, ?SplSi1B29:Int, ?SplSi1B30:Int, ?SplSi1B31:Int)))))
                 ListItem(Aggregate(variantIdx(0), ListItem(Range(#mkSplPubkey(
                   ?SplSi2B0:Int,  ?SplSi2B1:Int,  ?SplSi2B2:Int,  ?SplSi2B3:Int,
                   ?SplSi2B4:Int,  ?SplSi2B5:Int,  ?SplSi2B6:Int,  ?SplSi2B7:Int,
                   ?SplSi2B8:Int,  ?SplSi2B9:Int,  ?SplSi2B10:Int, ?SplSi2B11:Int,
                   ?SplSi2B12:Int, ?SplSi2B13:Int, ?SplSi2B14:Int, ?SplSi2B15:Int,
                   ?SplSi2B16:Int, ?SplSi2B17:Int, ?SplSi2B18:Int, ?SplSi2B19:Int,
                   ?SplSi2B20:Int, ?SplSi2B21:Int, ?SplSi2B22:Int, ?SplSi2B23:Int,
                   ?SplSi2B24:Int, ?SplSi2B25:Int, ?SplSi2B26:Int, ?SplSi2B27:Int,
                   ?SplSi2B28:Int, ?SplSi2B29:Int, ?SplSi2B30:Int, ?SplSi2B31:Int)))))
               ))
             )
           )
         )
      ~> #forceSetPlaceValue(
           place(LOCAL, appendP(PROJS, REFCELL_PROJS)),      // navigate to RefCell for borrow init
           #initBorrow(operandCopy(place(LOCAL, appendP(PROJS, REFCELL_PROJS))), 99)
         )
      ~> #continueAt(TARGET)
    </k>
    requires #functionName(FUNC) ==String "spl_token::entrypoint::cheatcode_is_spl_multisig"
      orBool #functionName(FUNC) ==String "cheatcode_is_spl_multisig"
    ensures #isByte(?SplMultisigM) andBool #isByte(?SplMultisigN)
      // signer 0
      andBool #isByte(?SplSi0B0)  andBool #isByte(?SplSi0B1)  andBool #isByte(?SplSi0B2)  andBool #isByte(?SplSi0B3)
      andBool #isByte(?SplSi0B4)  andBool #isByte(?SplSi0B5)  andBool #isByte(?SplSi0B6)  andBool #isByte(?SplSi0B7)
      andBool #isByte(?SplSi0B8)  andBool #isByte(?SplSi0B9)  andBool #isByte(?SplSi0B10) andBool #isByte(?SplSi0B11)
      andBool #isByte(?SplSi0B12) andBool #isByte(?SplSi0B13) andBool #isByte(?SplSi0B14) andBool #isByte(?SplSi0B15)
      andBool #isByte(?SplSi0B16) andBool #isByte(?SplSi0B17) andBool #isByte(?SplSi0B18) andBool #isByte(?SplSi0B19)
      andBool #isByte(?SplSi0B20) andBool #isByte(?SplSi0B21) andBool #isByte(?SplSi0B22) andBool #isByte(?SplSi0B23)
      andBool #isByte(?SplSi0B24) andBool #isByte(?SplSi0B25) andBool #isByte(?SplSi0B26) andBool #isByte(?SplSi0B27)
      andBool #isByte(?SplSi0B28) andBool #isByte(?SplSi0B29) andBool #isByte(?SplSi0B30) andBool #isByte(?SplSi0B31)
      // signer 1
      andBool #isByte(?SplSi1B0)  andBool #isByte(?SplSi1B1)  andBool #isByte(?SplSi1B2)  andBool #isByte(?SplSi1B3)
      andBool #isByte(?SplSi1B4)  andBool #isByte(?SplSi1B5)  andBool #isByte(?SplSi1B6)  andBool #isByte(?SplSi1B7)
      andBool #isByte(?SplSi1B8)  andBool #isByte(?SplSi1B9)  andBool #isByte(?SplSi1B10) andBool #isByte(?SplSi1B11)
      andBool #isByte(?SplSi1B12) andBool #isByte(?SplSi1B13) andBool #isByte(?SplSi1B14) andBool #isByte(?SplSi1B15)
      andBool #isByte(?SplSi1B16) andBool #isByte(?SplSi1B17) andBool #isByte(?SplSi1B18) andBool #isByte(?SplSi1B19)
      andBool #isByte(?SplSi1B20) andBool #isByte(?SplSi1B21) andBool #isByte(?SplSi1B22) andBool #isByte(?SplSi1B23)
      andBool #isByte(?SplSi1B24) andBool #isByte(?SplSi1B25) andBool #isByte(?SplSi1B26) andBool #isByte(?SplSi1B27)
      andBool #isByte(?SplSi1B28) andBool #isByte(?SplSi1B29) andBool #isByte(?SplSi1B30) andBool #isByte(?SplSi1B31)
      // signer 2
      andBool #isByte(?SplSi2B0)  andBool #isByte(?SplSi2B1)  andBool #isByte(?SplSi2B2)  andBool #isByte(?SplSi2B3)
      andBool #isByte(?SplSi2B4)  andBool #isByte(?SplSi2B5)  andBool #isByte(?SplSi2B6)  andBool #isByte(?SplSi2B7)
      andBool #isByte(?SplSi2B8)  andBool #isByte(?SplSi2B9)  andBool #isByte(?SplSi2B10) andBool #isByte(?SplSi2B11)
      andBool #isByte(?SplSi2B12) andBool #isByte(?SplSi2B13) andBool #isByte(?SplSi2B14) andBool #isByte(?SplSi2B15)
      andBool #isByte(?SplSi2B16) andBool #isByte(?SplSi2B17) andBool #isByte(?SplSi2B18) andBool #isByte(?SplSi2B19)
      andBool #isByte(?SplSi2B20) andBool #isByte(?SplSi2B21) andBool #isByte(?SplSi2B22) andBool #isByte(?SplSi2B23)
      andBool #isByte(?SplSi2B24) andBool #isByte(?SplSi2B25) andBool #isByte(?SplSi2B26) andBool #isByte(?SplSi2B27)
      andBool #isByte(?SplSi2B28) andBool #isByte(?SplSi2B29) andBool #isByte(?SplSi2B30) andBool #isByte(?SplSi2B31)
    [priority(30), preserves-definedness]
```

## RefCell borrow helpers

```k
  // RefCell::<&mut [u8]>::borrow / borrow_mut - returns Ref/RefMut wrapper with pointer to data
  rule [spl-borrow-data]:
    <k> #execTerminatorCall(_, FUNC, operandCopy(place(LOCAL, PROJS)) .Operands, DEST, TARGET, _UNWIND, _SPAN) ~> _CONT
      => #setSPLBorrowData(DEST, operandCopy(place(LOCAL, PROJS)))
         ~> #continueAt(TARGET)
    </k>
    requires #isSPLBorrowFunc(#functionName(FUNC))
    [priority(30), preserves-definedness]

  syntax KItem ::= #setSPLBorrowData ( Place , Evaluation ) [seqstrict(2)]
  rule <k> #setSPLBorrowData(DEST, Reference(OFFSET, place(LOCAL, PROJS), MUT, META))
        => #setLocalValue(DEST, Aggregate(variantIdx(0),
             ListItem(Aggregate(variantIdx(0), ListItem(PtrLocal(OFFSET, place(LOCAL, appendP(PROJS, projectionElemField(fieldIdx(1), #hack())  projectionElemField(fieldIdx(0), #hack()) .ProjectionElems)), MUT, META))))
             ListItem(Aggregate(variantIdx(0), ListItem(Reference(OFFSET, place (LOCAL, appendP(PROJS, projectionElemField(fieldIdx(0), #hack()) .ProjectionElems)), MUT, META)))))) ...
       </k>
```

## Pack / Unpack operations

```k
  // Account/Mint::unpack_from_slice, bincode::deserialize (for Rent) - extracts struct from SPLDataBuffer
  rule [spl-account-unpack]:
    <k> #execTerminatorCall(_, FUNC, OP:Operand .Operands, DEST, TARGET, _UNWIND, _SPAN) ~> _CONT
      => #splUnpack(DEST, #withDeref(OP))
         ~> #continueAt(TARGET)
    </k>
    requires #isSPLUnpackFunc(#functionName(FUNC))
    [priority(30), preserves-definedness]

  syntax KItem ::= #splUnpack ( Place , Evaluation ) [seqstrict(2)]
  rule <k> #splUnpack(DEST, SPLDataBuffer(VAL))
        => #setLocalValue(DEST, Aggregate(variantIdx(0), ListItem(VAL))) ...
       </k>

  // Account/Mint::pack_into_slice - writes struct into SPLDataBuffer
  rule [spl-account-pack]:
    <k> #execTerminatorCall(_, FUNC, SRC:Operand DST:Operand .Operands, _DEST, TARGET, _UNWIND, _SPAN) ~> _CONT
      => #splPack(#withDeref(SRC), #withDeref(DST)) ~> #continueAt(TARGET)
    </k>
    requires #isSPLPackFunc(#functionName(FUNC))
    [priority(30), preserves-definedness]

  syntax KItem ::= #splPack ( Evaluation , Operand ) [seqstrict(1)]
  rule <k> #splPack(VAL, operandCopy(DEST)) => #setLocalValue(DEST, SPLDataBuffer(VAL)) ... </k>
  rule <k> #splPack(VAL, operandMove(DEST)) => #setLocalValue(DEST, SPLDataBuffer(VAL)) ... </k>
```

## sol_memset on SPL data buffers

`sol_memset` is used by `delete_account` to zero out account data. Rather than
symbolically executing the byte-by-byte loop through `IterMut::next`, we
intercept the call and directly replace the `SPLDataBuffer` content with a
zeroed representation.

```{.k .symbolic}
  // sol_memset(buf, val, len) - fast-path full-buffer zeroization on recognized SPLDataBuffer values.
  // Any other call shape falls back to the ordinary call semantics below.
  rule [spl-sol-memset]:
    <k> #execTerminatorCall(FTY, FUNC,
          BUF:Operand VAL:Operand LEN:Operand .Operands,
          DEST, TARGET, UNWIND, SPAN) ~> _CONT
      => #execSPLSolMemset(FTY, FUNC, #withDeref(BUF), VAL, LEN, BUF, BUF VAL LEN .Operands, DEST, TARGET, UNWIND, SPAN)
    </k>
    requires #isSPLSolMemsetFunc(#functionName(FUNC))
    [priority(30), preserves-definedness]

  syntax KItem ::= #execSPLSolMemset ( Ty, MonoItemKind, Evaluation , Evaluation , Evaluation , Operand, Operands, Place, MaybeBasicBlockIdx, UnwindAction, Span ) [seqstrict(3,4,5)]

  rule <k> #execSPLSolMemset(_, _, SPLDataBuffer(_) #as BUF, VAL, Integer(LEN, 64, false), operandCopy(place(LOCAL, PROJS)), _ARGS, _DEST, TARGET, _UNWIND, _SPAN)
        => #setLocalValue(place(LOCAL, appendP(PROJS, projectionElemDeref .ProjectionElems)), SPLDataBuffer(Integer(0, 8, false))) ~> #continueAt(TARGET) ... </k>
    requires #isZeroMemsetValue(VAL)
     andBool LEN ==Int #splBufferLen(BUF)
     andBool 0 <Int #splBufferLen(BUF)
  rule <k> #execSPLSolMemset(_, _, SPLDataBuffer(_) #as BUF, VAL, Integer(LEN, 64, false), operandMove(place(LOCAL, PROJS)), _ARGS, _DEST, TARGET, _UNWIND, _SPAN)
        => #setLocalValue(place(LOCAL, appendP(PROJS, projectionElemDeref .ProjectionElems)), SPLDataBuffer(Integer(0, 8, false))) ~> #continueAt(TARGET) ... </k>
    requires #isZeroMemsetValue(VAL)
     andBool LEN ==Int #splBufferLen(BUF)
     andBool 0 <Int #splBufferLen(BUF)

  rule [spl-sol-memset-fallback]:
    <k> #execSPLSolMemset(FTY, FUNC, _BUF, _VAL, _LEN, _BUFOP, ARGS, DEST, TARGET, UNWIND, SPAN) ~> _
      => #setUpCalleeData(FUNC, ARGS, SPAN)
    </k>
    <currentFunc> CALLER => FTY </currentFunc>
    <currentFrame>
      <currentBody> _ </currentBody>
      <caller> OLDCALLER => CALLER </caller>
      <dest> OLDDEST => DEST </dest>
      <target> OLDTARGET => TARGET </target>
      <unwind> OLDUNWIND => UNWIND </unwind>
      <locals> LOCALS </locals>
    </currentFrame>
    <stack> STACK => ListItem(StackFrame(OLDCALLER, OLDDEST, OLDTARGET, OLDUNWIND, LOCALS)) STACK </stack>
    [owise]
```

## Rent sysvar handling

```{.k .symbolic}
  // Rent::get - returns stable value, cached in outermost frame
  rule [spl-rent-get]:
    <k> #execTerminatorCall(_, FUNC, .Operands, DEST, TARGET, _UNWIND, _SPAN) ~> _CONT
      => #writeSPLSysRent(DEST)
         ~> #continueAt(TARGET)
    </k>
    requires #isSPLRentGetFunc(#functionName(FUNC))
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
    <k> #execTerminatorCall(_, FUNC, ARG1:Operand ARG2:Operand .Operands, DEST, TARGET, _UNWIND, _SPAN) ~> _CONT
      => #execSPLCmpPubkeys( DEST, #withDeref(ARG1), #withDeref(ARG2))
         ~> #continueAt(TARGET)
    </k>
    requires #functionName(FUNC) ==String "spl_token::processor::Processor::cmp_pubkeys"
    [priority(30), preserves-definedness]

  syntax KItem ::= #execSPLCmpPubkeys( Place , Evaluation , Evaluation ) [seqstrict(2,3)]
  rule <k> #execSPLCmpPubkeys(DEST, Aggregate(variantIdx(0), ListItem(Range(KEY1))), Aggregate(variantIdx(0), ListItem(Range(KEY2))))
        => #setLocalValue(DEST, BoolVal(KEY1 ==K KEY2))
       ... </k>
    [preserves-definedness]
```

## Rent minimum_balance calculation simplification

The rent exemption check involves: `(int)((float)(data_len * lamports_per_byte_year) * 2.0)`
Since float casts create thunks, we simplify this pattern directly to `PRODUCT * 2`.

```k
  // Simplify: (int)((float)PRODUCT * 2.0) => PRODUCT * 2
  rule #cast(
         thunk(#applyBinOp(binOpMul,
           thunk(#cast(Integer(PRODUCT:Int, 64, false), castKindIntToFloat, INT_TY, FLOAT_TY)),
           Float(0.20000000000000000e1, 64),
           false)),
         castKindFloatToInt, FLOAT_TY, INT_TY)
    => Integer(PRODUCT *Int 2, 64, false)
```

## Linking identical accounts

When the `AccountInfo` are provided to the program from the solana runtime,
we restrict that if they have the same `key` then the rest of their fields are
the same. This cheatcode should only be on two `AccountInfo` after `cheatcode_is_account`
is called on those `AccountInfo` to set up the symbolic state. Furthermore this should
be called prior to capturing initial state and prior to executing the implementation.

```{.k .symbolic}
  // Path to account key: &AccountInfo -> AccountInfo -> key -> &Pubkey -> Pubkey
  syntax ProjectionElems ::= "KEY_PROJS" [alias]
  rule KEY_PROJS => projectionElemDeref                        // deref &AccountInfo
                    projectionElemField(fieldIdx(0), #hack())  // .key (&Pubkey)
                    projectionElemDeref                        // deref to Pubkey
                    .ProjectionElems

  // Cheatcode to link two accounts if they have the same key
  // Usage: cheatcode_maybe_same_account(&account1, &account2)
  // Effect: If account1.key == account2.key, then all SPL data fields are constrained equal
  rule [cheatcode-maybe-same-account]:
    <k> #execTerminatorCall(_, FUNC,
          operandCopy(place(LOCAL1, PROJS1))
          operandCopy(place(LOCAL2, PROJS2))
          .Operands, _DEST, TARGET, _UNWIND, _SPAN) ~> _CONT
      => #maybeLinkAccounts(
           operandCopy(place(LOCAL1, appendP(PROJS1, KEY_PROJS))),
           operandCopy(place(LOCAL2, appendP(PROJS2, KEY_PROJS))),
           operandCopy(place(LOCAL1, appendP(PROJS1, DATA_BUFFER_PROJS))),
           operandCopy(place(LOCAL2, appendP(PROJS2, DATA_BUFFER_PROJS)))
         ) ~> #continueAt(TARGET)
    </k>
    requires #functionName(FUNC) ==String "cheatcode_maybe_same_account"
      orBool #functionName(FUNC) ==String "spl_token::entrypoint::cheatcode_maybe_same_account"
    [priority(30), preserves-definedness]

  // Helper to evaluate keys and data, then apply constraint
  syntax KItem ::= #maybeLinkAccounts(Evaluation, Evaluation, Evaluation, Evaluation) [seqstrict]

  // Case: keys are equal - add ensures clause to constrain SPL data equality
  // The ensures clause adds the constraint that all SPL fields must be equal
  rule <k> #maybeLinkAccounts(
          Aggregate(variantIdx(0), ListItem(Range(KEY1))),
          Aggregate(variantIdx(0), ListItem(Range(KEY2))),
          SPLDataBuffer(Aggregate(variantIdx(0),
            ListItem(Aggregate(variantIdx(0), ListItem(Range(MINT1))))
            ListItem(Aggregate(variantIdx(0), ListItem(Range(OWNER1))))
            ListItem(Integer(AMOUNT1, 64, false))
            ListItem(Aggregate(variantIdx(HAS_DELEG1), ListItem(Aggregate(variantIdx(0), ListItem(Range(DELEG1))))))
            ListItem(Aggregate(variantIdx(STATE1), .List))
            ListItem(Aggregate(variantIdx(HAS_NATIVE1), ListItem(Integer(NATIVE1, 64, false))))
            ListItem(Integer(DELEG_AMT1, 64, false))
            ListItem(Aggregate(variantIdx(HAS_CLOSE1), ListItem(Aggregate(variantIdx(0), ListItem(Range(CLOSE1))))))
          )),
          SPLDataBuffer(Aggregate(variantIdx(0),
            ListItem(Aggregate(variantIdx(0), ListItem(Range(MINT2))))
            ListItem(Aggregate(variantIdx(0), ListItem(Range(OWNER2))))
            ListItem(Integer(AMOUNT2, 64, false))
            ListItem(Aggregate(variantIdx(HAS_DELEG2), ListItem(Aggregate(variantIdx(0), ListItem(Range(DELEG2))))))
            ListItem(Aggregate(variantIdx(STATE2), .List))
            ListItem(Aggregate(variantIdx(HAS_NATIVE2), ListItem(Integer(NATIVE2, 64, false))))
            ListItem(Integer(DELEG_AMT2, 64, false))
            ListItem(Aggregate(variantIdx(HAS_CLOSE2), ListItem(Aggregate(variantIdx(0), ListItem(Range(CLOSE2))))))
          ))
        ) => .K ... </k>
    requires KEY1 ==K KEY2
    ensures MINT1 ==K MINT2
      andBool OWNER1 ==K OWNER2
      andBool AMOUNT1 ==Int AMOUNT2
      andBool HAS_DELEG1 ==Int HAS_DELEG2
      andBool DELEG1 ==K DELEG2
      andBool STATE1 ==Int STATE2
      andBool HAS_NATIVE1 ==Int HAS_NATIVE2
      andBool NATIVE1 ==Int NATIVE2
      andBool DELEG_AMT1 ==Int DELEG_AMT2
      andBool HAS_CLOSE1 ==Int HAS_CLOSE2
      andBool CLOSE1 ==K CLOSE2
    [priority(30)]

  // Case: keys are different - no constraint needed
  rule <k> #maybeLinkAccounts(
          Aggregate(variantIdx(0), ListItem(Range(KEY1))),
          Aggregate(variantIdx(0), ListItem(Range(KEY2))),
          _, _
        ) => .K ... </k>
    requires notBool (KEY1 ==K KEY2)
    [priority(30)]
```

```k
endmodule
```
