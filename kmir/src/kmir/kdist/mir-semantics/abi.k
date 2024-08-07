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
