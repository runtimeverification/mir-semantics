/// accounts[0] // Account Info - Mint Case
/// accounts[1] // Authority Info
/// accounts[2..13] // Signers
/// instruction_data[0] // Authority Type (instruction)
/// instruction_data[1] // New Authority Follows (0 -> No, 1 -> Yes)
/// instruction_data[2..34] // New Authority Pubkey
#[inline(never)]
fn test_process_set_authority_mint_multisig(
    accounts: &[AccountInfo; 3],
    instruction_data: &[u8; 34],
) -> ProgramResult {
    cheatcode_mint!(&accounts[0]); // Assume Mint
    cheatcode_multisig!(&accounts[1]); // Authority

    //-Initial State-----------------------------------------------------------
    let mint_old = get_mint(&accounts[0]);
    let mint_data_len = accounts[0].data_len();
    let old_mint_authority_is_none = mint_old.mint_authority().is_none();
    let old_freeze_authority_is_none = mint_old.freeze_authority().is_none();
    let old_mint_authority = mint_old.mint_authority().cloned();
    let old_freeze_authority = mint_old.freeze_authority().cloned();
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[1]).is_initialized());
    let mint_is_initialised = mint_old.is_initialized();

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
    } else if mint_data_len != Account::LEN && mint_data_len != Mint::LEN {
        assert_eq!(result, Err(ProgramError::InvalidArgument));
        return result;
    } else if mint_data_len == Mint::LEN {
        // established by cheatcode_mint

        let mint_new = get_mint(&accounts[0]);

        if !mint_is_initialised.unwrap() {
            assert_eq!(result, Err(ProgramError::UninitializedAccount));
            return result;
        } else if instruction_data[0] != 0 && instruction_data[0] != 1 {
            // AuthorityType neither MintTokens nor FreezeAccount
            assert_eq!(result, Err(ProgramError::Custom(15)));
            return result;
        } else if instruction_data[0] == 0 {
            // MintTokens
            if old_mint_authority_is_none {
                assert_eq!(result, Err(ProgramError::Custom(5)));
                return result;
            }

            // Validate Owner
            inner_test_validate_owner(
                &old_mint_authority.unwrap(), // expected_owner
                &accounts[1],                 // owner_account_info
                &accounts[2..],               // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;

            if instruction_data[1] == 1 {
                // 1 ==> 34 <= instruction_data.len()
                assert_pubkey_from_slice!(mint_new.mint_authority().unwrap(), &instruction_data[2..34]);
            } else {
                assert_eq!(mint_new.mint_authority(), None);
            }
            assert!(result.is_ok())
        } else {
            // FreezeAccount
            assert_eq!(instruction_data[0], 1); // If not MintTokens (0), must be FreezeAccount (1)
            if old_freeze_authority_is_none {
                assert_eq!(result, Err(ProgramError::Custom(16)));
                return result;
            }

            // Validate Owner
            inner_test_validate_owner(
                &old_freeze_authority.unwrap(), // expected_owner
                &accounts[1],                   // owner_account_info
                &accounts[2..],                 // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;

            if instruction_data[1] == 1 {
                // 1 ==> 34 <= instruction_data.len()
                assert_pubkey_from_slice!(mint_new.freeze_authority().unwrap(), &instruction_data[2..34]);
            } else {
                assert_eq!(mint_new.freeze_authority(), None);
            }
            assert!(result.is_ok())
        }
    } else {
        unreachable!(); // mint_data_len == Mint::LEN must hold
    }

    result
}
