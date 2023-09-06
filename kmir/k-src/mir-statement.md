```k
require "mir-rvalue.md"
require "mir-identifiers.md"
require "mir-operand.md"
```
# [Statements]
[Statements](https://github.com/rust-lang/rust/blob/e3590fccfbdb6284bded9b70eca2e72b0c57e070/compiler/rustc_middle/src/mir/mod.rs#L1450) occur within a basic block. They are executed in sequence and never transfer control anywhere outside their basic block.

```k
module MIR-STATEMENT-SYNTAX
  imports MIR-PLACE
  imports MIR-RVALUE-SYNTAX
  imports MIR-IDENTIFIERS
  imports COVERAGE-SYNTAX

  syntax Statements ::= List {Statement, ""}

  syntax Statement  ::= Place "=" RValue ";" // StatementKind::Assign
                      | "FakeRead" FakeReadCause "," Place ";" // StatementKind::FakeRead. It is removed before codegen, which should be safe to ignore here?
                      | "Retag" "()" Place ";" //StatementKind::Retag where RetagKindPretty = "" RegtagKind::Default
                      | "Retag" "(" RetagKindPretty ")" Place ";" //StatementKind::Retag
                      | "StorageLive" "(" Local ")" ";" //StatementKind::StorageLive
                      | "StorageDead" "(" Local ")" ";" //StatementKind::StorageDead
                      | "discriminant" "(" Place ")" "=" VariantIdx ";" //StatementKind::SetDiscriminant
                      | "Deinit" "(" Place ")" ";" //StatementKind::Deinit
                      | "PlaceMention" "(" Place ")" ";" //StatementKind::PlaceMention
                      | "AscribeUserType" "(" Place "," Variance "," UserTypeProjection ")" ";" //StatementKind::AscribeUserType
                      | "Coverage" "::" CoverageKind "for" CodeRegion ";" //StatementKind::CoverageKind
                      | "Coverage" "::" CoverageKind ";" //StatementKind::CoverageKind
                      | NonDivergingIntrinsic ";" //StatemetKind::Intrinsic
                      | "ConstEvalCounter" ";" //StatementKind::ConstEvalCounter
                      | "nop" ";" //StatementKind::NOP

  syntax FakeReadCause ::= "ForMatchGuard"  //TODO: Cannot locate the fomatter.
                         | "ForMatchedPlace" DefId 
                         | "ForGuardBinding" 
                         | "ForLet" DefId 
                         | "ForIndex"

  syntax RetagKindPretty ::= "[fn entry]"  //RetagKind::FnEntry
                           | "[2phase]"    //RetagKind::TwoPhase
                           | "[raw]"       //RetagKind::Raw

  //TODO: should move to type or abi
  // https://github.com/rust-lang/rust/blob/ffaa32b7b646c208f20c827655bb98ff9868852e/compiler/rustc_type_ir/src/lib.rs#L785
  syntax Variance ::= "+" //Variance::Covariant 
                    | "-" //Variance::Contravariant
                    | "o" //Variance::Invariant
                    | "*" //Variance::Bivariant

  //TODO: should move to Type.
  syntax UserTypeProjection ::= "UserType" "(" Int ")" // UserTypeProjection.base:UserTypeAnnotationIndex, u32
                              | List{ProjectionElem, ","} // UserTypeProjection.projs: Vec<ProjectionKind>. Not sure which separator should it be, guessed "," since the implementation type is a Vec.

  syntax NonDivergingIntrinsic ::= "assume" "(" Operand ")" // NonDivergingIntrinsic::Assume
                                 | "copy_nonoverlapping" "(" "dst =" Operand "," "src =" Operand "," "count =" Operand ")"
endmodule
```
# [StatementKind::Coverage](https://github.com/rust-lang/rust/blob/master/compiler/rustc_middle/src/mir/coverage.rs)
They are inserted for instrumention, should not cause change the original code's execution result.

```k
module COVERAGE-SYNTAX
  import MIR-IDENTIFIERS

  syntax CoverageKind ::= "Counter" "(" CounterId ")" //CoverageKind::Counter
                        | "Expression" "(" ExpressionId ")" CoverageOperand CoverageOp CoverageOperand //CoverageKind::Expression
                        | "Unreachable" //CoverageKind::Unreachable
  syntax CounterId ::= Int //u32, https://github.com/rust-lang/rust/blob/ffaa32b7b646c208f20c827655bb98ff9868852e/compiler/rustc_middle/src/mir/coverage.rs#L11
  syntax ExpressionId ::= Int  //u32, https://github.com/rust-lang/rust/blob/ffaa32b7b646c208f20c827655bb98ff9868852e/compiler/rustc_middle/src/mir/coverage.rs#L36
  syntax CoverageOperand ::= "Zero" //Coverage::Operand::Zero
                           | "Counter" "(" CounterId ")" //Coverage::Operand::Counter(CounterId)
                           | "Expression" "(" ExpressionId ")" //Coverage::Operand::Expression(ExpressionId)
  syntax CoverageOp ::= "+" //Op::Add
                      | "-" //Op::Subtract
  // syntax CodeRegion ::= FileName ":" CodePosition "-" CodePosition
  syntax CodeRegion ::= "ab" ":" "cd" "-" "ef"
endmodule
```