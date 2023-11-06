```k
require "mir-syntax.md"
require "mir-configuration.md"
require "mir-operand.md"
```

Syntax of rvalues
-----------------

Rvalues are expression that appear on a right-hand-side of an assignment statement.

```k
module MIR-RVALUE-SYNTAX
  imports BOOL
  imports UNSIGNED-INT-SYNTAX
  imports MIR-TYPE-SYNTAX
  imports MIR-OPERAND-SYNTAX
```

### [`RValue`](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/enum.Rvalue.html)

The various kinds of rvalues that can appear in MIR.

```k
  syntax RValue ::= Use
                  | Repeat
                  | Ref
//                  | ThreadLocalRef
                  | AddressOf
                  | Len
                  | Cast
                  | NullaryOp
                  | UnaryOp
                  | BinaryOp
                  | Discriminant
                  | Aggregate
                  | ShallowInitBox
                  | CopyForDeref

  syntax Use    ::= Operand

  syntax Repeat ::= "[" Operand ";" Constant "]"
                  | "[" Operand ";" RustExpression "]" [avoid]
  syntax Ref // TODO: define

  // this seems to be responsible for function pointer assignmetn, e.g. `_1 = fn_name`
//  syntax ThreadLocalRef ::= PathExpression

  syntax AddressOf ::= "&" PtrModifiers Place

  syntax Len ::= "Len" "(" Place ")"

  // TODO: this needs additional productions
  syntax Cast ::= Operand "as" Type [prefer]
                | Operand "as" Type  "(" PointerCastArg ")" [prefer]
                | PathExpression "as" Type
                | PathExpression "as" Type "(" PointerCastArg ")"

  syntax PointerCastArg ::= "Pointer" "(" PointerCast ")"
  syntax PointerCast ::= "ReifyFnPointer"
                       | "UnsafeFnPointer"
                       | "ClosureFnPointer" "(" Unsafety ")"
                       | "MutToConstPointer"
                       | "ArrayToPointer"
                       | "Unsize"

  syntax Unsafety ::= "Unsafe" | "Normal"

  syntax NullaryOp ::= NullaryOpName "(" Type ")"
  syntax NullaryOpName ::= "SizeOf"  [token]
                         | "AlignOf" [token]  

  syntax UnaryOp ::= UnaryOpName "(" Operand ")"
  syntax UnaryOpName ::= "Not" [token]
                       | "Neg" [token]

  syntax BinaryOp ::= BinaryOpName "(" Operand "," Operand ")"
  syntax BinaryOpName ::= "Add"    [token]
                        | "Sub"    [token]
                        | "Mul"    [token]
                        | "Div"    [token]
                        | "Rem"    [token]
                        | "BitXor" [token]
                        | "BitAnd" [token]
                        | "BitOr"  [token]
                        | "Shl"    [token]
                        | "Shr"    [token]
                        | "Eq"     [token]
                        | "Lt"     [token]
                        | "Le"     [token]
                        | "Ne"     [token]
                        | "Ge"     [token]
                        | "Gt"     [token]
                        | "Offset" [token]
                        
  syntax Discriminant ::= "discriminant" "(" Place ")"

  syntax CopyForDeref ::= "deref_copy" NonTerminalPlace

  syntax Aggregate ::= Array
                     | Tuple
                     | Adt
                     | Closure
                     | Generator

  syntax Array ::= "[" "]"
                 | "[" Operand "]"
                 | "[" Operand "," OperandList "]"

  syntax Tuple  ::= "(" ")"
                  | "(" Operand "," OperandList ")"

  syntax Adt ::= StructConstructor
               | EnumConstructor

  syntax StructConstructor ::= Type "{" AdtFieldList "}"
                            //  | TypePath "(" OperandList ")" // compiletest-rs/ui/traits/copy-requires-self-wf.mir LINE 17

  // `AssertKind` `Eq`, `Ne` conflict with BinaryOp names https://github.com/rust-lang/rust/blob/f562931178ff103f23b9e9a10dc0deb38e0d064f/library/core/src/panicking.rs#L259-L263
  syntax EnumConstructor ::= Identifier
                           | Identifier "(" OperandList ")"
                           | PathExpression "::" Identifier [avoid]
                           | PathExpression "::" "Eq"
                           | PathExpression "::" "Ne"
                          //  | PathExpression "::" "Match" // Match isn't conflicting at the moment but might later
                           | PathExpression "::" Identifier "(" OperandList ")"

  syntax AdtField ::= AdtFieldName ":" Operand
  syntax AdtFieldList ::= List{AdtField, ","}

  syntax Closure ::= "[" "closure" "@" FilePosition "]"

  syntax Generator ::= "[" "generator" "@" FilePosition "(" "#" Int ")" "]"
                     | "[" "generator" "@" FilePosition "(" "#" Int ")" "]" "{" AdtFieldList "}"

  syntax ShallowInitBox ::= "ShallowInitBox" "(" Operand "," Type ")"

  syntax OperandList ::= List{Operand, ","}

  syntax PtrModifiers ::= "" | "mut" | "raw" "mut" | "raw" "const"

  syntax RValue ::= #unwrap(Operand)
```

```k
endmodule
```

Evaluation of rvalues
---------------------

```k
module MIR-RVALUE
  imports MIR-RVALUE-SYNTAX
  imports MIR-TYPES
  imports MIR-CONFIGURATION
  imports LIST
```

Evaluate a syntactic `RValue` into a semantics `RValueResult`. Inspired by [eval_rvalue_into_place](https://github.com/rust-lang/rust/blob/bd43458d4c2a01af55f7032f7c47d7c8fecfe560/compiler/rustc_const_eval/src/interpret/step.rs#L148).

```k
  syntax InterpResult ::= evalRValue(FunctionLikeKey, RValue) [function]
  //--------------------------------------------------------------------
  rule evalRValue(FN_KEY, VALUE:Operand)    => evalOperand(FN_KEY, VALUE)
  rule evalRValue(FN_KEY, UN_OP:UnaryOp)    => evalUnaryOp(FN_KEY, UN_OP)
  rule evalRValue(FN_KEY, BIN_OP:BinaryOp)  => evalBinaryOp(FN_KEY, BIN_OP)
  rule evalRValue(FN_KEY, ADDR:AddressOf)   => evalAddressOf(FN_KEY, ADDR)
  rule evalRValue(FN_KEY, CFD:CopyForDeref) => evalCopyForDeref(FN_KEY, CFD)
  rule evalRValue(FN_KEY, TUP:Tuple)        => evalTuple(FN_KEY, TUP)
  rule evalRValue(FN_KEY, ENUM:EnumConstructor) => evalEnumConstructor(FN_KEY, ENUM) [priority(51)]
  rule evalRValue(_FN_KEY, RVALUE)          => Unsupported(RVALUE) [owise]

  rule evalRValue(FN_KEY, #unwrap(OP))      => evalUnwrap(evalOperand(FN_KEY, OP)) 
```

### `Operand` evaluation

```k
  syntax MIRValue ::= evalOperand(FunctionLikeKey, Operand) [function]
  //------------------------------------------------------------------
  rule evalOperand(_, const VALUE:ConstantValue) => evalConstantValue(VALUE)
  rule evalOperand(FN_KEY, FIELD:Field)          => evalField(FN_KEY, FIELD)
  rule evalOperand(FN_KEY, LOCAL:Local)          => evalLocal(FN_KEY, LOCAL)
  rule evalOperand(FN_KEY, move LOCAL:Local)     => evalLocal(FN_KEY, LOCAL)
  rule evalOperand(FN_KEY, REF:Deref)            => evalDeref(FN_KEY, REF)

  syntax MIRValueNeList ::= evalOperandList(FunctionLikeKey, OperandList) [function]
  //--------------------------------------------------------------------------------
  rule evalOperandList(_FN_KEY, .OperandList) => .List
  rule evalOperandList(FN_KEY, OPERAND:Operand, REST:OperandList) => ListItem(evalOperand(FN_KEY, OPERAND)) {evalOperandList(FN_KEY, REST)}:>List
```

### `UnaryOp` evaluation

```k
  syntax MIRValue ::= evalUnaryOp(FunctionLikeKey, UnaryOp) [function]
  //------------------------------------------------------------------
  rule evalUnaryOp(FN_KEY, NAME:UnaryOpName (X:Operand)) =>
       evalUnaryOpImpl(FN_KEY, NAME, X)

  syntax MIRValue ::= evalUnaryOpImpl(FunctionLikeKey, UnaryOpName, Operand) [function]
  //-----------------------------------------------------------------------------------
  rule evalUnaryOpImpl(FN_KEY, Not, X)    => notBool {evalOperand(FN_KEY, X)}:>Bool
  rule evalUnaryOpImpl(FN_KEY, Neg, X)    => 0 -Int {evalOperand(FN_KEY, X)}:>Int
```

### `BinaryOp` evaluation

```k
  syntax MIRValue ::= evalBinaryOp(FunctionLikeKey, BinaryOp) [function]
  //--------------------------------------------------------------------
  rule evalBinaryOp(FN_KEY, NAME:BinaryOpName (X:Operand, Y:Operand)) =>
       evalBinaryOpImpl(FN_KEY, NAME, X, Y)

  syntax MIRValue ::= evalBinaryOpImpl(FunctionLikeKey, BinaryOpName, Operand, Operand) [function]
  //-----------------------------------------------------------------------
  rule evalBinaryOpImpl(FN_KEY, Add, X, Y)    => {evalOperand(FN_KEY, X)}:>Int +Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, Sub, X, Y)    => {evalOperand(FN_KEY, X)}:>Int -Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, Mul, X, Y)    => {evalOperand(FN_KEY, X)}:>Int *Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, Div, X, Y)    => {evalOperand(FN_KEY, X)}:>Int /Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, Rem, X, Y)    => {evalOperand(FN_KEY, X)}:>Int %Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, BitXor, X, Y) => {evalOperand(FN_KEY, X)}:>Int xorInt {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, BitOr, X, Y)  => {evalOperand(FN_KEY, X)}:>Int |Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, BitAnd, X, Y) => {evalOperand(FN_KEY, X)}:>Int &Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, Shl, X, Y)    => {evalOperand(FN_KEY, X)}:>Int <<Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, Shr, X, Y)    => {evalOperand(FN_KEY, X)}:>Int >>Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, Eq, X, Y)     => {evalOperand(FN_KEY, X)}:>Int ==Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, Lt, X, Y)     => {evalOperand(FN_KEY, X)}:>Int <Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, Le, X, Y)     => {evalOperand(FN_KEY, X)}:>Int <=Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, Ne, X, Y)     => {evalOperand(FN_KEY, X)}:>Int =/=Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, Ge, X, Y)     => {evalOperand(FN_KEY, X)}:>Int >=Int {evalOperand(FN_KEY, Y)}:>Int
  rule evalBinaryOpImpl(FN_KEY, Gt, X, Y)     => {evalOperand(FN_KEY, X)}:>Int >Int {evalOperand(FN_KEY, Y)}:>Int
  // rule evalBinaryOpImpl(FN_KEY, _, X, Y) => "not supported" [owise]
```

### Constant evaluation.
//TODO: implement other cases.

```k
  syntax MIRValue ::= evalConstantValue(ConstantValue) [function]
  //-------------------------------------------------------------
  rule evalConstantValue(VALUE:UnsignedLiteral) => UnsignedLiteral2Int(VALUE)
  rule evalConstantValue(VALUE:SignedLiteral)   => SignedLiteral2Int(VALUE)
  rule evalConstantValue(VALUE:StringLiteral)   => StringLitertal2String(VALUE)
  rule evalConstantValue(( ))                   => Unit
  rule evalConstantValue(VALUE:Bool)            => VALUE
  rule evalConstantValue(VALUE:ConstEnumConstructor)  => evalPrimitiveBound(VALUE)
//  rule evalConstantValue(_VALUE)              => "Error: evalConstantValue --- unsupported ConstantValue" [owise]
```

#### Primitive type bounds TODO: usize depends on architecture, which we currently do not handle

```k
  syntax Int ::= evalPrimitiveBound(ConstEnumConstructor) [function]
  syntax Int ::= maxUint(UintTy) [function]
  syntax Int ::= maxInt(IntTy)   [function]
  syntax Int ::= minInt(IntTy)   [function]
  //----------------------------------------------------------
  rule evalPrimitiveBound((UINT:UintTy :: .ExpressionPathList :: MAX):ConstEnumConstructor)  => maxUint(UINT) requires IdentifierToken2String(MAX) ==String "MAX"
  rule evalPrimitiveBound((_:UintTy :: .ExpressionPathList :: MIN):ConstEnumConstructor)  => 0 requires IdentifierToken2String(MIN) ==String "MIN"
  rule maxUint(u8)   => 255
  rule maxUint(u16)  => 65535
  rule maxUint(u32)  => 4294967295
  rule maxUint(u64)  => 18446744073709551615
  rule maxUint(u128) => 340282366920938463463374607431768211455

  rule evalPrimitiveBound((INT:IntTy :: .ExpressionPathList :: MAX):ConstEnumConstructor)  => maxInt(INT) requires IdentifierToken2String(MAX) ==String "MAX"
  rule evalPrimitiveBound((INT:IntTy :: .ExpressionPathList :: MIN):ConstEnumConstructor)  => minInt(INT) requires IdentifierToken2String(MIN) ==String "MIN"
  rule maxInt(i8)   => 127
  rule maxInt(i16)  => 32767
  rule maxInt(i32)  => 2147483647
  rule maxInt(i64)  => 9223372036854775807
  rule maxInt(i128) => 170141183460469231731687303715884105727
  rule minInt(i8)   => -128
  rule minInt(i16)  => -32768
  rule minInt(i32)  => -2147483648
  rule minInt(i64)  => -9223372036854775808
  rule minInt(i128) => -170141183460469231731687303715884105728
```

### `Local` evaluation

Locals only makes sense within a function-like, hence we evaluate them as a contextual function that grabs the value from the function-like's environment:

```k
  syntax MIRValue ::= evalLocal(FunctionLikeKey, Local) [function]
  //--------------------------------------------------------------
  rule [[ evalLocal(FN_KEY, LOCAL) => VALUE ]]
    <function>
      <fnKey> FN_KEY </fnKey>
      <localDecl>
        <index> INDEX </index>
        <value> VALUE </value>
        ...
      </localDecl>
      ...
    </function>
    requires  INDEX ==Int Local2Int(LOCAL)
```

### `Reference and Deref` evaluation

```k
  // TODO: These assumes PLACE is a Local, need to handle other options
  syntax MIRValue ::= evalAddressOf(FunctionLikeKey, AddressOf) [function]
  //----------------------------------------------------------------------
  rule [[ evalAddressOf(FN_KEY, & _PtrModifiers PLACE) => INDEX ]]
    <function>
      <fnKey> FN_KEY </fnKey>
      <localDecl>
        <index> INDEX </index>
        ...
      </localDecl>
      ...
    </function>
    requires INDEX ==Int Local2Int(PLACE)

  syntax MIRValue ::= evalDeref(FunctionLikeKey, Deref) [function]
  //--------------------------------------------------------------
  rule [[ evalDeref(FN_KEY, ( * PLACE)) => VALUE ]]
    <function>
      <fnKey> FN_KEY </fnKey>
        <localDecl>
          <index> REF </index>
          <value> INDEX </value>
          ...
        </localDecl>
        <localDecl>
          <index> INDEX </index>
          <value> VALUE </value>
          ...
        </localDecl>
      ...
    </function>
    requires REF ==Int Local2Int(PLACE)

  // TODO: Investigate if this requires some more checks or effects. Needs to cover more cases.
  syntax MIRValue ::= evalCopyForDeref(FunctionLikeKey, CopyForDeref) [function]
  //----------------------------------------------------------------------------
  rule evalCopyForDeref(FN_KEY, deref_copy(DEREF:Deref)) => evalDeref(FN_KEY, DEREF)
```

### `Aggregate` evaluation

```k
  syntax MIRValue ::= evalTuple(FunctionLikeKey, Tuple) [function]
  //--------------------------------------------------------------
  rule evalTuple(FN_KEY, ( OPERANDS , OperandList )) => ( evalOperandList(FN_KEY, OPERANDS, OperandList) )
```

### `Field` evaluation
```k
  syntax MIRValue ::= TupleArgs "[" Int "]" [function]
  rule ( ARGS:List ) [ INDEX ] => {ARGS[INDEX]}:>MIRValue

  syntax MIRValue ::= evalField(FunctionLikeKey, Field) [function]
  //--------------------------------------------------------------
  rule [[ evalField(FN_KEY, ( PLACE . INDEX : _TYPE ) ) => TUPLE[INDEX] ]] // Ignoring type currently
    <function>
      <fnKey> FN_KEY </fnKey>
        <localDecl>
          <index> PLACE_INDEX </index>
          <value> TUPLE </value>
          ...
        </localDecl>
      ...
    </function>
    requires PLACE_INDEX ==Int Local2Int(PLACE)
```

### `Enum` evaluation
```k
  syntax MIRValue ::= evalEnumConstructor(FunctionLikeKey, EnumConstructor) [function]
  //--------------------------------------------------------------
  rule evalEnumConstructor(FN_KEY, Option :: < _TYPES > :: .ExpressionPathList :: Some ( OP , .OperandList ) ) => OptSome(evalOperand(FN_KEY, OP:Operand))
    requires IdentifierToken2String(Option) ==String "Option" andBool IdentifierToken2String(Some) ==String "Some"
  rule evalEnumConstructor(_FN_KEY, Option :: < _TYPES > :: .ExpressionPathList :: None ) => OptNone
    requires IdentifierToken2String(Option) ==String "Option" andBool IdentifierToken2String(None) ==String "None"
```

### Internal Functions
```k
  syntax MIRValue ::= evalUnwrap(MIRValue) [function]
  //-------------------------------------------------
  rule evalUnwrap(OptSome( VALUE:MIRValue )) => VALUE
```

```k
endmodule
```
