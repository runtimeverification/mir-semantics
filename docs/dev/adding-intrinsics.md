# Adding Intrinsics

## Overview

This guide explains how to add support for new intrinsic functions in KMIR. Intrinsics are compiler built-in functions that don't have regular MIR bodies and require special semantic rules.

## Architecture

As of PR #665, intrinsics use a "freeze/heat" pattern:
1. **Operand Evaluation (Freeze)**: `#readOperands(ARGS)` evaluates all arguments to values
2. **Intrinsic Execution (Heat)**: `#execIntrinsic(symbol("name"), DEST)` executes with values on K cell
3. **Pattern Matching**: Rules match on specific value patterns for each intrinsic

## Development Workflow

### Step 1: Create Test File

Create test file in `kmir/src/tests/integration/data/exec-smir/intrinsic/`:

```rust
// your_intrinsic.rs
#![feature(core_intrinsics)]

fn main() {
    use std::intrinsics::your_intrinsic;
    
    // Set up test values
    let val = 42;
    let result = your_intrinsic(&val);
    
    // Add assertion to verify behavior
    assert!(result);
}
```

### Step 2: Add Test to Integration Suite

Edit `kmir/src/tests/integration/test_integration.py` and add entry to `EXEC_DATA`:

```python
(
    'your_intrinsic',
    EXEC_DATA_DIR / 'intrinsic' / 'your_intrinsic.smir.json',
    EXEC_DATA_DIR / 'intrinsic' / 'your_intrinsic.state',
    65,  # Start with small depth, increase if needed
),
```

The SMIR JSON will be generated automatically when the test runs.

### Step 3: Generate Initial State (Will Show Stuck Point)

```bash
# Generate initial state showing where execution gets stuck
make test-integration TEST_ARGS="-k 'exec_smir and your_intrinsic' --update-expected-output"

# This will create your_intrinsic.state showing execution stuck at:
# #execIntrinsic(symbol("your_intrinsic"), DEST)

# Save this for comparison
cp kmir/src/tests/integration/data/exec-smir/intrinsic/your_intrinsic.state \
   your_intrinsic.state.initial
```

### Step 4: Implement K Semantics Rule

Edit `kmir/src/kmir/kdist/mir-semantics/kmir.md`:

#### For Simple Value Operations (like `black_box`):

```k
rule <k> ListItem(ARG:Value) ~> #execIntrinsic(symbol("your_intrinsic"), DEST) 
      => #setLocalValue(DEST, process(ARG)) 
     ... </k>
```

#### For Reference Operations (like `raw_eq`):

```k
// Handle Reference values
rule <k> ListItem(Reference(_OFFSET, place(LOCAL, PROJ), _MUT, _META):Value)
         ~> #execIntrinsic(symbol("your_intrinsic"), DEST)
      => #readOperands(
           operandCopy(place(LOCAL, projectionElemDeref PROJ))
           .Operands
         ) ~> #execYourIntrinsic(DEST)
     ... </k>

// Helper function to avoid recursion
syntax KItem ::= #execYourIntrinsic(Place)
rule <k> ListItem(VAL:Value) ~> #execYourIntrinsic(DEST)
      => #setLocalValue(DEST, process(VAL))
     ... </k>
```

### Step 5: Add Documentation

Add a section in `kmir.md` under "Intrinsic Functions":

```markdown
#### Your Intrinsic (`std::intrinsics::your_intrinsic`)

Description of what the intrinsic does and how it's implemented.

**Current Limitations:**
- Any limitations or unhandled cases
- Future improvements needed
```

### Step 6: Rebuild and Test

```bash
# Rebuild K semantics
make build

# Run test again and update the state with working implementation
make test-integration TEST_ARGS="-k 'exec_smir and your_intrinsic' --update-expected-output"

# Compare to see the progress
diff your_intrinsic.state.initial \
     kmir/src/tests/integration/data/exec-smir/intrinsic/your_intrinsic.state
```

### Step 7: Verify Both Backends

```bash
# Test with both LLVM and Haskell backends
make test-integration TEST_ARGS="-k 'exec_smir and your_intrinsic'"

# Both should pass with consistent results
# If not, you may need backend-specific state files
```

## Examples

### Example 1: `black_box` (Simple Identity)

```k
// Takes one value, returns it unchanged
rule <k> ListItem(ARG:Value) ~> #execIntrinsic(symbol("black_box"), DEST) 
      => #setLocalValue(DEST, ARG) 
     ... </k>
```

### Example 2: `raw_eq` (Reference Comparison)

```k
// Takes two references, compares dereferenced values
rule <k> ListItem(Reference(_OFF1, place(L1, P1), _M1, _META1):Value) 
         ListItem(Reference(_OFF2, place(L2, P2), _M2, _META2):Value) 
         ~> #execIntrinsic(symbol("raw_eq"), DEST)
      => #readOperands(
           operandCopy(place(L1, projectionElemDeref P1))
           operandCopy(place(L2, projectionElemDeref P2))
           .Operands
         ) ~> #execRawEq(DEST)
     ... </k>

syntax KItem ::= #execRawEq(Place)
rule <k> ListItem(VAL1:Value) ListItem(VAL2:Value) ~> #execRawEq(DEST)
      => #setLocalValue(DEST, BoolVal(VAL1 ==K VAL2))
     ... </k>
```

## Common Patterns

### Pattern 1: Direct Value Processing
Use when the intrinsic operates directly on values without indirection.

### Pattern 2: Reference Dereferencing
Use `projectionElemDeref` to access values behind references.

### Pattern 3: Helper Functions
Create dedicated functions like `#execYourIntrinsic` to:
- Avoid recursion issues
- Separate concerns
- Make rules more readable

### Pattern 4: Multiple Operands
Pattern match multiple `ListItem` entries for multi-argument intrinsics.

## Testing Best Practices

1. **Start Simple**: Test with primitive types first
2. **Save Initial State**: Keep the stuck state for comparison
3. **Use Correct Test Filter**: Always use `exec_smir and your_intrinsic` to ensure correct test runs
4. **Check Both Backends**: Ensure LLVM and Haskell produce same results  
5. **Document Limitations**: Note what cases aren't handled yet
6. **Create Issue for Future Work**: Track enhancements needed (like #666 for `raw_eq`)

## Debugging Tips

### Check Execution State
```bash
# See where execution is stuck with verbose output
make test-integration TEST_ARGS="-k 'exec_smir and your_intrinsic' -vv"

# Look for the K cell content to see what values are present
```

### Understanding the State File
The state file shows the complete execution state. Key sections to check:
- `<k>`: Shows current execution point
- `<locals>`: Shows local variable values
- `<functions>`: Should contain `IntrinsicFunction(symbol("your_intrinsic"))`

### Verify Intrinsic Recognition
```bash
# Check SMIR JSON to confirm intrinsic is recognized
cat kmir/src/tests/integration/data/exec-smir/intrinsic/your_intrinsic.smir.json | grep -A5 your_intrinsic
```

## Common Issues

### Issue: Wrong test runs
**Solution**: Use `-k 'exec_smir and your_intrinsic'` to ensure `test_exec_smir` runs, not other tests.

### Issue: "Function not found"
**Solution**: The intrinsic should be automatically recognized if it appears in SMIR. Check the SMIR JSON to confirm.

### Issue: Execution stuck at `#execIntrinsic`
**Solution**: Your rule pattern doesn't match. Check:
- The exact intrinsic name in the symbol
- Value types on K cell (use `ListItem(VAL:Value)` to match any value)
- Number of arguments expected

### Issue: Recursion/infinite loop
**Solution**: Use helper functions to separate evaluation stages, avoid calling `#execIntrinsic` within itself.

### Issue: Different backend results
**Solution**: 
- Increase execution depth if needed
- Check for backend-specific evaluation order issues
- May need backend-specific expected files (`.llvm.state`, `.haskell.state`)

### Issue: Test timeout
**Solution**: 
- Start with smaller depth (e.g., 65 instead of 1000)
- Optimize your rule to avoid unnecessary computation
- Check for infinite loops in your implementation

## Important Notes

### The Freeze/Heat Pattern
The current architecture ensures all operands are evaluated before the intrinsic executes:
- **Freeze**: `#readOperands(ARGS)` evaluates operands to values
- **Heat**: Your rule matches on these values
- This prevents evaluation order issues and simplifies rules

### When to Use Helper Functions
Always use a helper function (like `#execRawEq`) when:
- You need to call `#readOperands` again (to avoid recursion)
- The logic is complex enough to benefit from separation
- You need multiple evaluation steps

### Testing Strategy
1. Write the test with expected behavior first
2. Generate initial state to see where it gets stuck
3. Implement the minimal rule needed
4. Update state to verify progress
5. Iterate to handle edge cases
6. Document limitations for future work

## References

- PR #665: `raw_eq` implementation with freeze/heat pattern refactoring
- PR #659: `black_box` implementation  
- Issue #666: Enhancements for complex `raw_eq` cases
- [Rust Intrinsics Documentation](https://doc.rust-lang.org/std/intrinsics/)