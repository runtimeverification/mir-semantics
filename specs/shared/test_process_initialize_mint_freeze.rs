/// accounts[0] // Mint Info
/// accounts[1] // Rent Sysvar Info
/// instruction_data[0]      // Decimals
/// instruction_data[1..33]  // Mint Authority Pubkey
/// instruction_data[33]     // Freeze Authority Exists? 1 for freeze
/// instruction_data[34..66] // instruction_data[33] == 1 ==> Freeze Authority
/// Pubkey
#[inline(never)]
fn test_process_initialize_mint_freeze(
    accounts: &[AccountInfo; 2],
    instruction_data: &[u8; 66],
) -> ProgramResult {
    cheatcode_mint!(&accounts[0]);
    cheatcode_rent!(&accounts[1]);

    //-Initial State-----------------------------------------------------------
    let minimum_balance = get_rent(&accounts[1]).minimum_balance(accounts[0].data_len()); // TODO float problem
    let mint_is_initialised_prior = get_mint(&accounts[0]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = call_process_initialize_mint!(accounts, instruction_data);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < 34 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if instruction_data[33] != 0 && instruction_data[33] != 1 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if instruction_data[33] == 1 && instruction_data.len() < 66 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.len() < 2 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].data_len() != Mint::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if key!(accounts[1]) != &RENT_ID {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
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

        if instruction_data[33] == 1 {
            assert_pubkey_from_slice!(mint_new.freeze_authority().unwrap(), &instruction_data[34..66]);
        }
    }

    result
}
