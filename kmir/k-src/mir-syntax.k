// (very) loosely based on https://rust-lang.github.io/rfcs/1211-mir.html

module MIR-SYNTAX
  imports INT

  syntax Mir ::= List{MirComponent, ""}
  syntax MirComponent ::= Function | FunctionForConstant

  syntax Function ::= FunctionSignature "{" FunctionBody "}"
  syntax FunctionSignature ::= "fn" FunctionPath "(" ParameterList ")" "->" Type
  syntax Parameter ::= VariableName ":" Type
  syntax ParameterList ::= List{Parameter, ","}

  syntax FunctionForConstant ::= FunctionForConstantSignature "{" FunctionBody "}"
  syntax FunctionForConstantSignature ::= FunctionPath "::" FunctionForConstantName ":" Type "="
  syntax FunctionForConstantName  ::= "{" "constant" "#" Int "}"  // anonymous
                                    | Identifier

  syntax FunctionBody ::= BindingList ScopeList BasicBlockList
  syntax Binding ::= "let" OptMut VariableName ":" Type ";"
  syntax BindingList ::= List{Binding, ""}
  syntax OptMut ::= "mut" | ""

  syntax Scope ::= "scope" Int "{" DebugList BindingList ScopeList "}"
  syntax ScopeList ::= List{Scope, ""}

  syntax Debug ::= "debug" UserVariableName "=>" VariableName ";"
  syntax DebugList ::= List{Debug, ""}

  syntax BasicBlock ::= BB ":" "{" StatementList Terminator ";" "}"
  syntax BasicBlockList ::= List {BasicBlock, ""}

  syntax Statement  ::= LValue "=" RValue
                      | "discriminant" "(" VariableName ")" "=" Int
  syntax TerminatedStatement ::= Statement ";"
  syntax StatementList ::= List {TerminatedStatement, ""}

  syntax Terminator ::= "return"
                      | "goto" "->" BB
                      // TODO: Can this happen for things other than panics?
                      | LValue "=" CallLike
                      | LValue "=" CallLike "->" TerminatorDestination
                      | CallLike
                      // I only found examples of this for assert and switchInt
                      | CallLike "->" TerminatorDestination

  syntax CallLike ::= CallFunctionPath "(" ArgumentList ")"

  // https://doc.rust-lang.org/reference/paths.html#paths-in-expressions
  syntax CallFunctionPath ::= FunctionPath
                            | FunctionPath GenericArguments

  syntax GenericArguments ::= "<" GenericArgumentList ">"
  syntax GenericArgumentList ::= List{Type, ","}
  syntax ArgumentList ::= List{BasicRValue, ","}

  syntax LValue ::= VariableName
                  | "(" "*" LValue ")"
                  | "(" LValue "." Int ":" Type ")"
                  | LValue "[" LValue "]"
                  | "(" VariableName "as" Type ")"

  syntax BasicRValue  ::= LValue
                        | discriminant(LValue)
                        | "move" LValue
                        | "&" PtrModifiers LValue
                        | Constant

  syntax RValue ::= BasicRValue
                  // It seems that, in practice, this list contains only const
                  // or only move items.
                  | "[" BasicRValueList "]"
                  | BasicRValue "as" Type "(" RValueTODO1 ")"

                  | "Neg" "(" BasicRValue ")"
                  | "CheckedMul" "(" BasicRValue "," BasicRValue ")"
                  | "Div" "(" BasicRValue "," BasicRValue ")"
                  | "Rem" "(" BasicRValue "," BasicRValue ")"
                  | "CheckedAdd" "(" LValue "," LValue ")"
                  | "CheckedSub" "(" BasicRValue "," BasicRValue ")"

                  | "BitAnd" "(" BasicRValue "," BasicRValue ")"
                  | "BitOr" "(" BasicRValue "," BasicRValue ")"
                  | "BitXor" "(" BasicRValue "," BasicRValue ")"
                  | "CheckedShl" "(" BasicRValue "," BasicRValue ")"
                  | "CheckedShr" "(" BasicRValue "," BasicRValue ")"

                  | "Eq" "(" BasicRValue "," BasicRValue ")"
                  | "Ne" "(" BasicRValue "," BasicRValue ")"
                  | "Gt" "(" BasicRValue "," BasicRValue ")"
                  | "Ge" "(" BasicRValue "," BasicRValue ")"
                  | "Lt" "(" BasicRValue "," BasicRValue ")"
                  | "Le" "(" BasicRValue "," BasicRValue ")"

                  | "Not" "(" BasicRValue ")"

                  | "Len" "(" LValue ")"


  syntax BasicRValueList ::= List{BasicRValue, ","}
  syntax PtrModifiers ::= "" | "mut" | "raw" "mut" | "raw" "const"

  syntax Constant ::= "const" ConstantValue
  syntax ConstantValue  ::= UnsignedLiteral
                          | SignedLiteral
                          | FloatLiteral
                          | CharLiteral
                          | StringLiteral
                          | ByteStringLiteral
                          | Bool
                          | EnumGenericArgumentOrConstConstant
                          | EnumGenericConstCastConstant
                          | EmptyTuple
                          | StructConstant
                          | StructParenthesisConstant
                          | AllocConstant
                          | TransmuteConstant
  syntax ConstantValueList ::= List{ConstantValue, ","}

  syntax AllocConstant ::= "{" Identifier ":" ReferenceType "}"
  syntax TransmuteConstant ::= "{" "transmute" "(" HexLiteral ")" ":" Type "}"

  syntax StructConstant ::= Type "{" "{" StructFieldConstantList "}" "}"
  syntax StructFieldConstant ::= StructFieldName ":" ConstantValue
  syntax StructFieldConstantList ::= List{StructFieldConstant, ","}

  syntax StructParenthesisConstant ::= Type "(" ConstantValueList ")"

  syntax EmptyTuple ::= "(" ")"

  syntax EnumGenericConstCastConstant ::= EnumGenericArgumentOrConstConstant "as" Type "(" ConstCastKind ")"
  syntax ConstCastKind ::= "IntToInt" | "IntToFloat"
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

  syntax FunctionPathComponent  ::= Identifier
                                  | PathLocation
  syntax FunctionPath ::= List{FunctionPathComponent, "::"}
  syntax PathLocation ::= "<impl" "at" FileLineColumnStartLiteral LineColumnEndLiteral ">"

  // Simplified forms of the Rust literals, since MIR does not seem to use the
  // full range.
  // https://doc.rust-lang.org/reference/tokens.html#literals
  syntax UnsignedLiteral ::= r"[0-9]+_(usize|u8|u16|u32|u64|u128)" [token]
  syntax SignedLiteral ::= r"[-]?[0-9]+_(isize|i8|i16|i32|i64|i128)" [token]
  syntax FloatLiteral ::= r"-?[0-9]+(.[0-9]+)?((E|e)(\\+|-)?[0-9]+)?(f32|f64)" [token]
  syntax HexLiteral ::= r"0x[0-9a-fA-F]+"  [token]
  syntax StringLiteral ::= r"[\\\"]([^\\\"\\\\\\n]|\\\\[\\\"'nrt0\\\\]|\\\\x[0-7][0-9a-fA-F]|\\\\u[0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F][0-9a-fA-F]?)?)?)?)?|\\\\\\n)*[\\\"]"  [token]
  syntax CharLiteral ::= r"[']([^\\\"\\\\\\n\\r\\t]|\\\\[\\\"'nrt0\\\\]|\\\\x[0-7][0-9a-fA-F]|\\\\u[0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F]([0-9a-fA-F][0-9a-fA-F]?)?)?)?)?|\\\\\\n)[']"  [token]
  syntax ByteStringLiteral ::= r"b[\\\"]([^\\\"\\\\\\n\\r\\t]|\\\\[\\\"'nrt0\\\\]|\\\\x[0-7][0-9a-fA-F]|\\\\\\n)*[\\\"]"  [token]
  syntax FileLineColumnStartLiteral ::= r"\\/.+:[0-9]+:[0-9]+:"  [token]
  syntax LineColumnEndLiteral ::= r"[0-9]+:[0-9]+"  [token]

  // https://doc.rust-lang.org/reference/types.html#type-expressions
  syntax Type ::= "(" Type ")"  [bracket]  // TypeNoBounds
                | TypeNoBounds
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
  
  // https://doc.rust-lang.org/reference/types/impl-trait.html
  syntax ImplTraitTypeOneBound ::= "impl" TraitBound
  // https://doc.rust-lang.org/reference/types/trait-object.html
  syntax TraitObjectTypeOneBound ::= "dyn" TraitBound
  // https://doc.rust-lang.org/reference/paths.html#paths-in-types
  syntax TypePath ::= "::" TypePathList
                    | TypePathList
  syntax TypePathList ::= NeList{TypePathSegment, "::"}

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
  syntax Lifetime ::= "'" Identifier

  // https://doc.rust-lang.org/reference/types/array.html
  syntax ArrayType ::= "[" Type ";" Int "]"
  // https://doc.rust-lang.org/reference/types/slice.html
  syntax SliceType ::= "[" Type "]"
  // https://doc.rust-lang.org/reference/paths.html#qualified-paths
  syntax QualifiedPathInType ::= QualifiedPathType
  syntax QualifiedPathInType ::= QualifiedPathInType "::" TypePathSegment
  syntax QualifiedPathType  ::= "<" Type ">"
                              | "<" Type "as" TypePath ">"

  // TODO: Finish implementing the sorts below.

  syntax TypePathSegment ::= Identifier
  syntax TraitBound ::= Identifier
  syntax TerminatorDestination ::= BB
  syntax RValueTODO1 ::= Identifier | Identifier "(" RValueTODO1 ")"

  syntax Identifier ::= r"[_a-zA-Z][_a-zA-Z0-9]*" [token]
  syntax VariableName ::= Identifier
  syntax UserVariableName ::= Identifier
  syntax StructFieldName ::= Identifier
  syntax BB ::= Identifier
endmodule
