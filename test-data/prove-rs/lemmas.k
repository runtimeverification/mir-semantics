requires "verify.k"

module LEMMAS
    imports VERIFY

    // For testing
    claim <k> runLemma(isRValueResult(_:RValueResult)) => doneLemma(true) ...</k>
    claim <k> runLemma(isRValueResult(_:MIRValue))     => doneLemma(true) ...</k>
endmodule