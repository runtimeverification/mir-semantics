# Symbolic locals for functions

This module contains rules that follow the same structure as `#init` in the KMIR module, however it reads the arguments for the signature of the start symbol and generates symbolic values for them.

```k
requires "../kmir.md"

module KMIR-SYMBOLIC-LOCALS [symbolic]
  imports KMIR-CONTROL-FLOW

  imports LIST

  rule <k> #execFunction(
              monoItem(
                SYMNAME,
                monoItemFn(_, _, someBody(body((FIRST:BasicBlock _) #as BLOCKS,RETURNLOCAL:LocalDecl LOCALS:LocalDecls, ARGCOUNT, _, _, _)))
              ),
              FUNCTIONNAMES
            )
        =>
           #reserveSymbolicsFor(LOCALS, ARGCOUNT)
        ~> #execBlock(FIRST)
         ...
       </k>
       <currentFunc> _ => #tyFromName(SYMNAME, FUNCTIONNAMES) </currentFunc>
       <currentFrame>
         <currentBody> _ => toKList(BLOCKS) </currentBody>
         <caller> _ => ty(-1) </caller> // no caller
         <dest> _ => place(local(-1), .ProjectionElems)</dest>
         <target> _ => noBasicBlockIdx </target>
         <unwind> _ => unwindActionUnreachable </unwind>
         <locals> _ => #reserveFor(RETURNLOCAL) </locals>
       </currentFrame>
    requires ARGCOUNT >Int 0
    [priority(25)]
```

## Declare symbolic arguments based on their types

```k
  syntax KItem ::= #reserveSymbolicsFor( LocalDecls, Int )

  rule <k> #reserveSymbolicsFor( .LocalDecls, _ ) => .K ... </k> [priority(40)]

  rule <k> #reserveSymbolicsFor( LOCALS:LocalDecls, N ) => .K ... </k>
       <locals> ... .List => #reserveFor(LOCALS) </locals> // No more arguments, treat the rest of the Decls normally
     requires N ==Int 0
```

## Integers

```k
  // Unsigned
  rule <k> #reserveSymbolicsFor( localDecl(TY, _, MUT) LOCALS:LocalDecls, COUNT        )
        => #reserveSymbolicsFor(                       LOCALS:LocalDecls, COUNT -Int 1 )
           ...
       </k>
       <locals> ... .List => ListItem(typedValue( Integer(?INT:Int, #bitWidth(PRIMTY), false), TY, MUT )) </locals>
       <types> ... TY |-> typeInfoPrimitiveType ( primTypeUint( PRIMTY ) ) ... </types>
    requires 0 <Int COUNT
    ensures #intConstraints( ?INT, PRIMTY )
    [preserves-definedness] // uint-type

  // Signed
  rule <k> #reserveSymbolicsFor( localDecl(TY, _, MUT) LOCALS:LocalDecls, COUNT        )
        => #reserveSymbolicsFor(                       LOCALS:LocalDecls, COUNT -Int 1 )
           ...
       </k>
       <locals> ... .List => ListItem(typedValue( Integer(?INT:Int, #bitWidth(PRIMTY), true), TY, MUT )) </locals>
       <types> ... TY |-> typeInfoPrimitiveType ( primTypeInt( PRIMTY ) ) ... </types>
    requires 0 <Int COUNT
    ensures #intConstraints( ?INT, PRIMTY )
    [preserves-definedness] // int-type

  syntax Bool ::= #intConstraints( Int, InTy ) [function, total]

  rule #intConstraints( X, TY:IntTy  ) => 0 -Int (2 ^Int (#bitWidth(TY) -Int 1)) <=Int X andBool X <Int 2 ^Int (#bitWidth(TY) -Int 1)
  rule #intConstraints( X, TY:UintTy ) => 0                                      <=Int X andBool X <Int 2 ^Int  #bitWidth(TY)
```

## Boolean Values

```k
  rule <k> #reserveSymbolicsFor( localDecl(TY, _, MUT) LOCALS:LocalDecls, COUNT        )
        => #reserveSymbolicsFor(                       LOCALS:LocalDecls, COUNT -Int 1 )
           ...
       </k>
       <locals> ... .List => ListItem(typedValue( BoolVal( ?_BOOL:Bool ), TY, MUT )) </locals>
       <types> ... TY |-> typeInfoPrimitiveType ( primTypeBool ) ... </types>
    requires 0 <Int COUNT
```

## References

```k
  rule <k> #reserveSymbolicsFor( localDecl(TY, _, MUT) LOCALS:LocalDecls, COUNT )
        => #reserveSymbolicsFor( localDecl(REFTY, span(-1), MUT) .LocalDecls, 1 ) // Reserve a symbolic value for the type referenced and put it onto the locals
        ~> #reserveSymbolicReference(TY, MUT)                                     // Create a stack frame and move the value there. Make the reference for it and
                                                                                  // put it onto the locals.
        ~> #reserveSymbolicsFor( LOCALS:LocalDecls, COUNT -Int 1 )                // Reserve the rest of the locals
           ...
       </k>
       <types> ... TY |-> typeInfoRefType ( REFTY ) ... </types>
    requires 0 <Int COUNT

  syntax KItem ::= #reserveSymbolicReference(Ty, Mutability)

  rule <k> #reserveSymbolicReference(TY, MUT) => .K
           ...
       </k>
       <locals> ... ListItem( VAL ) => ListItem( typedValue( Reference( size(STACK) +Int 1, place(local(0), .ProjectionElems), MUT ), TY, MUT ) ) </locals>
       <stack> STACK => STACK ListItem( StackFrame( ty(-1), place(local(-1), .ProjectionElems), noBasicBlockIdx, unwindActionUnreachable, ListItem( VAL ) ) ) </stack>
```

## Arrays and Slices

Slices have an unknown size and need to be abstracted as variables.

```k
  rule <k> #reserveSymbolicsFor( localDecl(TY, _, MUT) LOCALS:LocalDecls, COUNT )
        => #reserveSymbolicsFor( LOCALS:LocalDecls, COUNT -Int 1 )
           ...
       </k>
       <locals> ... .List => ListItem(typedValue( Range(?_SLICE), TY, MUT))</locals>
       <types> ... TY |-> typeInfoArrayType ( _ELEMTY, noTyConst ) ... </types>
    requires 0 <Int COUNT
```

 Arrays have statically known size and can be created with full list structure and symbolic array elements:

```k
  rule <k> #reserveSymbolicsFor( localDecl(TY, SPAN, MUT) LOCALS:LocalDecls, COUNT )
        => #mkArrayElems(ELEMTY, SPAN, MUT, LEN)
        ~> #mkSymbolicArray(TY, MUT)
        ~> #reserveSymbolicsFor( LOCALS, COUNT -Int 1)
           ...
       </k>
       <types> ... TY |-> typeInfoArrayType ( ELEMTY, someTyConst(tyConst(LEN, _)) ) ...</types>
    requires 0 <Int COUNT

  syntax KITEM ::= #mkArrayElems ( Ty , Span , Mutability , TyConstKind )
                 | #mkSymbolicArray ( Ty , Mutability )

  rule <k> #mkArrayElems(TY, SPAN, MUT, LEN)
        => #symbolicArgsAux( .List, asLocalDecls(makeList(readTyConstInt(LEN, TYPES), localDecl(TY, SPAN, MUT))))
            ...
       </k>
       <types> TYPES </types>
    requires isInt(readTyConstInt(LEN, TYPES))
    [preserves-definedness]

  syntax LocalDecls ::= asLocalDecls ( List ) [function]

  rule asLocalDecls(.List) => .LocalDecls

  rule asLocalDecls(ListItem(DECL:LocalDecl) REST) => DECL asLocalDecls(REST)

  rule asLocalDecls(ListItem(_OTHER) REST) => asLocalDecls(REST) [owise]

  rule <k> ELEMS:List ~> #mkSymbolicArray(TY, MUT) => .K
            ...
       </k>
       <locals> LOCALS => LOCALS ListItem(typedValue(Range(ELEMS), TY, MUT)) </locals>
```

# New Code to generate symbolic references in a list

DRAFT CODE. TODO: use wrappers with heating/cooling

```k
  syntax KItem ::= #symbolicArgsFor ( LocalDecls )
                 | #symbolicArgsAux ( List , LocalDecls ) // with accumulator
                 | #symbolicArgsAux2 ( List , LocalDecls ) // with accumulator
                 | #symbolicArg ( LocalDecl )

  rule <k> #symbolicArgsFor(LOCALS) => #symbolicArgsAux(.List, LOCALS) ... </k>

  rule <k> #symbolicArgsAux(ACC, .LocalDecls) => ACC ... </k>

  rule <k> #symbolicArgsAux(ACC, DECL:LocalDecl REST)
        => #symbolicArg(DECL) 
        ~> #symbolicArgsAux2(ACC, REST)
           ...
       </k>

  rule <k> TL:TypedLocal ~> #symbolicArgsAux2(ACC, REST) 
        => #symbolicArgsAux(ACC ListItem(TL), REST) 
          ... 
       </k>
```

## Integers

```k
  // Unsigned
  rule <k> #symbolicArg(localDecl(TY, _, MUT))
        => typedValue( Integer(?INT:Int, #bitWidth(PRIMTY), false), TY, MUT )
           ...
       </k>
       <types> ... TY |-> typeInfoPrimitiveType ( primTypeUint( PRIMTY ) ) ... </types>
    ensures #intConstraints( ?INT, PRIMTY )
    [preserves-definedness] // uint-type

  // Signed
  rule <k> #symbolicArg(localDecl(TY, _, MUT))
        => typedValue( Integer(?INT:Int, #bitWidth(PRIMTY), true), TY, MUT )
           ...
       </k>
       <types> ... TY |-> typeInfoPrimitiveType ( primTypeInt( PRIMTY ) ) ... </types>
    ensures #intConstraints( ?INT, PRIMTY )
    [preserves-definedness] // int-type

  syntax Bool ::= #intConstraints( Int, InTy ) [function, total]

  rule #intConstraints( X, TY:IntTy  ) => 0 -Int (2 ^Int (#bitWidth(TY) -Int 1)) <=Int X andBool X <Int 2 ^Int (#bitWidth(TY) -Int 1)
  rule #intConstraints( X, TY:UintTy ) => 0                                      <=Int X andBool X <Int 2 ^Int  #bitWidth(TY)
```

## Boolean Values

```k
  rule <k> #symbolicArg( localDecl(TY, _, MUT) )
        => typedValue( BoolVal( ?_BOOL:Bool ), TY, MUT )
           ...
       </k>
       <types> ... TY |-> typeInfoPrimitiveType ( primTypeBool ) ... </types>
```

## References

```k
  rule <k> #symbolicArg( localDecl(TY, SPAN, MUT) )
        => #symbolicArg( localDecl(REFTY, SPAN, MUT) ) // Create a symbolic value for the type
        ~> #symbolicRef(TY, MUT)                       // Move created value to stack frame and create reference
           ...
       </k>
       <types> ... TY |-> typeInfoRefType ( REFTY ) ... </types>

  syntax KItem ::= #symbolicRef(Ty, Mutability)

  rule <k> VAL:TypedValue ~> #symbolicRef(TY, MUT)
        => typedValue( Reference( 1, place(local(size(LOCALS)), .ProjectionElems), MUT ), TY, MUT )
           ...
       </k>
       <stack> ListItem( StackFrame( _, _, _, _, LOCALS => LOCALS ListItem( VAL ) ) ) ... </stack>
      // FIXME assumes a stack frame exists on the stack
```

## Arrays and Slices

Slices have an unknown length, so the list of elements is necessarily symbolic.

```k
  rule <k> #symbolicArg( localDecl(TY, _, MUT) )
        => typedValue( Range(?_SLICE), TY, MUT)
           ...
       </k>
       <types> ... TY |-> typeInfoArrayType ( _ELEMTY, noTyConst ) ... </types>
```

 Arrays have statically known size and can be created with full list structure and symbolic array elements:

```k
  rule <k> #symbolicArg( localDecl(TY, SPAN, MUT) )
        => #mkArrayElems(ELEMTY, SPAN, MUT, LEN)
        ~> #symbolicArray(TY, MUT)
           ...
       </k>
       <types> ... TY |-> typeInfoArrayType ( ELEMTY, someTyConst(tyConst(LEN, _)) ) ...</types>

  syntax KItem ::= #symbolicArray ( Ty , Mutability )

  rule <k> ELEMS:List ~> #symbolicArray(TY, MUT)
        => typedValue( Range(ELEMS), TY, MUT)
            ...
       </k>
```

## Enums and Structs

For `enum` types, it cannot be determined which variant is used, therefore the argument list is a variable. 

```k
  rule <k> #symbolicArg( localDecl(TY, _, MUT) )
        => typedValue( Aggregate(variantIdx(?_ENUM_IDX), ?_ENUM_ARGS), TY, MUT)
           ...
       </k>
       <types> ... TY |-> typeInfoEnumType ( _, _, _ ) ... </types>
```

For structs, we could generate suitable arguments with more type information about the fields. At the time of writing this information is not available, though.

```k
  rule <k> #symbolicArg( localDecl(TY, _, MUT) )
        => typedValue( Aggregate(variantIdx(0), ?_STRUCT_ARGS), TY, MUT)
           ...
       </k>
       <types> ... TY |-> typeInfoStructType ( _, _ ) ... </types>
```


# End of new code, old code follows

## Enums and Structs

For `enum` types, it cannot be determined which variant is used, therefore the argument list is a variable. 

```k
  rule <k> #reserveSymbolicsFor( localDecl(TY, _, MUT) LOCALS:LocalDecls, COUNT )
        => #reserveSymbolicsFor( LOCALS:LocalDecls, COUNT -Int 1 )
           ...
       </k>
       <locals> ... .List => ListItem(typedValue( Aggregate(variantIdx(?_ENUM_IDX), ?_ENUM_ARGS), TY, MUT))</locals>
       <types> ... TY |-> typeInfoEnumType ( _, _, _ ) ... </types>
    requires 0 <Int COUNT
```

For structs, we could generate suitable arguments with more type information about the fields. At the time of writing this information is not available, though.

```k
  rule <k> #reserveSymbolicsFor( localDecl(TY, _, MUT) LOCALS:LocalDecls, COUNT )
        => #reserveSymbolicsFor( LOCALS:LocalDecls, COUNT -Int 1 )
           ...
       </k>
       <locals> ... .List => ListItem(typedValue( Aggregate(variantIdx(0), ?_STRUCT_ARGS), TY, MUT))</locals>
       <types> ... TY |-> typeInfoStructType ( _, _ ) ... </types>
    requires 0 <Int COUNT
```

## Arbitrary Values

```k
  rule <k> #reserveSymbolicsFor( localDecl(TY, _, MUT) LOCALS:LocalDecls, COUNT        )
        => #reserveSymbolicsFor(                       LOCALS:LocalDecls, COUNT -Int 1 )
           ...
       </k>
       <locals> ... .List => ListItem(typedValue( ?_VAL:Value, TY, MUT )) </locals>
    requires 0 <Int COUNT
    [owise]

endmodule
```
