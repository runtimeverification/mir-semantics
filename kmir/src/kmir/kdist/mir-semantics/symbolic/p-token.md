```k
requires "../kmir-ast.md"
requires "../rt/data.md"
requires "../rt/configuration.md"
```

This module provides specialised data types and associated access rules
for data used by the p-token contract and its operations.

```k
module KMIR-P-TOKEN [symbolic] 
  imports TYPES
  imports BODY
  imports RT-DATA
```

## Special-purpose types for P-token

The `pinocchio::account_info::AccountInfo` type contains a (mutable) pointer to a `pinocchio::account_info::Account`.
However, in practice the pointed-at memory is assumed to contain additional data _after_ this `Account`.
The additional data is commonly an instance of `Transmutable` (assumed here), which limits the choices to 3 structs:
- `spl_token_interface::state::Account`
- `spl_token_interface::state::Mint`
- `spl_token_interface::state::Multisig`

We model this special assumption through a special subsort of `Value` with rules to create and access the contained inner structure as an aggregate of its own.

```k
  syntax Value ::= PAccount

  syntax PAccount ::= 
      PAccountAccount( PAcc , IAcc )  // p::Account and iface::Account structs
    | PAccountMint( PAcc , Value )     // p::Account and iface::Mint structs
    | PAccountMultisig( PAcc , Value ) // p::Account and iface::Multisig structs

  // pinocchio Account structure
  syntax U8 ::= U8( Int )
  syntax U32 ::= U32 ( Int )
  syntax U64 ::= U64 ( Int )
  syntax Ints ::= List {Int,""}
  syntax Key ::= Ints // 32 bytes

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
       PAcc (U8(A), U8(B), U8(C), U8(D), U32(E), toInts(KEY1BYTES), toInts(KEY2BYTES), U64(X), U64(Y))

  syntax Ints ::= toInts ( List ) [function]
  // -----------------------------------------------------------
  rule toInts(.List) => .Ints
  rule toInts( ListItem(Integer(X, 8, false)) REST:List) => X toInts(REST)

  syntax Value ::= #fromPAcc ( PAcc ) [function, total]
  // -----------------------------------------------------------
  rule #fromPAcc(PAcc (U8(A), U8(B), U8(C), U8(D), U32(E), KEY1INTS, KEY2INTS, U64(X), U64(Y)))
      =>
        Aggregate(variantIdx(0),
                  ListItem(Integer(A, 8, false))
                  ListItem(Integer(B, 8, false))
                  ListItem(Integer(C, 8, false))
                  ListItem(Integer(D, 8, false))
                  ListItem(Integer(E, 32, false))
                  ListItem(Range(fromInts(KEY1INTS)))
                  ListItem(Range(fromInts(KEY2INTS)))
                  ListItem(Integer(X, 64, false))
                  ListItem(Integer(Y, 64, false))
        )

  syntax List ::= fromInts ( Ints ) [function]
  // -----------------------------------------------------------
  rule fromInts(.Ints) => .List
  rule fromInts( X:Int REST:Ints) => ListItem(Integer(X, 8, false)) fromInts(REST)

  // interface account structure
  syntax Amount ::= Ints // 8 bytes
  syntax Flag ::= Ints // 4 bytes
  syntax IAcc ::= IAcc ( Key, Key, Amount, Flag, Key, U8, Flag, Amount, Amount, Flag, Key )

  // TODO fromIAcc function to create an Aggregate, used when dereferencing the data pointer

```

When accessing the special value's fields, it is transformed to a normal `Aggregate` struct on the fly
in order to avoid having to encode each field access individually.


```k
  // TODO special traverseProjection rules that call fromPAcc on demand when needed
```

The special values are introduced by a special function call (cheat code function).

```k
  // TODO special rule to intercept the cheat code function calls and replace them by #mkPToken<thing>

  // cheat codes and rules to create a special PTokenAccount flavour
  syntax KItem ::= #mkPTokenAccount ( Place )
                 | #mkPTokenMint ( Place )
                 | #mkPTokenMultisig ( Place )

  // place assumed to hold an AccountInfo, having 1 field holding a pointer to an account
  // follow the pointer in field 1 to read the account data
  // modify the pointee, creating additional data (different kinds) with fresh variables
  // 
  rule [p-token-account-account]:
    <k> #mkPTokenAccount(place(LOCAL, PROJS))
      => #setLocalValue(
            place(LOCAL, appendP(PROJS, projectionElemField(fieldIdx(0), ?HACK) projectionElemDeref .ProjectionElems)),
            #addAccount(operandCopy(place(LOCAL, appendP(PROJS, projectionElemField(fieldIdx(0), ?HACK) projectionElemDeref .ProjectionElems)))))
      ...
    </k>

  syntax Evaluation ::= #addAccount ( Evaluation ) [seqstrict()]
                //  | ##addMint ( Evaluation )    
                //  | ##addMultisig ( Evaluation )

  rule #addAccount(Aggregate(_, _) #as P_ACC)
      => PAccountAccount(#toPAcc(P_ACC), IAcc(?_MINT, ?_OWNER, ?_AMOUNT, ?_DELEGATEFLAG, ?_DELEGATE, U8(?STATE), ?_NATIVEFLAG, ?_NATIVE_AMOUNT, ?_DELEG_AMOUNT, ?_CLOSEFLAG, ?_CLOSE_AUTH))
    ensures 0 <=Int ?STATE andBool ?STATE <Int 256

```



```k
endmodule
```