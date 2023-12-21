requires "verify.k"

module LEMMAS
    imports VERIFY

    // For testing
    claim <k> runLemma(isRValueResult(_:RValueResult)) => doneLemma(true) ...</k>
    claim <k> runLemma(isRValueResult(_:MIRValue))     => doneLemma(true) ...</k>

    claim [passing1]: 
    <k> runLemma(isRValueResult(evalLocal(FN_KEY, PLACE))) => doneLemma(true) ...</k>
    <mir>
      <data>
        <functions>
            <function>
            <fnKey> FN_KEY </fnKey>
            <localDecls>
                <index> PLACE </index>
                <value> _ </value>
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
    //             <index> PLACE </index>
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
endmodule