module UTILS-SYNTAX
    imports INT-SYNTAX
    imports BOOL-SYNTAX

    syntax Int ::= "#width_max" "(" Int "," Bool ")"    [function] // params: width, signed. Calculates maximum number for the width.
    syntax Int ::= "#width_min" "(" Int "," Bool ")"    [function] // params: width, signed. Calculates minimum number for the width.
    syntax Int ::= "#chop" "(" Int "," Int "," Bool ")" [function] // params: number, width, signed. Wraps a number into it's bound.
endmodule

module UTILS
    imports UTILS-SYNTAX
    imports INT
    imports MINT
    imports BOOL

    // Unsigned
    rule #width_max(8,   false) => 255                                     // 2^8   - 1
    rule #width_max(16,  false) => 65535                                   // 2^16  - 1
    rule #width_max(32,  false) => 4294967295                              // 2^32  - 1
    rule #width_max(64,  false) => 18446744073709551615                    // 2^64  - 1
    rule #width_max(128, false) => 340282366920938463463374607431768211455 // 2^128 - 1
    
    // Signed with two's complement
    rule #width_max(8,   true) => 127                                     // 2^(8-1)   - 1
    rule #width_max(16,  true) => 32767                                   // 2^(16-1)  - 1
    rule #width_max(32,  true) => 2147483647                              // 2^(32-1)  - 1
    rule #width_max(64,  true) => 9223372036854775807                     // 2^(64-1)  - 1
    rule #width_max(128, true) => 170141183460469231731687303715884105727 // 2^(128-1) - 1
    
    // Unsigned (Can be collapsed when width is enum)
    rule #width_min(8,   false) => 0
    rule #width_min(16,  false) => 0
    rule #width_min(32,  false) => 0
    rule #width_min(64,  false) => 0
    rule #width_min(128, false) => 0
    
    // Signed with two's complement
    rule #width_min(8,   true) => -128                                     // -2^(8-1)
    rule #width_min(16,  true) => -32768                                   // -2^(16-1)
    rule #width_min(32,  true) => -2147483648                              // -2^(32-1)
    rule #width_min(64,  true) => -9223372036854775808                     // -2^(64-1)
    rule #width_min(128, true) => -170141183460469231731687303715884105728 // -2^(128-1)
    
    // Unsigned
    rule #chop(NUM, WIDTH, false) => NUM %Int (#width_max(WIDTH, false) +Int 1) requires 0 <=Int NUM

    // Signed 
    rule #chop(NUM, WIDTH, true) => 
        (-1 *Int (NUM &Int (1 <<Int (WIDTH -Int 1)))) // Negate value of MSB
        |Int (NUM &Int ((1 <<Int (WIDTH)) -Int 1)) // Bitmask all lower bits in
endmodule