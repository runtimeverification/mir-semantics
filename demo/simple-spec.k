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
endmodule