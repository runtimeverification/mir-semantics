Rust standard library
=====================

These modules define selected types and function from Rust's standard library

```k
module RUST-STD
  imports STD-OPTION
endmodule
```

```k
module STD-OPTION

  syntax {Sort} Sort ::= "None"
                       | "Some" Sort

endmodule
```

