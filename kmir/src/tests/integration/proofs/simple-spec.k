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

    claim [statement.1]: <k> #executeStatement(_3 = const 5_usize) => .K ...</k>
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

    claim [statement.2]: <k> #executeStatement(PLACE:Local = const 5_usize) => .K ...</k>
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

    claim [statement.3]: <k> #executeStatement(PLACE:Local = Add(const 3_i32, const 5_i32)) => .K ...</k>
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

    claim [statement.4]: <k> #executeStatement(_1:Local = move _2) => .K ...</k>
          <callStack> ListItem(FN_KEY) ... </callStack>
          <function>
            <fnKey> FN_KEY </fnKey>
              <localDecl>
                <index> 1 </index>
                <value> _ => 42 </value>
                ...
              </localDecl>
              <localDecl>
                <index> 2 </index>
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
                <index> INDEX1 </index>
                <value> _ => 8 </value>
                ...
              </localDecl>
              <localDecl>
                <index> INDEX2 </index>
                <value> _ => 9 </value>
                ...
              </localDecl>
              ...
          </function>
    requires INDEX1 ==Int Local2Int(PLACE1) andBool INDEX2 ==Int Local2Int(PLACE2) andBool INDEX1 =/=Int INDEX2

    claim [statements.2]: <k> #executeStatements(PLACE:Local = Add(const 3_i32, const 5_i32); PLACE:Local = Add(const 3_i32, const 6_i32);) => .K ...</k>
          <callStack> ListItem(FN_KEY) ... </callStack>
          <function>
            <fnKey> FN_KEY </fnKey>
              <localDecl>
                <index> INDEX </index>
                <value> _ => 9 </value>
                ...
              </localDecl>
              ...
          </function>
    requires INDEX ==Int Local2Int(PLACE)
endmodule