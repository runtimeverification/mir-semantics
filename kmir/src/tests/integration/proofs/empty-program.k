requires "../../../../k-src/mir.md"

module VERIFICATION
    imports K-EQUAL
    imports BASIC-K
    imports MIR-SYMBOLIC

    // LocalTokens will have parsing error if they are not enumerated here 
    syntax LocalToken ::= "_1" [token]
    syntax LocalToken ::= "_2" [token]
    syntax LocalToken ::= "_3" [token]
    syntax LocalToken ::= "_4" [token]

    syntax BBId ::= "bb0" [token]
endmodule

module EMPTY-PROGRAM
    imports VERIFICATION

    claim 
      <k>
        fn main :: .FunctionPath ( .ParameterList ) -> ( ) { .DebugList let mut _0 : ( ) ;  .BindingList .ScopeList bb0  : { .Statements return ; }  .BasicBlockList }  .Mir ~> .
        =>
        #halt ~> .
      </k>
      <callStack> .List </callStack>
      <returncode> 4 => 0 </returncode> 
      <phase> Initialization => Finalization </phase> 
      <functions> .Bag => ?_ </functions>
endmodule