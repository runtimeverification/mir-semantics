requires "verify.k"

module FUNCTIONS
    imports VERIFY

    claim [function]:
          <k>
            fn add :: .FunctionPath ( _1 : i32  , _2 : i32  , .ParameterList ) -> i32  { debug a => _1 ;  debug b => _2 ;  .DebugList let mut _0 : i32  ;  .BindingList .ScopeList bb0  : { _0 = Add ( _1 , _2 ) ;  .Statements return ; }  .BasicBlockList }  fn main :: .FunctionPath ( .ParameterList ) -> ( ) { .DebugList let mut _0 : ( ) ;  let  _1 : i32  ;  let mut _2 : bool  ;  let mut _3 : bool  ;  let mut _4 : i32  ;  let mut _5 : ! ;  .BindingList scope 1 { debug ans => _1 ;  .DebugList .BindingList .ScopeList }  .ScopeList bb0  : { .Statements _1 = add :: .ExpressionPathList ( const 20_i32 , const 22_i32 , .OperandList ) -> bb1  ; }  bb1  : { _4 = _1 ;  _3 = Eq ( const 42_i32 , move _4 ) ;  _2 = Not ( move _3 ) ;  .Statements switchInt ( move _2 ) -> [ 0 : bb3  , .SwitchTargets , otherwise : bb2  ] ; }  bb2  : { .Statements _5 = core :: panicking :: panic :: .ExpressionPathList ( const "assertion failed: 42 == ans" , .OperandList ) ; }  bb3  : { .Statements return ; }  .BasicBlockList }  .Mir
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
                  <value> ?_ </value>
                  ...
                </localDecl>
                <localDecl>
                  <index> _3 </index>
                  <ty> bool </ty>
                  <value> true </value>
                  ...
                </localDecl>
                <localDecl>
                  <index> _4 </index>
                  <ty> i32 </ty>
                  <value> 42 </value>
                  ...
                </localDecl>
                <localDecl>
                  <index> _5 </index>
                  <ty> ! </ty>
                  <value> ?_ </value>
                  ...
                </localDecl>
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
                <basicBlock>
                  <bbName> 3 </bbName>
                  <bbBody> ?_ </bbBody>
                </basicBlock>
              </basicBlocks>
            </function> 
            <function>
              <fnKey> Fn(add :: .FunctionPath) </fnKey>
              <localDecls>
                <localDecl>
                  <index> _0 </index>
                  <ty> i32 </ty>
                  <value> 42 </value>
                  ...
                </localDecl>
                <localDecl>
                  <index> _1 </index>
                  <ty> i32 </ty>
                  <value> ?_ </value>
                  ...
                </localDecl>
                <localDecl>
                  <index> _2 </index>
                  <ty> ?_ </ty>
                  <value> ?_ </value>
                  ...
                </localDecl>
              </localDecls>
              <basicBlocks>
                <basicBlock>
                  <bbName> 0 </bbName>
                  <bbBody> ?_ </bbBody>
                </basicBlock>
              </basicBlocks>
            </function> 
          </functions>

endmodule