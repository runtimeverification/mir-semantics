#[inline(never)]
fn test_process_sync_native(accounts: &[AccountInfo; 1]) -> ProgramResult {
    cheatcode_account!(&accounts[0]);

    //-Initial State-----------------------------------------------------------
    let src_old = get_account(&accounts[0]);
    let src_owner = owner!(&accounts[0]);
    let src_initialised = src_old.is_initialized();
    let src_native_amount = src_old.native_amount();
    let src_init_lamports = accounts[0].lamports();
    let src_init_amount = src_old.amount();

    //-Process Instruction-----------------------------------------------------
    let result = call_process_sync_native!(accounts);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() != 1 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if src_owner != &PROGRAM_ID {
        assert_eq!(result, Err(ProgramError::IncorrectProgramId))
    } else if accounts[0].data_len() != Account::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if src_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !src_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount))
    } else if src_native_amount.is_none() {
        assert_eq!(result, Err(ProgramError::Custom(19)))
    } else if src_init_lamports < src_native_amount.unwrap() {
        assert_eq!(result, Err(ProgramError::Custom(14)))
    } else if src_init_lamports - src_native_amount.unwrap() < src_init_amount {
        assert_eq!(result, Err(ProgramError::Custom(13)))
    } else {
        assert_eq!(
            get_account(&accounts[0]).amount(),
            src_init_lamports - src_native_amount.unwrap()
        );
        assert!(result.is_ok())
    }
    result
}
