```k
require "mir-syntax.k"
```

```k
module MIR-TYPES
  imports STRING
  imports MIR-SYNTAX
```

We use several hooks which convert between token and string representations:

```k
  syntax String ::= StringLiteral2Sring(StringLiteral) [function, total, hook(STRING.token2string)]
  syntax StringLiteral ::= String2SringLiteral(String) [function, total, hook(STRING.string2token)]

  syntax String ::= Local2String(Local) [function, total, hook(STRING.token2string)]
```

Additionally, we need functions that convert between syntactic and semantics representations of several types:

```k
  syntax Int ::= Local2Int(Local) [function, total]
  //-----------------------------------------------
  rule Local2Int(LOCAL) => #let STR = Local2String(LOCAL) #in String2Int(substrString(STR, 1, lengthString(STR)))
```

```k
endmodule
```
