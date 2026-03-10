// =============================================================================
// API Alignment Macros
// =============================================================================
// 
// Macros for consistency between SPL and P Token shared specifications

// --- AccountInfo Macros ---

macro_rules! key {
    ($acc:expr) => {
        $acc.key()
    };
}
macro_rules! owner {
    ($acc:expr) => {
        $acc.owner()
    };
}
macro_rules! is_signer {
    ($acc:expr) => {
        $acc.is_signer()
    };
}
macro_rules! same_account {
    ($acc1:expr, $acc2:expr) => {
        $acc1 == $acc2
    };
}

// --- Pubkey Macros ---

// For reference types - in p-token, no dereference needed
macro_rules! assert_pubkey_from_slice {
    ($actual:expr, $slice:expr) => {{
        assert_eq!($actual, $slice);
    }};
}

// For value types - same as above for p-token
macro_rules! assert_pubkey_from_slice_val {
    ($actual:expr, $slice:expr) => {{
        assert_eq!($actual, $slice);
    }};
}

// =============================================================================
// Cheatcodes
// =============================================================================

#[inline(never)]
fn cheatcode_is_account(_: &AccountInfo) {}
#[inline(never)]
fn cheatcode_is_mint(_: &AccountInfo) {}
#[inline(never)]
fn cheatcode_is_rent(_: &AccountInfo) {}
#[inline(never)]
fn cheatcode_is_multisig(_: &AccountInfo) {}
#[inline(never)]
fn cheatcode_maybe_same_account(_: &AccountInfo, _: &AccountInfo) {}

/// Cheatcode macros to abstract naming differences.
macro_rules! cheatcode_account {
    ($acc:expr) => {
        cheatcode_is_account($acc)
    };
}
macro_rules! cheatcode_mint {
    ($acc:expr) => {
        cheatcode_is_mint($acc)
    };
}
macro_rules! cheatcode_rent {
    ($acc:expr) => {
        cheatcode_is_rent($acc)
    };
}
macro_rules! cheatcode_multisig {
    ($acc:expr) => {
        cheatcode_is_multisig($acc)
    };
}

// =============================================================================
// Helper functions
// =============================================================================

fn get_account(account_info: &AccountInfo) -> &Account {
    unsafe {
        let byte_ptr = account_info.borrow_data_unchecked();
        let acc_ref = load_unchecked::<Account>(byte_ptr).unwrap();
        acc_ref
    }
}

fn get_mint(account_info: &AccountInfo) -> &Mint {
    unsafe {
        let byte_ptr = account_info.borrow_data_unchecked();
        let acc_ref = load_unchecked::<Mint>(byte_ptr).unwrap();
        acc_ref
    }
}

fn get_rent(account_info: &AccountInfo) -> &Rent {
    unsafe { Rent::from_bytes_unchecked(account_info.borrow_data_unchecked()) }
}

fn get_multisig(account_info: &AccountInfo) -> &Multisig {
    unsafe {
        let byte_ptr = account_info.borrow_data_unchecked();
        let multisig_ref = load_unchecked::<Multisig>(byte_ptr).unwrap();
        multisig_ref
    }
}

// =============================================================================
// Aliases
// =============================================================================

use pinocchio_token_interface::program::ID as PROGRAM_ID;
use pinocchio_token_interface::state::multisig::MAX_SIGNERS;
use pinocchio::sysvars::rent::Rent;
use pinocchio::sysvars::rent::RENT_ID;
use pinocchio_token_interface::native_mint::ID as NATIVE_MINT_ID;
use pinocchio_token_interface::state::account::INCINERATOR_ID;
use pinocchio::pubkey::PUBKEY_BYTES;
use pinocchio_token_interface::state::account_state::AccountState;

// =============================================================================
// Process call macros (ordered same as includes)
// =============================================================================

macro_rules! call_process_approve_checked {
    ($accounts:expr, $instruction_data:expr) => {
        process_approve_checked($accounts, $instruction_data)
    };
}
macro_rules! call_process_approve {
    ($accounts:expr, $instruction_data:expr) => {
        process_approve($accounts, $instruction_data)
    };
}
macro_rules! call_process_freeze_account {
    ($accounts:expr) => {
        process_freeze_account($accounts)
    };
}
macro_rules! call_process_get_account_data_size {
    ($accounts:expr) => {
        process_get_account_data_size($accounts)
    };
}
macro_rules! call_process_initialize_account2 {
    ($accounts:expr, $instruction_data:expr) => {
        process_initialize_account2($accounts, $instruction_data)
    };
}
macro_rules! call_process_initialize_account3 {
    ($accounts:expr, $instruction_data:expr) => {
        process_initialize_account3($accounts, $instruction_data)
    };
}
macro_rules! call_process_initialize_account {
    ($accounts:expr) => {
        process_initialize_account($accounts)
    };
}
macro_rules! call_process_initialize_immutable_owner {
    ($accounts:expr) => {
        process_initialize_immutable_owner($accounts)
    };
}
macro_rules! call_process_initialize_mint2 {
    ($accounts:expr, $instruction_data:expr) => {
        process_initialize_mint2($accounts, $instruction_data)
    };
}
macro_rules! call_process_initialize_mint2_no_freeze {
    ($accounts:expr, $instruction_data:expr) => {
        process_initialize_mint2($accounts, $instruction_data)
    };
}
macro_rules! call_process_initialize_mint {
    ($accounts:expr, $instruction_data:expr) => {
        process_initialize_mint($accounts, $instruction_data)
    };
}
macro_rules! call_process_initialize_mint_no_freeze {
    ($accounts:expr, $instruction_data:expr) => {
        process_initialize_mint($accounts, $instruction_data)
    };
}
macro_rules! call_process_initialize_multisig {
    ($accounts:expr, $instruction_data:expr) => {
        process_initialize_multisig($accounts, $instruction_data)
    };
}
macro_rules! call_process_initialize_multisig2 {
    ($accounts:expr, $instruction_data:expr) => {
        process_initialize_multisig2($accounts, $instruction_data)
    };
}
macro_rules! call_process_mint_to_checked {
    ($accounts:expr, $instruction_data:expr) => {
        process_mint_to_checked($accounts, $instruction_data)
    };
}
macro_rules! call_process_mint_to {
    ($accounts:expr, $instruction_data:expr) => {
        process_mint_to($accounts, $instruction_data)
    };
}
macro_rules! call_process_revoke {
    ($accounts:expr) => {
        process_revoke($accounts)
    };
}
macro_rules! call_process_set_authority {
    ($accounts:expr, $instruction_data:expr) => {
        process_set_authority($accounts, $instruction_data)
    };
}
macro_rules! call_process_sync_native {
    ($accounts:expr) => {
        process_sync_native($accounts)
    };
}
macro_rules! call_process_thaw_account {
    ($accounts:expr) => {
        process_thaw_account($accounts)
    };
}
macro_rules! call_process_close_account {
    ($accounts:expr) => {
        process_close_account($accounts)
    };
}
macro_rules! call_process_burn_checked {
    ($accounts:expr, $instruction_data:expr) => {
        process_burn_checked($accounts, $instruction_data)
    };
}
macro_rules! call_process_burn {
    ($accounts:expr, $instruction_data:expr) => {
        process_burn($accounts, $instruction_data)
    };
}
macro_rules! call_process_transfer_checked {
    ($accounts:expr, $instruction_data:expr) => {
        process_transfer_checked($accounts, $instruction_data)
    };
}
macro_rules! call_process_transfer {
    ($accounts:expr, $instruction_data:expr) => {
        process_transfer($accounts, $instruction_data)
    };
}
macro_rules! call_process_amount_to_ui_amount {
    ($accounts:expr, $instruction_data:expr) => {
        process_amount_to_ui_amount($accounts, $instruction_data)
    };
}
macro_rules! call_process_ui_amount_to_amount {
    ($accounts:expr, $instruction_data:expr) => {
        process_ui_amount_to_amount($accounts, $instruction_data)
    };
}
