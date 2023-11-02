```k
require "mir-lexer-syntax.md"
```

Syntax of MIR types
-------------------

```k
module MIR-TYPE-SYNTAX
  imports BOOL-SYNTAX
  imports UNSIGNED-INT-SYNTAX
  imports MIR-LEXER-SYNTAX
```

```k
  // https://doc.rust-lang.org/reference/types.html#type-expressions
  syntax Type ::= "(" Type ")"  [bracket]  // TypeNoBounds
                | TypeNoBounds
                | TraitObjectTypeReduced

  syntax RigidTy ::= "bool"
                   | "char"
                   | IntTy
                   | UintTy
                   | FloatTy
                   | "str"
                   | Array
                   | Slice

  syntax IntTy ::= "isize"
                 | "i8"
                 | "i16" 
                 | "i32"
                 | "i64"
                 | "i128"

  syntax UintTy ::= "usize"
                  | "u8"
                  | "u16"
                  | "u32"
                  | "u64"
                  | "u128"

  syntax FloatTy ::= "f32"
                   | "f64"

  syntax TypeList ::= List{Type, ","}

  syntax TypeNoBounds ::= ImplTraitTypeOneBound
                        // In the Rust syntax, ImplTraitTypeReduced is a direct
                        // child of type. For some reason, MIR allows `&impl A+B`
                        // so it needs to be a child of TypeNoBounds
                        | ImplTraitTypeReduced
                        | TraitObjectTypeOneBound
                        | TypePath
                        | NonPathImplementableType
                        // Probably not used in MIR: InferredType
                        | QualifiedPathInType
                        // Probably not used im MIR: MacroInvocation
                        | MirOnlyType

  syntax NonPathImplementableType ::= TupleType
                                    | NeverType
                                    | RawPointerType
                                    | ReferenceType
                                    // TODO: DoubleReferenceType should be removed.
                                    // This exists only because a type like
                                    // &&usize, which should probably be parsed as
                                    // &(&usize), fails to parse because
                                    // K identifies "&&" as a single token.
                                    // One option would be to replace all "&&"
                                    // tokens with "&" "&".
                                    | DoubleReferenceType
                                    | BareFunctionType

  // https://doc.rust-lang.org/reference/types/impl-trait.html
  syntax ImplTraitTypeOneBound ::= "impl" TraitBound

  // https://doc.rust-lang.org/reference/types/trait-object.html
  syntax TraitObjectTypeOneBound ::= "dyn" TraitBound

  // https://doc.rust-lang.org/reference/paths.html#paths-in-types
  syntax TypePath ::= "::" TypePathList "::" TypePathEndSegment
                    | TypePathList "::" TypePathEndSegment
                    | "::" TypePathEndSegment
                    | TypePathEndSegment

  syntax TypePathList ::= NeList{TypePathSegment, "::"}

  syntax TypePathSegment  ::= PathIdentSegment PathIdentSegmentSuffix
                            | PathIdentSegment "::" PathIdentSegmentSuffix
                            | PathOpaque

  syntax TypePathEndSegment ::= PathIdentSegment PathIdentSegmentEndSuffix [avoid] // [avoid] to stop parsing ambiguity  syntax Type ::= Type ":Type" [format(%1%2), org.kframework.kore.Sort(Type)] #SemanticCastToType(#token("ABCD","#KVariable"))
                              | PathIdentSegment "::" PathIdentSegmentEndSuffix
                              | PathOpaque

  // In the Rust documentation, TypePathFn is included in PathIdentSegmentSuffix.
  // However, that generates a parse ambiguity:
  // a::b() -> c::d
  // can be parsed either as a path with three elements:
  // a::(b() -> c)::d
  // or as a path with two elements:
  // a::(b() -> (c::d))
  // TODO: Figure out if this needs disambiguation at runtime, or
  // if having the TypePathFn part at the end is good enough.
  syntax PathIdentSegmentSuffix ::= ""
                                  | GenericArgs
  syntax PathIdentSegmentEndSuffix  ::= PathIdentSegmentSuffix
                                      | TypePathFn

  syntax PathIdentSegment ::= RigidTy [prefer]
  syntax PathIdentSegment ::= Identifier | "$crate"
  syntax GenericArgs ::= "<" GenericArgsList ">"
  syntax GenericArgsList ::= List{GenericArg, ","}
  syntax GenericArg ::= Lifetime
                      | Type
                      | GenericArgsConst
                      | GenericArgsBinding
                      | PathExpression "+" PathExpression
  syntax GenericArgsConst ::= LiteralExpression
                            | "-" LiteralExpression
                            | BlockExpression
                            // SimplePathSegmentReduced is not actually needed, it's covered by Type
  syntax GenericArgsBinding ::= Identifier "=" Type
  syntax TypePathFn ::= "(" TypeList ")" MaybeResultType
  syntax MaybeResultType ::= "" | "->" Type

  // https://doc.rust-lang.org/reference/types/tuple.html#tuple-types
  syntax TupleType  ::= "(" ")"
                      | "(" Type "," TypeList ")"
  // https://doc.rust-lang.org/reference/types/never.html
  syntax NeverType ::= "!"
  // https://doc.rust-lang.org/reference/types/pointer.html#raw-pointers-const-and-mut
  syntax RawPointerType ::= "*" "mut" TypeNoBounds
                          | "*" "const" TypeNoBounds
  // https://doc.rust-lang.org/reference/types/pointer.html#shared-references-
  syntax ReferenceType  ::= "&" TypeNoBounds
                          | "&" Lifetime TypeNoBounds
                          | "&" "mut" TypeNoBounds
                          | "&" Lifetime "mut" TypeNoBounds
  syntax DoubleReferenceType  ::= "&&" TypeNoBounds
                                | "&&" Lifetime TypeNoBounds
                                | "&&" "mut" TypeNoBounds
                                | "&&" Lifetime "mut" TypeNoBounds

  // https://doc.rust-lang.org/reference/trait-bounds.html
  // TODO: Make this a token.
  // TODO: There are various lifetime-related tokens that I combined into a
  // single one. Consider actually using multiple token types.
  syntax Lifetime ::= "'" Identifier | "'static"
  syntax LifetimeBounds ::= List{Lifetime, "+"}

  // https://doc.rust-lang.org/reference/types/array.html
  syntax Array ::= "[" Type ";" RustExpression "]"

  // https://doc.rust-lang.org/reference/types/slice.html
  syntax Slice ::= "[" Type "]"
  // https://doc.rust-lang.org/reference/paths.html#qualified-paths
  syntax QualifiedPathInType ::= QualifiedPathType
  syntax QualifiedPathInType ::= QualifiedPathInType "::" TypePathSegment
  syntax QualifiedPathType  ::= "<" Type ">"
                              | "<" Type "as" TypePath ">"
  // https://doc.rust-lang.org/reference/types/function-pointer.html
  syntax BareFunctionType ::= MaybeForLifetimes FunctionTypeQualifiers
                              "fn" "(" FunctionParametersMaybeNamedVariadic ")"
                              MaybeBareFunctionReturnType
                              MaybeCurlyBraceTypeAnnotation
  syntax FunctionTypeQualifiers ::= "" | "unsafe" | "extern" Abi | "unsafe" "extern" Abi
  syntax FunctionParametersMaybeNamedVariadic ::= MaybeNamedFunctionParameters
                                                // Not seen in MIR: MaybeNamedFunctionParametersVariadic
                                                // TODO: Try to generate this
  syntax MaybeNamedFunctionParameters ::= List {MaybeNamedParam, ","}
  syntax BareFunctionReturnType ::= "->" TypeNoBounds
  syntax MaybeBareFunctionReturnType ::= "" | BareFunctionReturnType
  // See
  // kmir/src/tests/integration/test-data/compiletest-rs/ui/closures/old-closure-fn-coerce.cs
  // for some rust code that produces this.
  syntax MaybeCurlyBraceTypeAnnotation ::= "" | "{" PathExpression "}"
  // https://doc.rust-lang.org/reference/trait-bounds.html#higher-ranked-trait-bounds
  syntax ForLifetimes ::= "for" GenericParams
  syntax MaybeForLifetimes ::= "" | ForLifetimes

  // https://doc.rust-lang.org/reference/items/generics.html
  syntax GenericParams ::= "<" GenericParamList ">"
  syntax GenericParamList ::= List{GenericParam, ","}

  // https://doc.rust-lang.org/reference/types/impl-trait.html
  // There is a parse conflict between
  // Type -> TypeNoBounds -> ImplTraitTypeOneBound -> impl TraitBound
  // and Type -> TypeParamBounds -> impl TypeParamBound -> impl TraitBound
  // This is an attempt to solve this issue.
  syntax ImplTraitType ::= ImplTraitTypeOneBound | ImplTraitTypeReduced
  syntax ImplTraitTypeReduced ::= "impl" TypeParamBoundsReduced
  // https://doc.rust-lang.org/reference/types/trait-object.html
  // TraitObjectType has a similar conflict as ImplTraitType, solved in the
  // same way.
  syntax TraitObjectType::= TraitObjectTypeOneBound | TraitObjectTypeReduced
  syntax TraitObjectTypeReduced ::= "dyn" TypeParamBoundsReduced
  // https://doc.rust-lang.org/reference/trait-bounds.html
  syntax TypeParamBounds ::= ImplTraitTypeOneBound | TypeParamBoundsReduced
  syntax TypeParamBoundsReduced ::= Lifetime
                                  | TypeParamBound "+" TypeParamBoundsList
  syntax TypeParamBoundsReduced2  ::= ImplTraitTypeOneBound
                                    | TypeParamBound "+" TypeParamBoundsList
  syntax TypeParamBoundsList ::= NeList{TypeParamBound, "+"}
  syntax TypeParamBound ::= Lifetime | TraitBound
  syntax TraitBound ::= TraitBoundInner
                      | "(" TraitBoundInner ")"
  syntax TraitBoundInner  ::= "?" MaybeForLifetimes TypePath
                            | MaybeForLifetimes TypePath

  // https://doc.rust-lang.org/reference/items/generics.html
  // OuterAttributes are likely not used for GenericParam in MIR.
  syntax GenericParam ::= LifetimeParam
                        | TypeParam
                        // ConstParam is likely not used in MIR.
  syntax LifetimeParam  ::= Lifetime
                          | Lifetime ":" LifetimeBounds
  syntax TypeParam  ::= RigidTy [prefer]
  syntax TypeParam  ::= Identifier MaybeColonTypeParamBounds MaybeEqualsType
  syntax MaybeColonTypeParamBounds ::= "" | ":" | ":" TypeParamBounds
  syntax MaybeEqualsType ::= "" | "=" Type

  // It is likely that MIR does not use the full syntax for MaybeNamedParam
  syntax MaybeNamedParam ::= Type

  syntax Abi ::= StringLiteral

  syntax FunctionPathComponent  ::= Identifier
                                  | PathLocation
                                  | PathClosure
                                  | PathConstant
                                  | PathOpaque
                                  | Int
  // TODO: Figure out if FunctionPath is always non-empty. If so, merge with
  // PathFunctionData
  syntax FunctionPath ::= List{FunctionPathComponent, "::"}
  syntax PathLocation ::= "<" "impl" "at" FilePosition ">"
  syntax PathClosure ::= "{" "closure" "#" Int "}"
  syntax PathConstant ::= "{" "constant" "#" Int "}"
  syntax PathOpaque ::= "{" "opaque" "#" Int "}"

  // TODO: Figure out if we need full expression syntax. We probably don't need,
  // e.g., ExpressionWithBlock
  // https://doc.rust-lang.org/reference/expressions.html
  syntax RustExpression ::= ExpressionWithoutBlock
                          | ExpressionWithBlock

  syntax ExpressionWithoutBlock ::= LiteralExpression
                                  | PathExpression
                                  // CallExpression
                                  // https://doc.rust-lang.org/reference/expressions/call-expr.html
                                  | RustExpression "(" RustExpressionList ")"
                                  // FieldExpression
                                  // https://doc.rust-lang.org/reference/expressions/field-expr.html
                                  | RustExpression "." Identifier
                                  // OperatorExpression
                                  // https://doc.rust-lang.org/reference/expressions/operator-expr.html
                                  // TypeCastExpression
                                  > RustExpression "as" TypeNoBounds
                                  // BorrowExpression
                                  > "&" RustExpression
                                  | "&" "mut" RustExpression
                                  | "&&" RustExpression
                                  | "&&" "mut" RustExpression
                                  // DereferenceExpression
                                  | "*" RustExpression
                                  // NegationExpression
                                  | "-" RustExpression
                                  | "!" RustExpression
                                  // ArithmeticOrLogicalExpression
                                  > left:
                                    RustExpression "*" RustExpression
                                  | RustExpression "/" RustExpression
                                  | RustExpression "%" RustExpression
                                  > left:
                                    // RustExpression " + " RustExpression // PASSES
                                    RustExpression "+" RustExpression // FAILS
                                  | RustExpression "-" RustExpression
                                  > left:
                                    RustExpression "<" "<" RustExpression
                                  | RustExpression ">" ">" RustExpression
                                  > left:
                                    RustExpression "&" RustExpression
                                  > left:
                                    RustExpression "|" RustExpression
                                  > left:
                                    RustExpression "^" RustExpression
                                  // ComparisonExpression
                                  > left:
                                    RustExpression "==" RustExpression
                                  | RustExpression "!=" RustExpression
                                  | RustExpression ">" RustExpression
                                  | RustExpression "<" RustExpression
                                  | RustExpression ">=" RustExpression
                                  | RustExpression "<=" RustExpression
                                  // LazyBooleanExpression
                                  > left:
                                    RustExpression "||" RustExpression
                                  | RustExpression "&&" RustExpression
                                  | GroupedExpression
  syntax ExpressionWithBlock ::= BlockExpression

  // https://doc.rust-lang.org/reference/expressions/block-expr.html
  syntax BlockExpression ::= "{" RustExpression "}"
  // https://doc.rust-lang.org/reference/expressions/literal-expr.html
  syntax LiteralExpression  ::= CharLiteral
                              | StringLiteral
                              | ByteLiteral
                              | ByteStringLiteral
                              | Int
                              | Bool

  // https://doc.rust-lang.org/reference/expressions/grouped-expr.html
  syntax GroupedExpression ::= "(" RustExpression ")"
  syntax RustExpressionList ::= List{RustExpression, ","}

  syntax Literal  ::= UnsignedLiteral
                    | SignedLiteral
                    | FloatLiteral
                    | HexLiteral
                    | StringLiteral
                    | CharLiteral
                    | ByteLiteral
                    | ByteStringLiteral

  // https://doc.rust-lang.org/reference/expressions/literal-expr.html
  syntax LiteralExpression  ::= CharLiteral
                              | StringLiteral
                              // RawStringLiteral is unlikely to be used in MIR
                              | ByteLiteral
                              | ByteStringLiteral
                              // RawByteStringLiteral is unlikely to be used in MIR
                              | UnsignedLiteral | Int
                              | FloatLiteral
                              | Bool

  // https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/pretty.rs#L725
  // https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/pretty.rs#L806
  // https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/pretty.rs#L848
  syntax DataAlloc ::= Identifier "(" MaybeStaticPath "size" ":" Int "," "align" ":" Int ")" "{" DataAllocData "}"
  syntax DataAllocData ::= DataAllocDataShortLine | DataAllocDataLines
  syntax DataAllocElement ::= AllocReferenceToken | DoubleHexDigit | "__"
  syntax DoubleHexDigit ::= Int | DoubleHexDigitNoInt
  syntax DoubleHexDigitNoInt ::= DoubleHexDigitNoIntLetter | DoubleHexDigitNoIntDigit

  syntax MaybeStaticPath ::= "" | "static" ":" FunctionPath ","
  syntax DataAllocDataShortLine ::= List{DataAllocElement, ""}
  syntax DataAllocDataLine ::= HexLiteral "|" DataAllocDataShortLine
  syntax DataAllocDataLines ::= NeList {DataAllocDataLine, ""}

  syntax FunctionAlloc ::= Identifier "(" "fn" ":" PathExpression "-" "shim" ")" 

  syntax BB ::= BBName MaybeBBCleanup
  syntax MaybeBBCleanup ::= "" | "(" "cleanup" ")"

  syntax MirOnlyType  ::= "[" "closure" "@" FilePosition "]"
                        | "[" "async" "fn" "body" "@" FilePosition "]"
                        | "[" "async" "block" "@" FilePosition "]"
                        | "[" MaybeStatic "generator" "@" FilePosition "]"
  syntax MaybeStatic ::= "" | "static"

  // Variable names can also clash with type names, see compiletest-rs/ui/moves/move-out-of-field.mir
  // TODO: Handle this clash. See issue #228
  syntax UserVariableName ::= Identifier
  syntax AdtFieldName ::= Identifier
  syntax BBName ::= BBId

  // https://doc.rust-lang.org/reference/expressions/path-expr.html
  syntax PathExpression ::= PathInExpression
                          | QualifiedPathInExpression
  // https://doc.rust-lang.org/reference/paths.html#paths-in-expressions
  syntax PathInExpression ::= "::" ExpressionPathList
                            | ExpressionPathList
  syntax ExpressionPathList ::= NeList{PathExprSegment, "::"}
  syntax PathExprSegment  ::= PathIdentSegment
                            | PathIdentSegment "::" GenericArgs
                            | PathLocation  // MIR-only thing.
                            | TypeImplSegment  // MIR-only thing.
  // https://doc.rust-lang.org/reference/paths.html#qualified-paths
  syntax QualifiedPathInExpression  ::= QualifiedPathType "::" ExpressionPathList

  syntax TypeImplSegment  ::= "<" "impl" NonPathImplementableType ">"


  // TODO: This grammar needs a preprocessing step that removes comments and
  // the textual representation at the end of memory dump lines, e.g. the
  // │ ........ part here:
  // alloc1 (static: RAND_SOURCE, size: 8, align: 8) {
  //   00 00 00 00 00 00 00 00                         │ ........
  // }
  // It should also replace │ by |.
  // For clarity, here are the (VSC) regular expressions for cleaning memory dumps:
  // Replace ^(\s*(?: [0-9a-fA-F][0-9a-fA-F])+)\s+│.*$ with $1
  // Replace ^(\s+0x[0-9a-fA-F]+\s+)│(\s*(?: [0-9a-fA-F][0-9a-fA-F])+)\s+│.*$ with $1|$2



```

```k
endmodule
```

Semantics of MIR types
----------------------

```k
module MIR-TYPES
  imports MIR-HOOKS
  imports MIR-VALUE
endmodule
```

Runtime `MIRValue` types
========================

```k
module MIR-VALUE
  imports INT
  imports STRING
  imports BYTES
  imports MIR-TYPE-SYNTAX
  imports MIR-LEXER-SYNTAX
  imports LIST

  syntax KItem ::= RValueResult
```

Result of interpretation (inspired by [InterpResult](https://github.com/rust-lang/rust/blob/bd43458d4c2a01af55f7032f7c47d7c8fecfe560/compiler/rustc_middle/src/mir/interpret/error.rs#L496)), either a `RValueResult` or an `InterpError`:

```k
  syntax InterpResult ::= RValueResult
                        | InterpError

  syntax RValueResult ::= fromInterpResult(InterpResult) [function]
  //---------------------------------------------------------------
  rule fromInterpResult(VALUE:RValueResult) => VALUE
  rule fromInterpResult(_ERROR:InterpError) => "Error: fromInterpResult --- InterpError encoutered" [owise]
```

The values of `RValueResult` sort represent the evaluation result of the syntactic `RValue`:
TODO: add more domain sorts

```k
  syntax MIRValue ::= Int
                    | String
                    | "Unit"
                    | Bool
                    | "Never"
                    | TupleArgs
                    | "UNIMPLEMENTED"

  syntax TupleArgs ::= "(" MIRValueNeList ")"
  
  syntax RValueResult ::= MIRValue

  syntax MIRValueNeList ::= List
```

The `InteprError` sort represent the errors that may occur while interpreting an `RValue` into `RValueResult` (inspired by [InterpError](https://github.com/rust-lang/rust/blob/bd43458d4c2a01af55f7032f7c47d7c8fecfe560/compiler/rustc_middle/src/mir/interpret/error.rs#L480)):

```k
  syntax InterpError ::= Unsupported(KItem)
```

A best-effort default value inference function, for locals initialization.
**ATTENTION** this function will return `UNIMPLEMENTED` for types that are not handled.

```k
  syntax MIRValue ::= defaultMIRValue(Type) [function]
  //--------------------------------------------------
  rule defaultMIRValue(( ):TupleType) => Unit
  rule defaultMIRValue(usize)         => 0
  rule defaultMIRValue(u8)            => 0
  rule defaultMIRValue(u16)           => 0
  rule defaultMIRValue(u32)           => 0
  rule defaultMIRValue(u64)           => 0
  rule defaultMIRValue(u128)          => 0
  rule defaultMIRValue(isize)         => 0
  rule defaultMIRValue(i8)            => 0
  rule defaultMIRValue(i16)           => 0
  rule defaultMIRValue(i32)           => 0
  rule defaultMIRValue(i64)           => 0
  rule defaultMIRValue(i128)          => 0
  rule defaultMIRValue(bool)          => false
  rule defaultMIRValue(!)             => Never
  rule defaultMIRValue(_:Type)        => UNIMPLEMENTED [owise]
```

```k
endmodule
```

Internal sort casts
-------------------

```k
module MIR-SORT-CASTS
  imports MIR-TYPE-SYNTAX
  imports MIR-RVALUE


  syntax Int ::= castMIRValueToInt(MIRValue) [function]
  //---------------------------------------------------
  rule castMIRValueToInt(X:Int) => X
  rule castMIRValueToInt(true:Bool) => 1
  rule castMIRValueToInt(false:Bool) => 0

  syntax FunctionPath ::= toFunctionPath(PathInExpression) [function]
  //-----------------------------------------------------------------
  rule toFunctionPath(.ExpressionPathList) => .FunctionPath
  rule toFunctionPath(NAME:Identifier :: .ExpressionPathList) => NAME :: .FunctionPath

endmodule
```

Hooked functions
----------------

```k
module MIR-HOOKS
  imports STRING
  imports MIR-SYNTAX
```

We use several hooks which convert between token and string representations:

```k
  syntax String ::= StringLiteral2Sring(StringLiteral) [function, total, hook(STRING.token2string)]
  syntax StringLiteral ::= String2SringLiteral(String) [function, total, hook(STRING.string2token)]

  syntax String ::= LocalToken2String(LocalToken) [function, total, hook(STRING.token2string)]
  syntax LocalToken ::= String2LocalToken(String) [function, total, hook(STRING.string2token)]

  syntax String ::= BBId2String(BBId) [function, total, hook(STRING.token2string)]

  syntax IdentifierToken ::= String2IdentifierToken(String) [function, total, hook(STRING.string2token)]

  syntax String ::= SignedLitertal2String(SignedLiteral) [function, total, hook(STRING.token2string)]
  syntax String ::= UnsignedLitertal2String(UnsignedLiteral) [function, total, hook(STRING.token2string)]
  syntax String ::= StringLitertal2String(StringLiteral) [function, total, hook(STRING.token2string)]
```

Additionally, we need functions that convert between syntactic and semantics representations of several types:

### Locals

```k
  syntax Int ::= Local2Int(Local) [function, total]
  //-----------------------------------------------
  rule Local2Int(LOCAL) => #let STR = LocalToken2String({LOCAL}:>LocalToken) #in String2Int(substrString(STR, 1, lengthString(STR))) [concrete]

  syntax Local ::= Int2Local(Int) [function, total]
  //-----------------------------------------------
  rule Int2Local(I) => String2LocalToken("_" +String Int2String(I))

  syntax Int ::= BBName2Int(BBName) [function, total]
  //-------------------------------------------------
  rule BBName2Int(NAME) => #let STR = BBId2String(NAME) #in String2Int(substrString(STR, 2, lengthString(STR)))
```

### Literals

* Unsigned integer literals

```k
  syntax Int ::= UnsignedLiteral2Int(UnsignedLiteral) [function]
  //------------------------------------------------------------
  rule UnsignedLiteral2Int(LITERAL) =>
    #let     STR = UnsignedLitertal2String(LITERAL)
    #in #let UNDERSCORE_POSITION = findChar(STR, "_", 0)
    #in String2Int(substrString(STR, 0, UNDERSCORE_POSITION))
```

* Signed integer literals

```k
  syntax Int ::= SignedLiteral2Int(SignedLiteral) [function]
  //--------------------------------------------------------
  rule SignedLiteral2Int(LITERAL) =>
    #let     STR = SignedLitertal2String(LITERAL)
    #in #let UNDERSCORE_POSITION = findChar(STR, "_", 0)
    #in String2Int(substrString(STR, 0, UNDERSCORE_POSITION))
```

```k
endmodule
```
