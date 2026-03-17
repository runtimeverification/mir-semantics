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
    cheatcode_mint!(&accounts[0]);
    cheatcode_account!(&accounts[1]);
    cheatcode_multisig!(&accounts[2]);

    #[cfg(feature = "assumptions")]
    {
        let multisig = get_multisig(&accounts[2]);
        if multisig.m < 1 || multisig.m > MAX_SIGNERS {
            return Ok(());
        }
        if multisig.n < 1 || multisig.n > MAX_SIGNERS {
            return Ok(());
        }
    }

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
        // mint.supply() and therefore cannot overflow because the minting itself
        // would already error out.
        let amount = unsafe { u64::from_le_bytes(*(instruction_data.as_ptr() as *const [u8; 8])) };
        if initial_amount.checked_add(amount).is_none() {
            return Err(ProgramError::Custom(99));
        }
    }

    //-Process Instruction-----------------------------------------------------
    let result = call_process_mint_to_checked!(accounts, instruction_data);

    //-Assert Postconditions---------------------------------------------------
    let mint_new = get_mint(&accounts[0]);
    let dst_new = get_account(&accounts[1]);

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
    } else if dst_init_state.unwrap() == AccountState::Frozen {
        // unwrap must succeed due to dst_initialised not being err
        assert_eq!(result, Err(ProgramError::Custom(17)));
        return result;
    } else if dst_new.is_native() {
        assert_eq!(result, Err(ProgramError::Custom(10)));
        return result;
    } else if key!(accounts[0]) != &dst_new.mint {
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
    } else if instruction_data[8] != mint_new.decimals {
        assert_eq!(result, Err(ProgramError::Custom(18)));
        return result;
    } else {
        if mint_new.mint_authority().is_some() {
            // Validate Owner
            inner_test_validate_owner(
                mint_new.mint_authority().unwrap(), // expected_owner
                &accounts[2],                       // owner_account_info
                &accounts[3..],                     // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;
        } else {
            assert_eq!(result, Err(ProgramError::Custom(5)));
            return result;
        }

        let amount = unsafe { u64::from_le_bytes(*(instruction_data.as_ptr() as *const [u8; 8])) };

        if amount == 0 && owner!(accounts[0]) != &PROGRAM_ID {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId));
            return result;
        } else if amount == 0 && owner!(accounts[1]) != &PROGRAM_ID {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId));
            return result;
        } else if amount != 0 && initial_supply.checked_add(amount).is_none() {
            assert_eq!(result, Err(ProgramError::Custom(14)));
            return result;
        }

        assert_eq!(mint_new.supply(), initial_supply + amount);
        assert_eq!(dst_new.amount(), initial_amount + amount);
        assert!(result.is_ok());
    }

    result
}
