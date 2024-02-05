requires "verify.k"

module SHOW
    imports VERIFY

    claim [show]:
          <k>
            fn main :: .FunctionPath ( .ParameterList ) -> ( ) { .DebugList let mut _0 : ( ) ;  let  _1 : i32  ;  let mut _2 : bool  ;  let mut _3 : bool  ;  let mut _4 : ! ;  .BindingList scope 1 { debug num => _1 ;  .DebugList .BindingList .ScopeList }  .ScopeList bb0  : { _1 = Add ( const 20_i32 , const 22_i32 ) ;  _3 = Eq ( _1 , const 42_i32 ) ;  _2 = Not ( move _3 ) ;  .Statements switchInt ( move _2 ) -> [ 0 : bb2  , .SwitchTargets , otherwise : bb1  ] ; }  bb1  : { .Statements _4 = core :: panicking :: panic :: .ExpressionPathList ( const "assertion failed: num == 42" , .OperandList ) ; }  bb2  : { .Statements return ; }  .BasicBlockList }  .Mir
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
                  <index> _0 </index>
                  <ty> ( ) </ty>
                  <value> Unit </value>
                  ...
                </localDecl>
                <localDecl>
                  <index> _1 </index>
                  <ty> i32 </ty>
                  <value> 42 </value>
                  ...
                </localDecl>
                <localDecl>
                  <index> _2 </index>
                  <ty> bool </ty>
                  <value> false </value>
                  ...
                </localDecl>
                <localDecl>
                  <index> _3 </index>
                  <ty> bool </ty>
                  <value> false </value>
                  ...
                </localDecl>
                <localDecl>
                  <index> _4 </index>
                  <ty> ! </ty>
                  <value> Never </value>
                  ...
                </localDecl>
                ...
              </localDecls>
              <basicBlocks>
                <basicBlock>
                  <bbName> 0 </bbName>
                  <bbBody> ?_ </bbBody>
                </basicBlock>
                <basicBlock>
                  <bbName> 1 </bbName>
                  <bbBody> ?_ </bbBody>
                </basicBlock>
                <basicBlock>
                  <bbName> 2 </bbName>
                  <bbBody> ?_ </bbBody>
                </basicBlock>
              </basicBlocks>
            </function> 
          </functions>

endmodule