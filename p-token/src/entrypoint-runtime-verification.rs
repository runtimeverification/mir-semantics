// The harnesses have blocks with the same error conidition
// beside each other which clippy doesn't like, but that is
// but that is preferable for clarity currently.
#![allow(clippy::if_same_then_else)]
// Code that is guarded from arithmetic overflow in both the
//  harness logic and by K protecting from UB is flagged
// by clippy
#![allow(clippy::arithmetic_side_effects)]
// Also note that there are some other inlined clippy bypasses
// in the harnesses that should be acknowledged

use {
    crate::processor::*,
    pinocchio::{
        account_info::AccountInfo,
        no_allocator, nostd_panic_handler, program_entrypoint,
        program_error::{ProgramError, ToStr},
        pubkey::Pubkey,
        sysvars::Sysvar,
        ProgramResult,
    },
    pinocchio_token_interface::{
        error::TokenError,
        state::{Initializable, Transmutable},
    },
};

program_entrypoint!(process_instruction);
// Do not allocate memory.
no_allocator!();
// Use the no_std panic handler.
nostd_panic_handler!();

/// Log an error.
#[cold]
fn log_error(error: &ProgramError) {
    pinocchio::log::sol_log(error.to_str::<TokenError>());
}

/// Process an instruction.
///
/// In the first stage, the entrypoint checks the discriminator of the
/// instruction data to determine whether the instruction is a "batch"
/// instruction or a "regular" instruction. This avoids nesting of "batch"
/// instructions, since it is not sound to have a "batch" instruction inside
/// another "batch" instruction.
#[inline(always)]
pub fn process_instruction(
    _program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    let [discriminator, remaining @ ..] = instruction_data else {
        return Err(TokenError::InvalidInstruction.into());
    };

    let result = if *discriminator == 255 {
        // 255 - Batch
        #[cfg(feature = "logging")]
        pinocchio::msg!("Instruction: Batch");

        process_batch(accounts, remaining)
    } else {
        inner_process_instruction(accounts, instruction_data)
    };

    result.inspect_err(log_error)
}

/// Process a "regular" instruction.
///
/// The processor of the token program is divided into two parts to reduce the
/// overhead of having a large `match` statement. The first part of the
/// processor handles the most common instructions, while the second part
/// handles the remaining instructions.
///
/// The rationale is to reduce the overhead of making multiple comparisons for
/// popular instructions.
///
/// Instructions on the first part of the inner processor:
///
/// - `0`: `InitializeMint`
/// - `1`: `InitializeAccount`
/// - `3`: `Transfer`
/// - `7`: `MintTo`
/// - `9`: `CloseAccount`
/// - `16`: `InitializeAccount2`
/// - `18`: `InitializeAccount3`
/// - `20`: `InitializeMint2`
#[inline(always)]
pub(crate) fn inner_process_instruction(
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    use pinocchio_token_interface::program::ID;

    let [discriminator, instruction_data @ ..] = instruction_data else {
        return Err(TokenError::InvalidInstruction.into());
    };

    match *discriminator {
        // 0 - Test InitializeMint
        0 => {
            #[cfg(feature = "logging")]
            pinocchio::msg!("Testing Instruction: InitializeMint");

            match instruction_data.len() {
                x if 66 <= x => test_process_initialize_mint_freeze(
                    accounts.first_chunk().unwrap(),
                    instruction_data.first_chunk().unwrap(),
                ),
                x if 34 <= x => test_process_initialize_mint_no_freeze(
                    accounts.first_chunk().unwrap(),
                    instruction_data.first_chunk().unwrap(),
                ),
                _ => panic!("Invalid instruction data length"),
            }
        }
        // 1 - Test InitializeAccount
        1 => {
            #[cfg(feature = "logging")]
            pinocchio::msg!("Testing Instruction: InitializeAccount");

            test_process_initialize_account(accounts.first_chunk().unwrap())
        }
        // 3 - Test Transfer
        3 => {
            #[cfg(feature = "logging")]
            pinocchio::msg!("Testing Instruction: Transfer");

            // TODO: Thoroughly test for insufficient account length
            // We should be calling `insufficient_accounts_length_transfer(x)?` in the
            // future
            match accounts.len() {
                x if accounts.len() < 3 => panic!("Invalid amount of accounts for transfer: {x}"),
                _ => (),
            }

            match accounts[2].data_len() {
                Multisig::LEN if accounts[2].is_owned_by(&ID) => test_process_transfer_multisig(
                    accounts.first_chunk().unwrap(),
                    instruction_data.first_chunk().unwrap(),
                ),
                _ => test_process_transfer(
                    accounts.first_chunk().unwrap(),
                    instruction_data.first_chunk().unwrap(),
                ),
            }
        }
        // 7 - MintTo
        7 => {
            #[cfg(feature = "logging")]
            pinocchio::msg!("Instruction: MintTo");

            // TODO: Thoroughly test for insufficient account length
            // We should be calling `insufficient_accounts_length_mint(x)?` in the future
            match accounts.len() {
                x if accounts.len() < 3 => panic!("Invalid amount of accounts for mint: {x}"),
                _ => (),
            }

            match accounts[2].data_len() {
                Multisig::LEN if accounts[2].is_owned_by(&ID) => test_process_mint_to_multisig(
                    accounts.first_chunk().unwrap(),
                    instruction_data.first_chunk().unwrap(),
                ),
                _ => test_process_mint_to(
                    accounts.first_chunk().unwrap(),
                    instruction_data.first_chunk().unwrap(),
                ),
            }
        }
        // 8 - Test Burn
        8 => {
            #[cfg(feature = "logging")]
            pinocchio::msg!("Testing Instruction: Burn");

            // TODO: Thoroughly test for insufficient account length
            // We should be calling `insufficient_accounts_length_burn(x)?` in the future
            match accounts.len() {
                x if accounts.len() < 3 => panic!("Invalid amount of accounts for burn: {x}"),
                _ => (),
            }

            match accounts[2].data_len() {
                Multisig::LEN if accounts[2].is_owned_by(&ID) => test_process_burn_multisig(
                    accounts.first_chunk().unwrap(),
                    instruction_data.first_chunk().unwrap(),
                ),
                _ => test_process_burn(
                    accounts.first_chunk().unwrap(),
                    instruction_data.first_chunk().unwrap(),
                ),
            }
        }
        // 9 - Test CloseAccount
        9 => {
            #[cfg(feature = "logging")]
            pinocchio::msg!("Testing Instruction: CloseAccount");

            // TODO: Thoroughly test for insufficient account length
            // We should be calling `insufficient_accounts_length_close_account(x)?` in the
            // future
            match accounts.len() {
                x if accounts.len() < 3 => {
                    panic!("Invalid amount of accounts for close_account: {x}")
                }
                _ => (),
            }

            match accounts[2].data_len() {
                Multisig::LEN if accounts[2].is_owned_by(&ID) => {
                    test_process_close_account_multisig(accounts.first_chunk().unwrap())
                }
                _ => test_process_close_account(accounts.first_chunk().unwrap()),
            }
        }
        // 12 - Test TransferChecked
        12 => {
            #[cfg(feature = "logging")]
            pinocchio::msg!("Testing Instruction: TransferChecked");

            // TODO: Thoroughly test for insufficient account length
            // We should be calling `insufficient_accounts_length_transfer_checked(x)?` in
            // the future
            match accounts.len() {
                x if accounts.len() < 4 => {
                    panic!("Invalid amount of accounts for transfer_checked: {x}")
                }
                _ => (),
            }

            match accounts[3].data_len() {
                Multisig::LEN if accounts[2].is_owned_by(&ID) => {
                    test_process_transfer_checked_multisig(
                        accounts.first_chunk().unwrap(),
                        instruction_data.first_chunk().unwrap(),
                    )
                }
                _ => test_process_transfer_checked(
                    accounts.first_chunk().unwrap(),
                    instruction_data.first_chunk().unwrap(),
                ),
            }
        }
        // 15 - Test BurnChecked
        15 => {
            #[cfg(feature = "logging")]
            pinocchio::msg!("Testing Instruction: BurnChecked");

            // TODO: Thoroughly test for insufficient account length
            // We should be calling `insufficient_accounts_length_burn_checked(x)?` in the
            // future
            match accounts.len() {
                x if accounts.len() < 3 => {
                    panic!("Invalid amount of accounts for burn_checked: {x}")
                }
                _ => (),
            }

            match accounts[2].data_len() {
                Multisig::LEN if accounts[2].is_owned_by(&ID) => {
                    test_process_burn_checked_multisig(
                        accounts.first_chunk().unwrap(),
                        instruction_data.first_chunk().unwrap(),
                    )
                }
                _ => test_process_burn_checked(
                    accounts.first_chunk().unwrap(),
                    instruction_data.first_chunk().unwrap(),
                ),
            }
        }
        // 16 - Test InitializeAccount2
        16 => {
            #[cfg(feature = "logging")]
            pinocchio::msg!("Testing Instruction: InitializeAccount2");

            test_process_initialize_account2(
                accounts.first_chunk().unwrap(),
                instruction_data.first_chunk().unwrap(),
            )
        }
        // 18 - Test InitializeAccount3
        18 => {
            #[cfg(feature = "logging")]
            pinocchio::msg!("Testing Instruction: InitializeAccount3");

            test_process_initialize_account3(
                accounts.first_chunk().unwrap(),
                instruction_data.first_chunk().unwrap(),
            )
        }
        // 20 - Test InitializeMint2
        20 => {
            #[cfg(feature = "logging")]
            pinocchio::msg!("Testing Instruction: InitializeMint2");

            match instruction_data.len() {
                x if 66 <= x => test_process_initialize_mint2_freeze(
                    accounts.first_chunk().unwrap(),
                    instruction_data.first_chunk().unwrap(),
                ),
                x if 34 <= x => test_process_initialize_mint2_no_freeze(
                    accounts.first_chunk().unwrap(),
                    instruction_data.first_chunk().unwrap(),
                ),
                _ => panic!("Invalid instruction data length"),
            }
        }
        d => inner_process_remaining_instruction(accounts, instruction_data, d),
    }
}

/// Process a remaining "regular" instruction.
///
/// This function is called by the [`inner_process_instruction`] function if the
/// discriminator does not match any of the common instructions. This function
/// is used to reduce the overhead of having a large `match` statement in the
/// [`inner_process_instruction`] function.
fn inner_process_remaining_instruction(
    accounts: &[AccountInfo],
    instruction_data: &[u8],
    discriminator: u8,
) -> ProgramResult {
    use pinocchio_token_interface::program::ID;

    match discriminator {
        // 2 - InitializeMultisig
        2 => {
            #[cfg(feature = "logging")]
            pinocchio::msg!("Instruction: InitializeMultisig");

            test_process_initialize_multisig(
                accounts.first_chunk().unwrap(),
                instruction_data.first_chunk().unwrap(),
            )
        }
        // 4 - Approve
        4 => {
            #[cfg(feature = "logging")]
            pinocchio::msg!("Instruction: Approve");

            // TODO: Thoroughly test for insufficient account length
            // We should be calling `insufficient_accounts_length_approve(x)?` in the future
            match accounts.len() {
                x if accounts.len() < 3 => panic!("Invalid amount of accounts for approve: {x}"),
                _ => (),
            }

            match accounts[2].data_len() {
                Multisig::LEN if accounts[2].is_owned_by(&ID) => test_process_approve_multisig(
                    accounts.first_chunk().unwrap(),
                    instruction_data.first_chunk().unwrap(),
                ),
                _ => test_process_approve(
                    accounts.first_chunk().unwrap(),
                    instruction_data.first_chunk().unwrap(),
                ),
            }
        }
        // 5 - Revoke
        5 => {
            #[cfg(feature = "logging")]
            pinocchio::msg!("Instruction: Revoke");

            // TODO: Thoroughly test for insufficient account length
            // We should be calling `insufficient_accounts_length_revoke(x)?` in the future
            match accounts.len() {
                x if accounts.len() < 2 => panic!("Invalid amount of accounts for revoke: {x}"),
                _ => (),
            }

            match accounts[1].data_len() {
                Multisig::LEN if accounts[1].is_owned_by(&ID) => {
                    test_process_revoke_multisig(accounts.first_chunk().unwrap())
                }
                _ => test_process_revoke(accounts.first_chunk().unwrap()),
            }
        }
        // 6 - SetAuthority
        6 => {
            #[cfg(feature = "logging")]
            pinocchio::msg!("Instruction: SetAuthority");

            // TODO: Thoroughly test for insufficient account length
            // We should be calling `insufficient_accounts_length_revoke(x)?` in the future
            match accounts.len() {
                x if accounts.len() < 2 => {
                    panic!("Invalid amount of accounts for set_authority: {x}")
                }
                _ => (),
            }

            // Determine if this is an Account or Mint based on data length
            if let Some(first_account) = accounts.first() {
                match first_account.data_len() {
                    Account::LEN => match accounts[1].data_len() {
                        Multisig::LEN if accounts[1].is_owned_by(&ID) => {
                            test_process_set_authority_account_multisig(
                                accounts.first_chunk().unwrap(),
                                instruction_data.first_chunk().unwrap(),
                            )
                        }
                        _ => test_process_set_authority_account(
                            accounts.first_chunk().unwrap(),
                            instruction_data.first_chunk().unwrap(),
                        ),
                    },
                    Mint::LEN => match accounts[1].data_len() {
                        Multisig::LEN if accounts[1].is_owned_by(&ID) => {
                            test_process_set_authority_mint_multisig(
                                accounts.first_chunk().unwrap(),
                                instruction_data.first_chunk().unwrap(),
                            )
                        }
                        _ => test_process_set_authority_mint(
                            accounts.first_chunk().unwrap(),
                            instruction_data.first_chunk().unwrap(),
                        ),
                    },
                    // FIXME: Create proof harness for this
                    _ => panic!("SetAuthority: Unexpected account data length"),
                }
            } else {
                // FIXME: Create proof harness for this
                Err(ProgramError::NotEnoughAccountKeys)
            }
        }
        // 10 - FreezeAccount
        10 => {
            #[cfg(feature = "logging")]
            pinocchio::msg!("Instruction: FreezeAccount");

            // TODO: Thoroughly test for insufficient account length
            // We should be calling `insufficient_accounts_length_freeze_account(x)?` in the
            // future
            match accounts.len() {
                x if accounts.len() < 3 => {
                    panic!("Invalid amount of accounts for freeze_account: {x}")
                }
                _ => (),
            }

            match accounts[2].data_len() {
                Multisig::LEN if accounts[2].is_owned_by(&ID) => {
                    test_process_freeze_account_multisig(accounts.first_chunk().unwrap())
                }
                _ => test_process_freeze_account(accounts.first_chunk().unwrap()),
            }
        }
        // 11 - ThawAccount
        11 => {
            #[cfg(feature = "logging")]
            pinocchio::msg!("Instruction: ThawAccount");

            // TODO: Thoroughly test for insufficient account length
            // We should be calling `insufficient_accounts_length_thaw_account(x)?` in the
            // future
            match accounts.len() {
                x if accounts.len() < 3 => {
                    panic!("Invalid amount of accounts for thaw_account: {x}")
                }
                _ => (),
            }

            match accounts[2].data_len() {
                Multisig::LEN if accounts[2].is_owned_by(&ID) => {
                    test_process_thaw_account_multisig(accounts.first_chunk().unwrap())
                }
                _ => test_process_thaw_account(accounts.first_chunk().unwrap()),
            }
        }
        // 13 - ApproveChecked
        13 => {
            #[cfg(feature = "logging")]
            pinocchio::msg!("Instruction: ApproveChecked");

            // TODO: Thoroughly test for insufficient account length
            // We should be calling `insufficient_accounts_length_approve_checked(x)?` in
            // the future
            match accounts.len() {
                x if accounts.len() < 4 => {
                    panic!("Invalid amount of accounts for approve_checked: {x}")
                }
                _ => (),
            }

            match accounts[3].data_len() {
                Multisig::LEN if accounts[3].is_owned_by(&ID) => {
                    test_process_approve_checked_multisig(
                        accounts.first_chunk().unwrap(),
                        instruction_data.first_chunk().unwrap(),
                    )
                }
                _ => test_process_approve_checked(
                    accounts.first_chunk().unwrap(),
                    instruction_data.first_chunk().unwrap(),
                ),
            }
        }
        // 14 - MintToChecked
        14 => {
            #[cfg(feature = "logging")]
            pinocchio::msg!("Instruction: MintToChecked");

            // TODO: Thoroughly test for insufficient account length
            // We should be calling `insufficient_accounts_length_mint_to_checked(x)?` in
            // the future
            match accounts.len() {
                x if accounts.len() < 3 => {
                    panic!("Invalid amount of accounts for mint_to_checked: {x}")
                }
                _ => (),
            }

            match accounts[2].data_len() {
                Multisig::LEN if accounts[2].is_owned_by(&ID) => {
                    test_process_mint_to_checked_multisig(
                        accounts.first_chunk().unwrap(),
                        instruction_data.first_chunk().unwrap(),
                    )
                }
                _ => test_process_mint_to_checked(
                    accounts.first_chunk().unwrap(),
                    instruction_data.first_chunk().unwrap(),
                ),
            }
        }
        // 17 - SyncNative
        17 => {
            #[cfg(feature = "logging")]
            pinocchio::msg!("Instruction: SyncNative");

            test_process_sync_native(accounts.first_chunk().unwrap())
        }
        // 19 - InitializeMultisig2
        19 => {
            #[cfg(feature = "logging")]
            pinocchio::msg!("Instruction: InitializeMultisig2");

            test_process_initialize_multisig2(
                accounts.first_chunk().unwrap(),
                instruction_data.first_chunk().unwrap(),
            )
        }
        // 21 - GetAccountDataSize
        21 => {
            #[cfg(feature = "logging")]
            pinocchio::msg!("Instruction: GetAccountDataSize");

            test_process_get_account_data_size(accounts.first_chunk().unwrap())
        }
        // 22 - InitializeImmutableOwner
        22 => {
            #[cfg(feature = "logging")]
            pinocchio::msg!("Instruction: InitializeImmutableOwner");

            test_process_initialize_immutable_owner(accounts.first_chunk().unwrap())
        }
        // 23 - AmountToUiAmount
        23 => {
            #[cfg(feature = "logging")]
            pinocchio::msg!("Instruction: AmountToUiAmount");

            test_process_amount_to_ui_amount(
                accounts.first_chunk().unwrap(),
                instruction_data.first_chunk().unwrap(),
            )
        }
        // 24 - UiAmountToAmount
        24 => {
            #[cfg(feature = "logging")]
            pinocchio::msg!("Instruction: UiAmountToAmount");

            test_process_ui_amount_to_amount(
                accounts.first_chunk().unwrap(),
                // instruction_data.first_chunk().unwrap(),
                instruction_data, // Sized won't work
            )
        }
        // 38 - WithdrawExcessLamports
        38 => {
            #[cfg(feature = "logging")]
            pinocchio::msg!("Instruction: WithdrawExcessLamports");

            // TODO: Thoroughly test for insufficient account length
            // We should be calling `insufficient_accounts_length_mint_to_checked(x)?` in
            // the future
            match accounts.len() {
                x if accounts.len() < 3 => {
                    panic!("Invalid amount of accounts for withdraw_excess_lamports: {x}")
                }
                _ => (),
            }

            if let Some(acc) = accounts.first() {
                match acc.data_len() {
                    Account::LEN => match accounts[2].data_len() {
                        Multisig::LEN if accounts[2].is_owned_by(&ID) => {
                            test_process_withdraw_excess_lamports_account_multisig(
                                accounts.first_chunk().unwrap(),
                            )
                        }
                        _ => test_process_withdraw_excess_lamports_account(
                            accounts.first_chunk().unwrap(),
                        ),
                    },
                    Mint::LEN => match accounts[2].data_len() {
                        Multisig::LEN if accounts[2].is_owned_by(&ID) => {
                            test_process_withdraw_excess_lamports_mint_multisig(
                                accounts.first_chunk().unwrap(),
                            )
                        }
                        _ => test_process_withdraw_excess_lamports_mint(
                            accounts.first_chunk().unwrap(),
                        ),
                    },
                    Multisig::LEN => match accounts[2].data_len() {
                        Multisig::LEN if accounts[2].is_owned_by(&ID) => {
                            test_process_withdraw_excess_lamports_multisig_multisig(
                                accounts.first_chunk().unwrap(),
                            )
                        }
                        _ => test_process_withdraw_excess_lamports_multisig(
                            accounts.first_chunk().unwrap(),
                        ),
                    },
                    // FIXME: Need harness for this
                    _other => panic!("withdraw_excess_lamports: Unexpected account data_len"),
                }
            } else {
                // FIXME: need to add harness isntead since instruction still accepts this case
                // and has an error code
                panic!("withdraw_excess_lamports: no accounts provided")
            }
        }
        _ => Err(TokenError::InvalidInstruction.into()),
    }
}

// Cheatcodes to inject AccountInfo assumptions
#[inline(never)]
fn cheatcode_is_account(_: &AccountInfo) {}
#[inline(never)]
fn cheatcode_is_mint(_: &AccountInfo) {}
#[inline(never)]
fn cheatcode_is_multisig(_: &AccountInfo) {} // TODO: implement multisig cheatcode
#[inline(never)]
fn cheatcode_is_rent(_: &AccountInfo) {}

use {
    pinocchio::sysvars::rent::Rent,
    pinocchio_token_interface::state::{
        account::Account, load_mut_unchecked, load_unchecked, mint::Mint, multisig::Multisig,
    },
};

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

fn get_multisig(account_info: &AccountInfo) -> &Multisig {
    unsafe {
        let byte_ptr = account_info.borrow_data_unchecked();
        let multisig_ref = load_unchecked::<Multisig>(byte_ptr).unwrap();
        multisig_ref
    }
}

fn get_rent(account_info: &AccountInfo) -> &Rent {
    unsafe { Rent::from_bytes_unchecked(account_info.borrow_data_unchecked()) }
}

/// This function encapsulates the specification of validating the signature
/// requirements In particular, code from mod.rs::validate_owner is checked
#[inline(never)]
fn inner_test_validate_owner(
    expected_owner: &Pubkey,
    owner_account_info: &AccountInfo,
    tx_signers: &[AccountInfo],
    maybe_multisig_is_initialised: Option<Result<bool, ProgramError>>,
    result: Result<(), ProgramError>,
) -> Result<(), ProgramError> {
    use pinocchio_token_interface::program::ID;

    // Validate Owner
    // Line 102-104 of validate_owner function in mod.rs
    if expected_owner != owner_account_info.key() {
        assert_eq!(result, Err(ProgramError::Custom(4)));
        result
    }
    // Line 106-108
    // We add the `maybe_multisig_is_initialised.is_some()` to not branch vacuously in the
    // non-multisig cases
    else if maybe_multisig_is_initialised.is_some()
        && owner_account_info.data_len() == Multisig::LEN
        && owner_account_info.is_owned_by(&ID)
    {
        // Guaranteed to succeed by `cheatcode_is_multisig`
        let multisig_is_initialised = maybe_multisig_is_initialised.unwrap();

        // Line 114
        if multisig_is_initialised.is_err() {
            assert_eq!(result, Err(ProgramError::InvalidAccountData));
            return result;
        } else if !multisig_is_initialised.unwrap() {
            assert_eq!(result, Err(ProgramError::UninitializedAccount));
            return result;
        } else {
            // Lines 116-117
            let multisig = get_multisig(owner_account_info);

            // Lines 119-129: Did all declared and allowed signers sign?
            let unsigned_exists = tx_signers.iter().any(|potential_signer| {
                multisig.signers.iter().any(|registered_key| {
                    registered_key == potential_signer.key() && !potential_signer.is_signer()
                })
            });

            if unsigned_exists {
                assert_eq!(result, Err(ProgramError::MissingRequiredSignature));
                return result;
            }

            // Lines 130-132: Were enough signatures received?
            let signers_count = multisig
                .signers
                .iter()
                .filter_map(|registered_key| {
                    tx_signers.iter().find(|potential_signer| {
                        potential_signer.key() == registered_key && potential_signer.is_signer()
                    })
                })
                .count();

            // Line 130-132: Check if we have enough signers (singers_count < multisig.m)
            if signers_count < multisig.m as usize {
                assert_eq!(result, Err(ProgramError::MissingRequiredSignature));
                return result;
            } else {
                return result;
            }
        }
    }
    // Line 133-135: Non-multisig case - check if owner_account_info.is_signer()
    else if !owner_account_info.is_signer() {
        assert_eq!(result, Err(ProgramError::MissingRequiredSignature));
        return result;
    } else {
        return result;
    }
}

// wrapper to ensure the test below is in the SMIR JSON
#[no_mangle]
pub unsafe extern "C" fn use_tests(acc: &AccountInfo) {
    test_ptoken_domain_data(acc, acc, acc);
}

// special test for basic domain data access
#[inline(never)]
fn test_ptoken_domain_data(acc: &AccountInfo, mint: &AccountInfo, rent: &AccountInfo) {
    cheatcode_is_mint(mint);
    unsafe {
        let test = mint.borrow_mut_data_unchecked();
        let imint = load_mut_unchecked::<Mint>(test);
        let imint = imint.unwrap();
        imint.set_initialized();
    }
    let imint = get_mint(mint);
    assert!(imint.is_initialized().unwrap());

    cheatcode_is_account(acc);
    unsafe {
        let test = acc.borrow_mut_data_unchecked();
        let iacc: Result<&mut Account, _> = load_mut_unchecked(test);
        let iacc = iacc.unwrap();
        iacc.set_native(true);
    }
    let iacc = get_account(acc);
    assert!(iacc.is_native());

    let owner = acc.owner();
    assert!(acc.is_owned_by(owner));
    // QUESTION: is pinocchio::Account ever written to through AccountInfo?

    // test the system's Rent sysvar
    let sysrent = Rent::get().unwrap();
    let rent_collected = 10;
    let (burnt, distributed) = sysrent.calculate_burn(rent_collected);
    assert!(sysrent.burn_percent > 100 || burnt <= rent_collected && distributed <= rent_collected);

    cheatcode_is_rent(rent);
    let prent = unsafe {
        let test = rent.borrow_data_unchecked();
        Rent::from_bytes_unchecked(test)
    };
    // cannot call any functions that use f64 in any way
    // assume burn_percent value <=100 and calculate with it
    let rent_collected = 10;
    let (burnt, distributed) = prent.calculate_burn(rent_collected);
    assert!(prent.burn_percent > 100 || burnt <= rent_collected && distributed <= rent_collected);
}

// Hack Tests For Stable MIR JSON ---------------------------------------------
/// accounts[0] // Mint Info
/// accounts[1] // Rent Sysvar Info
/// instruction_data[0]      // Decimals
/// instruction_data[1..33]  // Mint Authority Pubkey
/// instruction_data[33]     // Freeze Authority Exists? 1 for freeze
/// instruction_data[34..66] // instruction_data[33] == 1 ==> Freeze Authority
/// Pubkey
#[inline(never)]
pub fn test_process_initialize_mint_freeze(
    accounts: &[AccountInfo; 2],
    instruction_data: &[u8; 66],
) -> ProgramResult {
    cheatcode_is_mint(&accounts[0]);
    cheatcode_is_rent(&accounts[1]);

    //-Initial State-----------------------------------------------------------
    let minimum_balance = get_rent(&accounts[1]).minimum_balance(accounts[0].data_len()); // TODO float problem
    let mint_is_initialised_prior = get_mint(&accounts[0]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = process_initialize_mint(accounts, instruction_data);

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
    } else if mint_is_initialised_prior.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if mint_is_initialised_prior.unwrap() {
        assert_eq!(result, Err(ProgramError::Custom(6)))
    } else if accounts[0].lamports() < minimum_balance {
        assert_eq!(result, Err(ProgramError::Custom(0)))
    } else {
        assert!(get_mint(&accounts[0]).is_initialized().unwrap());
        assert_eq!(
            get_mint(&accounts[0]).mint_authority().unwrap(),
            &instruction_data[1..33]
        );
        assert_eq!(get_mint(&accounts[0]).decimals, instruction_data[0]);

        if instruction_data[33] == 1 {
            assert_eq!(
                get_mint(&accounts[0]).freeze_authority().unwrap(),
                &instruction_data[34..66]
            );
        }
    }

    result
}

/// accounts[0] // Mint Info
/// accounts[1] // Rent Sysvar Info
/// instruction_data[0]      // Decimals
/// instruction_data[1..33]  // Mint Authority Pubkey
/// instruction_data[33]     // Freeze Authority Exists? 0 for no freeze
#[inline(never)]
pub fn test_process_initialize_mint_no_freeze(
    accounts: &[AccountInfo; 2],
    instruction_data: &[u8; 34],
) -> ProgramResult {
    cheatcode_is_mint(&accounts[0]);
    cheatcode_is_rent(&accounts[1]);

    //-Initial State-----------------------------------------------------------
    let minimum_balance = get_rent(&accounts[1]).minimum_balance(accounts[0].data_len()); // TODO float problem
    let mint_is_initialised_prior = get_mint(&accounts[0]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = process_initialize_mint(accounts, instruction_data);

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
    } else if mint_is_initialised_prior.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if mint_is_initialised_prior.unwrap() {
        assert_eq!(result, Err(ProgramError::Custom(6)))
    } else if accounts[0].lamports() < minimum_balance {
        assert_eq!(result, Err(ProgramError::Custom(0)))
    } else {
        assert!(get_mint(&accounts[0]).is_initialized().unwrap());
        assert_eq!(
            get_mint(&accounts[0]).mint_authority().unwrap(),
            &instruction_data[1..33]
        );
        assert_eq!(get_mint(&accounts[0]).decimals, instruction_data[0]);

        #[allow(clippy::out_of_bounds_indexing)]
        // Guard above prevents this branch TODO: Perhaps remove?
        if instruction_data[33] == 1 {
            assert_eq!(
                get_mint(&accounts[0]).freeze_authority().unwrap(),
                &instruction_data[34..66]
            );
        }
    }

    result
}

/// accounts[0] // New Account Info
/// accounts[1] // Mint Info
/// accounts[2] // Owner Info
/// accounts[3] // Rent Sysvar Info
#[inline(never)]
pub fn test_process_initialize_account(accounts: &[AccountInfo; 4]) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_account(&accounts[0]);
    cheatcode_is_mint(&accounts[1]);
    cheatcode_is_account(&accounts[2]);
    cheatcode_is_rent(&accounts[3]);

    //-Initial State-----------------------------------------------------------
    let initial_state_new_account = get_account(&accounts[0]).account_state();

    let minimum_balance = get_rent(&accounts[3]).minimum_balance(accounts[0].data_len()); // TODO float problem
    let is_native_mint = accounts[1].key() == &pinocchio_token_interface::native_mint::ID;
    let mint_is_initialised = get_mint(&accounts[1]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = process_initialize_account(accounts);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() < 4 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
    } else if accounts[3].key() != &pinocchio::sysvars::rent::RENT_ID {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if accounts[0].data_len() != Account::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if initial_state_new_account.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if initial_state_new_account.unwrap() != account_state::AccountState::Uninitialized {
        assert_eq!(result, Err(ProgramError::Custom(6)))
    } else if accounts[0].lamports() < minimum_balance {
        assert_eq!(result, Err(ProgramError::Custom(0)))
    } else if !is_native_mint && accounts[1].owner() != &pinocchio_token_interface::program::ID {
        assert_eq!(result, Err(ProgramError::IncorrectProgramId))
    } else if !is_native_mint
        && accounts[1].owner() == &pinocchio_token_interface::program::ID
        && mint_is_initialised.is_err()
    {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !is_native_mint
        && accounts[1].owner() == &pinocchio_token_interface::program::ID
        && !mint_is_initialised.unwrap()
    {
        assert_eq!(result, Err(ProgramError::Custom(2)))
    } else {
        assert!(result.is_ok());
        assert_eq!(
            get_account(&accounts[0]).account_state().unwrap(),
            account_state::AccountState::Initialized
        );
        assert_eq!(get_account(&accounts[0]).mint, *accounts[1].key());
        assert_eq!(get_account(&accounts[0]).owner, *accounts[2].key());

        if is_native_mint {
            assert!(get_account(&accounts[0]).is_native());
            assert_eq!(
                get_account(&accounts[0]).native_amount().unwrap(),
                minimum_balance
            );
            assert_eq!(
                get_account(&accounts[0]).amount(),
                accounts[0].lamports() - minimum_balance
            );
        }
    }

    result
}

/// accounts[0] // Source Info
/// accounts[1] // Destination Info
/// accounts[2] // Authority Info
/// instruction_data[0..8] // Little Endian Bytes of u64 amount
#[inline(never)]
pub fn test_process_transfer(
    accounts: &[AccountInfo; 3],
    instruction_data: &[u8; 8],
) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_account(&accounts[0]);
    cheatcode_is_account(&accounts[1]);

    //-Initial State-----------------------------------------------------------
    let amount = unsafe { u64::from_le_bytes(*(instruction_data.as_ptr() as *const [u8; 8])) };
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let dst_initialised = get_account(&accounts[1]).is_initialized();
    let src_initial_amount = get_account(&accounts[0]).amount();
    let dst_initial_amount = get_account(&accounts[1]).amount();
    let src_initial_lamports = accounts[0].lamports();
    let dst_initial_lamports = accounts[1].lamports();
    let src_owner = get_account(&accounts[0]).owner;
    let old_src_delgate = get_account(&accounts[0]).delegate().cloned();
    let old_src_delgated_amount = get_account(&accounts[0]).delegated_amount();
    let maybe_multisig_is_initialised = None; // Value set to `None` since authority is an account

    //-Process Instruction-----------------------------------------------------
    let result = process_transfer(accounts, instruction_data);

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
    } else if accounts[0] != accounts[1] && dst_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if accounts[0] != accounts[1] && !dst_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount));
        return result;
    } else if get_account(&accounts[0]).account_state().unwrap()
        == account_state::AccountState::Frozen
    {
        assert_eq!(result, Err(ProgramError::Custom(17)));
        return result;
    } else if accounts[0] != accounts[1]
        && get_account(&accounts[1]).account_state().unwrap() == account_state::AccountState::Frozen
    {
        assert_eq!(result, Err(ProgramError::Custom(17)));
        return result;
    } else if src_initial_amount < amount {
        assert_eq!(result, Err(ProgramError::Custom(1)));
        return result;
    } else if accounts[0] != accounts[1]
        && get_account(&accounts[0]).mint != get_account(&accounts[1]).mint
    {
        assert_eq!(result, Err(ProgramError::Custom(3)));
        return result;
    } else {
        if old_src_delgate == Some(*accounts[2].key()) {
            // Validate Owner
            inner_test_validate_owner(
                &old_src_delgate.unwrap(), // expected_owner
                &accounts[2],              // owner_account_info
                &accounts[3..],            // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;

            if old_src_delgated_amount < amount {
                assert_eq!(result, Err(ProgramError::Custom(1)));
                return result;
            }
        } else {
            // Validate Owner
            inner_test_validate_owner(
                &src_owner,     // expected_owner
                &accounts[2],   // owner_account_info
                &accounts[3..], // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;
        }

        if (accounts[0] == accounts[1] || amount == 0)
            && accounts[0].owner() != &pinocchio_token_interface::program::ID
        {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId));
            return result;
        } else if (accounts[0] == accounts[1] || amount == 0)
            && accounts[1].owner() != &pinocchio_token_interface::program::ID
        {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId));
            return result;
        } else if accounts[0] != accounts[1]
            && amount != 0
            && get_account(&accounts[0]).is_native()
            && src_initial_lamports < amount
        {
            // Not sure how to fund native mint
            assert_eq!(result, Err(ProgramError::Custom(14)));
            return result;
        } else if accounts[0] != accounts[1]
            && amount != 0
            && get_account(&accounts[0]).is_native()
            && u64::MAX - amount < dst_initial_lamports
        {
            // Not sure how to fund native mint
            assert_eq!(result, Err(ProgramError::Custom(14)));
            return result;
        } else if accounts[0] != accounts[1] && amount != 0 {
            assert_eq!(
                get_account(&accounts[0]).amount(),
                src_initial_amount - amount
            );
            assert_eq!(
                get_account(&accounts[1]).amount(),
                dst_initial_amount + amount
            );

            if get_account(&accounts[0]).is_native() {
                assert_eq!(accounts[0].lamports(), src_initial_lamports - amount);
                assert_eq!(accounts[1].lamports(), dst_initial_lamports + amount);
            }
        }

        assert!(result.is_ok());

        // Delegate updates
        if old_src_delgate == Some(*accounts[2].key()) && accounts[0] != accounts[1] {
            assert_eq!(
                get_account(&accounts[0]).delegated_amount(),
                old_src_delgated_amount - amount
            );
            if old_src_delgated_amount - amount == 0 {
                assert_eq!(get_account(&accounts[0]).delegate(), None);
            }
        }
    }

    result
}

/// accounts[0] // Source Info
/// accounts[1] // Destination Info
/// accounts[2] // Authority Info
/// accounts[3..14] // Signers
/// instruction_data[0..8] // Little Endian Bytes of u64 amount
#[inline(never)]
pub fn test_process_transfer_multisig(
    accounts: &[AccountInfo; 4],
    instruction_data: &[u8; 8],
) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_account(&accounts[0]);
    cheatcode_is_account(&accounts[1]);
    cheatcode_is_multisig(&accounts[2]);

    //-Initial State-----------------------------------------------------------
    let amount = unsafe { u64::from_le_bytes(*(instruction_data.as_ptr() as *const [u8; 8])) };
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let dst_initialised = get_account(&accounts[1]).is_initialized();
    let src_initial_amount = get_account(&accounts[0]).amount();
    let dst_initial_amount = get_account(&accounts[1]).amount();
    let src_initial_lamports = accounts[0].lamports();
    let dst_initial_lamports = accounts[1].lamports();
    let src_owner = get_account(&accounts[0]).owner;
    let old_src_delgate = get_account(&accounts[0]).delegate().cloned();
    let old_src_delgated_amount = get_account(&accounts[0]).delegated_amount();
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[2]).is_initialized());

    //-Process Instruction-----------------------------------------------------
    let result = process_transfer(accounts, instruction_data);

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
    } else if accounts[0] != accounts[1] && dst_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if accounts[0] != accounts[1] && !dst_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount));
        return result;
    } else if get_account(&accounts[0]).account_state().unwrap()
        == account_state::AccountState::Frozen
    {
        assert_eq!(result, Err(ProgramError::Custom(17)));
        return result;
    } else if accounts[0] != accounts[1]
        && get_account(&accounts[1]).account_state().unwrap() == account_state::AccountState::Frozen
    {
        assert_eq!(result, Err(ProgramError::Custom(17)));
        return result;
    } else if src_initial_amount < amount {
        assert_eq!(result, Err(ProgramError::Custom(1)));
        return result;
    } else if accounts[0] != accounts[1]
        && get_account(&accounts[0]).mint != get_account(&accounts[1]).mint
    {
        assert_eq!(result, Err(ProgramError::Custom(3)));
        return result;
    } else {
        if old_src_delgate == Some(*accounts[2].key()) {
            // Validate Owner
            inner_test_validate_owner(
                &old_src_delgate.unwrap(), // expected_owner
                &accounts[2],              // owner_account_info
                &accounts[3..],            // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;

            if old_src_delgated_amount < amount {
                assert_eq!(result, Err(ProgramError::Custom(1)));
                return result;
            }
        } else {
            // Validate Owner
            inner_test_validate_owner(
                &src_owner,     // expected_owner
                &accounts[2],   // owner_account_info
                &accounts[3..], // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;
        }

        if (accounts[0] == accounts[1] || amount == 0)
            && accounts[0].owner() != &pinocchio_token_interface::program::ID
        {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId));
            return result;
        } else if (accounts[0] == accounts[1] || amount == 0)
            && accounts[1].owner() != &pinocchio_token_interface::program::ID
        {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId));
            return result;
        } else if accounts[0] != accounts[1]
            && amount != 0
            && get_account(&accounts[0]).is_native()
            && src_initial_lamports < amount
        {
            // Not sure how to fund native mint
            assert_eq!(result, Err(ProgramError::Custom(14)));
            return result;
        } else if accounts[0] != accounts[1]
            && amount != 0
            && get_account(&accounts[0]).is_native()
            && u64::MAX - amount < dst_initial_lamports
        {
            // Not sure how to fund native mint
            assert_eq!(result, Err(ProgramError::Custom(14)));
            return result;
        } else if accounts[0] != accounts[1] && amount != 0 {
            assert_eq!(
                get_account(&accounts[0]).amount(),
                src_initial_amount - amount
            );
            assert_eq!(
                get_account(&accounts[1]).amount(),
                dst_initial_amount + amount
            );

            if get_account(&accounts[0]).is_native() {
                assert_eq!(accounts[0].lamports(), src_initial_lamports - amount);
                assert_eq!(accounts[1].lamports(), dst_initial_lamports + amount);
            }
        }

        assert!(result.is_ok());

        // Delegate updates
        if old_src_delgate == Some(*accounts[2].key()) && accounts[0] != accounts[1] {
            assert_eq!(
                get_account(&accounts[0]).delegated_amount(),
                old_src_delgated_amount - amount
            );
            if old_src_delgated_amount - amount == 0 {
                assert_eq!(get_account(&accounts[0]).delegate(), None);
            }
        }
    }

    result
}

/// accounts[0] // Mint Info
/// accounts[1] // Destination Info
/// accounts[2] // Owner Info
/// instruction_data[0..8] // Little Endian Bytes of u64 amount
#[inline(never)]
pub fn test_process_mint_to(
    accounts: &[AccountInfo; 3],
    instruction_data: &[u8; 8],
) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_mint(&accounts[0]);
    cheatcode_is_account(&accounts[1]);

    //-Initial State-----------------------------------------------------------
    let initial_supply = get_mint(&accounts[0]).supply();
    let initial_amount = get_account(&accounts[1]).amount();
    let mint_initialised = get_mint(&accounts[0]).is_initialized();
    let dst_initialised = get_account(&accounts[1]).is_initialized();
    let dst_init_state = get_account(&accounts[1]).account_state();
    let maybe_multisig_is_initialised = None; // Value set to `None` since authority is an account

    //-Process Instruction-----------------------------------------------------
    let result = process_mint_to(accounts, instruction_data);

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
    } else if dst_init_state.unwrap() == account_state::AccountState::Frozen {
        // unwrap must succeed due to dst_initialised not being err
        assert_eq!(result, Err(ProgramError::Custom(17)));
        return result;
    } else if get_account(&accounts[1]).is_native() {
        assert_eq!(result, Err(ProgramError::Custom(10)));
        return result;
    } else if accounts[0].key() != &get_account(&accounts[1]).mint {
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
            // Validate Owner
            inner_test_validate_owner(
                get_mint(&accounts[0]).mint_authority().unwrap(), // expected_owner
                &accounts[2],                                     // owner_account_info
                &accounts[3..],                                   // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;
        } else {
            assert_eq!(result, Err(ProgramError::Custom(5)));
            return result;
        }

        let amount = unsafe { u64::from_le_bytes(*(instruction_data.as_ptr() as *const [u8; 8])) };

        if amount == 0 && accounts[0].owner() != &pinocchio_token_interface::program::ID {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId));
            return result;
        } else if amount == 0 && accounts[1].owner() != &pinocchio_token_interface::program::ID {
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

    result
}

/// accounts[0] // Mint Info
/// accounts[1] // Destination Info
/// accounts[2] // Owner Info
/// accounts[3..14] // Signers
/// instruction_data[0..8] // Little Endian Bytes of u64 amount
#[inline(never)]
pub fn test_process_mint_to_multisig(
    accounts: &[AccountInfo; 4],
    instruction_data: &[u8; 8],
) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_mint(&accounts[0]);
    cheatcode_is_account(&accounts[1]);
    cheatcode_is_multisig(&accounts[2]);

    //-Initial State-----------------------------------------------------------
    let initial_supply = get_mint(&accounts[0]).supply();
    let initial_amount = get_account(&accounts[1]).amount();
    let mint_initialised = get_mint(&accounts[0]).is_initialized();
    let dst_initialised = get_account(&accounts[1]).is_initialized();
    let dst_init_state = get_account(&accounts[1]).account_state();
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[2]).is_initialized());

    //-Process Instruction-----------------------------------------------------
    let result = process_mint_to(accounts, instruction_data);

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
    } else if dst_init_state.unwrap() == account_state::AccountState::Frozen {
        // unwrap must succeed due to dst_initialised not being err
        assert_eq!(result, Err(ProgramError::Custom(17)));
        return result;
    } else if get_account(&accounts[1]).is_native() {
        assert_eq!(result, Err(ProgramError::Custom(10)));
        return result;
    } else if accounts[0].key() != &get_account(&accounts[1]).mint {
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
            // Validate Owner
            inner_test_validate_owner(
                get_mint(&accounts[0]).mint_authority().unwrap(), // expected_owner
                &accounts[2],                                     // owner_account_info
                &accounts[3..],                                   // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;
        } else {
            assert_eq!(result, Err(ProgramError::Custom(5)));
            return result;
        }

        let amount = unsafe { u64::from_le_bytes(*(instruction_data.as_ptr() as *const [u8; 8])) };

        if amount == 0 && accounts[0].owner() != &pinocchio_token_interface::program::ID {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId));
            return result;
        } else if amount == 0 && accounts[1].owner() != &pinocchio_token_interface::program::ID {
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

    result
}

/// accounts[0] // Source Info
/// accounts[1] // Mint Info
/// accounts[2] // Authority Info
/// instruction_data[0..8] // Little Endian Bytes of u64 amount
#[inline(never)]
pub fn test_process_burn(accounts: &[AccountInfo; 3], instruction_data: &[u8; 8]) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_account(&accounts[0]);
    cheatcode_is_mint(&accounts[1]);

    //-Initial State-----------------------------------------------------------
    let amount = unsafe { u64::from_le_bytes(*(instruction_data.as_ptr() as *const [u8; 8])) };
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_init_amount = get_account(&accounts[0]).amount();
    let src_init_state = get_account(&accounts[0]).account_state();
    let src_is_native = get_account(&accounts[0]).is_native();
    let src_mint = get_account(&accounts[0]).mint;
    let src_owned_sys_inc = get_account(&accounts[0]).is_owned_by_system_program_or_incinerator();
    let src_owner = get_account(&accounts[0]).owner;
    let old_src_delgate = get_account(&accounts[0]).delegate().cloned();
    let old_src_delgated_amount = get_account(&accounts[0]).delegated_amount();
    let mint_initialised = get_mint(&accounts[1]).is_initialized();
    let mint_init_supply = get_mint(&accounts[1]).supply();
    let mint_owner = *accounts[1].owner();
    let maybe_multisig_is_initialised = None; // Value set to `None` since authority is an account

    //-Process Instruction-----------------------------------------------------
    let result = process_burn(accounts, instruction_data);

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
    } else if src_init_state.unwrap() == account_state::AccountState::Frozen {
        assert_eq!(result, Err(ProgramError::Custom(17)))
    } else if src_is_native {
        assert_eq!(result, Err(ProgramError::Custom(10)))
    } else if src_init_amount < amount {
        assert_eq!(result, Err(ProgramError::Custom(1)))
    } else if accounts[1].key() != &src_mint {
        assert_eq!(result, Err(ProgramError::Custom(3)))
    } else {
        if !src_owned_sys_inc {
            if old_src_delgate.is_some() && *accounts[2].key() == old_src_delgate.unwrap() {
                // Validate Owner
                inner_test_validate_owner(
                    &old_src_delgate.unwrap(), // expected_owner
                    &accounts[2],              // owner_account_info
                    &accounts[3..],            // tx_signers
                    maybe_multisig_is_initialised,
                    result.clone(),
                )?;

                if old_src_delgated_amount < amount {
                    assert_eq!(result, Err(ProgramError::Custom(1)));
                    return result;
                }
            } else {
                // Validate Owner
                inner_test_validate_owner(
                    &src_owner,     // expected_owner
                    &accounts[2],   // owner_account_info
                    &accounts[3..], // tx_signers
                    maybe_multisig_is_initialised,
                    result.clone(),
                )?;
            }
        }

        if amount == 0 && src_owner != pinocchio_token_interface::program::ID {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId))
        } else if amount == 0 && mint_owner != pinocchio_token_interface::program::ID {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId))
        } else {
            assert!(get_account(&accounts[0]).amount() == src_init_amount - amount);
            assert!(get_mint(&accounts[1]).supply() == mint_init_supply - amount);
            assert!(result.is_ok());

            // Delegate updates
            if old_src_delgate.is_some() && *accounts[2].key() == old_src_delgate.unwrap() {
                assert_eq!(
                    get_account(&accounts[0]).delegated_amount(),
                    old_src_delgated_amount - amount
                );
                if old_src_delgated_amount - amount == 0 {
                    assert_eq!(get_account(&accounts[0]).delegate(), None);
                }
            }
        }
    }

    result
}

/// accounts[0] // Source Info
/// accounts[1] // Mint Info
/// accounts[2] // Authority Info
/// accounts[3..14] // Signers
/// instruction_data[0..8] // Little Endian Bytes of u64 amount
#[inline(never)]
pub fn test_process_burn_multisig(
    accounts: &[AccountInfo; 4],
    instruction_data: &[u8; 8],
) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_account(&accounts[0]);
    cheatcode_is_mint(&accounts[1]);
    cheatcode_is_multisig(&accounts[2]);

    //-Initial State-----------------------------------------------------------
    let amount = unsafe { u64::from_le_bytes(*(instruction_data.as_ptr() as *const [u8; 8])) };
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_init_amount = get_account(&accounts[0]).amount();
    let src_init_state = get_account(&accounts[0]).account_state();
    let src_is_native = get_account(&accounts[0]).is_native();
    let src_mint = get_account(&accounts[0]).mint;
    let src_owned_sys_inc = get_account(&accounts[0]).is_owned_by_system_program_or_incinerator();
    let src_owner = get_account(&accounts[0]).owner;
    let old_src_delgate = get_account(&accounts[0]).delegate().cloned();
    let old_src_delgated_amount = get_account(&accounts[0]).delegated_amount();
    let mint_initialised = get_mint(&accounts[1]).is_initialized();
    let mint_init_supply = get_mint(&accounts[1]).supply();
    let mint_owner = *accounts[1].owner();
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[2]).is_initialized());

    //-Process Instruction-----------------------------------------------------
    let result = process_burn(accounts, instruction_data);

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
    } else if src_init_state.unwrap() == account_state::AccountState::Frozen {
        assert_eq!(result, Err(ProgramError::Custom(17)))
    } else if src_is_native {
        assert_eq!(result, Err(ProgramError::Custom(10)))
    } else if src_init_amount < amount {
        assert_eq!(result, Err(ProgramError::Custom(1)))
    } else if accounts[1].key() != &src_mint {
        assert_eq!(result, Err(ProgramError::Custom(3)))
    } else {
        if !src_owned_sys_inc {
            if old_src_delgate.is_some() && *accounts[2].key() == old_src_delgate.unwrap() {
                // Validate Owner
                inner_test_validate_owner(
                    &old_src_delgate.unwrap(), // expected_owner
                    &accounts[2],              // owner_account_info
                    &accounts[3..],            // tx_signers
                    maybe_multisig_is_initialised,
                    result.clone(),
                )?;

                if old_src_delgated_amount < amount {
                    assert_eq!(result, Err(ProgramError::Custom(1)));
                    return result;
                }
            } else {
                // Validate Owner
                inner_test_validate_owner(
                    &src_owner,     // expected_owner
                    &accounts[2],   // owner_account_info
                    &accounts[3..], // tx_signers
                    maybe_multisig_is_initialised,
                    result.clone(),
                )?;
            }
        }

        if amount == 0 && src_owner != pinocchio_token_interface::program::ID {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId))
        } else if amount == 0 && mint_owner != pinocchio_token_interface::program::ID {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId))
        } else {
            assert!(get_account(&accounts[0]).amount() == src_init_amount - amount);
            assert!(get_mint(&accounts[1]).supply() == mint_init_supply - amount);
            assert!(result.is_ok());

            // Delegate updates
            if old_src_delgate.is_some() && *accounts[2].key() == old_src_delgate.unwrap() {
                assert_eq!(
                    get_account(&accounts[0]).delegated_amount(),
                    old_src_delgated_amount - amount
                );
                if old_src_delgated_amount - amount == 0 {
                    assert_eq!(get_account(&accounts[0]).delegate(), None);
                }
            }
        }
    }

    result
}

/// accounts[0] // Source Info
/// accounts[1] // Destination Info
/// accounts[2] // Authority Info
#[inline(never)]
pub fn test_process_close_account(accounts: &[AccountInfo; 3]) -> ProgramResult {
    use pinocchio_token_interface::state::account::INCINERATOR_ID;

    cheatcode_is_account(&accounts[0]);
    cheatcode_is_account(&accounts[1]);

    //-Initial State-----------------------------------------------------------
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_data_len = accounts[0].data_len();
    let src_init_amount = get_account(&accounts[0]).amount();
    let src_init_lamports = accounts[0].lamports();
    let dst_init_lamports = accounts[1].lamports();
    let src_is_native = get_account(&accounts[0]).is_native();
    let src_owned_sys_inc = get_account(&accounts[0]).is_owned_by_system_program_or_incinerator();
    let authority = get_account(&accounts[0])
        .close_authority()
        .cloned()
        .unwrap_or(get_account(&accounts[0]).owner);
    let maybe_multisig_is_initialised = None; // Value set to `None` since authority is an account

    //-Process Instruction-----------------------------------------------------
    let result = process_close_account(accounts);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else if accounts[0] == accounts[1] {
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
            // Validate Owner
            inner_test_validate_owner(
                &authority,     // expected_owner
                &accounts[2],   // owner_account_info
                &accounts[3..], // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;
        } else if accounts[1].key() != &INCINERATOR_ID {
            assert_eq!(result, Err(ProgramError::InvalidAccountData));
            return result;
        } else if u64::MAX - src_init_lamports < dst_init_lamports {
            assert_eq!(result, Err(ProgramError::Custom(14)));
            return result;
        }

        // Validate owner falls through to here if no error
        assert_eq!(accounts[0].lamports(), 0);
        assert_eq!(
            accounts[1].lamports(),
            dst_init_lamports + src_init_lamports
        );
        assert_eq!(accounts[0].data_len(), 0); // TODO: More sol_memset stuff?
        assert!(result.is_ok());
    }
    result
}

/// accounts[0] // Source Info
/// accounts[1] // Destination Info
/// accounts[2] // Authority Info
/// accounts[3..14] // Multisig Signers
#[inline(never)]
pub fn test_process_close_account_multisig(accounts: &[AccountInfo; 4]) -> ProgramResult {
    use pinocchio_token_interface::state::account::INCINERATOR_ID;

    cheatcode_is_account(&accounts[0]);
    cheatcode_is_account(&accounts[1]);
    cheatcode_is_multisig(&accounts[2]);

    //-Initial State-----------------------------------------------------------
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_data_len = accounts[0].data_len();
    let src_init_amount = get_account(&accounts[0]).amount();
    let src_init_lamports = accounts[0].lamports();
    let dst_init_lamports = accounts[1].lamports();
    let src_is_native = get_account(&accounts[0]).is_native();
    let src_owned_sys_inc = get_account(&accounts[0]).is_owned_by_system_program_or_incinerator();
    let authority = get_account(&accounts[0])
        .close_authority()
        .cloned()
        .unwrap_or(get_account(&accounts[0]).owner);
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[2]).is_initialized());

    //-Process Instruction-----------------------------------------------------
    let result = process_close_account(accounts);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else if accounts[0] == accounts[1] {
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
            // Validate Owner
            inner_test_validate_owner(
                &authority,     // expected_owner
                &accounts[2],   // owner_account_info
                &accounts[3..], // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;
        } else if accounts[1].key() != &INCINERATOR_ID {
            assert_eq!(result, Err(ProgramError::InvalidAccountData));
            return result;
        } else if u64::MAX - src_init_lamports < dst_init_lamports {
            assert_eq!(result, Err(ProgramError::Custom(14)));
            return result;
        }

        // Validate owner falls through to here if no error
        assert_eq!(accounts[0].lamports(), 0);
        assert_eq!(
            accounts[1].lamports(),
            dst_init_lamports + src_init_lamports
        );
        assert_eq!(accounts[0].data_len(), 0); // TODO: More sol_memset stuff?
        assert!(result.is_ok());
    }
    result
}

/// accounts[0] // Source Info
/// accounts[1] // Mint Info
/// accounts[2] // Destination Info
/// accounts[3] // Authority Info
/// instruction_data[0..9] // Little Endian Bytes of u64 amount, and decimals
#[inline(never)]
pub fn test_process_transfer_checked(
    accounts: &[AccountInfo; 4],
    instruction_data: &[u8; 9],
) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_account(&accounts[0]);
    cheatcode_is_mint(&accounts[1]);
    cheatcode_is_account(&accounts[2]);

    //-Initial State-----------------------------------------------------------
    let amount = unsafe { u64::from_le_bytes(*(instruction_data.as_ptr() as *const [u8; 8])) };
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let dst_initialised = get_account(&accounts[2]).is_initialized();
    let src_initial_amount = get_account(&accounts[0]).amount();
    let dst_initial_amount = get_account(&accounts[2]).amount();
    let src_initial_lamports = accounts[0].lamports();
    let dst_initial_lamports = accounts[2].lamports();
    let src_owner = get_account(&accounts[0]).owner;
    let old_src_delgate = get_account(&accounts[0]).delegate().cloned();
    let old_src_delgated_amount = get_account(&accounts[0]).delegated_amount();
    let mint_initialised = get_mint(&accounts[1]).is_initialized();
    let maybe_multisig_is_initialised = None; // Value set to `None` since authority is an account

    //-Process Instruction-----------------------------------------------------
    let result = process_transfer_checked(accounts, instruction_data);

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
    } else if accounts[0] != accounts[2] && dst_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if accounts[0] != accounts[2] && !dst_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount));
        return result;
    } else if get_account(&accounts[0]).account_state().unwrap()
        == account_state::AccountState::Frozen
    {
        assert_eq!(result, Err(ProgramError::Custom(17)));
        return result;
    } else if accounts[0] != accounts[2]
        && get_account(&accounts[2]).account_state().unwrap() == account_state::AccountState::Frozen
    {
        assert_eq!(result, Err(ProgramError::Custom(17)));
        return result;
    } else if src_initial_amount < amount {
        assert_eq!(result, Err(ProgramError::Custom(1)));
        return result;
    } else if accounts[0] != accounts[2]
        && get_account(&accounts[0]).mint != get_account(&accounts[2]).mint
    {
        assert_eq!(result, Err(ProgramError::Custom(3)));
        return result;
    } else if accounts[1].key() != &get_account(&accounts[0]).mint {
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
    } else if instruction_data[8] != get_mint(&accounts[1]).decimals {
        assert_eq!(result, Err(ProgramError::Custom(18)));
        return result;
    } else {
        if old_src_delgate == Some(*accounts[3].key()) {
            // Because of the above if, there is a duplicated check in the following
            // function Validate Owner
            inner_test_validate_owner(
                &old_src_delgate.unwrap(), // expected_owner
                &accounts[3],              // owner_account_info
                &accounts[4..],            // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;

            if old_src_delgated_amount < amount {
                assert_eq!(result, Err(ProgramError::Custom(1)));
                return result;
            }
        } else {
            // Validate Owner
            inner_test_validate_owner(
                &src_owner,     // expected_owner
                &accounts[3],   // owner_account_info
                &accounts[4..], // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;
        }

        if (accounts[0] == accounts[2] || amount == 0)
            && accounts[0].owner() != &pinocchio_token_interface::program::ID
        {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId));
            return result;
        } else if (accounts[0] == accounts[2] || amount == 0)
            && accounts[2].owner() != &pinocchio_token_interface::program::ID
        {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId));
            return result;
        } else if accounts[0] != accounts[2] && amount != 0 {
            if get_account(&accounts[0]).is_native() && src_initial_lamports < amount {
                // Not sure how to fund native mint
                assert_eq!(result, Err(ProgramError::Custom(14)));
                return result;
            } else if get_account(&accounts[0]).is_native()
                && u64::MAX - amount < dst_initial_lamports
            {
                // Not sure how to fund native mint
                assert_eq!(result, Err(ProgramError::Custom(14)));
                return result;
            }

            assert_eq!(
                get_account(&accounts[0]).amount(),
                src_initial_amount - amount
            );
            assert_eq!(
                get_account(&accounts[2]).amount(),
                dst_initial_amount + amount
            );

            if get_account(&accounts[0]).is_native() {
                assert_eq!(accounts[0].lamports(), src_initial_lamports - amount);
                assert_eq!(accounts[1].lamports(), dst_initial_lamports + amount);
            }
        }

        assert!(result.is_ok());
        // Delegate updates
        if old_src_delgate == Some(*accounts[3].key()) && accounts[0] != accounts[2] {
            assert_eq!(
                get_account(&accounts[0]).delegated_amount(),
                old_src_delgated_amount - amount
            );
            if old_src_delgated_amount - amount == 0 {
                assert_eq!(get_account(&accounts[0]).delegate(), None);
            }
        }
    }

    result
}

/// accounts[0] // Source Info
/// accounts[1] // Mint Info
/// accounts[2] // Destination Info
/// accounts[3] // Authority Info
/// accounts[4..15] // Signers
/// instruction_data[0..9] // Little Endian Bytes of u64 amount, and decimals
#[inline(never)]
pub fn test_process_transfer_checked_multisig(
    accounts: &[AccountInfo; 5],
    instruction_data: &[u8; 9],
) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_account(&accounts[0]);
    cheatcode_is_mint(&accounts[1]);
    cheatcode_is_account(&accounts[2]);
    cheatcode_is_multisig(&accounts[3]);

    //-Initial State-----------------------------------------------------------
    let amount = unsafe { u64::from_le_bytes(*(instruction_data.as_ptr() as *const [u8; 8])) };
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let dst_initialised = get_account(&accounts[2]).is_initialized();
    let src_initial_amount = get_account(&accounts[0]).amount();
    let dst_initial_amount = get_account(&accounts[2]).amount();
    let src_initial_lamports = accounts[0].lamports();
    let dst_initial_lamports = accounts[2].lamports();
    let src_owner = get_account(&accounts[0]).owner;
    let old_src_delgate = get_account(&accounts[0]).delegate().cloned();
    let old_src_delgated_amount = get_account(&accounts[0]).delegated_amount();
    let mint_initialised = get_mint(&accounts[1]).is_initialized();
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[3]).is_initialized());

    //-Process Instruction-----------------------------------------------------
    let result = process_transfer_checked(accounts, instruction_data);

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
    } else if accounts[0] != accounts[2] && dst_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if accounts[0] != accounts[2] && !dst_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount));
        return result;
    } else if get_account(&accounts[0]).account_state().unwrap()
        == account_state::AccountState::Frozen
    {
        assert_eq!(result, Err(ProgramError::Custom(17)));
        return result;
    } else if accounts[0] != accounts[2]
        && get_account(&accounts[2]).account_state().unwrap() == account_state::AccountState::Frozen
    {
        assert_eq!(result, Err(ProgramError::Custom(17)));
        return result;
    } else if src_initial_amount < amount {
        assert_eq!(result, Err(ProgramError::Custom(1)));
        return result;
    } else if accounts[0] != accounts[2]
        && get_account(&accounts[0]).mint != get_account(&accounts[2]).mint
    {
        assert_eq!(result, Err(ProgramError::Custom(3)));
        return result;
    } else if accounts[1].key() != &get_account(&accounts[0]).mint {
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
    } else if instruction_data[8] != get_mint(&accounts[1]).decimals {
        assert_eq!(result, Err(ProgramError::Custom(18)));
        return result;
    } else {
        if old_src_delgate == Some(*accounts[3].key()) {
            // Because of the above if, there is a duplicated check in the following
            // function Validate Owner
            inner_test_validate_owner(
                &old_src_delgate.unwrap(), // expected_owner
                &accounts[3],              // owner_account_info
                &accounts[4..],            // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;

            if old_src_delgated_amount < amount {
                assert_eq!(result, Err(ProgramError::Custom(1)));
                return result;
            }
        } else {
            // Validate Owner
            inner_test_validate_owner(
                &src_owner,     // expected_owner
                &accounts[3],   // owner_account_info
                &accounts[4..], // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;
        }

        if (accounts[0] == accounts[2] || amount == 0)
            && accounts[0].owner() != &pinocchio_token_interface::program::ID
        {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId));
            return result;
        } else if (accounts[0] == accounts[2] || amount == 0)
            && accounts[2].owner() != &pinocchio_token_interface::program::ID
        {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId));
            return result;
        } else if accounts[0] != accounts[2] && amount != 0 {
            if get_account(&accounts[0]).is_native() && src_initial_lamports < amount {
                // Not sure how to fund native mint
                assert_eq!(result, Err(ProgramError::Custom(14)));
                return result;
            } else if get_account(&accounts[0]).is_native()
                && u64::MAX - amount < dst_initial_lamports
            {
                // Not sure how to fund native mint
                assert_eq!(result, Err(ProgramError::Custom(14)));
                return result;
            }

            assert_eq!(
                get_account(&accounts[0]).amount(),
                src_initial_amount - amount
            );
            assert_eq!(
                get_account(&accounts[2]).amount(),
                dst_initial_amount + amount
            );

            if get_account(&accounts[0]).is_native() {
                assert_eq!(accounts[0].lamports(), src_initial_lamports - amount);
                assert_eq!(accounts[1].lamports(), dst_initial_lamports + amount);
            }
        }

        assert!(result.is_ok());
        // Delegate updates
        if old_src_delgate == Some(*accounts[3].key()) && accounts[0] != accounts[2] {
            assert_eq!(
                get_account(&accounts[0]).delegated_amount(),
                old_src_delgated_amount - amount
            );
            if old_src_delgated_amount - amount == 0 {
                assert_eq!(get_account(&accounts[0]).delegate(), None);
            }
        }
    }

    result
}

/// accounts[0] // Source Info
/// accounts[1] // Mint Info
/// accounts[2] // Authority Info
/// instruction_data[0..9] // Little Endian Bytes of u64 amount, and decimals
#[inline(never)]
pub fn test_process_burn_checked(
    accounts: &[AccountInfo; 3],
    instruction_data: &[u8; 9],
) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_account(&accounts[0]);
    cheatcode_is_mint(&accounts[1]);

    //-Initial State-----------------------------------------------------------
    let amount = unsafe { u64::from_le_bytes(*(instruction_data.as_ptr() as *const [u8; 8])) };
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_init_amount = get_account(&accounts[0]).amount();
    let src_init_state = get_account(&accounts[0]).account_state();
    let src_is_native = get_account(&accounts[0]).is_native();
    let src_mint = get_account(&accounts[0]).mint;
    let src_owned_sys_inc = get_account(&accounts[0]).is_owned_by_system_program_or_incinerator();
    let src_owner = get_account(&accounts[0]).owner;
    let old_src_delgate = get_account(&accounts[0]).delegate().cloned();
    let old_src_delgated_amount = get_account(&accounts[0]).delegated_amount();
    let mint_initialised = get_mint(&accounts[1]).is_initialized();
    let mint_init_supply = get_mint(&accounts[1]).supply();
    let mint_decimals = get_mint(&accounts[1]).decimals;
    let mint_owner = *accounts[1].owner();
    let maybe_multisig_is_initialised = None; // Value set to `None` since authority is an account

    //-Process Instruction-----------------------------------------------------
    let result = process_burn_checked(accounts, instruction_data);

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
    } else if src_init_state.unwrap() == account_state::AccountState::Frozen {
        assert_eq!(result, Err(ProgramError::Custom(17)))
    } else if src_is_native {
        assert_eq!(result, Err(ProgramError::Custom(10)))
    } else if src_init_amount < amount {
        assert_eq!(result, Err(ProgramError::Custom(1)))
    } else if accounts[1].key() != &src_mint {
        assert_eq!(result, Err(ProgramError::Custom(3)))
    } else if instruction_data[8] != mint_decimals {
        assert_eq!(result, Err(ProgramError::Custom(18)))
    } else {
        if !src_owned_sys_inc {
            if old_src_delgate.is_some() && *accounts[2].key() == old_src_delgate.unwrap() {
                // Validate Owner
                inner_test_validate_owner(
                    &old_src_delgate.unwrap(), // expected_owner
                    &accounts[2],              // owner_account_info
                    &accounts[3..],            // tx_signers
                    maybe_multisig_is_initialised,
                    result.clone(),
                )?;

                if old_src_delgated_amount < amount {
                    assert_eq!(result, Err(ProgramError::Custom(1)));
                    return result;
                }
            } else {
                // Validate Owner
                inner_test_validate_owner(
                    &src_owner,     // expected_owner
                    &accounts[2],   // owner_account_info
                    &accounts[3..], // tx_signers
                    maybe_multisig_is_initialised,
                    result.clone(),
                )?;
            }
        }

        if amount == 0 && src_owner != pinocchio_token_interface::program::ID {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId))
        } else if amount == 0 && mint_owner != pinocchio_token_interface::program::ID {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId))
        } else {
            assert!(get_account(&accounts[0]).amount() == src_init_amount - amount);
            assert!(get_mint(&accounts[1]).supply() == mint_init_supply - amount);
            assert!(result.is_ok());

            // Delegate updates
            if old_src_delgate.is_some() && *accounts[2].key() == old_src_delgate.unwrap() {
                assert_eq!(
                    get_account(&accounts[0]).delegated_amount(),
                    old_src_delgated_amount - amount
                );
                if old_src_delgated_amount - amount == 0 {
                    assert_eq!(get_account(&accounts[0]).delegate(), None);
                }
            }
        }
    }

    result
}

/// accounts[0] // Source Info
/// accounts[1] // Mint Info
/// accounts[2] // Authority Info
/// accounts[3..14] // Signers
/// instruction_data[0..9] // Little Endian Bytes of u64 amount, and decimals
#[inline(never)]
pub fn test_process_burn_checked_multisig(
    accounts: &[AccountInfo; 4],
    instruction_data: &[u8; 9],
) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_account(&accounts[0]);
    cheatcode_is_mint(&accounts[1]);
    cheatcode_is_multisig(&accounts[2]);

    //-Initial State-----------------------------------------------------------
    let amount = unsafe { u64::from_le_bytes(*(instruction_data.as_ptr() as *const [u8; 8])) };
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_init_amount = get_account(&accounts[0]).amount();
    let src_init_state = get_account(&accounts[0]).account_state();
    let src_is_native = get_account(&accounts[0]).is_native();
    let src_mint = get_account(&accounts[0]).mint;
    let src_owned_sys_inc = get_account(&accounts[0]).is_owned_by_system_program_or_incinerator();
    let src_owner = get_account(&accounts[0]).owner;
    let old_src_delgate = get_account(&accounts[0]).delegate().cloned();
    let old_src_delgated_amount = get_account(&accounts[0]).delegated_amount();
    let mint_initialised = get_mint(&accounts[1]).is_initialized();
    let mint_init_supply = get_mint(&accounts[1]).supply();
    let mint_decimals = get_mint(&accounts[1]).decimals;
    let mint_owner = *accounts[1].owner();
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[2]).is_initialized());

    //-Process Instruction-----------------------------------------------------
    let result = process_burn_checked(accounts, instruction_data);

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
    } else if src_init_state.unwrap() == account_state::AccountState::Frozen {
        assert_eq!(result, Err(ProgramError::Custom(17)))
    } else if src_is_native {
        assert_eq!(result, Err(ProgramError::Custom(10)))
    } else if src_init_amount < amount {
        assert_eq!(result, Err(ProgramError::Custom(1)))
    } else if accounts[1].key() != &src_mint {
        assert_eq!(result, Err(ProgramError::Custom(3)))
    } else if instruction_data[8] != mint_decimals {
        assert_eq!(result, Err(ProgramError::Custom(18)))
    } else {
        if !src_owned_sys_inc {
            if old_src_delgate.is_some() && *accounts[2].key() == old_src_delgate.unwrap() {
                // Validate Owner
                inner_test_validate_owner(
                    &old_src_delgate.unwrap(), // expected_owner
                    &accounts[2],              // owner_account_info
                    &accounts[3..],            // tx_signers
                    maybe_multisig_is_initialised,
                    result.clone(),
                )?;

                if old_src_delgated_amount < amount {
                    assert_eq!(result, Err(ProgramError::Custom(1)));
                    return result;
                }
            } else {
                // Validate Owner
                inner_test_validate_owner(
                    &src_owner,     // expected_owner
                    &accounts[2],   // owner_account_info
                    &accounts[3..], // tx_signers
                    maybe_multisig_is_initialised,
                    result.clone(),
                )?;
            }
        }

        if amount == 0 && src_owner != pinocchio_token_interface::program::ID {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId))
        } else if amount == 0 && mint_owner != pinocchio_token_interface::program::ID {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId))
        } else {
            assert!(get_account(&accounts[0]).amount() == src_init_amount - amount);
            assert!(get_mint(&accounts[1]).supply() == mint_init_supply - amount);
            assert!(result.is_ok());

            // Delegate updates
            if old_src_delgate.is_some() && *accounts[2].key() == old_src_delgate.unwrap() {
                assert_eq!(
                    get_account(&accounts[0]).delegated_amount(),
                    old_src_delgated_amount - amount
                );
                if old_src_delgated_amount - amount == 0 {
                    assert_eq!(get_account(&accounts[0]).delegate(), None);
                }
            }
        }
    }

    result
}

/// accounts[0] // New Account Info
/// accounts[1] // Mint Info
/// accounts[2] // Rent Sysvar Info
/// instruction_data[..] // Owner
#[inline(never)]
pub fn test_process_initialize_account2(
    accounts: &[AccountInfo; 3],
    instruction_data: &[u8; 32],
) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_account(&accounts[0]);
    cheatcode_is_mint(&accounts[1]);
    cheatcode_is_rent(&accounts[2]);

    //-Initial State-----------------------------------------------------------
    let initial_state_new_account = get_account(&accounts[0]).account_state();

    let minimum_balance = get_rent(&accounts[2]).minimum_balance(accounts[0].data_len());

    let is_native_mint = accounts[1].key() == &pinocchio_token_interface::native_mint::ID;

    let mint_is_initialised = get_mint(&accounts[1]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = process_initialize_account2(accounts, instruction_data);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < pinocchio::pubkey::PUBKEY_BYTES {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
    } else if accounts[2].key() != &pinocchio::sysvars::rent::RENT_ID {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if accounts[0].data_len() != Account::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if initial_state_new_account.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if initial_state_new_account.unwrap() != account_state::AccountState::Uninitialized {
        assert_eq!(result, Err(ProgramError::Custom(6)))
    } else if accounts[0].lamports() < minimum_balance {
        assert_eq!(result, Err(ProgramError::Custom(0)))
    } else if !is_native_mint && accounts[1].owner() != &pinocchio_token_interface::program::ID {
        assert_eq!(result, Err(ProgramError::IncorrectProgramId))
    } else if !is_native_mint
        && accounts[1].owner() == &pinocchio_token_interface::program::ID
        && mint_is_initialised.is_err()
    {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !is_native_mint
        && accounts[1].owner() == &pinocchio_token_interface::program::ID
        && !mint_is_initialised.unwrap()
    {
        assert_eq!(result, Err(ProgramError::Custom(2)))
    } else {
        assert!(result.is_ok());
        assert_eq!(
            get_account(&accounts[0]).account_state().unwrap(),
            account_state::AccountState::Initialized
        );
        assert_eq!(get_account(&accounts[0]).mint, *accounts[1].key());
        assert_eq!(get_account(&accounts[0]).owner, *instruction_data);

        if is_native_mint {
            assert!(get_account(&accounts[0]).is_native());
            assert_eq!(
                get_account(&accounts[0]).native_amount().unwrap(),
                minimum_balance
            );
            assert_eq!(
                get_account(&accounts[0]).amount(),
                accounts[0].lamports() - minimum_balance
            );
        }
    }

    result
}

/// accounts[0] // New Account Info
/// accounts[1] // Mint Info
/// instruction_data[..] // Owner
#[inline(never)]
pub fn test_process_initialize_account3(
    accounts: &[AccountInfo; 2],
    instruction_data: &[u8; 32],
) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_account(&accounts[0]);
    cheatcode_is_mint(&accounts[1]);

    //-Initial State-----------------------------------------------------------
    let initial_state_new_account = get_account(&accounts[0]).account_state();

    // Note: Rent is a supported sysvar so ProgramError::UnsupportedSysvar should be
    // impossible
    let rent = pinocchio::sysvars::rent::Rent::get().unwrap();
    let minimum_balance = rent.minimum_balance(accounts[0].data_len());

    let is_native_mint = accounts[1].key() == &pinocchio_token_interface::native_mint::ID;

    let mint_is_initialised = get_mint(&accounts[1]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = process_initialize_account3(accounts, instruction_data);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < pinocchio::pubkey::PUBKEY_BYTES {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.len() < 2 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
    } else if accounts[0].data_len() != Account::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if initial_state_new_account.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if initial_state_new_account.unwrap() != account_state::AccountState::Uninitialized {
        assert_eq!(result, Err(ProgramError::Custom(6)))
    } else if accounts[0].lamports() < minimum_balance {
        assert_eq!(result, Err(ProgramError::Custom(0)))
    } else if !is_native_mint && accounts[1].owner() != &pinocchio_token_interface::program::ID {
        assert_eq!(result, Err(ProgramError::IncorrectProgramId))
    } else if !is_native_mint
        && accounts[1].owner() == &pinocchio_token_interface::program::ID
        && mint_is_initialised.is_err()
    {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !is_native_mint
        && accounts[1].owner() == &pinocchio_token_interface::program::ID
        && !mint_is_initialised.unwrap()
    {
        assert_eq!(result, Err(ProgramError::Custom(2)))
    } else {
        assert!(result.is_ok());
        assert_eq!(
            get_account(&accounts[0]).account_state().unwrap(),
            account_state::AccountState::Initialized
        );
        assert_eq!(get_account(&accounts[0]).mint, *accounts[1].key());
        assert_eq!(get_account(&accounts[0]).owner, *instruction_data);

        if is_native_mint {
            assert!(get_account(&accounts[0]).is_native());
            assert_eq!(
                get_account(&accounts[0]).native_amount().unwrap(),
                minimum_balance
            );
            assert_eq!(
                get_account(&accounts[0]).amount(),
                accounts[0].lamports() - minimum_balance
            );
        }
    }

    result
}

/// accounts[0] // Mint Info
/// instruction_data[0]      // Decimals
/// instruction_data[1..33]  // Mint Authority Pubkey
/// instruction_data[33]     // Freeze Authority Exists? 1 for freeze
/// instruction_data[34..66] // instruction_data[33] == 1 ==> Freeze Authority
/// Pubkey
#[inline(never)]
pub fn test_process_initialize_mint2_freeze(
    accounts: &[AccountInfo; 1],
    instruction_data: &[u8; 66],
) -> ProgramResult {
    cheatcode_is_mint(&accounts[0]);

    //-Initial State-----------------------------------------------------------
    // Note: Rent is a supported sysvar so ProgramError::UnsupportedSysvar should be
    // impossible
    let rent = pinocchio::sysvars::rent::Rent::get().unwrap();
    let minimum_balance = rent.minimum_balance(accounts[0].data_len());
    let mint_is_initialised_prior = get_mint(&accounts[0]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = process_initialize_mint2(accounts, instruction_data);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < 34 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if instruction_data[33] != 0 && instruction_data[33] != 1 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if instruction_data[33] == 1 && instruction_data.len() < 66 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.is_empty() {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].data_len() != Mint::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if mint_is_initialised_prior.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if mint_is_initialised_prior.unwrap() {
        assert_eq!(result, Err(ProgramError::Custom(6)))
    } else if accounts[0].lamports() < minimum_balance {
        assert_eq!(result, Err(ProgramError::Custom(0)))
    } else {
        assert!(get_mint(&accounts[0]).is_initialized().unwrap());
        assert_eq!(
            get_mint(&accounts[0]).mint_authority().unwrap(),
            &instruction_data[1..33]
        );
        assert_eq!(get_mint(&accounts[0]).decimals, instruction_data[0]);

        if instruction_data[33] == 1 {
            assert_eq!(
                get_mint(&accounts[0]).freeze_authority().unwrap(),
                &instruction_data[34..66]
            );
        }
    }

    result
}

/// accounts[0] // Mint Info
/// instruction_data[0]      // Decimals
/// instruction_data[1..33]  // Mint Authority Pubkey
/// instruction_data[33]     // Freeze Authority Exists? 0 for no freeze
#[inline(never)]
pub fn test_process_initialize_mint2_no_freeze(
    accounts: &[AccountInfo; 1],
    instruction_data: &[u8; 34],
) -> ProgramResult {
    cheatcode_is_mint(&accounts[0]);

    //-Initial State-----------------------------------------------------------
    // Note: Rent is a supported sysvar so ProgramError::UnsupportedSysvar should be
    // impossible
    let rent = pinocchio::sysvars::rent::Rent::get().unwrap();
    let minimum_balance = rent.minimum_balance(accounts[0].data_len());
    let mint_is_initialised_prior = get_mint(&accounts[0]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = process_initialize_mint2(accounts, instruction_data);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < 34 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if instruction_data[33] != 0 && instruction_data[33] != 1 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if instruction_data[33] == 1 && instruction_data.len() < 66 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.is_empty() {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].data_len() != Mint::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if mint_is_initialised_prior.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if mint_is_initialised_prior.unwrap() {
        assert_eq!(result, Err(ProgramError::Custom(6)))
    } else if accounts[0].lamports() < minimum_balance {
        assert_eq!(result, Err(ProgramError::Custom(0)))
    } else {
        assert!(get_mint(&accounts[0]).is_initialized().unwrap());
        assert_eq!(
            get_mint(&accounts[0]).mint_authority().unwrap(),
            &instruction_data[1..33]
        );
        assert_eq!(get_mint(&accounts[0]).decimals, instruction_data[0]);

        #[allow(clippy::out_of_bounds_indexing)]
        // Guard above prevents this branch TODO: Perhaps remove?
        if instruction_data[33] == 1 {
            assert_eq!(
                get_mint(&accounts[0]).freeze_authority().unwrap(),
                &instruction_data[34..66]
            );
        }
    }

    result
}

/// accounts[0]   // Multisig Info
/// accounts[1]   // Rent Sysvar Info
/// accounts[2..] // Signers
/// accounts[2..].len() // n
/// instruction_data[1] // m
#[inline(never)]
fn test_process_initialize_multisig(
    accounts: &[AccountInfo; 5],
    instruction_data: &[u8; 1],
) -> ProgramResult {
    cheatcode_is_multisig(&accounts[0]);
    cheatcode_is_rent(&accounts[1]);
    cheatcode_is_account(&accounts[2]); // Signer
    cheatcode_is_account(&accounts[3]); // Signer
    cheatcode_is_account(&accounts[4]); // Signer

    //-Initial State-----------------------------------------------------------
    let multisig_already_initialised = get_multisig(&accounts[0]).is_initialized();
    let multisig_init_lamports = accounts[0].lamports();
    let minimum_balance = get_rent(&accounts[1]).minimum_balance(accounts[0].data_len());

    //-Process Instruction-----------------------------------------------------
    let result = process_initialize_multisig(accounts, instruction_data);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.is_empty() {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.len() < 2 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[1].key() != &pinocchio::sysvars::rent::RENT_ID {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if accounts[0].data_len() != Multisig::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if multisig_already_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if multisig_already_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::Custom(6)))
    } else if multisig_init_lamports < minimum_balance {
        assert_eq!(result, Err(ProgramError::Custom(0)))
    } else if !Multisig::is_valid_signer_index((accounts.len() - 2) as u8) {
        assert_eq!(result, Err(ProgramError::Custom(7)))
    } else if !Multisig::is_valid_signer_index(instruction_data[0]) {
        assert_eq!(result, Err(ProgramError::Custom(8)))
    } else {
        assert!(accounts[2..]
            .iter()
            .map(|signer| *signer.key())
            .eq(get_multisig(&accounts[0])
                .signers
                .iter()
                .take(accounts[2..].len())
                .copied()));
        assert_eq!(get_multisig(&accounts[0]).m, instruction_data[0]);
        assert_eq!(get_multisig(&accounts[0]).n as usize, accounts.len() - 2);
        assert!(get_multisig(&accounts[0]).is_initialized().is_ok());
        assert!(get_multisig(&accounts[0]).is_initialized().unwrap());
        assert!(result.is_ok())
    }

    result
}

/// accounts[0] // Source Account Info
/// accounts[1] // Delegate Info
/// accounts[2] // Owner Info
/// instruction_data[0..8] // Little Endian Bytes of u64 amount
#[inline(never)]
fn test_process_approve(accounts: &[AccountInfo; 3], instruction_data: &[u8; 8]) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_account(&accounts[0]); // Source Account
    cheatcode_is_account(&accounts[1]); // Delegate

    //-Initial State-----------------------------------------------------------
    let amount = unsafe { u64::from_le_bytes(*(instruction_data.as_ptr() as *const [u8; 8])) };
    let src_owner = get_account(&accounts[0]).owner;
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_init_state = get_account(&accounts[0]).account_state();
    let maybe_multisig_is_initialised = None; // Value set to `None` since authority is an account

    //-Process Instruction-----------------------------------------------------
    let result = process_approve(accounts, instruction_data);

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
    } else if src_init_state.unwrap() == account_state::AccountState::Frozen {
        // This should be safe to unwrap due to above check passing
        assert_eq!(result, Err(ProgramError::Custom(17)))
    } else {
        // Validate Owner
        inner_test_validate_owner(
            &src_owner,     // expected_owner
            &accounts[2],   // owner_account_info
            &accounts[3..], // tx_signers
            maybe_multisig_is_initialised,
            result.clone(),
        )?;

        assert_eq!(
            get_account(&accounts[0]).delegate().unwrap(),
            accounts[1].key()
        );
        assert_eq!(get_account(&accounts[0]).delegated_amount(), amount);
        assert!(result.is_ok())
    }

    result
}

/// accounts[0] // Source Account Info
/// accounts[1] // Delegate Info
/// accounts[2] // Owner Info
/// accounts[3..14] // Signers
/// instruction_data[0..8] // Little Endian Bytes of u64 amount
#[inline(never)]
fn test_process_approve_multisig(
    accounts: &[AccountInfo; 4],
    instruction_data: &[u8; 8],
) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_account(&accounts[0]); // Source Account
    cheatcode_is_account(&accounts[1]); // Delegate
    cheatcode_is_multisig(&accounts[2]); // Owner

    //-Initial State-----------------------------------------------------------
    let amount = unsafe { u64::from_le_bytes(*(instruction_data.as_ptr() as *const [u8; 8])) };
    let src_owner = get_account(&accounts[0]).owner;
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_init_state = get_account(&accounts[0]).account_state();
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[2]).is_initialized());

    //-Process Instruction-----------------------------------------------------
    let result = process_approve(accounts, instruction_data);

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
    } else if src_init_state.unwrap() == account_state::AccountState::Frozen {
        // This should be safe to unwrap due to above check passing
        assert_eq!(result, Err(ProgramError::Custom(17)))
    } else {
        // Validate Owner
        inner_test_validate_owner(
            &src_owner,     // expected_owner
            &accounts[2],   // owner_account_info
            &accounts[3..], // tx_signers
            maybe_multisig_is_initialised,
            result.clone(),
        )?;

        assert_eq!(
            get_account(&accounts[0]).delegate().unwrap(),
            accounts[1].key()
        );
        assert_eq!(get_account(&accounts[0]).delegated_amount(), amount);
        assert!(result.is_ok())
    }

    result
}

/// accounts[0] // Source Account Info
/// accounts[1] // Owner Info
/// accounts[2..13] // Signers
#[inline(never)]
fn test_process_revoke(accounts: &[AccountInfo; 2]) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_account(&accounts[0]); // Source Account
    cheatcode_is_account(&accounts[1]); // Owner

    //-Initial State-----------------------------------------------------------
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_init_state = get_account(&accounts[0]).account_state();
    let src_owner = get_account(&accounts[0]).owner;
    let maybe_multisig_is_initialised = None; // Value set to `None` since authority is an account

    //-Process Instruction-----------------------------------------------------
    let result = process_revoke(accounts);

    //-Assert Postconditions---------------------------------------------------
    if accounts.is_empty() {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].data_len() != Account::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if src_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !src_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount))
    } else if accounts.len() < 2 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if src_init_state.unwrap() == account_state::AccountState::Frozen {
        assert_eq!(result, Err(ProgramError::Custom(17)))
    } else {
        // Validate Owner
        inner_test_validate_owner(
            &src_owner,     // expected_owner
            &accounts[1],   // owner_account_info
            &accounts[2..], // tx_signers
            maybe_multisig_is_initialised,
            result.clone(),
        )?;

        assert!(get_account(&accounts[0]).delegate().is_none());
        assert_eq!(get_account(&accounts[0]).delegated_amount(), 0);
        assert!(result.is_ok())
    }

    result
}

/// accounts[0] // Source Account Info
/// accounts[1] // Owner Info
/// accounts[2..13] // Signers
#[inline(never)]
fn test_process_revoke_multisig(accounts: &[AccountInfo; 3]) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_account(&accounts[0]); // Source Account
    cheatcode_is_multisig(&accounts[1]); // Owner

    //-Initial State-----------------------------------------------------------
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_init_state = get_account(&accounts[0]).account_state();
    let src_owner = get_account(&accounts[0]).owner;
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[1]).is_initialized());

    //-Process Instruction-----------------------------------------------------
    let result = process_revoke(accounts);

    //-Assert Postconditions---------------------------------------------------
    if accounts.is_empty() {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].data_len() != Account::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if src_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !src_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount))
    } else if accounts.len() < 2 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if src_init_state.unwrap() == account_state::AccountState::Frozen {
        assert_eq!(result, Err(ProgramError::Custom(17)))
    } else {
        // Validate Owner
        inner_test_validate_owner(
            &src_owner,     // expected_owner
            &accounts[1],   // owner_account_info
            &accounts[2..], // tx_signers
            maybe_multisig_is_initialised,
            result.clone(),
        )?;

        assert!(get_account(&accounts[0]).delegate().is_none());
        assert_eq!(get_account(&accounts[0]).delegated_amount(), 0);
        assert!(result.is_ok())
    }

    result
}

/// accounts[0] // Account Info - Account Case
/// accounts[1] // Authority Info
/// instruction_data[0] // Authority Type (instruction)
/// instruction_data[1] // New Authority Follows (0 -> No, 1 -> Yes)
/// instruction_data[2..34] // New Authority Pubkey
#[inline(never)]
fn test_process_set_authority_account(
    accounts: &[AccountInfo; 2],
    instruction_data: &[u8; 34],
) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_account(&accounts[0]); // Assume Account

    //-Initial State-----------------------------------------------------------
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_init_state = get_account(&accounts[0]).account_state();
    let src_owner = get_account(&accounts[0]).owner;
    let authority = get_account(&accounts[0])
        .close_authority()
        .cloned()
        .unwrap_or(get_account(&accounts[0]).owner);
    let account_data_len = accounts[0].data_len();
    let maybe_multisig_is_initialised = None; // Value set to `None` since authority is an account

    //-Process Instruction-----------------------------------------------------
    let result = process_set_authority(accounts, instruction_data);

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
    } else if account_data_len == Account::LEN {
        // established by cheatcode_is_account
        if src_initialised.is_err() {
            assert_eq!(result, Err(ProgramError::InvalidAccountData));
            return result;
        } else if !src_initialised.unwrap() {
            assert_eq!(result, Err(ProgramError::UninitializedAccount));
            return result;
        } else if src_init_state.unwrap() == account_state::AccountState::Frozen {
            assert_eq!(result, Err(ProgramError::Custom(17)));
            return result;
        } else if instruction_data[0] != 2 && instruction_data[0] != 3 {
            // AuthorityType neither AccountOwner nor CloseAccount
            assert_eq!(result, Err(ProgramError::Custom(15)));
            return result;
        } else if instruction_data[0] == 2 {
            // AccountOwner
            // Validate Owner
            inner_test_validate_owner(
                &src_owner,     // expected_owner
                &accounts[1],   // owner_account_info
                &accounts[2..], // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;

            if instruction_data[1] != 1 || instruction_data.len() < 34 {
                assert_eq!(result, Err(ProgramError::Custom(12)));
                return result;
            }

            assert_eq!(get_account(&accounts[0]).owner, instruction_data[2..34]);
            assert_eq!(get_account(&accounts[0]).delegate(), None);
            assert_eq!(get_account(&accounts[0]).delegated_amount(), 0);
            if get_account(&accounts[0]).is_native() {
                assert_eq!(get_account(&accounts[0]).close_authority(), None);
            }
            assert!(result.is_ok())
        } else {
            // CloseAccount
            assert_eq!(instruction_data[0], 3); // If not AccountOwner (2), must be CloseAccount (3)

            // Validate Owner
            inner_test_validate_owner(
                &authority,     // expected_owner
                &accounts[1],   // owner_account_info
                &accounts[2..], // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;

            if instruction_data[1] == 1 {
                // 1 ==> 34 <= instruction_data.len()
                assert_eq!(
                    get_account(&accounts[0]).close_authority().unwrap(),
                    &instruction_data[2..34]
                );
            } else {
                assert_eq!(get_account(&accounts[0]).close_authority(), None);
            }
            assert!(result.is_ok())
        }
    } else {
        unreachable!() // account_data_len == Account::LEN must hold
    }

    result
}

/// accounts[0] // Account Info - Account Case
/// accounts[1] // Authority Info
/// accounts[2..13] // Signers
/// instruction_data[0] // Authority Type (instruction)
/// instruction_data[1] // New Authority Follows (0 -> No, 1 -> Yes)
/// instruction_data[2..34] // New Authority Pubkey
#[inline(never)]
fn test_process_set_authority_account_multisig(
    accounts: &[AccountInfo; 3],
    instruction_data: &[u8; 34],
) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_account(&accounts[0]); // Assume Account
    cheatcode_is_multisig(&accounts[1]); // Authority

    //-Initial State-----------------------------------------------------------
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_init_state = get_account(&accounts[0]).account_state();
    let src_owner = get_account(&accounts[0]).owner;
    let authority = get_account(&accounts[0])
        .close_authority()
        .cloned()
        .unwrap_or(get_account(&accounts[0]).owner);
    let account_data_len = accounts[0].data_len();
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[1]).is_initialized());

    //-Process Instruction-----------------------------------------------------
    let result = process_set_authority(accounts, instruction_data);

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
    } else if account_data_len == Account::LEN {
        // established by cheatcode_is_account
        if src_initialised.is_err() {
            assert_eq!(result, Err(ProgramError::InvalidAccountData));
            return result;
        } else if !src_initialised.unwrap() {
            assert_eq!(result, Err(ProgramError::UninitializedAccount));
            return result;
        } else if src_init_state.unwrap() == account_state::AccountState::Frozen {
            assert_eq!(result, Err(ProgramError::Custom(17)));
            return result;
        } else if instruction_data[0] != 2 && instruction_data[0] != 3 {
            // AuthorityType neither AccountOwner nor CloseAccount
            assert_eq!(result, Err(ProgramError::Custom(15)));
            return result;
        } else if instruction_data[0] == 2 {
            // AccountOwner
            // Validate Owner
            inner_test_validate_owner(
                &src_owner,     // expected_owner
                &accounts[1],   // owner_account_info
                &accounts[2..], // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;

            if instruction_data[1] != 1 || instruction_data.len() < 34 {
                assert_eq!(result, Err(ProgramError::Custom(12)));
                return result;
            }

            assert_eq!(get_account(&accounts[0]).owner, instruction_data[2..34]);
            assert_eq!(get_account(&accounts[0]).delegate(), None);
            assert_eq!(get_account(&accounts[0]).delegated_amount(), 0);
            if get_account(&accounts[0]).is_native() {
                assert_eq!(get_account(&accounts[0]).close_authority(), None);
            }
            assert!(result.is_ok())
        } else {
            // CloseAccount
            assert_eq!(instruction_data[0], 3); // If not AccountOwner (2), must be CloseAccount (3)

            // Validate Owner
            inner_test_validate_owner(
                &authority,     // expected_owner
                &accounts[1],   // owner_account_info
                &accounts[2..], // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;

            if instruction_data[1] == 1 {
                // 1 ==> 34 <= instruction_data.len()
                assert_eq!(
                    get_account(&accounts[0]).close_authority().unwrap(),
                    &instruction_data[2..34]
                );
            } else {
                assert_eq!(get_account(&accounts[0]).close_authority(), None);
            }
            assert!(result.is_ok())
        }
    } else {
        unreachable!() // account_data_len == Account::LEN must hold
    }

    result
}

/// accounts[0] // Account Info - Mint Case
/// accounts[1] // Authority Info
/// instruction_data[0] // Authority Type (instruction)
/// instruction_data[1] // New Authority Follows (0 -> No, 1 -> Yes)
/// instruction_data[2..34] // New Authority Pubkey
#[inline(never)]
fn test_process_set_authority_mint(
    accounts: &[AccountInfo; 2],
    instruction_data: &[u8; 34],
) -> ProgramResult {
    cheatcode_is_mint(&accounts[0]); // Assume Mint
    cheatcode_is_account(&accounts[1]); // Authority

    //-Initial State-----------------------------------------------------------
    let mint_data_len = accounts[0].data_len();
    let old_mint_authority_is_none = get_mint(&accounts[0]).mint_authority().is_none();
    let old_freeze_authority_is_none = get_mint(&accounts[0]).freeze_authority().is_none();
    let old_mint_authority = get_mint(&accounts[0]).mint_authority().cloned();
    let old_freeze_authority = get_mint(&accounts[0]).freeze_authority().cloned();
    let maybe_multisig_is_initialised = None; // Value set to `None` since authority is an account
    let mint_is_initialised = get_mint(&accounts[0]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = process_set_authority(accounts, instruction_data);

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
    } else if mint_data_len == Mint::LEN {
        // established by cheatcode_is_mint
        if !mint_is_initialised.unwrap() {
            assert_eq!(result, Err(ProgramError::UninitializedAccount));
            return result;
        } else if instruction_data[0] != 0 && instruction_data[0] != 1 {
            // AuthorityType neither MintTokens nor FreezeAccount
            assert_eq!(result, Err(ProgramError::Custom(15)));
            return result;
        } else if instruction_data[0] == 0 {
            // MintTokens
            if old_mint_authority_is_none {
                assert_eq!(result, Err(ProgramError::Custom(5)));
                return result;
            }

            // Validate Owner
            inner_test_validate_owner(
                &old_mint_authority.unwrap(), // expected_owner
                &accounts[1],                 // owner_account_info
                &accounts[2..],               // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;

            if instruction_data[1] == 1 {
                // 1 ==> 34 <= instruction_data.len()
                assert_eq!(
                    get_mint(&accounts[0]).mint_authority().unwrap(),
                    &instruction_data[2..34]
                );
            } else {
                assert_eq!(get_mint(&accounts[0]).mint_authority(), None);
            }
            assert!(result.is_ok())
        } else {
            // FreezeAccount
            assert_eq!(instruction_data[0], 1); // If not MintTokens (0), must be FreezeAccount (1)
            if old_freeze_authority_is_none {
                assert_eq!(result, Err(ProgramError::Custom(16)));
                return result;
            }

            // Validate Owner
            inner_test_validate_owner(
                &old_freeze_authority.unwrap(), // expected_owner
                &accounts[1],                   // owner_account_info
                &accounts[2..],                 // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;

            if instruction_data[1] == 1 {
                // 1 ==> 34 <= instruction_data.len()
                assert_eq!(
                    get_mint(&accounts[0]).freeze_authority().unwrap(),
                    &instruction_data[2..34]
                );
            } else {
                assert_eq!(get_mint(&accounts[0]).freeze_authority(), None);
            }
            assert!(result.is_ok())
        }
    } else {
        unreachable!(); // mint_data_len == Mint::LEN must hold
    }

    result
}

/// accounts[0] // Account Info - Mint Case
/// accounts[1] // Authority Info
/// accounts[2..13] // Signers
/// instruction_data[0] // Authority Type (instruction)
/// instruction_data[1] // New Authority Follows (0 -> No, 1 -> Yes)
/// instruction_data[2..34] // New Authority Pubkey
#[inline(never)]
fn test_process_set_authority_mint_multisig(
    accounts: &[AccountInfo; 3],
    instruction_data: &[u8; 34],
) -> ProgramResult {
    cheatcode_is_mint(&accounts[0]); // Assume Mint
    cheatcode_is_multisig(&accounts[1]); // Authority

    //-Initial State-----------------------------------------------------------
    let mint_data_len = accounts[0].data_len();
    let old_mint_authority_is_none = get_mint(&accounts[0]).mint_authority().is_none();
    let old_freeze_authority_is_none = get_mint(&accounts[0]).freeze_authority().is_none();
    let old_mint_authority = get_mint(&accounts[0]).mint_authority().cloned();
    let old_freeze_authority = get_mint(&accounts[0]).freeze_authority().cloned();
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[1]).is_initialized());
    let mint_is_initialised = get_mint(&accounts[0]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = process_set_authority(accounts, instruction_data);

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
    } else if mint_data_len == Mint::LEN {
        // established by cheatcode_is_mint
        if !mint_is_initialised.unwrap() {
            assert_eq!(result, Err(ProgramError::UninitializedAccount));
            return result;
        } else if instruction_data[0] != 0 && instruction_data[0] != 1 {
            // AuthorityType neither MintTokens nor FreezeAccount
            assert_eq!(result, Err(ProgramError::Custom(15)));
            return result;
        } else if instruction_data[0] == 0 {
            // MintTokens
            if old_mint_authority_is_none {
                assert_eq!(result, Err(ProgramError::Custom(5)));
                return result;
            }

            // Validate Owner
            inner_test_validate_owner(
                &old_mint_authority.unwrap(), // expected_owner
                &accounts[1],                 // owner_account_info
                &accounts[2..],               // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;

            if instruction_data[1] == 1 {
                // 1 ==> 34 <= instruction_data.len()
                assert_eq!(
                    get_mint(&accounts[0]).mint_authority().unwrap(),
                    &instruction_data[2..34]
                );
            } else {
                assert_eq!(get_mint(&accounts[0]).mint_authority(), None);
            }
            assert!(result.is_ok())
        } else {
            // FreezeAccount
            assert_eq!(instruction_data[0], 1); // If not MintTokens (0), must be FreezeAccount (1)
            if old_freeze_authority_is_none {
                assert_eq!(result, Err(ProgramError::Custom(16)));
                return result;
            }

            // Validate Owner
            inner_test_validate_owner(
                &old_freeze_authority.unwrap(), // expected_owner
                &accounts[1],                   // owner_account_info
                &accounts[2..],                 // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;

            if instruction_data[1] == 1 {
                // 1 ==> 34 <= instruction_data.len()
                assert_eq!(
                    get_mint(&accounts[0]).freeze_authority().unwrap(),
                    &instruction_data[2..34]
                );
            } else {
                assert_eq!(get_mint(&accounts[0]).freeze_authority(), None);
            }
            assert!(result.is_ok())
        }
    } else {
        unreachable!(); // mint_data_len == Mint::LEN must hold
    }

    result
}

/// accounts[0] // Source Account Info
/// accounts[1] // Mint Info
/// accounts[2] // Authority Info
#[inline(never)]
fn test_process_freeze_account(accounts: &[AccountInfo; 3]) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_account(&accounts[0]);
    cheatcode_is_mint(&accounts[1]);

    //-Initial State-----------------------------------------------------------
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_init_state = get_account(&accounts[0]).account_state();
    let src_is_native = get_account(&accounts[0]).is_native();
    let src_mint = get_account(&accounts[0]).mint;
    let mint_initialised = get_mint(&accounts[1]).is_initialized();
    let mint_freeze_auth = get_mint(&accounts[1]).freeze_authority().cloned();
    let maybe_multisig_is_initialised = None; // Value set to `None` since authority is an account

    //-Process Instruction-----------------------------------------------------
    let result = process_freeze_account(accounts);

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
    } else if src_init_state.unwrap() == account_state::AccountState::Frozen {
        assert_eq!(result, Err(ProgramError::Custom(13)))
    } else if src_is_native {
        assert_eq!(result, Err(ProgramError::Custom(10)))
    } else if accounts[1].key() != &src_mint {
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
        // Validate Owner
        inner_test_validate_owner(
            &mint_freeze_auth.unwrap(), // expected_owner
            &accounts[2],               // owner_account_info
            &accounts[3..],             // tx_signers
            maybe_multisig_is_initialised,
            result.clone(),
        )?;

        assert_eq!(
            get_account(&accounts[0]).account_state().unwrap(),
            account_state::AccountState::Frozen
        );
        assert!(result.is_ok())
    }
    result
}

/// accounts[0] // Source Account Info
/// accounts[1] // Mint Info
/// accounts[2] // Authority Info
/// accounts[3..13] // Signers
#[inline(never)]
fn test_process_freeze_account_multisig(accounts: &[AccountInfo; 4]) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_account(&accounts[0]);
    cheatcode_is_mint(&accounts[1]);
    cheatcode_is_multisig(&accounts[2]);

    //-Initial State-----------------------------------------------------------
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_init_state = get_account(&accounts[0]).account_state();
    let src_is_native = get_account(&accounts[0]).is_native();
    let src_mint = get_account(&accounts[0]).mint;
    let mint_initialised = get_mint(&accounts[1]).is_initialized();
    let mint_freeze_auth = get_mint(&accounts[1]).freeze_authority().cloned();
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[2]).is_initialized());

    //-Process Instruction-----------------------------------------------------
    let result = process_freeze_account(accounts);

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
    } else if src_init_state.unwrap() == account_state::AccountState::Frozen {
        assert_eq!(result, Err(ProgramError::Custom(13)))
    } else if src_is_native {
        assert_eq!(result, Err(ProgramError::Custom(10)))
    } else if accounts[1].key() != &src_mint {
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
        // Validate Owner
        inner_test_validate_owner(
            &mint_freeze_auth.unwrap(), // expected_owner
            &accounts[2],               // owner_account_info
            &accounts[3..],             // tx_signers
            maybe_multisig_is_initialised,
            result.clone(),
        )?;

        assert_eq!(
            get_account(&accounts[0]).account_state().unwrap(),
            account_state::AccountState::Frozen
        );
        assert!(result.is_ok())
    }
    result
}

/// accounts[0] // Source Account Info
/// accounts[1] // Mint Info
/// accounts[2] // Authority Info
/// accounts[3..13] // Signers
#[inline(never)]
fn test_process_thaw_account(accounts: &[AccountInfo; 3]) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_account(&accounts[0]);
    cheatcode_is_mint(&accounts[1]);

    //-Initial State-----------------------------------------------------------
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_init_state = get_account(&accounts[0]).account_state();
    let src_is_native = get_account(&accounts[0]).is_native();
    let src_mint = get_account(&accounts[0]).mint;
    let mint_initialised = get_mint(&accounts[1]).is_initialized();
    let mint_freeze_auth = get_mint(&accounts[1]).freeze_authority().cloned();
    let maybe_multisig_is_initialised = None; // Value set to `None` since authority is an account

    //-Process Instruction-----------------------------------------------------
    let result = process_thaw_account(accounts);

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
    } else if src_init_state.unwrap() != account_state::AccountState::Frozen {
        assert_eq!(result, Err(ProgramError::Custom(13)))
    } else if src_is_native {
        assert_eq!(result, Err(ProgramError::Custom(10)))
    } else if accounts[1].key() != &src_mint {
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
        // Validate Owner
        inner_test_validate_owner(
            &mint_freeze_auth.unwrap(), // expected_owner
            &accounts[2],               // owner_account_info
            &accounts[3..],             // tx_signers
            maybe_multisig_is_initialised,
            result.clone(),
        )?;

        assert_eq!(
            get_account(&accounts[0]).account_state().unwrap(),
            account_state::AccountState::Initialized
        );
        assert!(result.is_ok())
    }
    result
}

/// accounts[0] // Source Account Info
/// accounts[1] // Mint Info
/// accounts[2] // Authority Info
/// accounts[3..13] // Signers
#[inline(never)]
fn test_process_thaw_account_multisig(accounts: &[AccountInfo; 4]) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_account(&accounts[0]);
    cheatcode_is_mint(&accounts[1]);
    cheatcode_is_multisig(&accounts[2]);

    //-Initial State-----------------------------------------------------------
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_init_state = get_account(&accounts[0]).account_state();
    let src_is_native = get_account(&accounts[0]).is_native();
    let src_mint = get_account(&accounts[0]).mint;
    let mint_initialised = get_mint(&accounts[1]).is_initialized();
    let mint_freeze_auth = get_mint(&accounts[1]).freeze_authority().cloned();
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[2]).is_initialized());

    //-Process Instruction-----------------------------------------------------
    let result = process_thaw_account(accounts);

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
    } else if src_init_state.unwrap() != account_state::AccountState::Frozen {
        assert_eq!(result, Err(ProgramError::Custom(13)))
    } else if src_is_native {
        assert_eq!(result, Err(ProgramError::Custom(10)))
    } else if accounts[1].key() != &src_mint {
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
        // Validate Owner
        inner_test_validate_owner(
            &mint_freeze_auth.unwrap(), // expected_owner
            &accounts[2],               // owner_account_info
            &accounts[3..],             // tx_signers
            maybe_multisig_is_initialised,
            result.clone(),
        )?;

        assert_eq!(
            get_account(&accounts[0]).account_state().unwrap(),
            account_state::AccountState::Initialized
        );
        assert!(result.is_ok())
    }
    result
}

/// accounts[0] // Source Account Info
/// accounts[1] // Expected Mint Info
/// accounts[2] // Delegate Info
/// accounts[3] // Owner Info
/// instruction_data[0..9] // Little Endian Bytes of u64 amount, and decimals
#[inline(never)]
fn test_process_approve_checked(
    accounts: &[AccountInfo; 4],
    instruction_data: &[u8; 9],
) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_account(&accounts[0]); // Source Account
    cheatcode_is_mint(&accounts[1]); // Expected Mint
    cheatcode_is_account(&accounts[2]); // Delegate

    //-Initial State-----------------------------------------------------------
    let amount = unsafe { u64::from_le_bytes(*(instruction_data.as_ptr() as *const [u8; 8])) };
    let src_owner = get_account(&accounts[0]).owner;
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_init_state = get_account(&accounts[0]).account_state();
    let mint_initialised = get_mint(&accounts[1]).is_initialized();
    let maybe_multisig_is_initialised = None; // Value set to `None` since authority is an account

    //-Process Instruction-----------------------------------------------------
    let result = process_approve_checked(accounts, instruction_data);

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
    } else if src_init_state.unwrap() == account_state::AccountState::Frozen {
        // This should be safe to unwrap due to above check passing
        assert_eq!(result, Err(ProgramError::Custom(17)))
    } else if accounts[1].key() != &get_account(&accounts[0]).mint {
        assert_eq!(result, Err(ProgramError::Custom(3)))
    } else if accounts[1].data_len() != Mint::LEN {
        // Not sure if this is even possible if we get past the case above
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if mint_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !mint_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount))
    } else if instruction_data[8] != get_mint(&accounts[1]).decimals {
        assert_eq!(result, Err(ProgramError::Custom(18)))
    } else {
        // Validate Owner
        inner_test_validate_owner(
            &src_owner,     // expected_owner
            &accounts[3],   // owner_account_info
            &accounts[4..], // tx_signers
            maybe_multisig_is_initialised,
            result.clone(),
        )?;

        assert_eq!(
            get_account(&accounts[0]).delegate().unwrap(),
            accounts[2].key()
        );
        assert_eq!(get_account(&accounts[0]).delegated_amount(), amount);
        assert!(result.is_ok())
    }

    result
}

/// accounts[0] // Source Account Info
/// accounts[1] // Expected Mint Info
/// accounts[2] // Delegate Info
/// accounts[3] // Owner Info
/// accounts[4..15] // Signers
/// instruction_data[0..9] // Little Endian Bytes of u64 amount, and decimals
#[inline(never)]
fn test_process_approve_checked_multisig(
    accounts: &[AccountInfo; 5],
    instruction_data: &[u8; 9],
) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_account(&accounts[0]); // Source Account
    cheatcode_is_mint(&accounts[1]); // Expected Mint
    cheatcode_is_account(&accounts[2]); // Delegate
    cheatcode_is_multisig(&accounts[3]); // Owner

    //-Initial State-----------------------------------------------------------
    let amount = unsafe { u64::from_le_bytes(*(instruction_data.as_ptr() as *const [u8; 8])) };
    let src_owner = get_account(&accounts[0]).owner;
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_init_state = get_account(&accounts[0]).account_state();
    let mint_initialised = get_mint(&accounts[1]).is_initialized();
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[3]).is_initialized());

    //-Process Instruction-----------------------------------------------------
    let result = process_approve_checked(accounts, instruction_data);

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
    } else if src_init_state.unwrap() == account_state::AccountState::Frozen {
        // This should be safe to unwrap due to above check passing
        assert_eq!(result, Err(ProgramError::Custom(17)))
    } else if accounts[1].key() != &get_account(&accounts[0]).mint {
        assert_eq!(result, Err(ProgramError::Custom(3)))
    } else if accounts[1].data_len() != Mint::LEN {
        // Not sure if this is even possible if we get past the case above
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if mint_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !mint_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount))
    } else if instruction_data[8] != get_mint(&accounts[1]).decimals {
        assert_eq!(result, Err(ProgramError::Custom(18)))
    } else {
        // Validate Owner
        inner_test_validate_owner(
            &src_owner,     // expected_owner
            &accounts[3],   // owner_account_info
            &accounts[4..], // tx_signers
            maybe_multisig_is_initialised,
            result.clone(),
        )?;

        assert_eq!(
            get_account(&accounts[0]).delegate().unwrap(),
            accounts[2].key()
        );
        assert_eq!(get_account(&accounts[0]).delegated_amount(), amount);
        assert!(result.is_ok())
    }

    result
}

/// accounts[0] // Mint Info
/// accounts[1] // Destination Info
/// accounts[2] // Owner Info
/// instruction_data[0..9] // Little Endian Bytes of u64 amount, and decimals
#[inline(never)]
fn test_process_mint_to_checked(
    accounts: &[AccountInfo; 3],
    instruction_data: &[u8; 9],
) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_mint(&accounts[0]);
    cheatcode_is_account(&accounts[1]);

    //-Initial State-----------------------------------------------------------
    let initial_supply = get_mint(&accounts[0]).supply();
    let initial_amount = get_account(&accounts[1]).amount();
    let mint_initialised = get_mint(&accounts[0]).is_initialized();
    let dst_initialised = get_account(&accounts[1]).is_initialized();
    let dst_init_state = get_account(&accounts[1]).account_state();
    let maybe_multisig_is_initialised = None; // Value set to `None` since authority is an account

    //-Process Instruction-----------------------------------------------------
    let result = process_mint_to_checked(accounts, instruction_data);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < 9 {
        assert_eq!(result, Err(ProgramError::Custom(12)));
        return result;
    } else if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else if accounts[1].data_len() != Account::LEN {
        // TODO Daniel: is it possible for something to be provided that has the same
        // len but is not an account?
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if dst_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if !dst_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount));
        return result;
    } else if dst_init_state.unwrap() == account_state::AccountState::Frozen {
        // unwrap must succeed due to dst_initialised not being err
        assert_eq!(result, Err(ProgramError::Custom(17)));
        return result;
    } else if get_account(&accounts[1]).is_native() {
        assert_eq!(result, Err(ProgramError::Custom(10)));
        return result;
    } else if accounts[0].key() != &get_account(&accounts[1]).mint {
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
    } else if instruction_data[8] != get_mint(&accounts[0]).decimals {
        assert_eq!(result, Err(ProgramError::Custom(18)));
        return result;
    } else {
        if get_mint(&accounts[0]).mint_authority().is_some() {
            // Validate Owner
            inner_test_validate_owner(
                get_mint(&accounts[0]).mint_authority().unwrap(), // expected_owner
                &accounts[2],                                     // owner_account_info
                &accounts[3..],                                   // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;
        } else {
            assert_eq!(result, Err(ProgramError::Custom(5)));
            return result;
        }

        let amount = unsafe { u64::from_le_bytes(*(instruction_data.as_ptr() as *const [u8; 8])) };

        if amount == 0 && accounts[0].owner() != &pinocchio_token_interface::program::ID {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId));
            return result;
        } else if amount == 0 && accounts[1].owner() != &pinocchio_token_interface::program::ID {
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

    result
}

/// accounts[0] // Mint Info
/// accounts[1] // Destination Info
/// accounts[2] // Owner Info
/// accounts[3..14] // Signers
/// instruction_data[0..9] // Little Endian Bytes of u64 amount, and decimals
#[inline(never)]
fn test_process_mint_to_checked_multisig(
    accounts: &[AccountInfo; 4],
    instruction_data: &[u8; 9],
) -> ProgramResult {
    use pinocchio_token_interface::state::account_state;

    cheatcode_is_mint(&accounts[0]);
    cheatcode_is_account(&accounts[1]);
    cheatcode_is_multisig(&accounts[2]);

    //-Initial State-----------------------------------------------------------
    let initial_supply = get_mint(&accounts[0]).supply();
    let initial_amount = get_account(&accounts[1]).amount();
    let mint_initialised = get_mint(&accounts[0]).is_initialized();
    let dst_initialised = get_account(&accounts[1]).is_initialized();
    let dst_init_state = get_account(&accounts[1]).account_state();
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[2]).is_initialized());

    //-Process Instruction-----------------------------------------------------
    let result = process_mint_to_checked(accounts, instruction_data);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < 9 {
        assert_eq!(result, Err(ProgramError::Custom(12)));
        return result;
    } else if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else if accounts[1].data_len() != Account::LEN {
        // TODO Daniel: is it possible for something to be provided that has the same
        // len but is not an account?
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if dst_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if !dst_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount));
        return result;
    } else if dst_init_state.unwrap() == account_state::AccountState::Frozen {
        // unwrap must succeed due to dst_initialised not being err
        assert_eq!(result, Err(ProgramError::Custom(17)));
        return result;
    } else if get_account(&accounts[1]).is_native() {
        assert_eq!(result, Err(ProgramError::Custom(10)));
        return result;
    } else if accounts[0].key() != &get_account(&accounts[1]).mint {
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
    } else if instruction_data[8] != get_mint(&accounts[0]).decimals {
        assert_eq!(result, Err(ProgramError::Custom(18)));
        return result;
    } else {
        if get_mint(&accounts[0]).mint_authority().is_some() {
            // Validate Owner
            inner_test_validate_owner(
                get_mint(&accounts[0]).mint_authority().unwrap(), // expected_owner
                &accounts[2],                                     // owner_account_info
                &accounts[3..],                                   // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;
        } else {
            assert_eq!(result, Err(ProgramError::Custom(5)));
            return result;
        }

        let amount = unsafe { u64::from_le_bytes(*(instruction_data.as_ptr() as *const [u8; 8])) };

        if amount == 0 && accounts[0].owner() != &pinocchio_token_interface::program::ID {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId));
            return result;
        } else if amount == 0 && accounts[1].owner() != &pinocchio_token_interface::program::ID {
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

    result
}

#[inline(never)]
fn test_process_sync_native(accounts: &[AccountInfo; 1]) -> ProgramResult {
    use pinocchio_token_interface::program;

    cheatcode_is_account(&accounts[0]);

    //-Initial State-----------------------------------------------------------
    let src_owner = accounts[0].owner();
    let src_initialised = get_account(&accounts[0]).is_initialized();
    let src_native_amount = get_account(&accounts[0]).native_amount();
    let src_init_lamports = accounts[0].lamports();
    let src_init_amount = get_account(&accounts[0]).amount();

    //-Process Instruction-----------------------------------------------------
    let result = process_sync_native(accounts);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() != 1 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if src_owner != &program::ID {
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
        assert_eq!(
            get_account(&accounts[0]).amount(),
            src_init_lamports - src_native_amount.unwrap()
        );
        assert!(result.is_ok())
    }
    result
}

/// accounts[0]   // Multisig Info
/// accounts[1..] // Signers
/// accounts[1..].len() // n
/// instruction_data[1] // m
#[inline(never)]
fn test_process_initialize_multisig2(
    accounts: &[AccountInfo; 4],
    instruction_data: &[u8; 1],
) -> ProgramResult {
    cheatcode_is_multisig(&accounts[0]);
    cheatcode_is_account(&accounts[1]); // Signer
    cheatcode_is_account(&accounts[2]); // Signer
    cheatcode_is_account(&accounts[3]); // Signer

    //-Initial State-----------------------------------------------------------
    let multisig_already_initialised = get_multisig(&accounts[0]).is_initialized();
    let multisig_init_lamports = accounts[0].lamports();
    // Note: Rent is a supported sysvar so ProgramError::UnsupportedSysvar should be
    // impossible
    let rent = pinocchio::sysvars::rent::Rent::get().unwrap();
    let minimum_balance = rent.minimum_balance(accounts[0].data_len());

    //-Process Instruction-----------------------------------------------------
    let result = process_initialize_multisig2(accounts, instruction_data);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.is_empty() {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.is_empty() {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].data_len() != Multisig::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if multisig_already_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if multisig_already_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::Custom(6)))
    } else if multisig_init_lamports < minimum_balance {
        assert_eq!(result, Err(ProgramError::Custom(0)))
    } else if !Multisig::is_valid_signer_index((accounts.len() - 1) as u8) {
        assert_eq!(result, Err(ProgramError::Custom(7)))
    } else if !Multisig::is_valid_signer_index(instruction_data[0]) {
        assert_eq!(result, Err(ProgramError::Custom(8)))
    } else {
        assert!(accounts[1..]
            .iter()
            .map(|signer| *signer.key())
            .eq(get_multisig(&accounts[0])
                .signers
                .iter()
                .take(accounts[1..].len())
                .copied()));
        assert_eq!(get_multisig(&accounts[0]).m, instruction_data[0]);
        assert_eq!(get_multisig(&accounts[0]).n as usize, accounts.len() - 1);
        assert!(get_multisig(&accounts[0]).is_initialized().is_ok());
        assert!(get_multisig(&accounts[0]).is_initialized().unwrap());
        assert!(result.is_ok())
    }

    result
}

/// accounts[0] // Mint Info
#[inline(never)]
fn test_process_get_account_data_size(accounts: &[AccountInfo; 1]) -> ProgramResult {
    cheatcode_is_mint(&accounts[0]);

    //-Initial State-----------------------------------------------------------
    let mint_initialised = get_mint(&accounts[0]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = process_get_account_data_size(accounts);

    //-Assert Postconditions---------------------------------------------------
    if accounts.is_empty() {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].owner() != &pinocchio_token_interface::program::ID {
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
    result
}

#[inline(never)]
fn test_process_initialize_immutable_owner(accounts: &[AccountInfo; 1]) -> ProgramResult {
    cheatcode_is_account(&accounts[0]);

    //-Initial State-----------------------------------------------------------
    let src_initialised = get_account(&accounts[0]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = process_initialize_immutable_owner(accounts);

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
    result
}

#[inline(never)]
fn test_process_amount_to_ui_amount(
    accounts: &[AccountInfo; 1],
    instruction_data: &[u8; 8],
) -> ProgramResult {
    cheatcode_is_mint(&accounts[0]);

    //-Initial State-----------------------------------------------------------
    let mint_initialised = get_mint(&accounts[0]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = process_amount_to_ui_amount(accounts, instruction_data);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < 8 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.is_empty() {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].owner() != &pinocchio_token_interface::program::ID {
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
    result
}

#[inline(never)]
fn test_process_ui_amount_to_amount(
    accounts: &[AccountInfo; 1],
    instruction_data: &[u8],
) -> ProgramResult {
    cheatcode_is_mint(&accounts[0]);

    //-Initial State-----------------------------------------------------------
    let ui_amount = core::str::from_utf8(instruction_data);
    let mint_initialised = get_mint(&accounts[0]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = process_ui_amount_to_amount(accounts, instruction_data);

    //-Assert Postconditions---------------------------------------------------
    // TODO: validations module is private, so we need a work around
    if ui_amount.is_err() {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.is_empty() {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].owner() != &pinocchio_token_interface::program::ID {
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
    } else if ui_amount.unwrap().starts_with('.')
        && ui_amount.unwrap().chars().skip(1).all(|c| c == '0')
    {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if ui_amount.unwrap().split_once('.').is_some_and(|(_, frac)| {
        (get_mint(&accounts[0]).decimals as usize) < frac.trim_end_matches('0').len()
    }) {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if ui_amount.unwrap().split_once('.').map_or(
        257_usize < ui_amount.unwrap().len() + (get_mint(&accounts[0]).decimals as usize),
        |(ints, _)| 257_usize < ints.len() + (get_mint(&accounts[0]).decimals as usize),
    ) {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    }
    /*else if ui_amount.unwrap() == "+." {
        // TODO: Why is this valid?
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if ui_amount.unwrap() == "+" {
        // TODO: Why is this valid?
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    }*/
    else if ui_amount.unwrap().starts_with('-') {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if ui_amount
        .unwrap()
        .contains(|c: char| !c.is_ascii_digit() && c != '+' && c != '.')
    {
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
            let lo = if hi.is_empty() {
                fracs.trim_start_matches('0')
            } else {
                fracs
            };

            let total_len = hi.len() + lo.len();

            match total_len.cmp(&MAX_VAL.len()) {
                core::cmp::Ordering::Less => false,
                core::cmp::Ordering::Greater => true,
                core::cmp::Ordering::Equal => {
                    if hi.len() > MAX_VAL.len() {
                        return true;
                    }
                    let (max_hi, max_lo) = MAX_VAL.split_at(hi.len());
                    hi > max_hi || (hi == max_hi && lo > max_lo)
                }
            }
        },
    ) {
        // TODO: What is going on ??? Need to fix
        // assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else {
        assert!(result.is_ok())
    }
    result
}

/// accounts[0] // Source Account Info (Account)
/// accounts[1] // Destination Info
/// accounts[2] // Authority Info
#[inline(never)]
fn test_process_withdraw_excess_lamports_account(accounts: &[AccountInfo; 3]) -> ProgramResult {
    cheatcode_is_account(&accounts[0]); // Source Account
    cheatcode_is_account(&accounts[1]); // Destination

    //-Initial State-----------------------------------------------------------
    let src_data_len = accounts[0].data_len();
    let src_account_initialised = get_account(&accounts[0]).is_initialized();
    let src_account_owner = get_account(&accounts[0]).owner;
    let src_account_is_native = get_account(&accounts[0]).is_native();
    let src_init_lamports = accounts[0].lamports();
    let dst_init_lamports = accounts[1].lamports();
    let maybe_multisig_is_initialised = None; // Value set to `None` since authority is an account

    // Note: Rent is a supported sysvar so ProgramError::UnsupportedSysvar should be
    // impossible
    let rent = pinocchio::sysvars::rent::Rent::get().unwrap();
    let minimum_balance = rent.minimum_balance(accounts[0].data_len());

    //-Process Instruction-----------------------------------------------------
    let result = process_withdraw_excess_lamports(accounts);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else {
        assert_eq!(src_data_len, Account::LEN); // established by cheatcode_is_account
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

            // Validate Owner
            inner_test_validate_owner(
                &src_account_owner, // expected_owner
                &accounts[2],       // owner_account_info
                &accounts[3..],     // tx_signers
                maybe_multisig_is_initialised,
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
            assert_eq!(
                accounts[1].lamports(),
                dst_init_lamports + src_init_lamports - minimum_balance
            );
            assert!(result.is_ok())
        }
    }

    result
}

/// accounts[0] // Source Account Info (Account)
/// accounts[1] // Destination Info
/// accounts[2] // Authority Info
/// accounts[3..14] // Signers
#[inline(never)]
fn test_process_withdraw_excess_lamports_account_multisig(
    accounts: &[AccountInfo; 4],
) -> ProgramResult {
    cheatcode_is_account(&accounts[0]); // Source Account
    cheatcode_is_account(&accounts[1]); // Destination
    cheatcode_is_multisig(&accounts[2]); // Authority

    //-Initial State-----------------------------------------------------------
    let src_data_len = accounts[0].data_len();
    let src_account_initialised = get_account(&accounts[0]).is_initialized();
    let src_account_owner = get_account(&accounts[0]).owner;
    let src_account_is_native = get_account(&accounts[0]).is_native();
    let src_init_lamports = accounts[0].lamports();
    let dst_init_lamports = accounts[1].lamports();
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[2]).is_initialized());

    // Note: Rent is a supported sysvar so ProgramError::UnsupportedSysvar should be
    // impossible
    let rent = pinocchio::sysvars::rent::Rent::get().unwrap();
    let minimum_balance = rent.minimum_balance(accounts[0].data_len());

    //-Process Instruction-----------------------------------------------------
    let result = process_withdraw_excess_lamports(accounts);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else {
        assert_eq!(src_data_len, Account::LEN); // established by cheatcode_is_account
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

            // Validate Owner
            inner_test_validate_owner(
                &src_account_owner, // expected_owner
                &accounts[2],       // owner_account_info
                &accounts[3..],     // tx_signers
                maybe_multisig_is_initialised,
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
            assert_eq!(
                accounts[1].lamports(),
                dst_init_lamports + src_init_lamports - minimum_balance
            );
            assert!(result.is_ok())
        }
    }

    result
}

/// accounts[0] // Source Account Info (Mint)
/// accounts[1] // Destination Info
/// accounts[2] // Authority Info
#[inline(never)]
fn test_process_withdraw_excess_lamports_mint(accounts: &[AccountInfo; 3]) -> ProgramResult {
    cheatcode_is_mint(&accounts[0]); // Source Account (Mint)
    cheatcode_is_account(&accounts[1]); // Destination

    //-Initial State-----------------------------------------------------------
    let src_data_len = accounts[0].data_len();
    let src_mint_initialised = get_mint(&accounts[0]).is_initialized();
    let src_mint_mint_authority = get_mint(&accounts[0]).mint_authority().cloned();
    let src_init_lamports = accounts[0].lamports();
    let dst_init_lamports = accounts[1].lamports();
    let maybe_multisig_is_initialised = None; // Value set to `None` since authority is an account

    // Note: Rent is a supported sysvar so ProgramError::UnsupportedSysvar should be
    // impossible
    let rent = pinocchio::sysvars::rent::Rent::get().unwrap();
    let minimum_balance = rent.minimum_balance(accounts[0].data_len());

    //-Process Instruction-----------------------------------------------------
    let result = process_withdraw_excess_lamports(accounts);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else {
        assert_eq!(src_data_len, Mint::LEN); // established by cheatcode_is_mint
        {
            if src_mint_initialised.is_err() {
                assert_eq!(result, Err(ProgramError::InvalidAccountData));
                return result;
            } else if !src_mint_initialised.unwrap() {
                assert_eq!(result, Err(ProgramError::UninitializedAccount));
                return result;
            } else if src_mint_mint_authority.is_some() {
                // Validate Owner
                inner_test_validate_owner(
                    &src_mint_mint_authority.unwrap(), // expected_owner
                    &accounts[2],                      // owner_account_info
                    &accounts[3..],                    // tx_signers
                    maybe_multisig_is_initialised,
                    result.clone(),
                )?;
            } else if accounts[0] != accounts[2] {
                assert_eq!(result, Err(ProgramError::Custom(15)));
                return result;
            } else if !accounts[2].is_signer() {
                assert_eq!(result, Err(ProgramError::MissingRequiredSignature));
                return result;
            } else if src_init_lamports < minimum_balance {
                assert_eq!(result, Err(ProgramError::Custom(0)));
                return result;
            } else if u64::MAX - src_init_lamports + minimum_balance < dst_init_lamports {
                assert_eq!(result, Err(ProgramError::Custom(0)));
                return result;
            }

            assert_eq!(accounts[0].lamports(), minimum_balance);
            assert_eq!(
                accounts[1].lamports(),
                dst_init_lamports + src_init_lamports - minimum_balance
            );
            assert!(result.is_ok())
        }
    }

    result
}

/// accounts[0] // Source Account Info (Mint)
/// accounts[1] // Destination Info
/// accounts[2] // Authority Info
/// accounts[3..14] // Signers
#[inline(never)]
fn test_process_withdraw_excess_lamports_mint_multisig(
    accounts: &[AccountInfo; 4],
) -> ProgramResult {
    cheatcode_is_mint(&accounts[0]); // Source Account (Mint)
    cheatcode_is_account(&accounts[1]); // Destination
    cheatcode_is_multisig(&accounts[2]); // Authority

    //-Initial State-----------------------------------------------------------
    let src_data_len = accounts[0].data_len();
    let src_mint_initialised = get_mint(&accounts[0]).is_initialized();
    let src_mint_mint_authority = get_mint(&accounts[0]).mint_authority().cloned();
    let src_init_lamports = accounts[0].lamports();
    let dst_init_lamports = accounts[1].lamports();
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[2]).is_initialized());

    // Note: Rent is a supported sysvar so ProgramError::UnsupportedSysvar should be
    // impossible
    let rent = pinocchio::sysvars::rent::Rent::get().unwrap();
    let minimum_balance = rent.minimum_balance(accounts[0].data_len());

    //-Process Instruction-----------------------------------------------------
    let result = process_withdraw_excess_lamports(accounts);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else {
        assert_eq!(src_data_len, Mint::LEN); // established by cheatcode_is_mint
        {
            if src_mint_initialised.is_err() {
                assert_eq!(result, Err(ProgramError::InvalidAccountData));
                return result;
            } else if !src_mint_initialised.unwrap() {
                assert_eq!(result, Err(ProgramError::UninitializedAccount));
                return result;
            } else if src_mint_mint_authority.is_some() {
                // Validate Owner
                inner_test_validate_owner(
                    &src_mint_mint_authority.unwrap(), // expected_owner
                    &accounts[2],                      // owner_account_info
                    &accounts[3..],                    // tx_signers
                    maybe_multisig_is_initialised,
                    result.clone(),
                )?;
            } else if accounts[0] != accounts[2] {
                assert_eq!(result, Err(ProgramError::Custom(15)));
                return result;
            } else if !accounts[2].is_signer() {
                assert_eq!(result, Err(ProgramError::MissingRequiredSignature));
                return result;
            } else if src_init_lamports < minimum_balance {
                assert_eq!(result, Err(ProgramError::Custom(0)));
                return result;
            } else if u64::MAX - src_init_lamports + minimum_balance < dst_init_lamports {
                assert_eq!(result, Err(ProgramError::Custom(0)));
                return result;
            }

            assert_eq!(accounts[0].lamports(), minimum_balance);
            assert_eq!(
                accounts[1].lamports(),
                dst_init_lamports + src_init_lamports - minimum_balance
            );
            assert!(result.is_ok())
        }
    }

    result
}

/// accounts[0] // Source Account Info
/// accounts[1] // Destination Info
/// accounts[2] // Authority Info
#[inline(never)]
fn test_process_withdraw_excess_lamports_multisig(accounts: &[AccountInfo; 3]) -> ProgramResult {
    cheatcode_is_multisig(&accounts[0]); // Source Account (Multisig)
    cheatcode_is_account(&accounts[1]); // Destination

    //-Initial State-----------------------------------------------------------
    let src_data_len = accounts[0].data_len();
    let src_init_lamports = accounts[0].lamports();
    let dst_init_lamports = accounts[1].lamports();
    let maybe_multisig_is_initialised = None; // Value set to `None` since authority is an account

    // Note: Rent is a supported sysvar so ProgramError::UnsupportedSysvar should be
    // impossible
    let rent = pinocchio::sysvars::rent::Rent::get().unwrap();
    let minimum_balance = rent.minimum_balance(accounts[0].data_len());

    //-Process Instruction-----------------------------------------------------
    let result = process_withdraw_excess_lamports(accounts);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else if src_data_len != Account::LEN
        && src_data_len != Mint::LEN
        && src_data_len != Multisig::LEN
    {
        assert_eq!(result, Err(ProgramError::Custom(13)));
        return result;
    } else {
        assert_eq!(src_data_len, Multisig::LEN); // established by cheatcode_is_multisig

        // Validate Owner
        inner_test_validate_owner(
            accounts[0].key(), // expected_owner
            &accounts[2],      // owner_account_info
            &accounts[3..],    // tx_signers
            maybe_multisig_is_initialised,
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
        assert_eq!(
            accounts[1].lamports(),
            dst_init_lamports + src_init_lamports - minimum_balance
        );
        assert!(result.is_ok())
    }

    result
}

/// accounts[0] // Source Account Info
/// accounts[1] // Destination Info
/// accounts[2] // Authority Info
/// accounts[3..14] // Signers
#[inline(never)]
fn test_process_withdraw_excess_lamports_multisig_multisig(
    accounts: &[AccountInfo; 4],
) -> ProgramResult {
    cheatcode_is_multisig(&accounts[0]); // Source Account (Multisig)
    cheatcode_is_account(&accounts[1]); // Destination
    cheatcode_is_multisig(&accounts[2]); // Authority

    //-Initial State-----------------------------------------------------------
    let src_data_len = accounts[0].data_len();
    let src_init_lamports = accounts[0].lamports();
    let dst_init_lamports = accounts[1].lamports();
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[2]).is_initialized());

    // Note: Rent is a supported sysvar so ProgramError::UnsupportedSysvar should be
    // impossible
    let rent = pinocchio::sysvars::rent::Rent::get().unwrap();
    let minimum_balance = rent.minimum_balance(accounts[0].data_len());

    //-Process Instruction-----------------------------------------------------
    let result = process_withdraw_excess_lamports(accounts);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else if src_data_len != Account::LEN
        && src_data_len != Mint::LEN
        && src_data_len != Multisig::LEN
    {
        assert_eq!(result, Err(ProgramError::Custom(13)));
        return result;
    } else {
        assert_eq!(src_data_len, Multisig::LEN); // established by cheatcode_is_multisig

        // Validate Owner
        inner_test_validate_owner(
            accounts[0].key(), // expected_owner
            &accounts[2],      // owner_account_info
            &accounts[3..],    // tx_signers
            maybe_multisig_is_initialised,
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
        assert_eq!(
            accounts[1].lamports(),
            dst_init_lamports + src_init_lamports - minimum_balance
        );
        assert!(result.is_ok())
    }

    result
}
