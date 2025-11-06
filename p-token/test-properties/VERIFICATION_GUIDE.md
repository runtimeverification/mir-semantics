# P-Token Formal Verification Guide

## Overview

This guide explains how to run formal verification for the p-token Solana program using the runtime-verification feature and cheatcode functions.

## Architecture

The codebase uses conditional compilation to separate production and verification code:

- **Production code**: `src/entrypoint.rs` - Used for normal builds
- **Verification code**: `src/entrypoint-runtime-verification.rs` - Used when `runtime-verification` feature is enabled

## Cheatcode Functions

Cheatcode functions are markers used by the formal verification tools to inject assumptions about account types:

```rust
fn cheatcode_is_account(_: &AccountInfo) {}
fn cheatcode_is_mint(_: &AccountInfo) {}
fn cheatcode_is_rent(_: &AccountInfo) {}
fn cheatcode_is_multisig(_: &AccountInfo) {} // Currently unsupported
```

These functions are no-ops at runtime but set up data required for the verification.

### Assumptions implemented in cheat codes

* Calling `cheatcode_is_{account,mint,multisig,rent}` asserts that the `Account` pointed-to by `AccountInfo` 
  is followed in memory by the respective data structure, `state::account::Account`, `state::mint::Mint`, 
  `state::multisig::Multisig`, or `sysvars::rent::Rent`.
* The cheat codes will set the data length (`data_len`) of the `AccountInfo` to the correct value for the underlying object:
   | Object   | `data_len` |
   |--------- | ---------- |
   | Account  | 165        |
   | Mint     |  82        |
   | Rent     |  17        |
   | Multisig | 355        |
* For the `Rent` sysvar, the proofs make additional assumptions to avoid overflows and imprecise `Float` computation:
  - The `lamports_per_byteyear` is assumed to be less than `2^32` (to avoid overflows during rent computation).
  - The `exemption_threshold` is fixed to value `2.0` (default). This means that computations will be performed in `u64`.
  - The `burn_percent` value is assumed to be between 0 and 100 (to avoid underflows during rent computation).
* Access to the data structure is provided by intercepting the following Rust functions:
   - `AccountInfo::borrow_data_unchecked` and `AccountInfo::borrow_mut_data_unchecked`
   - `Transmutable::load_unchecked` and `Transmutable::load_mut_unchecked` for the instances `Account`, `Mint`, `Multisig`
   - `sysvars::rent::Rent::from_bytes_unchecked` and `sysvars::rent::Rent::get`
  and replacing their function body execution by an effect that provides the desired access (read-only or mutable).

## Running Verification

### Prerequisites

1. Ensure submodules are initialized:
   ```bash
   cd test-properties
   ./setup.sh
   ```

2. Install `uv` if not already installed (Python package manager)

### Running Tests

#### Run specific test:
```bash
cd test-properties
./run-verification.sh test_process_transfer
```

#### Run all tests:
```bash
cd test-properties
./run-verification.sh -a
```

#### Custom options:
```bash
# With custom timeout (in seconds)
./run-verification.sh -t 600 test_process_transfer

# With custom prove-rs options
./run-verification.sh -o "--max-iterations 50 --max-depth 200" test_process_transfer
```

## Test Functions

All test functions are located in `src/entrypoint-runtime-verification.rs` and follow the pattern:
- `test_process_*` functions for testing individual instructions
- Each function has cheatcode calls at the beginning to mark account types
- Functions use fixed-size arrays for formal verification compatibility

## Feature Flag `runtime-verification`
Required for all verification tests. Enables the verification-specific entrypoint (entrypoint-runtime-verification.rs) and test functions.

## Available Tests

See `proofs.md` for the complete list of available test functions.

## Troubleshooting

### Linker Error (_sol_memcpy_)
This is a known issue with the current setup and doesn't affect the verification process. The verification tools work with the SMIR representation, not the linked binary.

### Module Not Found
If you get errors about the entrypoint module not being found, ensure you're building with the `runtime-verification` feature:
```bash
cargo build --features runtime-verification
```

## Notes

- Default settings: max-depth 2000, max-iterations 500, timeout 1h
- Results are stored in `artefacts/proof-SHA1-SHA2/` directory, where `SHA1` and `SHA2` indicate the version of `solana-token` and `mir-semantics` used.