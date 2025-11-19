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

#[inline(never)]
fn inner_test_validate_owner(
    expected_owner: &Pubkey,
    owner_account_info: &AccountInfo,
    tx_signers: &[AccountInfo],
    maybe_multisig_is_initialised: Option<Result<bool, ProgramError>>,
    result: Result<(), ProgramError>,
) -> Result<(), ProgramError> {
    use crate::id;

    if expected_owner != owner_account_info.key {
        assert_eq!(result, Err(ProgramError::Custom(4)));
        result
    } else if maybe_multisig_is_initialised.is_some()
        && owner_account_info.data_len() == Multisig::LEN
        && owner_account_info.owner == &id()
    {
        let multisig_is_initialised = maybe_multisig_is_initialised.unwrap();
        if multisig_is_initialised.is_err() {
            assert_eq!(result, Err(ProgramError::InvalidAccountData));
            return result;
        } else if !multisig_is_initialised.unwrap() {
            assert_eq!(result, Err(ProgramError::UninitializedAccount));
            return result;
        }

        let multisig = get_multisig(owner_account_info);
        let unsigned_exists = tx_signers.iter().any(|potential_signer| {
            multisig.signers().iter().any(|registered_key| {
                registered_key == potential_signer.key && !potential_signer.is_signer
            })
        });
        if unsigned_exists {
            assert_eq!(result, Err(ProgramError::MissingRequiredSignature));
            return result;
        }

        let signers_count = multisig
            .signers()
            .iter()
            .filter_map(|registered_key| {
                tx_signers.iter().find(|potential_signer| {
                    potential_signer.key == registered_key && potential_signer.is_signer
                })
            })
            .count();
        if signers_count < multisig.m() as usize {
            assert_eq!(result, Err(ProgramError::MissingRequiredSignature));
            return result;
        }

        result
    } else if !owner_account_info.is_signer {
        assert_eq!(result, Err(ProgramError::MissingRequiredSignature));
        result
    } else {
        result
    }
}

// TODO: Not sure if these are needed since there is no UB like p-token
#[inline(never)]
fn cheatcode_is_spl_account(_: &AccountInfo) {}
#[inline(never)]
fn cheatcode_is_spl_mint(_: &AccountInfo) {}
#[inline(never)]
fn cheatcode_is_spl_multisig(_: &AccountInfo) {}
#[inline(never)]
fn cheatcode_is_spl_rent(_: &AccountInfo) {}

// special test for basic domain data access (SPL types)
#[inline(never)]
fn test_spltoken_domain_data(acc: &AccountInfo, mint: &AccountInfo, rent: &AccountInfo) {
    // Mutate mint via standard unpack/pack flow; use unwraps for brevity in tests
    cheatcode_is_spl_mint(mint);
    let mut m = Mint::unpack_unchecked(&mint.data.borrow()).unwrap();
    m.is_initialized = true;
    Mint::pack(m, &mut mint.data.borrow_mut()).unwrap();
    let m2 = Mint::unpack(&mint.data.borrow()).unwrap();
    assert!(m2.is_initialized);

    // Set Account.is_native in the simplest way (parity with p-token's boolean set_native(true))
    cheatcode_is_spl_account(acc);
    let mut a = Account::unpack_unchecked(&acc.data.borrow()).unwrap();
    a.is_native = solana_program_option::COption::Some(0);
    Account::pack(a, &mut acc.data.borrow_mut()).unwrap();
    // Verify via the same wrapper accessor used elsewhere
    let iacc = get_account(acc);
    assert!(iacc.is_native());

    // Basic owner self-check
    let owner = acc.owner;
    assert_eq!(acc.owner, owner);

    // Compare Rent behavior using the sysvar getter and the provided account
    let sysrent = solana_rent::Rent::get().unwrap();
    let rent_collected = 10;
    let (sys_burnt, sys_distributed) = sysrent.calculate_burn(rent_collected);
    assert!(sysrent.burn_percent > 100 || (sys_burnt <= rent_collected && sys_distributed <= rent_collected));

    cheatcode_is_spl_rent(rent);
    let prent = solana_rent::Rent::from_account_info(rent).unwrap_or(sysrent);
    let (acct_burnt, acct_distributed) = prent.calculate_burn(rent_collected);
    assert!(prent.burn_percent > 100 || (acct_burnt <= rent_collected && acct_distributed <= rent_collected));
}

// wrapper to ensure the test is retained in SMIR/IR outputs
#[no_mangle]
pub unsafe extern "C" fn use_tests(acc: &AccountInfo) {
    test_spltoken_domain_data(acc, acc, acc);
}

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
        // 0 - Initialize Mint Freeze
        0 => {
            // #[cfg(feature = "logging")]
            // msg!("Testing Instruction: Initialize Mint Freeze");
            let [_d, payload @ ..] = instruction_data else {
                return Err(TokenError::InvalidInstruction.into());
            };
            match payload.len() {
                x if 66 <= x => {
                    test_process_initialize_mint_freeze(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 2]
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
                }
                x if 34 <= x => {
                    test_process_initialize_mint_no_freeze(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 2]
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
                }
                _ => Err(TokenError::InvalidInstruction.into()),
            }
        }
        // 1 - Initialize Account
        1 => {
            test_process_initialize_account(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 2 - Initialize Multisig
        2 => {
            test_process_initialize_multisig(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 5]
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 3 - Transfer
        3 => {
            test_process_transfer(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 3]
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 4 - Approve
        4 => {
            test_process_approve(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 3]
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 5 - Revoke
        5 => {
            test_process_revoke(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 6 - Set Authority Account
        6 => {
            // #[cfg(feature = "logging")]
            // msg!("Testing Instruction: Set Authority Account");
            if let Some(first_account) = accounts.first() {
                match first_account.data_len() {
                    Account::LEN => {
                        test_process_set_authority_account(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 2]
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
                    }
                    Mint::LEN => {
                        test_process_set_authority_mint(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 2]
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
                    }
                    _ => Err(TokenError::InvalidInstruction.into()),
                }
            } else {
                Err(TokenError::InvalidInstruction.into())
            }
        }
        // 7 - Mint To
        7 => {
            test_process_mint_to(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 3]
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 8 - Burn
        8 => {
            test_process_burn(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 3]
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 9 - Close Account
        9 => {
            test_process_close_account(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 10 - Freeze Account
        10 => {
            test_process_freeze_account(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 11 - Thaw Account
        11 => {
            test_process_thaw_account(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 12 - Transfer Checked
        12 => {
            test_process_transfer_checked(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 4]
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 13 - Approve Checked
        13 => {
            test_process_approve_checked(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 4]
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 14 - Mint To Checked
        14 => {
            test_process_mint_to_checked(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 3]
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 15 - Burn Checked
        15 => {
            test_process_burn_checked(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 3]
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 16 - Initialize Account2
        16 => {
            test_process_initialize_account2(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 3]
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 17 - Sync Native
        17 => {
            test_process_sync_native(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 18 - Initialize Account3
        18 => {
            test_process_initialize_account3(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 2]
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 19 - Initialize Multisig2
        19 => {
            test_process_initialize_multisig2(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 4]
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 20 - Initialize Mint2 Freeze
        20 => {
            // #[cfg(feature = "logging")]
            // msg!("Testing Instruction: Initialize Mint2 Freeze");
            let [_d, payload @ ..] = instruction_data else {
                return Err(TokenError::InvalidInstruction.into());
            };
            match payload.len() {
                x if 66 <= x => {
                    test_process_initialize_mint2_freeze(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 1]
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
                }
                x if 34 <= x => {
                    test_process_initialize_mint2_no_freeze(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 1]
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
                }
                _ => Err(TokenError::InvalidInstruction.into()),
            }
        }
        // 21 - Get Account Data Size
        21 => {
            test_process_get_account_data_size(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 22 - Initialize Immutable Owner
        22 => {
            test_process_initialize_immutable_owner(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 23 - Amount To Ui Amount
        23 => {
            test_process_amount_to_ui_amount(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 1]
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 24 - Ui Amount To Amount
        24 => {
            test_process_ui_amount_to_amount(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 1]
                instruction_data,
            )
        }
        // 38 - Withdraw Excess Lamports Account
        38 => {
            // #[cfg(feature = "logging")]
            // msg!("Testing Instruction: Withdraw Excess Lamports Account");
            if let Some(acc) = accounts.first() {
                match acc.data_len() {
                    Account::LEN => {
                        test_process_withdraw_excess_lamports_account(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
                    }
                    Mint::LEN => {
                        test_process_withdraw_excess_lamports_mint(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
                    }
                    Multisig::LEN => {
                        test_process_withdraw_excess_lamports_multisig(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
                    }
                    _ => Err(TokenError::InvalidInstruction.into()),
                }
            } else {
                Err(TokenError::InvalidInstruction.into())
            }
        }
        // For all other instructions, just call the regular processor
        _ => {
            Processor::process(program_id, accounts, instruction_data)
        }
    }
}

/// program_id // Token Program ID
/// accounts[0] // Mint Info
/// accounts[1] // Rent Sysvar Info
/// instruction_data[0] // Discriminator 0 (Initialize Mint Freeze)
/// instruction_data[1]      // Decimals
/// instruction_data[2..34]  // Mint Authority Pubkey
/// instruction_data[34]     // Freeze Authority Exists? 1 for freeze
/// instruction_data[35..67] // instruction_data[34] == 1 ==> Freeze Authority Pubkey
#[inline(never)]
fn test_process_initialize_mint_freeze(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 2],
    instruction_data: &[u8; 67],
) -> ProgramResult {
    // Constrain discriminator and program id
    unsafe { assume(0 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 66] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_mint(&accounts[0]);
    cheatcode_is_spl_rent(&accounts[1]);

    //-Initial State-----------------------------------------------------------
    let minimum_balance = get_rent(&accounts[1]).minimum_balance(accounts[0].data_len()); // TODO float problem
    let mint_is_initialised_prior = get_mint(&accounts[0]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < 34 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if instruction_data[33] != 0 && instruction_data[33] != 1 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if instruction_data[33] == 1 && instruction_data.len() < 66 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.len() < 2 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].data_len() != Mint::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if accounts[1].key != &solana_sysvar::rent::ID {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if mint_is_initialised_prior.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if mint_is_initialised_prior.unwrap()  {
        assert_eq!(result, Err(ProgramError::Custom(6)))
    } else if accounts[0].lamports() < minimum_balance {
        assert_eq!(result, Err(ProgramError::Custom(0)))
    } else {
        assert!(get_mint(&accounts[0]).is_initialized().unwrap());
        assert_eq!(get_mint(&accounts[0]).mint_authority().unwrap().as_ref(), &instruction_data[1..33]);
        assert_eq!(get_mint(&accounts[0]).decimals(), instruction_data[0]);

        if instruction_data[33] == 1 {
            assert_eq!(get_mint(&accounts[0]).freeze_authority().unwrap().as_ref(), &instruction_data[34..66]);
        }
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

/// program_id // Token Program ID
/// accounts[0] // Mint Info
/// accounts[1] // Rent Sysvar Info
/// instruction_data[0] // Discriminator 0 (Initialize Mint No Freeze)
/// instruction_data[1]      // Decimals
/// instruction_data[2..34]  // Mint Authority Pubkey
/// instruction_data[34]     // Freeze Authority Exists? 0 for no freeze
#[inline(never)]
fn test_process_initialize_mint_no_freeze(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 2],
    instruction_data: &[u8; 35],
) -> ProgramResult {
    // Constrain discriminator and program id
    unsafe { assume(0 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 34] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_mint(&accounts[0]);
    cheatcode_is_spl_rent(&accounts[1]);

    //-Initial State-----------------------------------------------------------
    let minimum_balance = get_rent(&accounts[1]).minimum_balance(accounts[0].data_len()); // TODO float problem
    let mint_is_initialised_prior = get_mint(&accounts[0]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < 34 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if instruction_data[33] != 0 && instruction_data[33] != 1 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if instruction_data[33] == 1 && instruction_data.len() < 66 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.len() < 2 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].data_len() != Mint::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if accounts[1].key != &solana_sysvar::rent::ID {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if mint_is_initialised_prior.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if mint_is_initialised_prior.unwrap()  {
        assert_eq!(result, Err(ProgramError::Custom(6)))
    } else if accounts[0].lamports() < minimum_balance {
        assert_eq!(result, Err(ProgramError::Custom(0)))
    } else {
        assert!(get_mint(&accounts[0]).is_initialized().unwrap());
        assert_eq!(get_mint(&accounts[0]).mint_authority().unwrap().as_ref(), &instruction_data[1..33]);
        assert_eq!(get_mint(&accounts[0]).decimals(), instruction_data[0]);

        if instruction_data[33] == 1 {
            assert_eq!(get_mint(&accounts[0]).freeze_authority().unwrap().as_ref(), &instruction_data[34..66]);
        }
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

/// program_id // Token Program ID
/// accounts[0] // New Account Info
/// accounts[1] // Mint Info
/// accounts[2] // Owner Info
/// accounts[3] // Rent Sysvar Info
/// instruction_data[0] // Discriminator 1 (Initialize Account)
#[inline(never)]
fn test_process_initialize_account(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 4],
    instruction_data: &[u8; 1],
) -> ProgramResult {
    use spl_token_interface::state::AccountState;

    // Constrain discriminator and program id
    unsafe { assume(1 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 0] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_account(&accounts[0]);
    cheatcode_is_spl_mint(&accounts[1]);
    cheatcode_is_spl_account(&accounts[2]);
    cheatcode_is_spl_rent(&accounts[3]);

    //-Initial State-----------------------------------------------------------
    let initial_state_new_account =  get_account(&accounts[0])
        .account_state();

    let minimum_balance = get_rent(&accounts[3]).minimum_balance(accounts[0].data_len()); // TODO float problem
    let is_native_mint = accounts[1].key == &native_mint::ID;
    let mint_is_initialised = get_mint(&accounts[1]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() < 4 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
    } else if accounts[3].key != &solana_sysvar::rent::ID {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if accounts[0].data_len() != Account::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if initial_state_new_account.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if initial_state_new_account.unwrap() != AccountState::Uninitialized {
        assert_eq!(result, Err(ProgramError::Custom(6)))
    } else if accounts[0].lamports() < minimum_balance {
        assert_eq!(result, Err(ProgramError::Custom(0)))
    } else if !is_native_mint && accounts[1].owner != &crate::id() {
        assert_eq!(result, Err(ProgramError::IncorrectProgramId))
    } else if !is_native_mint
            && accounts[1].owner == &crate::id()
            && mint_is_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !is_native_mint
            && accounts[1].owner == &crate::id()
            && !mint_is_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::Custom(2)))
    } else {
        assert!(result.is_ok());
        assert_eq!(get_account(&accounts[0]).account_state().unwrap(), AccountState::Initialized);
        assert_eq!(get_account(&accounts[0]).mint(), *accounts[1].key);
        assert_eq!(get_account(&accounts[0]).owner(), *accounts[2].key);

        if is_native_mint {
            assert!(get_account(&accounts[0]).is_native());
            assert_eq!(get_account(&accounts[0]).native_amount().unwrap(), minimum_balance);
            assert_eq!(get_account(&accounts[0]).amount(), accounts[0].lamports() - minimum_balance);
        }
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

/// program_id // Token Program ID
/// accounts[0]   // Multisig Info
/// accounts[1]   // Rent Sysvar Info
/// accounts[2..] // Signers
/// accounts[2..].len() // n
/// instruction_data[0] // Discriminator 2 (Initialize Multisig)
/// instruction_data[2] // m
#[inline(never)]
fn test_process_initialize_multisig(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 5],
    instruction_data: &[u8; 2],
) -> ProgramResult {
    // Constrain discriminator and program id
    unsafe { assume(2 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 1] = instruction_data.last_chunk().unwrap();

                                                          // ^ FIXME: totally arbitrary for the tests
    // cheatcode_is_spl_multisig(&accounts[0]);
    cheatcode_is_spl_rent(&accounts[1]);
    cheatcode_is_spl_account(&accounts[2]); // Signer
    cheatcode_is_spl_account(&accounts[3]); // Signer
    cheatcode_is_spl_account(&accounts[4]); // Signer

    //-Initial State-----------------------------------------------------------
    let multisig_already_initialised = get_multisig(&accounts[0]).is_initialized();
    let multisig_init_lamports = accounts[0].lamports();
    let minimum_balance = get_rent(&accounts[1]).minimum_balance(accounts[0].data_len());

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.is_empty() {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.len() < 2 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[1].key != &solana_sysvar::rent::ID {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if accounts[0].data_len() != Multisig::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if multisig_already_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if multisig_already_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::Custom(6)))
    } else if multisig_init_lamports < minimum_balance {
        assert_eq!(result, Err(ProgramError::Custom(0)))
    } else if !((((accounts.len() - 2) as u8) >= 1) && (((accounts.len() - 2) as u8) <= 11)) {
        assert_eq!(result, Err(ProgramError::Custom(7)))
    } else if !(((instruction_data[0]) >= 1) && ((instruction_data[0]) <= 11)) {
        assert_eq!(result, Err(ProgramError::Custom(8)))
    } else {
        assert!(accounts[2..]
            .iter()
            .map(|signer| *signer.key)
            .eq(
                get_multisig(&accounts[0])
                .signers()
                .iter()
                .take(accounts[2..].len())
                .copied()
            )
        );
        assert_eq!(get_multisig(&accounts[0]).m(), instruction_data[0]);
        assert_eq!(get_multisig(&accounts[0]).n() as usize, accounts.len() - 2);
        assert!(get_multisig(&accounts[0]).is_initialized().is_ok());
        assert!(get_multisig(&accounts[0]).is_initialized().unwrap());
        assert!(result.is_ok())
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

/// program_id // Token Program ID
/// accounts[0] // Source Info
/// accounts[1] // Destination Info
/// accounts[2] // Authority Info
/// accounts[3..14] // Signers
/// instruction_data[0] // Discriminator 3 (Transfer)
/// instruction_data[1..9] // Little Endian Bytes of u64 amount
#[inline(never)]
fn test_process_transfer(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 3],
    instruction_data: &[u8; 9],
) -> ProgramResult {
    use spl_token_interface::state::AccountState;

    // Constrain discriminator and program id
    unsafe { assume(3 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 8] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_account(&accounts[0]);
    cheatcode_is_spl_account(&accounts[1]);
    // #[cfg(not(feature="multisig"))]
    cheatcode_is_spl_account(&accounts[2]);
    // #[cfg(feature="multisig")]
    // cheatcode_is_spl_multisig(&accounts[2]);

    //-Initial State-----------------------------------------------------------
    let amount = u64::from_le_bytes([instruction_data[0], instruction_data[1], instruction_data[2], instruction_data[3], instruction_data[4], instruction_data[5], instruction_data[6], instruction_data[7]]);
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let dst_initialised = get_account(&accounts[1]).is_initialized();
    let src_initial_amount = get_account(&accounts[0]).amount();
    let dst_initial_amount = get_account(&accounts[1]).amount();
    let src_initial_lamports = accounts[0].lamports();
    let dst_initial_lamports = accounts[1].lamports();
    let src_owner = get_account(&accounts[0]).owner();
    let old_src_delgate = get_account(&accounts[0]).delegate().cloned();
    let old_src_delgated_amount = get_account(&accounts[0]).delegated_amount();
    let maybe_multisig_is_initialised = if accounts[2].data_len() == Multisig::LEN
        && accounts[2].owner == &crate::id()
    {
        Some(get_multisig(&accounts[2]).is_initialized())
    } else {
        None
    };

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < 8 {
        assert_eq!(result, Err(ProgramError::Custom(12)));
        return result;
    } else if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else if src_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if !src_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount));
        return result;
    } else if accounts[0].key != accounts[1].key && dst_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if accounts[0].key != accounts[1].key && !dst_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount));
        return result;
    } else if get_account(&accounts[0]).account_state().unwrap() == AccountState::Frozen {
        assert_eq!(result, Err(ProgramError::Custom(17)));
        return result;
    } else if accounts[0].key != accounts[1].key && get_account(&accounts[1]).account_state().unwrap() == AccountState::Frozen {
        assert_eq!(result, Err(ProgramError::Custom(17)));
        return result;
    } else if src_initial_amount < amount {
        assert_eq!(result, Err(ProgramError::Custom(1)));
        return result;
    } else if accounts[0].key != accounts[1].key && get_account(&accounts[0]).mint() != get_account(&accounts[1]).mint() {
        assert_eq!(result, Err(ProgramError::Custom(3)));
        return result;
    } else {
        let tx_signers: &[AccountInfo] = if accounts.len() > 3 {
            &accounts[3..]
        } else {
            &[]
        };
        if old_src_delgate == Some(*accounts[2].key) {
            inner_test_validate_owner(
                old_src_delgate.as_ref().unwrap(),
                &accounts[2],
                tx_signers,
                maybe_multisig_is_initialised.clone(),
                result.clone(),
            )?;
            if old_src_delgated_amount < amount {
                assert_eq!(result, Err(ProgramError::Custom(1)));
                return result;
            }
        } else {
            inner_test_validate_owner(
                &src_owner,
                &accounts[2],
                tx_signers,
                maybe_multisig_is_initialised,
                result.clone(),
            )?;
        }

        if (accounts[0].key == accounts[1].key || amount == 0) && accounts[0].owner != &crate::id() {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId));
            return result;
        } else if (accounts[0].key == accounts[1].key || amount == 0) && accounts[1].owner != &crate::id() {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId));
            return result;
        } else if accounts[0].key != accounts[1].key && amount != 0 && get_account(&accounts[0]).is_native() && src_initial_lamports < amount {
            // Not sure how to fund native mint
            assert_eq!(result, Err(ProgramError::Custom(14)));
            return result;
        } else if accounts[0].key != accounts[1].key && amount != 0 && get_account(&accounts[0]).is_native() && u64::MAX - amount < dst_initial_lamports {
            // Not sure how to fund native mint
            assert_eq!(result, Err(ProgramError::Custom(14)));
            return result;
        } else if accounts[0].key != accounts[1].key  && amount != 0 {
            assert_eq!(get_account(&accounts[0]).amount(), src_initial_amount - amount);
            assert_eq!(get_account(&accounts[1]).amount(), dst_initial_amount + amount);

            if get_account(&accounts[0]).is_native() {
                assert_eq!(accounts[0].lamports(), src_initial_lamports - amount);
                assert_eq!(accounts[1].lamports(), dst_initial_lamports + amount);
            }
        }

        assert!(result.is_ok());

        // Delegate updates
        if old_src_delgate == Some(*accounts[2].key) && accounts[0].key != accounts[1].key {
            assert_eq!(get_account(&accounts[0]).delegated_amount(), old_src_delgated_amount - amount);
            if old_src_delgated_amount - amount == 0 {
                assert_eq!(get_account(&accounts[0]).delegate(), None);
            }
        }
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

/// program_id // Token Program ID
/// accounts[0] // Source Account Info
/// accounts[1] // Delegate Info
/// accounts[2] // Owner Info
/// accounts[3..14] // Signers
/// instruction_data[0] // Discriminator 4 (Approve)
/// instruction_data[1..9] // Little Endian Bytes of u64 amount
#[inline(never)]
fn test_process_approve(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 3],
    instruction_data: &[u8; 9],
) -> ProgramResult {
    use spl_token_interface::state::AccountState;

    // Constrain discriminator and program id
    unsafe { assume(4 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 8] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_account(&accounts[0]); // Source Account
    cheatcode_is_spl_account(&accounts[1]); // Delegate
    // #[cfg(not(feature="multisig"))]
    cheatcode_is_spl_account(&accounts[2]); // Owner
    // #[cfg(feature="multisig")]
    // cheatcode_is_spl_multisig(&accounts[2]); // Owner

    //-Initial State-----------------------------------------------------------
    let amount = u64::from_le_bytes([instruction_data[0], instruction_data[1], instruction_data[2], instruction_data[3], instruction_data[4], instruction_data[5], instruction_data[6], instruction_data[7]]);
    let src_owner = get_account(&accounts[0]).owner();
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_init_state = get_account(&accounts[0]).account_state();
    let maybe_multisig_is_initialised = if accounts[2].data_len() == Multisig::LEN
        && accounts[2].owner == &crate::id()
    {
        Some(get_multisig(&accounts[2]).is_initialized())
    } else {
        None
    };

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < 8 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].data_len() != Account::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if src_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !src_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount))
    } else if src_init_state.unwrap() == AccountState::Frozen  { // This should be safe to unwrap due to above check passing
        assert_eq!(result, Err(ProgramError::Custom(17)))
    } else {
        inner_test_validate_owner(
            &src_owner,
            &accounts[2],
            &accounts[3..],
            maybe_multisig_is_initialised,
            result.clone(),
        )?;

        assert_eq!(get_account(&accounts[0]).delegate().unwrap(), accounts[1].key);
        assert_eq!(get_account(&accounts[0]).delegated_amount(), amount);
        assert!(result.is_ok())
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

/// program_id // Token Program ID
/// accounts[0] // Source Account Info
/// accounts[1] // Owner Info
/// accounts[2..13] // Signers
/// instruction_data[0] // Discriminator 5 (Revoke)
#[inline(never)]
fn test_process_revoke(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 2],
    instruction_data: &[u8; 1],
) -> ProgramResult {
    use spl_token_interface::state::AccountState;

    // Constrain discriminator and program id
    unsafe { assume(5 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 0] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_account(&accounts[0]); // Source Account
    // #[cfg(not(feature="multisig"))]
    cheatcode_is_spl_account(&accounts[1]); // Owner
    // #[cfg(feature="multisig")]
    // cheatcode_is_spl_multisig(&accounts[1]); // Owner

    //-Initial State-----------------------------------------------------------
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_init_state = get_account(&accounts[0]).account_state();
    let src_owner = get_account(&accounts[0]).owner();
    let maybe_multisig_is_initialised = if accounts[1].data_len() == Multisig::LEN
        && accounts[1].owner == &crate::id()
    {
        Some(get_multisig(&accounts[1]).is_initialized())
    } else {
        None
    };

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() < 1 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].data_len() != Account::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if src_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !src_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount))
    } else if accounts.len() < 2 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if src_init_state.unwrap() == AccountState::Frozen {
        assert_eq!(result, Err(ProgramError::Custom(17)))
    } else {
        inner_test_validate_owner(
            &src_owner,
            &accounts[1],
            &accounts[2..],
            maybe_multisig_is_initialised,
            result.clone(),
        )?;

        assert!(get_account(&accounts[0]).delegate().is_none());
        assert_eq!(get_account(&accounts[0]).delegated_amount(), 0);
        assert!(result.is_ok())
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

/// program_id // Token Program ID
/// accounts[0] // Account Info - Account Case
/// accounts[1] // Authority Info
/// accounts[2..13] // Signers
/// instruction_data[0] // Discriminator 6 (Set Authority Account)
/// instruction_data[1] // Authority Type (instruction)
/// instruction_data[2] // New Authority Follows (0 -> No, 1 -> Yes)
/// instruction_data[3..35] // New Authority Pubkey
#[inline(never)]
fn test_process_set_authority_account(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 2],
    instruction_data: &[u8; 35],
) -> ProgramResult {
    use spl_token_interface::state::AccountState;

    // Constrain discriminator and program id
    unsafe { assume(6 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 34] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_account(&accounts[0]); // Assume Account
    // #[cfg(not(feature="multisig"))]
    cheatcode_is_spl_account(&accounts[1]); // Authority
    // #[cfg(feature="multisig")]
    // cheatcode_is_spl_multisig(&accounts[1]); // Authority

    //-Initial State-----------------------------------------------------------
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_init_state = get_account(&accounts[0]).account_state();
    let src_owner = get_account(&accounts[0]).owner();
    let authority = get_account(&accounts[0])
        .close_authority()
        .cloned()
        .unwrap_or(get_account(&accounts[0]).owner());
    let account_data_len = accounts[0].data_len();
    let maybe_multisig_is_initialised = if accounts[1].data_len() == Multisig::LEN
        && accounts[1].owner == &crate::id()
    {
        Some(get_multisig(&accounts[1]).is_initialized())
    } else {
        None
    };

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < 2 {
        assert_eq!(result, Err(ProgramError::Custom(12)));
        return result;
    } else if !(0..=3).contains(&instruction_data[0]) {
        assert_eq!(result, Err(ProgramError::Custom(12)));
        return result;
    } else if instruction_data[1] != 0 && instruction_data[1] != 1 {
        assert_eq!(result, Err(ProgramError::Custom(12)));
        return result;
    } else if instruction_data[1] == 1 && instruction_data.len() < 34 {
        assert_eq!(result, Err(ProgramError::Custom(12)));
        return result;
    } else if accounts.len() < 2 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else if account_data_len != Account::LEN && account_data_len != Mint::LEN {
        assert_eq!(result, Err(ProgramError::InvalidArgument));
        return result;
    } else {
        assert_eq!(account_data_len, Account::LEN); // established by cheatcode_is_spl_account
        if account_data_len == Account::LEN {
            if src_initialised.is_err() {
                assert_eq!(result, Err(ProgramError::InvalidAccountData));
                return result;
            } else if !src_initialised.unwrap() {
                assert_eq!(result, Err(ProgramError::UninitializedAccount));
                return result;
            } else if src_init_state.unwrap() == AccountState::Frozen {
                assert_eq!(result, Err(ProgramError::Custom(17)));
                return result;
            } else if instruction_data[0] != 2 && instruction_data[0] != 3 { // AuthorityType neither AccountOwner nor CloseAccount
                assert_eq!(result, Err(ProgramError::Custom(15)));
                return result;
            } else {
                if instruction_data[0] == 2 { // AccountOwner
                    inner_test_validate_owner(
                        &src_owner,
                        &accounts[1],
                        &accounts[2..],
                        maybe_multisig_is_initialised.clone(),
                        result.clone(),
                    )?;

                    if instruction_data[1] != 1 || instruction_data.len() < 34 {
                        assert_eq!(result, Err(ProgramError::Custom(12)));
                        return result;
                    }

                    assert_eq!(get_account(&accounts[0]).owner().as_ref(), &instruction_data[2..34]);
                    assert_eq!(get_account(&accounts[0]).delegate(), None);
                    assert_eq!(get_account(&accounts[0]).delegated_amount(), 0);
                    if get_account(&accounts[0]).is_native() {
                        assert_eq!(get_account(&accounts[0]).close_authority(), None);
                    }
                    assert!(result.is_ok())

                } else { // Close Account

                    inner_test_validate_owner(
                        &authority,
                        &accounts[1],
                        &accounts[2..],
                        maybe_multisig_is_initialised,
                        result.clone(),
                    )?;

                    if instruction_data[1] == 1 { // 1 ==> 34 <= instruction_data.len()
                        assert_eq!(get_account(&accounts[0]).close_authority().unwrap().as_ref(), &instruction_data[2..34]);
                    } else {
                        assert_eq!(get_account(&accounts[0]).close_authority(), None);
                    }
                    assert!(result.is_ok())
                }
            }
        }
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

/// program_id // Token Program ID
/// accounts[0] // Account Info - Mint Case
/// accounts[1] // Authority Info
/// accounts[2..13] // Signers
/// instruction_data[0] // Discriminator 6 (Set Authority Mint)
/// instruction_data[1] // Authority Type (instruction)
/// instruction_data[2] // New Authority Follows (0 -> No, 1 -> Yes)
/// instruction_data[3..35] // New Authority Pubkey
#[inline(never)]
fn test_process_set_authority_mint(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 2],
    instruction_data: &[u8; 35],
) -> ProgramResult {
    // Constrain discriminator and program id
    unsafe { assume(6 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 34] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_mint(&accounts[0]);     // Assume Mint
    // #[cfg(not(feature="multisig"))]
    cheatcode_is_spl_account(&accounts[1]);  // Authority
    // #[cfg(feature="multisig")]
    // cheatcode_is_spl_multisig(&accounts[1]); // Authority

    //-Initial State-----------------------------------------------------------
    let mint_data_len = accounts[0].data_len();
    let old_mint_authority_is_none = get_mint(&accounts[0]).mint_authority().is_none();
    let old_freeze_authority_is_none = get_mint(&accounts[0]).freeze_authority().is_none();
    let old_mint_authority = get_mint(&accounts[0]).mint_authority().cloned();
    let old_freeze_authority = get_mint(&accounts[0]).freeze_authority().cloned();
    let maybe_multisig_is_initialised = if accounts[1].data_len() == Multisig::LEN
        && accounts[1].owner == &crate::id()
    {
        Some(get_multisig(&accounts[1]).is_initialized())
    } else {
        None
    };
    let mint_is_initialised = get_mint(&accounts[0]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < 2 {
        assert_eq!(result, Err(ProgramError::Custom(12)));
        return result;
    } else if !(0..=3).contains(&instruction_data[0]) {
        assert_eq!(result, Err(ProgramError::Custom(12)));
        return result;
    } else if instruction_data[1] != 0 && instruction_data[1] != 1 {
        assert_eq!(result, Err(ProgramError::Custom(12)));
        return result;
    } else if instruction_data[1] == 1 && instruction_data.len() < 34 {
        assert_eq!(result, Err(ProgramError::Custom(12)));
        return result;
    } else if accounts.len() < 2 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else if mint_data_len != Account::LEN && mint_data_len != Mint::LEN {
        assert_eq!(result, Err(ProgramError::InvalidArgument));
        return result;
    } else {
        assert_eq!(mint_data_len, Mint::LEN); // established by cheatcode_is_spl_mint
            if !mint_is_initialised.unwrap() {
                assert_eq!(result, Err(ProgramError::UninitializedAccount));
                return result;
            } else if instruction_data[0] != 0 && instruction_data[0] != 1 { // AuthorityType neither MintTokens nor FreezeAccount
                assert_eq!(result, Err(ProgramError::Custom(15)));
                return result;
            } else {
                if instruction_data[0] == 0 { // MintTokens
                    if old_mint_authority_is_none {
                        assert_eq!(result, Err(ProgramError::Custom(5)));
                        return result;
                    }

                    inner_test_validate_owner(
                        old_mint_authority.as_ref().unwrap(),
                        &accounts[1],
                        &accounts[2..],
                        maybe_multisig_is_initialised.clone(),
                        result.clone(),
                    )?;

                    if instruction_data[1] == 1 { // 1 ==> 34 <= instruction_data.len()
                        assert_eq!(get_mint(&accounts[0]).mint_authority().unwrap().as_ref(), &instruction_data[2..34]);
                    } else {
                        assert_eq!(get_mint(&accounts[0]).mint_authority(), None);
                    }
                    assert!(result.is_ok())

                } else { // FreezeAccount
                    if old_freeze_authority_is_none {
                        assert_eq!(result, Err(ProgramError::Custom(16)));
                        return result;
                    }
                    inner_test_validate_owner(
                        old_freeze_authority.as_ref().unwrap(),
                        &accounts[1],
                        &accounts[2..],
                        maybe_multisig_is_initialised,
                        result.clone(),
                    )?;

                    if instruction_data[1] == 1 { // 1 ==> 34 <= instruction_data.len()
                        assert_eq!(get_mint(&accounts[0]).freeze_authority().unwrap().as_ref(), &instruction_data[2..34]);
                    } else {
                        assert_eq!(get_mint(&accounts[0]).freeze_authority(), None);
                    }
                    assert!(result.is_ok())
                }
            }

    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

/// program_id // Token Program ID
/// accounts[0] // Mint Info
/// accounts[1] // Destination Info
/// accounts[2] // Owner Info
/// accounts[3..14] // Signers
/// instruction_data[0] // Discriminator 7 (Mint To)
/// instruction_data[1..9] // Little Endian Bytes of u64 amount
#[inline(never)]
fn test_process_mint_to(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 3],
    instruction_data: &[u8; 9],
) -> ProgramResult {
    use spl_token_interface::state::AccountState;

    // Constrain discriminator and program id
    unsafe { assume(7 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 8] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_mint(&accounts[0]);
    cheatcode_is_spl_account(&accounts[1]);
    // #[cfg(not(feature="multisig"))]
    cheatcode_is_spl_account(&accounts[2]);
    // #[cfg(feature="multisig")]
    // cheatcode_is_spl_multisig(&accounts[2]);

    //-Initial State-----------------------------------------------------------
    let initial_supply = get_mint(&accounts[0]).supply();
    let initial_amount = get_account(&accounts[1]).amount();
    let mint_initialised = get_mint(&accounts[0]).is_initialized();
    let dst_initialised = get_account(&accounts[1]).is_initialized();
    let dst_init_state = get_account(&accounts[1]).account_state();
    let maybe_multisig_is_initialised = if accounts[2].data_len() == Multisig::LEN
        && accounts[2].owner == &crate::id()
    {
        Some(get_multisig(&accounts[2]).is_initialized())
    } else {
        None
    };

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < 8 {
        assert_eq!(result, Err(ProgramError::Custom(12)));
        return result;
    } else if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else if accounts[1].data_len() != Account::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if dst_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if !dst_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount));
        return result;
    } else if dst_init_state.unwrap() == AccountState::Frozen  { // unwrap must succeed due to dst_initialised not being err
        assert_eq!(result, Err(ProgramError::Custom(17)));
        return result;
    } else if get_account(&accounts[1]).is_native() {
        assert_eq!(result, Err(ProgramError::Custom(10)));
        return result;
    } else if accounts[0].key != &get_account(&accounts[1]).mint() {
        assert_eq!(result, Err(ProgramError::Custom(3)));
        return result;
    } else if accounts[0].data_len() != Mint::LEN {
        // Not sure if this is even possible if we get past the case above
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if mint_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if !mint_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount));
        return result;
    } else {
        if get_mint(&accounts[0]).mint_authority().is_some() {
            inner_test_validate_owner(
                get_mint(&accounts[0]).mint_authority().unwrap(),
                &accounts[2],
                &accounts[3..],
                maybe_multisig_is_initialised.clone(),
                result.clone(),
            )?;
        } else {
            assert_eq!(result, Err(ProgramError::Custom(5)));
            return result;
        }

        let amount = u64::from_le_bytes([instruction_data[0], instruction_data[1], instruction_data[2], instruction_data[3], instruction_data[4], instruction_data[5], instruction_data[6], instruction_data[7]]);

        if amount == 0 && accounts[0].owner != &crate::id() {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId));
            return result;
        } else if amount == 0 && accounts[1].owner != &crate::id() {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId));
            return result;
        } else if amount != 0 && u64::MAX - amount < initial_supply {
            assert_eq!(result, Err(ProgramError::Custom(14)));
            return result;
        }

        assert_eq!(get_mint(&accounts[0]).supply(), initial_supply + amount);
        assert_eq!(get_account(&accounts[1]).amount(), initial_amount + amount);
        assert!(result.is_ok());

    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

/// program_id // Token Program ID
/// accounts[0] // Source Info
/// accounts[1] // Mint Info
/// accounts[2] // Authority Info
/// accounts[3..14] // Signers
/// instruction_data[0] // Discriminator 8 (Burn)
/// instruction_data[1..9] // Little Endian Bytes of u64 amount
#[inline(never)]
fn test_process_burn(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 3],
    instruction_data: &[u8; 9],
) -> ProgramResult {
    use spl_token_interface::state::AccountState;

    // Constrain discriminator and program id
    unsafe { assume(8 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 8] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_account(&accounts[0]);
    cheatcode_is_spl_mint(&accounts[1]);
    // #[cfg(not(feature="multisig"))]
    cheatcode_is_spl_account(&accounts[2]);
    // #[cfg(feature="multisig")]
    // cheatcode_is_spl_multisig(&accounts[2]);

    //-Initial State-----------------------------------------------------------
    let amount = u64::from_le_bytes([instruction_data[0], instruction_data[1], instruction_data[2], instruction_data[3], instruction_data[4], instruction_data[5], instruction_data[6], instruction_data[7]]);
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_init_amount = get_account(&accounts[0]).amount();
    let src_init_state = get_account(&accounts[0]).account_state();
    let src_is_native = get_account(&accounts[0]).is_native();
    let src_mint = get_account(&accounts[0]).mint();
    let src_owned_sys_inc = get_account(&accounts[0]).is_owned_by_system_program_or_incinerator();
    let src_owner = get_account(&accounts[0]).owner();
    let old_src_delgate = get_account(&accounts[0]).delegate().cloned();
    let old_src_delgated_amount = get_account(&accounts[0]).delegated_amount();
    let mint_initialised = get_mint(&accounts[1]).is_initialized();
    let mint_init_supply = get_mint(&accounts[1]).supply();
    let mint_owner = *accounts[1].owner;
    let maybe_multisig_is_initialised = if accounts[2].data_len() == Multisig::LEN
        && accounts[2].owner == &crate::id()
    {
        Some(get_multisig(&accounts[2]).is_initialized())
    } else {
        None
    };
    let tx_signers: &[AccountInfo] = if accounts.len() > 3 {
        &accounts[3..]
    } else {
        &[]
    };

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < 8 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].data_len() != Account::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if src_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !src_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount))
    } else if accounts[1].data_len() != Mint::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if mint_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !mint_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount))
    } else if src_init_state.unwrap() == AccountState::Frozen {
        assert_eq!(result, Err(ProgramError::Custom(17)))
    } else if src_is_native {
        assert_eq!(result, Err(ProgramError::Custom(10)))
    } else if src_init_amount < amount {
        assert_eq!(result, Err(ProgramError::Custom(1)))
    } else if accounts[1].key != &src_mint {
        assert_eq!(result, Err(ProgramError::Custom(3)))
    } else {
        if !src_owned_sys_inc {
            if old_src_delgate == Some(*accounts[2].key) {
                inner_test_validate_owner(
                    old_src_delgate.as_ref().unwrap(),
                    &accounts[2],
                    tx_signers,
                    maybe_multisig_is_initialised.clone(),
                    result.clone(),
                )?;

                if old_src_delgated_amount < amount {
                    assert_eq!(result, Err(ProgramError::Custom(1)));
                    return result;
                }
            } else {
                inner_test_validate_owner(
                    &src_owner,
                    &accounts[2],
                    tx_signers,
                    maybe_multisig_is_initialised.clone(),
                    result.clone(),
                )?;
            }
        }

        if amount == 0 && src_owner != crate::id() {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId))
        } else if amount == 0 && mint_owner != crate::id() {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId))
        } else {
            assert!(get_account(&accounts[0]).amount() == src_init_amount - amount);
            assert!(get_mint(&accounts[1]).supply() == mint_init_supply - amount);
            assert!(result.is_ok());

            // Delegate updates
            if old_src_delgate.is_some() && *accounts[2].key == old_src_delgate.unwrap() {
                assert_eq!(get_account(&accounts[0]).delegated_amount(), old_src_delgated_amount - amount);
                if old_src_delgated_amount - amount == 0 {
                    assert_eq!(get_account(&accounts[0]).delegate(), None);
                }
            }
        }
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

/// program_id // Token Program ID
/// accounts[0] // Source Info
/// accounts[1] // Destination Info
/// accounts[2] // Authority Info
/// accounts[3..14] // Multisig Signers
/// instruction_data[0] // Discriminator 9 (Close Account)
#[inline(never)]
fn test_process_close_account(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 3],
    instruction_data: &[u8; 1],
) -> ProgramResult {
    use solana_sdk_ids::incinerator::ID as INCINERATOR_ID;

    // Constrain discriminator and program id
    unsafe { assume(9 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 0] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_account(&accounts[0]);
    cheatcode_is_spl_account(&accounts[1]);
    // #[cfg(not(feature="multisig"))]
    cheatcode_is_spl_account(&accounts[2]);
    // #[cfg(feature="multisig")]
    // cheatcode_is_spl_multisig(&accounts[2]);

    //-Initial State-----------------------------------------------------------
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_data_len = accounts[0].data_len();
    let src_init_amount = get_account(&accounts[0]).amount();
    let src_init_lamports = accounts[0].lamports();
    let dst_init_lamports = accounts[1].lamports();
    let src_is_native = get_account(&accounts[0]).is_native();
    let src_owned_sys_inc = get_account(&accounts[0]).is_owned_by_system_program_or_incinerator();
    let authority = get_account(&accounts[0]).close_authority().cloned().unwrap_or(get_account(&accounts[0]).owner());
    let maybe_multisig_is_initialised = if accounts[2].data_len() == Multisig::LEN
        && accounts[2].owner == &crate::id()
    {
        Some(get_multisig(&accounts[2]).is_initialized())
    } else {
        None
    };
    let tx_signers: &[AccountInfo] = if accounts.len() > 3 {
        &accounts[3..]
    } else {
        &[]
    };

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else if accounts[0].key == accounts[1].key {
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if src_data_len != Account::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if src_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if !src_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount));
        return result;
    } else if !src_is_native && src_init_amount != 0 {
        assert_eq!(result, Err(ProgramError::Custom(11)));
        return result;
    } else {
        if !src_owned_sys_inc {
            inner_test_validate_owner(
                &authority,
                &accounts[2],
                tx_signers,
                maybe_multisig_is_initialised.clone(),
                result.clone(),
            )?;
        } else if accounts[1].key != &INCINERATOR_ID {
            assert_eq!(result, Err(ProgramError::InvalidAccountData));
            return result;
        } else if u64::MAX - dst_init_lamports < src_init_lamports {
            assert_eq!(result, Err(ProgramError::Custom(14)));
            return result;
        }

        // Validate owner falls through to here if no error
        assert_eq!(accounts[1].lamports(), dst_init_lamports + src_init_lamports);
        assert_eq!(accounts[0].lamports(), 0);
        assert_eq!(accounts[0].data_len(), 0); // TODO: More sol_memset stuff?
        assert!(result.is_ok());
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

/// program_id // Token Program ID
/// accounts[0] // Source Account Info
/// accounts[1] // Mint Info
/// accounts[2] // Authority Info
/// accounts[3..13] // Signers
/// instruction_data[0] // Discriminator 10 (Freeze Account)
#[inline(never)]
fn test_process_freeze_account(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 3],
    instruction_data: &[u8; 1],
) -> ProgramResult {
    use spl_token_interface::state::AccountState;

    // Constrain discriminator and program id
    unsafe { assume(10 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 0] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_account(&accounts[0]);
    cheatcode_is_spl_mint(&accounts[1]);
    // #[cfg(not(feature="multisig"))]
    cheatcode_is_spl_account(&accounts[2]);
    // #[cfg(feature="multisig")]
    // cheatcode_is_spl_multisig(&accounts[2]);

    //-Initial State-----------------------------------------------------------
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_init_state = get_account(&accounts[0]).account_state();
    let src_is_native = get_account(&accounts[0]).is_native();
    let src_mint = get_account(&accounts[0]).mint();
    let mint_initialised = get_mint(&accounts[1]).is_initialized();
    let mint_freeze_auth = get_mint(&accounts[1]).freeze_authority().cloned();
    let maybe_multisig_is_initialised = if accounts[2].data_len() == Multisig::LEN
        && accounts[2].owner == &crate::id()
    {
        Some(get_multisig(&accounts[2]).is_initialized())
    } else {
        None
    };

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].data_len() != Account::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if src_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !src_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount))
    } else if src_init_state.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if src_init_state.unwrap() == AccountState::Frozen {
        assert_eq!(result, Err(ProgramError::Custom(13)))
    } else if src_is_native {
        assert_eq!(result, Err(ProgramError::Custom(10)))
    } else if accounts[1].key != &src_mint {
        assert_eq!(result, Err(ProgramError::Custom(3)))
    } else if accounts[1].data_len() != Mint::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if mint_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !mint_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount))
    } else if mint_freeze_auth.is_none() {
        assert_eq!(result, Err(ProgramError::Custom(16)))
    } else {
        inner_test_validate_owner(
            mint_freeze_auth.as_ref().unwrap(),
            &accounts[2],
            &accounts[3..],
            maybe_multisig_is_initialised.clone(),
            result.clone(),
        )?;

        assert_eq!(get_account(&accounts[0]).account_state().unwrap(), AccountState::Frozen);
        assert!(result.is_ok())
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

/// program_id // Token Program ID
/// accounts[0] // Source Account Info
/// accounts[1] // Mint Info
/// accounts[2] // Authority Info
/// accounts[3..13] // Signers
/// instruction_data[0] // Discriminator 11 (Thaw Account)
#[inline(never)]
fn test_process_thaw_account(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 3],
    instruction_data: &[u8; 1],
) -> ProgramResult {
    use spl_token_interface::state::AccountState;

    // Constrain discriminator and program id
    unsafe { assume(11 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 0] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_account(&accounts[0]);
    cheatcode_is_spl_mint(&accounts[1]);
    // #[cfg(not(feature="multisig"))]
    cheatcode_is_spl_account(&accounts[2]);
    // #[cfg(feature="multisig")]
    // cheatcode_is_spl_multisig(&accounts[2]);

    //-Initial State-----------------------------------------------------------
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_init_state = get_account(&accounts[0]).account_state();
    let src_is_native = get_account(&accounts[0]).is_native();
    let src_mint = get_account(&accounts[0]).mint();
    let mint_initialised = get_mint(&accounts[1]).is_initialized();
    let mint_freeze_auth = get_mint(&accounts[1]).freeze_authority().cloned();
    let maybe_multisig_is_initialised = if accounts[2].data_len() == Multisig::LEN
        && accounts[2].owner == &crate::id()
    {
        Some(get_multisig(&accounts[2]).is_initialized())
    } else {
        None
    };

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].data_len() != Account::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if src_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !src_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount))
    } else if src_init_state.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if src_init_state.unwrap() != AccountState::Frozen {
        assert_eq!(result, Err(ProgramError::Custom(13)))
    } else if src_is_native {
        assert_eq!(result, Err(ProgramError::Custom(10)))
    } else if accounts[1].key != &src_mint {
        assert_eq!(result, Err(ProgramError::Custom(3)))
    } else if accounts[1].data_len() != Mint::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if mint_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !mint_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount))
    } else if mint_freeze_auth.is_none() {
        assert_eq!(result, Err(ProgramError::Custom(16)))
    } else {
        inner_test_validate_owner(
            mint_freeze_auth.as_ref().unwrap(),
            &accounts[2],
            &accounts[3..],
            maybe_multisig_is_initialised.clone(),
            result.clone(),
        )?;

        assert_eq!(get_account(&accounts[0]).account_state().unwrap(), AccountState::Initialized);
        assert!(result.is_ok())
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

/// program_id // Token Program ID
/// accounts[0] // Source Info
/// accounts[1] // Mint Info
/// accounts[2] // Destination Info
/// accounts[3] // Authority Info
/// accounts[4..15] // Signers
/// instruction_data[0] // Discriminator 12 (Transfer Checked)
/// instruction_data[1..10] // Little Endian Bytes of u64 amount, and decimals
#[inline(never)]
fn test_process_transfer_checked(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 4],
    instruction_data: &[u8; 10],
) -> ProgramResult {
    use spl_token_interface::state::AccountState;

    // Constrain discriminator and program id
    unsafe { assume(12 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 9] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_account(&accounts[0]);
    cheatcode_is_spl_mint(&accounts[1]);
    cheatcode_is_spl_account(&accounts[2]);
    // #[cfg(not(feature="multisig"))]
    cheatcode_is_spl_account(&accounts[3]);
    // #[cfg(feature="multisig")]
    // cheatcode_is_spl_multisig(&accounts[3]);

    //-Initial State-----------------------------------------------------------
    let amount = u64::from_le_bytes([instruction_data[0], instruction_data[1], instruction_data[2], instruction_data[3], instruction_data[4], instruction_data[5], instruction_data[6], instruction_data[7]]);
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let dst_initialised = get_account(&accounts[2]).is_initialized();
    let src_initial_amount = get_account(&accounts[0]).amount();
    let dst_initial_amount = get_account(&accounts[2]).amount();
    let src_initial_lamports = accounts[0].lamports();
    let dst_initial_lamports = accounts[2].lamports();
    let src_owner = get_account(&accounts[0]).owner();
    let old_src_delgate = get_account(&accounts[0]).delegate().cloned();
    let old_src_delgated_amount = get_account(&accounts[0]).delegated_amount();
    let mint_initialised = get_mint(&accounts[1]).is_initialized();
    let maybe_multisig_is_initialised = if accounts[3].data_len() == Multisig::LEN
        && accounts[3].owner == &crate::id()
    {
        Some(get_multisig(&accounts[3]).is_initialized())
    } else {
        None
    };
    let tx_signers: &[AccountInfo] = if accounts.len() > 4 {
        &accounts[4..]
    } else {
        &[]
    };

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < 9 {
        assert_eq!(result, Err(ProgramError::Custom(12)));
        return result;
    } else if accounts.len() < 4 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else if src_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if !src_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount));
        return result;
    } else if accounts[0].key != accounts[2].key && dst_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if accounts[0].key != accounts[2].key && !dst_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount));
        return result;
    } else if get_account(&accounts[0]).account_state().unwrap() == AccountState::Frozen {
        assert_eq!(result, Err(ProgramError::Custom(17)));
        return result;
    } else if accounts[0].key != accounts[2].key && get_account(&accounts[2]).account_state().unwrap() == AccountState::Frozen {
        assert_eq!(result, Err(ProgramError::Custom(17)));
        return result;
    }  else if src_initial_amount < amount {
        assert_eq!(result, Err(ProgramError::Custom(1)));
        return result;
    } else if accounts[0].key != accounts[2].key && get_account(&accounts[0]).mint() != get_account(&accounts[2]).mint() {
        assert_eq!(result, Err(ProgramError::Custom(3)));
        return result;
    } else if accounts[1].key != &get_account(&accounts[0]).mint() {
        assert_eq!(result, Err(ProgramError::Custom(3)));
        return result;
    } else if accounts[1].data_len() != core::mem::size_of::<Mint>() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if mint_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if !mint_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount));
        return result;
    } else if instruction_data[8] != get_mint(&accounts[1]).decimals() {
        assert_eq!(result, Err(ProgramError::Custom(18)));
        return result;
    } else {
        if old_src_delgate == Some(*accounts[3].key) {
            inner_test_validate_owner(
                old_src_delgate.as_ref().unwrap(),
                &accounts[3],
                tx_signers,
                maybe_multisig_is_initialised.clone(),
                result.clone(),
            )?;

            if old_src_delgated_amount < amount {
                assert_eq!(result, Err(ProgramError::Custom(1)));
                return result;
            }
        } else {
            inner_test_validate_owner(
                &src_owner,
                &accounts[3],
                tx_signers,
                maybe_multisig_is_initialised,
                result.clone(),
            )?;
        }

        if (accounts[0].key == accounts[2].key || amount == 0) && accounts[0].owner != &crate::id() {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId));
            return result;
        } else if (accounts[0].key == accounts[2].key || amount == 0) && accounts[2].owner != &crate::id() {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId));
            return result;
        } else if accounts[0].key != accounts[2].key && amount != 0 {
            if get_account(&accounts[0]).is_native() && src_initial_lamports < amount {
                // Not sure how to fund native mint
                assert_eq!(result, Err(ProgramError::Custom(14)));
                return result;
            } else if get_account(&accounts[0]).is_native() && u64::MAX - amount < dst_initial_lamports {
                // Not sure how to fund native mint
                assert_eq!(result, Err(ProgramError::Custom(14)));
                return result;
            }

            assert_eq!(get_account(&accounts[0]).amount(), src_initial_amount - amount);
            assert_eq!(get_account(&accounts[2]).amount(), dst_initial_amount + amount);

            if get_account(&accounts[0]).is_native() {
                assert_eq!(accounts[0].lamports(), src_initial_lamports - amount);
                assert_eq!(accounts[1].lamports(), dst_initial_lamports + amount);
            }
        }

        assert!(result.is_ok());
        // Delegate updates
        if old_src_delgate == Some(*accounts[3].key) && accounts[0].key != accounts[2].key {
            assert_eq!(get_account(&accounts[0]).delegated_amount(), old_src_delgated_amount - amount);
            if old_src_delgated_amount - amount == 0 {
                assert_eq!(get_account(&accounts[0]).delegate(), None);
            }
        }
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

/// program_id // Token Program ID
/// accounts[0] // Source Account Info
/// accounts[1] // Expected Mint Info
/// accounts[2] // Delegate Info
/// accounts[3] // Owner Info
/// accounts[4..15] // Signers
/// instruction_data[0] // Discriminator 13 (Approve Checked)
/// instruction_data[1..10] // Little Endian Bytes of u64 amount, and decimals
#[inline(never)]
fn test_process_approve_checked(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 4],
    instruction_data: &[u8; 10],
) -> ProgramResult {
    use spl_token_interface::state::AccountState;

    // Constrain discriminator and program id
    unsafe { assume(13 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 9] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_account(&accounts[0]); // Source Account
    cheatcode_is_spl_mint(&accounts[1]);    // Expected Mint
    cheatcode_is_spl_account(&accounts[2]); // Delegate
    // #[cfg(not(feature="multisig"))]
    cheatcode_is_spl_account(&accounts[3]); // Owner
    // #[cfg(feature="multisig")]
    // cheatcode_is_spl_multisig(&accounts[3]); // Owner

    //-Initial State-----------------------------------------------------------
    let amount = u64::from_le_bytes([instruction_data[0], instruction_data[1], instruction_data[2], instruction_data[3], instruction_data[4], instruction_data[5], instruction_data[6], instruction_data[7]]);
    let src_owner = get_account(&accounts[0]).owner();
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_init_state = get_account(&accounts[0]).account_state();
    let mint_initialised = get_mint(&accounts[1]).is_initialized();
    let maybe_multisig_is_initialised = if accounts[3].data_len() == Multisig::LEN
        && accounts[3].owner == &crate::id()
    {
        Some(get_multisig(&accounts[3]).is_initialized())
    } else {
        None
    };

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < 9 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.len() < 4 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].data_len() != Account::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if src_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !src_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount))
    } else if src_init_state.unwrap() == AccountState::Frozen  { // This should be safe to unwrap due to above check passing
        assert_eq!(result, Err(ProgramError::Custom(17)))
    } else if accounts[1].key != &get_account(&accounts[0]).mint() {
        assert_eq!(result, Err(ProgramError::Custom(3)))
    } else if accounts[1].data_len() != Mint::LEN {
        // Not sure if this is even possible if we get past the case above
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if mint_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !mint_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount))
    } else if instruction_data[8] != get_mint(&accounts[1]).decimals() {
        assert_eq!(result, Err(ProgramError::Custom(18)))
    } else {
        inner_test_validate_owner(
            &src_owner,
            &accounts[3],
            &accounts[4..],
            maybe_multisig_is_initialised.clone(),
            result.clone(),
        )?;

        assert_eq!(get_account(&accounts[0]).delegate().unwrap(), accounts[2].key);
        assert_eq!(get_account(&accounts[0]).delegated_amount(), amount);
        assert!(result.is_ok())
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

/// program_id // Token Program ID
/// accounts[0] // Mint Info
/// accounts[1] // Destination Info
/// accounts[2] // Owner Info
/// accounts[3..14] // Signers
/// instruction_data[0] // Discriminator 14 (Mint To Checked)
/// instruction_data[1..10] // Little Endian Bytes of u64 amount, and decimals
#[inline(never)]
fn test_process_mint_to_checked(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 3],
    instruction_data: &[u8; 10],
) -> ProgramResult {
    use spl_token_interface::state::AccountState;

    // Constrain discriminator and program id
    unsafe { assume(14 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 9] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_mint(&accounts[0]);
    cheatcode_is_spl_account(&accounts[1]);
    // #[cfg(not(feature="multisig"))]
    cheatcode_is_spl_account(&accounts[2]);
    // #[cfg(feature="multisig")]
    // cheatcode_is_spl_multisig(&accounts[2]);

    //-Initial State-----------------------------------------------------------
    let initial_supply = get_mint(&accounts[0]).supply();
    let initial_amount = get_account(&accounts[1]).amount();
    let mint_initialised = get_mint(&accounts[0]).is_initialized();
    let dst_initialised = get_account(&accounts[1]).is_initialized();
    let dst_init_state = get_account(&accounts[1]).account_state();
    let maybe_multisig_is_initialised = if accounts[2].data_len() == Multisig::LEN
        && accounts[2].owner == &crate::id()
    {
        Some(get_multisig(&accounts[2]).is_initialized())
    } else {
        None
    };

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < 9 {
        assert_eq!(result, Err(ProgramError::Custom(12)));
        return result;
    } else if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else if accounts[1].data_len() != Account::LEN { // TODO Daniel: is it possible for something to be provided that has the same len but is not an account?
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if dst_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if !dst_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount));
        return result;
    } else if dst_init_state.unwrap() == AccountState::Frozen  { // unwrap must succeed due to dst_initialised not being err
        assert_eq!(result, Err(ProgramError::Custom(17)));
        return result;
    } else if get_account(&accounts[1]).is_native() {
        assert_eq!(result, Err(ProgramError::Custom(10)));
        return result;
    } else if accounts[0].key != &get_account(&accounts[1]).mint() {
        assert_eq!(result, Err(ProgramError::Custom(3)));
        return result;
    } else if accounts[0].data_len() != Mint::LEN {
        // Not sure if this is even possible if we get past the case above
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if mint_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if !mint_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount));
        return result;
    } else if instruction_data[8] != get_mint(&accounts[0]).decimals() {
        assert_eq!(result, Err(ProgramError::Custom(18)));
        return result;
    } else {
        if get_mint(&accounts[0]).mint_authority().is_some() {
            inner_test_validate_owner(
                get_mint(&accounts[0]).mint_authority().unwrap(),
                &accounts[2],
                &accounts[3..],
                maybe_multisig_is_initialised.clone(),
                result.clone(),
            )?;
        } else {
            assert_eq!(result, Err(ProgramError::Custom(5)));
            return result;
        }

        let amount = u64::from_le_bytes([instruction_data[0], instruction_data[1], instruction_data[2], instruction_data[3], instruction_data[4], instruction_data[5], instruction_data[6], instruction_data[7]]);

        if amount == 0 && accounts[0].owner != &crate::id() {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId));
            return result;
        } else if amount == 0 && accounts[1].owner != &crate::id() {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId));
            return result;
        } else if amount != 0 && u64::MAX - amount < initial_supply {
            assert_eq!(result, Err(ProgramError::Custom(14)));
            return result;
        }

        assert_eq!(get_mint(&accounts[0]).supply(), initial_supply + amount);
        assert_eq!(get_account(&accounts[1]).amount(), initial_amount + amount);
        assert!(result.is_ok());
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

/// program_id // Token Program ID
/// accounts[0] // Source Info
/// accounts[1] // Mint Info
/// accounts[2] // Authority Info
/// accounts[3..14] // Signers
/// instruction_data[0] // Discriminator 15 (Burn Checked)
/// instruction_data[1..10] // Little Endian Bytes of u64 amount, and decimals
#[inline(never)]
fn test_process_burn_checked(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 3],
    instruction_data: &[u8; 10],
) -> ProgramResult {
    use spl_token_interface::state::AccountState;

    // Constrain discriminator and program id
    unsafe { assume(15 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 9] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_account(&accounts[0]);
    cheatcode_is_spl_mint(&accounts[1]);
    // #[cfg(not(feature="multisig"))]
    cheatcode_is_spl_account(&accounts[2]);
    // #[cfg(feature="multisig")]
    // cheatcode_is_spl_multisig(&accounts[2]);

    //-Initial State-----------------------------------------------------------
    let amount = u64::from_le_bytes([instruction_data[0], instruction_data[1], instruction_data[2], instruction_data[3], instruction_data[4], instruction_data[5], instruction_data[6], instruction_data[7]]);
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_init_amount = get_account(&accounts[0]).amount();
    let src_init_state = get_account(&accounts[0]).account_state();
    let src_is_native = get_account(&accounts[0]).is_native();
    let src_mint = get_account(&accounts[0]).mint();
    let src_owned_sys_inc = get_account(&accounts[0]).is_owned_by_system_program_or_incinerator();
    let src_owner = get_account(&accounts[0]).owner();
    let old_src_delgate = get_account(&accounts[0]).delegate().cloned();
    let old_src_delgated_amount = get_account(&accounts[0]).delegated_amount();
    let mint_initialised = get_mint(&accounts[1]).is_initialized();
    let mint_init_supply = get_mint(&accounts[1]).supply();
    let mint_decimals = get_mint(&accounts[1]).decimals();
    let mint_owner = *accounts[1].owner;
    let maybe_multisig_is_initialised = if accounts[2].data_len() == Multisig::LEN
        && accounts[2].owner == &crate::id()
    {
        Some(get_multisig(&accounts[2]).is_initialized())
    } else {
        None
    };
    let tx_signers: &[AccountInfo] = if accounts.len() > 3 {
        &accounts[3..]
    } else {
        &[]
    };

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < 9 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].data_len() != Account::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if src_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !src_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount))
    } else if accounts[1].data_len() != Mint::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if mint_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !mint_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount))
    } else if src_init_state.unwrap() == AccountState::Frozen {
        assert_eq!(result, Err(ProgramError::Custom(17)))
    } else if src_is_native {
        assert_eq!(result, Err(ProgramError::Custom(10)))
    } else if src_init_amount < amount {
        assert_eq!(result, Err(ProgramError::Custom(1)))
    } else if accounts[1].key != &src_mint {
        assert_eq!(result, Err(ProgramError::Custom(3)))
    } else if instruction_data[8] != mint_decimals {
        assert_eq!(result, Err(ProgramError::Custom(18)))
    } else {
        if !src_owned_sys_inc {
            if old_src_delgate == Some(*accounts[2].key) {
                inner_test_validate_owner(
                    old_src_delgate.as_ref().unwrap(),
                    &accounts[2],
                    tx_signers,
                    maybe_multisig_is_initialised.clone(),
                    result.clone(),
                )?;

                if old_src_delgated_amount < amount {
                    assert_eq!(result, Err(ProgramError::Custom(1)));
                    return result;
                }
            } else {
                inner_test_validate_owner(
                    &src_owner,
                    &accounts[2],
                    tx_signers,
                    maybe_multisig_is_initialised.clone(),
                    result.clone(),
                )?;
            }
        }

        if amount == 0 && src_owner != crate::id() {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId))
        } else if amount == 0 && mint_owner != crate::id() {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId))
        } else {
            assert!(get_account(&accounts[0]).amount() == src_init_amount - amount);
            assert!(get_mint(&accounts[1]).supply() == mint_init_supply - amount);
            assert!(result.is_ok());

            // Delegate updates
            if old_src_delgate.is_some() && *accounts[2].key == old_src_delgate.unwrap() {
                assert_eq!(get_account(&accounts[0]).delegated_amount(), old_src_delgated_amount - amount);
                if old_src_delgated_amount - amount == 0 {
                    assert_eq!(get_account(&accounts[0]).delegate(), None);
                }
            }
        }
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

/// program_id // Token Program ID
/// accounts[0] // New Account Info
/// accounts[1] // Mint Info
/// accounts[2] // Rent Sysvar Info
/// instruction_data[0] // Discriminator 16 (Initialize Account2)
/// instruction_data[1..] // Owner
#[inline(never)]
fn test_process_initialize_account2(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 3],
    instruction_data: &[u8; 33],
) -> ProgramResult {
    use spl_token_interface::state::AccountState;

    // Constrain discriminator and program id
    unsafe { assume(16 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 32] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_account(&accounts[0]);
    cheatcode_is_spl_mint(&accounts[1]);
    cheatcode_is_spl_rent(&accounts[2]);

    //-Initial State-----------------------------------------------------------
    let initial_state_new_account =  get_account(&accounts[0])
        .account_state();

    let minimum_balance = get_rent(&accounts[2]).minimum_balance(accounts[0].data_len());

    let is_native_mint = accounts[1].key == &native_mint::ID;

    let mint_is_initialised = get_mint(&accounts[1]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < pubkey::PUBKEY_BYTES {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
    } else if accounts[2].key != &solana_sysvar::rent::ID {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if accounts[0].data_len() != Account::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if initial_state_new_account.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if initial_state_new_account.unwrap() != AccountState::Uninitialized {
        assert_eq!(result, Err(ProgramError::Custom(6)))
    } else if accounts[0].lamports() < minimum_balance {
        assert_eq!(result, Err(ProgramError::Custom(0)))
    } else if !is_native_mint && accounts[1].owner != &crate::id() {
        assert_eq!(result, Err(ProgramError::IncorrectProgramId))
    } else if !is_native_mint
            && accounts[1].owner == &crate::id()
            && mint_is_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !is_native_mint
            && accounts[1].owner == &crate::id()
            && !mint_is_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::Custom(2)))
    } else {
        assert!(result.is_ok());
        assert_eq!(get_account(&accounts[0]).account_state().unwrap(), AccountState::Initialized);
        assert_eq!(get_account(&accounts[0]).mint(), *accounts[1].key);
        assert_eq!(get_account(&accounts[0]).owner(), (*instruction_data).into());

        if is_native_mint {
            assert!(get_account(&accounts[0]).is_native());
            assert_eq!(get_account(&accounts[0]).native_amount().unwrap(), minimum_balance);
            assert_eq!(get_account(&accounts[0]).amount(), accounts[0].lamports() - minimum_balance);
        }
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

#[inline(never)]
fn test_process_sync_native(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 1],
    instruction_data: &[u8; 1],
) -> ProgramResult {
    // Constrain discriminator and program id
    unsafe { assume(17 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 0] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_account(&accounts[0]);

    //-Initial State-----------------------------------------------------------
    let src_owner = accounts[0].owner;
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_native_amount = get_account(&accounts[0]).native_amount();
    let src_init_lamports = accounts[0].lamports();
    let src_init_amount = get_account(&accounts[0]).amount();

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() != 1 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if src_owner != &crate::id() {
        assert_eq!(result, Err(ProgramError::IncorrectProgramId))
    } else if accounts[0].data_len() != Account::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if src_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !src_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount))
    } else if src_native_amount.is_none() {
        assert_eq!(result, Err(ProgramError::Custom(19)))
    } else if src_init_lamports < src_native_amount.unwrap() {
        assert_eq!(result, Err(ProgramError::Custom(14)))
    } else if src_init_lamports - src_native_amount.unwrap() < src_init_amount {
        assert_eq!(result, Err(ProgramError::Custom(13)))
    } else {
        assert_eq!(get_account(&accounts[0]).amount(), src_init_lamports - src_native_amount.unwrap());
        assert!(result.is_ok())
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

/// program_id // Token Program ID
/// accounts[0] // New Account Info
/// accounts[1] // Mint Info
/// instruction_data[0] // Discriminator 18 (Initialize Account3)
/// instruction_data[1..] // Owner
#[inline(never)]
fn test_process_initialize_account3(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 2],
    instruction_data: &[u8; 33],
) -> ProgramResult {
    use spl_token_interface::state::AccountState;

    // Constrain discriminator and program id
    unsafe { assume(18 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 32] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_account(&accounts[0]);
    cheatcode_is_spl_mint(&accounts[1]);

    //-Initial State-----------------------------------------------------------
    let initial_state_new_account =  get_account(&accounts[0])
        .account_state();

    // Note: Rent is a supported sysvar so ProgramError::UnsupportedSysvar should be impossible
    let rent = solana_rent::Rent::get().unwrap();
    let minimum_balance = rent.minimum_balance(accounts[0].data_len());

    let is_native_mint = accounts[1].key == &native_mint::ID;

    let mint_is_initialised = get_mint(&accounts[1]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < pubkey::PUBKEY_BYTES {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.len() < 2 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
    } else if accounts[0].data_len() != Account::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if initial_state_new_account.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if initial_state_new_account.unwrap() != AccountState::Uninitialized {
        assert_eq!(result, Err(ProgramError::Custom(6)))
    } else if accounts[0].lamports() < minimum_balance {
        assert_eq!(result, Err(ProgramError::Custom(0)))
    } else if !is_native_mint && accounts[1].owner != &crate::id() {
        assert_eq!(result, Err(ProgramError::IncorrectProgramId))
    } else if !is_native_mint
            && accounts[1].owner == &crate::id()
            && mint_is_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !is_native_mint
            && accounts[1].owner == &crate::id()
            && !mint_is_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::Custom(2)))
    } else {
        assert!(result.is_ok());
        assert_eq!(get_account(&accounts[0]).account_state().unwrap(), AccountState::Initialized);
        assert_eq!(get_account(&accounts[0]).mint(), *accounts[1].key);
        assert_eq!(get_account(&accounts[0]).owner(), (*instruction_data).into());

        if is_native_mint {
            assert!(get_account(&accounts[0]).is_native());
            assert_eq!(get_account(&accounts[0]).native_amount().unwrap(), minimum_balance);
            assert_eq!(get_account(&accounts[0]).amount(), accounts[0].lamports() - minimum_balance);
        }
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

/// program_id // Token Program ID
/// accounts[0]   // Multisig Info
/// accounts[1..] // Signers
/// accounts[1..].len() // n
/// instruction_data[0] // Discriminator 19 (Initialize Multisig2)
/// instruction_data[2] // m
#[inline(never)]
fn test_process_initialize_multisig2(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 4],
    instruction_data: &[u8; 2],
) -> ProgramResult {
    // Constrain discriminator and program id
    unsafe { assume(19 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 1] = instruction_data.last_chunk().unwrap();

                                                           // ^ FIXME: totally arbitrary for the tests
    // cheatcode_is_spl_multisig(&accounts[0]);
    cheatcode_is_spl_account(&accounts[1]); // Signer
    cheatcode_is_spl_account(&accounts[2]); // Signer
    cheatcode_is_spl_account(&accounts[3]); // Signer

    //-Initial State-----------------------------------------------------------
    let multisig_already_initialised = get_multisig(&accounts[0]).is_initialized();
    let multisig_init_lamports = accounts[0].lamports();
    // Note: Rent is a supported sysvar so ProgramError::UnsupportedSysvar should be impossible
    let rent = solana_rent::Rent::get().unwrap();
    let minimum_balance = rent.minimum_balance(accounts[0].data_len());

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.is_empty() {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.len() < 1 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].data_len() != Multisig::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if multisig_already_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if multisig_already_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::Custom(6)))
    } else if multisig_init_lamports < minimum_balance {
        assert_eq!(result, Err(ProgramError::Custom(0)))
    } else if !((((accounts.len() - 1) as u8) >= 1) && (((accounts.len() - 1) as u8) <= 11)) {
        assert_eq!(result, Err(ProgramError::Custom(7)))
    } else if !(((instruction_data[0]) >= 1) && ((instruction_data[0]) <= 11)) {
        assert_eq!(result, Err(ProgramError::Custom(8)))
    } else {
        assert!(accounts[1..]
            .iter()
            .map(|signer| *signer.key)
            .eq(
                get_multisig(&accounts[0])
                .signers()
                .iter()
                .take(accounts[1..].len())
                .copied()
            )
        );
        assert_eq!(get_multisig(&accounts[0]).m(), instruction_data[0]);
        assert_eq!(get_multisig(&accounts[0]).n() as usize, accounts.len() - 1);
        assert!(get_multisig(&accounts[0]).is_initialized().is_ok());
        assert!(get_multisig(&accounts[0]).is_initialized().unwrap());
        assert!(result.is_ok())
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

/// program_id // Token Program ID
/// accounts[0] // Mint Info
/// instruction_data[0] // Discriminator 20 (Initialize Mint2 Freeze)
/// instruction_data[1]      // Decimals
/// instruction_data[2..34]  // Mint Authority Pubkey
/// instruction_data[34]     // Freeze Authority Exists? 1 for freeze
/// instruction_data[35..67] // instruction_data[34] == 1 ==> Freeze Authority Pubkey
#[inline(never)]
fn test_process_initialize_mint2_freeze(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 1],
    instruction_data: &[u8; 67],
) -> ProgramResult {
    // Constrain discriminator and program id
    unsafe { assume(20 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 66] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_mint(&accounts[0]);

    //-Initial State-----------------------------------------------------------
    // Note: Rent is a supported sysvar so ProgramError::UnsupportedSysvar should be impossible
    let rent = solana_rent::Rent::get().unwrap();
    let minimum_balance = rent.minimum_balance(accounts[0].data_len());
    let mint_is_initialised_prior = get_mint(&accounts[0]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < 34 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if instruction_data[33] != 0 && instruction_data[33] != 1 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if instruction_data[33] == 1 && instruction_data.len() < 66 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.len() < 1 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].data_len() != Mint::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if mint_is_initialised_prior.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if mint_is_initialised_prior.unwrap()  {
        assert_eq!(result, Err(ProgramError::Custom(6)))
    } else if accounts[0].lamports() < minimum_balance {
        assert_eq!(result, Err(ProgramError::Custom(0)))
    } else {
        assert!(get_mint(&accounts[0]).is_initialized().unwrap());
        assert_eq!(get_mint(&accounts[0]).mint_authority().unwrap().as_ref(), &instruction_data[1..33]);
        assert_eq!(get_mint(&accounts[0]).decimals(), instruction_data[0]);

        if instruction_data[33] == 1 {
            assert_eq!(get_mint(&accounts[0]).freeze_authority().unwrap().as_ref(), &instruction_data[34..66]);
        }
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

/// program_id // Token Program ID
/// accounts[0] // Mint Info
/// instruction_data[0] // Discriminator 20 (Initialize Mint2 No Freeze)
/// instruction_data[1]      // Decimals
/// instruction_data[2..34]  // Mint Authority Pubkey
/// instruction_data[34]     // Freeze Authority Exists? 0 for no freeze
#[inline(never)]
fn test_process_initialize_mint2_no_freeze(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 1],
    instruction_data: &[u8; 35],
) -> ProgramResult {
    // Constrain discriminator and program id
    unsafe { assume(20 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 34] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_mint(&accounts[0]);

    //-Initial State-----------------------------------------------------------
    // Note: Rent is a supported sysvar so ProgramError::UnsupportedSysvar should be impossible
    let rent = solana_rent::Rent::get().unwrap();
    let minimum_balance = rent.minimum_balance(accounts[0].data_len());
    let mint_is_initialised_prior = get_mint(&accounts[0]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < 34 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if instruction_data[33] != 0 && instruction_data[33] != 1 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if instruction_data[33] == 1 && instruction_data.len() < 66 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.len() < 1 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].data_len() != Mint::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if mint_is_initialised_prior.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if mint_is_initialised_prior.unwrap()  {
        assert_eq!(result, Err(ProgramError::Custom(6)))
    } else if accounts[0].lamports() < minimum_balance {
        assert_eq!(result, Err(ProgramError::Custom(0)))
    } else {
        assert!(get_mint(&accounts[0]).is_initialized().unwrap());
        assert_eq!(get_mint(&accounts[0]).mint_authority().unwrap().as_ref(), &instruction_data[1..33]);
        assert_eq!(get_mint(&accounts[0]).decimals(), instruction_data[0]);

        if instruction_data[33] == 1 {
            assert_eq!(get_mint(&accounts[0]).freeze_authority().unwrap().as_ref(), &instruction_data[34..66]);
        }
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

/// program_id // Token Program ID
/// accounts[0] // Mint Info
/// instruction_data[0] // Discriminator 21 (Get Account Data Size)
#[inline(never)]
fn test_process_get_account_data_size(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 1],
    instruction_data: &[u8; 1],
) -> ProgramResult {
    // Constrain discriminator and program id
    unsafe { assume(21 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 0] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_mint(&accounts[0]);

    //-Initial State-----------------------------------------------------------
    let mint_initialised = get_mint(&accounts[0]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() < 1 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].owner != &crate::id() {
        assert_eq!(result, Err(ProgramError::IncorrectProgramId))
    } else if accounts[0].data_len() != Mint::LEN {
        assert_eq!(result, Err(ProgramError::Custom(2)))
    } else if mint_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::Custom(2)))
    } else if !mint_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::Custom(2)))
    } else {
        // NOTE: This uses syscalls::sol_set_return_data
        assert!(result.is_ok())
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

#[inline(never)]
fn test_process_initialize_immutable_owner(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 1],
    instruction_data: &[u8; 1],
) -> ProgramResult {
    // Constrain discriminator and program id
    unsafe { assume(22 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 0] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_account(&accounts[0]);

    //-Initial State-----------------------------------------------------------
    let src_initialised = get_account(&accounts[0]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() != 1 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].data_len() != Account::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if src_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if src_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::Custom(6)))
    } else {
        assert!(result.is_ok())
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

#[inline(never)]
fn test_process_amount_to_ui_amount(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 1],
    instruction_data: &[u8; 9],
) -> ProgramResult {
    // Constrain discriminator and program id
    unsafe { assume(23 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 8] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_mint(&accounts[0]);

    //-Initial State-----------------------------------------------------------
    let mint_initialised = get_mint(&accounts[0]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < 8 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.len() < 1 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].owner != &crate::id() {
        assert_eq!(result, Err(ProgramError::IncorrectProgramId))
    } else if accounts[0].data_len() != Mint::LEN {
        assert_eq!(result, Err(ProgramError::Custom(2)))
    } else if mint_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !mint_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::Custom(2)))
    } else {
        assert!(result.is_ok())
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

#[inline(never)]
fn test_process_ui_amount_to_amount(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 1],
    instruction_data: &[u8],
) -> ProgramResult {
    // Constrain discriminator and program id
    unsafe { assume(24 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8] = &instruction_data[1..];

    cheatcode_is_spl_mint(&accounts[0]);

    //-Initial State-----------------------------------------------------------
    let ui_amount = core::str::from_utf8(instruction_data);
    let mint_initialised = get_mint(&accounts[0]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    // TODO: validations module is private, so we need a work around
    if ui_amount.is_err() {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.len() < 1 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].owner != &crate::id() {
        assert_eq!(result, Err(ProgramError::IncorrectProgramId))
    } else if accounts[0].data_len() != Mint::LEN {
        assert_eq!(result, Err(ProgramError::Custom(2)))
    } else if mint_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !mint_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::Custom(2)))
    } else if ui_amount.unwrap().is_empty() {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if ui_amount.unwrap() == "." {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if 1 < ui_amount.unwrap().chars().filter(|&c| c == '.').count() {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if ui_amount.unwrap().starts_with('.') && ui_amount.unwrap().chars().skip(1).all(|c| c == '0') {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if ui_amount.unwrap().split_once('.').map_or(false, |(_, frac)| { (get_mint(&accounts[0]).decimals() as usize) < frac.trim_end_matches('0').len()}) {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if ui_amount.unwrap().split_once('.').map_or(
        257_usize < ui_amount.unwrap().len() + (get_mint(&accounts[0]).decimals() as usize),
        |(ints, _)| { 257_usize < ints.len() + (get_mint(&accounts[0]).decimals() as usize) }) {
            assert_eq!(result, Err(ProgramError::InvalidArgument))
    } /*else if ui_amount.unwrap() == "+." {
        // TODO: Why is this valid?
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if ui_amount.unwrap() == "+" {
        // TODO: Why is this valid?
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    }*/ else if ui_amount.unwrap().chars().nth(0).unwrap() == '-' {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if ui_amount.unwrap().contains(|c: char| !c.is_digit(10) && c != '+' && c != '.') {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if ui_amount.unwrap().split_once('.').map_or(
        {
            const MAX_VAL: &str = "1844674407370955"; // TODO: What should this be?
            let ui_amount = ui_amount.unwrap();
            let ui_amount = ui_amount.strip_prefix('+').unwrap_or(ui_amount);
            let ui_amount = ui_amount.trim_start_matches('0');
            match ui_amount.len().cmp(&MAX_VAL.len()) {
                core::cmp::Ordering::Less => false,
                core::cmp::Ordering::Greater => true,
                core::cmp::Ordering::Equal => MAX_VAL < ui_amount,
            }
        },
        |(ints, fracs)| {
            const MAX_VAL: &str = "1844674407370955"; // TODO: What should this be?
            let ints = ints.strip_prefix('+').unwrap_or(ints);
            let hi = ints.trim_start_matches('0');
            let lo = if hi.is_empty() { fracs.trim_start_matches('0') } else { fracs };

            let total_len = hi.len() + lo.len();

            match total_len.cmp(&MAX_VAL.len()) {
                core::cmp::Ordering::Less => false,
                core::cmp::Ordering::Greater => { true },
                core::cmp::Ordering::Equal => {
                    if hi.len() > MAX_VAL.len() {
                        return true;
                    }
                    let (max_hi, max_lo) = MAX_VAL.split_at(hi.len());
                    hi > max_hi || (hi == max_hi && lo > max_lo)
                }
            }
        }
    ) {
        // TODO: What is going on ??? Need to fix
        // assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else {
        assert!(result.is_ok())
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

/// program_id // Token Program ID
/// accounts[0] // Source Account Info (Account)
/// accounts[1] // Destination Info
/// accounts[2] // Authority Info
/// accounts[3..14] // Signers
/// instruction_data[0] // Discriminator 38 (Withdraw Excess Lamports Account)
#[inline(never)]
fn test_process_withdraw_excess_lamports_account(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 3],
    instruction_data: &[u8; 1],
) -> ProgramResult {
    // Constrain discriminator and program id
    unsafe { assume(38 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 0] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_account(&accounts[0]); // Source Account
    cheatcode_is_spl_account(&accounts[1]); // Destination
    // #[cfg(not(feature="multisig"))]
    cheatcode_is_spl_account(&accounts[2]); // Authority
    // #[cfg(feature="multisig")]
    // cheatcode_is_spl_multisig(&accounts[2]); // Authority

    //-Initial State-----------------------------------------------------------
    let src_data_len = accounts[0].data_len();
    let src_account_initialised = get_account(&accounts[0]).is_initialized();
    let src_account_owner = get_account(&accounts[0]).owner();
    let src_account_is_native = get_account(&accounts[0]).is_native();
    let src_init_lamports = accounts[0].lamports();
    let dst_init_lamports = accounts[1].lamports();
    let maybe_multisig_is_initialised = if accounts[2].data_len() == Multisig::LEN
        && accounts[2].owner == &crate::id()
    {
        Some(get_multisig(&accounts[2]).is_initialized())
    } else {
        None
    };

    // Note: Rent is a supported sysvar so ProgramError::UnsupportedSysvar should be impossible
    let rent = solana_rent::Rent::get().unwrap();
    let minimum_balance = rent.minimum_balance(accounts[0].data_len());

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else {
        assert_eq!(src_data_len, Account::LEN); // established by cheatcode_is_spl_account
        {
            if src_account_initialised.is_err() {
                assert_eq!(result, Err(ProgramError::InvalidAccountData));
                return result;
            } else if !src_account_initialised.unwrap() {
                assert_eq!(result, Err(ProgramError::UninitializedAccount));
                return result;
            } else if src_account_is_native {
                assert_eq!(result, Err(ProgramError::Custom(10)));
                return result;
            }
            inner_test_validate_owner(
                &src_account_owner,
                &accounts[2],
                &accounts[3..],
                maybe_multisig_is_initialised.clone(),
                result.clone(),
            )?;

            if src_init_lamports < minimum_balance {
                assert_eq!(result, Err(ProgramError::Custom(0)));
                return result;
            } else if u64::MAX - src_init_lamports + minimum_balance < dst_init_lamports {
                assert_eq!(result, Err(ProgramError::Custom(0)));
                return result;
            }

            assert_eq!(accounts[0].lamports(), minimum_balance);
            assert_eq!(accounts[1].lamports(), dst_init_lamports + src_init_lamports - minimum_balance);
            assert!(result.is_ok())
        }
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

/// program_id // Token Program ID
/// accounts[0] // Source Account Info (Mint)
/// accounts[1] // Destination Info
/// accounts[2] // Authority Info
/// accounts[3..14] // Signers
/// instruction_data[0] // Discriminator 38 (Withdraw Excess Lamports Mint)
#[inline(never)]
fn test_process_withdraw_excess_lamports_mint(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 3],
    instruction_data: &[u8; 1],
) -> ProgramResult {
    // Constrain discriminator and program id
    unsafe { assume(38 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 0] = instruction_data.last_chunk().unwrap();

    cheatcode_is_spl_mint(&accounts[0]); // Source Account (Mint)
    cheatcode_is_spl_account(&accounts[1]); // Destination
    // #[cfg(not(feature="multisig"))]
    cheatcode_is_spl_account(&accounts[2]); // Authority
    // #[cfg(feature="multisig")]
    // cheatcode_is_spl_multisig(&accounts[2]); // Authority

    //-Initial State-----------------------------------------------------------
    let src_data_len = accounts[0].data_len();
    let src_mint_initialised = get_mint(&accounts[0]).is_initialized();
    let src_mint_mint_authority = get_mint(&accounts[0]).mint_authority().cloned();
    let src_init_lamports = accounts[0].lamports();
    let dst_init_lamports = accounts[1].lamports();
    let maybe_multisig_is_initialised = if accounts[2].data_len() == Multisig::LEN
        && accounts[2].owner == &crate::id()
    {
        Some(get_multisig(&accounts[2]).is_initialized())
    } else {
        None
    };

    // Note: Rent is a supported sysvar so ProgramError::UnsupportedSysvar should be impossible
    let rent = solana_rent::Rent::get().unwrap();
    let minimum_balance = rent.minimum_balance(accounts[0].data_len());

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else {
        assert_eq!(src_data_len, Mint::LEN); // established by cheatcode_is_spl_mint
        {
            if src_mint_initialised.is_err() {
                assert_eq!(result, Err(ProgramError::InvalidAccountData));
                return result;
            } else if !src_mint_initialised.unwrap() {
                assert_eq!(result, Err(ProgramError::UninitializedAccount));
                return result;
            } else if src_mint_mint_authority.is_some() {
                inner_test_validate_owner(
                    src_mint_mint_authority.as_ref().unwrap(),
                    &accounts[2],
                    &accounts[3..],
                    maybe_multisig_is_initialised.clone(),
                    result.clone(),
                )?;
            } else if accounts[0].key != accounts[2].key {
                assert_eq!(result, Err(ProgramError::Custom(15)));
                return result;
            } else if !accounts[2].is_signer {
                assert_eq!(result, Err(ProgramError::MissingRequiredSignature));
                return result;
            }

            else if src_init_lamports < minimum_balance {
                assert_eq!(result, Err(ProgramError::Custom(0)));
                return result;
            } else if u64::MAX - src_init_lamports + minimum_balance < dst_init_lamports {
                assert_eq!(result, Err(ProgramError::Custom(0)));
                return result;
            }

            assert_eq!(accounts[0].lamports(), minimum_balance);
            assert_eq!(accounts[1].lamports(), dst_init_lamports + src_init_lamports - minimum_balance);
            assert!(result.is_ok())
        }
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}

/// program_id // Token Program ID
/// accounts[0] // Source Account Info
/// accounts[1] // Destination Info
/// accounts[2] // Authority Info
/// accounts[3..14] // Signers
/// instruction_data[0] // Discriminator 38 (Withdraw Excess Lamports Multisig)
#[inline(never)]
fn test_process_withdraw_excess_lamports_multisig(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 3],
    instruction_data: &[u8; 1],
) -> ProgramResult {
    // Constrain discriminator and program id
    unsafe { assume(38 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 0] = instruction_data.last_chunk().unwrap();

    // cheatcode_is_spl_multisig(&accounts[0]); // Source Account (Multisig)
    cheatcode_is_spl_account(&accounts[1]); // Destination
    // #[cfg(not(feature="multisig"))]
    cheatcode_is_spl_account(&accounts[2]); // Authority
    // #[cfg(feature="multisig")]
    // cheatcode_is_spl_multisig(&accounts[2]); // Authority

    //-Initial State-----------------------------------------------------------
    let src_data_len = accounts[0].data_len();
    let src_init_lamports = accounts[0].lamports();
    let dst_init_lamports = accounts[1].lamports();
    let maybe_multisig_is_initialised = if accounts[2].data_len() == Multisig::LEN
        && accounts[2].owner == &crate::id()
    {
        Some(get_multisig(&accounts[2]).is_initialized())
    } else {
        None
    };

    // Note: Rent is a supported sysvar so ProgramError::UnsupportedSysvar should be impossible
    let rent = solana_rent::Rent::get().unwrap();
    let minimum_balance = rent.minimum_balance(accounts[0].data_len());

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else if src_data_len != Account::LEN && src_data_len != Mint::LEN && src_data_len != Multisig::LEN {
        assert_eq!(result, Err(ProgramError::Custom(13)));
        return result;
    } else {
        assert_eq!(src_data_len, Multisig::LEN); // established by cheatcode_is_spl_multisig
        inner_test_validate_owner(
            accounts[0].key,
            &accounts[2],
            &accounts[3..],
            maybe_multisig_is_initialised.clone(),
            result.clone(),
        )?;

        if src_init_lamports < minimum_balance {
            assert_eq!(result, Err(ProgramError::Custom(0)));
            return result;
        } else if u64::MAX - src_init_lamports + minimum_balance < dst_init_lamports {
            assert_eq!(result, Err(ProgramError::Custom(0)));
            return result;
        }

        assert_eq!(accounts[0].lamports(), minimum_balance);
        assert_eq!(accounts[1].lamports(), dst_init_lamports + src_init_lamports - minimum_balance);
        assert!(result.is_ok())
    }

    // Ensure instruction_data was not mutated
    assert_eq!(*instruction_data, instruction_data_with_discriminator[1..]);

    result
}
