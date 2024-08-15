module UTILS-SYNTAX
    imports INT-SYNTAX
    imports BOOL-SYNTAX

    syntax Int ::= "#chop" "(" Int "," Int "," Bool ")" [function]
endmodule

module UTILS
    imports UTILS-SYNTAX
    imports INT
    imports BOOL
    
    rule #chop(0, 0, true) => 0
endmodule