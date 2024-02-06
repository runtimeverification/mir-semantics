requires "verify.k"

module EMPTY-PROGRAM
    imports VERIFY

    claim [empty]:
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