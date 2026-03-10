/// accounts[0]   // Multisig Info
/// accounts[1]   // Rent Sysvar Info
/// accounts[2..] // Signers
/// accounts[2..].len() // n
/// instruction_data[1] // m
#[inline(never)]
fn test_process_initialize_multisig(
    accounts: &[AccountInfo; 5],
    instruction_data: &[u8; 1],
) -> ProgramResult {
    cheatcode_multisig!(&accounts[0]);
    cheatcode_rent!(&accounts[1]);
    cheatcode_account!(&accounts[2]); // Signer
    cheatcode_account!(&accounts[3]); // Signer
    cheatcode_account!(&accounts[4]); // Signer

    //-Initial State-----------------------------------------------------------
    let multisig_already_initialised = get_multisig(&accounts[0]).is_initialized();
    let multisig_init_lamports = accounts[0].lamports();
    let minimum_balance = get_rent(&accounts[1]).minimum_balance(accounts[0].data_len());

    //-Process Instruction-----------------------------------------------------
    let result = call_process_initialize_multisig!(accounts, instruction_data);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.is_empty() {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.len() < 2 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if key!(&accounts[1]) != &RENT_ID {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if accounts[0].data_len() != Multisig::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if multisig_already_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if multisig_already_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::Custom(6)))
    } else if multisig_init_lamports < minimum_balance {
        assert_eq!(result, Err(ProgramError::Custom(0)))
    } else if !((1..=MAX_SIGNERS as usize).contains(&(accounts.len() - 2))) {
        assert_eq!(result, Err(ProgramError::Custom(7)))
    } else if !(1..=MAX_SIGNERS).contains(&instruction_data[0]) {
        assert_eq!(result, Err(ProgramError::Custom(8)))
    } else {
        let multisig_new = get_multisig(&accounts[0]);
        assert!(accounts[2..]
            .iter()
            .map(|signer| *key!(signer))
            .eq(multisig_new.signers
                .iter()
                .take(accounts[2..].len())
                .copied()));
        assert_eq!(multisig_new.m, instruction_data[0]);
        assert_eq!(multisig_new.n as usize, accounts.len() - 2);
        assert!(multisig_new.is_initialized().is_ok());
        assert!(multisig_new.is_initialized().unwrap());
        assert!(result.is_ok())
    }

    result
}
