# P-Token Formal Verification Guide

## Overview

This guide explains how to run formal verification for the p-token Solana program using the runtime-verification feature and cheatcode functions.

## Architecture

The codebase uses conditional compilation to separate production and verification code:

- **Production code**: `src/entrypoint.rs` - Used for normal builds
- **Verification code**: `src/entrypoint-runtime-verification.rs` - Used when `runtime-verification` feature is enabled

Both P-Token and SPL token `entrypoint-runtime-verification.rs` have `include!` macros that import the respective prelude and shared
verification harnesses from the `shared/` directory. The verification code has proof harnesses for each instruction, and some have multiple
harnesses per instruction. Each proof harness calls the implementation (the instruction itself) but also has the specification as a precondition
and postcondition. The precondition expresses domain assumptions (see below) and also capture the initial state for comparision
with expected results in the postcondition. The postcondition checks each expected error condition (ordered) and the success case
appropriately updates the state.

## Cheatcode Functions

Cheatcode functions are markers used by the formal verification tools to inject assumptions about account types:

```rust
fn cheatcode_is_account(_: &AccountInfo) {}
fn cheatcode_is_mint(_: &AccountInfo) {}
fn cheatcode_is_rent(_: &AccountInfo) {}
fn cheatcode_is_multisig(_: &AccountInfo) {} // Currently unsupported for SPL-Token
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

## Domain Assumptions
Domain assumptions are added to harnesses behind feature flag `"assumptions"`, and are informed from Anza to be
valid for the Solana Runtime.

### Token Supply Cannot Exceed `u64`
Adding the feature flag will assume checked arithmetic always succeeds for the addition of the transfer, burn, or
mint amount with the destination account's old balance.

Appears in:
- `test_process_transfer`
- `test_process_transfer_checked`
- `test_process_burn`
- `test_process_burn_checked`
- `test_process_mint_to`
- `test_process_mint_to_checked`

The implementations `process_transfer`, `process_transfer_checked`, `process_burn`, `process_burn_checked`, `process_mint_to`,
`process_mint_to_checked` of P-Token assume that it is impossible for the `Account` field `amount` to exceed (`u64::MAX`) due
to the `Mint` field `supply` being a `u64`.

> // Note: The amount of a token account is always within the range of the mint supply (`u64`).

### AccountInfo Arguments Duplicates
It is assumed that if two `AccountInfo` for `Accounts` with the same `key` are provided as input to an instruction,
then the `Account` fields will be equivalent. Cheatcode `maybe_same_account` will link the symbolic state instantiated by
`cheatcode_is_account` (note this must be called prior), this should also be called prior to any state manipulation.
Currently this cheatcode will only link symbolic state for SPL Token _Account_ (not `AccountInfo` and not P-Token),
that would be valid under the same assumptions but has not been necessary for the current proofs.

## Limitations

### Compiling with non-solana target
Currently stable-mir-json does not compile to the solana bpf target. All syscalls are behind feature flags that check for solana
as the target operating system.

```rust
#[cfg(target_os = "solana")]
sol_memset_(self.data_ptr().sub(48), 0, 48);
```

Since the syscalls are not compiled, and thus do not appear in the Stable MIR JSON, the proof harnesses will not trigger the
assertions checking their effects due to them being behind similar feature flags.

```rust
#[cfg(any(target_os = "solana", target_arch = "bpf"))]
{
    // Solana-RT only syscall
    assert_eq!(*owner!(&accounts[0]), [0; 32]);
    assert_eq!(accounts[0].lamports(), 0);
    assert_eq!(accounts[0].data_len(), 0);
}
```

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

All test functions are located in `shared/` and follow the pattern:
- `test_process_*` functions for testing individual instructions
- Each function has cheatcode calls at the beginning to mark account types
- Functions use fixed-size arrays for formal verification compatibility

## Feature Flags

### Feature Flag `runtime-verification`
Required for all verification tests. Enables the verification-specific entrypoint (entrypoint-runtime-verification.rs) and test functions.

### Feature Flag `assumptions`
Adds domain assumptions to the proof harnesses.

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