```k
require "mir-types.md"
require "mir-place.md"
```
[`Operand`](https://github.com/rust-lang/rust/blob/e3590fccfbdb6284bded9b70eca2e72b0c57e070/compiler/rustc_middle/src/mir/mod.rs#L1889)

Operands are leafs, i.e. the "basic components" of rvalues: either a loading of a place, or a constant.

```k
module MIR-OPERAND-SYNTAX
  imports MIR-PLACE
  imports MIR-CONSTANT-SYNTAX

  syntax Operand ::= Place
                   | "move" Place
                   | Constant
endmodule
```

```k
module MIR-CONSTANT-SYNTAX
  imports MIR-TYPE-SYNTAX
```

### [`Constant`](https://github.com/rust-lang/rust/blob/e3590fccfbdb6284bded9b70eca2e72b0c57e070/compiler/rustc_middle/src/mir/mod.rs#L2219)
There are three types of constants- 
- constant value from the type system
- constant that are unevaluated, thus not part of the type system
- constant that doesnot go back to type system like pointers.

Literals and const generic parameters are eagerly converted to a constant, everything else becomes `Unevaluated`.

```k
  syntax Constant ::= "const " ConstantValue   //ConstantKind::Ty(ty::Const<'tcx>), ty::Const = rustc_type_ir::ConstKind, https://github.com/rust-lang/rust/blob/c40cfcf0494ff7506e753e750adb00eeea839f9c/compiler/rustc_type_ir/src/sty.rs#L896
                    | "const " "_"             //ConstantKind::Unevaluated(UnevaluatedConst<'tcx>, Ty<'tcx>), const_eval
                    //|                          //ConstantKind::Val(interpret::ConstValue<'tcx>, Ty<'tcx>), used by miri and CTFE, https://github.com/rust-lang/rust/blob/9bd60a60cefdddca1f507083dda37e1664b295c5/compiler/rustc_middle/src/mir/interpret/value.rs#L32

  syntax ConstantValueTree  ::= ConstByteStr   //ty::ConstKind::Value(value:Valtree), ty::ValTree::Branch(_), ty::Ref(_, inner_ty, _), inner_ty match ty::Slice(t)
                          | ConstString    //ty::ConstKind::Value(value:Valtree), ty::ValTree::Branch(_), ty::Ref(_, inner_ty, _), inner_ty match ty::Str
                          | ConstScalarInt  //ty::ConstKind::Value(value:Valtree), (ty::ValTree::Leaf(leaf), _), where _ does not match ty::Ref(_, inner_ty, _). https://github.com/rust-lang/rust/blob/9bd60a60cefdddca1f507083dda37e1664b295c5/compiler/rustc_middle/src/ty/print/pretty.rs#L1469
                         // | ConstScalarPointer
                          | ConstScalarIntRef //ty::ConstKind::Value(value:Valtree), ty::ValTree::Leaf(leaf), ty::Ref(_, inner_ty, _)

  syntax ConstByteStr ::= "b" "\"" String "\""  //escaped ascii, https://github.com/rust-lang/rust/blob/3f8c8f51f777f4fab14074cde975bc4bbce3ca5a/compiler/rustc_middle/src/ty/print/pretty.rs#L1547
  
  syntax ConstString ::= StringLiteral         // What's the difference with String sort

  //TODO: Consider using builtIn Mint sort
  syntax ConstScalarInt ::= Int "_" UintTy     //ty::Uint
                          | Int "_" IntTy      //ty::Int
                          | Bool               //ty::Bool
                          | Float FloatTy      //ty::Float
                          | CharLiteral        //ty::Char
                          | "{" "0x" Int "as" Type "}" //Pointer Types: ty::Ref(..) | ty::RawPtr(_) | ty::FnPtr(_)
                          | "{" "transmute(())" ":" Type "}"            //Other scalaint types.
                          | "{" "transmute(" "0x" Int ")" ":" Type "}"  //Other scalaint types.
                          | Int               //Other scalaint types with no type print.
  syntax ConstScalarIntRef ::= "&" ConstScalarInt

// https://github.com/rust-lang/rust/blob/c5833f1956bea474034ffec5ab2c75f343548038/compiler/rustc_middle/src/ty/consts/int.rs#L28
  syntax MinInt ::= "isize::MIN"   [token]
                  | "i8::MIN"      [token]
                  | "i16::MIN"     [token]
                  | "i32::MIN"     [token]
                  | "i64::MIN"     [token]
                  | "i128::MIN"    [token]

  syntax MaxInt ::= "isize::MAX"   [token]
                  | "i8::MAX"      [token]
                  | "i16::MAX"     [token]
                  | "i32::MAX"     [token]
                  | "i64::MAX"     [token]
                  | "i128::MAX"    [token]

  syntax MinUint ::= "usize::MIN"  [token]
                   | "u8::MIN"     [token]
                   | "u16::MIN"    [token]
                   | "u32::MIN"    [token]
                   | "u64::MIN"    [token]
                   | "u128::MIN"   [token]

  syntax MaxUint ::= "usize::MAX"  [token]
                   | "u8::MAX"     [token]
                   | "u16::MAX"    [token]
                   | "u32::MAX"    [token]
                   | "u64::MAX"    [token]
                   | "u128::MAX"   [token]

  // syntax ConstantValueList ::= List{ConstantValue, ","}

  // syntax ConstEnumConstructor ::= Identifier
  //                               | Identifier "(" ConstantValueList ")"
  //                               | PathExpression "::" Identifier
  //                               | PathExpression "::" Identifier "(" ConstantValueList ")"

  // syntax AllocConstant ::= "{" Identifier ":" Type "}"
  // syntax TransmuteConstant ::= "{" "transmute" "(" HexLiteral ")" ":" Type "}"

  // syntax TupleConstant  ::= "(" ")"
  //                         | "(" ConstantValue "," ConstantValueList ")"

  // syntax AdtConstant ::= Type "{" "{" AdtFieldConstantList "}" "}"
  //                      | Type "{" AdtFieldConstantList "}"
  // syntax AdtFieldConstant ::= AdtFieldName ":" ConstantValue
  // syntax AdtFieldConstantList ::= List{AdtFieldConstant, ","}
endmodule
```