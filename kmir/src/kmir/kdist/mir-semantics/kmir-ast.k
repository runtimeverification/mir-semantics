requires "abi.k"
requires "alloc.k"
requires "body.k"
requires "lib.k"
requires "mono.k"
requires "target.k"
requires "ty.k"

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
