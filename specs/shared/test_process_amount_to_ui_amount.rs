#[inline(never)]
fn test_process_amount_to_ui_amount(
    accounts: &[AccountInfo; 1],
    instruction_data: &[u8; 8],
) -> ProgramResult {
    cheatcode_mint!(&accounts[0]);

    //-Initial State-----------------------------------------------------------
    let mint_initialised = get_mint(&accounts[0]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = call_process_amount_to_ui_amount!(accounts, instruction_data);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < 8 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.is_empty() {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if owner!(&accounts[0]) != &PROGRAM_ID {
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
