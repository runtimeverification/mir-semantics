requires "../../../../../k-src/mir.md"

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

module LEMMAS
    imports VERIFICATION

    // For testing
    claim <k> runLemma(isRValueResult(_:RValueResult)) => doneLemma(true) ...</k>
    claim <k> runLemma(isRValueResult(_:MIRValue))     => doneLemma(true) ...</k>
endmodule