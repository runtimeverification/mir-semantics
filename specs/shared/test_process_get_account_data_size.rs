/// accounts[0] // Mint Info
#[inline(never)]
fn test_process_get_account_data_size(accounts: &[AccountInfo; 1]) -> ProgramResult {
    cheatcode_mint!(&accounts[0]);

    //-Initial State-----------------------------------------------------------
    let mint_initialised = get_mint(&accounts[0]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = call_process_get_account_data_size!(accounts);

    //-Assert Postconditions---------------------------------------------------
    if accounts.is_empty() {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if owner!(&accounts[0]) != &PROGRAM_ID {
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
