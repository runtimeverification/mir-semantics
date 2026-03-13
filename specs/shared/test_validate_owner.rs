/// accounts[0]    // Source Account Info (provides expected_owner)
/// accounts[1]    // Owner Info
#[inline(never)]
fn test_validate_owner(
    accounts: &[AccountInfo; 2],
) -> ProgramResult {
    cheatcode_account!(&accounts[0]);    // Source Account
    cheatcode_account!(&accounts[1]);    // Owner

    //-Initial State-----------------------------------------------------------
    let src_old = get_account(&accounts[0]);
    let expected_owner = src_old.owner;
    let maybe_multisig_is_initialised = None;

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
