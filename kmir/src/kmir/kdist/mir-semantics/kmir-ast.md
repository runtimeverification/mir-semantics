```k
requires "abi.md"
requires "alloc.md"
requires "body.md"
requires "lib.md"
requires "mono.md"
requires "target.md"
requires "ty.md"

module KMIR-AST
  imports ABI
  imports ALLOC
  imports BODY
  imports LIB
  imports MONO
  imports TARGET
  imports TYPES
```

`Crate` deviates from the Stable MIR definition of crate (which is a struct containing `id: CrateNum`, `name: Symbol`, `is_local: bool`) since this is not rich enough in information for our purposes. 
```k 
  syntax Crate ::= Symbol GlobalAllocs FunctionNames MonoItems BaseTypes
                 [symbol(crate), group(mir---name--allocs--functions--items--types)]

  syntax FunctionKind ::= functionNormalSym(Symbol) [symbol(FunctionKind::NormalSym), group(mir-enum)]
                        | functionIntrinsic(Symbol) [symbol(FunctionKind::IntrinsicSym), group(mir-enum)]
                        | functionNoop(Symbol)      [symbol(FunctionKind::NoOpSym), group(mir-enum)]

  syntax FunctionName ::= functionName(Ty, FunctionKind)
                          [symbol(functionName), group(mir)]

  syntax FunctionNames ::= List [group(mir-klist-FunctionName)]

  syntax BaseType ::= baseType( Ty, TyKind ) [group(mir)]

  syntax BaseTypes ::= List{BaseType, ""} [group(mir-list), symbol(BaseTypes::append), terminator-symbol(BaseTypes::empty)]

endmodule
```