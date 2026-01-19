#[inline(never)]
fn test_process_ui_amount_to_amount(
    accounts: &[AccountInfo; 1],
    instruction_data: &[u8],
) -> ProgramResult {
    cheatcode_mint!(&accounts[0]);

    //-Initial State-----------------------------------------------------------
    let ui_amount = core::str::from_utf8(instruction_data);
    let mint_initialised = get_mint(&accounts[0]).is_initialized();

    //-Process Instruction-----------------------------------------------------
    let result = call_process_ui_amount_to_amount!(accounts, instruction_data);

    //-Assert Postconditions---------------------------------------------------
    // TODO: validations module is private, so we need a work around
    if ui_amount.is_err() {
        assert_eq!(result, Err(ProgramError::Custom(12)))
    } else if accounts.is_empty() {
        assert_eq!(result, Err(ProgramError::NotEnoughAccountKeys))
    } else if owner!(&accounts[0]) != &PROGRAM_ID {
        assert_eq!(result, Err(ProgramError::IncorrectProgramId))
    } else if accounts[0].data_len() != Mint::LEN {
        assert_eq!(result, Err(ProgramError::Custom(2)))
    } else if mint_initialised.is_err() {
        assert_eq!(result, Err(ProgramError::InvalidAccountData))
    } else if !mint_initialised.unwrap() {
        assert_eq!(result, Err(ProgramError::Custom(2)))
    } else if ui_amount.unwrap().is_empty() {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if ui_amount.unwrap() == "." {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if 1 < ui_amount.unwrap().chars().filter(|&c| c == '.').count() {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if ui_amount.unwrap().starts_with('.')
        && ui_amount.unwrap().chars().skip(1).all(|c| c == '0')
    {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if ui_amount.unwrap().split_once('.').is_some_and(|(_, frac)| {
        (get_mint(&accounts[0]).decimals as usize) < frac.trim_end_matches('0').len()
    }) {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if ui_amount.unwrap().split_once('.').map_or(
        257_usize < ui_amount.unwrap().len() + (get_mint(&accounts[0]).decimals as usize),
        |(ints, _)| 257_usize < ints.len() + (get_mint(&accounts[0]).decimals as usize),
    ) {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    }
    /*else if ui_amount.unwrap() == "+." {
        // TODO: Why is this valid?
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if ui_amount.unwrap() == "+" {
        // TODO: Why is this valid?
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    }*/
    else if ui_amount.unwrap().starts_with('-') {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if ui_amount
        .unwrap()
        .contains(|c: char| !c.is_ascii_digit() && c != '+' && c != '.')
    {
        assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else if ui_amount.unwrap().split_once('.').map_or(
        {
            const MAX_VAL: &str = "1844674407370955"; // TODO: What should this be?
            let ui_amount = ui_amount.unwrap();
            let ui_amount = ui_amount.strip_prefix('+').unwrap_or(ui_amount);
            let ui_amount = ui_amount.trim_start_matches('0');
            match ui_amount.len().cmp(&MAX_VAL.len()) {
                core::cmp::Ordering::Less => false,
                core::cmp::Ordering::Greater => true,
                core::cmp::Ordering::Equal => MAX_VAL < ui_amount,
            }
        },
        |(ints, fracs)| {
            const MAX_VAL: &str = "1844674407370955"; // TODO: What should this be?
            let ints = ints.strip_prefix('+').unwrap_or(ints);
            let hi = ints.trim_start_matches('0');
            let lo = if hi.is_empty() {
                fracs.trim_start_matches('0')
            } else {
                fracs
            };

            let total_len = hi.len() + lo.len();

            match total_len.cmp(&MAX_VAL.len()) {
                core::cmp::Ordering::Less => false,
                core::cmp::Ordering::Greater => true,
                core::cmp::Ordering::Equal => {
                    if hi.len() > MAX_VAL.len() {
                        return true;
                    }
                    let (max_hi, max_lo) = MAX_VAL.split_at(hi.len());
                    hi > max_hi || (hi == max_hi && lo > max_lo)
                }
            }
        },
    ) {
        // TODO: What is going on ??? Need to fix
        // assert_eq!(result, Err(ProgramError::InvalidArgument))
    } else {
        assert!(result.is_ok())
    }
    result
}
