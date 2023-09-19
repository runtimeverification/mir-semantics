```k
require "mir-identifiers.md"
require "mir-assert.md"
require "mir-operand.md"
require "mir-place.md"
```
## [Terminators](https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/enum.TerminatorKind.html) occur at the end of a basic block and always transfer control outside the current block: either to a block within the same function or to a block outside of it.

```k
module MIR-TERMINATOR-SYNTAX
  import MIR-IDENTIFIERS
  import MIR-ASSERT-SYNTAX
  import MIR-OPERAND-SYNTAX
  import MIR-PLACE

  syntax Terminator ::= "goto" "->" BBId //TerminatorKind::Goto
                      | "switchInt" "(" Operand ")" "->" "[" SwitchTargets "," OwTarget "]" //Terminator::SwitchInt{Operand, SwitchTargets}
                      | "return"  //&[]
                      | "generator_drop" //&[]
                      | "resume" //&[]
                      | "abort" //TerminatorKind::Terminate, &[]
                      | Place "=" "yield" "(" Operand ")" "->" BBId //TerminatorKind::Yield, Yield { resume: t, drop: Some(ref u), .. } unwind() is always None.
                      | Place "=" "yield" "(" Operand ")" // TerminatorKind::Yield, Yield { resume: t, drop: None, .. }, unwind() is always None.
                      | "unreachale" //TerminatorKind::Unreachale, &[]                     
                      | "drop" Place "->" DropSuccessor//TerminatorKind::Drop                                      
                      // | Place "=" Operand "(" ")" "->" CallSuccessor //TerminatorKind::Call, Case 3_1 and Case 3_3
                      | Place "=" Operand "()" "->" CallSuccessor [group(termCall)] //TerminatorKind::Call, Case 3_1 and Case 3_3
                      | Place "=" Operand "(" ArgList ")" "->" CallSuccessor [group(termCall)] //TerminatorKind::Call, Case 3_1 and Case 3_3
                      | Place "=" Operand "()" [group(termCall)] //TerminatorKind::Call, Case 3_2: Call { target: None, unwind: UnwindAction::Cleanup(ref mut t), .. } -> (0, None) => ""
                      | Place "=" Operand "(" ArgList ")" [group(termCall)] //TerminatorKind::Call, Case 3_2: Call { target: None, unwind: UnwindAction::Cleanup(ref mut t), .. } -> (0, None) => ""
                      | "assert" "(" "!" Operand "," AssertKind ")" "->" AssertSuccessor//Terminator::Assert not 
                      | "assert" "(" Operand "," AssertKind ")" "->" AssertSuccessor //Terminator::Assert expected
                      | "falseEdge" "->" BBId      //FalseEdge { real_target, ref imaginary_target } and unwind() on TerminatorKind::FalseEdge { .. } => None, -> (1, None) => BBId
                      | "falseUnwind" "->" FalseUnwindSuccessor  //TerminatorKind::FalseUnwind
//                      | "asm!({}, )" //TODO:https://github.com/rust-lang/rust/blob/e81522aa0e0bef810c8e8298128a652339c992c3/compiler/rustc_middle/src/mir/terminator.rs#L340

  syntax priorities termCall > rustUnit 

  // https://doc.rust-lang.org/beta/nightly-rustc/rustc_middle/mir/terminator/struct.SwitchTargets.html
  syntax SwitchTargets ::= List{SwitchTarget, ","} //SwitchTargets{values: SmallVec<u128, usize>, targets: SmallVec<BBId, usize>}
  syntax SwitchTarget ::= Int ":" BBId //Int as u128, Int as SwitchTargets.values. SwitchTarget.targets.len = SwitchTarget.value.len + 1
  syntax OwTarget ::= "otherwise" ":" BBId // In rustc, OwTarget's BBId is the last element of the SwitchTargets. Our definition make it an independent branch.

  syntax ArgList ::= List{Operand, ","} //https://github.com/rust-lang/rust/blob/bda32a4023b1d3f96e56e1b2fc7510324f430316/compiler/rustc_middle/src/mir/pretty.rs#L650

  //UnwindAction::Cleanup(BBId) is specially handled as case 1.
  syntax UnwindAction ::= "unwind continue"     //UnwindAction::Continue
                        | "unwind unreachable"  //UnwindAction::Unreachale
                        | "unwind terminate"    //UnwindAction::Terminate
                     
  syntax DropSuccessor ::= BBId // Case 2_1: Drop { target: t, unwind: UnwindAction::Cleanup(ref u), .. } | (1, None) => BBId where unwind():: Some(UnwindAction::Cleanup(_)) => None
                         | "[" "return" ":" BBId "," UnwindAction "]" // case 2_2: Drop { target: t, unwind: _, .. } |  (1, Some(unwind)) => "[return:" BBId, UnwindAction "]" require unwind != CleanUp(_)
  
  syntax CallSuccessor ::= BBId //Case 3_1: Call { target: Some(ref mut t), unwind: UnwindAction::Cleanup(ref mut u), .. } -> (1, None) => BBId
                         | "[" "return" ":" BBId "," UnwindAction "]" //Case 3_3: Call { target: Some(ref mut t), unwind: _, .. } -> (1, UnwindAction) => [return:" BBId "," UnwindAction "]" require UnwindAction != CleanUp(BBId)

  syntax AssertSuccessor ::= BBId//Case 2_1: Assert { target: t, unwind: UnwindAction::Cleanup(ref u), .. } -> (1, None) => BBId
                           | "[" "success:" BBId "," UnwindAction "]" // Case 2_2: Assert { target: t, unwind: _, .. } -> (1, UnwindAction) => "[ success:" BBId "," UnwindAction "]" require UnwindAction != CleanUp

  syntax FalseUnwindSuccessor ::= BBId  //Case 2_1: FalseUnwind { real_target: t, unwind: UnwindAction::Cleanup(ref u) } -> (1, None) => BBId
                       | "[" "real" ":" BBId "," UnwindAction "]"     //Case 2_2: FalseUnwind { real_target: t, unwind: _ } -> (1, UnwindAction) => "[real :" BBId "," UnwindAction "]" requires unwind != CleanUp(_)

endmodule
```
