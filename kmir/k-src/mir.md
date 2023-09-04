```k
// require "mir-syntax.md"
require "mir-configuration.md"
```

```k
module MIR
  // imports MIR-SYNTAX
  imports MIR-CONFIGURATION

  // configuration
  //   <k> $PGM:Mir </k>
  //   <returncode exit=""> 4 </returncode>     // the simulator exit code
  
endmodule
```

`MIR-SYMBOLIC` is a stub module to be used with the Haskell backend in the future. It does not import `MIR-AMBIGUITIES`, since the `amb` productions seem to not be supported by the Haskell backend. We may need to consult the C semantics team when we start working on symbolic execution.

```k
module MIR-SYMBOLIC
  //imports MIR-CONFIGURATION

endmodule
```