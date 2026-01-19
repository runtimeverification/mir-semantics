/// accounts[0] // Source Account Info
/// accounts[1] // Owner Info
/// accounts[2..13] // Signers
#[inline(never)]
fn test_process_revoke(accounts: &[AccountInfo; 2]) -> ProgramResult {
    cheatcode_account!(&accounts[0]); // Source Account
    cheatcode_account!(&accounts[1]); // Owner

    //-Initial State-----------------------------------------------------------
    let src_old = get_account(&accounts[0]);
    let src_initialised = src_old.is_initialized();
    let src_init_state = src_old.account_state();
    let src_owner = src_old.owner;
    let maybe_multisig_is_initialised = None; // Value set to `None` since authority is an account

    //-Process Instruction-----------------------------------------------------
    let result = call_process_revoke!(accounts);

    //-Assert Postconditions---------------------------------------------------
    if accounts.is_empty() {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].data_len() != Account::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if src_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !src_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount))
    } else if accounts.len() < 2 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if src_init_state.unwrap() == AccountState::Frozen {
        assert_eq!(result, Err(ProgramError::Custom(17)))
    } else {
        // Validate Owner
        inner_test_validate_owner(
            &src_owner,     // expected_owner
            &accounts[1],   // owner_account_info
            &accounts[2..], // tx_signers
            maybe_multisig_is_initialised,
            result.clone(),
        )?;

        let src_new = get_account(&accounts[0]);
        assert!(src_new.delegate().is_none());
        assert_eq!(src_new.delegated_amount(), 0);
        assert!(result.is_ok())
    }

    result
}
