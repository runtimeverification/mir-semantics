/// accounts[0] // Source Info
/// accounts[1] // Destination Info
/// accounts[2] // Authority Info
/// instruction_data[0..8] // Little Endian Bytes of u64 amount
#[inline(never)]
pub fn test_process_transfer(
    accounts: &[AccountInfo; 3],
    instruction_data: &[u8; 8],
) -> ProgramResult {
    cheatcode_account!(&accounts[0]);
    cheatcode_account!(&accounts[1]);
    cheatcode_account!(&accounts[2]); // Excluding the multisig case

    //-Initial State-----------------------------------------------------------
    let src_old = get_account(&accounts[0]);
    let amount = u64::from_le_bytes([
        instruction_data[0], instruction_data[1], instruction_data[2], instruction_data[3],
        instruction_data[4], instruction_data[5], instruction_data[6], instruction_data[7],
    ]);
    let src_initialised = src_old.is_initialized();
    let dst_initialised = get_account(&accounts[1]).is_initialized();
    let src_initial_amount = src_old.amount();
    let dst_initial_amount = get_account(&accounts[1]).amount();
    let src_initial_lamports = accounts[0].lamports();
    let dst_initial_lamports = accounts[1].lamports();
    let src_owner = src_old.owner;
    let old_src_delgate = src_old.delegate().cloned();
    let old_src_delgated_amount = src_old.delegated_amount();
    let maybe_multisig_is_initialised = None;

    #[cfg(feature = "assumptions")]
    // avoids potential overflow in destination account. assuming global supply bound by u64
    if !same_account!(accounts[0], accounts[1]) && dst_initial_amount.checked_add(amount).is_none() {
        return Err(ProgramError::Custom(99));
    }

    //-Process Instruction-----------------------------------------------------
    let result = call_process_transfer!(accounts, instruction_data);

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
    } else if !same_account!(accounts[0], accounts[1]) && dst_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if !same_account!(accounts[0], accounts[1]) && !dst_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount));
        return result;
    } else if get_account(&accounts[0]).account_state().unwrap() == AccountState::Frozen {
        assert_eq!(result, Err(ProgramError::Custom(17)));
        return result;
    } else if !same_account!(accounts[0], accounts[1])
        && get_account(&accounts[1]).account_state().unwrap() == AccountState::Frozen
    {
        assert_eq!(result, Err(ProgramError::Custom(17)));
        return result;
    } else if src_initial_amount < amount {
        assert_eq!(result, Err(ProgramError::Custom(1)));
        return result;
    } else if !same_account!(accounts[0], accounts[1])
        && get_account(&accounts[0]).mint != get_account(&accounts[1]).mint
    {
        assert_eq!(result, Err(ProgramError::Custom(3)));
        return result;
    } else {
        let src_new = get_account(&accounts[0]);
        if old_src_delgate == Some(*key!(&accounts[2])) {
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
        if ((same_account!(accounts[0], accounts[1])) || amount == 0)
            && owner!(&accounts[0]) != &PROGRAM_ID
        {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId));
            return result;
        } else if ((same_account!(accounts[0], accounts[1])) || amount == 0)
            && owner!(&accounts[1]) != &PROGRAM_ID
        {
            assert_eq!(result, Err(ProgramError::IncorrectProgramId));
            return result;
        } else if !same_account!(accounts[0], accounts[1])
            && amount != 0
            && src_new.is_native()
            && src_initial_lamports < amount
        {
            assert_eq!(result, Err(ProgramError::Custom(14)));
            return result;
        } else if !same_account!(accounts[0], accounts[1])
            && amount != 0
            && src_new.is_native()
            && dst_initial_lamports.checked_add(amount).is_none()
        {
            assert_eq!(result, Err(ProgramError::Custom(14)));
            return result;
        }

        assert!(result.is_ok());

        if !same_account!(accounts[0], accounts[1]) && amount != 0 {
            assert_eq!(src_new.amount(), src_initial_amount - amount);
            assert_eq!(
                get_account(&accounts[1]).amount(),
                dst_initial_amount + amount
            );

            if src_new.is_native() {
                assert_eq!(accounts[0].lamports(), src_initial_lamports - amount);
                assert_eq!(accounts[1].lamports(), dst_initial_lamports + amount);
            }
        }

        // Delegate updates
        if old_src_delgate == Some(*key!(&accounts[2])) && !same_account!(accounts[0], accounts[1]) {
            assert_eq!(src_new.delegated_amount(), old_src_delgated_amount - amount);
            if old_src_delgated_amount - amount == 0 {
                assert_eq!(src_new.delegate(), None);
            }
        }
    }

    result
}
