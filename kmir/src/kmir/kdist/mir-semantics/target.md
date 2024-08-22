```k
module TARGET-SORTS

syntax MachineSize

endmodule

module TARGET
  imports TARGET-SORTS
  imports INT

syntax MachineInfo ::= machineInfo(endian: Endian, pointerWidth: MachineSize)
syntax Endian ::= "endianLittle" |  "endianBig"
syntax MachineSize ::= machineSize(numBits: Int)

endmodule
```