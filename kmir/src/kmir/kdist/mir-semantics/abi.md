```k
requires "lib.md"
requires "target.md"
requires "ty.md"

module ABI
  imports LIB-SORTS
  imports TARGET-SORTS
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

syntax LayoutShape ::= layoutShape(fields: FieldsShape, variants: VariantsShape, abi: ValueAbi, abiAlign: Align, layoutSize: MachineSize)
syntax LayoutShapes ::= List {LayoutShape, ""}

syntax FieldsShape ::= "fieldsShapePrimitive"
                     | fieldsShapeUnion(NonZero)
                     | fieldsShapeArray(stride: MachineSize, count: MIRInt)
                     | fieldsShapeArbitrary(offsets: MachineSizeList)

syntax VariantsShape ::= variantsShapeSingle(index: VariantIdx)
                       | variantsShapeMultiple(tag: Scalar, tagEncoding: TagEncoding, tagField: MIRInt, variants: LayoutShapes)

syntax ValueAbi ::= "valueAbiUninhabited"
                   | valueAbiScalar(Scalar)
                   | valueAbiScalarPair(Scalar, Scalar)
                   | valueAbiVector(element: Scalar, count: MIRInt)
                   | valueAbiAggregate(sized: Bool)

syntax NonZero ::= nonZero(Int)
syntax MachineSizeList ::= List {MachineSize, ""}

syntax TagEncoding ::= "tagEncodingDirect"
                      | tagEncodingNiche(untaggedVariant: VariantIdx, nicheVariants: RangeInclusiveForVariantIdx, nicheStart: MIRInt)

syntax Scalar ::= scalarInitialized(value: Primitive, validRange: WrappingRange)
                | scalarUnion(value: Primitive)
syntax Primitive ::= primitiveInt(length: IntegerLength, signed: MIRBool)
                   | primitiveFloat(length: FloatLength)
                   | primitivePointer(addressSpace: AddressSpace)
syntax IntegerLength ::= "integerLengthI8"
                       | "integerLengthI16"
                       | "integerLengthI32"
                       | "integerLengthI64"
                       | "integerLengthI128"
syntax FloatLength ::= "floatLengthF16"
                     | "floatLengthF32"
                     | "floatLengthF64"
                     | "floatLengthF128"

syntax AddressSpace ::= addressSpace(Int)

syntax WrappingRange ::= wrappingRange(start: MIRInt, end: MIRInt)

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
- [LayoutS](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_abi/src/lib.rs#L1553-L1594)
- [FieldsShape](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_abi/src/lib.rs#L1162-L1204)
- [Variants](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_abi/src/lib.rs#L1421-L1440)
- [Abi](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_abi/src/lib.rs#L1297-L1313)
- [TagEncoding](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_abi/src/lib.rs#L1442-L1465)
- [Scalar](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_abi/src/lib.rs#L1068-L1088)
- [Primitive](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_abi/src/lib.rs#L957-L971)
- [Integer](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_abi/src/lib.rs#L797-L806)
- [Float](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_abi/src/lib.rs#L922-L930)
- [AddressSpace](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_abi/src/lib.rs#L1285-L1290)
- [WrappingRange](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_abi/src/lib.rs#L1003-L1017)
- [Conv](https://github.com/runtimeverification/rust/blob/85f90a461262f7ca37a6e629933d455fa9c3ee48/compiler/rustc_target/src/abi/call/mod.rs#L730-L762)

#### SMIR (Bridge)
- [FnAbi](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/abi.rs#L67-L81)
- [ArgAbi](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/abi.rs#L83-L93)
- [Layout](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/abi.rs#L43-L49)
- [TyAndLayout](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/abi.rs#L35-L41)
- [PassMode](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/abi.rs#L123-L145)
- [LayoutShape](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/abi.rs#L51-L65)
- [FieldsShape](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/abi.rs#L147-L162)
- [VariantsShape](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/abi.rs#L164-L184)
- [ValueAbi](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/abi.rs#L203-L219)
- [TagEncoding](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/abi.rs#L186-L201)
- [Scalar](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/abi.rs#L237-L249)
- [Primitive](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/abi.rs#L251-L265)
- [IntegerLength](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/abi.rs#L275-L287)
- [FloatLength](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/abi.rs#L289-L300)
- [AddressSpace](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/abi.rs#L267-L273)
- [WrappingRange](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/abi.rs#L302-L308)
- [CallConvention](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_smir/src/rustc_smir/convert/abi.rs#L95-L121)

#### Stable MIR
- [FnAbi](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/abi.rs#L13-L32)
- [ArgAbi](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/abi.rs#L34-L40)
- [Layout](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/abi.rs#L112-L113)
- [TyAndLayout](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/abi.rs#L64-L68)
- [PassMode](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/abi.rs#L42-L61)
- [LayoutShape](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/abi.rs#L70-L92)
- [FieldsShape](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/abi.rs#L130-L156)
- [VariantsShape](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/abi.rs#L181-L198)
- [ValueAbi](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/abi.rs#L223-L238)
- [TagEncoding](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/abi.rs#L200-L221)
- [Scalar](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/abi.rs#L253-L270)
- [Primitive](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/abi.rs#L283-L301)
- [IntegerLength](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/abi.rs#L313-L321)
- [FloatLength](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/abi.rs#L323-L330)
- [AddressSpace](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/abi.rs#L355-L359)
- [WrappingRange](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/abi.rs#L366-L377)
- [CallConvention](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/stable_mir/src/abi.rs#L423-L454)
