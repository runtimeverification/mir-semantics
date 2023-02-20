// (very) loosely based on https://rust-lang.github.io/rfcs/1211-mir.html

module MIR-SYNTAX
  imports INT

  syntax Mir ::= List{MirComponent, ""}
  syntax MirComponent ::= Function | FunctionForConstant | DataAlloc | FunctionForPromoted

  syntax Function ::= FunctionSignature "{" FunctionBody "}"
  syntax FunctionSignature ::= "fn" FunctionPath "(" ParameterList ")" "->" Type
  syntax Parameter ::= VariableName ":" Type
  syntax ParameterList ::= List{Parameter, ","}

  syntax FunctionForConstant ::= FunctionForConstantSignature "{" FunctionBody "}"
  syntax FunctionForConstantSignature ::= MaybeStaticConst PathFunctionConstant ":" Type "="
  syntax MaybeStaticConst ::= "" | "static" | "const"

  syntax FunctionForPromoted ::= FunctionForPromotedSignature "{" FunctionBody "}"
  syntax FunctionForPromotedSignature ::= "promoted" "[" Int "]" "in" FunctionPath ":" Type "="

  // Mir-only, most likely, inspired from PathExpression, FunctionPath and similar.
  syntax PathFunctionConstant ::= NeList{PathFunctionConstantSegment, "::"}
  syntax PathFunctionConstantSegment  ::= PathExprSegment
                                        | "{" "constant" "#" Int "}"  // anonymous

  syntax FunctionBody ::= DebugList BindingList ScopeList BasicBlockList
  syntax Binding ::= "let" OptMut VariableName ":" Type ";"
  syntax BindingList ::= List{Binding, ""}
  syntax OptMut ::= "mut" | ""

  syntax Scope ::= "scope" Int "{" DebugList BindingList ScopeList "}"
  syntax ScopeList ::= List{Scope, ""}

  syntax Debug ::= "debug" UserVariableName "=>" LValue ";"
  syntax DebugList ::= List{Debug, ""}

  syntax BasicBlock ::= BB ":" "{" StatementList Terminator ";" "}"
  syntax BasicBlockList ::= List {BasicBlock, ""}

  syntax Statement  ::= LValue "=" RValue
                      | "discriminant" "(" VariableName ")" "=" Int
  syntax TerminatedStatement ::= Statement ";"
  syntax StatementList ::= List {TerminatedStatement, ""}

  syntax Terminator ::= "return"
                      | "unreachable"
                      | "resume"
                      | "goto" "->" BB
                      // TODO: Can this happen for things other than panics?
                      | LValue "=" CallLike
                      | LValue "=" CallLike "->" TerminatorDestination
                      | CallLike
                      // I only found examples of this for assert and switchInt
                      | CallLike "->" TerminatorDestination

  // https://doc.rust-lang.org/reference/expressions/call-expr.html
  syntax CallLike ::= Callable "(" ArgumentList ")" | AssertCall
  syntax Callable ::= PathExpression | "move" VariableName
  syntax AssertCall ::= assert(AssertArgumentList)
  syntax AssertArgument ::= BasicRValue | "!" BasicRValue | StringLiteral
  syntax AssertArgumentList ::= NeList{AssertArgument, ","}

  // https://doc.rust-lang.org/reference/expressions/path-expr.html
  syntax PathExpression ::= PathInExpression | QualifiedPathInExpression
  // https://doc.rust-lang.org/reference/paths.html#paths-in-expressions
  syntax PathInExpression ::= "::" ExpressionPathList
                            | ExpressionPathList
  syntax ExpressionPathList ::= NeList{PathExprSegment, "::"}
  syntax PathExprSegment  ::= PathIdentSegment
                            | PathIdentSegment "::" GenericArgs
                            | PathLocation  // Mir-only thing.
  // https://doc.rust-lang.org/reference/paths.html#qualified-paths
  syntax QualifiedPathInExpression  ::= QualifiedPathType "::" ExpressionPathList

  syntax ArgumentList ::= List{BasicRValue, ","}

  syntax LValue ::= VariableName
                  | LValueNoVariable
  syntax LValueNoVariable ::= "(" "*" LValue ")"
                            | "(" LValue "." Int ":" Type ")"
                            | LValue "[" LValue "]"
                            | "(" LValue "as" Type ")"

  syntax BasicRValue  ::= VariableName
                        | BasicRValueNoVariable
  syntax BasicRValueNoVariable  ::=  LValueNoVariable
                                  | "move" LValue
                                  | Constant

  syntax RValue ::= BasicRValueNoVariable  [avoid]
                  // It seems that, in practice, this list contains only const
                  // or only move items.
                  | "[" BasicRValueList "]"
                  | "[" BasicRValue ";" Int "]"
                  | BasicRValue "as" Type "(" RValueTODO1 ")"  [avoid]
                  | PathExpression "as" Type
                  // TODO: The confusion between `PathExpression "as" Type`
                  // and `PathExpression "as" Type "(" RValueTODO1 ")"` is
                  // fairly ugly, it's unclear how to properly disambiguate here.
                  | PathExpression "as" Type "(" RValueTODO1 ")" [avoid]
                  | discriminant(LValue)
                  | "&" PtrModifiers LValue

                  | StructRValue
                  | TupleRValue
                  | PathExpression
  syntax BasicRValueList ::= List{BasicRValue, ","}

  // TODO: Is "Type" the proper non-terminal here, or is it "ExpressionPath"
  // or "TypePath"?
  syntax StructRValue ::= Type "{" StructRValueFieldList "}"
                        | Type "(" BasicRValueList ")"
  syntax StructRValueField ::= StructFieldName ":" BasicRValue
  syntax StructRValueFieldList ::= List{StructRValueField, ","}

  syntax TupleRValue  ::= "(" ")"
                        | "(" BasicRValue "," BasicRValueList ")"

  syntax PtrModifiers ::= "" | "mut" | "raw" "mut" | "raw" "const"

  syntax Constant ::= "const" ConstantValue
  syntax ConstantValue  ::= UnsignedLiteral
                          | SignedLiteral
                          | FloatLiteral
                          | CharLiteral
                          | StringLiteral
                          | ByteLiteral
                          | ByteStringLiteral
                          | Bool
                          | EnumGenericArgumentOrConstConstant
                          | TupleConstant
                          | StructConstant
                          | StructParenthesisConstant
                          | AllocConstant
                          | TransmuteConstant
  syntax ConstantValueList ::= List{ConstantValue, ","}

  syntax AllocConstant ::= "{" Identifier ":" ReferenceType "}"
  syntax TransmuteConstant ::= "{" "transmute" "(" HexLiteral ")" ":" Type "}"

  syntax TupleConstant  ::= "(" ")"
                          | "(" ConstantValue "," ConstantValueList ")"

  syntax StructConstant ::= Type "{" "{" StructFieldConstantList "}" "}"
                          | Type "{" StructFieldConstantList "}"
  syntax StructFieldConstant ::= StructFieldName ":" ConstantValue
  syntax StructFieldConstantList ::= List{StructFieldConstant, ","}

  syntax StructParenthesisConstant ::= Type "(" ConstantValueList ")"

  // Usually enums look like this:
  // _42 = core::panicking::AssertKind::Eq
  // but sometimes like this:
  // _42 = const Ne;
  // Constants look like this:
  // _42 = i32::MAX
  // Template arguments look like this:
  // _42 = const CB_NAME_MAX_LENGTH
  //
  // There is also something strange that looks like this:
  // _42 = const _
  // possibly generated by code like this:
  // fn as_array<T>(slice: &[T]) -> &[T; $len] {
  //     assert_eq!(slice.len(), $len);
  //     unsafe { &*(slice.as_ptr() as *const [_; $len]) }
  // }
  syntax EnumGenericArgumentOrConstConstant ::= Type "::" Identifier
                                              | Identifier

  syntax ConstructorEnum ::= PathExpression "::" Identifier

  syntax FunctionPathComponent  ::= Identifier
                                  | PathLocation
                                  | PathClosure
  syntax FunctionPath ::= List{FunctionPathComponent, "::"}
  syntax PathLocation ::= "<" "impl" "at" FilePosition ">"
  syntax PathClosure ::= "{" "closure" "#" Int "}"

  // Simplified forms of the Rust literals, since MIR does not seem to use the
  // full range.
  // https://doc.rust-lang.org/reference/tokens.html#literals
  syntax UnsignedLiteral ::= r"[0-9]+_(usize|u8|u16|u32|u64|u128)" [token]
  syntax SignedLiteral ::= r"[-]?[0-9]+_(isize|i8|i16|i32|i64|i128)" [token]
  syntax FloatLiteral ::= r"-?[0-9]+(.[0-9]+)?((E|e)(\\+|-)?[0-9]+)?(f32|f64)" [token]
  syntax HexLiteral ::= r"0x[0-9a-fA-F]+"  [token]
  syntax StringLiteral ::= r"[\\\"]([^\\\"\\\\\\n]|\\\\[\\\"'nrt0\\\\]|\\\\x[0-7][0-9a-fA-F]|\\\\u[0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F][0-9a-fA-F]?)?)?)?)?|\\\\\\n)*[\\\"]"  [token]
  syntax CharLiteral ::= r"[']([^\\\"\\\\\\n\\r\\t]|\\\\[\\\"'nrt0\\\\]|\\\\x[0-7][0-9a-fA-F]|\\\\u[0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F][0-9a-fA-F]?)?)?)?)?|\\\\\\n)[']"  [token]
  syntax ByteLiteral ::= r"b[']([^\\\"\\\\\\n\\r\\t]|\\\\[\\\"'nrt0\\\\]|\\\\x[0-7][0-9a-fA-F]|\\\\u[0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F][0-9a-fA-F]?)?)?)?)?|\\\\\\n)[']"  [token]
  syntax ByteStringLiteral ::= r"b[\\\"]([^\\\"\\\\\\n\\r\\t]|\\\\[\\\"'nrt0\\\\]|\\\\x[0-7][0-9a-fA-F]|\\\\\\n)*[\\\"]"  [token]

  syntax FilePosition ::= FileLineColumnStartLiteral LineColumnEndLiteral
  syntax FileLineColumnStartLiteral ::= r"[^@ ]+:[0-9]+:[0-9]+:"  [token]
  syntax LineColumnEndLiteral ::= r"[0-9]+:[0-9]+"  [token]

  // https://doc.rust-lang.org/reference/types.html#type-expressions
  syntax Type ::= "(" Type ")"  [bracket]  // TypeNoBounds
                | TypeNoBounds
                | ImplTraitTypeReduced
                | TraitObjectTypeReduced

  syntax TypeList ::= List{Type, ","}

  syntax TypeNoBounds ::= ImplTraitTypeOneBound
                        | TraitObjectTypeOneBound
                        | TypePath
                        | TupleType
                        | NeverType
                        | RawPointerType
                        | ReferenceType
                        | ArrayType
                        | SliceType
                        // Probably not used in mir: InferredType
                        | QualifiedPathInType
                        | BareFunctionType
                        // Probably not used im mir: MacroInvocation
                        | MirOnlyType
  
  // https://doc.rust-lang.org/reference/types/impl-trait.html
  syntax ImplTraitTypeOneBound ::= "impl" TraitBound
  // https://doc.rust-lang.org/reference/types/trait-object.html
  syntax TraitObjectTypeOneBound ::= "dyn" TraitBound
  // https://doc.rust-lang.org/reference/paths.html#paths-in-types
  syntax TypePath ::= "::" TypePathList
                    | TypePathList
  syntax TypePathList ::= NeList{TypePathSegment, "::"}
  syntax TypePathSegment  ::= PathIdentSegment PathIdentSegmentSuffix
                            | PathIdentSegment "::" PathIdentSegmentSuffix
  syntax PathIdentSegmentSuffix ::= ""
                                  | GenericArgs
                                  | TypePathFn
  syntax PathIdentSegment ::= Identifier | "$crate"
  syntax GenericArgs ::= "<" GenericArgsList ">"
  syntax GenericArgsList ::= List{GenericArg, ","}
  syntax GenericArg ::= Lifetime
                      | Type
                      | GenericArgsConst
                      | GenericArgsBinding
  syntax GenericArgsConst ::= LiteralExpression
                            | "-" LiteralExpression
                            // BlockExpression is likely not used in mir
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

  // https://doc.rust-lang.org/reference/trait-bounds.html
  // TODO: Make this a token.
  // TODO: There are various lifetime-related tokens that I combined into a
  // single one. Consider actually using multiple token types.
  syntax Lifetime ::= "'" Identifier | "'static"
  syntax LifetimeBounds ::= List{Lifetime, "+"}

  // https://doc.rust-lang.org/reference/types/array.html
  syntax ArrayType ::= "[" Type ";" Int "]"
  // https://doc.rust-lang.org/reference/types/slice.html
  syntax SliceType ::= "[" Type "]"
  // https://doc.rust-lang.org/reference/paths.html#qualified-paths
  syntax QualifiedPathInType ::= QualifiedPathType
  syntax QualifiedPathInType ::= QualifiedPathInType "::" TypePathSegment
  syntax QualifiedPathType  ::= "<" Type ">"
                              | "<" Type "as" TypePath ">"
  // https://doc.rust-lang.org/reference/types/function-pointer.html
  syntax BareFunctionType ::= MaybeForLifetimes FunctionTypeQualifiers
                              "fn" "(" FunctionParametersMaybeNamedVariadic ")"
                              MaybeBareFunctionReturnType
  syntax FunctionTypeQualifiers ::= "" | "unsafe" | "extern" Abi | "unsafe" "extern" Abi
  syntax FunctionParametersMaybeNamedVariadic ::= MaybeNamedFunctionParameters
                                                // Not seen in mir: MaybeNamedFunctionParametersVariadic
                                                // TODO: Try to generate this
  syntax MaybeNamedFunctionParameters ::= List {MaybeNamedParam, ","}
  syntax BareFunctionReturnType ::= "->" TypeNoBounds
  syntax MaybeBareFunctionReturnType ::= "" | BareFunctionReturnType
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
  // OuterAttributes are likely not used for GenericParam in mir.
  syntax GenericParam ::= LifetimeParam
                        | TypeParam
                        // ConstParam is likely not used in mir.
  syntax LifetimeParam  ::= Lifetime
                          | Lifetime ":" LifetimeBounds
  syntax TypeParam  ::= Identifier MaybeColonTypeParamBounds MaybeEqualsType
  syntax MaybeColonTypeParamBounds ::= "" | ":" | ":" TypeParamBounds
  syntax MaybeEqualsType ::= "" | "=" Type

  // It is likely that Mir does not use the full syntax for MaybeNamedParam
  syntax MaybeNamedParam ::= Type

  // https://doc.rust-lang.org/reference/expressions/literal-expr.html
  syntax LiteralExpression  ::= CharLiteral
                              | StringLiteral
                              // RawStringLiteral is unlikely to be used in mir
                              | ByteLiteral
                              | ByteStringLiteral
                              // RawByteStringLiteral is unlikely to be used in mir
                              | UnsignedLiteral | Int
                              | FloatLiteral
                              | Bool

  syntax DataAlloc ::= Identifier "(" MaybeStaticIdentifier "size" ":" Int "," "align" ":" Int ")" "{" DataAllocData "}"
  syntax DataAllocData ::= DataAllocDataShortLine | DataAllocDataLines
  syntax DoubleHexDigit ::= Int | DoubleHexDigitNoInt
  syntax DoubleHexDigitNoInt ::= DoubleHexDigitNoIntLetter | DoubleHexDigitNoIntDigit
  syntax DoubleHexDigitNoIntLetter ::= r"[a-fA-F][0-9a-fA-F]" [token(2)]
  syntax DoubleHexDigitNoIntDigit ::= r"[0-9][a-fA-F]" [token]
  syntax MaybeStaticIdentifier ::= "" | "static" ":" Identifier ","
  syntax DataAllocDataShortLine ::= List{DoubleHexDigit, ""}
  syntax DataAllocDataLine ::= HexLiteral "|" DataAllocDataShortLine
  syntax DataAllocDataLines ::= NeList {DataAllocDataLine, ""}

  syntax TerminatorDestination ::= BB | SwitchIntCases | CallDestination | AssertDestination
  syntax SwitchIntCases ::= "[" IntCaseList "," OtherwiseCase "]"
  syntax IntCaseList ::= NeList{IntCase, ","}
  syntax IntCase ::= Int ":" BB
  syntax OtherwiseCase ::= "otherwise" ":" BB
  syntax CallDestination ::= "[" "return" ":" BB "," "unwind" ":" BB "]"
  syntax AssertDestination ::= "[" "success" ":" BB "," "unwind" ":" BB "]"

  syntax BB ::= BBName MaybeBBCleanup
  syntax MaybeBBCleanup ::= "" | "(" "cleanup" ")"

  // TODO: Finish implementing the sorts below.

  syntax RValueTODO1 ::= ConstCastKind | Identifier | Identifier "(" RValueTODO1 ")"
  syntax ConstCastKind ::= "IntToInt" | "IntToFloat"
  syntax Abi ::= StringLiteral
  syntax MirOnlyType ::= "[" "closure" "@" FilePosition "]"

  syntax VariableToken ::= r"_[0-9]+"  [token(2)]
  syntax BBToken ::= r"bb[0-9]+"  [token(2)]
  syntax IdentifierToken ::= r"[_a-zA-Z][_a-zA-Z0-9]*" [token]

  syntax Identifier ::= IdentifierToken | VariableToken | BBToken | DoubleHexDigitNoIntLetter

  syntax VariableName ::= VariableToken
  syntax UserVariableName ::= Identifier
  syntax StructFieldName ::= Identifier
  syntax BBName ::= BBToken

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
endmodule
