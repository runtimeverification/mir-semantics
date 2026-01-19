/// Unified harness for WithdrawExcessLamports instruction (discriminator 38).
///
/// This harness handles all source account types (Account, Mint, Multisig) and
/// authority types (single signer or multisig) in one function.
///
/// program_id      // Token Program ID
/// accounts[0]     // Source Account Info (Account, Mint, or Multisig)
/// accounts[1]     // Destination Info
/// accounts[2]     // Authority Info
/// accounts[3..]   // Signers (for multisig authority)
/// instruction_data[0] // Discriminator 38 (Withdraw Excess Lamports)
#[inline(never)]
fn test_process_withdraw_excess_lamports(
    program_id: &Pubkey,
    accounts: &[AccountInfo; 4],
    instruction_data: &[u8; 1],
) -> ProgramResult {
    // Constrain discriminator and program id
    unsafe { assume(38 == instruction_data[0]); }
    unsafe { assume(program_id == &crate::id()); }

    let instruction_data_with_discriminator = instruction_data;

    //-Process Instruction-----------------------------------------------------
    let result = Processor::process(program_id, accounts, instruction_data_with_discriminator);

    //-Assert Postconditions---------------------------------------------------
    // NOTE: WithdrawExcessLamports (discriminator 38) is a token-2022 instruction that does not
    // exist in the original spl-token program. The original spl-token's TokenInstruction only
    // supports discriminators 0-24. When Processor::process receives discriminator 38, it fails
    // at TokenInstruction::unpack() with InvalidInstruction error.
    assert_eq!(result, Err(TokenError::InvalidInstruction.into()));
    result
}
