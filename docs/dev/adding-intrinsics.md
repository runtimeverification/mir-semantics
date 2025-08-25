# Adding Intrinsics

## Development Workflow

### Step 1: Create Test File
Create `tests/rust/intrinsic/your_intrinsic.rs`:

```rust
fn main() {
    let result = your_intrinsic(args);
    assert_eq!(result, expected);
}
```

### Step 2: Generate SMIR and Verify Intrinsic Detection
```bash
# Generate SMIR JSON
make generate-tests-smir

# Update expected outputs and verify intrinsic is detected
make test-unit TEST_ARGS="--update-expected-output"
```

Check `tests/expected/unit/test_smir/test_function_symbols/your_intrinsic.expected.json` to confirm the intrinsic appears as `IntrinsicSym`.

### Step 3: Run Initial Integration Test
```bash
# Run test and update expected output (will show stuck at intrinsic call)
make test-integration TEST_ARGS="-k your_intrinsic --update-expected-output"

# Backup the initial state for comparison
cp tests/expected/integration/test_exec_smir/intrinsic_your_intrinsic.state \
   tests/expected/integration/test_exec_smir/intrinsic_your_intrinsic.state.backup
```

### Step 4: Implement K Rule
Edit `kmir/src/kmir/kdist/mir-semantics/kmir.md`:

```k
rule <k> #execIntrinsic(mirString("your_intrinsic"), ARGS, DEST) => 
      /* your implementation */
     ... </k>
```

### Step 5: Rebuild and Test
```bash
# Rebuild K semantics
make build

# Run test again
make test-integration TEST_ARGS="-k your_intrinsic --update-expected-output"

# Compare results
diff tests/expected/integration/test_exec_smir/intrinsic_your_intrinsic.state.backup \
     tests/expected/integration/test_exec_smir/intrinsic_your_intrinsic.state
```

The diff should show progress past the intrinsic call if implementation is correct.

### Step 6: Verify Results
Ensure the test completes successfully and the intrinsic behaves as expected.

## Example: black_box

Initial state (before rule):
```
#setUpCalleeData ( IntrinsicFunction ( mirString ( "black_box" ) ) , ...)
```

After implementing rule:
```
Program continues execution with value 11 passed through
```