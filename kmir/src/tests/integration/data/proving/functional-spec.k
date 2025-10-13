module FUNCTIONAL-SPEC
  imports KMIR

 claim [substrBytes-empty]:
       RangeInteger(0, 1, false, substrBytes(ARG_RANGEINT228:Bytes, 0, 0))
    => RangeInteger(0, 1, false, .Bytes)
    requires 8 ==Int lengthBytes ( ARG_RANGEINT228:Bytes )

endmodule

