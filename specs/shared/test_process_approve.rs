fn test_process_approve(accounts: &[AccountInfo; 3], instruction_data: &[u8; 8]) -> ProgramResult {
    cheatcode_account!(&accounts[0]); // Source Account
    cheatcode_account!(&accounts[1]); // Delegate
    cheatcode_account!(&accounts[2]); // Excluding the multisig case

    //-Initial State-----------------------------------------------------------
    let src_old = get_account(&accounts[0]);
    let amount = unsafe { u64::from_le_bytes(*(instruction_data.as_ptr() as *const [u8; 8])) };
    let src_owner = src_old.owner;
    let src_initialised = src_old.is_initialized();
    let src_init_state = src_old.account_state();
    let maybe_multisig_is_initialised = None; // Value set to `None` since authority is an account

    //-Process Instruction-----------------------------------------------------
    let result = call_process_approve!(accounts, instruction_data);

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
    } else if src_init_state.unwrap() == AccountState::Frozen {
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

        let src_new = get_account(&accounts[0]);
        assert_eq!(src_new.delegate().unwrap(), key!(accounts[1]));
        assert_eq!(src_new.delegated_amount(), amount);
        assert!(result.is_ok())
    }

    result
}
