// =============================================================================
// API Alignment (Wrappers and Macros)
// =============================================================================
// 
// Macros for consistency between SPL and P Token shared specifications.
// Wrapper types are required around `Account`, `Mint`, and `Multisig` provide
// an interface that is consistent with the P-Token types API.

// --- Wrappers ---

/// A wrapper struct for Account that provides Deref to access fields directly.
struct AccountWrapper(Result<Account, ProgramError>);

impl AccountWrapper {
    fn is_initialized(&self) -> Result<bool, ProgramError> {
        match &self.0 {
            Ok(a) => Ok(a.state != AccountState::Uninitialized),
            Err(e) => Err(e.clone()),
        }
    }

    fn delegate(&self) -> Option<&Pubkey> {
        match &self.0 {
            Ok(a) => match a.delegate.as_ref() {
                solana_program_option::COption::None => None,
                solana_program_option::COption::Some(delegate) => Some(delegate),
            },
            Err(_) => None,
        }
    }

    fn account_state(&self) -> Result<AccountState, ProgramError> {
        match &self.0 {
            Ok(a) => Ok(a.state),
            Err(e) => Err(e.clone()),
        }
    }

    fn is_native(&self) -> bool {
        match &self.0 {
            Ok(a) => a.is_native.is_some(),
            Err(_) => false,
        }
    }

    fn native_amount(&self) -> Option<u64> {
        match &self.0 {
            Ok(a) => match a.is_native {
                solana_program_option::COption::Some(amt) => Some(amt),
                solana_program_option::COption::None => None,
            },
            Err(_) => None,
        }
    }

    fn close_authority(&self) -> Option<&Pubkey> {
        match &self.0 {
            Ok(a) => match a.close_authority.as_ref() {
                solana_program_option::COption::Some(pk) => Some(pk),
                solana_program_option::COption::None => None,
            },
            Err(_) => None,
        }
    }

    fn is_owned_by_system_program_or_incinerator(&self) -> bool {
        match &self.0 {
            Ok(a) => a.owner == solana_sdk_ids::system_program::ID || a.owner == solana_sdk_ids::incinerator::ID,
            Err(_) => false,
        }
    }

    fn amount(&self) -> u64 {
        self.0.as_ref().expect("AccountWrapper: underlying account missing").amount
    }

    fn delegated_amount(&self) -> u64 {
        self.0.as_ref().expect("AccountWrapper: underlying account missing").delegated_amount
    }
}

impl core::ops::Deref for AccountWrapper {
    type Target = Account;
    fn deref(&self) -> &Self::Target {
        self.0.as_ref().expect("AccountWrapper: underlying account missing")
    }
}

/// A wrapper struct for Mint that provides Deref to access fields directly.
struct MintWrapper(Result<Mint, ProgramError>);

impl MintWrapper {
    fn is_initialized(&self) -> Result<bool, ProgramError> {
        match &self.0 {
            Ok(m) => Ok(m.is_initialized),
            Err(e) => Err(e.clone()),
        }
    }

    fn mint_authority(&self) -> Option<&Pubkey> {
        match &self.0 {
            Ok(m) => match m.mint_authority.as_ref() {
                solana_program_option::COption::Some(pk) => Some(pk),
                solana_program_option::COption::None => None,
            },
            Err(_) => None,
        }
    }

    fn freeze_authority(&self) -> Option<&Pubkey> {
        match &self.0 {
            Ok(m) => match m.freeze_authority.as_ref() {
                solana_program_option::COption::Some(pk) => Some(pk),
                solana_program_option::COption::None => None,
            },
            Err(_) => None,
        }
    }

    fn supply(&self) -> u64 {
        self.0.as_ref().expect("MintWrapper: underlying mint missing").supply
    }
}

impl core::ops::Deref for MintWrapper {
    type Target = Mint;
    fn deref(&self) -> &Self::Target {
        self.0.as_ref().expect("MintWrapper: underlying mint missing")
    }
}

/// A wrapper struct for Multisig that provides Deref to access fields directly.
struct MultisigWrapper(Result<Multisig, ProgramError>);

impl MultisigWrapper {
    fn is_initialized(&self) -> Result<bool, ProgramError> {
        match &self.0 {
            Ok(m) => Ok(m.is_initialized),
            Err(e) => Err(e.clone()),
        }
    }
}

impl core::ops::Deref for MultisigWrapper {
    type Target = Multisig;
    fn deref(&self) -> &Self::Target {
        self.0.as_ref().expect("MultisigWrapper: underlying multisig missing")
    }
}

// --- AccountInfo Macros ---

macro_rules! key {
    ($acc:expr) => {
        $acc.key
    };
}
macro_rules! owner {
    ($acc:expr) => {
        $acc.owner
    };
}
macro_rules! is_signer {
    ($acc:expr) => {
        $acc.is_signer
    };
}
macro_rules! same_account {
    ($acc1:expr, $acc2:expr) => {
        key!($acc1) == key!($acc2)
    };
}

// --- Pubkey Macros ---

// For reference types (&Pubkey) - dereferences $actual
macro_rules! assert_pubkey_from_slice {
    ($actual:expr, $slice:expr) => {{
        let expected_pubkey = Pubkey::new_from_array($slice.try_into().unwrap());
        assert_eq!(*$actual, expected_pubkey);
    }};
}

// For value types (Pubkey) - no dereference
macro_rules! assert_pubkey_from_slice_val {
    ($actual:expr, $slice:expr) => {{
        let expected_pubkey = Pubkey::new_from_array($slice.try_into().unwrap());
        assert_eq!($actual, expected_pubkey);
    }};
}

// unpacking an optional pubkey.
// code copied from interface::instruction::TokenInstruction
fn unpack_pubkey_option(input: &[u8]) -> Result<(solana_program_option::COption<Pubkey>, &[u8]), ProgramError> {
    match input.split_first() {
        Option::Some((&0, rest)) => Ok((solana_program_option::COption::None, rest)),
        Option::Some((&1, rest)) if rest.len() >= 32 => {
            let (key, rest) = rest.split_at(32);
            let pk = Pubkey::try_from(key).map_err(|_| TokenError::InvalidInstruction)?;
            Ok((solana_program_option::COption::Some(pk), rest))
        }
        _ => Err(TokenError::InvalidInstruction.into()),
    }
}


// =============================================================================
// Cheatcodes
// =============================================================================

#[inline(never)]
fn cheatcode_is_spl_account(_: &AccountInfo) {}
#[inline(never)]
fn cheatcode_is_spl_mint(_: &AccountInfo) {}
#[inline(never)]
fn cheatcode_is_spl_rent(_: &AccountInfo) {}
#[inline(never)]
fn cheatcode_is_spl_multisig(_: &AccountInfo) {}

/// Cheatcode macros to abstract naming differences.
macro_rules! cheatcode_account {
    ($acc:expr) => {
        cheatcode_is_spl_account($acc)
    };
}
macro_rules! cheatcode_mint {
    ($acc:expr) => {
        cheatcode_is_spl_mint($acc)
    };
}
macro_rules! cheatcode_rent {
    ($acc:expr) => {
        cheatcode_is_spl_rent($acc)
    };
}
macro_rules! cheatcode_multisig {
    ($acc:expr) => {
        cheatcode_is_spl_multisig($acc)
    };
}

// =============================================================================
// Helper functions
// =============================================================================

fn get_account(account_info: &AccountInfo) -> AccountWrapper {
    AccountWrapper(Account::unpack_unchecked(&account_info.data.borrow()))
}

fn get_mint(account_info: &AccountInfo) -> MintWrapper {
    MintWrapper(Mint::unpack_unchecked(&account_info.data.borrow()))
}

fn get_rent(account_info: &AccountInfo) -> solana_rent::Rent {
    bincode::deserialize(&account_info.data.borrow()).unwrap()
}

fn get_multisig(account_info: &AccountInfo) -> MultisigWrapper {
    MultisigWrapper(Multisig::unpack_unchecked(&account_info.data.borrow()))
}

// =============================================================================
// Aliases
// =============================================================================

use crate::ID as PROGRAM_ID;
use solana_rent::Rent;
use solana_sysvar::rent::ID as RENT_ID;
use spl_token_interface::native_mint::ID as NATIVE_MINT_ID;
use solana_sdk_ids::incinerator::ID as INCINERATOR_ID;
use solana_pubkey::PUBKEY_BYTES;
// Note: AccountState is already imported in the main file

// =============================================================================
// Process call macros (ordered same as includes)
// =============================================================================

macro_rules! call_process_approve_checked {
    ($accounts:expr, $instruction_data:expr) => {{
        let data = $instruction_data;
        let amount = u64::from_le_bytes(data[0..8].try_into().unwrap());
        let decimals = data[8];
        Processor::process_approve(&PROGRAM_ID, $accounts, amount, Some(decimals))
    }};
}
macro_rules! call_process_approve {
    ($accounts:expr, $instruction_data:expr) => {{
        let data = $instruction_data;
        let amount = u64::from_le_bytes(data[0..8].try_into().unwrap());
        Processor::process_approve(&PROGRAM_ID, $accounts, amount, None)
    }};
}
macro_rules! call_process_freeze_account {
    ($accounts:expr) => {{
        Processor::process_toggle_freeze_account(&PROGRAM_ID, $accounts, true)
    }};
}
macro_rules! call_process_get_account_data_size {
    ($accounts:expr) => {{
        Processor::process_get_account_data_size(&PROGRAM_ID, $accounts)
    }};
}
macro_rules! call_process_initialize_account2 {
    ($accounts:expr, $instruction_data:expr) => {{
        let data = $instruction_data;
        let owner = Pubkey::new_from_array(data[0..32].try_into().unwrap());
        Processor::process_initialize_account2(&PROGRAM_ID, $accounts, owner)
    }};
}
macro_rules! call_process_initialize_account3 {
    ($accounts:expr, $instruction_data:expr) => {{
        let data = $instruction_data;
        let owner = Pubkey::new_from_array(data[0..32].try_into().unwrap());
        Processor::process_initialize_account3(&PROGRAM_ID, $accounts, owner)
    }};
}
macro_rules! call_process_initialize_account {
    ($accounts:expr) => {{
        Processor::process_initialize_account(&PROGRAM_ID, $accounts)
    }};
}
macro_rules! call_process_initialize_immutable_owner {
    ($accounts:expr) => {{
        Processor::process_initialize_immutable_owner($accounts)
    }};
}
macro_rules! call_process_initialize_mint2 {
    ($accounts:expr, $instruction_data:expr) => {{
        let data = $instruction_data;
        let decimals = data[0];
        let mint_authority = Pubkey::new_from_array(data[1..33].try_into().unwrap());
        match data[33] {
            // see TokenInstruction::unpack_pubkey_option, used in TokenInstruction::unpack()
            0 =>
                Processor::process_initialize_mint2(
                    $accounts,
                    decimals,
                    mint_authority,
                    solana_program_option::COption::None
                ),
            1 => {
                let freeze_authority =
                    solana_program_option::COption::Some(Pubkey::new_from_array(data[34..66].try_into().unwrap()));
                Processor::process_initialize_mint2($accounts, decimals, mint_authority, freeze_authority)
            },
            _ => Err(TokenError::InvalidInstruction.into()),
        }
    }};
}
macro_rules! call_process_initialize_mint2_no_freeze {
    ($accounts:expr, $instruction_data:expr) => {{
        let data = $instruction_data;
        let decimals = data[0];
        let mint_authority = Pubkey::new_from_array(data[1..33].try_into().unwrap());
        assert!(data.len() == 34);
        if data[33] != 0 {
            Err(TokenError::InvalidInstruction.into())
        } else {
            Processor::process_initialize_mint2($accounts, decimals, mint_authority, solana_program_option::COption::None)
        }
    }};
}
macro_rules! call_process_initialize_mint {
    ($accounts:expr, $instruction_data:expr) => {{
        let data = $instruction_data;
        let decimals = data[0];
        let mint_authority = Pubkey::new_from_array(data[1..33].try_into().unwrap());
        match data[33] {
            // see TokenInstruction::unpack_pubkey_option, used in TokenInstruction::unpack()
            0 =>
                Processor::process_initialize_mint(
                    $accounts,
                    decimals,
                    mint_authority,
                    solana_program_option::COption::None
                ),
            1 => {
                let freeze_authority =
                    solana_program_option::COption::Some(Pubkey::new_from_array(data[34..66].try_into().unwrap()));
                Processor::process_initialize_mint($accounts, decimals, mint_authority, freeze_authority)
            },
            _ => Err(TokenError::InvalidInstruction.into()),
        }
    }};
}
macro_rules! call_process_initialize_mint_no_freeze {
    ($accounts:expr, $instruction_data:expr) => {{
        let data = $instruction_data;
        let decimals = data[0];
        let mint_authority = Pubkey::new_from_array(data[1..33].try_into().unwrap());
        assert!(data.len() == 34);
        if data[33] != 0 {
            Err(TokenError::InvalidInstruction.into())
        } else {
            Processor::process_initialize_mint($accounts, decimals, mint_authority, solana_program_option::COption::None)
        }
    }};
}
macro_rules! call_process_initialize_multisig {
    ($accounts:expr, $instruction_data:expr) => {{
        let data = $instruction_data;
        let m = data[0];
        Processor::process_initialize_multisig($accounts, m)
    }};
}
macro_rules! call_process_initialize_multisig2 {
    ($accounts:expr, $instruction_data:expr) => {{
        let data = $instruction_data;
        let m = data[0];
        Processor::process_initialize_multisig2($accounts, m)
    }};
}
macro_rules! call_process_mint_to_checked {
    ($accounts:expr, $instruction_data:expr) => {{
        let data = $instruction_data;
        let amount = u64::from_le_bytes(data[0..8].try_into().unwrap());
        let decimals = data[8];
        Processor::process_mint_to(&PROGRAM_ID, $accounts, amount, Some(decimals))
    }};
}
macro_rules! call_process_mint_to {
    ($accounts:expr, $instruction_data:expr) => {{
        let data = $instruction_data;
        let amount = u64::from_le_bytes(data[0..8].try_into().unwrap());
        Processor::process_mint_to(&PROGRAM_ID, $accounts, amount, None)
    }};
}
macro_rules! call_process_revoke {
    ($accounts:expr) => {{
        Processor::process_revoke(&PROGRAM_ID, $accounts)
    }};
}
macro_rules! call_process_set_authority {
    ($accounts:expr, $instruction_data:expr) => {{
        let data = $instruction_data;
        let authority_type = match data[0] {
            0 => crate::instruction::AuthorityType::MintTokens,
            1 => crate::instruction::AuthorityType::FreezeAccount,
            2 => crate::instruction::AuthorityType::AccountOwner,
            3 => crate::instruction::AuthorityType::CloseAccount,
            _ => return Err(TokenError::InvalidInstruction.into()),
        };
        // unpack optional new auth, throw error on malformed option
        let (new_authority, _rest) = unpack_pubkey_option(&data[1..34])?;
        Processor::process_set_authority(&PROGRAM_ID, $accounts, authority_type, new_authority)
    }};
}
macro_rules! call_process_sync_native {
    ($accounts:expr) => {{
        Processor::process_sync_native(&PROGRAM_ID, $accounts)
    }};
}
macro_rules! call_process_thaw_account {
    ($accounts:expr) => {{
        Processor::process_toggle_freeze_account(&PROGRAM_ID, $accounts, false)
    }};
}
macro_rules! call_process_close_account {
    ($accounts:expr) => {{
        Processor::process_close_account(&PROGRAM_ID, $accounts)
    }};
}
macro_rules! call_process_burn_checked {
    ($accounts:expr, $instruction_data:expr) => {{
        let data = $instruction_data;
        let amount = u64::from_le_bytes(data[0..8].try_into().unwrap());
        let decimals = data[8];
        Processor::process_burn(&PROGRAM_ID, $accounts, amount, Some(decimals))
    }};
}
macro_rules! call_process_burn {
    ($accounts:expr, $instruction_data:expr) => {{
        let data = $instruction_data;
        let amount = u64::from_le_bytes(data[0..8].try_into().unwrap());
        Processor::process_burn(&PROGRAM_ID, $accounts, amount, None)
    }};
}
macro_rules! call_process_transfer_checked {
    ($accounts:expr, $instruction_data:expr) => {{
        let data = $instruction_data;
        let amount = u64::from_le_bytes(data[0..8].try_into().unwrap());
        let decimals = data[8];
        Processor::process_transfer(&PROGRAM_ID, $accounts, amount, Some(decimals))
    }};
}
macro_rules! call_process_transfer {
    ($accounts:expr, $instruction_data:expr) => {{
        let data = $instruction_data;
        let amount = u64::from_le_bytes(data[0..8].try_into().unwrap());
        Processor::process_transfer(&PROGRAM_ID, $accounts, amount, None)
    }};
}
macro_rules! call_process_amount_to_ui_amount {
    ($accounts:expr, $instruction_data:expr) => {{
        let data = $instruction_data;
        let amount = u64::from_le_bytes(data[0..8].try_into().unwrap());
        Processor::process_amount_to_ui_amount(&PROGRAM_ID, $accounts, amount)
    }};
}
macro_rules! call_process_ui_amount_to_amount {
    ($accounts:expr, $instruction_data:expr) => {{
        let data = $instruction_data;
        let ui_amount = core::str::from_utf8(data).map_err(|_| TokenError::InvalidInstruction)?;
        Processor::process_ui_amount_to_amount(&PROGRAM_ID, $accounts, ui_amount)
    }};
}
