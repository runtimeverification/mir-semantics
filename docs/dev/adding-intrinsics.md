# Adding Intrinsics

## Overview

This guide explains how to add support for new intrinsic functions in KMIR. Intrinsics are compiler built-in functions that don't have regular MIR bodies and require special semantic rules.

## Architecture

Intrinsics are handled with direct operand passing:
1. **Direct Operand Passing**: `#execIntrinsic(symbol("name"), ARGS, DEST)` receives operands directly
2. **Pattern Matching**: Rules match on specific operand patterns for each intrinsic
3. **Operand Evaluation**: Each intrinsic rule handles its own operand evaluation as needed

See implementation in [kmir.md](../../kmir/src/kmir/kdist/mir-semantics/kmir.md)

## Development Workflow

### Step 1: Create Test File

Create a Rust test file in `kmir/src/tests/integration/data/exec-smir/intrinsic/` that uses your intrinsic and verifies its behavior with assertions.

### Step 2: Add Test to Integration Suite

Add entry to `EXEC_DATA` in [test_integration.py](../../kmir/src/tests/integration/test_integration.py):

```python
(
    'your_intrinsic',
    EXEC_DATA_DIR / 'intrinsic' / 'your_intrinsic.smir.json',
    EXEC_DATA_DIR / 'intrinsic' / 'your_intrinsic.state',
    65,  # Start with small depth, increase if needed
),
```

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

Add rules to [kmir.md](../../kmir/src/kmir/kdist/mir-semantics/kmir.md). 

To find implementation patterns for your intrinsic:
```bash
# Search for existing intrinsic implementations
grep -A10 "#execIntrinsic(symbol" kmir/src/kmir/kdist/mir-semantics/kmir.md

# Look for helper functions and evaluation patterns
grep -B2 -A5 "seqstrict" kmir/src/kmir/kdist/mir-semantics/kmir.md
```

Study existing intrinsics like `black_box` (simple value operation) and `raw_eq` (reference dereferencing with helper functions) as reference implementations.

### Step 5: Add Documentation

Document your intrinsic in the K semantics file with its implementation.

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

For implementation examples, see existing intrinsics in [kmir.md](../../kmir/src/kmir/kdist/mir-semantics/kmir.md).

## Common Patterns

### Pattern 1: Direct Operand Evaluation
Use when the intrinsic needs to evaluate its operands directly.

### Pattern 2: Reference Dereferencing with #withDeref
Use the `#withDeref` helper function to add dereferencing to operands.

### Pattern 3: seqstrict for Automatic Evaluation
Use `[seqstrict(2,3)]` attribute to automatically evaluate operand arguments.

### Pattern 4: Pattern Matching on Operands
Match specific operand patterns directly in the `#execIntrinsic` rule.

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

### Direct Operand Passing
The current architecture passes operands directly to intrinsic rules:
- **Direct Access**: Rules receive operands directly in `#execIntrinsic`
- **Custom Evaluation**: Each intrinsic controls its own operand evaluation
- **Better Indexing**: K can better index rules with explicit operand patterns

### When to Use Helper Functions
Always use a helper function when:
- You need automatic operand evaluation (with `seqstrict`)
- The logic is complex enough to benefit from separation
- You want to transform operands before evaluation (like with `#withDeref`)

### Testing Strategy
1. Write the test with expected behavior first
2. Generate initial state to see where it gets stuck
3. Implement the minimal rule needed
4. Update state to verify progress
5. Iterate to handle edge cases
6. Document limitations for future work

## References

- Recent intrinsic PRs in repository history
- [Rust Intrinsics Documentation](https://doc.rust-lang.org/std/intrinsics/)