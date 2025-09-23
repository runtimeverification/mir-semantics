```k
requires "lib.md"
requires "target.md"
requires "ty.md"

module ABI
  imports LIB-SORTS
  imports TYPES-SORTS
  imports INT

syntax RangeInclusiveForVariantIdx ::= rangeInclusiveForVariantIdx(start: VariantIdx, end: VariantIdx)

syntax FnAbi ::= fnAbi(args: ArgAbis, ret: ArgAbi, fixedCount: MIRInt, conv: CallConvention, cVariadic: MIRBool)

syntax ArgAbi ::= argAbi(ty: Ty, layout: Layout, mode: PassMode)
syntax ArgAbis ::= List {ArgAbi, ""}

syntax Layout ::= layout(Int)
syntax TyAndLayout ::= tyAndLayout(ty: Ty, layout: Layout)

syntax PassMode ::= "passModeIgnore"
                  | passModeDirect(Opaque)
                  | passModePair(Opaque, Opaque)
                  | passModeCast(padI32: MIRBool, cast: Opaque)
                  | passModeIndirect(attrs: Opaque, metaAttrs: Opaque, onStack: MIRBool)

syntax CallConvention ::= "callConventionC"
                        | "callConventionRust"
                        | "callConventionCold"
                        | "callConventionPreserveMost"
                        | "callConventionPreserveAll"
                        | "callConventionArmAapcs"
                        | "callConventionCCmseNonSecureCall"
                        | "callConventionMsp430Intr"
                        | "callConventionPtxKernel"
                        | "callConventionX86Fastcall"
                        | "callConventionX86Intr"
                        | "callConventionX86Stdcall"
                        | "callConventionX86ThisCall"
                        | "callConventionX86VectorCall"
                        | "callConventionX8664SysV"
                        | "callConventionX8664Win64"
                        | "callConventionAvrInterrupt"
                        | "callConventionAvrNonBlockingInterrupt"
                        | "callConventionRiscvInterrupt"

endmodule
```

### Index

#### Internal MIR
- [FnAbi](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_target/src/abi/call/mod.rs#L786-L815)
- [ArgAbi](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_target/src/abi/call/mod.rs#L569-L575)
- [Layout](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_target/src/abi/mod.rs#L71-L73)
- [TyAndLayout](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_target/src/abi/mod.rs#L133-L144)
- [PassMode](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_target/src/abi/call/mod.rs#L34-L70)
- [Conv](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_target/src/abi/call/mod.rs#L730-L762)

#### SMIR (Bridge)
- [FnAbi](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/abi.rs#L67-L81)
- [ArgAbi](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/abi.rs#L83-L93)
- [Layout](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/abi.rs#L43-L49)
- [TyAndLayout](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/abi.rs#L35-L41)
- [PassMode](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/abi.rs#L123-L145)
- [CallConvention](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/abi.rs#L95-L121)

#### Stable MIR
- [FnAbi](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/abi.rs#L13-L32)
- [ArgAbi](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/abi.rs#L34-L40)
- [Layout](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/abi.rs#L112-L113)
- [TyAndLayout](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/abi.rs#L64-L68)
- [PassMode](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/abi.rs#L42-L61)
- [CallConvention](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/abi.rs#L423-L454)
