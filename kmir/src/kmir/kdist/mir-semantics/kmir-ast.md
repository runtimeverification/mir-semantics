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

  syntax Pgm ::= Symbol GlobalAllocsMap MonoItems [symbol(pgm)]

endmodule
```