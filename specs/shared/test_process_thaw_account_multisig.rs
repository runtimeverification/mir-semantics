/// accounts[0] // Source Account Info
/// accounts[1] // Mint Info
/// accounts[2] // Authority Info
/// accounts[3..13] // Signers
#[inline(never)]
fn test_process_thaw_account_multisig(accounts: &[AccountInfo; 4]) -> ProgramResult {
    cheatcode_account!(&accounts[0]);
    cheatcode_mint!(&accounts[1]);
    cheatcode_multisig!(&accounts[2]);

    #[cfg(feature = "assumptions")]
    {
        let multisig = get_multisig(&accounts[2]);
        if multisig.m < 1 || multisig.m > MAX_SIGNERS as u8 {
            return Ok(());
        }
        if multisig.n < 1 || multisig.n > MAX_SIGNERS as u8 {
            return Ok(());
        }
    }

    //-Initial State-----------------------------------------------------------
    let src_old = get_account(&accounts[0]);
    let mint_old = get_mint(&accounts[1]);
    let src_initialised = src_old.is_initialized();
    let src_init_state = src_old.account_state();
    let src_is_native = src_old.is_native();
    let src_mint = src_old.mint;
    let mint_initialised = mint_old.is_initialized();
    let mint_freeze_auth = mint_old.freeze_authority().cloned();
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[2]).is_initialized());

    //-Process Instruction-----------------------------------------------------
    let result = call_process_thaw_account!(accounts);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].data_len() != Account::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if src_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !src_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount))
    } else if src_init_state.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if src_init_state.unwrap() != AccountState::Frozen {
        assert_eq!(result, Err(ProgramError::Custom(13)))
    } else if src_is_native {
        assert_eq!(result, Err(ProgramError::Custom(10)))
    } else if key!(&accounts[1]) != &src_mint {
        assert_eq!(result, Err(ProgramError::Custom(3)))
    } else if accounts[1].data_len() != Mint::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if mint_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !mint_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount))
    } else if mint_freeze_auth.is_none() {
        assert_eq!(result, Err(ProgramError::Custom(16)))
    } else {
        // Validate Owner
        inner_test_validate_owner(
            &mint_freeze_auth.unwrap(), // expected_owner
            &accounts[2],               // owner_account_info
            &accounts[3..],             // tx_signers
            maybe_multisig_is_initialised,
            result.clone(),
        )?;

        assert_eq!(
            get_account(&accounts[0]).account_state().unwrap(),
            AccountState::Initialized
        );
        assert!(result.is_ok())
    }
    result
}
