requires "verify.k"

module SIMPLE-SPEC
    imports VERIFY

    claim [statement.1]: <k> #executeStatement(_3 = const 5_usize) => .K ...</k>
          <callStack> ListItem(FN_KEY) ... </callStack>
          <function>
            <fnKey> FN_KEY </fnKey>
              <localDecl>
                <index> _3 </index>
                <value> _ => 5 </value>
                ...
              </localDecl>
              ...
          </function>

    claim [statement.2]: <k> #executeStatement(PLACE:Local = const 5_usize) => .K ...</k>
          <callStack> ListItem(FN_KEY) ... </callStack>
          <function>
            <fnKey> FN_KEY </fnKey>
              <localDecl>
                <index> PLACE </index>
                <value> _ => 5 </value>
                ...
              </localDecl>
              ...
          </function>

    claim [statement.3]: <k> #executeStatement(PLACE:Local = Add(const 3_i32, const 5_i32)) => .K ...</k>
          <callStack> ListItem(FN_KEY) ... </callStack>
          <function>
            <fnKey> FN_KEY </fnKey>
              <localDecl>
                <index> PLACE </index>
                <value> _ => 8 </value>
                ...
              </localDecl>
              ...
          </function>

    claim [statement.4]: <k> #executeStatement(_1:Local = move _2) => .K ...</k>
          <callStack> ListItem(FN_KEY) ... </callStack>
          <function>
            <fnKey> FN_KEY </fnKey>
              <localDecl>
                <index> _1 </index>
                <value> _ => 42 </value>
                ...
              </localDecl>
              <localDecl>
                <index> _2 </index>
                <value> 42 </value>
                ...
              </localDecl>
              ...
          </function>

    claim [statements.1]: <k> #executeStatements(PLACE1:Local = Add(const 3_i32, const 5_i32); PLACE2:Local = Add(const 3_i32, const 6_i32);) => .K ...</k>
          <callStack> ListItem(FN_KEY) ... </callStack>
          <function>
            <fnKey> FN_KEY </fnKey>
              <localDecl>
                <index> PLACE1 </index>
                <value> _ => 8 </value>
                ...
              </localDecl>
              <localDecl>
                <index> PLACE2 </index>
                <value> _ => 9 </value>
                ...
              </localDecl>
              ...
          </function>
    requires PLACE1 =/=K PLACE2

    claim [statements.2]: <k> #executeStatements(PLACE:Local = Add(const 3_i32, const 5_i32); PLACE:Local = Add(const 3_i32, const 6_i32);) => .K ...</k>
          <callStack> ListItem(FN_KEY) ... </callStack>
          <function>
            <fnKey> FN_KEY </fnKey>
              <localDecl>
                <index> PLACE </index>
                <value> _ => 9 </value>
                ...
              </localDecl>
              ...
          </function>

    claim [terminator.1]: <k> #executeTerminator(return) => .K ...</k>
    <callStack> ListItem(FN_KEY) REST => REST </callStack>
    <function>
    <fnKey> FN_KEY </fnKey>
      <localDecl>
      <index> _0 </index>
        <value> _RETURN_VALUE </value>
        ...
      </localDecl>
      ...
    </function>
    requires FN_KEY =/=K Fn(main)

    claim [terminator.2]: <k> #executeTerminator(return) => #halt ...</k>
    <returncode> _ => 0 </returncode>
    <phase> Execution => Finalization </phase>
    <callStack> ListItem(Fn(main)) .List => .List </callStack>
    <function>
    <fnKey> Fn(main) </fnKey>
      <localDecl>
      <index> _0 </index>
        <value> Unit </value>
        ...
      </localDecl>
      ...
    </function>

    claim [basicBlock.1]: <k> #executeBasicBlock(Fn(main), INDEX) => #halt ...</k>
    <returncode> _ => 0 </returncode>
    <phase> Execution => Finalization </phase>
    <callStack> ListItem(Fn(main)) .List => .List </callStack>
    <currentBasicBlock> _ => INDEX </currentBasicBlock>
    <functions>
      <function>
      <fnKey> Fn(main) </fnKey>
        <localDecls>
          <localDecl>
          <index> _0 </index>
            <value> Unit </value>
            ...
          </localDecl>
          ...
        </localDecls>
        <basicBlocks>
          <basicBlock>
          <bbName> INDEX </bbName>
            <bbBody> { .Statements return;} </bbBody>
          </basicBlock>
          ...
        </basicBlocks>
      </function>
      ...
    </functions>

    claim [basicBlock.2]: <k> #executeBasicBlock(FN_KEY, INDEX) => .K ...</k>
    <phase> Execution </phase>
    <callStack> ListItem(FN_KEY) REST => REST </callStack>
    <currentBasicBlock> _ => INDEX </currentBasicBlock>
    <functions>
      <function>
      <fnKey> FN_KEY </fnKey>
        <localDecls>
          <localDecl>
          <index> _0 </index>
            <value> _RETURN_CODE </value>
            ...
          </localDecl>
          ...
        </localDecls>
        <basicBlocks>
          <basicBlock>
          <bbName> INDEX </bbName>
            <bbBody> { .Statements return;} </bbBody>
          </basicBlock>
          ...
        </basicBlocks>
      </function>
      ...
    </functions>
    requires FN_KEY =/=K Fn(main)

    claim [basicBlock.3]: <k> #executeBasicBlock(FN_KEY, INDEX) => .K ...</k>
    <phase> Execution </phase>
    <callStack> ListItem(FN_KEY) REST => REST </callStack>
    <currentBasicBlock> _ => INDEX </currentBasicBlock>
    <functions>
      <function>
      <fnKey> FN_KEY </fnKey>
        <localDecls>
          <localDecl>
          <index> _0 </index>
            <value> _RETURN_CODE </value>
            ...
          </localDecl>
          <localDecl>
          <index> _1 </index>
            <value> _ => 8 </value>
            ...
          </localDecl>
          ...
        </localDecls>
        <basicBlocks>
          <basicBlock>
          <bbName> INDEX </bbName>
            <bbBody> { _1 = Add(const 3_usize, const 5_usize); .Statements return;} </bbBody>
          </basicBlock>
          ...
        </basicBlocks>
      </function>
      ...
    </functions>
    requires FN_KEY =/=K Fn(main)

    claim [basicBlock.4]: <k> #executeTerminator(assert(const true, _KIND) -> ((bb2:BBName _):BB)) => .K ...</k>
    <phase> Execution </phase>
    <callStack> ListItem(FN_KEY) REST => REST </callStack>
    <currentBasicBlock> _ => 2 </currentBasicBlock>
    <functions>
      <function>
      <fnKey> FN_KEY </fnKey>
        <localDecls>
          <localDecl>
          <index> _0 </index>
            <value> _RETURN_CODE </value>
            ...
          </localDecl>
          <localDecl>
          <index> _2 </index>
            <value> _ => 8 </value>
            ...
          </localDecl>
          ...
        </localDecls>
        <basicBlocks>
          <basicBlock>
          <bbName> 2 </bbName>
            <bbBody> { _2 = Add(const 3_usize, const 5_usize); .Statements return;} </bbBody>
          </basicBlock>
          ...
        </basicBlocks>
      </function>
      ...
    </functions>
    requires FN_KEY =/=K Fn(main)

    claim [basicBlock.5]: <k> #executeTerminator(assert(_1:Local, _KIND) -> ((bb2:BBName _):BB)) => .K ...</k>
    <phase> Execution </phase>
    <callStack> ListItem(FN_KEY) REST => REST </callStack>
    <currentBasicBlock> _ => 2 </currentBasicBlock>
    <functions>
      <function>
      <fnKey> FN_KEY </fnKey>
        <localDecls>
          <localDecl>
          <index> _0 </index>
            <value> _RETURN_CODE </value>
            ...
          </localDecl>
          <localDecl>
          <index> _1 </index>
            <value> true </value>
            ...
          </localDecl>
          <localDecl>
          <index> _2 </index>
            <value> _ => 8 </value>
            ...
          </localDecl>
          ...
        </localDecls>
        <basicBlocks>
          <basicBlock>
          <bbName> 2 </bbName>
            <bbBody> { _2 = Add(const 3_usize, const 5_usize); .Statements return;} </bbBody>
          </basicBlock>
          ...
        </basicBlocks>
      </function>
      ...
    </functions>
    requires FN_KEY =/=K Fn(main)

    claim [basicBlock.6]: <k> #executeTerminator(assert(PLACE1, _KIND) -> ((bb2:BBName _):BB)) => .K ...</k>
    <phase> Execution </phase>
    <callStack> ListItem(FN_KEY) REST => REST </callStack>
    <currentBasicBlock> _ => 2 </currentBasicBlock>
    <functions>
      <function>
      <fnKey> FN_KEY </fnKey>
        <localDecls>
          <localDecl>
          <index> _0 </index>
            <value> _RETURN_CODE </value>
            ...
          </localDecl>
          <localDecl>
          <index> PLACE1 </index>
            <value> true </value>
            ...
          </localDecl>
          <localDecl>
          <index> PLACE2 </index>
            <value> _ => 8 </value>
            ...
          </localDecl>
          ...
        </localDecls>
        <basicBlocks>
          <basicBlock>
          <bbName> 2 </bbName>
            <bbBody> { PLACE2 = Add(const 3_usize, const 5_usize); .Statements return;} </bbBody>
          </basicBlock>
          ...
        </basicBlocks>
      </function>
      ...
    </functions>
    requires FN_KEY =/=K Fn(main)
      andBool PLACE1 =/=K PLACE2

    claim [basicBlock.7]: <k> #executeTerminator(goto -> ((bb2:BBName _):BB)) => .K ...</k>
    <phase> Execution </phase>
    <callStack> ListItem(FN_KEY) REST => REST </callStack>
    <currentBasicBlock> _ => 2 </currentBasicBlock>
    <functions>
      <function>
      <fnKey> FN_KEY </fnKey>
        <localDecls>
          <localDecl>
          <index> _0 </index> // This is necessary but we don't really want to have to list it I think...
          ...
          </localDecl>
        </localDecls>
        <basicBlocks>
          <basicBlock>
          <bbName> 2 </bbName>
            <bbBody> { .Statements return;} </bbBody>
          </basicBlock>
          ...
        </basicBlocks>
        ...
      </function>
      ...
    </functions>
    requires FN_KEY =/=K Fn(main)

    // claim [terminator]: <k> #executeTerminator(_1 = Fn(temp) ( .OperandList )) -> ((bb2:BBName _):BB) ...</k>
    // <mir>
    //   <simulator>
    //     <callStack> ListItem(Fn(main)) .List </callStack>
    //     <currentBasicBlock> _ => 2 </currentBasicBlock>
    //     ...
    //   </simulator>
    //   <data>
    //     <functions>
    //       <function>
    //       <fnKey> Fn(main) </fnKey>
    //       <localDecls>
    //         <localDecl>
    //         <index> _1 <index>

    //         </localDecl>
    //       </localDecls>
    //       </function>
    //     </functions>
    //   </data>
    // </mir>
endmodule