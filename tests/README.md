# MIR Semantics Tests

This directory contains tests for the MIR semantics implementation.

## Structure

- `rust/`: Original Rust source code for testing
- `smir/`: Generated SMIR JSON files from Rust programs
- `expected/`: Expected output files for various test types
- `scripts/`: Helper scripts for test generation and execution

## Adding New Tests

1. Add your Rust program to `rust/` directory (maintaining subdirectory structure)
2. Generate SMIR JSON using the make target: `make generate-tests-smir`
3. Add expected output files to `expected/`
4. Update test configuration as needed

## Make Targets

### Generate SMIR JSON Files
```bash
make generate-tests-smir
```
This target processes all `.rs` files in `tests/rust/` and generates corresponding `.smir.json` files in `tests/smir/`, maintaining the same directory structure.

### Clean Generated Files
```bash
make clean-tests-smir
```
This target removes all generated `.smir.json` files from `tests/smir/` directory.

### Regenerate All Files
```bash
make regenerate-tests-smir
```
This target cleans and then regenerates all SMIR JSON files (equivalent to `clean-tests-smir` + `generate-tests-smir`).

## Directory Structure Example

```
tests/
├── rust/
│   ├── arithmetic/
│   │   ├── basic.rs
│   │   └── complex.rs
│   └── references/
│       └── simple.rs
├── smir/
│   ├── arithmetic/
│   │   ├── basic.smir.json
│   │   └── complex.smir.json
│   └── references/
│       └── simple.smir.json
└── expected/
    ├── execution/
    └── proof/
```