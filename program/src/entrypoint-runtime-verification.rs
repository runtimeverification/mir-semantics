//! Program entrypoint for runtime verification proofs of original spl token implmentation

use {
    crate::{
        processor::Processor,
        state::{Account, AccountState, Mint, Multisig},
    },
    solana_account_info::AccountInfo,
    solana_program_error::{ProgramError, ProgramResult},
    solana_program_pack::Pack,
    solana_pubkey::Pubkey,
    solana_sysvar::Sysvar,
    spl_token_interface::error::TokenError,
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

// Include prelude (macros, cheatcodes, wrappers, helpers)
include!("../../specs/prelude-spl-token.rs");

// Include inner_test_validate_owner
include!("../../specs/shared/inner_test_validate_owner.rs");

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
                        accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                        payload.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                    )
                }
                x if 34 <= x => {
                    test_process_initialize_mint_no_freeze(
                        accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                        payload.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                    )
                }
                _ => Err(TokenError::InvalidInstruction.into()),
            }
        }
        // 1 - Initialize Account
        1 => {
            test_process_initialize_account(
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 2 - Initialize Multisig
        2 => {
            test_process_initialize_multisig(
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                instruction_data[1..].first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 3 - Transfer
        3 => {
            if accounts.len() >= 4
                && accounts[2].data_len() == Multisig::LEN
                && accounts[2].owner == &crate::id()
            {
                test_process_transfer_multisig(
                    accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 4]
                    instruction_data.last_chunk().ok_or(TokenError::InvalidInstruction)?,
                )
            } else {
                test_process_transfer(
                    accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 3]
                    instruction_data.last_chunk().ok_or(TokenError::InvalidInstruction)?,
                )
            }
        }
        // 4 - Approve
        4 => {
            if accounts.len() >= 4
                && accounts[2].data_len() == Multisig::LEN
                && accounts[2].owner == &crate::id()
            {
                test_process_approve_multisig(
                    accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 4]
                    instruction_data.last_chunk().ok_or(TokenError::InvalidInstruction)?,
                )
            } else {
                test_process_approve(
                    accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 3]
                    instruction_data.last_chunk().ok_or(TokenError::InvalidInstruction)?,
                )
            }
        }
        // 5 - Revoke
        5 => {
            if accounts.len() >= 3
                && accounts[1].data_len() == Multisig::LEN
                && accounts[1].owner == &crate::id()
            {
                test_process_revoke_multisig(
                    accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                )
            } else {
                test_process_revoke(
                    accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                )
            }
        }
        // 6 - Set Authority Account
        6 => {
            // #[cfg(feature = "logging")]
            // msg!("Testing Instruction: Set Authority Account");
            if let Some(first_account) = accounts.first() {
                match first_account.data_len() {
                    Account::LEN => {
                        if accounts.len() >= 3
                            && accounts[1].data_len() == Multisig::LEN
                            && accounts[1].owner == &crate::id()
                        {
                            test_process_set_authority_account_multisig(
                                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                                instruction_data[1..].first_chunk().ok_or(TokenError::InvalidInstruction)?,
                            )
                        } else {
                            test_process_set_authority_account(
                                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                                instruction_data[1..].first_chunk().ok_or(TokenError::InvalidInstruction)?,
                            )
                        }
                    }
                    Mint::LEN => {
                        if accounts.len() >= 3
                            && accounts[1].data_len() == Multisig::LEN
                            && accounts[1].owner == &crate::id()
                        {
                            test_process_set_authority_mint_multisig(
                                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 3]
                                instruction_data[1..].first_chunk().ok_or(TokenError::InvalidInstruction)?,
                            )
                        } else {
                            test_process_set_authority_mint(
                                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 2]
                                instruction_data[1..].first_chunk().ok_or(TokenError::InvalidInstruction)?,
                            )
                        }
                    }
                    _ => Err(TokenError::InvalidInstruction.into()),
                }
            } else {
                Err(TokenError::InvalidInstruction.into())
            }
        }
        // 7 - Mint To
        7 => {
            if accounts.len() >= 4
                && accounts[2].data_len() == Multisig::LEN
                && accounts[2].owner == &crate::id()
            {
                test_process_mint_to_multisig(
                    accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 4]
                    instruction_data.last_chunk().ok_or(TokenError::InvalidInstruction)?,
                )
            } else {
                test_process_mint_to(
                    accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 3]
                    instruction_data.last_chunk().ok_or(TokenError::InvalidInstruction)?,
                )
            }
        }
        // 8 - Burn
        8 => {
            if accounts.len() >= 4
                && accounts[2].data_len() == Multisig::LEN
                && accounts[2].owner == &crate::id()
            {
                test_process_burn_multisig(
                    accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 4]
                    instruction_data.last_chunk().ok_or(TokenError::InvalidInstruction)?,
                )
            } else {
                test_process_burn(
                    accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 3]
                    instruction_data.last_chunk().ok_or(TokenError::InvalidInstruction)?,
                )
            }
        }
        // 9 - Close Account
        9 => {
            if accounts.len() >= 4
                && accounts[2].data_len() == Multisig::LEN
                && accounts[2].owner == &crate::id()
            {
                test_process_close_account_multisig(
                    accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                )
            } else {
                test_process_close_account(
                    accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                )
            }
        }
        // 10 - Freeze Account
        10 => {
            if accounts.len() >= 4
                && accounts[2].data_len() == Multisig::LEN
                && accounts[2].owner == &crate::id()
            {
                test_process_freeze_account_multisig(
                    accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                )
            } else {
                test_process_freeze_account(
                    accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                )
            }
        }
        // 11 - Thaw Account
        11 => {
            if accounts.len() >= 4
                && accounts[2].data_len() == Multisig::LEN
                && accounts[2].owner == &crate::id()
            {
                test_process_thaw_account_multisig(
                    accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                )
            } else {
                test_process_thaw_account(
                    accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                )
            }
        }
        // 12 - Transfer Checked
        12 => {
            if accounts.len() >= 5
                && accounts[3].data_len() == Multisig::LEN
                && accounts[3].owner == &crate::id()
            {
                test_process_transfer_checked_multisig(
                    accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                    instruction_data[1..].first_chunk().ok_or(TokenError::InvalidInstruction)?,
                )
            } else {
                test_process_transfer_checked(
                    accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                    instruction_data[1..].first_chunk().ok_or(TokenError::InvalidInstruction)?,
                )
            }
        }
        // 13 - Approve Checked
        13 => {
            if accounts.len() >= 5
                && accounts[3].data_len() == Multisig::LEN
                && accounts[3].owner == &crate::id()
            {
                test_process_approve_checked_multisig(
                    accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                    instruction_data[1..].first_chunk().ok_or(TokenError::InvalidInstruction)?,
                )
            } else {
                test_process_approve_checked(
                    accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                    instruction_data[1..].first_chunk().ok_or(TokenError::InvalidInstruction)?,
                )
            }
        }
        // 14 - Mint To Checked
        14 => {
            if accounts.len() >= 4
                && accounts[2].data_len() == Multisig::LEN
                && accounts[2].owner == &crate::id()
            {
                test_process_mint_to_checked_multisig(
                    accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                    instruction_data[1..].first_chunk().ok_or(TokenError::InvalidInstruction)?,
                )
            } else {
                test_process_mint_to_checked(
                    accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 3]
                    instruction_data.last_chunk().ok_or(TokenError::InvalidInstruction)?,
                )
            }
        }
        // 15 - Burn Checked
        15 => {
            if accounts.len() >= 4
                && accounts[2].data_len() == Multisig::LEN
                && accounts[2].owner == &crate::id()
            {
                test_process_burn_checked_multisig(
                    accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                    instruction_data[1..].first_chunk().ok_or(TokenError::InvalidInstruction)?,
                )
            } else {
                test_process_burn_checked(
                    accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                    instruction_data[1..].first_chunk().ok_or(TokenError::InvalidInstruction)?,
                )
            }
        }
        // 16 - Initialize Account2
        16 => {
            test_process_initialize_account2(
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 3]
                instruction_data[1..].first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 17 - Sync Native
        17 => {
            test_process_sync_native(
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 18 - Initialize Account3
        18 => {
            test_process_initialize_account3(
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 2]
                instruction_data[1..].first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 19 - Initialize Multisig2
        19 => {
            test_process_initialize_multisig2(
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                instruction_data[1..].first_chunk().ok_or(TokenError::InvalidInstruction)?,
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
                        accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 1]
                        instruction_data[1..].first_chunk().ok_or(TokenError::InvalidInstruction)?,
                    )
                }
                x if 34 <= x => {
                    test_process_initialize_mint2_no_freeze(
                        accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?, // CHANGE P-Token: accounts: &[AccountInfo; 1]
                        instruction_data[1..].first_chunk().ok_or(TokenError::InvalidInstruction)?,
                    )
                }
                _ => Err(TokenError::InvalidInstruction.into()),
            }
        }
        // 21 - Get Account Data Size
        21 => {
            test_process_get_account_data_size(
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 22 - Initialize Immutable Owner
        22 => {
            test_process_initialize_immutable_owner(
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 23 - Amount To Ui Amount
        23 => {
            test_process_amount_to_ui_amount(
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                instruction_data[1..].first_chunk().ok_or(TokenError::InvalidInstruction)?,
            )
        }
        // 24 - Ui Amount To Amount
        24 => {
            test_process_ui_amount_to_amount(
                accounts.first_chunk().ok_or(TokenError::InvalidInstruction)?,
                &instruction_data[1..],
            )
        }
        // 38 - Withdraw Excess Lamports
        38 => {
            // #[cfg(feature = "logging")]
            // msg!("Testing Instruction: Withdraw Excess Lamports");
            test_process_withdraw_excess_lamports(
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

// wrapper to ensure the test below is in the SMIR JSON
#[no_mangle]
pub unsafe extern "C" fn use_tests(acc: &AccountInfo) {
    test_spltoken_domain_data(acc, acc, acc);
}

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

// Withdraw Excess Lamports test harness (spl-token specific)
include!("../../specs/withdraw-spl-token.rs");
