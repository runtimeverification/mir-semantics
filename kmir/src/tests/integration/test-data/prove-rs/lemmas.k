requires "verify.k"

module LEMMAS
    imports VERIFY

    // For testing
    // claim <k> runLemma(isRValueResult(_:RValueResult)) => doneLemma(true) ...</k>
    // claim <k> runLemma(isRValueResult(_:MIRValue))     => doneLemma(true) ...</k>

    // claim [passing1]: 
    // <k> runLemma(isRValueResult(evalLocal(FN_KEY, PLACE))) => doneLemma(true) ...</k>
    // <mir>
    //   <data>
    //     <functions>
    //         <function>
    //         <fnKey> FN_KEY </fnKey>
    //         <localDecls>
    //             <index> INDEX </index>
    //             <value> _ </value>
    //             ...
    //         </localDecls>
    //         ...
    //         </function>
    //     </functions>
    //   </data>
    //   ...
    // </mir>
    // requires INDEX ==Int Local2Int(PLACE)

    // claim [passing2]: 
    // <k> #assert( FN_KEY, _1, _KIND) => .K ...</k>
    // <mir>
    //   <data>
    //     <functions>
    //         <function>
    //         <fnKey> FN_KEY </fnKey>
    //         <localDecls>
    //             <index> 1 </index>
    //             <value> true </value>
    //             ...
    //         </localDecls>
    //         ...
    //         </function>
    //     </functions>
    //   </data>
    //   ...
    // </mir>
    
    // Having multiple cells creates spurious branching for panics and internal panics
    claim [passing3]: 
    <k> #assert( FN_KEY, _1, _KIND) => .K ...</k>
    <mir>
      <data>
        <functions>
            <function>
            <fnKey> FN_KEY </fnKey>
            <localDecls>
              <localDecl>
              <index> _1 </index>
                <value> true:Bool </value>
                ...
              </localDecl>
              <localDecl>
              <index> _0 </index>
                <value> 8 </value>
                ...
              </localDecl>
              ...
            </localDecls>
            ...
            </function>
        </functions>
      </data>
      ...
    </mir>
    
    // claim [failing1]: 
    // <k> runLemma(evalLocal(FN_KEY:FunctionLikeKey, PLACE:Local)) => doneLemma(3:Int) ...</k>
    // <returncode> 4 </returncode>
    // <mir>
    //   <simulator>
    //     <callStack> ListItem(Fn(main)) .List </callStack>
    //     <currentBasicBlock> 0 </currentBasicBlock>
    //     <phase> Execution </phase>
    //   </simulator>
    //   <data>
    //     <functions>
    //       <function>
    //       <fnKey> FN_KEY </fnKey>
    //       <localDecls>
    //         <localDecl>
    //             <index> INDEX </index>
    //             <mutability> Not </mutability>
    //             <internal> false </internal>
    //             <ty> u32 </ty>
    //             <value> 3:Int </value>
    //         </localDecl>
    //         ...
    //       </localDecls>
    //       <basicBlocks>
    //         <basicBlock>
    //           <bbName>
    //             0
    //           </bbName>
    //           <bbBody>
    //             { _0 = _1 ; .Statements return ; }
    //           </bbBody>
    //         </basicBlock>
    //         ...
    //       </basicBlocks>
    //       </function>
    //       ...
    //     </functions>
    //   </data>
    // </mir>
    // requires INDEX ==Int Local2Int(PLACE)
endmodule