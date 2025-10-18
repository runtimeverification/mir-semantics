//! Program entrypoint for runtime verification proofs of original spl token implmentation

use {
    crate::{processor::Processor, state::{Account, AccountState, Mint, Multisig}},
    solana_account_info::AccountInfo,
    solana_program_error::{ProgramError, ProgramResult},
    solana_program_pack::Pack,
    solana_pubkey::Pubkey,
    spl_token_interface::error::TokenError,
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
}

fn get_mint(account_info: &AccountInfo) -> MintWrapper {
    MintWrapper(Mint::unpack(&account_info.data.borrow()))
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
    AccountWrapper(Account::unpack(&account_info.data.borrow()))
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
    MultisigWrapper(Multisig::unpack(&account_info.data.borrow()))
}

// TODO: Not sure if these are needed since there is no UB like p-token
// fn cheatcode_is_account(_: &AccountInfo) {}
// fn cheatcode_is_mint(_: &AccountInfo) {}
// fn cheatcode_is_multisig(_: &AccountInfo) {}

/// A runtime verification cheatcode to set the instruction discriminator.
/// TODO: Currently calling assert for concrete testing but needs backend support in K.
fn cheatcode_set_descriminator(discriminator: u8, instruction_data: &[u8]) {
    assert_eq!(discriminator, instruction_data[0]);
}

/// A runtime verification cheatcode to set the program ID.
/// TODO: Currently calling assert for concrete testing but needs backend support in K.
fn cheatcode_set_program_id(program_id: &Pubkey) {
    assert_eq!(program_id, &crate::id());
}

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
        // 3 - Transfer
        3 => {
            test_process_transfer(
                program_id,
                accounts, // CHANGE P-Token: accounts: &[AccountInfo; 3]
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 21 - Get Account Data Size
        21 => {
            test_process_get_account_data_size(
                program_id,
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                instruction_data.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // For all other instructions, just call the regular processor
        _ => {
            Processor::process(program_id, accounts, instruction_data)
        }
    }
}

/// accounts[0] // Source Info
/// accounts[1] // Destination Info
/// accounts[2] // Authority Info
/// accounts[3..14] // Signers
/// instruction_data[0..8] // Little Endian Bytes of u64 amount
#[inline(never)]
fn test_process_transfer(
    program_id: &Pubkey,
    accounts: &[AccountInfo], // CHANGE P-Token: accounts: &[AccountInfo; 3]
    instruction_data: &[u8; 9],
) -> ProgramResult {
    use spl_token_interface::state::AccountState;

    // Set descriminator and program id to concrete value
    cheatcode_set_descriminator(3, instruction_data);
    cheatcode_set_program_id(program_id);

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 8] = instruction_data.last_chunk().unwrap();

    // cheatcode_is_account(&accounts[0]);
    // cheatcode_is_account(&accounts[1]);
    // #[cfg(not(feature="multisig"))]
    // cheatcode_is_account(&accounts[2]);
    // #[cfg(feature="multisig")]
    // cheatcode_is_multisig(&accounts[2]);

    //-Initial State-----------------------------------------------------------
    let amount = u64::from_le_bytes(*instruction_data);
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let dst_initialised = get_account(&accounts[1]).is_initialized();
    let src_initial_amount = get_account(&accounts[0]).amount();
    let dst_initial_amount = get_account(&accounts[1]).amount();
    let src_initial_lamports = accounts[0].lamports();
    let dst_initial_lamports = accounts[1].lamports();
    let src_owner = get_account(&accounts[0]).owner();
    let old_src_delgate = get_account(&accounts[0]).delegate().cloned();
    let old_src_delgated_amount = get_account(&accounts[0]).delegated_amount();
    // #[cfg(feature="multisig")]
    let multisig_is_initialised = get_multisig(&accounts[2]).is_initialized();

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
        if old_src_delgate == Some(*accounts[2].key) {
            { // Validate Owner
                // Line 102-104 of validate_owner function in mod.rs
                // if accounts[2].key != accounts[2].key {... } // Now redundant

                // Line 106-108
                if accounts[2].data_len() == Multisig::LEN && accounts[2].owner == &crate::id() {
                    // #[cfg(feature="multisig")]
                    {
                        // Line 114
                        if multisig_is_initialised.is_err() {
                            assert_eq!(result, Err(ProgramError::InvalidAccountData));
                            return result;
                        } else if !multisig_is_initialised.unwrap() {
                            assert_eq!(result, Err(ProgramError::UninitializedAccount));
                            return result;
                        } else {
                            // Lines 116-117
                            let multisig = get_multisig(&accounts[2]);

                            // Lines 119-129: Did all declared and allowed signers sign?
                            let unsigned_exists = accounts[3..].iter()
                                .any(|potential_signer| {
                                    multisig.signers()
                                        .iter()
                                        .any(|registered_key| registered_key == potential_signer.key && !potential_signer.is_signer)
                                });

                            if unsigned_exists {
                                assert_eq!(result, Err(ProgramError::MissingRequiredSignature));
                                return result;
                            }

                            // Lines 130-132: Were enough signatures received?
                            let signers_count = multisig.signers().iter()
                                .filter_map(|registered_key| {
                                    accounts[3..].iter()
                                        .find(|potential_signer| potential_signer.key == registered_key && potential_signer.is_signer)
                                })
                                .count();

                            // Line 130-132: Check if we have enough signers (singers_count < multisig.m())
                            if signers_count < multisig.m() as usize {
                                assert_eq!(result, Err(ProgramError::MissingRequiredSignature));
                                return result;
                            }
                        }
                    }
                }
                // Line 133-135: Non-multisig case - check if owner_account_info.is_signer()
                else if !accounts[2].is_signer {
                    assert_eq!(result, Err(ProgramError::MissingRequiredSignature));
                    return result;
                }
            }

            if old_src_delgated_amount < amount {
                assert_eq!(result, Err(ProgramError::Custom(1)));
                return result;
            }
        } else {
            { // Validate Owner
                // Line 102-104 of validate_owner function in mod.rs
                if src_owner != *accounts[2].key {
                    assert_eq!(result, Err(ProgramError::Custom(4)));
                    return result;
                }
                // Line 106-108
                else if accounts[2].data_len() == Multisig::LEN && accounts[2].owner == &crate::id() {
                    // #[cfg(feature="multisig")]
                    {
                        // Line 114
                        if multisig_is_initialised.is_err() {
                            assert_eq!(result, Err(ProgramError::InvalidAccountData));
                            return result;
                        } else if !multisig_is_initialised.unwrap() {
                            assert_eq!(result, Err(ProgramError::UninitializedAccount));
                            return result;
                        } else {
                            // Lines 116-117
                            let multisig = get_multisig(&accounts[2]);

                            // Lines 119-129: Did all declared and allowed signers sign?
                            let unsigned_exists = accounts[3..].iter()
                                .any(|potential_signer| {
                                    multisig.signers()
                                        .iter()
                                        .any(|registered_key| registered_key == potential_signer.key && !potential_signer.is_signer)
                                });

                            if unsigned_exists {
                                assert_eq!(result, Err(ProgramError::MissingRequiredSignature));
                                return result;
                            }

                            // Lines 130-132: Were enough signatures received?
                            let signers_count = multisig.signers().iter()
                                .filter_map(|registered_key| {
                                    accounts[3..].iter()
                                        .find(|potential_signer| potential_signer.key == registered_key && potential_signer.is_signer)
                                })
                                .count();

                            // Line 130-132: Check if we have enough signers (singers_count < multisig.m())
                            if signers_count < multisig.m() as usize {
                                assert_eq!(result, Err(ProgramError::MissingRequiredSignature));
                                return result;
                            }
                        }
                    }
                }
                // Line 133-135: Non-multisig case - check if owner_account_info.is_signer()
                else if !accounts[2].is_signer {
                    assert_eq!(result, Err(ProgramError::MissingRequiredSignature));
                    return result;
                }
            }
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

/// accounts[0] // Mint Info
#[inline(never)]
fn test_process_get_account_data_size(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 1],
    instruction_data: &[u8; 1],
) -> ProgramResult {
    // Set descriminator and program id to concrete value
    cheatcode_set_descriminator(21, instruction_data);
    cheatcode_set_program_id(program_id);

    // Strip discriminator so instruction data is equivalent p-token harness
    let instruction_data_with_discriminator = &instruction_data.clone();
    let instruction_data: &[u8; 0] = instruction_data.last_chunk().unwrap();

    // cheatcode_is_mint(&accounts[0]);

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
