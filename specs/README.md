# Specs - Runtime Verification Harness

This directory contains shared runtime verification specifications for Solana token programs. The specs provide a common harness for verifying both
**p-token** (pinocchio-based) and **spl-token** (solana-based) implementations. The differences between each will be handled by macros,
allowing for small surface area of change that is easily reviewable.

## Architecture

```
specs/
├── prelude-p-token.rs      # P-token specific macros and helpers
├── prelude-spl-token.rs    # SPL-token specific macros and wrappers
└── shared/                 # Common spec files (44 files)
    ├── inner_test_validate_owner.rs
    └── test_process_*.rs
```

### How It Works

Both token implementations include the shared specs via the `include!` macro:

**p-token** (`p-token/src/entrypoint-runtime-verification.rs`):
```rust
include!("../../specs/prelude-p-token.rs");
include!("../../specs/shared/inner_test_validate_owner.rs");
include!("../../specs/shared/test_process_transfer.rs");
// ... more specs
```

**spl-token** (`program/src/entrypoint-runtime-verification.rs`):
```rust
include!("../../specs/prelude-spl-token.rs");
include!("../../specs/shared/inner_test_validate_owner.rs");
include!("../../specs/shared/test_process_transfer.rs");
// ... more specs
```

## API Abstraction

The preludes define macros that abstract API differences between implementations:

### AccountInfo Access Macros

| Macro | p-token (methods) | spl-token (fields) |
|-------|-------------------|-------------------|
| `key!($acc)` | `$acc.key()` | `$acc.key` |
| `owner!($acc)` | `$acc.owner()` | `$acc.owner` |
| `is_signer!($acc)` | `$acc.is_signer()` | `$acc.is_signer` |

### Cheatcode Macros

| Macro | p-token | spl-token |
|-------|---------|-----------|
| `cheatcode_account!($acc)` | `cheatcode_is_account($acc)` | `cheatcode_is_spl_account($acc)` |
| `cheatcode_mint!($acc)` | `cheatcode_is_mint($acc)` | `cheatcode_is_spl_mint($acc)` |

### Process Call Macros

| Macro | p-token | spl-token |
|-------|---------|-----------|
| `call_process_transfer!(...)` | Direct function call | `Processor::process_transfer(...)` with parsing |
| `call_process_mint_to!(...)` | Direct function call | `Processor::process_mint_to(...)` with parsing |

### ID Aliases

| Alias | p-token | spl-token |
|-------|---------|-----------|
| `PROGRAM_ID` | `pinocchio_token_interface::program::ID` | `crate::ID` |
| `RENT_ID` | `pinocchio::sysvars::rent::RENT_ID` | `solana_sysvar::rent::ID` |
| `NATIVE_MINT_ID` | `pinocchio_token_interface::native_mint::ID` | `spl_token_interface::native_mint::ID` |

## Spec File Structure

Each spec file follows a standard structure:

```rust
/// accounts[0] // Source Info
/// accounts[1] // Destination Info
/// accounts[2] // Authority Info
/// instruction_data[0..8] // Little Endian Bytes of u64 amount
#[inline(never)]
fn test_process_transfer(
    accounts: &[AccountInfo; 3],
    instruction_data: &[u8; 8],
) -> ProgramResult {
    // Cheatcodes for symbolic execution setup
    cheatcode_account!(&accounts[0]);
    cheatcode_account!(&accounts[1]);

    //-Initial State-----------------------------------------------------------
    let src_old = get_account(&accounts[0]);
    // ... capture initial state

    //-Process Instruction-----------------------------------------------------
    let result = call_process_transfer!(accounts, instruction_data);

    //-Assert Postconditions---------------------------------------------------
    if /* error condition */ {
        assert_eq!(result, Err(ProgramError::...));
        return result;
    }
    // ... more conditions

    assert!(result.is_ok());
    // ... verify state changes

    result
}
```
