// (very) loosely based on https://rust-lang.github.io/rfcs/1211-mir.html

module MIR-SYNTAX
  imports BOOL
  imports UNSIGNED-INT-SYNTAX

  syntax Mir ::= List{MirComponent, ""}
  syntax MirComponent ::= Function | FunctionForData | DataAlloc | FunctionForPromoted

  syntax Function ::= FunctionSignature "{" FunctionBody "}"
  syntax FunctionSignature ::= "fn" FunctionPath "(" ParameterList ")" "->" Type
  syntax Parameter ::= Local ":" Type
  syntax ParameterList ::= List{Parameter, ","}

  syntax FunctionForData ::= FunctionForDataSignature "{" FunctionBody "}"
  syntax FunctionForDataSignature ::= MaybeStaticConstMut PathFunctionData ":" Type "="
  syntax MaybeStaticConstMut ::= "" | "static" | "const" | "static" "mut"

  syntax FunctionForPromoted ::= FunctionForPromotedSignature "{" FunctionBody "}"
  syntax FunctionForPromotedSignature ::= "promoted" "[" Int "]" "in" FunctionPath ":" Type "="

  // Mir-only, most likely, inspired from PathExpression, FunctionPath and similar.
  syntax PathFunctionData ::= NeList{PathFunctionDataSegment, "::"}
  // TODO: Consider merging PathFunctionDataSegment with FunctionPathComponent
  syntax PathFunctionDataSegment  ::= FunctionPathComponent
                                    | "{" "constant" "#" Int "}"  // anonymous
                                    | Int

  syntax FunctionBody ::= DebugList BindingList ScopeList BasicBlockList
  syntax Binding ::= "let" OptMut Local ":" Type ";"
  syntax BindingList ::= List{Binding, ""}
  syntax OptMut ::= "mut" | ""

  syntax Scope ::= "scope" Int "{" DebugList BindingList ScopeList "}"
  syntax ScopeList ::= List{Scope, ""}

  syntax Debug ::= "debug" UserVariableName "=>" Place ";"
  syntax DebugList ::= List{Debug, ""}

  syntax BasicBlock ::= BB ":" "{" StatementList Terminator ";" "}"
  syntax BasicBlockList ::= List {BasicBlock, ""}

  // https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/syntax.rs#L242
  // https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/mod.rs#L1432
  syntax Statement  ::= Place "=" RValue
                      // FakeRead does not seem to be used
                      | "discriminant" "(" Place ")" "=" Int
                      | "Deinit" "(" Place ")"
                      | "StorageLive" "(" Local ")"
                      | "StorageDead" "(" Local ")"
                      // Retag does not seem to be used
                      // AscribeUserType does not seem to be used
                      // Coverage does not seem to be used
                      | NonDivergingIntrinsic
                      | "ConstEvalCounter"
                      // Nop does not seem to be used
  syntax NonDivergingIntrinsic  ::= "assume" "(" Place ")"
                                  | "copy_nonoverlapping" "(" "dst" "=" RValue "," "src" "=" RValue "," "count" "=" RValue ")"
  syntax TerminatedStatement ::= Statement ";"
  syntax StatementList ::= List {TerminatedStatement, ""}

  // https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/syntax.rs#L532
  // https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/terminator.rs#L300
  syntax Terminator ::= "return"
                      | "unreachable"
                      | "resume"
                      | "goto" "->" BB
                      // TODO: Can this happen for things other than panics?
                      | Place "=" CallLike
                      | Place "=" CallLike "->" TerminatorDestination
                      | CallLike
                      // I only found examples of this for assert and switchInt
                      | CallLike "->" TerminatorDestination

  // https://doc.rust-lang.org/reference/expressions/call-expr.html
  syntax CallLike ::= Callable "(" ArgumentList ")" | AssertCall
  syntax Callable ::= PathExpression | "move" Local
  syntax AssertCall ::= "assert" "(" AssertArgumentList ")"
  syntax AssertArgument ::= BasicRValue | "!" BasicRValue | StringLiteral
  syntax AssertArgumentList ::= NeList{AssertArgument, ","}

  // https://doc.rust-lang.org/reference/expressions/path-expr.html
  syntax PathExpression ::= PathInExpression | QualifiedPathInExpression
  // https://doc.rust-lang.org/reference/paths.html#paths-in-expressions
  syntax PathInExpression ::= "::" ExpressionPathList
                            | ExpressionPathList
  syntax ExpressionPathList ::= NeList{PathExprSegment, "::"}
  syntax PathExprSegment  ::= PathIdentSegment
                            | PathIdentSegment "::" GenericArgsWithName  // GenericArgsWithName is Mir-only.
                            | PathLocation  // Mir-only thing.
                            | SliceImpl  // Mir-only thing.
  // https://doc.rust-lang.org/reference/paths.html#qualified-paths
  syntax QualifiedPathInExpression  ::= QualifiedPathType "::" ExpressionPathList

  syntax SliceImpl ::= "<" "impl" "[" Type "]" ">"

  // TODO: In practice, this is probably a list of a rather restricted vesion
  // of RValue, close to BasicRValue. Consider restricting the sort.
  syntax ArgumentList ::= List{RValue, ","}

  // See
  // kmir/src/tests/integration/test-data/compiletest-rs/ui/closures/old-closure-fn-coerce.cs
  // for some rust code that produces this.
  syntax GenericArgsWithName ::= "<" GenericArgsWithNameList ">"
  syntax GenericArgsWithNameList ::= List{GenericArgWithName, ","}
  syntax GenericArgWithName ::= Type "{" PathExpression "}"
                              | GenericArg

  // Place:
  // https://github.com/rust-lang/rust/blob/master/compiler/rustc_middle/src/mir/syntax.rs#L826
  // Place serialization:
  // https://github.com/rust-lang/rust/blob/master/compiler/rustc_middle/src/mir/mod.rs#L1697
  syntax Place  ::= Local
                  | NonTerminalPlace
  // PlaceElem is ProjectionElem:
  // https://github.com/rust-lang/rust/blob/master/compiler/rustc_middle/src/mir/syntax.rs#L981
  // ProjectionElem:
  // https://github.com/rust-lang/rust/blob/master/compiler/rustc_middle/src/mir/syntax.rs#L826
  syntax NonTerminalPlace ::= "(" "*" Place ")"  // Deref
                            | "(" Place "." Int ":" Type ")"  // Field
                            | Place "[" Local "]"  // Index
                            // | "(" Place "as" Type ")"  // OpaqueCast
                            | "(" Place "as" Type ")"  // Downcast(Some(..), ..)
                            // | "(" Place "as" "variant" "#" Int ")"  // Downcast(None, ..)
                            | Place "[" Int "of" Int "]"  // ConstantIndex { from_end: false }
                            | Place "[" "-" Int "of" Int "]"  // ConstantIndex { from_end: true }
                            | Place "[" Int ":" "]"  // Subslice{to: 0, from_end: true}
                            | Place "[" ":" "-" Int "]"  // Subslice{from: 0, from_end: true}
                            | Place "[" Int ":" "-" Int "]"  // Subslice{from_end: true}
                            | Place "[" Int ".." Int "]"  // Subslice{from_end: false}

  syntax BasicRValue  ::= Local
                        | BasicRValueNoVariable
  syntax BasicRValueNoVariable  ::=  NonTerminalPlace
                                  | "move" Place
                                  | Constant

  syntax RValue ::= BasicRValueNoVariable  [avoid]
                  // It seems that, in practice, this list contains only const
                  // or only move items.
                  | "[" BasicRValueList "]"
                  | "[" BasicRValue ";" ArrayLen "]"
                  | "[" "generator" "@" FilePosition "(" "#" Int ")" "]"
                  | "[" "generator" "@" FilePosition "(" "#" Int ")" "]" "{" StructRValueFieldList "}"
                  | BasicRValue "as" Type "(" RValueTODO1 ")"  [avoid]
                  | PathExpression "as" Type
                  // TODO: The confusion between `PathExpression "as" Type`
                  // and `PathExpression "as" Type "(" RValueTODO1 ")"` is
                  // fairly ugly, it's unclear how to properly disambiguate here.
                  | PathExpression "as" Type "(" RValueTODO1 ")" [avoid]
                  | "&" PtrModifiers Place
                  // TODO: I don't need all branches of NonTerminalPlace,
                  // consider restricting this.
                  | "deref_copy" NonTerminalPlace
                  // TODO: ShallowInitBox may conflict with actual structs.
                  // Currently structs can't be named like that. We should allow
                  // that and disambiguate.
                  | "ShallowInitBox" "(" BasicRValue "," Type ")"

                  | StructRValue
                  | TupleRValue
                  | PathExpression
                  | ClosureRValue
  syntax BasicRValueList ::= List{BasicRValue, ","}

  // TODO: Is "Type" the proper non-terminal here, or is it "ExpressionPath"
  // or "TypePath"?
  syntax StructRValue ::= Type "{" StructRValueFieldList "}"
                        | Type "(" BasicRValueList ")"
  syntax StructRValueField ::= StructFieldName ":" BasicRValue
  syntax StructRValueFieldList ::= List{StructRValueField, ","}

  syntax TupleRValue  ::= "(" ")"
                        | "(" BasicRValue "," BasicRValueList ")"

  // https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/mod.rs#L2108
  syntax ClosureRValue ::= "[" "closure" "@" FilePosition "]"

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
                          | LiteralAsConstant
  syntax ConstantValueList ::= List{ConstantValue, ","}

  syntax AllocConstant ::= "{" Identifier ":" Type "}"
  syntax TransmuteConstant ::= "{" "transmute" "(" HexLiteral ")" ":" Type "}"

  syntax TupleConstant  ::= "(" ")"
                          | "(" ConstantValue "," ConstantValueList ")"

  syntax StructConstant ::= Type "{" "{" StructFieldConstantList "}" "}"
                          | Type "{" StructFieldConstantList "}"
  syntax StructFieldConstant ::= StructFieldName ":" ConstantValue
  syntax StructFieldConstantList ::= List{StructFieldConstant, ","}

  syntax StructParenthesisConstant ::= Type "(" ConstantValueList ")"

  syntax LiteralAsConstant ::= "{" Literal "as" Type "}"

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
  syntax ByteStringLiteral ::= r"b[\\\"]([^\\\"\\\\\\n\\r\\t]|\\\\[\\\"'nrt0\\\\]|\\\\x[0-9a-fA-F][0-9a-fA-F]|\\\\\\n)*[\\\"]"  [token]

  syntax Literal  ::= UnsignedLiteral
                    | SignedLiteral
                    | FloatLiteral
                    | HexLiteral
                    | StringLiteral
                    | CharLiteral
                    | ByteLiteral
                    | ByteStringLiteral

  syntax FilePosition ::= FileLineColumnStartLiteral LineColumnEndLiteral
  syntax FileLineColumnStartLiteral ::= r"[^@ ]+:[0-9]+:[0-9]+:"  [token]
  syntax LineColumnEndLiteral ::= r"[0-9]+:[0-9]+"  [token]

  // https://doc.rust-lang.org/reference/types.html#type-expressions
  syntax Type ::= "(" Type ")"  [bracket]  // TypeNoBounds
                | TypeNoBounds
                | TraitObjectTypeReduced

  syntax TypeList ::= List{Type, ","}

  syntax TypeNoBounds ::= ImplTraitTypeOneBound
                        // In the Rust syntax, ImplTraitTypeReduced is a direct
                        // child of type. For some reason, mir allows `&impl A+B`
                        // so it needs to be a child of TypeNoBounds
                        | ImplTraitTypeReduced
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
                            | "{" "opaque" "#" Int "}"
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
  syntax ArrayType ::= "[" Type ";" ArrayLen "]"
  syntax ArrayLen ::= Int | PathExpression
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

  // https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/pretty.rs#L725
  // https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/pretty.rs#L806
  // https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/pretty.rs#L848
  syntax DataAlloc ::= Identifier "(" MaybeStaticPath "size" ":" Int "," "align" ":" Int ")" "{" DataAllocData "}"
  syntax DataAllocData ::= DataAllocDataShortLine | DataAllocDataLines
  syntax DataAllocElement ::= AllocReferenceToken | DoubleHexDigit | "__"
  syntax DoubleHexDigit ::= Int | DoubleHexDigitNoInt
  syntax DoubleHexDigitNoInt ::= DoubleHexDigitNoIntLetter | DoubleHexDigitNoIntDigit
  syntax AllocReferenceToken ::= r"#\\(-*alloc[0-9]+(?:\\+0x[0-9a-fA-F]+)?-*\\)#"  [token]
  syntax DoubleHexDigitNoIntLetter ::= r"[a-fA-F][0-9a-fA-F]" [token(2)]
  syntax DoubleHexDigitNoIntDigit ::= r"[0-9][a-fA-F]" [token]
  syntax MaybeStaticPath ::= "" | "static" ":" FunctionPath ","
  syntax DataAllocDataShortLine ::= List{DataAllocElement, ""}
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

  // https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/mod.rs#L650
  syntax Local ::= LocalToken

  // https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/mod.rs#L650
  syntax LocalToken ::= r"_[0-9]+"  [token(2)]

  // TODO: Finish implementing the sorts below.

  // TODO: Allow assert and assume as normal identifiers.
  syntax OtherTokens  ::= "align" | "assume"
                        | "body"
                        | "cleanup" | "closure" | "constant"
                        | "copy_nonoverlapping" | "count"
                        | "debug" | "deref_copy" | "discriminant" | "dst"
                        | "generator" | "goto"
                        | "opaque" | "otherwise"
                        | "promoted"
                        | "resume"
                        | "StorageLive" | "StorageDead"
                        | "scope" | "size" | "src" | "success"
                        | "unreachable" | "unwind"
                        | "transmute"
                        | "__"
                        | ConstCastKind
  syntax RValueTODO1 ::= ConstCastKind | Identifier | Identifier "(" RValueTODO1 ")"
  syntax ConstCastKind ::= "IntToInt" | "IntToFloat"
  syntax Abi ::= StringLiteral
  syntax MirOnlyType  ::= "[" "closure" "@" FilePosition "]"
                        | "[" "async" "fn" "body" "@" FilePosition "]"
                        | "[" MaybeStatic "generator" "@" FilePosition "]"
  syntax MaybeStatic ::= "" | "static"

  syntax BBToken ::= r"bb[0-9]+"  [token(2)]
  syntax IdentifierToken ::= r"[_a-zA-Z][_a-zA-Z0-9]*" [token]

  syntax Identifier ::= IdentifierToken | LocalToken | BBToken
                      | DoubleHexDigitNoIntLetter | OtherTokens

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
