//! Program entrypoint for runtime verification proofs of original spl token implmentation

use {
    crate::{processor::Processor, state::{Account, AccountState, Mint, Multisig}},
    solana_account_info::AccountInfo,
    solana_program_error::{ProgramError, ProgramResult},
    solana_program_pack::Pack,
    solana_pubkey::{self as pubkey, Pubkey},
    solana_sysvar::Sysvar,
    spl_token_interface::{error::TokenError, native_mint},
    std::intrinsics::assume,
};

solana_program_entrypoint::entrypoint!(process_instruction);

/// Process an instruction, edited to call RV proof harnesses
fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    let result = inner_process_instruction(program_id, accounts, instruction_data);

    if let Err(ref _error) = result {
        // Log the error
        // msg!(_error.to_str::<TokenError>()); // Removing for less dependencies
    }

    result
}

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
        self.0.as_ref().map(|m| m.supply).unwrap_or(0)
    }

    fn decimals(&self) -> u8 {
        self.0.as_ref().map(|m| m.decimals).unwrap_or(0)
    }
}

fn get_mint(account_info: &AccountInfo) -> MintWrapper {
    MintWrapper(Mint::unpack_unchecked(&account_info.data.borrow()))
}

/// A wrapper struct as middleware so that the same functions called
/// on the p-token Account are called on the spl Account. However,
/// this means that fields have to be accessed through functions.
struct AccountWrapper(Result<Account, ProgramError>);

impl AccountWrapper {
    fn is_initialized(&self) -> Result<bool, ProgramError> {
        match &self.0 {
            Ok(a) => Ok(a.state != AccountState::Uninitialized),
            Err(e) => Err(e.clone()),
        }
    }

    fn amount(&self) -> u64 {
        self.0.as_ref().map(|a| a.amount).unwrap()
    }

    fn mint(&self) -> Pubkey {
        self.0.as_ref().map(|a| a.mint).unwrap()
    }

    fn owner(&self) -> Pubkey {
        self.0.as_ref().map(|a| a.owner).unwrap()
    }

    fn delegate(&self) -> Option<&Pubkey> {
        match self.0.as_ref().unwrap().delegate.as_ref() {
            solana_program_option::COption::None => None,
            solana_program_option::COption::Some(delegate) => Some(delegate),
        }
    }

    fn delegated_amount(&self) -> u64 {
        self.0.as_ref().map(|a| a.delegated_amount).unwrap()
    }

    fn account_state(&self) -> Result<AccountState, ProgramError> {
        self.0.as_ref().map(|a| a.state).map_err(|e| e.clone())
    }

    fn is_native(&self) -> bool {
        self.0.as_ref().map(|a| a.is_native.is_some()).unwrap()
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
}

/// So the AccountWrapper derefs the wrapped Account
impl core::ops::Deref for AccountWrapper {
    type Target = Result<Account, ProgramError>;
    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

/// Helper function from p-token must be implemented on AccountWrapper
fn get_account(account_info: &AccountInfo) -> AccountWrapper {
    AccountWrapper(Account::unpack_unchecked(&account_info.data.borrow()))
}

/// A wrapper struct as middleware so that the same functions called
/// on the p-token Multisig are called on the spl Multisig. However,
/// this means that fields have to be accessed through functions.
struct MultisigWrapper(Result<Multisig, ProgramError>);

impl MultisigWrapper {
    fn is_initialized(&self) -> Result<bool, ProgramError> {
        match &self.0 {
            Ok(m) => Ok(m.is_initialized),
            Err(e) => Err(e.clone()),
        }
    }

    fn signers(&self) -> &[Pubkey] {
        match &self.0 {
            Ok(m) => &m.signers[..],
            Err(_) => &[],
        }
    }

    fn m(&self) -> u8 {
        self.0.as_ref().map(|m| m.m).unwrap_or(0) // FIXME: Change to stright unwrap?
    }

    fn n(&self) -> u8 {
        self.0.as_ref().map(|m| m.n).unwrap_or(0)
    }
}

/// So the MultisigWrapper derefs the wrapped Multisig
impl core::ops::Deref for MultisigWrapper {
    type Target = Result<Multisig, ProgramError>;
    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

/// Helper function from p-token must be implemented on MultisigWrapper
fn get_multisig(account_info: &AccountInfo) -> MultisigWrapper {
    MultisigWrapper(Multisig::unpack_unchecked(&account_info.data.borrow()))
}

fn get_rent(_account_info: &AccountInfo) -> solana_rent::Rent {
    solana_rent::Rent::get().unwrap()
}

// TODO: Not sure if these are needed since there is no UB like p-token
// fn cheatcode_is_account(_: &AccountInfo) {}
// fn cheatcode_is_mint(_: &AccountInfo) {}
// fn cheatcode_is_multisig(_: &AccountInfo) {}
// fn cheatcode_is_rent(_: &AccountInfo) {}

// Inline `assume` is used directly in test harnesses; no helper functions needed.

/// Inner instruction processor that dispatches to proof harnesses
fn inner_process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    let [discriminator, _rest @ ..] = instruction_data else {
        return Err(TokenError::InvalidInstruction.into());
    };

    match *discriminator {
        // === AUTO-GENERATED MATCH ARMS ===
        // For all other instructions, just call the regular processor
        _ => {
            Processor::process(program_id, accounts, instruction_data)
        }
    }
}

// === AUTO-GENERATED HARNESS FUNCTIONS ===
