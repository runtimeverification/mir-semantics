# MIR Execution Steps

**Last Updated: 2025-08-05**

Execution steps based on `assert_eq.rs`, applying a total of 156 rules, transforming from node 1 to node 3.

## Execution Steps List

### 1. Function Call Initialization Phase
- [Function Call Start](../kmir/src/kmir/kdist/mir-semantics/kmir.md#L461)
- [Setup Callee Data](../kmir/src/kmir/kdist/mir-semantics/kmir.md#L494)
- [Complete Argument Setup](../kmir/src/kmir/kdist/mir-semantics/kmir.md#L519)

### 2. Basic Block Execution Phase
- [Execute Basic Block](../kmir/src/kmir/kdist/mir-semantics/kmir.md#L256)
- [Execute Statement Sequence](../kmir/src/kmir/kdist/mir-semantics/kmir.md#L264)

### 3. Statement Execution Phase
- [Handle Assignment Statement](../kmir/src/kmir/kdist/mir-semantics/kmir.md#L279)
- [Set Local Variable Value (Hot Rule)](../kmir/src/kmir/kdist/mir-semantics/rt/data.md#L173)

### 4. Operand Processing Phase
- [Handle RValue Use](../kmir/src/kmir/kdist/mir-semantics/rt/data.md#L608)
- [Handle Constant Operand](../kmir/src/kmir/kdist/mir-semantics/rt/data.md#L122)
- [Decode Allocated Constant](../kmir/src/kmir/kdist/mir-semantics/rt/data.md#L1073)

### 5. Arithmetic Operation Phase
- [Binary Operation Processing](../kmir/src/kmir/kdist/mir-semantics/rt/data.md#L1109)
- [Binary Operation Result](../kmir/src/kmir/kdist/mir-semantics/rt/data.md#L1174)

### 6. Assertion Check Phase
- [Assertion Check Start](../kmir/src/kmir/kdist/mir-semantics/kmir.md#L563)
- [Expectation Check (Hot Rule)](../kmir/src/kmir/kdist/mir-semantics/kmir.md#L568)
- [Move Operand Processing](../kmir/src/kmir/kdist/mir-semantics/rt/data.md#L154)
- [Projection Traversal and Move Marking](../kmir/src/kmir/kdist/mir-semantics/rt/data.md#L357)
- [Expectation Check (Cold Rule)](../kmir/src/kmir/kdist/mir-semantics/kmir.md#L568)

### 7. Control Flow Processing Phase
- [Assertion Success Processing](../kmir/src/kmir/kdist/mir-semantics/kmir.md#L570)
- [Execute Target Basic Block](../kmir/src/kmir/kdist/mir-semantics/kmir.md#L245)
