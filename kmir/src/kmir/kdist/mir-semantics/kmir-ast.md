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

  syntax Pgm ::= Symbol GlobalAllocs FunctionNames MonoItems
                 [symbol(pgm), group(mir---name--allocs--functions--items)]

  syntax FunctionKind ::= functionNormalSym(Symbol) [symbol(FunctionKind::NormalSym), group(mir-enum)]
                        | functionIntrinsic(Symbol) [symbol(FunctionKind::IntrinsicSym), group(mir-enum)]
                        | functionNoop(Symbol)      [symbol(FunctionKind::NoOpSym), group(mir-enum)]

  syntax FunctionName ::= functionName(MIRInt, FunctionKind)
                          [symbol(functionName), group(mir)]

  syntax FunctionNames ::= List [group(mir-klist-FunctionName)]

endmodule
```