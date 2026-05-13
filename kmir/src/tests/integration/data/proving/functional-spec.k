module FUNCTIONAL-SPEC
  imports KMIR

 // claim [substrBytes-empty]:
 //       RangeInteger(0, 1, false, substrBytes(ARG_RANGEINT228:Bytes, 0, 0))
 //    => RangeInteger(0, 1, false, .Bytes)
 //    requires 8 ==Int lengthBytes ( ARG_RANGEINT228 )

 // claim [substrBytes-entire]:
 //       RangeInteger(0, 1, false, substrBytes(ARG_RANGEINT228:Bytes, 0, 8))
 //    => RangeInteger(0, 1, false, ARG_RANGEINT228)
 //    requires 8 ==K lengthBytes ( ARG_RANGEINT228 )

  claim [substrBytes-entire]:
        <k> substrBytes(ARG_RANGEINT228:Bytes, 0, 8) => ARG_RANGEINT228 ... </k>
     requires 8 ==Int lengthBytes ( ARG_RANGEINT228 )

endmodule

