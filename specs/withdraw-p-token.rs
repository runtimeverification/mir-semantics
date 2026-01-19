/// accounts[0] // Source Account Info (Account)
/// accounts[1] // Destination Info
/// accounts[2] // Authority Info
#[inline(never)]
fn test_process_withdraw_excess_lamports_account(accounts: &[AccountInfo; 3]) -> ProgramResult {
    cheatcode_is_account(&accounts[0]); // Source Account
    cheatcode_is_account(&accounts[1]); // Destination
    cheatcode_is_account(&accounts[2]); // Excluding the multisig case

    //-Initial State-----------------------------------------------------------
    let src_old = get_account(&accounts[0]);
    let src_data_len = accounts[0].data_len();
    let src_account_initialised = src_old.is_initialized();
    let src_account_owner = src_old.owner;
    let src_account_is_native = src_old.is_native();
    let src_init_lamports = accounts[0].lamports();
    let dst_init_lamports = accounts[1].lamports();
    let maybe_multisig_is_initialised = None; // Value set to `None` since authority is an account

    // Note: Rent is a supported sysvar so ProgramError::UnsupportedSysvar should be
    // impossible
    let rent = pinocchio::sysvars::rent::Rent::get().unwrap();
    let minimum_balance = rent.minimum_balance(accounts[0].data_len());

    //-Process Instruction-----------------------------------------------------
    let result = process_withdraw_excess_lamports(accounts);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else {
        assert_eq!(src_data_len, Account::LEN); // established by cheatcode_is_account
        {
            if src_account_initialised.is_err() {
                assert_eq!(result, Err(ProgramError::InvalidAccountData));
                return result;
            } else if !src_account_initialised.unwrap() {
                assert_eq!(result, Err(ProgramError::UninitializedAccount));
                return result;
            } else if src_account_is_native {
                assert_eq!(result, Err(ProgramError::Custom(10)));
                return result;
            }

            // Validate Owner
            inner_test_validate_owner(
                &src_account_owner, // expected_owner
                &accounts[2],       // owner_account_info
                &accounts[3..],     // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;

            if src_init_lamports < minimum_balance {
                assert_eq!(result, Err(ProgramError::Custom(0)));
                return result;
            } else if dst_init_lamports
                .checked_add(src_init_lamports - minimum_balance)
                .is_none()
            {
                assert_eq!(result, Err(ProgramError::Custom(14)));
                return result;
            }

            assert_eq!(accounts[0].lamports(), minimum_balance);
            assert_eq!(
                accounts[1].lamports(),
                dst_init_lamports + (src_init_lamports - minimum_balance)
            );
            assert!(result.is_ok())
        }
    }

    result
}

/// accounts[0] // Source Account Info (Account)
/// accounts[1] // Destination Info
/// accounts[2] // Authority Info
/// accounts[3..14] // Signers
#[inline(never)]
fn test_process_withdraw_excess_lamports_account_multisig(
    accounts: &[AccountInfo; 4],
) -> ProgramResult {
    cheatcode_is_account(&accounts[0]); // Source Account
    cheatcode_is_account(&accounts[1]); // Destination
    cheatcode_is_multisig(&accounts[2]); // Authority

    //-Initial State-----------------------------------------------------------
    let src_old = get_account(&accounts[0]);
    let src_data_len = accounts[0].data_len();
    let src_account_initialised = src_old.is_initialized();
    let src_account_owner = src_old.owner;
    let src_account_is_native = src_old.is_native();
    let src_init_lamports = accounts[0].lamports();
    let dst_init_lamports = accounts[1].lamports();
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[2]).is_initialized());

    // Note: Rent is a supported sysvar so ProgramError::UnsupportedSysvar should be
    // impossible
    let rent = pinocchio::sysvars::rent::Rent::get().unwrap();
    let minimum_balance = rent.minimum_balance(accounts[0].data_len());

    //-Process Instruction-----------------------------------------------------
    let result = process_withdraw_excess_lamports(accounts);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else {
        assert_eq!(src_data_len, Account::LEN); // established by cheatcode_is_account
        {
            if src_account_initialised.is_err() {
                assert_eq!(result, Err(ProgramError::InvalidAccountData));
                return result;
            } else if !src_account_initialised.unwrap() {
                assert_eq!(result, Err(ProgramError::UninitializedAccount));
                return result;
            } else if src_account_is_native {
                assert_eq!(result, Err(ProgramError::Custom(10)));
                return result;
            }

            // Validate Owner
            inner_test_validate_owner(
                &src_account_owner, // expected_owner
                &accounts[2],       // owner_account_info
                &accounts[3..],     // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;

            if src_init_lamports < minimum_balance {
                assert_eq!(result, Err(ProgramError::Custom(0)));
                return result;
            } else if u64::MAX - src_init_lamports + minimum_balance < dst_init_lamports {
                assert_eq!(result, Err(ProgramError::Custom(0)));
                return result;
            }

            assert_eq!(accounts[0].lamports(), minimum_balance);
            assert_eq!(
                accounts[1].lamports(),
                dst_init_lamports + src_init_lamports - minimum_balance
            );
            assert!(result.is_ok())
        }
    }

    result
}

/// accounts[0] // Source Account Info (Mint)
/// accounts[1] // Destination Info
/// accounts[2] // Authority Info
#[inline(never)]
fn test_process_withdraw_excess_lamports_mint(accounts: &[AccountInfo; 3]) -> ProgramResult {
    cheatcode_is_mint(&accounts[0]); // Source Account (Mint)
    cheatcode_is_account(&accounts[1]); // Destination
    cheatcode_is_account(&accounts[2]); // Excluding the multisig case

    //-Initial State-----------------------------------------------------------
    let src_old = get_mint(&accounts[0]);
    let src_data_len = accounts[0].data_len();
    let src_mint_initialised = src_old.is_initialized();
    let src_mint_mint_authority = src_old.mint_authority().cloned();
    let src_init_lamports = accounts[0].lamports();
    let dst_init_lamports = accounts[1].lamports();
    let maybe_multisig_is_initialised = None; // Value set to `None` since authority is an account

    // Note: Rent is a supported sysvar so ProgramError::UnsupportedSysvar should be
    // impossible
    let rent = pinocchio::sysvars::rent::Rent::get().unwrap();
    let minimum_balance = rent.minimum_balance(accounts[0].data_len());

    //-Process Instruction-----------------------------------------------------
    let result = process_withdraw_excess_lamports(accounts);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else {
        assert_eq!(src_data_len, Mint::LEN); // established by cheatcode_is_mint
        {
            if src_mint_initialised.is_err() {
                assert_eq!(result, Err(ProgramError::InvalidAccountData));
                return result;
            } else if !src_mint_initialised.unwrap() {
                assert_eq!(result, Err(ProgramError::UninitializedAccount));
                return result;
            } else if src_mint_mint_authority.is_some() {
                // Validate Owner
                inner_test_validate_owner(
                    &src_mint_mint_authority.unwrap(), // expected_owner
                    &accounts[2],                      // owner_account_info
                    &accounts[3..],                    // tx_signers
                    maybe_multisig_is_initialised,
                    result.clone(),
                )?;
            } else if accounts[0] != accounts[2] {
                assert_eq!(result, Err(ProgramError::Custom(15)));
                return result;
            } else if !accounts[2].is_signer() {
                assert_eq!(result, Err(ProgramError::MissingRequiredSignature));
                return result;
            }

            if src_init_lamports < minimum_balance {
                assert_eq!(result, Err(ProgramError::Custom(0)));
                return result;
            } else if dst_init_lamports
                .checked_add(src_init_lamports - minimum_balance)
                .is_none()
            {
                assert_eq!(result, Err(ProgramError::Custom(14)));
                return result;
            }

            assert!(result.is_ok());
            assert_eq!(accounts[0].lamports(), minimum_balance);
            assert_eq!(
                accounts[1].lamports(),
                dst_init_lamports
                    .checked_add(src_init_lamports - minimum_balance)
                    .unwrap()
            );
        }
    }
    result
}

/// accounts[0] // Source Account Info (Mint)
/// accounts[1] // Destination Info
/// accounts[2] // Authority Info
/// accounts[3..14] // Signers
#[inline(never)]
fn test_process_withdraw_excess_lamports_mint_multisig(
    accounts: &[AccountInfo; 4],
) -> ProgramResult {
    cheatcode_is_mint(&accounts[0]); // Source Account (Mint)
    cheatcode_is_account(&accounts[1]); // Destination
    cheatcode_is_multisig(&accounts[2]); // Authority

    //-Initial State-----------------------------------------------------------
    let src_old = get_mint(&accounts[0]);
    let src_data_len = accounts[0].data_len();
    let src_mint_initialised = src_old.is_initialized();
    let src_mint_mint_authority = src_old.mint_authority().cloned();
    let src_init_lamports = accounts[0].lamports();
    let dst_init_lamports = accounts[1].lamports();
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[2]).is_initialized());

    // Note: Rent is a supported sysvar so ProgramError::UnsupportedSysvar should be
    // impossible
    let rent = pinocchio::sysvars::rent::Rent::get().unwrap();
    let minimum_balance = rent.minimum_balance(accounts[0].data_len());

    //-Process Instruction-----------------------------------------------------
    let result = process_withdraw_excess_lamports(accounts);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else {
        assert_eq!(src_data_len, Mint::LEN); // established by cheatcode_is_mint
        {
            if src_mint_initialised.is_err() {
                assert_eq!(result, Err(ProgramError::InvalidAccountData));
                return result;
            } else if !src_mint_initialised.unwrap() {
                assert_eq!(result, Err(ProgramError::UninitializedAccount));
                return result;
            } else if src_mint_mint_authority.is_some() {
                // Validate Owner
                inner_test_validate_owner(
                    &src_mint_mint_authority.unwrap(), // expected_owner
                    &accounts[2],                      // owner_account_info
                    &accounts[3..],                    // tx_signers
                    maybe_multisig_is_initialised,
                    result.clone(),
                )?;
            } else if accounts[0] != accounts[2] {
                assert_eq!(result, Err(ProgramError::Custom(15)));
                return result;
            } else if !accounts[2].is_signer() {
                assert_eq!(result, Err(ProgramError::MissingRequiredSignature));
                return result;
            } else if src_init_lamports < minimum_balance {
                assert_eq!(result, Err(ProgramError::Custom(0)));
                return result;
            } else if u64::MAX - src_init_lamports + minimum_balance < dst_init_lamports {
                assert_eq!(result, Err(ProgramError::Custom(0)));
                return result;
            }

            assert_eq!(accounts[0].lamports(), minimum_balance);
            assert_eq!(
                accounts[1].lamports(),
                dst_init_lamports + src_init_lamports - minimum_balance
            );
            assert!(result.is_ok())
        }
    }

    result
}

/// accounts[0] // Source Account Info
/// accounts[1] // Destination Info
/// accounts[2] // Authority Info
#[inline(never)]
fn test_process_withdraw_excess_lamports_multisig(accounts: &[AccountInfo; 3]) -> ProgramResult {
    cheatcode_is_multisig(&accounts[0]); // Source Account (Multisig)
    cheatcode_is_account(&accounts[1]); // Destination
    cheatcode_is_account(&accounts[2]); // Excluding the multisig case

    //-Initial State-----------------------------------------------------------
    let src_data_len = accounts[0].data_len();
    let src_init_lamports = accounts[0].lamports();
    let dst_init_lamports = accounts[1].lamports();
    let maybe_multisig_is_initialised = None; // Value set to `None` since authority is an account

    // Note: Rent is a supported sysvar so ProgramError::UnsupportedSysvar should be
    // impossible
    let rent = pinocchio::sysvars::rent::Rent::get().unwrap();
    let minimum_balance = rent.minimum_balance(accounts[0].data_len());

    //-Process Instruction-----------------------------------------------------
    let result = process_withdraw_excess_lamports(accounts);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else if src_data_len != Account::LEN
        && src_data_len != Mint::LEN
        && src_data_len != Multisig::LEN
    {
        assert_eq!(result, Err(ProgramError::Custom(13)));
        return result;
    } else {
        assert_eq!(src_data_len, Multisig::LEN); // established by cheatcode_is_multisig

        // Validate Owner
        inner_test_validate_owner(
            accounts[0].key(), // expected_owner
            &accounts[2],      // owner_account_info
            &accounts[3..],    // tx_signers
            maybe_multisig_is_initialised,
            result.clone(),
        )?;

        if src_init_lamports < minimum_balance {
            assert_eq!(result, Err(ProgramError::Custom(0)));
            return result;
        } else if dst_init_lamports
            .checked_add(src_init_lamports - minimum_balance)
            .is_none()
        {
            assert_eq!(result, Err(ProgramError::Custom(0)));
            return result;
        }

        assert_eq!(accounts[0].lamports(), minimum_balance);
        assert_eq!(
            accounts[1].lamports(),
            dst_init_lamports + (src_init_lamports - minimum_balance)
        );
        assert!(result.is_ok())
    }

    result
}

/// accounts[0] // Source Account Info
/// accounts[1] // Destination Info
/// accounts[2] // Authority Info
/// accounts[3..14] // Signers
#[inline(never)]
fn test_process_withdraw_excess_lamports_multisig_multisig(
    accounts: &[AccountInfo; 4],
) -> ProgramResult {
    cheatcode_is_multisig(&accounts[0]); // Source Account (Multisig)
    cheatcode_is_account(&accounts[1]); // Destination
    cheatcode_is_multisig(&accounts[2]); // Authority

    //-Initial State-----------------------------------------------------------
    let src_data_len = accounts[0].data_len();
    let src_init_lamports = accounts[0].lamports();
    let dst_init_lamports = accounts[1].lamports();
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[2]).is_initialized());

    // Note: Rent is a supported sysvar so ProgramError::UnsupportedSysvar should be
    // impossible
    let rent = pinocchio::sysvars::rent::Rent::get().unwrap();
    let minimum_balance = rent.minimum_balance(accounts[0].data_len());

    //-Process Instruction-----------------------------------------------------
    let result = process_withdraw_excess_lamports(accounts);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else if src_data_len != Account::LEN
        && src_data_len != Mint::LEN
        && src_data_len != Multisig::LEN
    {
        assert_eq!(result, Err(ProgramError::Custom(13)));
        return result;
    } else {
        assert_eq!(src_data_len, Multisig::LEN); // established by cheatcode_is_multisig

        // Validate Owner
        inner_test_validate_owner(
            accounts[0].key(), // expected_owner
            &accounts[2],      // owner_account_info
            &accounts[3..],    // tx_signers
            maybe_multisig_is_initialised,
            result.clone(),
        )?;

        if src_init_lamports < minimum_balance {
            assert_eq!(result, Err(ProgramError::Custom(0)));
            return result;
        } else if u64::MAX - src_init_lamports + minimum_balance < dst_init_lamports {
            assert_eq!(result, Err(ProgramError::Custom(0)));
            return result;
        }

        assert_eq!(accounts[0].lamports(), minimum_balance);
        assert_eq!(
            accounts[1].lamports(),
            dst_init_lamports + src_init_lamports - minimum_balance
        );
        assert!(result.is_ok())
    }

    result
}
