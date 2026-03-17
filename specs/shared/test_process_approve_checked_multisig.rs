/// accounts[0] // Source Account Info
/// accounts[1] // Expected Mint Info
/// accounts[2] // Delegate Info
/// accounts[3] // Owner Info
/// accounts[4..15] // Signers
/// instruction_data[0..9] // Little Endian Bytes of u64 amount, and decimals
#[inline(never)]
fn test_process_approve_checked_multisig(
    accounts: &[AccountInfo; 5],
    instruction_data: &[u8; 9],
) -> ProgramResult {
    cheatcode_account!(&accounts[0]); // Source Account
    cheatcode_mint!(&accounts[1]); // Expected Mint
    cheatcode_account!(&accounts[2]); // Delegate
    cheatcode_multisig!(&accounts[3]); // Owner

    #[cfg(feature = "assumptions")]
    {
        let multisig = get_multisig(&accounts[3]);
        if multisig.m < 1 || multisig.m > MAX_SIGNERS as u8 {
            return Ok(());
        }
        if multisig.n < 1 || multisig.n > MAX_SIGNERS as u8 {
            return Ok(());
        }
    }

    //-Initial State-----------------------------------------------------------
    let src_old = get_account(&accounts[0]);
    let amount = u64::from_le_bytes([
        instruction_data[0], instruction_data[1], instruction_data[2], instruction_data[3],
        instruction_data[4], instruction_data[5], instruction_data[6], instruction_data[7],
    ]);
    let src_owner = src_old.owner;
    let src_initialised = src_old.is_initialized();
    let src_init_state = src_old.account_state();
    let mint_initialised = get_mint(&accounts[1]).is_initialized();
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[3]).is_initialized());

    //-Process Instruction-----------------------------------------------------
    let result = call_process_approve_checked!(accounts, instruction_data);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < 9 {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.len() < 4 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if accounts[0].data_len() != Account::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if src_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !src_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount))
    } else if src_init_state.unwrap() == AccountState::Frozen {
        // This should be safe to unwrap due to above check passing
        assert_eq!(result, Err(ProgramError::Custom(17)))
    } else if key!(&accounts[1]) != &get_account(&accounts[0]).mint {
        assert_eq!(result, Err(ProgramError::Custom(3)))
    } else if accounts[1].data_len() != Mint::LEN {
        // Not sure if this is even possible if we get past the case above
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if mint_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !mint_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount))
    } else if instruction_data[8] != get_mint(&accounts[1]).decimals {
        assert_eq!(result, Err(ProgramError::Custom(18)))
    } else {
        // Validate Owner
        inner_test_validate_owner(
            &src_owner,     // expected_owner
            &accounts[3],   // owner_account_info
            &accounts[4..], // tx_signers
            maybe_multisig_is_initialised,
            result.clone(),
        )?;

        let src_new = get_account(&accounts[0]);
        assert_eq!(src_new.delegate().unwrap(), key!(&accounts[2]));
        assert_eq!(src_new.delegated_amount(), amount);
        assert!(result.is_ok())
    }

    result
}
