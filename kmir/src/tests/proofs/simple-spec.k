requires "../../../k-src/mir.md"

module VERIFICATION
    imports K-EQUAL
    imports BASIC-K
    imports MIR-SYMBOLIC

endmodule

module SIMPLE-SPEC
    imports VERIFICATION

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