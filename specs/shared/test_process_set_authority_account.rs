/// accounts[0] // Account Info - Account Case
/// accounts[1] // Authority Info
/// instruction_data[0] // Authority Type (instruction)
/// instruction_data[1] // New Authority Follows (0 -> No, 1 -> Yes)
/// instruction_data[2..34] // New Authority Pubkey
#[inline(never)]
fn test_process_set_authority_account(
    accounts: &[AccountInfo; 2],
    instruction_data: &[u8; 34],
) -> ProgramResult {
    cheatcode_account!(&accounts[0]); // Assume Account
    cheatcode_account!(&accounts[1]); // Excluding the multisig case

    //-Initial State-----------------------------------------------------------
    let src_old = get_account(&accounts[0]);
    let src_initialised = src_old.is_initialized();
    let src_init_state = src_old.account_state();
    let src_owner = src_old.owner;
    let authority = src_old.close_authority().cloned().unwrap_or(src_old.owner);
    let account_data_len = accounts[0].data_len();
    let maybe_multisig_is_initialised = None; // Value set to `None` since authority is an account

    //-Process Instruction-----------------------------------------------------
    let result = call_process_set_authority!(accounts, instruction_data);

    //-Assert Postconditions---------------------------------------------------
    if instruction_data.len() < 2 {
        assert_eq!(result, Err(ProgramError::Custom(12)));
        return result;
    } else if !(0..=3).contains(&instruction_data[0]) {
        assert_eq!(result, Err(ProgramError::Custom(12)));
        return result;
    } else if instruction_data[1] != 0 && instruction_data[1] != 1 {
        assert_eq!(result, Err(ProgramError::Custom(12)));
        return result;
    } else if instruction_data[1] == 1 && instruction_data.len() < 34 {
        assert_eq!(result, Err(ProgramError::Custom(12)));
        return result;
    } else if accounts.len() < 2 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else if account_data_len != Account::LEN && account_data_len != Mint::LEN {
        assert_eq!(result, Err(ProgramError::InvalidArgument));
        return result;
    } else if account_data_len == Account::LEN {
        // established by cheatcode_is_account

        let src_new = get_account(&accounts[0]);

        if src_initialised.is_err() {
            assert_eq!(result, Err(ProgramError::InvalidAccountData));
            return result;
        } else if !src_initialised.unwrap() {
            assert_eq!(result, Err(ProgramError::UninitializedAccount));
            return result;
        } else if src_init_state.unwrap() == AccountState::Frozen {
            assert_eq!(result, Err(ProgramError::Custom(17)));
            return result;
        } else if instruction_data[0] != 2 && instruction_data[0] != 3 {
            // AuthorityType neither AccountOwner nor CloseAccount
            assert_eq!(result, Err(ProgramError::Custom(15)));
            return result;
        } else if instruction_data[0] == 2 {
            // AccountOwner
            // Validate Owner
            inner_test_validate_owner(
                &src_owner,     // expected_owner
                &accounts[1],   // owner_account_info
                &accounts[2..], // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;

            if instruction_data[1] != 1 || instruction_data.len() < 34 {
                assert_eq!(result, Err(ProgramError::Custom(12)));
                return result;
            }

            assert_pubkey_from_slice_val!(src_new.owner, instruction_data[2..34]);
            assert_eq!(src_new.delegate(), None);
            assert_eq!(src_new.delegated_amount(), 0);
            if src_new.is_native() {
                assert_eq!(src_new.close_authority(), None);
            }
            assert!(result.is_ok())
        } else {
            // CloseAccount
            assert_eq!(instruction_data[0], 3); // If not AccountOwner (2), must be CloseAccount (3)

            // Validate Owner
            inner_test_validate_owner(
                &authority,     // expected_owner
                &accounts[1],   // owner_account_info
                &accounts[2..], // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;

            if instruction_data[1] == 1 {
                // 1 ==> 34 <= instruction_data.len()
                assert_pubkey_from_slice!(src_new.close_authority().unwrap(), &instruction_data[2..34]);
            } else {
                assert_eq!(src_new.close_authority(), None);
            }
            assert!(result.is_ok())
        }
    } else {
        unreachable!() // account_data_len == Account::LEN must hold
    }

    result
}
