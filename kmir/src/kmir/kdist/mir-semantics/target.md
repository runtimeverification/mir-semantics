```k
requires "ty.md"

module TARGET
  imports INT
  imports TYPES

syntax MachineInfo ::= machineInfo(endian: Endian, pointerWidth: MachineSize) [group(mir---endian--pointer-width)]
syntax Endian ::= "endianLittle" [group(mir-enum), symbol(Endian::Little)]
                | "endianBig" [group(mir-enum), symbol(Endian::Big)]

endmodule
```

### Index

#### Internal MIR
- MachineInfo - not present
- [Endian](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_abi/src/lib.rs#L387-L392)

#### SMIR (Bridge)
- [MachineInfo](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/context.rs#L39-L48)
- [Endian](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/abi.rs#L24-L33)

#### Stable MIR
- [MachineInfo](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/target.rs#L6-L11)
- [Endian](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/target.rs#L27-L31)
