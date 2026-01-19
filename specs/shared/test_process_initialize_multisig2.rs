/// accounts[0]   // Multisig Info
/// accounts[1..] // Signers
/// accounts[1..].len() // n
/// instruction_data[1] // m
#[inline(never)]
fn test_process_initialize_multisig2(
    accounts: &[AccountInfo; 4],
    instruction_data: &[u8; 1],
) -> ProgramResult {
    cheatcode_multisig!(&accounts[0]);
    cheatcode_account!(&accounts[1]); // Signer
    cheatcode_account!(&accounts[2]); // Signer
    cheatcode_account!(&accounts[3]); // Signer

    //-Initial State-----------------------------------------------------------
    let multisig_already_initialised = get_multisig(&accounts[0]).is_initialized();
    let multisig_init_lamports = accounts[0].lamports();
    // Note: Rent is a supported sysvar so ProgramError::UnsupportedSysvar should be
    // impossible
    let rent = Rent::get().unwrap();
    let minimum_balance = rent.minimum_balance(accounts[0].data_len());

    //-Process Instruction-----------------------------------------------------
    let result = call_process_initialize_multisig2!(accounts, instruction_data);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.is_empty() {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.is_empty() {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].data_len() != Multisig::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if multisig_already_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if multisig_already_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::Custom(6)))
    } else if multisig_init_lamports < minimum_balance {
        assert_eq!(result, Err(ProgramError::Custom(0)))
    } else if !((1..=11).contains(&(accounts.len() - 1))) {
        assert_eq!(result, Err(ProgramError::Custom(7)))
    } else if !(1..=11).contains(&instruction_data[0]) {
        assert_eq!(result, Err(ProgramError::Custom(8)))
    } else {
        let multisig_new = get_multisig(&accounts[0]);
        assert!(accounts[1..]
            .iter()
            .map(|signer| *key!(signer))
            .eq(multisig_new.signers
                .iter()
                .take(accounts[1..].len())
                .copied()));
        assert_eq!(multisig_new.m, instruction_data[0]);
        assert_eq!(multisig_new.n as usize, accounts.len() - 1);
        assert!(multisig_new.is_initialized().is_ok());
        assert!(multisig_new.is_initialized().unwrap());
        assert!(result.is_ok())
    }

    result
}
