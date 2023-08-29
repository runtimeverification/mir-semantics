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
endmodule

module SIMPLE-SPEC
    imports VERIFICATION

    claim <k> #executeStatement(_3 = const 5_usize) => .K ...</k>
          <callStack> ListItem(FN_KEY) ... </callStack>
          <function>
            <fnKey> FN_KEY </fnKey>
              <localDecl> 
                <index> 3 </index>
                <value> _ => 5 </value>
                ...
              </localDecl>
              ...
          </function>

    claim <k> #executeStatement(PLACE:Local = const 5_usize) => .K ...</k>
          <callStack> ListItem(FN_KEY) ... </callStack>
          <function>
            <fnKey> FN_KEY </fnKey>
              <localDecl> 
                <index> INDEX </index>
                <value> _ => 5 </value>
                ...
              </localDecl>
              ...
          </function>
    requires INDEX ==Int Local2Int(PLACE)

    claim <k> #executeStatement(PLACE:Local = Add(const 3_i32, const 5_i32)) => .K ...</k>
          <callStack> ListItem(FN_KEY) ... </callStack>
          <function>
            <fnKey> FN_KEY </fnKey>
              <localDecl> 
                <index> INDEX </index>
                <value> _ => 8 </value>
                ...
              </localDecl>
              ...
          </function>
    requires INDEX ==Int Local2Int(PLACE)

endmodule