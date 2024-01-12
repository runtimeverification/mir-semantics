requires "verify.k"

module ADD
    imports VERIFY

    claim 
          <k>
            fn main :: .FunctionPath ( .ParameterList ) -> ( ) { .DebugList let mut _0 : ( ) ;  let  _1 : i32  ;  .BindingList scope 1 { debug num => _1 ;  .DebugList .BindingList .ScopeList }  .ScopeList bb0  : { _1 = Add ( const 20_i32 , const 22_i32 ) ;  .Statements return ; }  .BasicBlockList }  .Mir
            =>
            #halt ~> .
          </k>
          <callStack> .List </callStack>
          <returncode> 4 => 0 </returncode> 
          <phase> Initialization => Finalization </phase> 
          <functions> 
            .Bag
          => 
            <function> 
              <fnKey> Fn(main) </fnKey>
              <localDecls>
                <localDecl>
                  <index> 0 </index>
                  ...
                </localDecl>
                <localDecl>
                  <index> 1 </index>
                  <value> 42 </value>
                  ...
                </localDecl>
                ...
              </localDecls>
              <basicBlocks>
                <bbName> 0 </bbName>
                <bbBody> ?_ </bbBody>
              </basicBlocks>
            </function> 
          </functions>

endmodule