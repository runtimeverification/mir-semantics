#[inline(never)]
fn test_process_initialize_immutable_owner(accounts: &[AccountInfo; 1]) -> ProgramResult {
    cheatcode_account!(&accounts[0]);

    //-Initial State-----------------------------------------------------------
    let src_initialised = get_account(&accounts[0]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = call_process_initialize_immutable_owner!(accounts);

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
