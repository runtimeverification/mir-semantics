/// accounts[0] // Source Info
/// accounts[1] // Mint Info
/// accounts[2] // Authority Info
/// accounts[3..14] // Signers
/// instruction_data[0..8] // Little Endian Bytes of u64 amount
#[inline(never)]
fn test_process_burn_multisig(
    accounts: &[AccountInfo; 4],
    instruction_data: &[u8; 8],
) -> ProgramResult {
    cheatcode_account!(&accounts[0]);
    cheatcode_mint!(&accounts[1]);
    cheatcode_multisig!(&accounts[2]);

    //-Initial State-----------------------------------------------------------
    let src_old = get_account(&accounts[0]);
    let mint_old = get_mint(&accounts[1]);
    let amount = u64::from_le_bytes([
        instruction_data[0], instruction_data[1], instruction_data[2], instruction_data[3],
        instruction_data[4], instruction_data[5], instruction_data[6], instruction_data[7],
    ]);
    let src_initialised = src_old.is_initialized();
    let src_init_amount = src_old.amount();
    let src_init_state = src_old.account_state();
    let src_is_native = src_old.is_native();
    let src_mint = src_old.mint;
    let src_owned_sys_inc = src_old.is_owned_by_system_program_or_incinerator();
    let src_owner = src_old.owner;
    let old_src_delgate = src_old.delegate().cloned();
    let old_src_delgated_amount = src_old.delegated_amount();
    let mint_initialised = mint_old.is_initialized();
    let mint_init_supply = mint_old.supply();
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[2]).is_initialized());

    //-Process Instruction-----------------------------------------------------
    let result = call_process_burn!(accounts, instruction_data);

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
    } else if key!(&accounts[1]) != &src_mint {
        assert_eq!(result, Err(ProgramError::Custom(3)))
    } else {
        if !src_owned_sys_inc {
            if old_src_delgate.is_some() && *key!(&accounts[2]) == old_src_delgate.unwrap() {
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
                inner_test_validate_owner(
                    &src_owner,     // expected_owner
                    &accounts[2],   // owner_account_info
                    &accounts[3..], // tx_signers
                    maybe_multisig_is_initialised,
                    result.clone(),
                )?;
            }
        }

        if amount == 0 && owner!(&accounts[0]) != &PROGRAM_ID {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId))
        } else if amount == 0 && owner!(&accounts[1]) != &PROGRAM_ID {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId))
        } else {
            let src_new = get_account(&accounts[0]);
            assert!(src_new.amount() == src_init_amount - amount);
            assert!(get_mint(&accounts[1]).supply() == mint_init_supply - amount);
            assert!(result.is_ok());

            // Delegate updates
            if old_src_delgate.is_some() && *key!(&accounts[2]) == old_src_delgate.unwrap() {
                assert_eq!(src_new.delegated_amount(), old_src_delgated_amount - amount);
                if old_src_delgated_amount - amount == 0 {
                    assert_eq!(src_new.delegate(), None);
                }
            }
        }
    }

    result
}
