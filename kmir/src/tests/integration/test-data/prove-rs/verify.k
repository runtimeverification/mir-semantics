requires "../../../../../k-src/mir.md"

module VERIFY
    imports K-EQUAL
    imports BASIC-K
    imports MIR-SYMBOLIC

    // LocalTokens will have parsing error if they are not enumerated here 
    syntax LocalToken ::= "_0" [token]
    syntax LocalToken ::= "_1" [token]
    syntax LocalToken ::= "_2" [token]
    syntax LocalToken ::= "_3" [token]
    syntax LocalToken ::= "_4" [token]

    syntax BBId ::= "bb0" [token]
    syntax BBId ::= "bb1" [token]
    syntax BBId ::= "bb2" [token]
    syntax BBId ::= "bb3" [token]
    syntax BBId ::= "bb4" [token]

    syntax IdentifierToken ::= "a" [token]
    syntax IdentifierToken ::= "b" [token]
    syntax IdentifierToken ::= "num" [token]
    syntax IdentifierToken ::= "ans" [token]
    syntax IdentifierToken ::= "add" [token]

    syntax IdentifierToken ::= "core" [token]
    syntax IdentifierToken ::= "panicking" [token]
    syntax IdentifierToken ::= "panic" [token]
    syntax IdentifierToken ::= "\"assertion failed: num == 42\"" [token]
    syntax IdentifierToken ::= "\"assertion failed: 42 == ans\"" [token]
endmodule