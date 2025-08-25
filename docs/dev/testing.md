# Testing Guide

## Test Structure

```
tests/
├── rust/          # Source test files
├── smir/          # Generated SMIR JSON
└── expected/      # Expected outputs
    ├── unit/
    └── integration/
```

## Running Tests

### Unit Tests
```bash
make test-unit
```

### Integration Tests
```bash
make test-integration
```

### Update Expected Outputs
```bash
# Unit tests
make test-unit TEST_ARGS="--update-expected-output"

# Integration tests  
make test-integration TEST_ARGS="--update-expected-output"

# Or use shortcut for exec_smir tests
make update-exec-smir
```

### Run Specific Tests
```bash
# Run tests matching pattern
make test-integration TEST_ARGS="-k black_box"

# Run with verbose output
make test-integration TEST_ARGS="-v"
```

## Adding New Tests

1. Add `.rs` file to `tests/rust/`
2. Generate SMIR: `make generate-tests-smir`
3. Run test to generate expected outputs
4. Verify outputs are correct
5. Commit both test and expected files