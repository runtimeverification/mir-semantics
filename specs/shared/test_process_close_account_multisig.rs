/// accounts[0] // Source Info
/// accounts[1] // Destination Info
/// accounts[2] // Authority Info
/// accounts[3..14] // Multisig Signers
#[inline(never)]
fn test_process_close_account_multisig(accounts: &[AccountInfo; 4]) -> ProgramResult {
    cheatcode_account!(&accounts[0]);
    cheatcode_account!(&accounts[1]);
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
    let src_initialised = src_old.is_initialized();
    let src_data_len = accounts[0].data_len();
    let src_init_amount = src_old.amount();
    let src_init_lamports = accounts[0].lamports();
    let dst_init_lamports = accounts[1].lamports();
    let src_is_native = src_old.is_native();
    let src_owned_sys_inc = src_old.is_owned_by_system_program_or_incinerator();
    let authority = src_old.close_authority().cloned().unwrap_or(src_old.owner);
    let maybe_multisig_is_initialised = Some(get_multisig(&accounts[2]).is_initialized());

    //-Process Instruction-----------------------------------------------------
    let result = call_process_close_account!(accounts);

    //-Assert Postconditions---------------------------------------------------
    if accounts.len() < 3 {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys));
        return result;
    } else if same_account!(accounts[0], accounts[1]) {
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if src_data_len != Account::LEN {
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if src_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData));
        return result;
    } else if !src_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::UninitializedAccount));
        return result;
    } else if !src_is_native && src_init_amount != 0 {
        assert_eq!(result, Err(ProgramError::Custom(11)));
        return result;
    } else {
        if !src_owned_sys_inc {
            // Validate Owner
            inner_test_validate_owner(
                &authority,     // expected_owner
                &accounts[2],   // owner_account_info
                &accounts[3..], // tx_signers
                maybe_multisig_is_initialised,
                result.clone(),
            )?;
        } else if key!(&accounts[1]) != &INCINERATOR_ID {
            assert_eq!(result, Err(ProgramError::InvalidAccountData));
            return result;
        }

        if dst_init_lamports.checked_add(src_init_lamports).is_none() {
            assert_eq!(result, Err(ProgramError::Custom(14)));
            return result;
        }
        assert!(result.is_ok());

        // Validate owner falls through to here if no error
        assert_eq!(
            accounts[1].lamports(),
            dst_init_lamports + src_init_lamports
        );
        #[cfg(any(target_os = "solana", target_arch = "bpf"))]
        {
            // Solana-RT only syscall
            assert_eq!(*owner!(&accounts[0]), [0; 32]);
            assert_eq!(accounts[0].lamports(), 0);
            assert_eq!(accounts[0].data_len(), 0);
        }
    }
    result
}
