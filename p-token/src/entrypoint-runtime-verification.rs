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
        state::{
            account::Account, load_mut_unchecked, load_unchecked, mint::Mint, multisig::Multisig,
            Initializable, Transmutable,
        },
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

// Include prelude (macros, cheatcodes, helpers)
include!("../../specs/prelude-p-token.rs");

// Include inner_test_validate_owner
include!("../../specs/shared/inner_test_validate_owner.rs");

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

// Shared test harnesses ---------------------------------------------------
include!("../../specs/shared/test_process_approve_checked.rs");
include!("../../specs/shared/test_process_approve_checked_multisig.rs");
include!("../../specs/shared/test_process_approve.rs");
include!("../../specs/shared/test_process_approve_multisig.rs");
include!("../../specs/shared/test_process_freeze_account.rs");
include!("../../specs/shared/test_process_freeze_account_multisig.rs");
include!("../../specs/shared/test_process_get_account_data_size.rs");
include!("../../specs/shared/test_process_initialize_account2.rs");
include!("../../specs/shared/test_process_initialize_account3.rs");
include!("../../specs/shared/test_process_initialize_account.rs");
include!("../../specs/shared/test_process_initialize_immutable_owner.rs");
include!("../../specs/shared/test_process_initialize_mint2_freeze.rs");
include!("../../specs/shared/test_process_initialize_mint2_no_freeze.rs");
include!("../../specs/shared/test_process_initialize_mint_freeze.rs");
include!("../../specs/shared/test_process_initialize_mint_no_freeze.rs");
include!("../../specs/shared/test_process_initialize_multisig.rs");
include!("../../specs/shared/test_process_initialize_multisig2.rs");
include!("../../specs/shared/test_process_mint_to_checked.rs");
include!("../../specs/shared/test_process_mint_to_checked_multisig.rs");
include!("../../specs/shared/test_process_mint_to.rs");
include!("../../specs/shared/test_process_mint_to_multisig.rs");
include!("../../specs/shared/test_process_revoke.rs");
include!("../../specs/shared/test_process_revoke_multisig.rs");
include!("../../specs/shared/test_process_set_authority_account.rs");
include!("../../specs/shared/test_process_set_authority_account_multisig.rs");
include!("../../specs/shared/test_process_set_authority_mint.rs");
include!("../../specs/shared/test_process_set_authority_mint_multisig.rs");
include!("../../specs/shared/test_process_sync_native.rs");
include!("../../specs/shared/test_process_thaw_account.rs");
include!("../../specs/shared/test_process_thaw_account_multisig.rs");
include!("../../specs/shared/test_process_close_account.rs");
include!("../../specs/shared/test_process_close_account_multisig.rs");
include!("../../specs/shared/test_process_burn_checked.rs");
include!("../../specs/shared/test_process_burn_checked_multisig.rs");
include!("../../specs/shared/test_process_burn.rs");
include!("../../specs/shared/test_process_burn_multisig.rs");
include!("../../specs/shared/test_process_transfer_checked.rs");
include!("../../specs/shared/test_process_transfer_checked_multisig.rs");
include!("../../specs/shared/test_process_transfer.rs");
include!("../../specs/shared/test_process_transfer_multisig.rs");
include!("../../specs/shared/test_process_amount_to_ui_amount.rs");
include!("../../specs/shared/test_process_ui_amount_to_amount.rs");

// Withdraw Excess Lamports test harnesses (p-token specific)
include!("../../specs/withdraw-p-token.rs");
