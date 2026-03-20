/// Computes the expected result of mod.rs::validate_owner.
#[inline(never)]
fn expected_validate_owner_result(
    expected_owner: &Pubkey,
    owner_account_info: &AccountInfo,
    tx_signers: &[AccountInfo],
    maybe_multisig_is_initialised: Option<Result<bool, ProgramError>>,
) -> Result<(), ProgramError> {
    if expected_owner != key!(owner_account_info) {
        return Err(ProgramError::Custom(4));
    }
    // We add the `maybe_multisig_is_initialised.is_some()` to not branch vacuously in the
    // non-multisig cases
    else if maybe_multisig_is_initialised.is_some()
        && owner_account_info.data_len() == Multisig::LEN
        && (owner!(owner_account_info) == &PROGRAM_ID)
    {
        // Guaranteed to succeed by `cheatcode_is_multisig`
        let multisig_is_initialised = maybe_multisig_is_initialised.unwrap();
        if multisig_is_initialised.is_err() {
            return Err(ProgramError::InvalidAccountData);
        } else if !multisig_is_initialised.unwrap() {
            return Err(ProgramError::UninitializedAccount);
        } else {
            let multisig = get_multisig(owner_account_info);

            // Did all declared and allowd signers sign?
            let unsigned_exists = tx_signers.iter().any(|potential_signer| {
                multisig.signers[0..multisig.n as usize]
                    .iter()
                    .any(|registered_key| {
                        registered_key == key!(potential_signer) && !is_signer!(potential_signer)
                    })
            });
            if unsigned_exists {
                return Err(ProgramError::MissingRequiredSignature);
            }

            // Were enough signatures received?
            let signers_count = multisig.signers[0..multisig.n as usize]
                .iter()
                .filter_map(|registered_key| {
                    tx_signers.iter().find(|potential_signer| {
                        key!(potential_signer) == registered_key && is_signer!(potential_signer)
                    })
                })
                .count();

            // Check if we have enough signers
            if signers_count < multisig.m as usize {
                return Err(ProgramError::MissingRequiredSignature);
            }

            return Ok(());
        }
    }
    // Non-multisig case - check if owner_account_info.is_signer()
    else if !is_signer!(owner_account_info) {
        return Err(ProgramError::MissingRequiredSignature);
    }

    Ok(())
}

/// This function encapsulates the specification of validating the signature
/// requirements In particular, code from mod.rs::validate_owner is checked
#[inline(never)]
fn inner_test_validate_owner(
    expected_owner: &Pubkey,
    owner_account_info: &AccountInfo,
    tx_signers: &[AccountInfo],
    maybe_multisig_is_initialised: Option<Result<bool, ProgramError>>,
    result: Result<(), ProgramError>,
) -> Result<(), ProgramError> {
    if expected_owner != key!(owner_account_info) {
        assert_eq!(result, Err(ProgramError::Custom(4)));
        return result;
    }
    // We add the `maybe_multisig_is_initialised.is_some()` to not branch vacuously in the
    // non-multisig cases
    else if maybe_multisig_is_initialised.is_some()
        && owner_account_info.data_len() == Multisig::LEN
        && (owner!(owner_account_info) == &PROGRAM_ID)
    {
        // Guaranteed to succeed by `cheatcode_is_multisig`
        let multisig_is_initialised = maybe_multisig_is_initialised.unwrap();
        if multisig_is_initialised.is_err() {
            assert_eq!(result, Err(ProgramError::InvalidAccountData));
            return result;
        } else if !multisig_is_initialised.unwrap() {
            assert_eq!(result, Err(ProgramError::UninitializedAccount));
            return result;
        } else {
            let multisig = get_multisig(owner_account_info);

            // Did all declared and allowd signers sign?
            let unsigned_exists = tx_signers.iter().any(|potential_signer| {
                multisig.signers[0..multisig.n as usize]
                    .iter()
                    .any(|registered_key| {
                        registered_key == key!(potential_signer) && !is_signer!(potential_signer)
                    })
            });
            if unsigned_exists {
                assert_eq!(result, Err(ProgramError::MissingRequiredSignature));
                return result;
            }

            // Were enough signatures received?
            let signers_count = multisig.signers[0..multisig.n as usize]
                .iter()
                .filter_map(|registered_key| {
                    tx_signers.iter().find(|potential_signer| {
                        key!(potential_signer) == registered_key && is_signer!(potential_signer)
                    })
                })
                .count();

            // Check if we have enough signers
            if signers_count < multisig.m as usize {
                assert_eq!(result, Err(ProgramError::MissingRequiredSignature));
                return result;
            }

            return Ok(());
        }
    }
    // Non-multisig case - check if owner_account_info.is_signer()
    else if !is_signer!(owner_account_info) {
        assert_eq!(result, Err(ProgramError::MissingRequiredSignature));
        return result;
    }

    Ok(())
}
