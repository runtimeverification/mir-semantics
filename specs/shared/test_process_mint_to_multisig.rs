/// accounts[0] // Mint Info
/// accounts[1] // Destination Info
/// accounts[2] // Owner Info
/// accounts[3..14] // Signers
/// instruction_data[0..8] // Little Endian Bytes of u64 amount
#[inline(never)]
fn test_process_mint_to_multisig(
    accounts: &[AccountInfo; 4],
    instruction_data: &[u8; 8],
) -> ProgramResult {
    cheatcode_mint!(&accounts[0]);
    cheatcode_account!(&accounts[1]);
    cheatcode_multisig!(&accounts[2]);

    //-Initial State-----------------------------------------------------------
    let mint_old = get_mint(&accounts[0]);
    let dst_old = get_account(&accounts[1]);
    let initial_supply = mint_old.supply();
    let initial_amount = dst_old.amount();
    let mint_initialised = mint_old.is_initialized();
    let dst_initialised = dst_old.is_initialized();
    let dst_init_state = dst_old.account_state();
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[2]).is_initialized());

    #[cfg(feature = "assumptions")]
    {
        // Do not execute if adding to the account balance would overflow.
        // shared::mint_to.rs,L68 is based on the assumption that initial_amount <=
        // mint.supply and therefore cannot overflow because the minting itself
        // would already error out.
        let amount = u64::from_le_bytes([
            instruction_data[0], instruction_data[1], instruction_data[2], instruction_data[3],
            instruction_data[4], instruction_data[5], instruction_data[6], instruction_data[7],
        ]);
        if initial_amount.checked_add(amount).is_none() {
            return Err(ProgramError::Custom(99));
        }
    }

    //-Process Instruction-----------------------------------------------------
    let result = call_process_mint_to!(accounts, instruction_data);

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
    } else if dst_init_state.unwrap() == AccountState::Frozen {
        assert_eq!(result, Err(ProgramError::Custom(17)));
        return result;
    } else if get_account(&accounts[1]).is_native() {
        assert_eq!(result, Err(ProgramError::Custom(10)));
        return result;
    } else if key!(&accounts[0]) != &get_account(&accounts[1]).mint {
        assert_eq!(result, Err(ProgramError::Custom(3)));
        return result;
    } else if accounts[0].data_len() != Mint::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if mint_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if !mint_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount));
        return result;
    } else {
        let mint_new = get_mint(&accounts[0]);
        let mint_authority_new = mint_new.mint_authority();
        if mint_authority_new.is_some() {
            inner_test_validate_owner(
                mint_authority_new.unwrap(), // expected_owner
                &accounts[2],                // owner_account_info
                &accounts[3..],              // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;
        } else {
            assert_eq!(result, Err(ProgramError::Custom(5)));
            return result;
        }

        let amount = u64::from_le_bytes([
            instruction_data[0], instruction_data[1], instruction_data[2], instruction_data[3],
            instruction_data[4], instruction_data[5], instruction_data[6], instruction_data[7],
        ]);

        if amount == 0 && owner!(&accounts[0]) != &PROGRAM_ID {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId));
            return result;
        } else if amount == 0 && owner!(&accounts[1]) != &PROGRAM_ID {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId));
            return result;
        } else if amount != 0 && amount.checked_add(initial_supply).is_none() {
            assert_eq!(result, Err(ProgramError::Custom(14)));
            return result;
        }

        assert_eq!(mint_new.supply(), initial_supply + amount);
        assert_eq!(get_account(&accounts[1]).amount(), initial_amount + amount);
        assert!(result.is_ok());
    }

    result
}
