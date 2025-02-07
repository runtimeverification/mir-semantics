# Top-Down Description of the Semantics of MIR Constructs

## Executing a `Body` (function call)
Every _rust function_ gets compiled into a `Body`. A function body is
broken up into a number of _basic blocks_ (portions of code with
straight-line control flow).

A function _call_ is executed by setting up the arguments and local
variables, and then executing its body. After the function call, the
return value (result) needs to be written back to the _destination_
given in the call, and execution continues with the _target_ basic
block.  An _unwind_ property indicates how to proceed when the call
unwinds (i.e., panics).

The _args_, _destination_, _unwind_, and (optional!) _target_ are
supplied by either the `Terminator` kind `Call` (within a program), or
unnecessary (when calling `main`).

The execution of a body consists of
* setting up a stack frame for this call
  - with reserved space for all _locals_: return value, arg.s, and local
    variables
  - with the (caller's) function address to return to (as well as
    _destination_, _target_, _unwind_)
  - with all _basic blocks_ of the function body
* and then executing block 0 of the _basic blocks_

## Blocks and Control Flow

Executing a block means to execute its contained _statements_ in
order, followed by the _terminator_ action.

### Execution of Terminators (Control Flow)

The _terminator_ can be one of a variety of terminator kinds,
indicating different continuations to the basic block.

Some of these `TerminatorKind`s are only relevant for MIR
transformations while elaborating higher-level operations and
checking, others directly affect the execution control flow.


| Kind            | Data        |                           | Action                                    |
|-----------------|-------------|---------------------------|-------------------------------------------|
| Goto            | block       |                           | continue with given block                 |
|-----------------|-------------|---------------------------|-------------------------------------------|
| SwitchInt       | discr       | value to switch over      | evaluate value and follow                 |
|                 | targets     | alternative continuations | the selected alternative                  |
|-----------------|-------------|---------------------------|-------------------------------------------|
| ?UnwindResume   |             |                           | Continue unwinding after "landing pad"(?) |
|-----------------|-------------|---------------------------|-------------------------------------------|
| UnwindTerminate | Reason      |                           | Terminate after "landing pad"(?)          |
|-----------------|-------------|---------------------------|-------------------------------------------|
| Return          |             | assign _0 to destination  | continue with _target_ from call          |
|                 |             |                           | and maybe more, "exact semantics unclear" |
|-----------------|-------------|---------------------------|-------------------------------------------|
| Unreachable     |             | cannot be reached         | undefined behaviour if executed           |
|-----------------|-------------|---------------------------|-------------------------------------------|
| Call            | func        | function address to call  | set up stack frame for, load, and call    |
|                 | args        | arguments                 | given function                            |
|                 | destination | to store returned value   | (will store return value at _destination_ |
|                 | target      | next block to go to       | and proceed with _target_ block)          |
|                 | unwind      |                           |                                           |
|-----------------|-------------|---------------------------|-------------------------------------------|
| TailCall        | func        | function address to call  | special version of `Call` for tail calls  |
|                 | args        | arguments                 | replaces the stack frame instead of an    |
|                 |             |                           | duplicating destination and target        |
|-----------------|-------------|---------------------------|-------------------------------------------|
| Assert          | cond        | operand to check (bool)   | evaluates _cond_, compares to _expected_  |
|                 | expected    | expected result of check  | if equal, continue with _target_          |
|                 | msg         | msg for panic! call       | otherwise `panic!` with _msg_             |
|                 | target      | continuation if OK        |                                           |
|                 | unwind      |                           |                                           |
|-----------------|-------------|---------------------------|-------------------------------------------|
| InlineAsm       | (for asm)   |                           | executes inline ASM and returns           |
|                 | targets     | next blocks, default 1st  | to the _targets[1]_ block, UNCLEAR        |
|-----------------|-------------|---------------------------|-------------------------------------------|
| **Irrelevant**  |             |                           |                                           |
|-----------------|-------------|---------------------------|-------------------------------------------|
| Drop            | place       | memory to drop            | UNCLEAR: noop after "drop elaboration"    |
|                 | target      | next block to go to       |                                           |
|                 | unwind      |                           |                                           |
|                 | replace     |                           |                                           |
|-----------------|-------------|---------------------------|-------------------------------------------|
| Yield           | ...         | for coroutine blocks only | return a value to caller, resume from     |
|                 |             |                           | given block when called again.            |
|-----------------|-------------|---------------------------|-------------------------------------------|
| CoroutineDrop   | ...         | ?                         |                                           |
|-----------------|-------------|---------------------------|-------------------------------------------|
| FalseEdge       | real target | for borrow checker only   | behaves like `Goto` with _real target_    |
| FalseUnwind     | real target | for borrow checker only   | behaves like `Goto` with _real target_    |
|-----------------|-------------|---------------------------|-------------------------------------------|

### Statements (within a Basic Block)

The list of statements in a basic block is executed sequentially. Each
`Statement` has a certain `StatementKind`. Some `StatementKind`s won't
appear in the MIR that gets executed by the semantics, others do.

| Kind             | Data                                    | Action                                   |
|------------------|-----------------------------------------|------------------------------------------|
| Assign           | (Place, RValue)                         | evaluates place and rvalue, assigns      |
| ?SetDiscriminant | place, variant_index                    | write variant discriminant to place      |
|------------------|-----------------------------------------|------------------------------------------|
| Deinit           | (Place)                                 | writes `uninit` to the place             |
| StorageLive      | (Local)                                 | allocates memory for the local           |
| StorageDead      | (Local)                                 | deallocates memory for the local         |
|------------------|-----------------------------------------|------------------------------------------|
| ?Retag           | (RetagKind, Place)                      | only for `miri`, puts fresh tag on place |
| Intrinsic        | (NonDivergingIntrinsic)                 | optimised call to intrinsic, saves block |
| PlaceMention     | (Place)                                 | (technical, records place access)        |
|------------------|-----------------------------------------|------------------------------------------|
| FakeRead         | (FakeReadCause, Place)                  | disallowed after drop elaboration        |
| AscribeUserType  | ((Place, UserTypeProjection), Variance) | relates types in assign, NOOP at runtime |
| Coverage         | (CoverageKind)                          | CostCtr indication for coverage counters |
| ConstEvalCounter |                                         | counts const eval. cost, NOOP otherwise  |
| Nop              |                                         | NOOP                                     |

The [code of the constant
interpreter](https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_const_eval/src/interpret/step.rs#L57-L291)
demonstrates the semantics outlined in the table further. For
instance, `Retag` and `PlaceMention` evaluate the given `Place`
(`FakeRead` does not!).

## Memory

Some of the above constructs (statements `Storage{Live,Dead}` and
`Deinit`, terminators `Drop`) are only relevant if memory allocation
is part of the semantic model. In the KMIR semantics (so far), memory
is intended to be modeled at a more abstract level.

The `Assign` statement is where memory is accessed for reading or
writing. An `RValue` is computed, potentially reading some arguments,
and then written to a `Place`.

### `Place`s
A `Place` is a `Local` variable (actually just its index), and
potentially a vector of `ProjectionElem`ents.
- `Deref`erencing references or pointers (or `Box`es allocated in the
  heap)
- `Field` access in struct.s and tuples
- `Index`ing into arrays (from front or back)
- Casting values (`OpaqueCast` or `Downcast` - variant narrowing)


### `RValue`s

An `RValue` is an operation that produces a value which can then be assigned to a `Place`.

| RValue         | Arguments                                       | Action                               |
|----------------|-------------------------------------------------|--------------------------------------|
| Use            | Operand                                         | use (i.e., copy) operand unmodified  |
| Repeat         | Operand, Const                                  | create array [Operand;Const]         |
| Ref            | Region, BorrowKind, Place                       | create reference to place            |
| ThreadLocalRef | DefId                                           | thread-local reference (?)           |
| AddressOf      | Mutability, Place                               | creates pointer to place             |
| Len            | Place                                           | array or slice size                  |
| Cast           | CastKind, Operand, Ty                           | different kinds of type casts        |
|----------------|-------------------------------------------------|--------------------------------------|
| BinaryOp       | BinOp, Box<(Operand, Operand)>                  | different fixed operations           |
| NullaryOp      | NullOp, Ty                                      | on ints, bool, floats                |
| UnaryOp        | UnOp, Operand                                   | (see below)                          |
|----------------|-------------------------------------------------|--------------------------------------|
| Discriminant   | Place                                           | discriminant (of sums types) (?)     |
| Aggregate      | Box<AggregateKind>, IndexVec<FieldIdx, Operand> | disallowed after lowering. DF helper |
| ShallowInitBox | Operand, Ty                                     | ?                                    |
| CopyForDeref   | Place                                           | use (copy) contents of `Place`       |

See https://github.com/runtimeverification/rust/blob/9131ddf5faba14fab225a7bf8ef5ee5dafe12e3b/compiler/rustc_const_eval/src/interpret/step.rs#L139-L291

### Operations

Operations are described cursorily in the `RValue` descriptions and in
the `BinOp` and `UnaryOp` descriptions. Their exact semantics,
however, must sometimes be retrieved from the compiler code.

The `Operand`s of operations are `Copy` or `Move` from `Place`s, or
`ConstOperand`s allocated in a `Box`.
Both `Copy` and `Move` _load_ the operand from a `Place`.

#### Nullary Operations `NullOp`

| SizeOf                                        | size of a type                                 |
| AlignOf,                                      | minimum alignment of a type                    |
| OffsetOf(&'tcx List<(VariantIdx, FieldIdx)>), | offset of a field in a struct                  |
| UbChecks                                      | whether upper-bound checks should be performed |

#### Unary Operations `UnOp`

| Not         | logical inversion                                           |
| Neg         | arithmetic inversion                                        |
| PtrMetadata | get pointer metadata. Only allowed in MIR:Runtime phase (?) |

#### Binary Operations `BinOp`, operands A and B

| Add             | (A + B truncated, bool overflow flag)  | int, float     |                                    |
| AddUnchecked    | A + B                                  | int, float     | must have been wrapped in `unsafe` |
| AddWithOverflow | (A + B truncated, bool overflow flag)  | int, float     | not present in stable MIR          |
| Sub             | (A - B truncated, bool underflow flag) | int, float     |                                    |
| SubUnchecked    | A - B                                  | int, float     |                                    |
| SubWithOverflow | (A - B truncated, bool underflow flag) | int, float     | not present in stable MIR          |
| Mul             | (A * B truncated, bool overflow flag)  | int, float     |                                    |
| MulUnchecked    | A * B                                  | int, float     |                                    |
| MulWithOverflow | (A * B truncated, bool overflow flag)  | int, float     | not present in stable MIR          |
| Div             | A / B or A `div` B                     | int, float     |                                    |
| Rem             | A `mod` B, rounding towards zero       | int            |                                    |
| BitXor          | A `xor` B                              | int            |                                    |
| BitAnd          | A & B                                  | int            |                                    |
| BitOr           | A \| B                                 | int            |                                    |
| Shl             | (A << B truncated, bool overflow flag) | int            |                                    |
| ShlUnchecked    | A << B                                 | int            |                                    |
| Shr             | (A >> B truncated?                     | int            |                                    |
| ShrUnchecked    | A >> B                                 | int            |                                    |
| Eq              | A == B                                 | int,float,bool |                                    |
| Lt              | A < B                                  | int,float      |                                    |
| Le              | A <= B                                 | int,float      |                                    |
| Ne              | A /= B                                 | int,float      |                                    |
| Ge              | A >= B                                 | int,float      |                                    |
| Gt              | A > B                                  | int,float      |                                    |
| Cmp             | cmp A B (LT -1, EQ 0, GT 1)            | int,float      |                                    |
| Offset          | offset from a pointer                  | pointers       |                                    |
