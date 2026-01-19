#[inline(never)]
pub fn test_process_initialize_mint2_no_freeze(
    accounts: &[AccountInfo; 1],
    instruction_data: &[u8; 34],
) -> ProgramResult {
    cheatcode_mint!(&accounts[0]);

    //-Initial State-----------------------------------------------------------
    // Note: Rent is a supported sysvar so ProgramError::UnsupportedSysvar should be
    // impossible
    let rent = Rent::get().unwrap();
    let minimum_balance = rent.minimum_balance(accounts[0].data_len());
    let mint_is_initialised_prior = get_mint(&accounts[0]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = call_process_initialize_mint2_no_freeze!(accounts, instruction_data);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < 34 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if instruction_data[33] != 0 && instruction_data[33] != 1 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if instruction_data[33] == 1 && instruction_data.len() < 66 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.is_empty() {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].data_len() != Mint::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if mint_is_initialised_prior.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if mint_is_initialised_prior.unwrap() {
        assert_eq!(result, Err(ProgramError::Custom(6)))
    } else if accounts[0].lamports() < minimum_balance {
        assert_eq!(result, Err(ProgramError::Custom(0)))
    } else {
        assert!(result.is_ok());

        let mint_new = get_mint(&accounts[0]);
        assert!(mint_new.is_initialized().unwrap());
        assert_pubkey_from_slice!(mint_new.mint_authority().unwrap(), &instruction_data[1..33]);
        assert_eq!(mint_new.decimals, instruction_data[0]);

        #[allow(clippy::out_of_bounds_indexing)]
        // Guard above prevents this branch TODO: Perhaps remove?
        if instruction_data[33] == 1 {
            assert_pubkey_from_slice!(mint_new.freeze_authority().unwrap(), &instruction_data[34..66]);
        }
    }

    result
}
