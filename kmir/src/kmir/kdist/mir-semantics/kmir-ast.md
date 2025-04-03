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


  syntax Pgm ::= Symbol GlobalAllocs FunctionNames MonoItems TypeMappings
                 [symbol(pgm), group(mir---name--allocs--functions--items--types)]

  syntax FunctionKind ::= functionNormalSym(Symbol) [symbol(FunctionKind::NormalSym), group(mir-enum)]
                        | functionIntrinsic(Symbol) [symbol(FunctionKind::IntrinsicSym), group(mir-enum)]
                        | functionNoop(Symbol)      [symbol(FunctionKind::NoOpSym), group(mir-enum)]

  syntax FunctionName ::= functionName(Ty, FunctionKind)
                          [symbol(functionName), group(mir)]

  syntax FunctionNames ::= List [group(mir-klist-FunctionName)]

// move this to ty.md
  syntax TypeInfo ::= typeInfoBaseType(Basetype)         [symbol(TypeInfo::Basetype)  , group(mir-enum)]
                    | enumType(MIRString, Discriminants) [symbol(TypeInfo::EnumType)  , group(mir-enum---name--discriminants)]
                    | structType(MIRString)              [symbol(TypeInfo::StructType), group(mir-enum---name)]

  syntax Basetype ::= "Bool"         [group(mir-enum), symbol(Basetype::Bool)]
                  | "Char"           [group(mir-enum), symbol(Basetype::Char)]
                  | Int(IntTy)       [group(mir-enum), symbol(Basetype::Int)]
                  | Uint(UintTy)     [group(mir-enum), symbol(Basetype::Uint)]
                  | Float(FloatTy)   [group(mir-enum), symbol(Basetype::Float)]
                  | "Str"            [group(mir-enum), symbol(Basetype::Str)]

  syntax Discriminant ::= Discriminant ( Ty , MIRInt ) [group(mir)]

  syntax Discriminants ::= List{Discriminant, ""} [group(mir-list), symbol(Discriminants::append), terminator-symbol(Discriminants::empty)]

  syntax TypeMapping ::= TypeMapping( Ty, TypeInfo ) [group(mir)]

  syntax TypeMappings ::= List{TypeMapping, ""} [group(mir-list), symbol(TypeMappings::append), terminator-symbol(TypeMappings::empty)]

  syntax KItem ::= #init( Pgm )

endmodule
```