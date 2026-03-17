/// accounts[0]    // Source Account Info (provides expected_owner)
/// accounts[1]    // Owner Info (multisig)
/// accounts[2..4] // Signers
#[inline(never)]
fn test_validate_owner_multisig(
    accounts: &[AccountInfo; 5],
) -> ProgramResult {
    cheatcode_account!(&accounts[0]);    // Source Account
    cheatcode_multisig!(&accounts[1]);   // Owner (multisig)

    #[cfg(feature = "assumptions")]
    {
        let multisig = get_multisig(&accounts[1]);
        if multisig.m < 1 || multisig.m > MAX_SIGNERS {
            return Ok(());
        }
        if multisig.n < 1 || multisig.n > MAX_SIGNERS {
            return Ok(());
        }
    }

    //-Initial State-----------------------------------------------------------
    let src_old = get_account(&accounts[0]);
    let expected_owner = src_old.owner;
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[1]).is_initialized());

    //-Process Instruction-----------------------------------------------------
    let result = expected_validate_owner_result(
        &expected_owner,
        &accounts[1],
        &accounts[2..],
        maybe_multisig_is_initialised.clone(),
    );

    //-Assert Postconditions---------------------------------------------------
    inner_test_validate_owner(
        &expected_owner,
        &accounts[1],
        &accounts[2..],
        maybe_multisig_is_initialised,
        result.clone(),
    )?;

    result
}
