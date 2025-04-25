# Symbolic locals for functions

This module contains rules that follow the same structure as `#init` in the KMIR module, however it reads the arguments for the signature of the start symbol and generates symbolic values for them.

```k
requires "../kmir.md"

module KMIR-SYMBOLIC-LOCALS [symbolic]
  imports KMIR-CONTROL-FLOW

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

  rule <k> #reserveSymbolicsFor( .LocalDecls, _ ) => .K ... </k>

  rule <k> #reserveSymbolicsFor( LOCALS:LocalDecls, 0 ) => .K ... </k>
       <locals> ... .List => #reserveFor(LOCALS) </locals> // No more arguments, treat the rest of the Decls normally

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

  // Signed
  rule <k> #reserveSymbolicsFor( localDecl(TY, _, MUT) LOCALS:LocalDecls, COUNT        )
        => #reserveSymbolicsFor(                       LOCALS:LocalDecls, COUNT -Int 1 )
           ...
       </k>
       <locals> ... .List => ListItem(typedValue( Integer(?INT:Int, #bitWidth(PRIMTY), true), TY, MUT )) </locals>
       <types> ... TY |-> typeInfoPrimitiveType ( primTypeInt( PRIMTY ) ) ... </types>
    requires 0 <Int COUNT
    ensures #intConstraints( ?INT, PRIMTY )

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
