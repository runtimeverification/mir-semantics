# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

MIR Semantics provides a K Framework-based formal semantics for Rust's Stable MIR (Mid-level Intermediate Representation), enabling symbolic execution and formal verification of Rust programs.

## Essential Commands

### Build and Setup
```bash
# Initial setup - install stable-mir-json tool for SMIR generation
make stable-mir-json

# Build K semantics definitions (required after any K file changes)
make build

# Full build and check
make check build
```

### Testing
```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests (requires stable-mir-json and build)
make test-integration

# Run a single test
uv --directory kmir run pytest kmir/src/tests/integration/test_prove.py::test_prove_rs -k "test_name"

# Generate and parse SMIR for test files
make smir-parse-tests
```

### Code Quality
```bash
# Format code
make format

# Check code quality (linting, type checking, formatting)
make check

# Individual checks
make check-flake8
make check-mypy
make check-black
```

### Working with KMIR Tool
```bash
# Activate environment for interactive use
source kmir/.venv/bin/activate

# Or run commands directly
uv --directory kmir run kmir <command>

# Prove Rust code directly (recommended)
uv --directory kmir run kmir prove-rs path/to/file.rs --verbose

# Generate SMIR JSON from Rust
./scripts/generate-smir-json.sh file.rs output_dir

# View proof results
uv --directory kmir run kmir show proof_id --proof-dir ./proof_dir
```

## Architecture Overview

### Directory Structure
- `kmir/` - Python frontend tool and K semantics
  - `src/kmir/` - Python implementation
    - `kmir.py` - Main KMIR class handling K semantics interaction
    - `smir.py` - SMIR JSON parsing and info extraction
    - `kdist/mir-semantics/` - K semantics definitions
  - `src/tests/` - Test suites
    - `integration/data/prove-rs/` - Rust test programs for prove-rs
    - `integration/data/exec-smir/` - Rust programs for execution tests

### Key K Semantics Files
- `kmir.md` - Main execution semantics and control flow
- `mono.md` - Monomorphized item definitions  
- `body.md` - Function body and basic block semantics
- `rt/configuration.md` - Runtime configuration cells
- `rt/data.md` - Runtime data structures
- `ty.md` - Type system definitions

### Python-K Integration
The Python layer (`kmir.py`) bridges between SMIR JSON and K semantics:
1. Parses SMIR JSON via `SMIRInfo` class
2. Transforms to K terms using `_make_function_map`, `_make_type_and_adt_maps`
3. Executes via K framework's `KProve`/`KRun` interfaces

### Intrinsic Functions
Intrinsic functions (like `black_box`, `raw_eq`) don't have regular function bodies. They're handled by:
1. Python: `_make_function_map` adds `IntrinsicFunction` entries to function map
2. K: Special rules in `kmir.md` execute intrinsics via `#execIntrinsic`

**See `docs/dev/adding-intrinsics.md` for detailed implementation guide.**

## Testing Patterns

### prove-rs Tests
Tests in `kmir/src/tests/integration/data/prove-rs/` follow this pattern:
- Simple Rust programs with assertions
- File naming: `test-name.rs` (passes), `test-name-fail.rs` (expected to fail)
- Tests run via `kmir prove-rs` command
- Generate SMIR automatically during test execution

### Adding New Tests
1. Add Rust file to `prove-rs/` directory
2. Use assertions to verify behavior
3. Run with: `uv --directory kmir run kmir prove-rs your-test.rs`

## Development Workflow

### Before Starting Any Task
1. **Always read relevant documentation first**:
   - Check `docs/` directory for guides on specific topics
   - Review existing implementations of similar features
   - Study test patterns in `kmir/src/tests/`
2. **Understand existing patterns**:
   - Look at recent PRs for implementation examples
   - Check how similar features are implemented
   - Follow established conventions in the codebase

### Modifying K Semantics
1. Edit `.md` files in `kmir/src/kmir/kdist/mir-semantics/`
2. Run `make build` to compile changes
3. Test with `make test-integration`

### Modifying Python Code
1. Edit files in `kmir/src/kmir/`
2. Run `make format && make check` to verify code quality and formatting
3. Test with `make test-unit`

### Adding Intrinsic Support
See `docs/dev/adding-intrinsics.md` for complete guide with examples.

## Debugging Tips

### Viewing Proof Execution
```bash
# Show specific nodes in proof
uv --directory kmir run kmir show proof_id --nodes "1,2,3" --proof-dir ./proof_dir

# Show transitions between nodes
uv --directory kmir run kmir show proof_id --node-deltas "1:2,2:3" --proof-dir ./proof_dir

# Show rules applied
uv --directory kmir run kmir show proof_id --rules "1:2" --proof-dir ./proof_dir

# Full details with static info
uv --directory kmir run kmir show proof_id --full-printer --no-omit-static-info --proof-dir ./proof_dir
```

### Common Issues
- `Function not found` errors: Check if function is in `FUNCTIONS_CELL` (may be intrinsic)
- K compilation errors: Rules must be properly formatted, check syntax
- SMIR generation fails: Ensure using correct Rust nightly version (2024-11-29)

## Code Style Guidelines
- **Intrinsic Rules**: Keep intrinsic implementations simple - use direct `#setLocalValue(DEST, ARG)` when possible instead of creating unnecessary helper rules